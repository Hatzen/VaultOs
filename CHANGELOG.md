# Changelog

All notable changes to the VaultOs operating system and platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Planned
- Automated in-OS OTA update checker & Ed25519 verification client.
- European sovereign mirror setup (Hetzner, Germany).
- Verified Boot / Custom AVB 2.0 Root-of-Trust for locked bootloader: delivered in `1.0.2` (`WITH_AVB ?= true` + `avb_custom_key`). Remaining future work: release-key APK platform signing (`PRODUCT_DEFAULT_DEV_CERTIFICATE`) and `user` build type hardening.

---

## [1.0.2] - 2026-11-15

> [!NOTE]
> **RELEASE DISCLAIMER — UNOFFICIAL COMMUNITY BUILD WITH CUSTOM AVB 2.0 ROOT-OF-TRUST**
>
> - This `v1.0.2` release (`vaultos_otter`) is an unofficial community build (`eng`/`userdebug` lineage build string still carries `UNOFFICIAL-otter` / `test-keys` for APEX/APK Java signing), **with full Android Verified Boot (AVB 2.0) enabled (`vbmeta` & `vbmeta_system` `Flags: 0`, `SHA256_RSA4096`) and signed with the VaultOs custom AVB key (`avb_custom_key.bin`)**.
> - On **SHIFTphone 8 (`otter`)**, you **CAN** lock the bootloader with this `v1.0.2` release **only after**:
>   1. Flashing `vbmeta.img`, `vbmeta_system.img`, and enrolling `avb_custom_key` (`fastboot flash avb_custom_key avb_custom_key.bin`),
>   2. Flashing `boot.img` / `vendor_boot.img` / `dtbo.img` and sideloading `vaultos_otter-ota.zip`, and
>   3. Running and passing the built-in **CustomOtterControl -> OEM Lock Readiness Check** dry-run inside the booted OS.
> - **Do NOT lock the bootloader** on earlier releases (`v1.0.0`, `v1.0.1`), on debug boot images if mismatched, or on self-built images compiled without `WITH_AVB=true` and a custom private AVB key (those are unofficial unsigned/`--flags 3` builds and **cannot run with a locked bootloader**).

### Added
- **Bootloader Lock-Ready Production Default (`WITH_AVB ?= true`)**:
  - Updated `BoardConfig.mk` (`device/shift/otter`, commit `f231af1`) so Verified Boot (`WITH_AVB ?= true`) is enabled by default for production builds and automatically picks up `vendor/vaultos/security/avb_custom_key.pem` (`SHA256_RSA4096`) when present (`vbmeta` & `vbmeta_system` `Flags: 0`, `avbtool info_image` verified).
  - `avb_custom_key.bin` (SHA-256: `54085da319aa83befe4e8df03aaeb2f992b4f6940ac8865d855d3bc6419664ed`, SHA-1: `494589df304dbee089f10c21b25b07511794f9b5`) is published with the release for `fastboot flash avb_custom_key avb_custom_key.bin`.
  - Updated `vendor/vaultos/.gitignore` (`3e48215`) so private keys (`*.pem`, `*.key`, `*.pk8`) are never committed.
- **New OLED Default Wallpaper (`VaultOs powered by Bastegra`)**:
  - Generated `default_wallpaper.png` (`1080x2400`, pure OLED black background matching `bootanimation.zip` neon-teal/cyan glowing arcs and white `V` emblem, `"V A U L T   O S"` title, and `"VaultOs powered by Bastegra"` slogan) across all 7 `FrameworkResVaultOs` resource buckets (`drawable-hdpi`, `drawable-nodpi`, `drawable-sw600dp-nodpi`, `drawable-sw720dp-nodpi`, `drawable-xhdpi`, `drawable-xxhdpi`, `drawable-xxxhdpi`).
- **CustomOtterControl & App Suite Updates**:
  - Added **OEM Lock Readiness Dry-Run Check** inside `CustomOtterControl` to verify AVB state, vbmeta digest, custom key enrollment readiness, and partition integrity before locking the bootloader.
  - Added **SD Card `.zip` Provisioning Importer** & **Mandatory APK Update** handler (`CustomOtterControl`).
  - Implemented roadmap features `001`, `003`, `004`, `006`, `009`, and `011`.
  - Deactivated `FancyLauncher` from the bundled app suite.
- **Release & Installer Updates**:
  - Updated `vaultos_installer.py` and `README.md` for `v1.0.2` (`vbmeta.img`, `vbmeta_system.img`, `avb_custom_key.bin`) and added explicit locked-bootloader disclaimers across all releases (`v1.0.0`, `v1.0.1`, `v1.0.2`).

