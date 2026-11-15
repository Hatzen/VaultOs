<p align="center">
  <h1 align="center">VaultOs</h1>
  <p align="center"><strong>The Sovereign, Air-Gapped, Privacy-First Mobile Operating System</strong></p>
  <p align="center">Built for the <strong>SHIFTphone 8</strong> (QCM6490 / <code>otter</code>) on <strong>Android 16 / LineageOS 23.2</strong></p>
</p>

---

## 🛡️ Mission & Philosophy

Modern smartphones are built on continuous data extraction, opaque telemetry, remote killswitches, and mandatory cloud dependencies. **VaultOs** re-architects the mobile computing paradigm around absolute digital sovereignty:

* **Zero Mandatory Connectivity**: The OS boots and functions 100% offline. No cloud accounts, no SIM activation traps, no telemetry pings.
* **Hardware Repairability & Trust**: Developed natively for the modular, ethically manufactured, repairable **SHIFTphone 8** (`otter`).
* **Kernel-Level Hardening**: Built with an air-gapped Linux kernel (`5.4-qgki`) with integrated **KernelSU-Next**, strict USB data gating against forensic interception, and root-level control given back to the device owner.
* **Cryptographic Attestation**: Separation of open community reproducible builds from official hardware-verified release signatures.

---

## 📱 Supported Devices

| Device | Codename | Platform | Android Version | Status |
| :--- | :--- | :--- | :--- | :--- |
| **SHIFTphone 8** | `otter` | Qualcomm Yupik / QCM6490 | **16 (BP4A / LineageOS 23.2)** | **Active (`v1.0.2` AVB 2.0)** |

> [!WARNING]
> **DISCLAIMER — Unofficial Builds vs. Locked Bootloader Support**
>
> * **Unofficial / Unsigned Builds (including legacy releases `v1.0.0` & `v1.0.1`)**: Any unofficial build compiled without a private `avb_custom_key.pem` and `WITH_AVB=true` (i.e. `vbmeta flags=3` / AOSP public `testkey`) is an **unofficial unsigned build that CANNOT run with a locked bootloader**. Executing `fastboot flashing lock` on such a build will fail Verified Boot (`device is corrupt`).
> * **Production `v1.0.2`+ Builds (`WITH_AVB=true` default)**: Built with Android Verified Boot 2.0 enabled (`vbmeta flags=0`) and signed with the VaultOs custom AVB key (`avb_custom_key.bin`). These builds **can** run with a locked bootloader once you enroll `avb_custom_key.bin` while unlocked, complete a full first boot, and verify **`CustomOtterControl` → Bootloader-Lock Dry-Run** reports `✅ BEREIT FUER CLOSED BOOTLOADER` before running `fastboot flashing lock`.

---

## 🏛️ Repository Architecture

VaultOs is built on a clean, modular repository layout:

```
VaultOs Platform
├── Hatzen/VaultOs                     # Flagship portal, documentation, releases & installer
├── Hatzen/android_vendor_vaultos      # ROM vendor layer: overlays, apps, runtime configs, manifests
├── Hatzen/android_device_shift_otter  # Upstream-aligned SHIFTphone 8 device tree
├── Hatzen/android_kernel_shift_qcm6490# Hardened kernel with KernelSU-Next & air-gap features
└── Hatzen/android_packages_apps_SetupWizard # Offline provisioning setup wizard
```

---

## ⚡ Flashing VaultOs

### Option A: Automated Standalone Installer (Recommended)

VaultOs includes a zero-dependency, cross-platform CLI installer for Linux, macOS, and Windows that handles downloads, cryptographic SHA-256 validation, device codename assertion, and guided flashing automatically:

```bash
# 1. Clone repository
git clone https://github.com/Hatzen/VaultOs.git
cd VaultOs

# 2. Run the installer (requires python 3.8+ and platform-tools in PATH)
python tools/installer/vaultos_installer.py
```

---

### Option B: Manual Flashing Steps

