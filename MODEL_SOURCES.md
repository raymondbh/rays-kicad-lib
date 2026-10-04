# SPICE model sources

This document records the provenance and intended use of every public model in
the distributed SPICE libraries. Every public model is used by a distributed
symbol and exercised by the ngspice smoke test.

## `spice/BJT_NPN.lib`

| Model | Status | Provenance |
|---|---|---|
| `BD139` | Used | Historical imported model; exact source not recorded |
| `BD175` | Used | Historical imported model; exact source not recorded |
| `2N3904` | Used | Historical Philips-tagged model; exact source not recorded |
| `2N5551` | Used | Historical NSC-tagged model; exact source not recorded |
| `BC847A` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC847B` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC847C` | Used | Historical Philips-tagged model; exact source not recorded |

## `spice/BJT_PNP.lib`

| Model | Status | Provenance |
|---|---|---|
| `BD140` | Used | Historical imported model; exact source not recorded |
| `BD176` | Used | Historical imported model; exact source not recorded |
| `2N3906` | Used | Historical Philips-tagged model; exact source not recorded |
| `2N5401` | Used | Historical Fairchild-tagged model; exact source not recorded |
| `BC857A` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC857B` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC857C` | Used | Historical Philips-tagged model; exact source not recorded |

## `spice/Diodes.lib`

| Model | Status | Provenance |
|---|---|---|
| `1N5817`, `1N5818`, `1N5819` | Used | Historical imported models; exact source not recorded |
| `PDZ12B` | Used | Historical imported model; exact source not recorded |
| `1N4148` | Used | Generic switching model calibrated to the official Vishay data sheet |
| `1N4742A` | Used | Generic DC model calibrated to the official Vishay data sheet; no manufacturer SPICE model is bundled |
| `LED_RED`, `LED_GREEN`, `LED_BLUE`, `LED_WHITE` | Used | Generic models calibrated to the documented forward voltage at 20 mA |
| `BZX55C2V7`, `BZX55C3V6`, `BZX55C5V1`, `BZX55C6V2`, `BZX55C18`, `BZX55C30`, `BZX55C68` | Used | Converted and calibrated from the Vishay PSpice files identified in the library comments |
| `BZX55C10` | Used | Generic DC model calibrated to the official Vishay data sheet; no manufacturer SPICE model is published |
| `1N4001` through `1N4007` | Used | Generic family models with rated reverse-voltage parameters |

The Vishay PSpice topology was preserved, the `POLY(1)` source was converted to
an ngspice-compatible behavioral source, and each breakdown offset was
calibrated at selected nominal operating points. Original source URLs and attribution
are retained beside each subcircuit.

