#!/bin/sh
# Read-only; never elevates, changes settings, installs packages, or saves a report.
# Output can contain machine identifiers. Review before sharing.
set -u
run() {
    printf '\n$'
    for argument do printf ' %s' "$argument"; done
    printf '\n'
    if command -v "$1" >/dev/null 2>&1; then
        "$@" || printf '(Unavailable, permission needed, or nonzero diagnostic result.)\n'
    else
        printf '(Command is not installed.)\n'
    fi
}
run uname -r
run cat /etc/os-release
run mokutil --sb-state
run cat /sys/kernel/security/lockdown
run efibootmgr
run findmnt /boot/efi
run nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
run modinfo -F signer nvidia
run dkms status
run systemctl --failed --no-legend
printf '\nThis is evidence to review, not a pass/fail certification.\n'
