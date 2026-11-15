#!/usr/bin/env python3
"""Build a hash-verified VaultOs provisioning & mandatory-update ZIP bundle.

Creates `vaultos_bundle.zip` containing:
  - manifest.json (SHA-256 hashes, mandatory flags for APKs, exact target_path for files)
  - apps/<apk_filename>
  - files/<relative_index>/<filename>

Usage example:
  python tools/pipeline/create_vaultos_bundle.py \
    --output vaultos_bundle.zip \
    --apk path/to/CustomOtterControl.apk:de.hartz.software.customottercontrol:mandatory \
    --apk path/to/Insular.apk:com.oasisfeng.island.fdroid:optional \
    --file ./survival_manual.pdf:/storage/emulated/0/Documents/VaultOs/survival_manual.pdf
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import zipfile


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def parse_apk_spec(spec: str) -> tuple[Path, str, bool]:
    """Parse `<local_path>[:<package_name>[:mandatory|optional]]` cleanly even with Windows drive letters."""
    mandatory = True
    parts = spec.rsplit(":", 2)
    # Detect trailing `:mandatory` / `:optional`
    if len(parts) >= 2 and parts[-1].lower() in {"mandatory", "optional", "true", "false"}:
        flag = parts[-1].lower()
        mandatory = flag in {"mandatory", "true"}
        spec_no_flag = spec[: -(len(parts[-1]) + 1)]
    else:
        spec_no_flag = spec

    path_candidate = Path(spec_no_flag)
    if path_candidate.exists():
        return path_candidate, "", mandatory

    if ":" in spec_no_flag:
        local_str, package_name = spec_no_flag.rsplit(":", 1)
        local_path = Path(local_str)
        if local_path.exists():
            return local_path, package_name.strip(), mandatory

    raise FileNotFoundError(f"APK path not found in --apk spec: {spec}")


def parse_file_spec(spec: str) -> tuple[Path, str, bool]:
    """Parse `<local_path>:<device_target_path>[:keep]` cleanly even with Windows drive letters."""
    overwrite = True
    candidate_spec = spec
    if spec.lower().endswith(":keep"):
        overwrite = False
        candidate_spec = spec[:-5]
    elif spec.lower().endswith(":overwrite"):
        overwrite = True
        candidate_spec = spec[:-10]

    # On Windows, `<local_path>` may start with `C:\...`
    sep_idx = candidate_spec.find(":/")
    if sep_idx == -1:
        sep_idx = candidate_spec.rfind(":")
    if sep_idx <= 1:
        raise ValueError(
            f"Invalid --file spec '{spec}'. Expected '<local_path>:/device/target/path[:keep]'."
        )

    local_path = Path(candidate_spec[:sep_idx])
    target_path = candidate_spec[sep_idx + 1 :].strip()
    if not local_path.exists():
        raise FileNotFoundError(f"Local file or directory not found: {local_path}")
    if not target_path.startswith("/"):
        raise ValueError(f"Device target path must be absolute (start with '/'): {target_path}")
    return local_path, target_path, overwrite


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Package VaultOs APKs (with mandatory update flags) and target files into a ZIP bundle."
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        type=Path,
        help="Output ZIP path (e.g. vaultos_bundle.zip)",
    )
    parser.add_argument(
        "--name",
        default="VaultOs Offline Provisioning Bundle",
        help="Human-readable bundle name stored in manifest.json",
    )
    parser.add_argument(
        "--apk",
        action="append",
        default=[],
        help="APK spec: <local_apk_path>[:<package_id>][:(mandatory|optional)]. Repeatable.",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="File/dir spec: <local_path>:</absolute/device/target_path>[:keep]. Repeatable.",
    )
    args = parser.parse_args()

    if not args.apk and not args.file:
        parser.error("Provide at least one --apk or --file entry.")

    apps_manifest = []
    files_manifest = []
    zip_entries: list[tuple[Path, str]] = []

    used_apk_names: set[str] = set()
    for spec in args.apk:
        apk_path, package_name, mandatory = parse_apk_spec(spec)
        arc_name = apk_path.name
        if arc_name in used_apk_names:
            arc_name = f"{len(used_apk_names)}_{apk_path.name}"
        used_apk_names.add(arc_name)
        zip_path = f"apps/{arc_name}"
        zip_entries.append((apk_path, zip_path))
        apps_manifest.append(
            {
                "name": apk_path.stem,
                "package": package_name,
                "file": zip_path,
                "sha256": sha256_file(apk_path),
                "mandatory": mandatory,
            }
        )

    for idx, spec in enumerate(args.file):
        local_path, target_path, overwrite = parse_file_spec(spec)
        if local_path.is_dir():
            target_root = target_path.rstrip("/")
            for child in sorted(local_path.rglob("*")):
                if not child.is_file():
                    continue
                rel = child.relative_to(local_path).as_posix()
                zip_path = f"files/{idx}/{rel}"
                zip_entries.append((child, zip_path))
                files_manifest.append(
                    {
                        "description": f"{local_path.name}/{rel}",
                        "source": zip_path,
                        "target_path": f"{target_root}/{rel}",
                        "sha256": sha256_file(child),
                        "overwrite": overwrite,
                    }
                )
        else:
            zip_path = f"files/{idx}/{local_path.name}"
            zip_entries.append((local_path, zip_path))
            files_manifest.append(
                {
                    "description": local_path.name,
                    "source": zip_path,
                    "target_path": target_path,
                    "sha256": sha256_file(local_path),
                    "overwrite": overwrite,
                }
            )

    manifest = {
        "version": 2,
        "bundle_name": args.name,
        "created_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "apps": apps_manifest,
        "files": files_manifest,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        for src_path, arc_path in zip_entries:
            compress = zipfile.ZIP_STORED if arc_path.endswith(".apk") else zipfile.ZIP_DEFLATED
            zf.write(src_path, arc_path, compress_type=compress)

    print(
        f"Created {args.output} ({args.output.stat().st_size} bytes): "
        f"{len(apps_manifest)} APK(s), {len(files_manifest)} file(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

