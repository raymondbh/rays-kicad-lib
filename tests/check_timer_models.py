#!/usr/bin/env python3
"""Check NE555 timing, latch priorities and loaded outputs with ngspice."""

import argparse
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def measurement(name, command, low, high):
    """Initialize a sentinel so a missing measurement cannot pass a check."""
    return [f'let {name} = 1e99', f'meas tran {name} {command}',
            f'if {name} < {low:.12g} | {name} > {high:.12g}',
            f'  echo FAIL: {name} outside {low:.8g} to {high:.8g}',
            '  quit 1', 'end']


def header(title):
    return [title, f'.include "{(ROOT / "spice/Timers.lib").as_posix()}"', '.temp 25']


def astable_deck(supply, *, ramp=False, control=None, offset=0, ra=10000, rb=47000,
                 capacitance=1e-7, instance=None):
    """Also accept a real KiCad-exported instance with the P1..P8 net labels."""
    period = math.log(2) * (ra + 2 * rb) * capacitance
    stop = 7 * period
    low_ratio, high_ratio = (1/3, 2/3) if control is None else (control/2, control)
    high_time = (ra + rb) * capacitance * math.log((1-low_ratio)/(1-high_ratio))
    low_time = rb * capacitance * math.log(high_ratio/low_ratio)
    title = f'NE555 astable {supply}V ramp={ramp} control={control} offset={offset}'
    deck = header(title) + [f'VGND P1 0 {offset}']
    deck += [f'VCC P8 P1 ' + (f'PWL(0 0 10u 0 110u {supply})' if ramp else str(supply)),
             # An explicit reset makes the initial DC state deterministic.
             ('RRESET P4 P8 1' if ramp else f'VRESET P4 P1 PULSE(0 {supply} 10u 100n 100n 1 2)'),
             f'RA P8 P7 {ra}', f'RB P7 P6 {rb}', 'RJOIN P6 P2 1m',
             f'CT P6 P1 {capacitance}', 'CC P5 P1 10n', 'RL P3 P1 1k',
             instance or 'XU1 P1 P2 P3 P4 P5 P6 P7 P8 NE555P']
    if control is not None:
        deck += [f'VCTRL P5 P1 {supply * control}']
    deck += ['.control', 'set noaskquit', f'tran {period/2000:.12g} {stop:.12g}',
             'let out = v(P3)-v(P1)', 'let timing = v(P6)-v(P1)']
    edge = (supply - 1.4) / 2
    # With the output initially low, rising/falling edges have the same index.
    checks = measurement('high_time', f'TRIG out VAL={edge} RISE=3 TARG out VAL={edge} FALL=3',
                         high_time * .97, high_time * 1.03)
    checks += measurement('low_time', f'TRIG out VAL={edge} FALL=3 TARG out VAL={edge} RISE=4',
                          low_time * .97, low_time * 1.03)
    checks += measurement('cap_low', f'MIN timing FROM={stop*.6} TO={stop}',
                          supply*low_ratio-.03, supply*low_ratio+.03)
    checks += measurement('cap_high', f'MAX timing FROM={stop*.6} TO={stop}',
                          supply*high_ratio-.03, supply*high_ratio+.03)
    checks += measurement('rise_time', f'WHEN out={edge} RISE=3', 0, stop)
    checks += measurement('fall_time', f'WHEN out={edge} FALL=3', 0, stop)
    # Check settled load voltages, independently of switching overshoot.
    checks += [f'let sample_high = rise_time + {high_time/2:.12g}',
               f'let sample_low = fall_time + {low_time/2:.12g}']
    checks += measurement('out_high', 'FIND out AT=$&sample_high', supply-1.7, supply-1.3)
    checks += measurement('out_low', 'FIND out AT=$&sample_low', -.01, .1)
    return deck + checks + [f'echo PASS: {title}', 'quit 0', '.endc', '.end']


def monostable_deck(supply):
    deck = header(f'NE555 monostable {supply}V') + [
        f'VCC vcc 0 {supply}', f'VR reset 0 PULSE(0 {supply} 10u 100n 100n 1 2)',
        # The second trigger during a pulse must not restart the timing interval.
        f'VT trig 0 PWL(0 {supply} 1m {supply} 1.0001m 0 1.02m 0 1.0201m {supply}'
        f' 2m {supply} 2.0001m 0 2.02m 0 2.0201m {supply}'
        f' 10m {supply} 10.0001m 0 10.02m 0 10.0201m {supply})',
        'RT vcc timing 47k', 'CT timing 0 100n', 'CC ctrl 0 10n', 'RL out 0 1k',
        'XU1 0 trig out reset ctrl timing timing vcc NE555P',
        '.control', 'set noaskquit', 'tran 2u 18m']
    expected = math.log(3) * 47000 * 1e-7
    for i in (1, 2):
        deck += measurement(f'pulse{i}', f'TRIG v(out) VAL={(supply-1.4)/2} RISE={i}'
                             f' TARG v(out) VAL={(supply-1.4)/2} FALL={i}', expected*.97, expected*1.03)
    deck += measurement('idle', 'FIND v(out) AT=8m', -.01, .1)
    deck += measurement('discharged', 'FIND v(timing) AT=8m', 0, .03)
    return deck + [f'echo PASS: monostable {supply}V width, repeated trigger, discharge, rearm',
                   'quit 0', '.endc', '.end']


