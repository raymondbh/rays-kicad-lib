#!/usr/bin/env python3
"""Build a deterministic KiCad 10 PCM archive."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = "com.github.raymondbh.rays-kicad-lib"
INSTALLED_IDENTIFIER = IDENTIFIER.replace(".", "_")
SYMBOL_FILES = (
    "rayslib-bjt-smd.kicad_sym",
    "rayslib-bjt-tht.kicad_sym",
    "rayslib-diode-tht.kicad_sym",
    "rayslib-passive-tht.kicad_sym",
)
SPICE_FILES = ("BJT_NPN.lib", "BJT_PNP.lib", "Diodes.lib", "Passives.lib")
SOURCE_PREFIX = "${KICAD_RAYSLIB}/spice/"
PCM_PREFIX = f"${{KICAD10_3RD_PARTY}}/symbols/{INSTALLED_IDENTIFIER}/spice/"
ZIP_TIMESTAMP = (2024, 1, 1, 0, 0, 0)


def zip_write(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=None, help="Override the metadata version")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()

    metadata = json.loads((ROOT / "pcm" / "metadata.json").read_text(encoding="utf-8"))
    if args.version:
        metadata["versions"][0]["version"] = args.version
    version = metadata["versions"][0]["version"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"rays-kicad-lib-{version}-pcm.zip"

    with zipfile.ZipFile(output, "w") as archive:
        zip_write(archive, "metadata.json", (json.dumps(metadata, indent=2) + "\n").encode())
        for filename in SYMBOL_FILES:
            source = (ROOT / "symbol" / filename).read_text(encoding="utf-8")
            packaged = source.replace(SOURCE_PREFIX, PCM_PREFIX)
            if SOURCE_PREFIX in packaged or "${KICAD_RAYSLIB}" in packaged:
                raise RuntimeError(f"Unconverted source path in {filename}")
            if PCM_PREFIX not in packaged:
                raise RuntimeError(f"No packaged model path found in {filename}")
            zip_write(archive, f"symbols/{filename}", packaged.encode())
        for filename in SPICE_FILES:
            zip_write(archive, f"symbols/spice/{filename}", (ROOT / "spice" / filename).read_bytes())
        for filename in ("README.md", "MODEL_SOURCES.md", "LICENSE"):
            zip_write(archive, f"resources/{filename}", (ROOT / filename).read_bytes())

    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("The generated ZIP archive failed its integrity check")
        json.loads(archive.read("metadata.json"))

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
