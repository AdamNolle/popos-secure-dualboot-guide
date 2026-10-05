# Setup guide

Read [architecture](architecture.md) and [recovery](troubleshooting.md) first. This is an advanced, custom arrangement for an existing UEFI Pop!_OS and Windows installation. It does not partition disks, install either OS, or replace official installation instructions. System76's installation guidance starts with Secure Boot disabled; this guide adds a separately tested custom chain afterward.

Keep a bootable Pop recovery USB and backups. If Windows device encryption/BitLocker is enabled, have the recovery key available before firmware/boot changes. Do not publish that key. Commands below are examples to review and adapt, not a paste-all script.

## 1. Inventory with Secure Boot disabled

Run `sh scripts/check-system.sh` locally. Also inspect:

```sh
lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINTS,PARTUUID,UUID
findmnt /boot/efi
sudo efibootmgr -v
sudo cat /boot/efi/loader/loader.conf
sudo cat /boot/efi/loader/entries/Pop_OS-current.conf
```

Identify the Linux ESP and the Windows ESP from their files and filesystem/partition types. Do not infer identity from `nvme0n1` numbering: it can change. Use PARTUUIDs for the template. Keep the existing root UUID and kernelstub options; no root UUID is needed by the menu template.

Back up both ESPs and firmware entry listings to private storage. An `efibootmgr` listing documents entries but is not a backup of all firmware variables or keys. Record how to select the original Pop and Windows entries in firmware. Check free space on the Linux ESP before copying or rebuilding images.

## 2. Install tools from trusted distribution sources

Check candidates for your release first:

```sh
apt-cache policy shim-signed mokutil sbsigntool refind
sudo apt-get -o DPkg::Lock::Timeout=600 install shim-signed mokutil sbsigntool openssl
```

Installing bootloader packages can run post-install scripts. Re-check boot entries afterward. Obtain rEFInd from its distribution package or upstream release and retain its license/provenance. This repository includes no EFI binaries. Locate the installed files using `dpkg -L shim-signed` and package listings; paths and filenames vary.

Use the current Microsoft-signed shim and matching MOK Manager (`mmx64.efi`). Do not substitute an unsigned shim. Check package authenticity and the image signature list with `sbverify --list FILE`. Signature-list output alone does not establish that your firmware accepts the signer or that its revocation policy permits this build.

## 3. Generate your own local key

Use a unique certificate name, for example `My Desktop Secure Boot`. Do not reuse this project's reference identity or anyone else's private key.

```sh
sudo install -d -m 700 /var/lib/local-secure-boot
sudo sh -c 'umask 077; test ! -e /var/lib/local-secure-boot/MOK.key && test ! -e /var/lib/local-secure-boot/MOK.pem && openssl req -new -x509 -newkey rsa:3072 -nodes \
  -keyout /var/lib/local-secure-boot/MOK.key \
  -out /var/lib/local-secure-boot/MOK.pem -days 3650 \
  -subj "/CN=My Desktop Secure Boot/" \
  -addext "basicConstraints=critical,CA:FALSE" \
  -addext "keyUsage=critical,digitalSignature" \
  -addext "extendedKeyUsage=codeSigning"'
sudo openssl x509 -in /var/lib/local-secure-boot/MOK.pem -outform DER \
  -out /var/lib/local-secure-boot/MOK.der
sudo chmod 600 /var/lib/local-secure-boot/MOK.key
```

**Only generate into a new state directory.** These commands must not overwrite an existing installation's signing key. Back up the private key securely offline; automatic signing needs root access to it. Track certificate expiry and plan renewal/enrollment before expiry.

Request MOK enrollment:

```sh
sudo mokutil --import /var/lib/local-secure-boot/MOK.der
```

Choose your own temporary enrollment password. Complete the blue MOK Manager screen during a boot through shim, inspect the certificate identity, and reboot as requested. The screen is not guaranteed to appear when booting a different EFI entry. Verify enrollment afterward using `mokutil --test-key` and certificate listings. Do not record enrollment passwords in the repository.

## 4. Stage the chain and theme

Work in a private staging directory, with Secure Boot still off. Prepare:

| Linux ESP location | Content |
|---|---|
| `EFI/refind/shimx64.efi` | Unmodified Microsoft-signed shim |
| `EFI/refind/mmx64.efi` | Matching MOK Manager |
| `EFI/refind/grubx64.efi` | rEFInd signed by your local key |
| `EFI/refind/refind_x64.efi` | Same signed rEFInd, retained conventional filename |
| `EFI/refind-standard/refind_x64.efi` | Optional recovery menu binary |
| `EFI/refind/themes/cosmic-dark/` | Contents of this repository's theme directory |
| `EFI/systemd/systemd-bootx64.efi` | Existing native loader signed by your local key |

