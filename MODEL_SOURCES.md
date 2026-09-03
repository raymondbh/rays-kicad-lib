# SPICE model sources

This document records the provenance and intended use of every public model in
the distributed SPICE libraries. Model names marked as planned are retained for
symbols that will be added later.

## `spice/BJT_NPN.lib`

| Model | Status | Provenance |
|---|---|---|
| `BD139` | Planned symbol | Historical imported model; exact source not recorded |
| `BD175` | Used | Historical imported model; exact source not recorded |
| `2N3904` | Used | Historical Philips-tagged model; exact source not recorded |
| `2N5551` | Used | Historical NSC-tagged model; exact source not recorded |
| `BC847A` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC847B` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC847C` | Used | Historical Philips-tagged model; exact source not recorded |

## `spice/BJT_PNP.lib`

| Model | Status | Provenance |
|---|---|---|
| `BD140` | Planned symbol | Historical imported model; exact source not recorded |
| `BD176` | Used | Historical imported model; exact source not recorded |
| `2N3906` | Used | Historical Philips-tagged model; exact source not recorded |
| `2N5401` | Used | Historical Fairchild-tagged model; exact source not recorded |
| `BC857A` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC857B` | Used | Historical Philips-tagged model; exact source not recorded |
| `BC857C` | Used | Historical Philips-tagged model; exact source not recorded |

## `spice/Diodes.lib`

| Model | Status | Provenance |
|---|---|---|
| `1N5817`, `1N5818`, `1N5819` | Planned symbols | Historical imported models; exact source not recorded |
| `PDZ12B` | Planned symbol | Historical imported model; exact source not recorded |
| `LED_RED`, `LED_GREEN`, `LED_BLUE`, `LED_WHITE` | Used | Generic models calibrated to the documented forward voltage at 20 mA |
| `BZX55C2V7`, `BZX55C3V6`, `BZX55C5V1`, `BZX55C6V2`, `BZX55C18`, `BZX55C30`, `BZX55C68` | Used | Converted and calibrated from the Vishay PSpice files identified in the library comments |
| `1N4001` through `1N4007` | Used | Generic family models with rated reverse-voltage parameters |

The Vishay PSpice topology was preserved, the `POLY(1)` source was converted to
an ngspice-compatible behavioral source, and each breakdown offset was
calibrated at the data-sheet test current. Original source URLs and attribution
are retained beside each subcircuit.

## `spice/Passives.lib`

| Model | Status | Provenance |
|---|---|---|
| `POTLIN` | Used | Generic parameterized linear potentiometer model created for this library |

## Redistribution note

The repository itself is MIT licensed. Historical imported and manufacturer
model files may have separate terms. Their redistribution status must be
confirmed before submitting this package to KiCad's official public PCM
repository. This first package is intended for a project-hosted GitHub release.