The October 2026 symbol metadata review uses the current
[Vishay BZX55 data sheet](https://www.vishay.com/docs/85604/bzx55.pdf): BZX55C30
is specified at 5 mA and BZX55C68 at 2.5 mA. Their previous descriptions used
2 mA and 1 mA. The model parameters were not changed or recalibrated during
this review; the revised descriptions do not establish a new model calibration.

## `spice/OpAmps.lib`

| Model | Status | Provenance |
|---|---|---|
| `UA741CP` | Used | Generic ngspice model calibrated to the official Texas Instruments UA741 data sheet |
| `TL072CP` | Used | Converted from the official Texas Instruments TL072 PSpice model (`SLOJ067`) |
| `LM358P` | Used | Generic ngspice model calibrated to the official Texas Instruments LM358 data sheet |

The public models use physical PDIP-8 pin order. PSpice-only polynomial sources
in the TL072 model were converted to ngspice-compatible behavioral sources, and
its original manufacturer comments and attribution are retained. The UA741 and
LM358 models are documented, ngspice-native educational macromodels.

The TL072CP description follows section 5.8 of
[TI TL07xx Rev. W](https://www.ti.com/lit/ds/symlink/tl072.pdf), which specifies
5.25 MHz typical GBW for the P package. The bundled SLOJ067 model dates from
1989 and was not refitted to that specification during the metadata review.

## `spice/Passives.lib`

| Model | Status | Provenance |
|---|---|---|
| `POTLIN` | Used | Generic parameterized linear potentiometer model created for this library |

## `spice/JFET.lib` and `spice/MOSFET.lib`

These five models are repository-authored, generic educational approximations,
not imported manufacturer SPICE models. Electrical envelopes and pin assignments
are taken from these onsemi data sheets:

| Models | Reference | TO-92 pins 1 / 2 / 3 |
|---|---|---|
| `2N3819` | [2N3819/D, Rev. 0](https://www.onsemi.com/download/data-sheet/pdf/2n3819-d.pdf) | S / G / D |
| `J111`, `J112`, `J113` | [MMBFJ113/D, Rev. 5, including TO-92 J111-J113](https://www.onsemi.com/download/data-sheet/pdf/mmbfj113-d.pdf) | D / S / G |
| `2N7000` | [2N7000/D, Rev. 8](https://www.onsemi.com/download/data-sheet/pdf/2n7000-d.pdf) | S / G / D |

The J111/J112 numbering is also shown explicitly in
[J111/D](https://www.onsemi.com/download/data-sheet/pdf/j111-d.pdf).
The symbols use `Package_TO_SOT_THT:TO-92_Inline_Wide`, matching the existing
THT transistor library's spread-lead footprint convention. Check the actual
manufacturer's pinout before substitution: the
[Central Semiconductor 2N3819](https://my.centralsemi.com/datasheets/2N3819.PDF)
uses D/G/S instead of the onsemi S/G/D assignment selected here.

The JFETs use native ngspice `NJF` models with D/G/S terminal order. KiCad calls
this device family `NJFET`, with `Sim.Type=SHICHMANHODGES`. The selected nominal
cutoff parameters are -4 V, -6 V, -3 V, and -1.5 V for 2N3819, J111, J112, and
J113 respectively. Their approximate zero-gate drain currents at 15 V are
10.5 mA, 112 mA, 47 mA, and 14 mA. These represent individual example devices,
not guaranteed typical values or production distributions.

The 2N7000 uses a three-terminal D/G/S subcircuit with a level-1 MOS channel,
its bulk tied to source, fixed capacitances, and an explicit body diode.
At 25 C it gives approximately 2.13 V threshold at 1 mA, 5.57 ohm on-resistance
at 4.5 V/75 mA, and 3.11 ohm at 10 V/500 mA (a pulsed test condition).

`tests/smoke/fets.cir` checks the data-sheet DC envelopes, JFET cutoff sweeps,
body-diode direction, and loaded 2N7000 switching. Capacitances are approximate;
these models are not characterized for RF performance, noise, switching losses,
gate charge, self-heating, temperature corners, or manufacturing spread. JFET
gate breakdown and MOSFET gate-oxide breakdown are not modeled. The MOSFET diode's
breakdown parameter does not qualify the model for avalanche-energy analysis.

## `spice/BJT_Arrays.lib`

These 16 package wrappers are repository-authored. Physical pin assignments,
footprints and gain reference conditions are listed in
[the SMD BJT notes](docs/BJT_ARRAYS.md), with manufacturer data-sheet links.
The numerical electrical models have the following origins:

| Package | Electrical model origin |
|---|---|
| `BCM847DS` | Two existing BC847B models; nominal matching approximation. |
| `BCM857DS` | Two existing BC857B models; nominal matching approximation. |
| `DMMT3904W` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/3320/DMMT3904W.spice.txt), unchanged apart from local model names and package wrapping. |
| `DMMT3906W` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/3322/DMMT3906W.spice.txt), unchanged apart from local model names and package wrapping. |
| `BC817DPN` | Repository-authored generic NPN/PNP models (BF=260, IKF=1 A); checked at 100 mA, 1 V. |
| `BC847BPN` | Existing BC847B and BC857B models; complementary approximation. |
| `DMMT5551` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/3324/DMMT5551.spice.txt), unchanged apart from local model names and package wrapping. |
| `DMMT5401` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/3323/DMMT5401.spice.txt), unchanged apart from local model names and package wrapping. |
| `MMDT5551` | DMMT5551 electrical parameters reused with the MMDT5551 pinout; a family approximation, not an exact manufacturer model. |
| `MMDT5401` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/2558/MMDT5401.spice.txt), unchanged apart from local model names and package wrapping. |
| `MMDT5501` | Repository-authored generic NPN/PNP models (BF=190, IKF=0.3 A); checked against UTC gain limits at 10 mA, 5 V. |
| `MMPQ6700` | Existing 2N3904/2N3906 models, corresponding to the transistor types referenced by the onsemi data sheet; package approximation. |
| `MMBT3904` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/2869/MMBT3904.spice.txt), unchanged apart from local model names and package wrapping. |
| `MMBT3906` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/2962/MMBT3906.spice.txt), unchanged apart from local model names and package wrapping. |
| `MMDT3904` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/2905/MMDT3904.spice.txt), unchanged apart from local model names and package wrapping. |
| `MMDT3906` | [Diodes manufacturer parameters](https://www.diodes.com/spice/download/2893/MMDT3906.spice.txt), unchanged apart from local model names and package wrapping. |

Manufacturer parameters retain their source attribution and applicable terms;
the wrapper does not make them repository-authored electrical models. Original
Diodes source URLs include the manufacturer's disclaimer and model metadata.

The approximations are for nominal bias, switching and teaching exercises.
Identical model copies give ideal nominal matching; no production spread,
thermal coupling, self-heating, avalanche rating or safe operating area is
represented. Global temperature is not a thermal connection between devices.
Capacitance, noise and temperature accuracy have not been qualified for the
approximations. Description ratings are hardware limits, not simulated clamps.

`tests/check_bjt_models.py` measures all 32 transistor sections at the selected
hFE test points, tests loaded switching and checks the six matched packages as
current mirrors and differential pairs. Mirror collectors use equal voltages
to separate nominal matching from Early-effect error. These regressions do not
establish full data-sheet compliance. `tests/check_bjt_kicad.py` verifies actual
KiCad SPICE/PCB exports, including package grouping and an omitted unit.

## Redistribution note

The repository itself is MIT licensed. Historical imported and manufacturer
model files may have separate terms. Their redistribution status must be
confirmed before submitting this package to KiCad's official public PCM
repository. This first package is intended for a project-hosted GitHub release.