For each executable needing a local signature, write a separate output and verify it before replacing its target:

```sh
sudo sbsign --key /var/lib/local-secure-boot/MOK.key \
  --cert /var/lib/local-secure-boot/MOK.pem --output STAGED_SIGNED.efi SOURCE.efi
sudo sbverify --cert /var/lib/local-secure-boot/MOK.pem STAGED_SIGNED.efi
```

Replace the uppercase paths with actual reviewed files. Do not re-sign Microsoft's Windows boot manager or shim with your local key. If you alter a previously signed binary (such as the BIOS-label change), remove the now-invalid old signature from the **staged copy** before re-signing. Preserve the original separately. Never deploy a file whose signature verification fails.

Optional gear title: see [theme instructions](theme.md). Signing may append a signature; stale signatures on modified images caused a verification failure during the original work.

## 5. Render the maintenance helper

This writes only a new local file, and rejects placeholder/invalid partition identifiers:

```sh
python3 scripts/render-config.py \
  --linux-esp-partuuid YOUR_LINUX_ESP_PARTUUID \
  --windows-esp-partuuid YOUR_WINDOWS_ESP_PARTUUID \
  --signer-cn 'My Desktop Secure Boot' \
  --output local/local-secure-boot-sign
```

Replace the two UUID arguments first. Review the output. The signer expects the paths in step 4, a valid existing Pop current entry, a writable FAT Linux ESP mounted at `/boot/efi`, and the root-only MOK files. It also expects kernel headers for module signing. The optional standard menu is maintained only if that directory exists.

Install the reviewed helper and early-boot files:

```sh
sudo install -m 755 local/local-secure-boot-sign /usr/local/sbin/local-secure-boot-sign
sudo install -m 755 templates/00-local-secure-boot-lockdown /etc/initramfs-tools/scripts/init-top/00-local-secure-boot-lockdown
sudo install -m 755 templates/local-secure-boot-tools /etc/initramfs-tools/hooks/local-secure-boot-tools
sudo install -d /etc/dkms/framework.conf.d
sudo install -m 644 templates/dkms-signing.conf /etc/dkms/framework.conf.d/local-secure-boot.conf
sudo /usr/local/sbin/local-secure-boot-sign
sudo update-initramfs -u -k all
sudo /usr/local/sbin/local-secure-boot-sign
```

Review existing files before overwriting them and back them up first. The helper signs supported DKMS files under `updates/dkms`, signs installed root and ESP kernels and the native/fallback loader, and writes both menus. It does not install/sign shim or the staged rEFInd files for you. See [maintenance limitations](maintenance.md).

Inspect the built initramfs as described in [verification](verification.md). The actual image must contain `od`, its runtime dependencies, and the protection script **before udev**. Verify the ESP's kernel and initramfs match the intended `/boot` files. Configure the native loader's existing `loader.conf` to use `default Pop_OS-current.conf` and `timeout 0`, preserving other relevant settings. Inspect persistent EFI default/one-shot overrides with `bootctl status`; do not blindly erase EFI variables.

## 6. Install update hooks after the initial run succeeds

```sh
sudo install -m 755 templates/local-secure-boot-hook /etc/kernel/postinst.d/zzzz-local-secure-boot
sudo install -m 755 templates/local-secure-boot-hook /etc/initramfs/post-update.d/zzzz-local-secure-boot
sudo install -m 644 templates/apt-signing.conf /etc/apt/apt.conf.d/99-local-secure-boot
```

These execute privileged signing code during updates. They are appropriate only after verifying the generated helper and initial chain. A hook failure must be investigated before rebooting; see [maintenance](maintenance.md).

## 7. Add and test the firmware entry

Use the actual Linux ESP parent disk and partition number found in step 1:

```sh
sudo efibootmgr --create --disk /dev/YOUR_DISK --part YOUR_ESP_NUMBER \
  --label 'Dark Dual Boot (Secure Boot)' --loader '\EFI\refind\shimx64.efi'
```

This placeholder command is intentionally not runnable unchanged. Creating an entry can change boot priority. Record the resulting number; never assume it is `0004`. Retain the original Pop and Windows entries. Use firmware setup to make the new shim entry first, and confirm BootCurrent and BootOrder after a real restart. On the reference MSI board the persistent setting was under Settings → Boot → UEFI Hard Disk Drive BBS Priorities; menu names vary.

First test both OS choices with Secure Boot off. Address invisible menus using the monitor procedure before proceeding. Then enable Secure Boot while retaining existing keys, keep the shim entry first, select Pop, and complete [all physical verification steps](verification.md). Do not clear factory keys or disable SBAT checks to get past a failure.
