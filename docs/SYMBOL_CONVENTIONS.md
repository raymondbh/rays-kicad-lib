# Symbol descriptions and keywords

Use these conventions for every new or updated library symbol. All field text
is English. The description summarizes the physical component; simulation
provenance and limitations belong in [MODEL_SOURCES.md](../MODEL_SOURCES.md).

## Description

Use one short line in this order:

```text
Type/function key values, package (optional pinout note)
```

Use the compact style of the original library: capitalize descriptive words,
keep familiar abbreviations such as NPN, JFET, MOSFET, LED, and Op-Amp, and
separate the package with a comma. Do not repeat the part number from `Value`.
Omit redundant words such as `transistor` after NPN and `diode` after Zener.

| Family | Content and example |
|---|---|
| BJT | Polarity, function, voltage, current and gain range: `NPN General Purpose 40V 200mA hFE 100–300, TO-92` |
| BJT gain selection | Add the range for A/B/C variants: `NPN General Purpose 45V 100mA hFE 200–450, SOT-23` |
| JFET | Channel, mode, voltage rating, maximum drain current if specified, IDSS and cutoff voltage: `N-Channel Depletion VDG 35V IDSS 2mA min VGS(off) -0.5 to -3V, TO-92` |
| MOSFET | Channel, operating mode, voltage and current: `N-Channel E-MOSFET 60V 200mA, TO-92` |
| Rectifier | Voltage and current: `Rectifier 1000V 1A, DO-41` |
| Schottky | Voltage and current: `Schottky Rectifier 40V 1A, DO-41` |
| Switching diode | Voltage and current: `Fast Switching Diode 100V 150mA, DO-35` |
| Zener | Voltage, test current and power: `Zener 12V at 21mA 1.3W, DO-41` |
| LED | Color, forward voltage and test current: `Generic Red LED 2.0V at 20mA, 5mm` |
| Operational amplifier | Channels, function and bandwidth: `Dual Low-Power Op-Amp 700kHz, PDIP-8` |
| Potentiometer | Taper and mounting: `Linear Potentiometer, Horizontal THT` |

### Values and notation

- In descriptions, join numbers and units: `40V`, `200mA`, `700kHz`, `5mm`.
  Use a decimal point and an en dash for gain ranges, such as `200–450`.
  Explanatory documentation may use spaces between values and units.
- Omit parameter labels such as `VCEO`, `IF(AV)`, `VZ`, and `GBW` from the
  short description. Their meaning follows the family conventions below.
- BJT voltage/current values summarize collector-emitter voltage and collector
  current ratings. MOSFET values summarize drain-source voltage and drain
  current ratings. Use positive magnitudes for PNP rating summaries.
- Rectifier and switching-diode values summarize repetitive peak reverse
  voltage and average forward current, not surge current.
- Keep the test current for every Zener: `Zener <voltage> at <current> <power>,
  <package>`. Use nominal voltage; leave tolerance and min/max limits in the
  data sheet. Power ratings depend on the stated thermal conditions.
- Include power primarily for Zener diodes. Omit it from BJT descriptions to
  keep them short and avoid mixing ambient- and case-temperature ratings.
- Include the data-sheet DC gain range as `hFE <min>–<max>` for both THT and
  SMD BJTs. Use limits from one specified test point and the exact gain grade,
  where applicable. If only a minimum is specified, use `hFE <value> min`.
  Do not substitute the model's BF value or small-signal gain for DC gain.
  Record the selected test conditions below rather than in the description.
- Use `E-MOSFET` for enhancement mode (normally off at zero gate-source voltage)
  and `D-MOSFET` for depletion mode (normally on at zero gate-source voltage).
  Keep the channel designation: for example, `N-Channel E-MOSFET` for 2N7000.
- Op-amp bandwidth values are typical gain-bandwidth products. Generic LED
  voltages are nominal model targets at the stated current, not manufacturer
  guarantees. Keep `Generic` for LEDs that have no selected manufacturer.
