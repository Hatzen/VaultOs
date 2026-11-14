#!/usr/bin/env bash
#
# VaultOs Prebuilt Apps Release Pipeline (Linux / macOS)
# Compiles CustomOtterControl and ParAnnoying as Android release APKs
# and stages them into android_vendor_vaultos/apps/.
# Reads optional overrides from <repo_root>/.env or environment variables.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load .env from repo root if present (without clobbering already-exported vars)
if [[ -f "${REPO_ROOT}/.env" ]]; then
    while IFS='=' read -r raw_key raw_val || [[ -n "${raw_key:-}" ]]; do
        line="${raw_key%%#*}"
        [[ -z "${line// }" ]] && continue
        key="$(echo "${raw_key}" | xargs)"
        val="$(echo "${raw_val:-}" | tr -d '\r' | sed -E 's/^["'\'']|["'\'']$//g')"
        if [[ -n "${key}" && -z "${!key:-}" ]]; then
            export "${key}=${val}"
        fi
    done < "${REPO_ROOT}/.env"
fi

resolve_path() {
    local val="$1"
    if [[ "${val}" = /* ]]; then
        echo "${val}"
    else
        echo "${REPO_ROOT}/${val}"
    fi
}

CUSTOM_OTTER_DIR="$(resolve_path "${CUSTOM_OTTER_DIR:-../../AndroidStudioProjects/CustomOtterControl}")"
PARANNOYING_DIR="$(resolve_path "${PARANNOYING_DIR:-../../StudioProjects/ParAnnoying}")"
VENDOR_VAULTOS_DIR="$(resolve_path "${VENDOR_VAULTOS_DIR:-../android_vendor_vaultos}")"

build_and_stage() {
    local name="$1"
    local project_dir="$2"
    local gradle_task="$3"
    local built_rel="$4"
    local dest_path="$5"

    if [[ ! -d "${project_dir}" ]]; then
        echo "ERROR: [${name}] Directory not found: ${project_dir} (copy .env.example to .env and configure paths)" >&2
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
