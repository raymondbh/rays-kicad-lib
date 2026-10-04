# SMD transistors and multi-unit packages

Each physical part has one library symbol. Duals have units A/B, and MMPQ6700
has units A/B/C/D. Place units with the same reference (for example Q1A/Q1B)
to obtain one footprint, one BOM component and one SPICE package instance.
Units can be moved, rotated and mirrored independently. Draw an optional
package outline directly in the schematic when it helps explain a circuit.
There are no combined `_Pair` or `_Array` symbols.

`Matched Pair` identifies a manufacturer-specified matched part, not a special
symbol layout. A shared package does not by itself imply guaranteed matching.
The bundled models use independent nominal BJTs: self-heating, thermal coupling
and production mismatch are not simulated. See [model sources](../MODEL_SOURCES.md).

## Physical pin assignments

Numbers below are physical package pins in C/B/E order. Unit order follows the
selected manufacturer's device numbering. Use the exact linked data sheet when
substituting parts: DMMT3904W and MMDT3904, for example, have different pinouts.

| Part and data sheet | Units: polarity C/B/E | KiCad footprint |
|---|---|---|
| [BCM847DS](https://assets.nexperia.com/documents/data-sheet/BCM847DS.pdf) (Nexperia) | A: NPN 6/2/1; B: NPN 3/5/4 | `Package_TO_SOT_SMD:SOT-23-6` |
| [BCM857DS](https://assets.nexperia.com/documents/data-sheet/BCM857DS.pdf) (Nexperia) | A: PNP 6/2/1; B: PNP 3/5/4 | `Package_TO_SOT_SMD:SOT-23-6` |
| [DMMT3904W](https://www.diodes.com/datasheet/download/DMMT3904W.pdf) (Diodes Incorporated) | A: NPN 3/2/4; B: NPN 6/1/5 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| [DMMT3906W](https://www.diodes.com/datasheet/download/DMMT3906W.pdf) (Diodes Incorporated) | A: PNP 3/2/4; B: PNP 6/1/5 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| [BC817DPN](https://assets.nexperia.com/documents/data-sheet/BC817DPN.pdf) (Nexperia) | A: NPN 6/2/1; B: PNP 3/5/4 | `Package_TO_SOT_SMD:SOT-23-6` |
| [BC847BPN](https://assets.nexperia.com/documents/data-sheet/BC847BPN.pdf) (Nexperia) | A: NPN 6/2/1; B: PNP 3/5/4 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| [DMMT5551](https://www.diodes.com/datasheet/download/DMMT5551.pdf) (Diodes Incorporated) | A: NPN 1/2/6; B: NPN 4/3/5 | `Package_TO_SOT_SMD:SOT-23-6` |
| [DMMT5401](https://www.diodes.com/datasheet/download/DMMT5401.pdf) (Diodes Incorporated) | A: PNP 1/2/6; B: PNP 4/3/5 | `Package_TO_SOT_SMD:SOT-23-6` |
| [MMDT5551](https://www.diodes.com/datasheet/download/MMDT5551.pdf) (Diodes Incorporated) | A: NPN 6/2/1; B: NPN 3/5/4 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| [MMDT5401](https://www.diodes.com/datasheet/download/MMDT5401.pdf) (Diodes Incorporated) | A: PNP 6/2/1; B: PNP 3/5/4 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| [MMDT5501](https://www.unisonic.com.tw/uploadfiles/836/part_no_pdf/MMDT5501.pdf) (UTC) | A: NPN 6/2/1; B: PNP 3/5/4 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| [MMPQ6700](https://www.onsemi.com/download/data-sheet/pdf/mmpq6700-fcs-d.pdf) (onsemi) | A: NPN 1+2/15/16; B: NPN 3+4/13/14; C: PNP 5+6/11/12; D: PNP 7+8/9/10 | `Package_SO:SOIC-16_3.9x9.9mm_P1.27mm` |
| [MMBT3904](https://www.diodes.com/datasheet/download/MMBT3904.pdf) (Diodes Incorporated) | A: NPN 3/1/2 | `Package_TO_SOT_SMD:SOT-23` |
| [MMBT3906](https://www.diodes.com/datasheet/download/MMBT3906.pdf) (Diodes Incorporated) | A: PNP 3/1/2 | `Package_TO_SOT_SMD:SOT-23` |
| [MMDT3904](https://www.diodes.com/datasheet/download/MMDT3904.pdf) (Diodes Incorporated) | A: NPN 3/5/4; B: NPN 6/2/1 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |
| [MMDT3906](https://www.diodes.com/datasheet/download/MMDT3906.pdf) (Diodes Incorporated) | A: PNP 3/5/4; B: PNP 6/2/1 | `Package_TO_SOT_SMD:SOT-363_SC-70-6` |

MMPQ6700 has two internally connected collector pins per transistor. Both pins
are stacked in each symbol unit; the second pin is hidden. Both physical pads
receive the collector net. The SPICE wrapper joins them through a 1 microohm
strap to avoid an ideal zero-voltage loop when both pins share a net.

SOT457 and SOT26 use KiCad's SOT-23-6 footprint. SOT363 uses
SOT-363_SC-70-6. MMDT5501 uses the UTC pinout and ratings, including 160 V
collector-emitter ratings for both polarities.

## Gain values in descriptions

The following data-sheet limits apply at 25 C and the stated bias point.
Currents and voltages are magnitudes, including for PNP devices. They are not
model BF values or limits valid at every operating point.

| Part | hFE | IC | VCE |
|---|---|---|---|
| BCM847DS | 200–450 | 2 mA | 5 V |
| BCM857DS | 200–450 | 2 mA | 5 V |
| DMMT3904W | 100–300 | 10 mA | 1 V |
| DMMT3906W | 100–300 | 10 mA | 1 V |
| BC817DPN | 160–400 | 100 mA | 1 V |
| BC847BPN | 200–450 | 2 mA | 5 V |
| DMMT5551 | 80–250 | 10 mA | 5 V |
| DMMT5401 | 60–240 | 10 mA | 5 V |
| MMDT5551 | 80–250 | 10 mA | 5 V |
| MMDT5401 | 60–240 | 10 mA | 5 V |
| MMDT5501 | 120–270 | 10 mA | 5 V |
| MMPQ6700 | 70 min | 10 mA | 1 V |
| MMBT3904 | 100–300 | 10 mA | 1 V |
| MMBT3906 | 100–300 | 10 mA | 1 V |
| MMDT3904 | 100–300 | 10 mA | 1 V |
| MMDT3906 | 100–300 | 10 mA | 1 V |

## Simulation and maintenance

The symbols reference `spice/BJT_Arrays.lib`. Its subcircuit terminal order is
ascending physical pin number, so `Sim.Pins` maps each pin to the same-numbered
model terminal. Private BJT model names are scoped inside each package.
Keep simulation properties consistent across units of one reference.

KiCad exports omitted units as distinct unconnected model nodes. For predictable
simulation bias, place unused units too and give their terminals a suitable
inactive connection; a schematic no-connect marker does not supply DC bias.

`tools/bjt_catalog.json` records symbol metadata and physical pin assignments.
After editing it, run `python tools/generate_bjt_symbols.py` to regenerate these
16 entries while preserving the earlier SMD library entries. Changes to pinouts
also require corresponding SPICE wrapper changes. Run the validation commands
in [PCM packaging](PCM_PACKAGING.md) before committing.