- For JFETs, retain the labels `VDS` or `VDG`, `ID`, `IDSS`, and `VGS(off)`.
  IDSS is the drain current at VGS = 0, not the maximum drain-current rating.
  Include `ID <value> max` only when the data sheet specifies that rating.
  Use `min` for a one-sided IDSS limit and signed values for cutoff voltage;
  separate negative range endpoints with `to` for readability.
- Do not include simulation defaults as
  fixed hardware ratings for adjustable components such as potentiometers.

### BJT gain reference conditions

These ranges apply at the listed bias point, not over all currents and
temperatures. Current and voltage below are magnitudes, including for PNP
devices; consult the linked data sheets for temperature and pulse conditions.
Unsuffixed symbols use the standard range, not a narrower selected gain grade.

| Device and data sheet | hFE range | Collector current | Collector-emitter voltage |
|---|---|---|---|
| [2N3904](https://www.onsemi.com/download/data-sheet/pdf/2n3904-d.pdf) | 100–300 | 10 mA | 1 V |
| [2N3906](https://www.onsemi.com/download/data-sheet/pdf/2n3906-d.pdf) | 100–300 | 10 mA | 1 V |
| [2N5401](https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf) | 60–240 | 10 mA | 5 V |
| [2N5551](https://www.onsemi.com/pdf/datasheet/2n5551t-d.pdf) | 80–250 | 10 mA | 5 V |
| [BD175](https://www.onsemi.com/download/data-sheet/pdf/bd179-fcs-d.pdf) | 40–250 | 150 mA | 2 V |
| [BD176](https://www.onsemi.com/download/data-sheet/pdf/bd176-d.pdf) | 40–250 | 150 mA | 2 V |
| [BD139](https://www.onsemi.com/download/data-sheet/pdf/bd139-d.pdf) | 40–250 | 150 mA | 2 V |
| [BD140](https://www.onsemi.com/download/data-sheet/pdf/bd140-d.pdf) | 40–250 | 150 mA | 2 V |
| [BC847 A/B/C](https://assets.nexperia.com/documents/data-sheet/BC847X_SER.pdf) | A: 110–220; B: 200–450; C: 420–800 | 2 mA | 5 V |
| [BC857 A/B/C](https://assets.nexperia.com/documents/data-sheet/BC856_BC857_BC858.pdf) | A: 125–250; B: 220–475; C: 420–800 | 2 mA | 5 V |

### JFET reference conditions

- [onsemi 2N3819](https://www.onsemi.com/download/data-sheet/pdf/2n3819-d.pdf)
  specifies VDS = 25 V and ID = 100 mA as maximum ratings. IDSS is 2–20 mA
  at VDS = 15 V, VGS = 0. VGS(off) is listed as -8 V in the maximum column,
  measured at VDS = 15 V and ID = 10 nA, with no minimum specified.
  The description's `-8V max` follows this data-sheet convention: it is the
  maximum required negative cutoff-voltage magnitude, not a typical value.
  Electrical characteristics apply at TA = 25 degrees C.
- [onsemi J111/J112/J113](https://www.onsemi.com/download/data-sheet/pdf/mmbfj113-d.pdf)
  specifies VDG = 35 V, with no separate maximum VDS or ID rating.
  Do not relabel VDG as VDS or use forward gate current as maximum drain current.
  IDSS minima are 20, 5 and 2 mA respectively, at VDS = 15 V and VGS = 0
  (pulse width at most 300 us, duty cycle at most 2%). VGS(off) ranges are
  -3 to -10 V, -1 to -5 V and -0.5 to -3 V respectively, measured at
  VDS = 5 V and ID = 1 uA. Electrical characteristics apply at TJ = 25 degrees C.

### Package and pinout

Use familiar package names such as `TO-92`, `TO-126`, `SOT-23`, `DO-35`, `DO-41`,
`SOD-323`, and `PDIP-8`. Describe size or mounting style for generic components
without a standard package code. The `Footprint` field holds the exact land pattern.

If a manufacturer pinout note is needed, append it after the package,
for example `TO-92 (onsemi S-G-D)` for 2N3819.
The terminal sequence denotes physical pin numbers 1, 2, and 3, respectively.
Full FET pin assignments remain in `MODEL_SOURCES.md` and `Sim.Pins`.
Do not change pin numbers, footprints, or simulation mappings during wording edits.

## Search keywords

Use space-separated terms in this order: family, technology or polarity,
function or useful selection, package, mounting style. Keep acronyms uppercase
and ordinary words lowercase. Examples:

```text
transistor BJT NPN general-purpose amplifier switch TO-92 THT
transistor JFET N-channel depletion analog-switch TO-92 THT
diode Zener voltage-regulator DO-35 THT
amplifier opamp dual low-power single-supply PDIP-8 THT
```

Include meaningful distinctions such as `gain-group-A` and LED color. Do not
copy the entire description, numeric ratings, or part number into the keywords.
`5mm` is a compact size keyword for the generic LED package.

## Data sheets and model documentation

Prefer a direct manufacturer data-sheet URL in `Datasheet`. A family data sheet
is appropriate when it covers the exact variant and package. Leave the field
empty for generic components without a selected manufacturer's data sheet.

Check numerical values against the selected variant, not another member of the
family. Record model origin, calibration points, and omissions in
`MODEL_SOURCES.md`; do not add `generic educational SPICE model` to individual
physical-device descriptions. A data-sheet link does not imply the bundled
model was supplied by that manufacturer or reproduces every rating.

The October 2026 metadata review used the linked manufacturer data sheets.
These details are important when maintaining the descriptions:

- [Vishay BZX55, Rev. 2.0](https://www.vishay.com/docs/85604/bzx55.pdf) gives
  explicit voltage ranges. BZX55C30 is specified at 5 mA and BZX55C68 at 2.5 mA;
  the previous descriptions listed 2 mA and 1 mA. Other included BZX55 parts
  use 5 mA. Power ratings require the stated lead-temperature conditions.
- [Nexperia PDZ-B, Rev. 5](https://assets.nexperia.com/documents/data-sheet/PDZ-B_SER.pdf)
  specifies PDZ12B as 11.74 to 12.24 V at 5 mA. The compact description uses
  its nominal 12V designation and retains the 5mA test current; it does not
  claim a symmetric tolerance.
- [Nexperia BC847](https://assets.nexperia.com/documents/data-sheet/BC847X_SER.pdf)
  and [BC857](https://assets.nexperia.com/documents/data-sheet/BC856_BC857_BC858.pdf)
  define the A/B/C gain ranges at 2 mA collector-current magnitude and 5 V
  collector-emitter-voltage magnitude. They are not the model's `BF` values.
- [TI TL07xx, Rev. W](https://www.ti.com/lit/ds/symlink/tl072.pdf), section 5.8,
  lists 5.25 MHz typical GBW for TL072C in the P package. Its 3 MHz row applies
  to NS/PS packages and TL07xM devices. The bundled historical model is unchanged.
- [TI LM358](https://www.ti.com/lit/ds/symlink/lm358.pdf) lists 700 kHz for the
  original LM358, distinct from LM358B variants.
  [TI UA741 product data](https://www.ti.com/product/UA741) lists 1 MHz typical GBW.

## Review an update

Compare description values with the linked data sheet and verify the package
matches the existing symbol. For metadata-only changes, check that the diff is
limited to `Description`, `ki_keywords`, and any intended `Datasheet` updates.
Run `python tools/validate_library.py` and `git diff --check`. Simulation tests
are needed when models or simulation mappings change, rather than for wording
alone. Do not update release versions or indexes during a metadata cleanup;
regenerate the package and indexes together when preparing the next release.
