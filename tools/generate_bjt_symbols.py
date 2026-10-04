#!/usr/bin/env python3
"""Regenerate the catalogued SMD BJTs while preserving existing library entries."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'tools/bjt_catalog.json'
LIBRARY = ROOT / 'symbol/rayslib-bjt-smd.kicad_sym'


def symbol(device):
    name = device['name']
    count = len(device['transistors'])
    prop_y = 1.905
    prop_x = 5.08
    props = {
        'Reference': 'Q', 'Value': device['name'], 'Footprint': device['footprint'],
        'Datasheet': device['datasheet'], 'Description': device['description'],
        'Sim.Library': '${KICAD_RAYSLIB}/spice/BJT_Arrays.lib',
        'Sim.Name': device['name'], 'Sim.Device': 'SUBCKT',
    }
    pins = sorted({p for t in device['transistors'] for p in t['c'] + [t['b'], t['e']]})
    props['Sim.Pins'] = ' '.join(f'{p}={p}' for p in pins)
    polarities = list(dict.fromkeys(t['polarity'] for t in device['transistors']))
    selection = 'matched-pair' if device['matched'] else ('complementary' if len(polarities)>1 else 'general-purpose')
    view = 'multi-unit' if count > 1 else 'single'
    props['ki_keywords'] = f'transistor BJT {" ".join(polarities)} {selection} {view} {device["package"]} SMD'
    props['ki_fp_filters'] = device['footprint'].split(':')[1].replace('-', '?') + '*'
    if count > 1:
        props['ki_locked'] = ''
    out = [f'\t(symbol "{name}"', '\t\t(pin_names (offset 0) (hide yes))',
           '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)']
    for key, value in props.items():
        visible = key in ('Reference', 'Value')
        x,y = (prop_x, prop_y + (1.905 if key=='Reference' else 0)) if visible else (0,0)
        effects = '(font (size 1.27 1.27))' + (' (justify left)' if visible else '')
        effects += '' if visible else ' (hide yes)'
        out.append(f'\t\t(property {json.dumps(key)} {json.dumps(value, ensure_ascii=False)} (at {x:g} {y:g} 0) (effects {effects}))')
    for i, t in enumerate(device['transistors']):
        out.append(f'\t\t(symbol "{name}_{i+1}_1"')
        def point(a, b):
            return f'{a:g} {b:g}'
        def line(points, width=0, fill='none'):
            out.append('\t\t\t(polyline (pts '+ ' '.join(f'(xy {point(a,b)})' for a,b in points)+f') (stroke (width {width}) (type default)) (fill (type {fill})))')
        line([(-2.54,0),(.635,0)])
        line([(.635,1.905),(.635,-1.905)],.508)
        line([(.635,.635),(2.54,2.54)])
        line([(.635,-.635),(2.54,-2.54)])
        arrow = [(1.27,-1.778),(1.778,-1.27),(2.286,-2.286),(1.27,-1.778)] if t['polarity']=='NPN' else [(1.016,-1.016),(1.524,-2.032),(2.032,-1.524),(1.016,-1.016)]
        line(arrow,fill='outline')
        out.append(f'\t\t\t(circle (center {point(1.27,0)}) (radius 2.8194) (stroke (width 0.254) (type default)) (fill (type none)))')
        terminals = [('B',t['b'],-5.08,0,0,'input',False),('E',t['e'],2.54,-5.08,90,'passive',False)]
        terminals += [('C',p,2.54,5.08,270,'passive',j>0) for j,p in enumerate(t['c'])]
        for terminal,number,a,b,angle,kind,hidden in terminals:
            hide=' (hide yes)' if hidden else ''
            out.append(f'\t\t\t(pin {kind} line (at {point(a,b)} {angle}) (length 2.54){hide} (name "{terminal}" (effects (font (size 1.27 1.27)))) (number "{number}" (effects (font (size 1.27 1.27)))))')
        out.append('\t\t)')
    out.append('\t)')
    return '\n'.join(out)


def main():
    devices = json.loads(CATALOG.read_text(encoding='utf-8'))
    names = {d['name'] + suffix for d in devices for suffix in ('', '_Pair', '_Array')}
    text = LIBRARY.read_text(encoding='utf-8')
    # Existing entries use a single tab at the top symbol level.
    blocks = re.split(r'(?=^\t\(symbol ")', text, flags=re.M)
    header, existing = blocks[0], []
    for block in blocks[1:]:
        name = re.match(r'\t\(symbol "([^"]+)"', block)[1]
        if name not in names:
            existing.append(block.rstrip().removesuffix('\n)').rstrip())
    added = [symbol(d) for d in devices]
    LIBRARY.write_text(header + '\n'.join(existing+added) + '\n)\n',encoding='utf-8',newline='\n')
    print(f'Generated {len(added)} symbols for {len(devices)} physical devices.')


if __name__ == '__main__':
    main()