def latch_deck(supply):
    mid = supply/2
    high = supply*.9
    deck = header(f'NE555 latch {supply}V') + [
        f'VCC vcc 0 {supply}',
        f'VR reset 0 PWL(0 0 .1m 0 .1001m {supply} 3.5m {supply} 3.5001m 0'
        f' 4m 0 4.0001m {supply})',
        f'VT trig 0 PWL(0 {mid} 1m {mid} 1.0001m 0 1.2m 0 1.2001m {mid}'
        f' 3m {mid} 3.0001m 0 4.5m 0 4.5001m {mid})',
        f'VH thres 0 PWL(0 {mid} 2m {mid} 2.0001m {high} 2.2m {high}'
        f' 2.2001m {mid} 3m {mid} 3.0001m {high})',
        'CC ctrl 0 10n', 'RL out 0 1k', 'RD vcc dis 10k',
        'XU1 0 trig out reset ctrl thres dis vcc NE555P',
        '.control', 'set noaskquit', 'tran 1u 5m']
    for i, (time, is_high) in enumerate([(0.5, False), (1.1, True), (1.5, True),
                                        (2.1, False), (2.5, False), (3.2, True),
                                        (3.7, False), (4.2, True), (4.7, False)]):
        deck += measurement(f'output{i}', f'FIND v(out) AT={time}m',
                             supply-1.7 if is_high else -.01, supply-1.3 if is_high else .1)
        deck += measurement(f'discharge{i}', f'FIND v(dis) AT={time}m',
                             supply-.01 if is_high else 0, supply+.01 if is_high else .03)
    return deck + [f'echo PASS: latch {supply}V hold, TRIG priority, RESET priority, discharge',
                   'quit 0', '.endc', '.end']


def loaded_deck(supply):
    deck = header(f'NE555 loaded outputs {supply}V') + [
        f'VCC vcc 0 {supply}',
        'ISOURCE out_h 0 20m', 'ISINK vcc out_l 20m', 'IDIS vcc dis_l 8m',
        'XHIGH 0 0 out_h vcc ctrl_h 0 dis_h vcc NE555P',
        'XLOW 0 vcc out_l 0 ctrl_l 0 dis_l vcc NE555P',
        '.control', 'set noaskquit', 'tran 100n 10u']
    deck += measurement('source_voltage', 'FIND v(out_h) AT=9u', supply-1.7, supply-1.3)
    deck += measurement('sink_voltage', 'FIND v(out_l) AT=9u', 0, .4)
    deck += measurement('discharge_voltage', 'FIND v(dis_l) AT=9u', .05, .4)
    return deck + [f'echo PASS: loaded {supply}V source/sink at 20mA, discharge at 8mA',
                   'quit 0', '.endc', '.end']


def run_deck(name, lines, output, dll=None):
    output.mkdir(parents=True, exist_ok=True)
    path = output / (name + '.cir')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    command = [sys.executable, str(ROOT/'tools/run_ngspice.py'), str(path)]
    if dll:
        command += ['--dll', dll]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
    log = result.stdout + result.stderr
    (output/(name+'.log')).write_text(log, encoding='utf-8')
    if result.returncode or 'PASS:' not in log:
        raise RuntimeError(log)
    for line in log.splitlines():
        if 'PASS:' in line:
            print(line, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dll')
    args = parser.parse_args()
    output = ROOT/'dist/timer-tests'
    for supply in (5, 9, 15):
        for name, lines in [('astable', astable_deck(supply)),
                            ('ramp', astable_deck(supply, ramp=True)),
                            ('control', astable_deck(supply, control=.5)),
                            ('monostable', monostable_deck(supply)),
                            ('latch', latch_deck(supply)), ('loaded', loaded_deck(supply))]:
            run_deck(f'{name}_{supply}V', lines, output, args.dll)
    run_deck('floating_ground', astable_deck(5, offset=3), output, args.dll)
    run_deck('slow', astable_deck(5, capacitance=1e-6), output, args.dll)
    run_deck('fast', astable_deck(5, capacitance=1e-8), output, args.dll)
    run_deck('equal_resistors', astable_deck(5, ra=22000, rb=22000), output, args.dll)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
