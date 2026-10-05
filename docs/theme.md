# Dark theme and BIOS label

Copy `assets/cosmic-dark/` to `EFI/refind/themes/cosmic-dark/` on the correctly identified Linux ESP after backing up existing content. The rendered menu includes its `theme.conf`; it uses 192px OS icons and 48px tool icons, Windows default, a 20-second timer, and firmware/reboot/shutdown controls. It does not force a graphics resolution.

The four-square Windows-style icon, Tux, and clear tool symbols were used on the reference machine. Retain the Tux copyright notice and third-party notices when redistributing. The preview was captured in a VM and its countdown is illustrative.

## Optional gear text: BIOS

In rEFInd 0.14.2 the gear's `Reboot to Computer Setup Utility` title is compiled into the executable. Changing theme.conf alone does not rename it. `scripts/rename-refind-label.py` replaces exactly that UTF-16 string in a **new staged copy**, preserves image length, and refuses unknown/multiple matches. It targets only the inspected version/layout; use an upstream source change/build for a different binary.

```sh
python3 scripts/rename-refind-label.py upstream-refind_x64.efi local/refind-bios.efi
sbattach --remove local/refind-bios.efi   # only if the staged source had a signature
```

After removing stale signatures, sign the staged image with your own enrolled key and run `sbverify --cert` before installing. See setup.md. Keep the original untouched. The original attempt to sign a modified binary while retaining its stale signature failed verification; nothing from that failed check was installed.

The label patch changes wording, not the firmware action. Changing any executable bytes invalidates existing signatures. A distribution/upstream rEFInd update replaces this customization; reapply only after confirming the expected source string and repeat signature/boot checks. No pre-signed or unsigned EFI executable is distributed in this repository.
