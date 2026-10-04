# PCM packaging and release

This document describes how maintainers validate, build, index, and release
the KiCad 10 Plugin and Content Manager package.

## Validate the library

Run the static symbol and model checks from the repository root:

```text
python tools/validate_library.py
```

If `ngspice` is installed, run the operating-point and transient smoke tests:

```text
ngspice -b -o ngspice.log tests/smoke/all_models.cir
ngspice -b -o opamps.log tests/smoke/opamps.cir
ngspice -b -o ua741-transient.log tests/smoke/ua741_transient.cir
ngspice -b -o fets.log tests/smoke/fets.cir
```

The operating-point tests cover the original model libraries. The isolated UA741
test also verifies transient convergence without coupling unrelated op-amp
macromodels into the same transient analysis.
The FET test checks DC data-sheet envelopes, JFET cutoff voltages, the MOSFET
body diode, and transient switching.

Run the new SMD BJT model tests and actual KiCad 10 netlist exports as well:

```text
python tests/check_bjt_models.py
python tests/check_bjt_kicad.py --kicad-cli kicad-cli
```

The BJT checks cover all 16 new package models (32 transistor sections), physical
pin ordering and one PCB/BOM component per package. Generated decks, schematics
and logs are stored in `dist/`. CI runs the static and ngspice checks; the KiCad
export test requires a local KiCad 10 installation.

On Windows, KiCad's bundled Python and ngspice DLL can run the tests without a
separate Python or ngspice installation. For example, in PowerShell:

```powershell
$env:NGSPICE_DLL = 'C:/Program Files/KiCad/10.0/bin/ngspice.dll'
& 'C:/Program Files/KiCad/10.0/bin/python.exe' tests/check_bjt_models.py
& 'C:/Program Files/KiCad/10.0/bin/python.exe' tools/run_ngspice.py tests/smoke/fets.cir
& 'C:/Program Files/KiCad/10.0/bin/python.exe' tests/check_bjt_kicad.py --kicad-cli 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
```

`tools/run_ngspice.py` also accepts the other smoke-test decks listed above.

### Smoke-test requirements and troubleshooting

Run smoke tests with `ngspice -b`, as shown above. Batch mode does not behave
exactly like an interactive KiCad simulation or a shared-library `run` command.
For a batch netlist that relies on a `.tran` directive, as the UA741 test does,
include an output directive such as `.print`:

```text
.tran 10u 2m
.print tran v(OUT)
```

Without `.print`, `.plot`, or `.fourier`, this form of batch execution may report
that no simulations ran even when the circuit loads successfully.

The FET test instead runs `tran` explicitly inside a `.control` block and checks
the results with `meas` and conditional checks. It exits with `quit 1` on a failed
check and `quit 0` on success; it does not require a `.print tran` directive.
A successful model load or operating-point analysis alone does not replace
either form of transient test.

Keep operating-point tests for multiple models separate from focused transient
tests. This makes convergence failures easier to associate with one model and
prevents unrelated macromodels from affecting transient initialization.

The ngspice version bundled with KiCad 10 may be newer than the version
available on the GitHub Actions runner. Smoke tests must pass in CI as well as
with KiCad 10. When a result differs, record both versions and inspect the CI
log before changing a model.

## Build the package

Build the version declared in `pcm/metadata.json`:

```text
python tools/build_pcm_package.py
```

The deterministic archive is written to `dist/`. Source symbol model paths are
rewritten from `KICAD_RAYSLIB` to the KiCad 10 PCM installation directory.

To test another version without editing the metadata first:

```text
python tools/build_pcm_package.py --version X.Y.Z
```

## Update the repository indexes

Set the new version in `pcm/metadata.json`, then regenerate `packages.json` and
`repository.json`:

```text
python tools/build_pcm_package.py --version X.Y.Z --update-repository-index
```

Commit the metadata and regenerated indexes together with the release content.
The generated archive under `dist/` is ignored because the release workflow
builds and uploads it. Do not reuse a version whose release archive has already
been published.

## Create a release

1. Confirm that the validation workflow passes on `main`.
2. Create a tag matching the version in the metadata and indexes, for example
   `vX.Y.Z`.
3. Push the tag.
4. Confirm that the `Create PCM release` workflow passes.
5. Confirm that the GitHub Release contains the versioned PCM ZIP archive.

Tags matching `v*` run the static validation and ngspice smoke test, build the
archive, verify the committed repository indexes, and create the GitHub
Release.

A workflow rerun always uses the commit referenced by the tag. Pushing a fix to
`main` does not change an existing tag. If a tag-triggered workflow fails before
publishing a release, commit and validate the fix on `main`, then recreate the
tag at the corrected commit. Never move a tag for an archive that has already
been published.
