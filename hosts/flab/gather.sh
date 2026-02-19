#!/bin/bash

# ASUS Server Hardware & IPMI Inventory Script
# Saves output to dated files in ./hardware_inventory/YYYY-MM-DD/

set -e  # Exit on any error

# Create timestamp and directory
DATE=$(date +%Y%m%d-%H-%M)
DIR="$(hostname)/$DATE"
mkdir -p "$DIR"

echo "Collecting hardware inventory to $DIR/..." | tee "$DIR/summary.txt"

# Load IPMI modules first
gmodprobe ipmi_devintf ipmi_si ipmi_msghandler 2>/dev/null || true

# Helper function to run command and save output
run_cmd() {
    local cmd="$1"
    local file="$2"
    echo "Running: $cmd" | tee -a "$DIR/summary.txt"
    eval "$cmd" > "$DIR/$file" 2>&1 || echo "Command failed: $cmd" >> "$DIR/$file"
}

## MOTHERBOARD DETAILS
echo -e "\n=== MOTHERBOARD INFO ===" | tee -a "$DIR/summary.txt"
run_cmd "gdmidecode -t baseboard"           "motherboard.txt"
run_cmd "gdmidecode -t 2"                   "motherboard_type2.txt"
run_cmd "gdmidecode -s baseboard-serial-number" "motherboard_serial.txt"

## GENERAL HARDWARE
echo -e "\n=== GENERAL HARDWARE ===" | tee -a "$DIR/summary.txt"
run_cmd "glshw -short"                      "lshw_short.txt"
run_cmd "glshw -class system,motherboard"   "lshw_motherboard.txt"
run_cmd "lspci -v | head -50"                   "pci_devices.txt"
run_cmd "lspci -nnk"                            "pci_detailed.txt"
run_cmd "gdmidecode -t processor"           "cpu_info.txt"
run_cmd "gdmidecode -t memory"              "memory_info.txt"
run_cmd "lsusb"                                 "usb_devices.txt"

## IPMI/BMC DETAILS
echo -e "\n=== IPMI/BMC INFO ===" | tee -a "$DIR/summary.txt"
run_cmd "ipmitool -I open mc info"              "ipmi_mc_info.txt"
run_cmd "ipmitool fru"                          "ipmi_fru.txt"
run_cmd "ipmitool lan print"                    "ipmi_lan.txt"
run_cmd "ipmitool sensor"                       "ipmi_sensors.txt"
run_cmd "ipmitool user list 1"                  "ipmi_users.txt"
run_cmd "ipmitool sel list"                     "ipmi_sel_logs.txt"

## SYSTEM INFO
echo -e "\n=== SYSTEM INFO ===" | tee -a "$DIR/summary.txt"
run_cmd "uname -a"                              "kernel_version.txt"
run_cmd "lscpu"                                 "cpu_summary.txt"
run_cmd "free -h"                               "memory_usage.txt"
run_cmd "df -h"                                 "disk_usage.txt"

# Create archive
echo -e "\n=== Creating archive ===" | tee -a "$DIR/summary.txt"
tar -czf "${DIR}.tgz" -C "$(dirname $DIR)" "$(basename $DIR)" && rm -rf "$DIR"
echo "Archive created: ${DIR}.tgz"

echo "Inventory collection complete!"
echo "Files saved in: $DIR/"
echo "Compressed archive: ${DIR}.tgz"