#### Prerequisites
* Unlocked bootloader on your SHIFTphone 8 (`fastboot getvar unlocked` -> `yes`).
* Android platform-tools (`adb` and `fastboot`).
* Release files from the [Releases](https://github.com/Hatzen/VaultOs/releases) page:
  * `boot.img`
  * `vendor_boot.img`
  * `dtbo.img`
  * `vbmeta.img` & `vbmeta_system.img` (`v1.0.2`+)
  * `avb_custom_key.bin` (`v1.0.2`+ custom AVB 2.0 public key)
  * `vaultos_otter-ota.zip`
  * `SHA256SUMS`

> [!CAUTION]
> **Check Release Signature Before Locking Bootloader**: Legacy releases (`v1.0.0`, `v1.0.1`) and self-compiled builds without `WITH_AVB=true` are **unofficial unsigned builds that cannot run with a locked bootloader**. Never lock the bootloader on those builds.

#### Manual Steps
1. **Reboot to Fastboot**:
   ```bash
   adb reboot bootloader
   ```
2. **Flash Core Partitions**:
   ```bash
   fastboot flash boot boot.img
   fastboot flash vendor_boot vendor_boot.img
   fastboot flash dtbo dtbo.img
   fastboot flash vbmeta vbmeta.img
   fastboot flash vbmeta_system vbmeta_system.img
   ```
3. **Optional (only for `v1.0.2`+ AVB Lock-Ready builds) — Enroll Custom AVB Key**:
   ```bash
   fastboot flash avb_custom_key avb_custom_key.bin
   ```
4. **Reboot to Recovery**:
   ```bash
   fastboot reboot recovery
   ```
5. **Sideload Full OS**:
   * On device screen: Select **Apply update** -> **Apply from ADB**.
   * Run on host:
     ```bash
     adb sideload vaultos_otter-ota.zip
     ```
6. *(First install only)*: In recovery, select **Factory reset / Format data** $\rightarrow$ **Reboot system now**.
7. *(Optional — Locking Bootloader safely on `v1.0.2`+)*: Boot completely into VaultOs while still unlocked, open **CustomOtterControl** and run **Bootloader-Lock Dry-Run**. Only if it passes with zero blockers (`flags=0`, custom AVB key, air-gapped kernel), reboot to bootloader and run `fastboot flashing lock` (wipes `/data`).

---

## 🔨 Building from Source

To build VaultOs from source on Linux (Ubuntu 22.04+ ARM64/x86_64):

```bash
# 1. Initialize repo with LineageOS 23.2 base
repo init -u https://github.com/LineageOS/android.git -b lineage-23.2 --git-lfs

# 2. Add VaultOs local manifest
mkdir -p .repo/local_manifests
curl -fsSL https://raw.githubusercontent.com/Hatzen/android_vendor_vaultos/main/manifest/vaultos.xml \
  -o .repo/local_manifests/vaultos.xml

# 3. Synchronize repositories
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags

# 4. Compile VaultOs
source build/envsetup.sh
lunch vaultos_otter-bp4a-userdebug
m bacon -j$(nproc)
```

### ⚡ Built-in Root & KernelSU Toggle Flag

VaultOs includes native, out-of-the-box root powered by **KernelSU-Next** with zero post-flash steps, Magisk patching, or custom recovery workflows. Root is fully toggleable at compile time via the `WITH_KSU` flag:

* **Build with Root (Default)**:
  Compiles the `KernelSU-Next` driver into the kernel via non-GKI manual hooks (`CONFIG_KSU_MANUAL_HOOK=y`) and pre-installs the presigned KernelSU Manager app in `/product/app/KernelSU`:
  ```bash
  m bacon -j$(nproc)
  ```

* **Build without Root (Stock Non-Rooted Kernel)**:
  Pass `WITH_KSU=false` in the build environment to generate a 100% stock kernel without root hooks and omit the KernelSU management app:
  ```bash
  WITH_KSU=false m bacon -j$(nproc)
  ```

### 🔒 Hardware Air-Gap & USB Debug Toggle (`WITH_USB_DEBUG`)

Production VaultOs builds enforce a hardware-level air-gap in the kernel and DeviceTree by disabling the primary USB controller (`dwc3@a600000`), Wi-Fi (`icnss2`), and cellular baseband (`pil_modem`). For device bring-up, logcat capture, and debugging, you can compile developer `boot.img` / `vendor_boot.img` images with USB data enabled:

* **Air-Gapped Production Build (Default)**:
  ```bash
  m bacon -j$(nproc)
  ```

* **Developer USB-Debug Boot Image (`boot-usb-debug.img`)**:
  ```bash
  WITH_USB_DEBUG=true m bootimage vendorbootimage -j$(nproc)
  ```

### 🛡️ Verified Boot / Locked Bootloader Toggle (`WITH_AVB`)

Production builds enable Android Verified Boot 2.0 by default (`WITH_AVB=true`, `vbmeta flags=0`) and automatically pick up `vendor/vaultos/security/avb_custom_key.pem` when present:

* **Locked-Bootloader-Ready Production Build (Default — `WITH_AVB=true`)**:
  ```bash
  m bacon -j$(nproc)
  ```
* **Development Build Without AVB Enforcement (`vbmeta --flags 3`, CANNOT lock bootloader)**:
  ```bash
  WITH_AVB=false m bacon -j$(nproc)
  ```

---

## ⚙️ Developer Setup & `.env` Configuration

Local workstation paths, SSH hosts, and optional publishing tokens are kept strictly outside Git in a local `.env` file (ignored via `.gitignore`).

1. **Create your local `.env` from the template**:
   ```bash
   cp .env.example .env
   ```
2. **Adjust paths for your machine** in `.env`:
   * `CUSTOM_OTTER_DIR` — Path to local `CustomOtterControl` Android Studio project
   * `PARANNOYING_DIR` — Path to local `ParAnnoying` Android Studio project
   * `VENDOR_VAULTOS_DIR` — Path to `android_vendor_vaultos`
   * `BUILD_SSH_HOST`, `BUILD_SSH_USER`, `BUILD_LIMA_INSTANCE`, `BUILD_REMOTE_ROOT` — Optional remote AOSP builder settings
3. **Build and stage signed release APKs** into `android_vendor_vaultos/apps/`:
   * **Windows (PowerShell)**:
     ```powershell
     powershell -ExecutionPolicy Bypass -File .\tools\pipeline\update_prebuilt_apps.ps1
     ```
   * **Linux / macOS**:
     ```bash
     ./tools/pipeline/update_prebuilt_apps.sh
     ```
4. **Open full multi-repository IDE view**: Open `VaultOs.code-workspace` via **File -> Open Workspace from File...** to view all 9 VaultOs repositories in Git Source Control.

---

## 📜 License & Compliance

VaultOs open-source components are licensed under the [Apache License, Version 2.0](LICENSE).  
The Linux kernel is licensed under [GNU GPL v2](https://www.gnu.org/licenses/gpl-2.0.html).  
LineageOS components remain under their respective upstream licenses.

