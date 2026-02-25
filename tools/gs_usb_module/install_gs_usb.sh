#!/bin/bash
set -euo pipefail

MOD_NAME="gs_usb"
KERNEL_REL="$(uname -r)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_PATH="${SCRIPT_DIR}/gs_usb.ko"
TARGET_DIR="/lib/modules/${KERNEL_REL}/updates/drivers/net/can/usb"
TARGET_PATH="${TARGET_DIR}/${MOD_NAME}.ko"

if [ ! -f "${MODULE_PATH}" ]; then
    echo "Error: ${MODULE_PATH} not found."
    exit 1
fi

echo "Installing ${MOD_NAME}.ko for kernel ${KERNEL_REL} ..."
sudo mkdir -p "${TARGET_DIR}"
sudo cp "${MODULE_PATH}" "${TARGET_PATH}"
sudo depmod -a "${KERNEL_REL}"

echo "Reloading module ..."
sudo modprobe -r "${MOD_NAME}" 2>/dev/null || true
sudo modprobe "${MOD_NAME}"

echo
echo "Done. Current CAN interfaces:"
ip -br link show type can || true
