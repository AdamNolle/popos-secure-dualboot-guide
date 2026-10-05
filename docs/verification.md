# Verification and test record

Run checks after a real reboot, before applying any live workaround. A live `echo integrity` can make the current state look correct while hiding a broken early hook.

```sh
mokutil --sb-state
cat /sys/kernel/security/lockdown
sudo efibootmgr -v
nvidia-smi
modinfo -F signer nvidia
systemctl --failed
journalctl -b -k --no-pager | rg 'Secure boot|Lockdown|Xid|verification|Loaded X.509'
```

Expected for the secure route: Secure Boot enabled; `none [integrity] confidentiality` (or stricter confinement); intended shim BootCurrent; enrolled certificate imported; NVIDIA driver functioning; no unexplained failures. A module's signer text alone is not cryptographic verification. The kernel must trust its signing key and load it with enforcement active.

Windows: the human must select Windows, reach the desktop, choose Restart, see the menu, and return to Linux. If possible, run elevated PowerShell `Confirm-SecureBootUEFI` or check System Information → Secure Boot State in Windows too. Record a user-confirmed Windows startup separately from a directly queried Windows Secure Boot state.

## Inspect the actual initramfs

Extract into a new empty private directory:

```sh
mkdir -p local
unmkinitramfs /boot/initrd.img-$(uname -r) local/initrd-current
cat local/initrd-current/main/scripts/init-top/ORDER
ls -l local/initrd-current/main/usr/bin/od
cat local/initrd-current/main/scripts/init-top/00-local-secure-boot-lockdown
```

On this distribution the main archive is under `main/`; inspect the extraction layout rather than assuming this on other versions. The protection script must precede `/scripts/init-top/udev`. `od` must be executable with its loader and libraries included. For a trusted locally built image, `sudo chroot local/initrd-current/main /usr/bin/od --version` checks those dependencies. Do not chroot into untrusted downloaded images as root.

Read `Pop_OS-current.conf` to obtain the EFI kernel/initramfs paths. Compare them with the intended `/boot` files using `cmp` or hashes. Do not guess the Pop directory UUID. Check signatures with `sbverify --cert YOUR_PUBLIC_CERT FILE` and module signing metadata. After updates, the target kernel may differ from `uname -r`, which describes the running kernel.

## Reference physical results

| Check | Result and evidence |
|---|---|
| Linux through shim → rEFInd → systemd-boot, Secure Boot off | Passed physical boot |
| Correct firmware priority persists | BootCurrent and BootOrder checked after restarts |
| HDMI-only startup isolation | User-confirmed success; DP reconnected after Linux loaded |
| Both monitors after OSD changes | User-confirmed menu/startup success, including Windows restart |
| First BIOS exit after enabling Secure Boot | Black before menu; case reset required; cause unproven |
| Linux with Secure Boot on | Directly verified enabled state and MOK certificate import |
| Automatic early integrity lockdown | Directly verified on subsequent fresh boots without live modification |
| NVIDIA RTX 5080 with Secure Boot on | `nvidia-smi` successful with driver 595.84 |
| Windows boot and return to Linux with Secure Boot left on | User-confirmed Windows leg; Linux Secure Boot rechecked afterward |
| Failed services after cleanup | None in final checked Linux session |
| Temporary rEFInd logging | Removed; menu changes limited to logging line; Windows default/20 seconds retained |

Reference work completed October 5, 2026. The historical test results apply to the original machine, not automatically to newly rendered templates on a different machine.

## Isolated tests performed during original work

A QEMU/OVMF VM used copies of the motherboard's public trust/revocation databases and the enrolled public MOK certificate. It exercised signed shim → signed rEFInd → signed systemd-boot → signed Pop kernel. An unsigned probe module was rejected, a signed probe loaded, and a deliberately altered kernel was refused with Access denied. NVIDIA's signature was accepted; driver initialization reported no GPU in the VM, as expected.

These test fixtures, EFI images, firmware variable dumps, and machine logs are deliberately not distributed here. A VM cannot certify physical GPU/display startup. The original VM also missed the real initramfs's missing `od`, so an isolated success must never replace artifact inspection and a physical test.

## Exit checklist

- Test normal warm restarts and a cold start when convenient; record results honestly.
- Check that menu countdown/default and BIOS label match the user's preference.
- Keep the original recovery entry and a recovery USB.
- Disable temporary `log_level 1`; if using this helper, remove `/var/lib/local-secure-boot/boot-debug` and regenerate the menu after backing it up.
- Treat later freezes as new evidence. No finite test proves indefinite stability.
