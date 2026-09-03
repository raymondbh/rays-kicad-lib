#!/usr/bin/env python3
"""Build a deterministic KiCad 10 PCM archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = "com.github.raymondbh.rays-kicad-lib"
INSTALLED_IDENTIFIER = IDENTIFIER.replace(".", "_")
REPOSITORY_BASE_URL = "https://raw.githubusercontent.com/raymondbh/rays-kicad-lib/main"
RELEASE_BASE_URL = "https://github.com/raymondbh/rays-kicad-lib/releases/download"
SYMBOL_FILES = (
    "rayslib-bjt-smd.kicad_sym",
    "rayslib-bjt-tht.kicad_sym",
    "rayslib-diode-smd.kicad_sym",
    "rayslib-diode-tht.kicad_sym",
    "rayslib-passive-tht.kicad_sym",
)
SPICE_FILES = ("BJT_NPN.lib", "BJT_PNP.lib", "Diodes.lib", "Passives.lib")
SOURCE_PREFIX = "${KICAD_RAYSLIB}/spice/"
PCM_PREFIX = f"${{KICAD10_3RD_PARTY}}/symbols/{INSTALLED_IDENTIFIER}/spice/"
ZIP_TIMESTAMP = (2024, 1, 1, 0, 0, 0)


def zip_write(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.create_system = 3  # Use Unix ZIP metadata on every build platform.
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def read_text_lf(path: Path) -> str:
    """Read UTF-8 text with deterministic LF line endings."""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=None, help="Override the metadata version")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument(
        "--update-repository-index",
        action="store_true",
        help="Update repository.json and packages.json for this release",
    )
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
            source = read_text_lf(ROOT / "symbol" / filename)
            packaged = source.replace(SOURCE_PREFIX, PCM_PREFIX)
            if SOURCE_PREFIX in packaged or "${KICAD_RAYSLIB}" in packaged:
                raise RuntimeError(f"Unconverted source path in {filename}")
            if PCM_PREFIX not in packaged:
                raise RuntimeError(f"No packaged model path found in {filename}")
            zip_write(archive, f"symbols/{filename}", packaged.encode())
        for filename in SPICE_FILES:
            data = read_text_lf(ROOT / "spice" / filename).encode()
            zip_write(archive, f"symbols/spice/{filename}", data)
        for filename in ("README.md", "MODEL_SOURCES.md", "LICENSE"):
            zip_write(archive, f"resources/{filename}", read_text_lf(ROOT / filename).encode())

    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("The generated ZIP archive failed its integrity check")
        json.loads(archive.read("metadata.json"))

    if args.update_repository_index:
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        with zipfile.ZipFile(output) as archive:
            install_size = sum(info.file_size for info in archive.infolist())
        published_metadata = json.loads(json.dumps(metadata))
        published_metadata.pop("$schema", None)
        current_version = published_metadata["versions"][0]
        current_version.update(
            {
                "download_url": f"{RELEASE_BASE_URL}/v{version}/{output.name}",
                "download_sha256": digest,
                "download_size": output.stat().st_size,
                "install_size": install_size,
            }
        )
        existing_packages = None
        if (ROOT / "packages.json").is_file():
            existing_packages = json.loads(
                (ROOT / "packages.json").read_text(encoding="utf-8")
            )
        previous_versions = []
        if existing_packages:
            for package in existing_packages.get("packages", []):
                if package.get("identifier") == IDENTIFIER:
                    previous_versions = package.get("versions", [])
                    break
        published_metadata["versions"] = [current_version] + [
            item for item in previous_versions if item.get("version") != version
        ]
        packages = {"packages": [published_metadata]}
        (ROOT / "packages.json").write_text(
            json.dumps(packages, indent=2) + "\n", encoding="utf-8"
        )
        existing_repository = None
        if (ROOT / "repository.json").is_file():
            existing_repository = json.loads(
                (ROOT / "repository.json").read_text(encoding="utf-8")
            )
        if existing_packages == packages and existing_repository:
            timestamp = existing_repository["packages"]["update_timestamp"]
        else:
            timestamp = int(time.time())
        repository = {
            "$schema": "https://go.kicad.org/pcm/schemas/v1#/definitions/Repository",
            "name": "Ray's KiCad Library",
            "maintainer": {
                "name": "Raymond Berg Hansen",
                "contact": {"web": "https://github.com/raymondbh/rays-kicad-lib"},
            },
            "packages": {
                "url": f"{REPOSITORY_BASE_URL}/packages.json",
                "update_timestamp": timestamp,
                "update_time_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp)),
            },
        }
        (ROOT / "repository.json").write_text(
            json.dumps(repository, indent=2) + "\n", encoding="utf-8"
        )
        print(ROOT / "repository.json")
        print(ROOT / "packages.json")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
