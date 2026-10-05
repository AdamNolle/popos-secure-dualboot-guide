# Sources and further reading

Use current primary documentation alongside the dated reference results. Package behavior and firmware trust/revocations can change.

- [System76: installing Pop!_OS](https://support.system76.com/support/install-pop) — official installation baseline and Secure Boot guidance.
- [System76: bootloader repair](https://support.system76.com/support/bootloader) — identify your real partitions before adapting repair commands.
- [rEFInd: Secure Boot](https://www.rodsbooks.com/refind/secureboot.html) — shim and local trust.
- [rEFInd: configuration](https://www.rodsbooks.com/refind/configfile.html) — timeout, defaults, manual entries, tools, and themes.
- [rEFInd: installation](https://www.rodsbooks.com/refind/installing.html) — upstream layout and installation considerations.
- [systemd v255 shim integration source](https://github.com/systemd/systemd/blob/v255/src/boot/efi/shim.c) — relevant to the native loader build tested here.
- [Ubuntu: Secure Boot](https://documentation.ubuntu.com/security/security-features/platform-protections/secure-boot/) — platform trust and module signing context.
- [MSI: boot priority](https://www.msi.com/support/technical_details/MB_Boot_Priority) — firmware/BBS ordering.
- [Acer XV275KP3 manual, System menu](https://www.manua.ls/acer/xv275kp3/manual?p=27) — manufacturer-authored manual mirrored by a third party; Quick Start, input, and Auto Source controls. Confirm the exact P3 model.
- [NVIDIA: UEFI display troubleshooting](https://nvidia.custhelp.com/app/answers/detail/a_id/5310/) — display isolation ideas; do not assume a listed firmware tool applies to an RTX 5080.
- [Solaar installation](https://pwr-solaar.github.io/Solaar/installation/).
- [Looking Glass B7 requirements](https://looking-glass.io/docs/B7/requirements/).
- [System76 firmware daemon source](https://github.com/pop-os/system76-firmware).
- [COSMIC compositor source](https://github.com/pop-os/cosmic-comp) — diagnostic environment variables are implementation/version dependent.

Community dual-boot guides were useful context during troubleshooting. Instructions to clear factory keys, replace firmware trust wholesale, or delete SBAT policy were not part of the final setup. This repository intentionally documents the tested shim/MOK approach and its limits instead.
