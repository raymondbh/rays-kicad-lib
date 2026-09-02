# Ray's SPICE-ready KiCad library

This repository contains a compact KiCad 10 symbol library for electronics
education. Every symbol distributed in the PCM package has a corresponding
ngspice model, an explicit pin mapping, and a suitable footprint where
applicable.

## Included symbols

- NPN and PNP bipolar transistors in through-hole and SMD packages
- BZX55C Zener diodes
- Generic red, green, blue, and white LEDs
- 1N4001 through 1N4007 rectifier diodes
- A parameterized linear potentiometer

See [MODEL_SOURCES.md](MODEL_SOURCES.md) for model provenance, calibration
notes, and models retained for planned symbols.

## Install a GitHub Release package

1. Download the file named `rays-kicad-lib-<version>-pcm.zip` from the GitHub
   release.
2. Open KiCad 10.
3. Open **Plugin and Content Manager**.
4. Select **Install from File...** and choose the downloaded ZIP file.
5. Apply the pending installation if KiCad asks for confirmation.

KiCad normally adds installed symbol libraries to the global library table.
The nickname may have the configured PCM prefix, which is `PCM_` by default.
The bundled models are installed below KiCad's `KICAD10_3RD_PARTY` directory;
no custom SPICE path is required.

## Install from a clone

1. Clone or download this repository.
2. In KiCad, open **Preferences > Configure Paths**.
3. Add `KICAD_RAYSLIB` and set it to the absolute repository path.
4. Open **Preferences > Manage Symbol Libraries**.
5. Add the four `.kicad_sym` files from the `symbol` directory as global or
   project libraries.

The source symbols use paths such as:

```text
${KICAD_RAYSLIB}/spice/Diodes.lib
```

The package builder rewrites these paths to the PCM installation directory in
the generated archive.

## Validate

Run the static symbol/model checks:

```text
python tools/validate_library.py
```

If `ngspice` is installed, run the operating-point smoke test from the
repository root:

```text
ngspice -b tests/smoke/all_models.cir
```

The smoke test instantiates every public model, including models retained for
planned symbols.

## Build the PCM archive

```text
python tools/build_pcm_package.py
```

The archive is written to `dist/`. To build a release with a specific version:

```text
python tools/build_pcm_package.py --version 1.0.0
```

Release tags matching `v*` run validation, execute the ngspice smoke test,
build the archive, and attach it to a GitHub Release.

## Custom PCM repository

KiCad can use a project-hosted PCM repository by adding the URL under the PCM
repository settings. A repository requires a static repository index and
package index in addition to release ZIP files. The initial distribution uses
GitHub Releases and **Install from File**; repository-index publication can be
added later, for example with GitHub Pages.

## License

Repository-authored content is available under the MIT license. Imported and
manufacturer-derived SPICE models may have separate redistribution terms; see
`MODEL_SOURCES.md` before republishing the package through a public catalog.
