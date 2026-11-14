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
| **SHIFTphone 8** | `otter` | Qualcomm Yupik / QCM6490 | **16 (BP4A / LineageOS 23.2)** | **Stable (v1.0.0)** |

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

## ⚡ Quick Start: Flashing VaultOs

### Prerequisites
* Unlocked bootloader on your SHIFTphone 8 (`fastboot getvar unlocked` -> `yes`).
* Android platform-tools (`adb` and `fastboot`).
* Official release files from the [Releases](https://github.com/Hatzen/VaultOs/releases) page:
  * `boot.img`
  * `vendor_boot.img`
  * `dtbo.img`
  * `vaultos_otter-ota.zip`

### Flashing Steps
1. **Reboot to Fastboot**:
   ```bash
   adb reboot bootloader
   ```
2. **Flash Core Partitions**:
   ```bash
   fastboot flash boot boot.img
   fastboot flash vendor_boot vendor_boot.img
   fastboot flash dtbo dtbo.img
   ```
3. **Reboot to Recovery**:
   ```bash
   fastboot reboot recovery
   ```
4. **Sideload Full OS**:
   * On device screen: Select **Apply update** -> **Apply from ADB**.
   * Run on host:
     ```bash
     adb sideload vaultos_otter-ota.zip
     ```
5. *(First install only)*: In recovery, select **Factory reset / Format data** $\rightarrow$ **Reboot system now**.

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

---

## 📜 License & Compliance

VaultOs open-source components are licensed under the [Apache License, Version 2.0](LICENSE).  
The Linux kernel is licensed under [GNU GPL v2](https://www.gnu.org/licenses/gpl-2.0.html).  
LineageOS components remain under their respective upstream licenses.

