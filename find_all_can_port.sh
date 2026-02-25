#!/bin/bash

get_can_ifaces() {
    ip -br link show type can | awk '{print $1}'
}

get_iface_info() {
    local iface="$1"
    ethtool -i "$iface" 2>/dev/null
}

# Check if ethtool is installed
if ! dpkg -l | grep -q "ethtool"; then
    echo "Error: ethtool not detected in the system."
    echo "Please install ethtool using the following command:"
    echo "sudo apt update && sudo apt install ethtool"
    exit 1
fi

# Check if can-utils is installed
if ! dpkg -l | grep -q "can-utils"; then
    echo "Error: can-utils not detected in the system."
    echo "Please install can-utils using the following command:"
    echo "sudo apt update && sudo apt install can-utils"
    exit 1
fi

echo "Both ethtool and can-utils are installed."

CAN_IFACES=$(get_can_ifaces)
if [ -z "$CAN_IFACES" ]; then
    echo "No CAN interface detected yet. Trying to load gs_usb driver..."
    modprobe gs_usb 2>/dev/null || sudo -n modprobe gs_usb 2>/dev/null || true
    sleep 1
    CAN_IFACES=$(get_can_ifaces)
fi

if [ -z "$CAN_IFACES" ]; then
    echo "No CAN interface detected."
    echo "Hint: the README value like 3-1.4:1.0 is only an example."
    echo "On your PC, bus-info can also be 1-*, 2-*, 4-* ... (not always 3-*)."
    echo
    echo "Please check with:"
    echo "  ip -br link show type can"
    echo "  lsmod | grep gs_usb"
    if command -v lsusb >/dev/null 2>&1; then
        echo "  lsusb -t"
    fi
    exit 1
fi

USB_CAN_FOUND=0

for iface in $CAN_IFACES; do
    INFO=$(get_iface_info "$iface")
    if [ -z "$INFO" ]; then
        echo "Error: Unable to get ethtool info for interface $iface."
        continue
    fi
    DRIVER=$(printf "%s\n" "$INFO" | awk '/driver/ {print $2}')
    BUS_INFO=$(printf "%s\n" "$INFO" | awk '/bus-info/ {print $2}')

    if [ -z "$BUS_INFO" ]; then
        echo "Error: Unable to get bus-info for interface $iface."
        continue
    fi

    if [ "$DRIVER" = "mttcan" ] || [[ "$BUS_INFO" == *.mttcan ]]; then
        echo "Interface $iface is onboard CAN (driver $DRIVER, bus-info $BUS_INFO), not USB CAN."
        continue
    fi

    USB_CAN_FOUND=1
    echo "Interface $iface is connected to USB port $BUS_INFO (driver $DRIVER)"
done

if [ "$USB_CAN_FOUND" -eq 0 ]; then
    echo
    echo "No USB CAN adapter detected."
    if command -v lsusb >/dev/null 2>&1 && lsusb | grep -qiE '1d50:606f|candlelight USB to CAN adapter'; then
        echo "A candleLight USB-CAN device is present on USB, but no CAN interface was created."
        if lsmod | grep -q '^gs_usb'; then
            echo "gs_usb driver is loaded. Check kernel logs: dmesg -w"
        else
            if modinfo gs_usb >/dev/null 2>&1; then
                echo "gs_usb driver exists but is not loaded. Run: sudo modprobe gs_usb"
            else
                echo "gs_usb driver is missing for kernel $(uname -r). Build/install it, or use onboard CAN (mttcan)."
            fi
        fi
    fi
    echo "If you expect the Piper USB-CAN module, check with:"
    echo "  lsusb"
    echo "  dmesg -w   # then unplug/replug the USB-CAN module"
fi
