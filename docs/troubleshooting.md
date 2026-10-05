# Troubleshooting and recovery

Locate the failure stage before changing anything. A menu that never becomes visible, a Linux kernel failure, and a frozen COSMIC session need different evidence.

## Black screen before the menu

1. Note whether this follows BIOS Save & Exit, a Windows restart, a Linux restart, or a cold start. Time the wait; the reference system sometimes took nearly a minute from power-on to desktop.
2. Leave firmware keys and boot files alone while isolating the display path. Power on the monitor before the computer.
3. Test one display connected by HDMI with DisplayPort disconnected. If Linux loads, reconnect DP afterward. This isolates the pre-OS display path; it does not identify a specific defective component.
4. On the **Acer XV275K P3** reference display, System → Quick Start Mode On, Auto Source Off, Input DP was followed by successful both-display restarts. Use the [correct model manual](sources.md); other monitors may use different names or power behavior.
5. Keep the 20-second menu timeout and inherit the firmware video mode. Avoid forcing a high rEFInd resolution while diagnosing.
6. After a successful boot inspect BootCurrent/BootOrder and any BootNext override. If OS-written priority does not persist, save the desired shim entry in the firmware's drive/BBS priority settings.

A case reset getting past one BIOS-exit black screen is not proof the problem is fixed. Repeat an ordinary restart. Do not repeatedly power-cycle a system that may be writing data; distinguish a pre-OS hang from a running OS with an invisible display.

## Menu appears, Linux selection fails

Keep the error wording or a photo locally. Check whether the menu loads the native systemd path, whether the kernel and loader signatures verify, whether the expected MOK is enrolled, and whether the EFI initramfs matches the intended `/boot` image. Do not add `nomodeset`, change kernels, replace loaders, and alter signing all at once.

If necessary disable **only Secure Boot** temporarily and boot the original Pop entry. Keep all factory keys. Inspect the previous boot journal, although a failure before Linux starts may have no journal at all.

## Secure Boot on, NVIDIA missing

Check the trusted certificate, lockdown state, `modinfo -F signer nvidia`, `dkms status`, and kernel journal. Re-sign/rebuild the appropriate module for the target kernel and regenerate its initramfs. A signed module in `/lib/modules` is insufficient when the ESP initramfs still holds an old copy.

Do not turn off signature enforcement to conceal an invalid or untrusted signature. With Secure Boot OFF, a key-not-found/taint message may occur while the driver still loads; interpret this in context.

## Secure Boot on, lockdown still shows [none]

The reference kernel did not automatically enable lockdown through this custom route. Verify the real early initramfs hook, its position before udev, and `od` plus dependencies. Rebuild and inspect the image copied to the ESP. Then reboot and check before making live changes. The separate initramfs remains unauthenticated even when the hook works; see architecture.md.

## System76 firmware service fails on an MSI board

On the reference MSI desktop, integrity lockdown denied raw I/O required by `system76-firmware-daemon`. Confirm hardware identity and journal evidence first. That System76 system-firmware service was disabled on this machine while general `fwupd` remained active:

```sh
sudo systemctl disable --now system76-firmware-daemon.service
sudo systemctl reset-failed system76-firmware-daemon.service
systemctl is-active fwupd
```

Do not apply this blindly to System76 hardware. Undo with `sudo systemctl enable --now system76-firmware-daemon.service` if appropriate. This does not disable System76 power management or NVIDIA.

## Recovery sequence

1. Disable Secure Boot temporarily if the custom chain cannot start. Do not clear or reset keys.
2. Select the saved original Pop firmware entry or a known-good recovery USB.
3. Identify and mount the actual Linux root and ESP using filesystem/partition IDs; follow the current [System76 bootloader repair documentation](https://support.system76.com/support/bootloader).
4. Restore reviewed backups or repair the failed stage. Preserve Windows' ESP and existing Windows boot manager.
5. If removing this customization, first disable the three signing hooks and any matching DKMS override, then restore the original menu/loader files and boot priority from your backup. Only remove the custom directory when a different boot route is working. Never remove the entire ESP or unrelated fallback files.
6. Re-test with Secure Boot off, then the signed route. Keep the signing key until all files depending on it are retired or re-signed under an enrolled replacement.

Do not follow internet advice to clear PK/KEK/db/dbx, delete SBAT policy, or sign arbitrary binaries as a generic recovery shortcut.
