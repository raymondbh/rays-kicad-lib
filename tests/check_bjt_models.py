#!/usr/bin/env python3
"""Measure each transistor at its data-sheet gain point using ngspice."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def switching_deck(devices):
    deck=['Independent BJT unit switching and isolation',
          f'.include "{(ROOT/"spice/BJT_Arrays.lib").as_posix()}"','.temp 25']
    checks=[]
    index=0
    for d in devices:
        nodes={}
        first = index
        for t in d['transistors']:
            tag=f't{index}'
            sign=1 if t['polarity']=='NPN' else -1
            # Give each transistor a separate time slot; its partner stays off.
            delay=10*(index+1)
            for p in t['c']:nodes[p]=tag+'c'
            nodes[t['b']]=tag+'b';nodes[t['e']]='0'
            deck += [f'VS{index} {tag}s 0 {5*sign}',
                     f'VD{index} {tag}d 0 PULSE(0 {5*sign} {delay}u 10n 10n 4u 1m)',
                     f'RB{index} {tag}d {tag}b 10k',f'RC{index} {tag}s {tag}c 2k']
            checks += [f'let on{index} = 999',f'let off{index} = 999',
                       f'meas tran on{index} FIND v({tag}c) AT={delay+2}u',
                       f'meas tran off{index} FIND v({tag}c) AT={delay-2}u',
                       f'if abs(on{index}) > 0.35 | abs(off{index}-{5*sign}) > 0.02',
                       f'  echo FAIL: {d["name"]} transistor {index} on/off or unit isolation',
                       '  quit 1','end']
            index+=1
        for i, t in enumerate(d['transistors'], first):
            sign = 1 if t['polarity'] == 'NPN' else -1
            for other in range(first, index):
                if other == i:
                    continue
                checks += [f'let isolated{i}_{other} = 999',
                           f'meas tran isolated{i}_{other} FIND v(t{i}c) AT={10*(other+1)+2}u',
                           f'if abs(isolated{i}_{other}-{5*sign}) > 0.02',
                           f'  echo FAIL: {d["name"]} inactive unit responds to its partner',
                           '  quit 1', 'end']
        deck += ['X'+d['name']+' '+' '.join(nodes[p] for p in sorted(nodes))+' '+d['name']]
    deck += ['.control','set noaskquit',f'tran 20n {10*(index+1)}u']+checks
    deck += [f'echo PASS: independent transient switching of {index} transistors','quit 0','.endc','.end']
    return deck


def pair_deck(devices):
    deck=['Matched pair current mirror and differential transfer',
          f'.include "{(ROOT/"spice/BJT_Arrays.lib").as_posix()}"','.temp 25','VDIFF differential 0 0']
    checks=[]
    for d in devices:
        if not d['matched']:continue
        n=d['name'];sign=1 if d['transistors'][0]['polarity']=='NPN' else -1
        nodes={}
        for i,t in enumerate(d['transistors']):
            for p in t['c']:nodes[p]=n+'base' if i==0 else n+'out'
            nodes[t['b']]=n+'base';nodes[t['e']]='0'
        # Equal collector voltages isolate matching from Early-effect error.
        deck += [f'I{n} 0 {n}base {sign*.001}',f'EM{n} {n}out 0 {n}base 0 1',
                 'XM'+n+' '+' '.join(nodes[p] for p in sorted(nodes))+' '+n]
        # A second package forms a differential pair, with independently sensed collectors.
        nodes={}
        for i,t in enumerate(d['transistors']):
            for p in t['c']:nodes[p]=n+f'c{i}'
            nodes[t['b']]=n+'b' if i==0 else '0';nodes[t['e']]=n+'tail'
            deck += [f'VC{n}{i} {n}c{i} 0 {sign*5}']
        deck += [f'E{n} {n}b 0 differential 0 {sign}',f'IT{n} {n}tail 0 {sign*.002}',
                 'XD'+n+' '+' '.join(nodes[p] for p in sorted(nodes))+' '+n]
        checks += [f'let mirror_{n} = abs(i(EM{n}))/0.001',
                   f'if mirror_{n} < 0.9 | mirror_{n} > 1.1',
                   f'  echo FAIL: {n} current mirror','  quit 1','end']
    deck += ['.control','set noaskquit','op']+checks
    deck += ['dc VDIFF -0.1 0.1 0.001']
    for d in devices:
        if not d['matched']:continue
        n=d['name']
        deck += [f'let a_{n} = abs(i(VC{n}0))',f'let b_{n} = abs(i(VC{n}1))',
                 f'let diff_{n} = a_{n}-b_{n}',
                 f'let midpoint_{n} = 999',
                 f'meas dc midpoint_{n} FIND diff_{n} AT=0',
                 f'if abs(midpoint_{n}) > 1u | diff_{n}[0] > -0.0018 | diff_{n}[200] < 0.0018',
                 f'  echo FAIL: {n} differential pair balance or steering','  quit 1','end']
    deck += ['echo PASS: six nominal matched current mirrors and differential pairs','quit 0','.endc','.end']
    return deck


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dll')
    args=parser.parse_args()
    devices=json.loads((ROOT/'tools/bjt_catalog.json').read_text(encoding='utf8'))
    out=ROOT/'dist/bjt-tests'
    out.mkdir(parents=True,exist_ok=True)
    deck=['BJT array data-sheet gain and pin mapping regression',
          f'.include "{(ROOT/"spice/BJT_Arrays.lib").as_posix()}"',
          '.temp 25', 'VSWEEP drive 0 0']
    checks=[]
    index=0
    for d in devices:
        nodes={}
        for t in d['transistors']:
            tag=f't{index}'
            sign=1 if t['polarity']=='NPN' else -1
            for p in t['c']:nodes[p]=tag+'c'
            nodes[t['b']]=tag+'b';nodes[t['e']]='0'
            deck += [f'VC{index} {tag}c 0 {sign*d["gain_vce"]}',f'EB{index} {tag}b 0 drive 0 {sign}']
            checks += [f'let ic{index} = abs(i(VC{index}))',
                       f'let gain{index} = abs(i(VC{index})/i(EB{index}))',
                       f'let h{index} = -1',
                       f'meas dc h{index} FIND gain{index} WHEN ic{index}={d["gain_ic"]} CROSS=1',
                       f'if h{index} < {d["gain"][0]}'+(f' | h{index} > {d["gain"][1]}' if d['gain'][1] else ''),
                       f'  echo FAIL: {d["name"]} transistor {tag} hFE outside data-sheet limits',
                       '  let failures = failures + 1','end']
            index+=1
        deck+=['X'+d['name']+' '+' '.join(nodes[p] for p in sorted(nodes))+' '+d['name']]
    deck+=['.control','set noaskquit','dc VSWEEP 0.3 1.2 0.001','let failures = 0']+checks
    deck+=['if failures > 0','  quit 1','end',f'echo PASS: {index} transistors at data-sheet hFE test points','quit 0','.endc','.end']
    for name,lines in [('gain',deck),('switching',switching_deck(devices)),('pairs',pair_deck(devices))]:
        path=out/(name+'.cir');path.write_text('\n'.join(lines)+'\n',encoding='utf8')
        command=[sys.executable,str(ROOT/'tools/run_ngspice.py'),str(path)]
        if args.dll:command+=['--dll',args.dll]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        log=result.stdout+result.stderr
        (out/(name+'.log')).write_text(log,encoding='utf8')
        if result.returncode:
            print(log)
            return result.returncode
        for line in log.splitlines():
            if 'PASS:' in line:print(line)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
