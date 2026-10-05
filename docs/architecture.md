# Architecture and reference hardware

The reference desktop ran Pop!_OS 24.04 with COSMIC and Windows 11 on UEFI. The successful configuration was checked on October 5, 2026. Versions below are a record, not a recommendation to install those exact versions today.

| Component | Reference configuration |
|---|---|
| CPU | AMD Ryzen 9 9900X |
| Motherboard | MSI MAG B850 TOMAHAWK MAX WIFI |
| GPU | PNY NVIDIA RTX 5080, open driver 595.84 |
| Linux kernel | 7.1.5-76070105-generic |
| Native loader | systemd-boot 255.4, Pop distribution build |
| Menu | rEFInd 0.14.2 |
| First-stage loader | Ubuntu Microsoft-signed shim 15.8 |
| DisplayPort display | Acer XV275K P3 |
| HDMI display | Acer B277 |

The firmware starts `EFI/refind/shimx64.efi` on the Linux ESP. Shim validates `EFI/refind/grubx64.efi`, which is a locally signed rEFInd binary using the filename shim expects. It is not GRUB despite that filename.

rEFInd offers Windows Boot Manager on the Windows ESP and `EFI/systemd/systemd-bootx64.efi` on the Linux ESP. The latter uses `loader/entries/Pop_OS-current.conf`; kernelstub maintains the Pop kernel and initramfs. rEFInd's default is Windows with a 20-second timer; systemd-boot's inner menu uses Pop's current entry with a zero-second timeout.

The local certificate signs rEFInd, systemd-boot, Pop kernels, and relevant DKMS modules. Its private key stays in a root-only directory. MOK enrollment adds local trust through shim without replacing the motherboard's factory trust databases. Native distribution module signatures remain intact.

The standard fallback menu and original Pop firmware entry remain available for recovery with Secure Boot disabled. Do not assume a direct native loader entry trusts a MOK certificate: that trust is supplied through shim.

## Why two boot managers?

rEFInd supplies the graphical menu; systemd-boot preserves Pop's normal loader entry and kernelstub update behavior. The tested systemd build verifies the next kernel through shim. This compatibility must be checked again on another build. A visually working menu is not proof that later executable verification is enforced.

## Security boundary

The installed chain validates signed EFI executables, and early integrity lockdown restricts unsigned kernel modules and raw hardware access. Tests rejected an altered kernel and an unsigned test module while accepting a locally signed probe.

The initramfs is a separate file and is **not authenticated** by this chain. An attacker able to modify it could remove the protection hook or change early userspace. Secure Boot ON plus an integrity status is therefore not equivalent to authenticating every part of startup. Boot options and the whole ESP also need consideration in a stronger threat model. This guide makes no claim of resistance to an attacker with write access to the ESP or root signing key.

A signed UKI can bring the initramfs and embedded command line into a signed artifact. Moving Pop/kernelstub to that model needs its own update, space, trust, recovery, and physical-boot testing; it is outside the tested implementation here.

## Important implementation lessons

- Firmware may ignore or rewrite an OS-written BootOrder. Saving the desired entry in the MSI BIOS BBS priority menu made it persist on this machine.
- A slow monitor can conceal a correctly running menu. Do not immediately replace the bootloader when the failure happens before any menu is visible.
- The real initramfs initially lacked `od`. A VM test with a different BusyBox build had passed. The separate tools hook now includes `/usr/bin/od` and its dependencies.
- Adding a dependency to the early script unexpectedly put it after udev in generated ORDER. The final script mounts efivarfs itself if needed and its position before udev is checked in the built image.
- One case reset was required after enabling Secure Boot in BIOS. Later normal restarts and a Windows round trip worked. No exact explanation for that one failure was proven.
