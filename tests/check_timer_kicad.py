#!/usr/bin/env python3
"""Verify NE555 physical pins and run the actual KiCad-exported SPICE instance."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from kicad_sexpr import parse, children, child, properties
from check_timer_models import astable_deck, run_deck


def uid():
    return str(uuid.uuid4())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-cli', default='kicad-cli')
    parser.add_argument('--dll')
    args = parser.parse_args()
    output = ROOT/'dist/timer-kicad'
    output.mkdir(parents=True, exist_ok=True)
    library = (ROOT/'symbol/rayslib-timer-tht.kicad_sym').read_text(encoding='utf-8')
    block = library[library.index('\t(symbol "NE555P"'):].rstrip().removesuffix('\n)')
    symbol = parse(block)
    props = properties(symbol)
    pins = [p for body in children(symbol, 'symbol') for p in children(body, 'pin')]
    expected_names = {'1':'GND', '2':'TRIG', '3':'OUT', '4':'~{RESET}',
                      '5':'CONT', '6':'THRES', '7':'DISCH', '8':'VCC'}
    assert len(pins) == 8
    assert {child(p, 'number')[1]:child(p, 'name')[1] for p in pins} == expected_names
    assert props['Footprint'] == 'Package_DIP:DIP-8_W7.62mm'
    assert props['Datasheet'] == 'https://www.ti.com/lit/ds/symlink/ne555.pdf'
    root_id = uid()
    lib_id = 'rayslib-timer-tht:NE555P'
    embedded = block.replace('(symbol "NE555P"', f'(symbol "{lib_id}"', 1)
    path = output/'NE555P.kicad_sch'
    lines = [f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root_id}) (paper "A4")',
             '(lib_symbols '+embedded+')']
    for pin in pins:
        position = child(pin, 'at')
        number = child(pin, 'number')[1]
        x, y = 100+float(position[1]), 100-float(position[2])
        lines += [f'(label "P{number}" (at {x:g} {y:g} 0)'
                  f' (effects (font (size 1 1)) (justify left bottom)) (uuid {uid()}))']
    lines += [f'(symbol (lib_id "{lib_id}") (at 100 100 0) (unit 1)'
              f' (in_bom yes) (on_board yes) (dnp no) (uuid {uid()})']
    for key, value in props.items():
        if key == 'Reference':
            value = 'U1'
        lines += [f'(property {json.dumps(key)} {json.dumps(value,ensure_ascii=False)} (at 115 100 0)'
                  ' (effects (font (size 1.27 1.27)) (hide yes)))']
    lines += [f'(pin "{child(pin,"number")[1]}" (uuid {uid()}))' for pin in pins]
    lines += [f'(instances (project "{path.stem}" (path "/{root_id}" (reference "U1") (unit 1)))))',
              '(embedded_fonts no)', ')']
    path.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    env = dict(os.environ, KICAD_RAYSLIB=ROOT.as_posix(),
               KICAD_CONFIG_HOME=(output/'config').resolve().as_posix(),
               KICAD_DOCUMENTS_HOME=(output/'documents').resolve().as_posix())
    for fmt, ext in [('spice', '.cir'), ('kicadxml', '.xml')]:
        result = subprocess.run([args.kicad_cli, 'sch', 'export', 'netlist', '--format', fmt,
                                 '-o', str(path.with_suffix(ext)), str(path)],
                                env=env, capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError(result.stdout+result.stderr)
    netlist = path.with_suffix('.cir').read_text(encoding='utf-8')
    instances = [line for line in netlist.splitlines() if re.match(r'^XU1\s', line, re.I)]
    assert len(instances) == 1, netlist
    tokens = instances[0].split()
    assert [p.lstrip('/') for p in tokens[1:-1]] == [f'P{i}' for i in range(1,9)], netlist
    assert tokens[-1] == 'NE555P', netlist
    includes = [line for line in netlist.splitlines() if line.lower().startswith('.include ')]
    assert len(includes) == 1, netlist
    assert Path(includes[0].split('"')[1]).resolve() == (ROOT/'spice/Timers.lib').resolve(), netlist
    root = ET.parse(path.with_suffix('.xml')).getroot()
    comps = root.findall('./components/comp')
    assert len(comps) == 1 and comps[0].get('ref') == 'U1'
    assert comps[0].findtext('value') == 'NE555P'
    assert comps[0].findtext('footprint') == props['Footprint']
    actual = {node.get('pin'):net.get('name').lstrip('/') for net in root.findall('./nets/net')
              for node in net.findall('node') if node.get('ref') == 'U1'}
    assert actual == {str(i):f'P{i}' for i in range(1,9)}, actual
    print('PASS: NE555P physical pins, footprint, model path and SPICE terminal order', flush=True)
    # Keep the exact instance and include emitted by KiCad; attach a test circuit
    # to its exported labels and verify timing with the same numerical checks.
    deck = astable_deck(5, instance=instances[0])
    deck[1] = includes[0]
    deck = [line if line == instances[0] else re.sub(r'\bP([1-8])\b', r'/P\1', line)
            for line in deck]
    run_deck('exported_astable', deck, output, args.dll)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
