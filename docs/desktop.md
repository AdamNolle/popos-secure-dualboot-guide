# Optional desktop fixes

These are separate from Secure Boot. Apply only the parts matching your hardware and preferences, preserve the previous settings, and validate each change independently.

## NVIDIA and freezes

Use the driver packages supported by your installed Pop release; inspect `apt-cache policy system76-driver-nvidia`, `nvidia-smi`, `dkms status`, and previous-boot kernel logs first. Avoid mixing distribution packages with NVIDIA's standalone `.run` installer. An Xid entry or compositor error is evidence to investigate, not proof the GPU is defective.

The reference COSMIC/NVIDIA investigation used `COSMIC_DISABLE_SYNCOBJ=1` and pinned compositor rendering to the actual NVIDIA PCI device with `COSMIC_RENDER_DEVICE` and `COSMIC_DRM_ALLOW_DEVICES`. These are version-specific diagnostic workarounds, not universal performance settings. Inspect the installed compositor's supported options/current source before using them. Do not copy this machine's PCI device IDs. They can affect synchronization, flicker, or performance; remove the overrides and log out/in to undo. No long-term freeze cure was proven solely by setting these variables.

## Logitech peripherals

Linux kernel HID drivers normally handle keyboards/mice; `hid_logitech_hidpp` and `hid_logitech_dj` support relevant Logitech receiver/device functions. UVC cameras use the kernel camera stack. Solaar is an optional Linux configuration tool for supported devices, not a replacement kernel driver. Check [supported installation methods](https://pwr-solaar.github.io/Solaar/installation/), then use the distribution package where suitable:

```sh
sudo apt-get -o DPkg::Lock::Timeout=600 install solaar
solaar show
lsusb
```

If receiver permissions changed after installation, reload the installed udev rules and reconnect the receiver or log out/in. Do not use blanket world-writable hidraw permissions. Not every Windows vendor feature is available on Linux. Check `fwupdmgr get-devices` and vendor support for actual firmware availability; detected hardware is not proof an update exists.

## DisplayPort/HDMI audio

Use `wpctl status`, `pavucontrol`, and the sound settings to identify the NVIDIA output profile and intended monitor. DP audio may have an HDMI-labelled ALSA profile. Check mute, the hardware speaker/monitor volume, the selected sink, and the monitor's own audio source. Do not assume the monitor has speakers rather than only a headphone output.

Both reference monitors produced audible output only after a user-requested 100% test; subsequent normal volume was lowered. Ask before loud playback, especially with headphones, and return to the user's preferred volume. This was a routing/volume verification, not an installation of a special monitor driver.

## Narration and panel battery icon

For desktops honoring the GNOME accessibility setting:

```sh
gsettings get org.gnome.desktop.a11y.applications screen-reader-enabled
gsettings set org.gnome.desktop.a11y.applications screen-reader-enabled false
```

Stop an already-running screen reader through the desktop's accessibility controls; changing a stored setting may not stop an existing process. Undo by setting `true` if desired. COSMIC versions can expose their own settings too.

Remove only the Battery applet through COSMIC panel customization. Preserve the Power/shutdown applet. Logitech battery reporting can still be useful on a desktop. If editing COSMIC config files, back up the exact file and account for schema changes; avoid replacing the user's whole panel configuration with somebody else's.

## Performance preference

`system76-power profile performance` selects the highest supported profile, not a fixed maximum clock. Thermal, workload, and hardware limits remain. Review `templates/desktop-performance-apply` before installing; it checks profile, CPU governors/preferences, and boost, and tolerates only the specific unsupported SATA power-policy error observed on the reference controller.

For persistence on matching systems, install the reviewed helper as `/usr/local/sbin/desktop-performance-apply` and use a local unit such as:

```ini
[Unit]
Description=Apply desktop performance preference
After=system76-power.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/desktop-performance-apply
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable only after a successful manual run. This sample applies at boot; reapply if another power manager changes the policy. Undo by disabling/removing the custom service, reloading systemd, and selecting `system76-power profile balanced`. Do not install competing power managers or force clocks/overclock as a generic crash fix.

## Terminal paste

`^[[200~` is a bracketed-paste marker being shown literally. Test in a fresh terminal and shell first. In Bash/readline, preserve existing configuration and add `set enable-bracketed-paste on` to `~/.inputrc`, then open a fresh session. Avoid introducing raw escape sequences or auto-executing clipboard contents in shell startup files.

The usual terminal paste shortcut is Ctrl+Shift+V. Configure Ctrl+V → Paste in COSMIC Terminal if preferred; preserve Ctrl+C as interrupt. An embedded terminal may have separate application shortcuts. A Bash-only Ctrl+V binding is not universal: editors, password prompts, and other programs need the terminal application's paste action. Do not blindly bind clipboard text to `eval` or send embedded newlines as commands. The reference machine had an additional Bash editable-line clipboard helper; that host-specific helper is not shipped as a universal shortcut here.

## Repeated password prompts

Sudo credential caching and graphical PolicyKit authentication are separate mechanisms. If a longer sudo cache is desired, use `sudo visudo -f /etc/sudoers.d/local-cache` and a user-specific rule such as `Defaults:YOUR_USER timestamp_timeout=60`. Replace the account name and validate with `sudo visudo -c`. Cross-terminal caching can be requested with `timestamp_type=global`, at the cost of sharing the authentication window between terminals. Rebooting clears the cache. These settings do not eliminate graphical prompts; do not use broad NOPASSWD or permissive PolicyKit rules as a workaround.

## Looking Glass

Looking Glass uses a Windows VM host component while Linux and the client run concurrently, with the required GPU/shared-memory setup. The Windows installation selected during a reboot is not running alongside Linux. Installing the client does not make that dual-boot Windows desktop available. See [official requirements](https://looking-glass.io/docs/B7/requirements/) before undertaking a separate VM/GPU-passthrough project. The reference machine had the B7 client installed, but no Windows VM or passthrough was created.
