#!/usr/bin/env python3
"""Extract and verify fastboot images directly from a VaultOs OTA ZIP (`payload.bin`).

Why this exists:
  Running `m bacon` rebuilds filesystem/AVB images inside `target_files` /
  `vaultos_otter-ota.zip`, which can yield different dm-verity salts,
  timestamps, or vbmeta root digests than loose `$OUT/*.img` files.
  Flashing mismatched `vbmeta.img` / `vbmeta_system.img` alongside an OTA's
  `super` partitions causes dm-verity corruption restarts when AVB is enforced
  under a locked bootloader.

  Extracting `boot.img`, `vendor_boot.img`, `dtbo.img`, `vbmeta.img`, and
  `vbmeta_system.img` directly from `vaultos_otter-ota.zip`'s `payload.bin`
  guarantees byte-for-byte consistency with the OTA's dynamic partitions.
"""

from __future__ import annotations

import argparse
import bz2
import hashlib
import lzma
from pathlib import Path
import struct
import sys
import zipfile

DEFAULT_PARTITIONS = ("boot", "vendor_boot", "dtbo", "vbmeta", "vbmeta_system")
AIRGAP_DTB_NODES = ("dwc3@a600000", "qcom,wcn6750", "qcom,mss@4080000")
STANDARD_RELEASE_ORDER = (
    "boot.img",
    "vendor_boot.img",
    "dtbo.img",
    "vbmeta.img",
    "vbmeta_system.img",
    "avb_custom_key.bin",
    "boot-usb-debug.img",
    "vendor_boot-usb-debug.img",
    "vaultos_otter-ota.zip",
    "release_flags.json",
)


