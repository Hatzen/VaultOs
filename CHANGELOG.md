# Changelog

All notable changes to the VaultOs operating system and platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Planned
- Automated in-OS OTA update checker & Ed25519 verification client.
- European sovereign mirror setup (Hetzner, Germany).
- Hardware attestation & bootloader re-locking with custom AVB root-of-trust.

---

## [1.0.1] - 2026-11-14

### Fixed
- **Critical — `CustomOtterControl` False-Positive Wipe & Wakelock Fixes**:
  - Fixed `CellularConnectionDetector` returning `true` when `READ_PHONE_STATE` was not granted and fixed invalid `TELEPHONY_SERVICE` -> `SubscriptionManager` cast.
  - Gated automated factory-reset behind an opt-in preference (`default = false`) in `ConnectionGuard`, preventing accidental wipes on service launch.
  - Resolved JobScheduler ID collision (`0` vs `1001`/`1002`), removed forced 2-second `overrideDeadline` polling, and called `jobFinished()` in `UsbSchedulerService`, `NetworkSchedulerService`, and `BluetoothNfcGuardService`.
  - Pre-granted runtime permissions for `CustomOtterControl` and switched prebuilt packaging to signed release APKs (`app-release.apk`).
- **Critical — Kernel USB Air-Gap Restoration (`WITH_USB_DEBUG`)**:
  - Re-disabled `dwc3@a600000` in `yupik-usb.dtsi` and guarded `dwc3_msm_probe()` behind `!defined(CONFIG_VAULTOS_USB_DEBUG)`.
  - Added compile-time `WITH_USB_DEBUG=true` (`CONFIG_VAULTOS_USB_DEBUG`) toggle in `BoardConfig.mk` and `Kconfig` to generate separate `boot-usb-debug.img` / `vendor_boot-usb-debug.img` developer images while keeping production releases hardware-airgapped.
- **Battery Optimization & Dead Radio/Wi-Fi Service Removal**:
  - Set `ro.radio.noril=yes`, `ro.vendor.radio.noril=yes`, and `config.disable_telephony=true`, omitted telephony/Wi-Fi feature XMLs from `device.mk`, blocklisted `rmnet_*.ko`, and stopped background RIL/CNSS/LOWI/Wificond polling daemons (`init.class_main.sh`, `init.target.rc`, `init.qcom.rc`, `init.vaultos.rc`).
- **Custom Bootanimation & Default Wallpaper Enforcement**:
  - Set `TARGET_BOOTANIMATION := vendor/vaultos/media/bootanimation.zip` in `BoardConfig.mk`.
  - Removed `theme:` nesting from `FrameworkResVaultOs`, `SystemUIResVaultOs`, and `SettingsProviderResVaultOs` so Android 16 scans static RROs in `/product/overlay/`, and populated all density buckets for `default_wallpaper.png`.

### Added
- **Multi-Root Workspace & Prebuilt Release Pipeline**:
  - Added `VaultOs.code-workspace` for unified Git source control across all 9 VaultOs repositories.
  - Added `tools/pipeline/update_prebuilt_apps.ps1` and `.sh` to compile and stage release APKs for `CustomOtterControl` and `ParAnnoying`.

---

## [1.0.0] - 2026-11-14 *(Pre-Release — Superseded by 1.0.1)*

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
