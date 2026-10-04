#!/usr/bin/env python3
"""Validate symbol-to-SPICE mappings and package source invariants."""

from __future__ import annotations

import re
import json
import sys
from collections import Counter
from pathlib import Path

from kicad_sexpr import parse, children, child, properties as symbol_properties


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_DIR = ROOT / "symbol"
SPICE_DIR = ROOT / "spice"

EXPECTED_SYMBOLS = 64
PROPERTY_RE = re.compile(r'\(property "([^"]+)" "([^"]*)"')
TOP_SYMBOL_RE = re.compile(r'^\t\(symbol "([^"]+)"')
PIN_NUMBER_RE = re.compile(r'^\s*\(number "([^"]+)"', re.MULTILINE)
DEFINITION_RE = re.compile(r"^\s*\.(model|subckt)\s+(\S+)\s*(.*)$", re.IGNORECASE)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def symbol_blocks(path: Path) -> list[tuple[str, list[str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    starts = [(index, match.group(1)) for index, line in enumerate(lines)
              if (match := TOP_SYMBOL_RE.match(line))]
    blocks = []
    for position, (start, name) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        blocks.append((name, lines[start:end]))
    return blocks


def public_definitions(path: Path) -> list[tuple[str, str, str]]:
    definitions = []
    depth = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        match = DEFINITION_RE.match(line)
        if match:
            kind, name, remainder = match.groups()
            kind = kind.upper()
            if depth == 0 and not name.startswith("__"):
                model_type = remainder.split("(", 1)[0].split()[0].upper() if kind == "MODEL" else ""
                definitions.append((name, kind, model_type))
            if kind == "SUBCKT":
                depth += 1
        elif re.match(r"^\s*\.ends\b", line, re.IGNORECASE):
            depth = max(0, depth - 1)
    return definitions


def main() -> int:
    errors: list[str] = []
    symbols: list[tuple[Path, str, dict[str, str], set[str]]] = []

    for path in sorted(SYMBOL_DIR.glob("*.kicad_sym")):
        for name, block in symbol_blocks(path):
            text = "\n".join(block)
            properties = dict(PROPERTY_RE.findall(text))
            pins = set(PIN_NUMBER_RE.findall(text))
            symbols.append((path, name, properties, pins))

    if len(symbols) != EXPECTED_SYMBOLS:
        fail(errors, f"Expected {EXPECTED_SYMBOLS} symbols, found {len(symbols)}")

    definitions: dict[str, tuple[Path, str, str]] = {}
    counts: Counter[str] = Counter()
    for path in sorted(SPICE_DIR.glob("*.lib")):
        for name, kind, model_type in public_definitions(path):
            key = name.upper()
            counts[key] += 1
            definitions[key] = (path, kind, model_type)

    for name, count in sorted(counts.items()):
        if count != 1:
            fail(errors, f"Public model {name} is defined {count} times")

    used_models: set[str] = set()
    required = {
        "Value", "Footprint", "Description", "ki_keywords", "Sim.Library",
        "Sim.Name", "Sim.Device", "Sim.Pins",
    }
    for path, name, properties, pins in symbols:
        missing = sorted(key for key in required if not properties.get(key))
        if missing:
            fail(errors, f"{path.name}:{name} has empty or missing fields: {', '.join(missing)}")
            continue
        expected_value = name
        if properties["Value"] != expected_value:
            fail(errors, f"{path.name}:{name} has Value={properties['Value']}")
        library = properties["Sim.Library"]
        if "\\" in library:
            fail(errors, f"{path.name}:{name} uses backslashes in Sim.Library")
        prefix = "${KICAD_RAYSLIB}/"
        if not library.startswith(prefix):
            fail(errors, f"{path.name}:{name} has unsupported Sim.Library={library}")
            continue
        model_path = ROOT / library[len(prefix):]
        if not model_path.is_file():
            fail(errors, f"{path.name}:{name} references missing {model_path.relative_to(ROOT)}")
            continue
        model_name = properties["Sim.Name"].upper()
        used_models.add(model_name)
        definition = definitions.get(model_name)
        if not definition:
            fail(errors, f"{path.name}:{name} references undefined model {properties['Sim.Name']}")
            continue
        definition_path, kind, model_type = definition
        if definition_path.resolve() != model_path.resolve():
            fail(errors, f"{path.name}:{name} model is defined in a different library")
        device = properties["Sim.Device"].upper()
        expected_device = "SUBCKT" if kind == "SUBCKT" else {
            "NJF": "NJFET", "PJF": "PJFET",
        }.get(model_type, model_type)
        if device != expected_device:
            fail(errors, f"{path.name}:{name} uses {device}, expected {expected_device}")
        mapped_pins = {item.split("=", 1)[0] for item in properties["Sim.Pins"].split()}
        if pins and mapped_pins != pins:
            fail(errors, f"{path.name}:{name} maps pins {sorted(mapped_pins)}, symbol has {sorted(pins)}")

    unused = set(definitions) - used_models
    if unused:
        fail(errors, f"SPICE models without symbols: {sorted(unused)}")

    validate_bjt_catalog(errors)

    legacy_files = list((SPICE_DIR / "Model").glob("**/*"))
    if any(path.is_file() for path in legacy_files):
        fail(errors, "Legacy files remain below spice/Model")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(symbols)} symbols and {len(definitions)} public SPICE models.")
    return 0


CATALOG = json.loads((ROOT / 'tools/bjt_catalog.json').read_text(encoding='utf-8'))



def validate_bjt_catalog(errors: list[str]) -> None:
    """Check every physical terminal, unit and package wrapper against the catalog."""
    library = parse((SYMBOL_DIR / 'rayslib-bjt-smd.kicad_sym').read_text(encoding='utf-8'))
    entries = {s[1]: s for s in children(library, 'symbol')}
    models = (SPICE_DIR / 'BJT_Arrays.lib').read_text(encoding='utf-8')
    for d in CATALOG:
        base = d['name']
        expected = {str(p): (i, terminal) for i,t in enumerate(d['transistors'],1)
                    for terminal,pins in [('C',t['c']),('B',[t['b']]),('E',[t['e']])]
                    for p in pins}
        names = [base]
        for name in names:
            if name not in entries:
                fail(errors, f'Missing BJT view {name}')
                continue
            s = entries[name]
            props = symbol_properties(s)
            for field,value in [('Value',base),('Footprint',d['footprint']),('Datasheet',d['datasheet']),
                                ('Description',d['description']),('Sim.Name',base),
                                ('Sim.Library','${KICAD_RAYSLIB}/spice/BJT_Arrays.lib')]:
                if props.get(field) != value:
                    fail(errors, f'{name}: unexpected {field}')
            mappings = props.get('Sim.Pins','').split()
            if sorted(mappings) != sorted(f'{p}={p}' for p in expected):
                fail(errors, f'{name}: SPICE mapping differs from physical pin order')
            actual = {}
            units = set()
            for body in children(s,'symbol'):
                unit = int(body[1].rsplit('_',2)[1])
                units.add(unit)
                for pin in children(body,'pin'):
                    number = child(pin,'number')[1]
                    if number in actual:
                        fail(errors, f'{name}: duplicate physical pin {number}')
                    actual[number] = (unit,child(pin,'name')[1])
            wanted = expected if name == base else {p:(1,t) for p,(_,t) in expected.items()}
            if actual != wanted:
                fail(errors, f'{name}: wrong transistor terminal or unit assignment')
            if units != {v[0] for v in wanted.values()}:
                fail(errors, f'{name}: unexpected unit set')
        match = re.search(r'^\.subckt '+base+r'\s+([^\n]+)\n(.*?)^\.ends\b',models,re.I|re.M|re.S)
        if not match or match[1].split() != sorted(expected,key=int):
            fail(errors, f'{base}: incorrect subcircuit terminals')
            continue
        for i,t in enumerate(d['transistors'],1):
            q = re.search(r'^Q'+str(i)+r'\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',match[2],re.M)
            if not q or list(q.groups()[:3]) != [str(t['c'][0]),str(t['b']),str(t['e'])]:
                fail(errors, f'{base}: transistor {i} C/B/E mapping is incorrect')
            elif not re.search(r'^\.model\s+'+re.escape(q[4])+r'\s+'+t['polarity']+r'\b',match[2],re.I|re.M):
                fail(errors, f'{base}: transistor {i} polarity is incorrect')
            for p in t['c'][1:]:
                if not re.search(r'^RC\S+\s+'+str(t['c'][0])+r'\s+'+str(p)+r'\s+1u\s*$',match[2],re.M):
                    fail(errors, f'{base}: missing internal collector strap to pin {p}')


if __name__ == "__main__":
    raise SystemExit(main())