### Cryptographic Checksums (SHA-256)
| Artifact | Size (Bytes) | SHA-256 |
|---|---|---|
| `boot.img` | 100663296 | `a62764f8d2211b3ba671d902ba9448625607360e48f46c1e38423ff2a47db482` |
| `vendor_boot.img` | 100663296 | `d2225c48c101588d3458b18e358addd5e28da0fc2dc6c3e7f02115b521fd82e4` |
| `dtbo.img` | 25165824 | `85e05880e32d65a2d76b8db9393f0adb9883654f4491bb1d25bb874e9a56c837` |
| `vbmeta.img` | 65536 | `04e18ceed5052d545b194df32e045b95606384c7ffb897da3bd1df446f5673dd` |
| `vbmeta_system.img` | 65536 | `8dd94087d0da5013d14a1accb155e44b9d7f75003ddf3a12ccf5b467296d75a6` |
| `avb_custom_key.bin` | 1032 | `54085da319aa83befe4e8df03aaeb2f992b4f6940ac8865d855d3bc6419664ed` |
| `boot-usb-debug.img` | 100663296 | `ec093bb510c19f19dab553301a59301cc4786b1ccd247a2f860341a82bcffd84` |
| `vendor_boot-usb-debug.img` | 100663296 | `c00516e8bedda1f1ca0652307404a36244343cf306c1d827d108a4f48d9642d8` |
| `vaultos_otter-ota.zip` | 1853708679 | `5c879030bba2e7aa8b42c0d53171b9dd42b2d4185e3d03d4157e2f1945869aec` |

---

## [1.0.1] - 2026-11-15

> [!CAUTION]
> **DISCLAIMER — UNOFFICIAL UNSIGNED BUILD (CANNOT RUN WITH LOCKED BOOTLOADER)**
>
> `v1.0.1` is an unofficial unsigned build generated with `vbmeta flags=3` (`--flags 3`, AVB verification disabled) and default AOSP test-keys. **It CANNOT run with a locked bootloader** — running `fastboot flashing lock` on `v1.0.1` will halt boot (`device is corrupt`). Upgrade to `v1.0.2` (with `avb_custom_key.bin`) before locking the bootloader.

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
- **Prebuilt KernelSU-Next Packaging**:
  - Added `preprocessed: true` and `skip_preprocessed_apk_checks: true` for `KernelSU` (`KernelSU_Next_v3.3.0_33214-release.apk`, `targetSdkVersion=36`) to preserve its upstream v2 signature.

### Added
- **Multi-Root Workspace & Prebuilt Release Pipeline**:
  - Added `VaultOs.code-workspace` for unified Git source control across all 9 VaultOs repositories.
  - Added `tools/pipeline/update_prebuilt_apps.ps1` and `.sh` to compile and stage release APKs for `CustomOtterControl` and `ParAnnoying`.

### Cryptographic Checksums (SHA-256)

| Artifact | Size | SHA-256 Checksum |
| :--- | :--- | :--- |
| `boot.img` | 96.0 MiB | `4487e5047ad6be001d7d9854f236995ae429f266672d812a5995b285dada8046` |
| `vendor_boot.img` | 96.0 MiB | `cd604194d3a5b87746a4a689f9c90c377db1733d3c03943c3411f1c073f0ccfd` |
| `dtbo.img` | 24.0 MiB | `eb0c4fc48bb3d2427160e9581712d491859a3f14eba256ae681be73549fe3469` |
| `boot-usb-debug.img` | 96.0 MiB | `57dca85fb0b3b970e954fbd3daa678be9bdcdab14fe8e6d16c30f91d9753b27c` |
| `vendor_boot-usb-debug.img` | 96.0 MiB | `b98ea61a85ffe8477ebdbf3ba3f2fbe5f3f3c44ecae9ffaef1c28451f8ee0f90` |
| `vaultos_otter-ota.zip` | 1.73 GiB | `9667150c57dd91adccc59dddc2c53f2c43b4bdc56d875a98e617836074191e7c` |

---

## [1.0.0] - 2026-11-14 *(Pre-Release — Superseded by 1.0.1)*

> [!CAUTION]
> **DISCLAIMER — UNOFFICIAL UNSIGNED BUILD (CANNOT RUN WITH LOCKED BOOTLOADER)**
>
> `v1.0.0` is an unofficial unsigned pre-release build generated with `vbmeta flags=3` (`--flags 3`, AVB verification disabled) and default AOSP test-keys. **It CANNOT run with a locked bootloader** — running `fastboot flashing lock` on `v1.0.0` will halt boot (`device is corrupt`). Upgrade to `v1.0.2` (with `avb_custom_key.bin`) before locking the bootloader.

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
