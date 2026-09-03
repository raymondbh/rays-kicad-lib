#!/usr/bin/env python3
"""Validate symbol-to-SPICE mappings and package source invariants."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SYMBOL_DIR = ROOT / "symbol"
SPICE_DIR = ROOT / "spice"

EXPECTED_SYMBOLS = 37
PROPERTY_RE = re.compile(r'\(property "([^"]+)" "([^"]*)"')
TOP_SYMBOL_RE = re.compile(r'^\t\(symbol "([^"]+)"')
PIN_NUMBER_RE = re.compile(r'^\s*\(number "([^"]+)"')
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
            if depth == 0:
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
        if properties["Value"] != name:
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
        expected_device = "SUBCKT" if kind == "SUBCKT" else model_type
        if device != expected_device:
            fail(errors, f"{path.name}:{name} uses {device}, expected {expected_device}")
        mapped_pins = {item.split("=", 1)[0] for item in properties["Sim.Pins"].split()}
        if pins and mapped_pins != pins:
            fail(errors, f"{path.name}:{name} maps pins {sorted(mapped_pins)}, symbol has {sorted(pins)}")

    unused = set(definitions) - used_models
    if unused:
        fail(errors, f"SPICE models without symbols: {sorted(unused)}")

    legacy_files = list((SPICE_DIR / "Model").glob("**/*"))
    if any(path.is_file() for path in legacy_files):
        fail(errors, "Legacy files remain below spice/Model")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(symbols)} symbols and {len(definitions)} public SPICE models.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
