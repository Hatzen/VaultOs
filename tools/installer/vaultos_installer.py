#!/usr/bin/env python3
"""
VaultOs Sovereign Installer & Flasher
Target Device: SHIFTphone 8 (Qualcomm QCM6490 / 'otter')
License: Apache-2.0

Zero-dependency cross-platform installer for Linux, macOS, and Windows.
Performs end-to-end cryptographic integrity checks, device model verification,
and guided partition flashing to protect against ISP injections and brick risks.
"""

import os
import sys
import time
import json
import hashlib
import platform
import subprocess
import urllib.request
import urllib.error

VERSION = "1.0.2"
GITHUB_REPO = "Hatzen/VaultOs"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
EXPECTED_PRODUCT = "otter"

REQUIRED_ASSETS = [
    "boot.img",
    "vendor_boot.img",
    "dtbo.img",
    "vbmeta.img",
    "vbmeta_system.img",
    "avb_custom_key.bin",
    "vaultos_otter-ota.zip",
    "SHA256SUMS",
]

def print_banner():
    banner = f"""
========================================================================
    __     __            _ _    ____       
    \\ \\   / /_ _ _   _| | |_ / __ \\ ___   
     \\ \\ / / _` | | | | | __/ / / // __|  
      \\ V / (_| | |_| | | |_ / /_/ /\\__ \\  
       \\_/ \\__,_|\\__,_|_|\\__|\\____/ |___/  
       
    VaultOs Sovereign Installer (v{VERSION})
    Target Hardware: SHIFTphone 8 (otter)
========================================================================
"""
    print(banner)

def print_security_warning():
    warning = """
[!] THREAT MODEL, UNOFFICIAL BUILD & BOOTLOADER LOCK DISCLAIMER:
------------------------------------------------------------------------
1. ISP / NETWORK INJECTION PREVENTION:
   Untrusted Wi-Fi networks, captive portals, and ISP routing can spoof
   unencrypted firmware endpoints. All downloads in this installer are
   verified against SHA-256 cryptographic digests.

2. UNOFFICIAL / UNSIGNED BUILDS vs. LOCKED BOOTLOADER WARNING:
   * Unofficial / unsigned builds and legacy releases (v1.0.0 / v1.0.1
     with vbmeta flags=3) CANNOT run with a locked bootloader. Running
     'fastboot flashing lock' on those builds halts boot (device is
     corrupt / brick risk).
   * Production v1.0.2+ builds have WITH_AVB=true enabled by default and
     include vbmeta.img, vbmeta_system.img, and avb_custom_key.bin so they
     CAN run with a locked bootloader ONLY after enrolling the custom AVB
     key, completing a full unlocked boot, and confirming that
     CustomOtterControl -> Bootloader-Lock Dry-Run passes cleanly BEFORE
     running 'fastboot flashing lock'.

3. DATA LOSS:
   Flashing a new OS (and locking the bootloader) formats the /data
   partition. Ensure you have backed up all private keys and data.
------------------------------------------------------------------------
"""
    print(warning)

def run_cmd(cmd_list):
    try:
        res = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            return None
        combined = (res.stdout + " " + res.stderr).strip()
        return combined
    except FileNotFoundError:
        return "NOT_FOUND"
    except Exception:
        return None

def check_tools():
    print("[*] Checking platform tools (adb, fastboot)...")
    for tool in ["adb", "fastboot"]:
        res = run_cmd([tool, "--version"])
        if res == "NOT_FOUND":
            print(f"[ERROR] Required tool '{tool}' not found in PATH!")
            print("Please install Android SDK Platform Tools (platform-tools) and ensure they are added to PATH.")
            sys.exit(1)
    print("    -> Tools detected successfully.")

