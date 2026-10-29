# NE555 timer

`rayslib-timer-tht:NE555P` represents the Texas Instruments bipolar timer in
PDIP-8. The footprint is `Package_DIP:DIP-8_W7.62mm`. Recommended supply limits
are 4.5 to 16 V; electrical characteristics are specified at 5 to 15 V in
[TI SLFS022K](https://www.ti.com/lit/ds/symlink/ne555.pdf).

| Physical pin | Signal | Model terminal |
|---|---|---|
| 1 | GND | VSS |
| 2 | TRIG | TRIG |
| 3 | OUT | OUT |
| 4 | RESET, active low | RESET |
| 5 | CONT | CONT |
| 6 | THRES | THRES |
| 7 | DISCH, open collector | DISCH |
| 8 | VCC | VCC |

`spice/Timers.lib` contains one eight-terminal subcircuit, `NE555P`, in physical
pin order. `Sim.Pins` explicitly maps every terminal. The internal ground port
is named VSS to avoid ngspice's special treatment of the name GND. Pin 1 must
be wired; the model also supports circuits whose local ground is above 0 V.

## Simulation setup

Use transient analysis. A free-running oscillator has no stable DC operating
point. Start with a supply ramp or briefly pull RESET low so ngspice can find
a defined initial state. No `UIC`, PSpice compatibility setting, XSPICE code
model or external digital library is required with these startup conditions.
An ideal DC supply with RESET tied high can require operating-point recovery;
do not rely on its initial output state.

For example, this astable circuit runs at approximately 138 Hz:

```spice
NE555P astable example
.include spice/Timers.lib
VCC vcc 0 5
VRESET reset 0 PULSE(0 5 10u 100n 100n 1 2)
RA vcc discharge 10k
RB discharge timing 47k
CT timing 0 100n
CC control 0 10n
RL output 0 1k
XU1 0 timing output reset control timing discharge vcc NE555P
.tran 1u 40m
.print tran v(output) v(timing)
.end
```

The RESET pulse is low initially and then stays high throughout this analysis.
Alternatively, tie RESET to VCC and use `PWL(0 0 10u 0 110u 5)` for the supply.
In KiCad, use the corresponding voltage-source waveforms and connect the eight
symbol pins as shown above. Start with a maximum transient step of 1 us for
this example; smaller timing capacitors require shorter steps.

In astable operation, the ideal high and low times are approximately
`ln(2) * (RA + RB) * CT` and `ln(2) * RB * CT`. The finite discharge resistance
causes a small deviation, especially with a low RA value. In monostable
operation, connect THRES and DISCH to the timing capacitor, charge it through
RT from VCC and apply a short negative pulse to TRIG. Pulse length is
approximately `ln(3) * RT * CT`; release TRIG before the timing interval ends.
Give unused inputs a defined voltage. A 10 nF bypass on CONT is a suitable
starting point when no external control voltage is used.

## Model scope and regression checks

This is a repository-authored nominal behavioral approximation based on TI's
functional description, not a TI-supplied or transistor-level model. It includes
the three 5 kohm divider resistors, approximately 1/3 and 2/3 supply thresholds,
CONT loading, latch memory, trigger priority over threshold, reset priority,
an open-collector discharge switch and a bipolar output with finite drive.

The output has approximately 1.4 V source headroom, 3 ohm source resistance and
15 ohm sink resistance at small currents, with soft 200 mA limits. The discharge
switch is approximated by 18 ohm on-resistance. These are nominal approximations,
not guarantees at all loads. Fixed internal time constants and an effective
1 nF output capacitance stabilize transitions; this is not a measured terminal
capacitance. Use the model for timing and ordinary resistive loads, not accurate
edge shapes or maximum-frequency analysis.

`python tests/check_timer_models.py` checks astable high/low times, capacitor
thresholds, monostable pulse width and rearming, repeated triggers, latch memory,
RESET and TRIG priorities, CONT modulation, supply-ramp startup, output sourcing
and sinking at 20 mA, and discharge at 8 mA. Core cases run at 5, 9 and 15 V.
Additional cases cover local ground offset, resistor ratio changes and
approximately 14 Hz to 1.4 kHz oscillation. Timing checks allow 3% deviation
from the ideal RC formulas; these are regression tolerances, not hardware limits.

`python tests/check_timer_kicad.py --kicad-cli kicad-cli` verifies the physical
pins, model path, SPICE order and PCB footprint through KiCad 10 netlist exports,
then simulates the exported instance in the astable test circuit. Both test
scripts accept `--dll` or use `NGSPICE_DLL` through `tools/run_ngspice.py`.
Generated fixtures and logs are stored under `dist/`.

Input bias currents, input protection, temperature variation, manufacturing
spread, power-on state, self-heating, supply-current spikes, overload and
short-circuit behavior are not characterized. Supply current is only a nominal
approximation. The model is not qualified outside the tested operating range,
for driving large reactive loads or for use as a CMOS 555 substitute.
