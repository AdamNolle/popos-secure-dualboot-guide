# Maintenance

The reference helper uses a filesystem lock, validates the mounted Linux ESP's PARTUUID/FAT/read-write state, and avoids recursion when an initramfs rebuild invokes its own post-update hook. The rendered helper is privileged code: inspect it before installation.

## Update order

1. Sign changed DKMS modules with the local MOK key.
2. Run depmod for affected kernel versions.
3. Sign root kernel images.
4. Rebuild existing initramfs images whose modules changed, using `LOCAL_SECURE_BOOT_REBUILD=1` to avoid recursion.
5. Sign the EFI kernel/native loader copies and regenerate the menu.
6. Verify final files and sync.

The DKMS configuration sets `mok_signing_key` and `mok_certificate` for future builds. Kernel post-install, initramfs post-update, and apt post-invoke hooks run the helper. The MOK key remains root-only and never enters Git.

## Limits of the template

- Assumes Pop/kernelstub, `/boot/efi`, a `Pop_OS-current.conf` entry, and this repository's theme paths.
- Handles `.ko`, `.ko.zst`, `.ko.xz`, and `.ko.gz` directly under each kernel's `updates/dkms`; other layouts need adaptation.
- It uses module signer common-name text to decide whether re-signing is needed. This is a maintenance shortcut, **not verification of certificate identity**. During key rotation or if multiple certificates share a CN, explicitly rebuild/re-sign modules and verify the enrolled certificate and module key identity. Use unique CNs.
- It does not install or automatically refresh shim, MOK Manager, rEFInd, or recovery-kernel copies. Monitor distribution/upstream security updates and refresh those copies deliberately, then verify signatures and real boots. A copy of a revoked or obsolete shim can stop working after firmware/dbx updates.
- DKMS headers must be present. A skipped version without headers is not proof that all its modules are ready.
- Signing a file only establishes provenance under that key, not that the code is safe. Use trusted upstream/distribution builds.
- The helper regenerates `refind.conf`. Put enduring menu changes in the template/local installed generator too, or they will be overwritten.
- This is not an authenticated-initramfs or UKI maintenance system.

## After kernel, NVIDIA, or bootloader updates

Do not reboot past a failed signing hook. Read its error and check ESP space/mount status, key access, headers, module signatures, current entry, and initramfs contents. Verify the intended next-boot files, not just the running kernel. Test a real Secure Boot boot and `nvidia-smi` after significant updates.

Package management is serialized. Use `apt-get -o DPkg::Lock::Timeout=600 ...` to wait; do not remove locks, interrupt a running package manager, or start two simultaneous installs.

## Key renewal and backup

Back up the root-only signing state privately, plus ESP contents and boot configuration. Track certificate expiry. Before replacing a key, enroll the replacement, rebuild/sign all intended artifacts under it, and test the entire chain. Keep the old trusted key available for recovery until migration is complete. Never store key material, MOK passwords, BitLocker recovery keys, or raw NVRAM dumps in issues or commits.

## Repository validation

`python3 -m unittest discover -s tests -v` runs offline checks and mocked update sequencing. It does not read private keys, change EFI variables, rebuild the host kernel, or reboot. Physical verification is described separately.
