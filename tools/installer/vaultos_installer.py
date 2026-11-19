#!/usr/bin/env python3
"""
VaultOs Sovereign Installer & Flasher
Target Device: SHIFTphone 8 (Qualcomm QCM6490 / 'otter')
License: Apache-2.0

Zero-dependency cross-platform installer for Linux, macOS, and Windows.
Performs cryptographic SHA-256 verification, release-flag lock gating,
multi-device serial isolation, Recovery USB-debug sideloading, and safe
AVB custom-key enrollment / gated bootloader locking (v2.0+).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Import payload verification helper when running from repository checkout
PIPELINE_DIR = Path(__file__).resolve().parent.parent / "pipeline"
if PIPELINE_DIR.is_dir():
    sys.path.insert(0, str(PIPELINE_DIR))

VERSION = "1.0.3"
LOCKED_BOOTLOADER_SUPPORTED = False
GITHUB_REPO = "Hatzen/VaultOs"
EXPECTED_PRODUCT = "otter"

REQUIRED_ASSETS = [
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
    "SHA256SUMS",
]

OPTIONAL_ASSETS = {"release_flags.json", "avb_custom_key.bin"}


def print_banner():
    banner = f"""
========================================================================
    __     __            _ _    ____
    \\ \\   / /_ _ _   _| | |_ / __ \\ ___
     \\ \\ / / _` | | | | | __/ / / // __|
      \\ V / (_| | |_| | | |_ / /_/ /\\__ \\
       \\_/ \\__,_|\\__,_|_|\\__|\\____/ |___/

    VaultOs Sovereign Installer (v{VERSION})
    Target Hardware: SHIFTphone 8 ({EXPECTED_PRODUCT})
========================================================================
"""
    print(banner)


def print_security_warning():
    warning = """
[!] THREAT MODEL & BOOTLOADER LOCK DISCLAIMER:
------------------------------------------------------------------------
1. CRYPTOGRAPHIC INTEGRITY:
   All downloaded and local release artifacts are verified against
   SHA-256 checksums before touching any device partition.

2. LOCKED BOOTLOADER SAFETY GATE:
   * Releases flagged locked_bootloader_supported=false (including v1.0.x)
     MUST stay on an UNLOCKED bootloader.
   * Closed-bootloader flashing (available once verified in v2.0+) checks
     'fastboot flashing get_unlock_ability == 1' and OTA/AVB payload
     consistency before ever triggering 'fastboot flashing lock'.

3. DATA LOSS:
   First-time installation (and unlocking/locking the bootloader) formats
   /data. Ensure important files are backed up beforehand.
------------------------------------------------------------------------
"""
    print(warning)


def run_cmd(cmd_list: list[str]) -> tuple[int, str] | tuple[None, str]:
    try:
        res = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        combined = f"{res.stdout}\n{res.stderr}".strip()
        return res.returncode, combined
    except FileNotFoundError:
        return None, "NOT_FOUND"
    except Exception as exc:
        return 1, str(exc)


def fastboot_cmd(serial: str | None, *args: str) -> list[str]:
    base = ["fastboot"]
    if serial:
        base.extend(["-s", serial])
    base.extend(args)
    return base


def adb_cmd(serial: str | None, *args: str) -> list[str]:
    base = ["adb"]
    if serial:
        base.extend(["-s", serial])
    base.extend(args)
    return base


def check_tools():
    print("[*] Checking platform tools (adb, fastboot)...")
    for tool in ("adb", "fastboot"):
        rc, out = run_cmd([tool, "--version"])
        if rc is None or out == "NOT_FOUND":
            print(f"[ERROR] Required tool '{tool}' not found in PATH!")
            print("Please install Android SDK Platform Tools and add it to PATH.")
            sys.exit(1)
    print("    -> Platform tools detected.")


def get_release_info(tag: str | None, use_latest: bool) -> dict:
    if use_latest:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    else:
        resolved_tag = tag if tag else f"v{VERSION}"
        if not resolved_tag.startswith("v"):
            resolved_tag = f"v{resolved_tag}"
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{resolved_tag}"

    print(f"[*] Querying release metadata ({url})...")
    req = urllib.request.Request(url, headers={"User-Agent": "VaultOs-Installer"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"    -> Discovered Release: {data['name']} ({data['tag_name']})")
            return data
    except Exception as exc:
        print(f"[ERROR] Failed to fetch release metadata: {exc}")
        sys.exit(1)


def download_file(url: str, target_path: str):
    fname = os.path.basename(target_path)
    print(f"[*] Downloading {fname}...")
    req = urllib.request.Request(url, headers={"User-Agent": "VaultOs-Installer"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(target_path, "wb") as out:
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        last_print = 0.0
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if total > 0 and (now - last_print > 1.0 or downloaded == total):
                pct = (downloaded / total) * 100
                print(
                    f"    [{fname}] {downloaded / (1024 * 1024):.1f} / "
                    f"{total / (1024 * 1024):.1f} MB ({pct:.1f}%)",
                    end="\r",
                    flush=True,
                )
                last_print = now
    print(f"\n    -> {fname} download complete.")


def verify_checksums(download_dir: str):
    print("\n[*] Verifying cryptographic integrity (SHA-256)...")
    sums_file = os.path.join(download_dir, "SHA256SUMS")
    if not os.path.exists(sums_file):
        print("[ERROR] SHA256SUMS file not found!")
        sys.exit(1)

    expected_hashes: dict[str, str] = {}
    with open(sums_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                expected_hashes[parts[1]] = parts[0]

    all_ok = True
    for fname, exp_hash in expected_hashes.items():
        fpath = os.path.join(download_dir, fname)
        if not os.path.exists(fpath):
            if fname in OPTIONAL_ASSETS or fname not in REQUIRED_ASSETS:
                continue
            print(f"    [FAIL] Missing file: {fname}")
            all_ok = False
            continue

        h = hashlib.sha256()
        with open(fpath, "rb") as f:
            while chunk := f.read(1024 * 1024):
                h.update(chunk)
        calc_hash = h.hexdigest()
        if calc_hash == exp_hash:
            print(f"    [VERIFIED] {fname}: SHA-256 OK ({calc_hash[:16]}...)")
        else:
            print(f"    [TAMPERED] {fname}: expected {exp_hash}, got {calc_hash}")
            all_ok = False

    if not all_ok:
        print("\n[CRITICAL ERROR] File integrity verification failed! Halting.")
        sys.exit(1)
    print("    -> All present release artifacts verified against SHA256SUMS.")


def read_release_flags(download_dir: str) -> tuple[bool, str]:
    flags_path = os.path.join(download_dir, "release_flags.json")
    if os.path.exists(flags_path):
        try:
            with open(flags_path, "r", encoding="utf-8") as f:
                flags = json.load(f)
            return bool(flags.get("locked_bootloader_supported", False)), str(
                flags.get("locked_bootloader_reason", "")
            )
        except Exception as exc:
            print(f"[WARN] Could not parse release_flags.json ({exc}); locking disabled.")
            return False, ""
    return LOCKED_BOOTLOADER_SUPPORTED, ""


def _parse_fastboot_devices(raw: str) -> list[str]:
    serials: list[str] = []
    for line in raw.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[1] == "fastboot":
            serials.append(parts[0])
    return serials


def _parse_adb_devices(raw: str) -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] in {"device", "recovery", "sideload"}:
            devices.append((parts[0], parts[1]))
    return devices


def detect_device(preferred_serial: str | None) -> tuple[str | None, str | None]:
    rc, fb_raw = run_cmd(["fastboot", "devices"])
    if rc == 0 and fb_raw:
        fb_devs = _parse_fastboot_devices(fb_raw)
        if preferred_serial:
            if preferred_serial in fb_devs:
                return "fastboot", preferred_serial
        else:
            otter_devs = []
            for ser in fb_devs:
                prc, pout = run_cmd(fastboot_cmd(ser, "getvar", "product"))
                if prc == 0 and EXPECTED_PRODUCT in pout.lower():
                    otter_devs.append(ser)
            if len(otter_devs) == 1:
                return "fastboot", otter_devs[0]
            if len(fb_devs) == 1:
                return "fastboot", fb_devs[0]
            if len(fb_devs) > 1:
                print(f"[ERROR] Multiple fastboot devices detected ({fb_devs}). Pass --serial <id>.")
                sys.exit(1)

    rc, adb_raw = run_cmd(["adb", "devices"])
    if rc == 0 and adb_raw:
        adb_devs = _parse_adb_devices(adb_raw)
        if preferred_serial:
            for ser, mode in adb_devs:
                if ser == preferred_serial:
                    return mode, ser
        else:
            non_emu = [(s, m) for s, m in adb_devs if not s.startswith("emulator-")]
            if len(non_emu) == 1:
                return non_emu[0][1], non_emu[0][0]
            if len(adb_devs) == 1:
                return adb_devs[0][1], adb_devs[0][0]
            if len(non_emu) > 1:
                print(f"[ERROR] Multiple physical ADB devices detected ({non_emu}). Pass --serial <id>.")
                sys.exit(1)

    return None, None


def wait_for_fastboot(preferred_serial: str | None) -> str:
    print("[*] Waiting for SHIFTphone 8 in Fastboot mode...")
    for _ in range(45):
        mode, ser = detect_device(preferred_serial)
        if mode == "fastboot" and ser:
            print(f"    -> Fastboot device ready: {ser}")
            return ser
        if mode in {"adb", "recovery"} and ser:
            print(f"[*] Rebooting {ser} ({mode}) to Fastboot bootloader...")
            subprocess.run(adb_cmd(ser, "reboot", "bootloader"))
            preferred_serial = ser
        time.sleep(2)
    print("[ERROR] Timeout waiting for device in Fastboot mode.")
    sys.exit(1)


def get_fastboot_var(serial: str, var: str) -> str:
    _, out = run_cmd(fastboot_cmd(serial, "getvar", var))
    for line in out.splitlines():
        if f"{var}:" in line:
            return line.split(f"{var}:", 1)[1].strip().lower()
    return ""


def verify_hardware_and_lock_state(serial: str, auto_yes: bool = False) -> bool:
    print(f"[*] Verifying hardware codename for {serial}...")
    product = get_fastboot_var(serial, "product")
    if EXPECTED_PRODUCT not in product:
        print(f"[SECURITY ALERT] Connected device '{product}' is not '{EXPECTED_PRODUCT}'. Aborting.")
        sys.exit(1)
    unlocked = get_fastboot_var(serial, "unlocked") == "yes"
    print(f"    -> Hardware: {product} | Bootloader unlocked: {'yes' if unlocked else 'no'}")
    if unlocked:
        return True

    rc, ability_out = run_cmd(fastboot_cmd(serial, "flashing", "get_unlock_ability"))
    if rc == 0 and "get_unlock_ability: 1" in ability_out:
        ans = "y" if auto_yes else input(
            "[?] Bootloader is locked, but OEM unlock is enabled (get_unlock_ability=1).\n"
            "    Trigger 'fastboot flashing unlock' now (wipes /data)? [y/N]: "
        ).strip().lower()
        if ans == "y":
            subprocess.run(fastboot_cmd(serial, "flashing", "unlock"))
            input("    -> Confirm 'Unlock the bootloader' on phone screen, let it return to fastboot, then press Enter...")
            if get_fastboot_var(serial, "unlocked") == "yes":
                return True
        print("[ERROR] Bootloader remains locked. Aborting installation.")
        sys.exit(1)

    print(
        "[ERROR] Bootloader is locked and 'get_unlock_ability' is 0.\n"
        "        Boot into Android Settings -> System -> Developer options,\n"
        "        enable 'OEM unlocking', reboot to fastboot, and re-run this installer."
    )
    sys.exit(1)


def verify_ota_payload_consistency(download_dir: str):
    """Ensure local vbmeta/boot images match vaultos_otter-ota.zip if pipeline module is present."""
    ota_zip = Path(download_dir) / "vaultos_otter-ota.zip"
    if not ota_zip.exists():
        return
    try:
        import extract_ota_images  # type: ignore
    except ImportError:
        return

    print("[*] Double-checking fastboot images against OTA payload.bin...")
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        extracted = extract_ota_images.extract_partitions(
            ota_zip, tmp_path, ("vbmeta", "vbmeta_system", "boot", "vendor_boot", "dtbo")
        )
        for part_name, (_, _, payload_sha) in extracted.items():
            local_img = Path(download_dir) / f"{part_name}.img"
            if not local_img.exists():
                continue
            local_sha = hashlib.sha256(local_img.read_bytes()).hexdigest()
            if local_sha != payload_sha:
                print(
                    f"[CRITICAL ERROR] {local_img.name} ({local_sha[:12]}...) does NOT match "
                    f"OTA payload ({payload_sha[:12]}...)! Aborting to prevent dm-verity brick."
                )
                sys.exit(1)
    print("    -> All boot/dtbo/vbmeta images match OTA payload byte-for-byte.")


def flash_unlocked_os(serial: str, download_dir: str, locked_supported: bool, lock_reason: str):
    print("\n" + "=" * 70)
    print("    BEGINNING FLASH PROCESS")
    print("=" * 70)

    if not locked_supported:
        print("\n[!] NOTICE: This release carries locked_bootloader_supported = false.")
        if lock_reason:
            print(f"    Reason: {lock_reason}")
        print("    Keep the bootloader UNLOCKED (do NOT run 'fastboot flashing lock').\n")

    boot_usb = os.path.join(download_dir, "boot-usb-debug.img")
    vboot_usb = os.path.join(download_dir, "vendor_boot-usb-debug.img")
    dtbo_img = os.path.join(download_dir, "dtbo.img")

    # Flash USB-debug boot/vendor_boot + matching dtbo on current slot so Recovery
    # has USB ADB enabled for sideload; the OTA payload atomically writes all matched
    # air-gapped production partitions (boot/vendor_boot/dtbo/vbmeta*/super) to target slot.
    pre_parts = [
        ("boot", boot_usb if os.path.exists(boot_usb) else os.path.join(download_dir, "boot.img")),
        ("vendor_boot", vboot_usb if os.path.exists(vboot_usb) else os.path.join(download_dir, "vendor_boot.img")),
        ("dtbo", dtbo_img),
    ]
    for part, img_file in pre_parts:
        print(f"[*] Flashing temporary recovery-capable {part} ({os.path.basename(img_file)})...")
        res = subprocess.run(fastboot_cmd(serial, "flash", part, img_file))
        if res.returncode != 0:
            print(f"[ERROR] Failed to flash {part}!")
            sys.exit(1)

    avb_key = os.path.join(download_dir, "avb_custom_key.bin")
    if os.path.exists(avb_key):
        print(f"[*] Enrolling VaultOs custom AVB public key ({os.path.basename(avb_key)})...")
        res = subprocess.run(fastboot_cmd(serial, "flash", "avb_custom_key", avb_key))
        if res.returncode != 0:
            print("[WARN] 'fastboot flash avb_custom_key' returned non-zero (continuing unlocked).")

    print("\n[*] Rebooting device into Recovery...")
    subprocess.run(fastboot_cmd(serial, "reboot", "recovery"))

    print("\n" + "-" * 70)
    print("[ACTION REQUIRED ON PHONE SCREEN]:")
    print("1. First install only: select 'Factory reset' -> 'Format data/factory reset'.")
    print("2. In Recovery main menu: select 'Apply update' -> 'Apply from ADB'.")
    print("Waiting automatically for ADB sideload mode...")
    print("-" * 70)

    subprocess.run(adb_cmd(serial, "wait-for-sideload"))
    ota_zip = os.path.join(download_dir, "vaultos_otter-ota.zip")
    print(f"\n[*] Sideloading full VaultOs production OTA ({os.path.basename(ota_zip)})...")
    res = subprocess.run(adb_cmd(serial, "sideload", ota_zip))
    if res.returncode != 0:
        print("[ERROR] Sideload failed! Check USB connection and recovery log.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("    FLASHING COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("Select 'Reboot system now' on the phone screen to boot production VaultOs.")
    if not locked_supported:
        print("[IMPORTANT] Keep the bootloader UNLOCKED on this release (closed bootloader is targeted for v2.0).")


def gate_and_lock_bootloader(serial: str, download_dir: str, auto_yes: bool):
    """Strict pre-lock safety gate for verified v2.0+ locked-bootloader builds."""
    locked_supported, lock_reason = read_release_flags(download_dir)
    if not locked_supported:
        print("\n[BLOCKED] Bootloader locking is DISABLED for this release (locked_bootloader_supported=false).")
        if lock_reason:
            print(f"          {lock_reason}")
        sys.exit(1)

    verify_ota_payload_consistency(download_dir)

    rc, unlock_out = run_cmd(fastboot_cmd(serial, "flashing", "get_unlock_ability"))
    ability = "1" if rc == 0 and "get_unlock_ability: 1" in unlock_out else "0"
    if ability != "1":
        print(
            "\n[BLOCKED] 'fastboot flashing get_unlock_ability' is 0!\n"
            "          Locking now would permanently block re-unlocking if a boot error occurs.\n"
            "          Verify /frp unlock flag = 0x01 in CustomOtterControl before locking."
        )
        sys.exit(1)

    avb_key = os.path.join(download_dir, "avb_custom_key.bin")
    if not os.path.exists(avb_key):
        print("[BLOCKED] Missing avb_custom_key.bin for custom AVB root-of-trust enrollment.")
        sys.exit(1)

    if not auto_yes:
        ans = input(
            "\n[CONFIRM LOCK] All pre-lock safety gates passed (get_unlock_ability=1).\n"
            "Running 'fastboot flashing lock' wipes /data. Type 'LOCK' to proceed: "
        ).strip()
        if ans != "LOCK":
            print("Aborted bootloader lock.")
            sys.exit(0)

    res = subprocess.run(fastboot_cmd(serial, "flash", "avb_custom_key", avb_key))
    if res.returncode != 0:
        print("[ERROR] Failed to flash avb_custom_key!")
        sys.exit(1)

    print("[*] Triggering 'fastboot flashing lock' — confirm on phone screen with Volume + Power.")
    subprocess.run(fastboot_cmd(serial, "flashing", "lock"))
    print(
        "[IMPORTANT] Keep 'OEM unlocking' ON in Developer Options until AFTER the first locked\n"
        "            Yellow Verified Boot reaches the home screen cleanly!"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VaultOs Sovereign Installer & Flasher (SHIFTphone 8)")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip initial confirmation prompt")
    parser.add_argument("-d", "--dir", type=str, default=None, help="Directory for release downloads/files")
    parser.add_argument("-s", "--serial", type=str, default=None, help="Target adb/fastboot device serial")
    parser.add_argument("--tag", type=str, default=None, help=f"GitHub release tag (default: v{VERSION})")
    parser.add_argument("--latest", action="store_true", help="Query GitHub /releases/latest instead of fixed version")
    parser.add_argument("--offline", action="store_true", help="Use local files in --dir without GitHub downloads")
    parser.add_argument("--lock", action="store_true", help="Gated bootloader lock workflow (v2.0+ releases only)")
    return parser.parse_args()


def main():
    args = parse_args()
    print_banner()
    print_security_warning()

    if not args.yes:
        confirm = input("Do you wish to proceed? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted by user.")
            sys.exit(0)

    check_tools()
    work_dir = os.path.abspath(args.dir) if args.dir else os.path.join(
        os.path.expanduser("~"), ".vaultos", "downloads", f"v{VERSION}"
    )
    os.makedirs(work_dir, exist_ok=True)

    if not args.offline:
        release_data = get_release_info(args.tag, args.latest)
        asset_urls = {a["name"]: a["browser_download_url"] for a in release_data.get("assets", [])}
        for asset_name in REQUIRED_ASSETS:
            target_path = os.path.join(work_dir, asset_name)
            if os.path.exists(target_path) and asset_name not in {"SHA256SUMS", "release_flags.json"}:
                print(f"[*] Found existing local file: {asset_name} (skipping download).")
                continue
            if asset_name in asset_urls:
                download_file(asset_urls[asset_name], target_path)
            elif asset_name in OPTIONAL_ASSETS:
                print(f"[*] Optional metadata asset '{asset_name}' not attached; continuing.")
            else:
                print(f"[ERROR] Asset '{asset_name}' not found in release assets!")
                sys.exit(1)

    verify_checksums(work_dir)
    locked_supported, lock_reason = read_release_flags(work_dir)

    if args.lock and not locked_supported:
        print("\n[BLOCKED] '--lock' is not permitted on this release (locked_bootloader_supported=false).")
        if lock_reason:
            print(f"          {lock_reason}")
        sys.exit(1)

    serial = wait_for_fastboot(args.serial)
    verify_hardware_and_lock_state(serial, auto_yes=args.yes)

    if args.lock:
        gate_and_lock_bootloader(serial, work_dir, args.yes)
    else:
        verify_ota_payload_consistency(work_dir)
        flash_unlocked_os(serial, work_dir, locked_supported, lock_reason)


if __name__ == "__main__":
    main()
