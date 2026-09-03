# PCM packaging and release

This document describes how maintainers validate, build, index, and release
the KiCad 10 Plugin and Content Manager package.

## Validate the library

Run the static symbol and model checks from the repository root:

```text
python tools/validate_library.py
```

If `ngspice` is installed, run the operating-point smoke test:

```text
ngspice -b -o ngspice.log tests/smoke/all_models.cir
```

The smoke test instantiates every public model.

## Build the package

Build the version declared in `pcm/metadata.json`:

```text
python tools/build_pcm_package.py
```

The deterministic archive is written to `dist/`. Source symbol model paths are
rewritten from `KICAD_RAYSLIB` to the KiCad 10 PCM installation directory.

To test another version without editing the metadata first:

```text
python tools/build_pcm_package.py --version 1.0.1
```

## Update the repository indexes

Set the new version in `pcm/metadata.json`, then regenerate `packages.json` and
`repository.json`:

```text
python tools/build_pcm_package.py --version 1.0.1 --update-repository-index
```

Commit the metadata, package contents, and regenerated indexes together. Do
not reuse a version whose release archive has already been published.

## Create a release

1. Confirm that the validation workflow passes on `main`.
2. Create a tag matching the version in the metadata and indexes, for example
   `v1.0.1`.
3. Push the tag.
4. Confirm that the `Create PCM release` workflow passes.
5. Confirm that the GitHub Release contains the versioned PCM ZIP archive.

Tags matching `v*` run the static validation and ngspice smoke test, build the
archive, verify the committed repository indexes, and create the GitHub
Release.