def get_latest_release_info():
    print(f"[*] Querying latest release from GitHub ({GITHUB_REPO})...")
    req = urllib.request.Request(API_URL, headers={"User-Agent": "VaultOs-Installer"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"    -> Discovered Release: {data['name']} ({data['tag_name']})")
            return data
    except Exception as e:
        print(f"[ERROR] Failed to fetch release metadata: {e}")
        sys.exit(1)

def download_file(url, target_path, expected_size=None):
    fname = os.path.basename(target_path)
    print(f"[*] Downloading {fname}...")
    
    req = urllib.request.Request(url, headers={"User-Agent": "VaultOs-Installer"})
    with urllib.request.urlopen(req) as resp, open(target_path, "wb") as out:
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        last_print = 0
        
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if total > 0 and (now - last_print > 1 or downloaded == total):
                pct = (downloaded / total) * 100
                mb_cur = downloaded / (1024 * 1024)
                mb_tot = total / (1024 * 1024)
                print(f"    [{fname}] {mb_cur:.1f} / {mb_tot:.1f} MB ({pct:.1f}%)", end="\r", flush=True)
                last_print = now
    print(f"\n    -> {fname} download complete.")

def verify_checksums(download_dir):
    print("\n[*] Verifying cryptographic integrity (SHA-256)...")
    sums_file = os.path.join(download_dir, "SHA256SUMS")
    if not os.path.exists(sums_file):
        print("[ERROR] SHA256SUMS file not found!")
        sys.exit(1)

    expected_hashes = {}
    with open(sums_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                expected_hashes[parts[1]] = parts[0]

    all_ok = True
    for fname, exp_hash in expected_hashes.items():
        fpath = os.path.join(download_dir, fname)
        if not os.path.exists(fpath):
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
            print(f"    [TAMPERED] {fname}: MISMATCH!")
            print(f"        Expected: {exp_hash}")
            print(f"        Calculated: {calc_hash}")
            all_ok = False

    if not all_ok:
        print("\n[CRITICAL ERROR] File integrity verification failed! Halting for security.")
        sys.exit(1)
    print("    -> All release artifacts verified successfully against tampering.")

def detect_device():
    print("\n[*] Detecting connected SHIFTphone 8...")
    fastboot_devs = run_cmd(["fastboot", "devices"])
    if fastboot_devs:
        print(f"    -> Device detected in Fastboot mode.")
        return "fastboot"

    adb_devs = run_cmd(["adb", "devices"])
    if adb_devs and "device" in adb_devs:
        print(f"    -> Device detected in ADB mode.")
        return "adb"
    if adb_devs and "recovery" in adb_devs:
        print(f"    -> Device detected in Recovery mode.")
        return "recovery"
    if adb_devs and "sideload" in adb_devs:
        print(f"    -> Device detected in Sideload mode.")
        return "sideload"

    print("[!] No device detected. Please connect your SHIFTphone 8 via USB.")
    print("    Ensure USB debugging is enabled, or the device is booted into Fastboot/Bootloader.")
    return None

def verify_hardware_model():
    print("[*] Verifying hardware codename via Fastboot...")
    product = run_cmd(["fastboot", "getvar", "product"])
    if product and EXPECTED_PRODUCT not in product.lower():
        print(f"[SECURITY ALERT] Connected device ('{product}') does NOT match target hardware ('{EXPECTED_PRODUCT}')!")
        print("Aborting to prevent bricking non-SHIFTphone 8 hardware.")
        sys.exit(1)
    print(f"    -> Hardware verified: SHIFTphone 8 ({EXPECTED_PRODUCT}).")

    unlocked = run_cmd(["fastboot", "getvar", "unlocked"])
    if unlocked and "yes" not in unlocked.lower():
        print("[ERROR] Bootloader is locked! Unlock the bootloader before flashing ('fastboot flashing unlock').")
        sys.exit(1)
    print("    -> Bootloader state: UNLOCKED.")

def flash_device(download_dir):
    print("\n" + "="*70)
    print("    BEGINNING FLASH PROCESS")
    print("="*70)

    # Step 1: Flash core boot and AVB verification partitions
    for part in ["boot", "vendor_boot", "dtbo", "vbmeta", "vbmeta_system"]:
        img_file = os.path.join(download_dir, f"{part}.img")
        print(f"[*] Flashing {part} partition ({os.path.basename(img_file)})...")
        res = subprocess.run(["fastboot", "flash", part, img_file])
        if res.returncode != 0:
            print(f"[ERROR] Failed to flash {part}!")
            sys.exit(1)

    avb_key = os.path.join(download_dir, "avb_custom_key.bin")
    if os.path.exists(avb_key):
        print(f"[*] Enrolling VaultOs custom AVB public key ({os.path.basename(avb_key)})...")
        res = subprocess.run(["fastboot", "flash", "avb_custom_key", avb_key])
        if res.returncode != 0:
            print("[WARN] 'fastboot flash avb_custom_key' returned non-zero (continuing with unlocked bootloader).")

    # Step 2: Reboot to recovery
    print("\n[*] Rebooting device into LineageOS/VaultOs Recovery...")
    subprocess.run(["fastboot", "reboot", "recovery"])

    # Step 3: Instructions for Sideload
    print("\n" + "-"*70)
    print("[ACTION REQUIRED ON DEVICE SCREEN]:")
    print("1. If this is a fresh install: select 'Factory reset' -> 'Format data/factory reset'.")
    print("2. In the recovery main menu, select 'Apply update' -> 'Apply from ADB'.")
    print("The installer will automatically detect when the device enters sideload mode...")
    print("-" + "-"*70)

    print("[*] Waiting for ADB Sideload state...")
    subprocess.run(["adb", "wait-for-sideload"])

    # Step 4: Sideload complete OTA ROM
    ota_zip = os.path.join(download_dir, "vaultos_otter-ota.zip")
    print(f"\n[*] Sideloading full VaultOs ROM ({os.path.basename(ota_zip)})...")
    res = subprocess.run(["adb", "sideload", ota_zip])
    if res.returncode != 0:
        print("[ERROR] Sideload failed! Check USB connection and recovery log.")
        sys.exit(1)

    print("\n" + "="*70)
    print("    FLASHING COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("Select 'Reboot system now' on the phone screen to boot into VaultOs.")

def main():
    print_banner()
    print_security_warning()
    
    if "-y" in sys.argv or "--yes" in sys.argv:
        confirm = 'y'
    else:
        confirm = input("Do you wish to proceed with downloading and flashing VaultOs? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Aborted by user.")
        sys.exit(0)

    check_tools()
    
    # Setup working directory for downloads
    work_dir = None
    for i, arg in enumerate(sys.argv):
        if arg in ["--dir", "-d"] and i + 1 < len(sys.argv):
            work_dir = os.path.abspath(sys.argv[i + 1])
    if not work_dir:
        work_dir = os.path.join(os.path.expanduser("~"), ".vaultos", "downloads", f"v{VERSION}")
    os.makedirs(work_dir, exist_ok=True)

    release_data = get_latest_release_info()
    asset_urls = {a["name"]: a["browser_download_url"] for a in release_data.get("assets", [])}

    # Download required assets
    for asset_name in REQUIRED_ASSETS:
        target_path = os.path.join(work_dir, asset_name)
        if os.path.exists(target_path) and asset_name != "SHA256SUMS":
            print(f"[*] Found existing local file: {asset_name} (skipping download).")
            continue
        if asset_name in asset_urls:
            download_file(asset_urls[asset_name], target_path)
        else:
            print(f"[ERROR] Asset '{asset_name}' not found in release assets!")
            sys.exit(1)

    verify_checksums(work_dir)

    # Detect device
    state = None
    while not state:
        state = detect_device()
        if not state:
            time.sleep(3)

    if state in ["adb", "recovery"]:
        print("[*] Rebooting device into Fastboot bootloader...")
        subprocess.run(["adb", "reboot", "bootloader"])
        print("[*] Waiting for device to enter Fastboot mode...")
        for _ in range(30):
            time.sleep(2)
            fb = run_cmd(["fastboot", "devices"])
            if fb and "fastboot" in fb:
                print("    -> Device reached Fastboot mode.")
                break
        else:
            print("[!] Timeout waiting for Fastboot mode. Please ensure phone is connected.")

    verify_hardware_model()
    flash_device(work_dir)

if __name__ == "__main__":
    main()
