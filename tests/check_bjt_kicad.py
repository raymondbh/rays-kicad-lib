#!/usr/bin/env python3
"""Exercise actual KiCad exports for every SMD BJT view and an unplaced unit."""

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
sys.path.insert(0, str(ROOT / 'tools'))
from kicad_sexpr import parse, children, child, properties


def uid():
    return str(uuid.uuid4())


def schematic(block, name, output, only_first=False):
    symbol = parse(block)
    props = properties(symbol)
    root_id = uid()
    stem = output.stem
    lib_id = 'rayslib-bjt-smd:' + name
    embedded = block.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    units = sorted({int(s[1].rsplit('_', 2)[1]) for s in children(symbol,'symbol')} - {0})
    if only_first:
        units = units[:1]
    out = [f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root_id}) (paper "A4")',
           '(lib_symbols ' + embedded + ')']
    for j, unit in enumerate(units):
        x,y = 55+j%2*100, 55+j//2*80
        pins = []
        for body in children(symbol, 'symbol'):
            if int(body[1].rsplit('_',2)[1]) in (0,unit):
                pins += children(body,'pin')
        positions = {}
        for p in pins:
            at = child(p,'at')
            positions.setdefault((float(at[1]),float(at[2])), []).append(int(child(p,'number')[1]))
        for (a,b),numbers in positions.items():
            out.append(f'(label "P{min(numbers)}" (at {x+a:g} {y-b:g} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {uid()}))')
        out.append(f'(symbol (lib_id "{lib_id}") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid {uid()})')
        for key,value in props.items():
            if key == 'Reference': value='Q1'
            out.append(f'(property {json.dumps(key)} {json.dumps(value,ensure_ascii=False)} (at {x+7} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        for p in pins:
            out.append(f'(pin "{child(p,"number")[1]}" (uuid {uid()}))')
        out.append(f'(instances (project "{stem}" (path "/{root_id}" (reference "Q1") (unit {unit})))))')
    out += ['(embedded_fonts no)', ')']
    output.write_text('\n'.join(out)+'\n',encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-cli', default='kicad-cli')
    parser.add_argument('--output', type=Path, default=ROOT/'dist/bjt-kicad')
    parser.add_argument('--devices', nargs='*')
    args = parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    env = dict(os.environ, KICAD_RAYSLIB=ROOT.as_posix(),
               KICAD_CONFIG_HOME=(args.output/'config').resolve().as_posix(),
               KICAD_DOCUMENTS_HOME=(args.output/'documents').resolve().as_posix())
    lib = (ROOT/'symbol/rayslib-bjt-smd.kicad_sym').read_text(encoding='utf8')
    blocks = {}
    for block in re.split(r'(?=^\t\(symbol ")',lib,flags=re.M)[1:]:
        name = re.match(r'\t\(symbol "([^"]+)"',block)[1]
        blocks[name] = block.rstrip().removesuffix('\n)').strip()
    devices = json.loads((ROOT/'tools/bjt_catalog.json').read_text(encoding='utf8'))
    count = 0
    for device in devices:
        if args.devices and device['name'] not in args.devices: continue
        expected = {}
        for t in device['transistors']:
            for p in t['c']: expected[str(p)] = f'P{min(t["c"])}'
            for p in [t['b'],t['e']]:expected[str(p)] = f'P{p}'
        for name in [device['name']]:
            path = args.output/(name+'.kicad_sch')
            schematic(blocks[name],name,path)
            for fmt,ext in [('spice','.cir'),('kicadxml','.xml')]:
                result = subprocess.run([args.kicad_cli,'sch','export','netlist','--format',fmt,'-o',str(path.with_suffix(ext)),str(path)],env=env,capture_output=True,text=True,timeout=60)
                if result.returncode: raise RuntimeError(result.stdout+result.stderr)
            spice = path.with_suffix('.cir').read_text()
            instances = [line.split() for line in spice.splitlines() if re.match(r'^XQ1\s',line,re.I)]
            assert len(instances)==1, (name,spice)
            assert [p.lstrip('/') for p in instances[0][1:-1]]==[expected[p] for p in sorted(expected,key=int)],(name,spice)
            assert instances[0][-1]==device['name'],(name,spice)
            root=ET.parse(path.with_suffix('.xml')).getroot()
            comps=root.findall('./components/comp')
            assert len(comps)==1 and comps[0].get('ref')=='Q1',name
            assert comps[0].findtext('value')==device['name'],name
            assert comps[0].findtext('footprint')==device['footprint'],name
            actual={n.get('pin'):net.get('name').lstrip('/') for net in root.findall('./nets/net') for n in net.findall('node') if n.get('ref')=='Q1'}
            assert actual==expected,(name,actual,expected)
            count+=1
            print('PASS',name,'SPICE pin order, one PCB/BOM component',flush=True)
    # Omit B and verify it is not shorted to A or duplicated as a package.
    name='BCM847DS'
    path=args.output/'BCM847DS_unused.kicad_sch'
    schematic(blocks[name],name,path,only_first=True)
    result=subprocess.run([args.kicad_cli,'sch','export','netlist','--format','spice','-o',str(path.with_suffix('.cir')),str(path)],env=env,capture_output=True,text=True,timeout=60)
    assert result.returncode==0,result.stderr
    text=path.with_suffix('.cir').read_text()
    rows=[line.split() for line in text.splitlines() if re.match(r'^XQ1\s',line,re.I)]
    assert len(rows)==1,text
    nodes=[p.lstrip('/') for p in rows[0][1:-1]]
    assert len(nodes)==6 and [nodes[i] for i in (0,1,5)]==['P1','P2','P6'],text
    assert len(set(nodes))==6,text
    print(f'PASS {count} views and unplaced unit B')


if __name__=='__main__':
    main()