def _read_varint(buf: bytes, idx: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        byte = buf[idx]
        idx += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return result, idx
        shift += 7


def _parse_proto(buf: bytes) -> dict[int, list[int | bytes]]:
    idx = 0
    fields: dict[int, list[int | bytes]] = {}
    while idx < len(buf):
        tag, idx = _read_varint(buf, idx)
        field_num, wire_type = tag >> 3, tag & 7
        if wire_type == 0:
            val, idx = _read_varint(buf, idx)
        elif wire_type == 2:
            length, idx = _read_varint(buf, idx)
            val = buf[idx : idx + length]
            idx += length
        elif wire_type == 1:
            val = buf[idx : idx + 8]
            idx += 8
        elif wire_type == 5:
            val = buf[idx : idx + 4]
            idx += 4
        else:
            raise ValueError(f"Unsupported protobuf wire type {wire_type} on field {field_num}")
        fields.setdefault(field_num, []).append(val)
    return fields


def _decompress_op(op_type: int, data: bytes) -> bytes:
    if op_type == 0:  # REPLACE
        return data
    if op_type == 1:  # REPLACE_BZ
        return bz2.decompress(data)
    if op_type == 8:  # REPLACE_XZ
        return lzma.decompress(data)
    raise ValueError(
        f"Unsupported payload install operation type {op_type}; expected full OTA REPLACE/BZ/XZ."
    )


def extract_partitions(
    ota_zip: Path, output_dir: Path, partitions: tuple[str, ...]
) -> dict[str, tuple[Path, int, str]]:
    """Extract full-partition images from `ota_zip`'s `payload.bin` and verify payload hashes."""
    output_dir.mkdir(parents=True, exist_ok=True)
    wanted = set(partitions)
    results: dict[str, tuple[Path, int, str]] = {}

    with zipfile.ZipFile(ota_zip, "r") as zf:
        info = zf.getinfo("payload.bin")
        if info.compress_type != zipfile.ZIP_STORED:
            raise RuntimeError("payload.bin inside OTA zip must be stored uncompressed (ZIP_STORED)")

        with ota_zip.open("rb") as raw_zip:
            raw_zip.seek(info.header_offset)
            local_hdr = raw_zip.read(30)
            fn_len, extra_len = struct.unpack("<HH", local_hdr[26:30])
            payload_start = info.header_offset + 30 + fn_len + extra_len

            raw_zip.seek(payload_start)
            hdr = raw_zip.read(24)
            if hdr[:4] != b"CrAU":
                raise ValueError(f"Invalid payload magic: {hdr[:4]!r}")
            version, manifest_len, metadata_sig_len = struct.unpack(">QQI", hdr[4:24])
            if version != 2:
                raise ValueError(f"Unsupported payload format version: {version}")

            manifest_bytes = raw_zip.read(manifest_len)
            manifest = _parse_proto(manifest_bytes)
            block_size = int(manifest.get(3, [4096])[0])
            data_offset = payload_start + 24 + manifest_len + metadata_sig_len

            for part_raw in manifest.get(13, []):
                part = _parse_proto(part_raw)  # type: ignore[arg-type]
                name = bytes(part[1][0]).decode("utf-8")
                if name not in wanted:
                    continue

                ninfo = _parse_proto(part[7][0])  # type: ignore[arg-type]
                part_size = int(ninfo[1][0])
                expected_hash = bytes(ninfo[2][0]).hex()
                out_buf = bytearray(part_size)

                for op_raw in part.get(8, []):
                    op = _parse_proto(op_raw)  # type: ignore[arg-type]
                    op_type = int(op[1][0])
                    data_off = int(op[2][0])
                    data_len = int(op[3][0])
                    raw_zip.seek(data_offset + data_off)
                    decompressed = _decompress_op(op_type, raw_zip.read(data_len))

                    dec_pos = 0
                    for ext_raw in op.get(6, []):
                        ext = _parse_proto(ext_raw)  # type: ignore[arg-type]
                        start_block = int(ext[1][0])
                        num_blocks = int(ext[2][0])
                        byte_off = start_block * block_size
                        byte_end = min(byte_off + num_blocks * block_size, part_size)
                        out_buf[byte_off:byte_end] = decompressed[dec_pos : dec_pos + (byte_end - byte_off)]
                        dec_pos += num_blocks * block_size

                actual_hash = hashlib.sha256(out_buf).hexdigest()
                if actual_hash != expected_hash:
                    raise RuntimeError(
                        f"SHA-256 mismatch extracting {name}: got {actual_hash}, expected {expected_hash}"
                    )

                out_path = output_dir / f"{name}.img"
                out_path.write_bytes(out_buf)
                results[name] = (out_path, len(out_buf), actual_hash)

    missing = wanted - set(results.keys())
    if missing:
        raise RuntimeError(f"Partitions missing from OTA payload: {sorted(missing)}")
    return results


def _parse_vbmeta_summary(vbmeta_bytes: bytes) -> dict[str, object]:
    if vbmeta_bytes[:4] != b"AVB0" or len(vbmeta_bytes) < 256:
        raise ValueError("Invalid AVB0 header")
    auth_sz, _ = struct.unpack(">QQ", vbmeta_bytes[12:28])
    algo = struct.unpack(">I", vbmeta_bytes[28:32])[0]
    pk_off, pk_sz = struct.unpack(">QQ", vbmeta_bytes[64:80])
    rollback = struct.unpack(">Q", vbmeta_bytes[112:120])[0]
    flags = struct.unpack(">I", vbmeta_bytes[120:124])[0]
    pk_start = 256 + auth_sz + pk_off
    pk_bytes = vbmeta_bytes[pk_start : pk_start + pk_sz]
    return {
        "algo": algo,
        "flags": flags,
        "rollback_index": rollback,
        "pk_sha1": hashlib.sha1(pk_bytes).hexdigest() if pk_bytes else None,
        "pk_sha256": hashlib.sha256(pk_bytes).hexdigest() if pk_bytes else None,
    }


def _find_dtb_node_statuses(dtb_blob: bytes, node_targets: tuple[str, ...]) -> dict[str, str]:
    magic, totalsize, off_struct, off_strings = struct.unpack(">IIII", dtb_blob[:16])
    if magic != 0xD00DFEED:
        raise ValueError("Invalid FDT magic in DTB")
    pos = off_struct
    stack: list[str] = []
    statuses: dict[str, str] = {}
    while pos < totalsize:
        token = struct.unpack(">I", dtb_blob[pos : pos + 4])[0]
        pos += 4
        if token == 1:  # FDT_BEGIN_NODE
            end = dtb_blob.find(b"\x00", pos)
            name = dtb_blob[pos:end].decode("ascii", errors="ignore")
            pos = (end + 4) & ~3
            stack.append(name)
        elif token == 2:  # FDT_END_NODE
            if stack:
                stack.pop()
        elif token == 3:  # FDT_PROP
            plen, nameoff = struct.unpack(">II", dtb_blob[pos : pos + 8])
            pos += 8
            val = dtb_blob[pos : pos + plen]
            pos = (pos + plen + 3) & ~3
            prop_end = dtb_blob.find(b"\x00", off_strings + nameoff)
            prop_name = dtb_blob[off_strings + nameoff : prop_end].decode("ascii", errors="ignore")
            if prop_name == "status" and stack:
                node_name = stack[-1]
                for target in node_targets:
                    if target in node_name:
                        statuses[node_name] = val.rstrip(b"\x00").decode("ascii", errors="ignore")
        elif token == 9:  # FDT_END
            break
    return statuses


def verify_extracted_images(
    output_dir: Path,
    avb_key_bin: Path | None,
    allow_permissive: bool,
    allow_usb_debug: bool,
) -> None:
    """Verify AVB keys/flags, SELinux cmdline, and kernel DTB air-gap states on extracted images."""
    expected_pk_sha256 = hashlib.sha256(avb_key_bin.read_bytes()).hexdigest() if avb_key_bin and avb_key_bin.exists() else None

    for vb_name in ("vbmeta.img", "vbmeta_system.img"):
        vb_path = output_dir / vb_name
        if not vb_path.exists():
            continue
        info = _parse_vbmeta_summary(vb_path.read_bytes())
        print(
            f"[AVB] {vb_name}: algo={info['algo']} flags={info['flags']} "
            f"rollback={info['rollback_index']} pk_sha1={info['pk_sha1']}"
        )
        if expected_pk_sha256 and info["pk_sha256"] != expected_pk_sha256:
            raise RuntimeError(
                f"{vb_name} public key SHA-256 ({info['pk_sha256']}) does not match {avb_key_bin}"
            )

    boot_bytes = (output_dir / "boot.img").read_bytes()
    vboot_bytes = (output_dir / "vendor_boot.img").read_bytes()
    if not allow_permissive and (b"selinux=permissive" in boot_bytes or b"selinux=permissive" in vboot_bytes):
        raise RuntimeError("Found androidboot.selinux=permissive in production boot/vendor_boot!")

    if not allow_usb_debug:
        fdt_magic = b"\xd0\x0d\xfe\xed"
        idx = vboot_bytes.find(fdt_magic)
        if idx == -1:
            raise RuntimeError("Could not locate DTB inside vendor_boot.img for air-gap verification")
        totalsize = struct.unpack(">I", vboot_bytes[idx + 4 : idx + 8])[0]
        statuses = _find_dtb_node_statuses(vboot_bytes[idx : idx + totalsize], AIRGAP_DTB_NODES)
        print(f"[DTB] vendor_boot air-gap nodes: {statuses}")
        for target in AIRGAP_DTB_NODES:
            matched = [v for k, v in statuses.items() if target in k]
            if not matched or any(v != "disabled" for v in matched):
                raise RuntimeError(f"Expected DTB node '{target}' to be 'disabled', got {statuses}")


def write_sha256sums(output_dir: Path) -> Path:
    lines: list[str] = []
    seen: set[str] = set()
    ordered_names = list(STANDARD_RELEASE_ORDER) + sorted(
        p.name for p in output_dir.iterdir() if p.is_file() and p.name != "SHA256SUMS" and p.name not in STANDARD_RELEASE_ORDER
    )
    for name in ordered_names:
        if name in seen:
            continue
        p = output_dir / name
        if not p.is_file() or name == "SHA256SUMS":
            continue
        seen.add(name)
        digest = hashlib.sha256()
        with p.open("rb") as f:
            while chunk := f.read(1024 * 1024):
                digest.update(chunk)
        lines.append(f"{digest.hexdigest()}  {name}")
    sums_path = output_dir / "SHA256SUMS"
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sums_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ota_zip", type=Path, help="Path to vaultos_otter-ota.zip")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Target directory for extracted .img files (defaults to ota_zip's parent directory)",
    )
    parser.add_argument(
        "--avb-key",
        type=Path,
        default=None,
        help="Optional avb_custom_key.bin to assert public key match in vbmeta*",
    )
    parser.add_argument("--allow-permissive", action="store_true", help="Allow selinux=permissive")
    parser.add_argument("--allow-usb-debug", action="store_true", help="Skip disabled-DTB air-gap check")
    parser.add_argument("--write-sums", action="store_true", help="Regenerate SHA256SUMS in output_dir")
    args = parser.parse_args()

    out_dir = args.output_dir or args.ota_zip.parent
    avb_key = args.avb_key or (out_dir / "avb_custom_key.bin")

    extracted = extract_partitions(args.ota_zip, out_dir, DEFAULT_PARTITIONS)
    for name, (path, size, digest) in extracted.items():
        print(f"[OK] {name:14s} -> {path.name:18s} ({size:10d} bytes) sha256={digest}")

    verify_extracted_images(out_dir, avb_key if avb_key.exists() else None, args.allow_permissive, args.allow_usb_debug)

    if args.write_sums:
        sums_path = write_sha256sums(out_dir)
        print(f"[OK] Updated {sums_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
