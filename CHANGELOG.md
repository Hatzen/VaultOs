# Changelog

All notable changes to the VaultOs operating system and platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Planned
- Standalone zero-dependency cross-platform installer (Windows & Linux).
- Automated in-OS OTA update checker & Ed25519 verification client.
- European sovereign mirror setup (Hetzner, Germany).
- Hardware attestation & bootloader re-locking with custom AVB root-of-trust.

---

## [1.0.0] - 2026-11-14

### Added
- **Initial Official VaultOs Release** for the **SHIFTphone 8 (`otter`)**.
- **Android 16 / LineageOS 23.2 (`BP4A`)** sovereign base system.
- **Air-Gapped Hardened Kernel** (`5.4.302-qgki`):
  - Native **KernelSU-Next** manual hook integration (`v3.3.0`).
  - Restrictive USB data blocking profiles for forensic defense against hardware interception.
- **Offline SetupWizard**:
  - Fully offline initial provisioning bypassing mandatory Google, SIM, and Wi-Fi captive portals.
- **Decoupled Architecture**:
  - Full modular ROM layer decoupled into `vendor/vaultos`.
  - Upstream-clean device tree in `device/shift/otter` (`android_device_shift_otter`).
- **Cyber-Teal OLED Bootanimation**:
  - High-performance 35 FPS boot animation featuring the central VaultOs vector icon with dual rotating neon-teal and electric-cyan arcs (`#03DAC5` / `#00E5FF`) on pure OLED black.
- **Custom Otter Control (`v1.0`)**:
  - Hardware button integration and screen OCR text extraction.
  - Quick actions for Fastboot and Recovery reboots.
  - Integrated ISP injection, tamper risk, and bootloader brick prevention advisories.
  - Emergency device wipe capability (`MASTER_CLEAR`).
- **Sovereign Utility Suite**:
  - Prebuilt air-gapped office and documentation tooling (Collabora Office Mobile).
  - On-device local LLM engine (Pocket LLM).
  - Isolated terminal environment (Termux).
  - Offline command manual and knowledge bases (Linux Command Bibliotheca, Wikipedia Kiwix reader).
  - Sensor-driven star and sky orientation (SkyMap).
  - Device telemetry and battery preservation (Stepsy, Kernel Manager).
- **Security & Overlay Design**:
  - Pure OLED black dark mode with cyber-teal accent palettes (`#03DAC5` / `#018786`).
  - Presigned APK validation enforcing uncompressed JNI execution rules.

### Fixed
- **System Installer Collision**: Removed Insular from system prebuilts (`/product/app`) to prevent fatal `PackageManagerService` installer collision (`There must be exactly one installer`). Insular is supported as a user-level sandboxing app on `/data`.
- **Prebuilt APK Validation**: Resolved Android 16 targetSdkVersion >= 30 preprocessed enforcement for all bundled apps.

### Cryptographic Checksums (SHA-256)

| Artifact | Size | SHA-256 Checksum |
| :--- | :--- | :--- |
| `boot.img` | 96.0 MB | `5a94171771823c936a055d921f58ca820cb496e4597ddc6ac0cb88d97b58c5e3` |
| `vendor_boot.img` | 96.0 MB | `720891c46691e4a886686c24466c532a033691a05e3ad0ec10d495be60205d2b` |
| `dtbo.img` | 24.0 MB | `9324df9b9e0c2504d559760620786f105861faec3fedbc749fdf823a7303c6f2` |
| `vaultos_otter-ota.zip` | 1.73 GB | `c57749882337a814bfdd6f6267c392fbd9b1a5ef6231496ae44e4040bfca5714` |
