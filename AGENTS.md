# Instructions for AI assistants

## Objective and starting point

Help a human understand, reproduce, maintain, or diagnose this custom setup. Preserve working boot paths. Read README.md, docs/architecture.md, docs/setup.md, and docs/troubleshooting.md before proposing system changes. The repository itself is a guide; editing it does not authorize changes to the current host's boot configuration.

User instructions govern the requested scope. Inspect the current state; do not assume the reader is using the reference hardware, partition numbering, software versions, or account.

## Establish evidence first

1. Identify OS, kernel, hardware, GPU, UEFI/legacy mode, Secure Boot state, mounted ESP, partition UUIDs, BootCurrent, BootOrder, and any BootNext/one-shot override.
2. Read the actual current loader entries and existing maintenance hooks. Check both root initramfs and the copy on the ESP.
3. Separate a black screen BEFORE the menu from a failure AFTER Linux selection and a desktop compositor freeze. Ask where it fails if unknown.
4. Use read-only diagnostics first. Explain the concrete reason for any administrator prompt. Batch related changes with a backup and verification, without creating a general privileged helper.
5. Keep local logs and identifiers out of commits. Never read private signing key contents into chat or logs.

## Constraints

- Never copy reference-machine partition IDs, PCI IDs, boot numbers, passwords, or certificate identities onto another machine.
- Never clear firmware PK/KEK/db/dbx, delete SBAT policy, disable signature verification, or blindly sign Windows' boot manager to make a failing boot pass.
- Do not disable kernel protections to hide an NVIDIA signing failure.
- Do not add unconditional `lockdown=integrity` to a Secure Boot OFF recovery route. On the reference setup, MOK trust was unavailable in that mode and the driver failed.
- Do not treat `mokutil --sb-state` alone as proof that module restrictions are active. Check `/sys/kernel/security/lockdown`, the trusted certificate, and NVIDIA.
- Do not assume a VM passed the same initramfs as the host. The reference VM had `od`; the real image did not. Inspect the built artifact and its script ORDER.
- Do not delete apt/dpkg lock files or run concurrent package mutations. Wait for their owner and use a lock timeout.
- Do not install a Windows Logitech driver on Linux, promise Looking Glass works with an offline dual-boot Windows installation, or flash GPU/board firmware as a speculative fix.
- Keep existing Microsoft trust, native Pop boot entry, and a bootable recovery path. Avoid forced rEFInd display modes during display diagnosis.
- Do not broaden sudo/PolicyKit permissions for convenience. Never use repository examples as an excuse for blanket NOPASSWD.
- Reboots, physical firmware settings, MOK enrollment, and monitor OSD interaction require the human. Do not initiate a reboot unless explicitly authorized.

## Working sequence

Inventory → backup → confirm recovery → prepare reviewed files → validate placeholders and signatures → install only the approved changes → inspect actual initramfs/ESP copies → test Secure Boot OFF → human enables Secure Boot → verify physical Linux and NVIDIA → human tests Windows and return → remove temporary logging → document the result.

For an already-working installation, change only what is needed; do not rebuild the whole chain to rename a menu item.

## Source and test discipline

Use current primary sources linked in docs/sources.md for version-sensitive advice. Describe community workarounds as such. Verify installed binaries rather than trusting a package name.

The signer template preserves the field-tested approach, but generalized output has not been boot-tested on every machine. Tests cover rendering, ESP validation, recursion, and update ordering; they are not hardware certification. Run `python3 -m unittest discover -s tests -v` after editing scripts or templates. Add tests only for meaningful behavior.

Any changed EFI executable must be re-signed and verified before installation. Never install an image with a stale signature. Keep the label patch optional and offline; do not mutate a mounted EFI binary directly.

## Completion criteria

Report what is directly verified, user-confirmed, inferred, and still untested. A successful single reboot is useful evidence, not “bulletproof.” Do not invent a root cause for a pre-menu blank screen. Record recovery instructions and disable temporary diagnostics when finished. Mention that the separate initramfs is unauthenticated; do not equate this arrangement with a fully authenticated UKI chain.
