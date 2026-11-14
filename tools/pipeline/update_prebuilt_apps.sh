#!/usr/bin/env bash
#
# VaultOs Prebuilt Apps Release Pipeline (Linux / macOS)
# Compiles CustomOtterControl and ParAnnoying as Android release APKs
# and stages them into android_vendor_vaultos/apps/.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

CUSTOM_OTTER_DIR="${CUSTOM_OTTER_DIR:-${WORKSPACE_ROOT}/CustomOtterControl}"
PARANNOYING_DIR="${PARANNOYING_DIR:-${HOME}/StudioProjects/ParAnnoying}"
VENDOR_VAULTOS_DIR="${VENDOR_VAULTOS_DIR:-${WORKSPACE_ROOT}/android_vendor_vaultos}"

build_and_stage() {
    local name="$1"
    local project_dir="$2"
    local gradle_task="$3"
    local built_rel="$4"
    local dest_path="$5"

    if [[ ! -d "${project_dir}" ]]; then
        echo "ERROR: [${name}] Directory not found: ${project_dir}" >&2
        exit 1
    fi

    echo "========================================"
    echo " Building ${name} (${gradle_task})"
    echo "========================================"

    (cd "${project_dir}" && ./gradlew "${gradle_task}" --no-daemon)

    local built_apk="${project_dir}/${built_rel}"
    if [[ ! -f "${built_apk}" ]]; then
        echo "ERROR: [${name}] Expected APK not found: ${built_apk}" >&2
        exit 1
    fi

    mkdir -p "$(dirname "${dest_path}")"
    cp -f "${built_apk}" "${dest_path}"

    local sha
    sha="$(sha256sum "${dest_path}" | awk '{print $1}')"
    local size_bytes
    size_bytes="$(wc -c < "${dest_path}")"
    echo "[${name}] Staged -> ${dest_path} (${size_bytes} bytes, sha256: ${sha})"
}

build_and_stage \
    "CustomOtterControl" \
    "${CUSTOM_OTTER_DIR}" \
    ":app:assembleRelease" \
    "app/build/outputs/apk/release/app-release.apk" \
    "${VENDOR_VAULTOS_DIR}/apps/CustomOtterControl/app-release.apk"

rm -f "${VENDOR_VAULTOS_DIR}/apps/CustomOtterControl/app-debug.apk" \
      "${VENDOR_VAULTOS_DIR}/apps/CustomOtterControl/app-release-unsigned.apk"

build_and_stage \
    "ParAnnoying" \
    "${PARANNOYING_DIR}" \
    ":app:assembleProdRelease" \
    "app/build/outputs/apk/prod/release/app-prod-release.apk" \
    "${VENDOR_VAULTOS_DIR}/apps/Parannoying/app-prod-release.apk"

echo "Pipeline complete."
