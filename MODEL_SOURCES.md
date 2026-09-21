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
calibrated at the data-sheet test current. Original source URLs and attribution
are retained beside each subcircuit.

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

## Redistribution note

The repository itself is MIT licensed. Historical imported and manufacturer
model files may have separate terms. Their redistribution status must be
confirmed before submitting this package to KiCad's official public PCM
repository. This first package is intended for a project-hosted GitHub release.
