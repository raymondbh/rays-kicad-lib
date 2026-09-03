# Ray's SPICE-ready KiCad library

This repository contains a compact KiCad 10 symbol library for electronics
education. Every symbol distributed in the PCM package has a corresponding
ngspice model, an explicit pin mapping, and a suitable footprint where
applicable.

## Library contents

The package contains a curated collection of symbols for schematic capture and
SPICE-based teaching exercises. Only symbols with working bundled ngspice
models are distributed. Each included symbol has an explicit simulation pin
mapping and a suitable footprint where applicable.

See [MODEL_SOURCES.md](MODEL_SOURCES.md) for model provenance and calibration
notes.

## Install with the PCM repository (recommended)

1. Open KiCad 10 and start **Plugin and Content Manager**.
2. Open the repository settings and add this URL:

   ```text
   https://raw.githubusercontent.com/raymondbh/rays-kicad-lib/main/repository.json
   ```

3. Refresh the repository list.
4. Select **Ray's SPICE-ready KiCad Library** and install the desired version.
5. Close and restart KiCad so the installed symbol libraries are loaded.

GitHub hosts the repository indexes as raw files from `main`. Versioned package
archives are downloaded from GitHub Releases.

KiCad normally adds installed symbol libraries to the global library table.
The nickname may have the configured PCM prefix, which is `PCM_` by default.
The bundled models are installed below KiCad's `KICAD10_3RD_PARTY` directory;
no custom SPICE path is required.

## Install a downloaded GitHub Release package

1. Download the file named `rays-kicad-lib-<version>-pcm.zip` from the GitHub
   release.
2. Open KiCad 10.
3. Open **Plugin and Content Manager**.
4. Select **Install from File...** and choose the downloaded ZIP file.
5. Apply the pending installation if KiCad asks for confirmation.
6. Close and restart KiCad so the installed symbol libraries are loaded.

## Install from a clone

1. Clone or download this repository.
2. In KiCad, open **Preferences > Configure Paths**.
3. Add `KICAD_RAYSLIB` and set it to the absolute repository path.
4. Open **Preferences > Manage Symbol Libraries**.
5. Add the `.kicad_sym` files from the `symbol` directory as global or project
   libraries.

The source symbols use paths such as:

```text
${KICAD_RAYSLIB}/spice/Diodes.lib
```

PCM package validation, build, indexing, and release instructions are kept in
[docs/PCM_PACKAGING.md](docs/PCM_PACKAGING.md).

## License

Repository-authored content is available under the MIT license. Imported and
manufacturer-derived SPICE models may have separate redistribution terms; see
`MODEL_SOURCES.md` before republishing the package through a public catalog.
