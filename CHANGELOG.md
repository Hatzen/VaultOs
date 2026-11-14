# Changelog

All notable changes to the VaultOs operating system and platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Planned
- Standalone zero-dependency cross-platform installer (Windows & Linux).
- Automated in-OS OTA update checker & verification client.
- Hardware killswitch dashboard in Custom Otter Control.
- European sovereign mirror setup (Hetzner, Germany).

---

## [1.0.0] - 2026-11-14

### Added
- **Initial Official VaultOs Release** for the **SHIFTphone 8 (`otter`)**.
- **Android 16 / LineageOS 23.2 (`BP4A`)** sovereign base system.
- **Air-Gapped Hardened Kernel** (`5.4.302-qgki`):
  - Native **KernelSU-Next** manual hook integration (`v3.3.0`).
  - Restrictive USB data blocking profiles for forensic defense.
- **Offline SetupWizard**:
  - Automatically bypasses mandatory Google / cellular SIM / Wi-Fi provisioning screens.
- **Decoupled Architecture**:
  - Full modular ROM layer decoupled into `vendor/vaultos`.
  - Upstream-clean device tree in `device/shift/otter` (`android_device_shift_otter`).
- **Sovereign Utility Suite**:
  - Prebuilt air-gapped office and documentation tooling (Collabora Office Mobile).
  - On-device local LLM engine (Pocket LLM).
  - Isolated terminal environment (Termux).
  - Secure sandboxing & work profile manager (Insular / Island).
  - Offline command manual and knowledge bases (Linux Command Bibliotheca, Wikipedia Kiwix reader).
  - Sensor-driven star and sky orientation (SkyMap).
  - Device telemetry and battery preservation (Custom Otter Control, Stepsy, Kernel Manager).
- **Security & Overlay Design**:
  - Pure OLED black dark mode with cyber-teal accent palettes (`#03DAC5` / `#018786`).
  - Presigned APK validation enforcing uncompressed JNI execution rules.

### Security
- Cryptographic SHA-256 and Ed25519 payload verification standards.
- Enforced air-gap networking constraints at the framework overlay level.
