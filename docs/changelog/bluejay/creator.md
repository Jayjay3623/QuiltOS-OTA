# QuiltOS Creator 0.2.1 — Pixel 6a

Delivered as a sequential incremental update from QuiltOS 0.2.0. Devices on
0.1.9 must install 0.2.0 first.

## What changed

- First boot now visibly belongs to QuiltOS: “Welcome to QuiltOS”, centred
  Start, lower Accessibility and Emergency Call actions, no first-page Skip,
  a subtle animated Quilt gradient, and centred progress state on applicable
  steps while retaining the established Android setup graph.
- An early wallpaper step offers bundled 1080×2400 Light Quilt and Dark Quilt
  wallpapers. The choice is persisted and applied through Android's
  `WallpaperManager`; Light Quilt remains the default.
- QuiltOS Settings now provides an honest guided Magisk workflow. Manager
  installation is reported separately from runtime root. **Root active** is
  shown only when Magisk answers and a live root shell reports `uid=0`.
- Enabling root requires selecting the matching Android boot image, passing
  local device/header/size checks, comparing its published SHA-256, patching a
  copy in Magisk, and performing an explicit reboot-required bootloader step.
  QuiltOS does not patch or flash the phone automatically.
- Disabling root guides restoration of the exact matching stock image and does
  not report success until the post-reboot runtime probe finds no Magisk root.
- Iconify remains optional, clearly states its root-backend requirement, and is
  available later in QuiltOS Settings. Setup never enables root automatically.
- The fixed updater storage path, non-crashing update-engine handling, and
  QuiltOS 0.2.0 privacy/settings changes remain present.

## Matching stock boot image

- File: `quiltos-boot-1784465756.img`
- SHA-256: `d091c0290a1c965fc14297d8e524b47f40605bdf47cd736edfb9191d7206d512`
- Use only with QuiltOS 0.2.1 build incremental `1784465756` on bluejay.

## Validation scope

- Component build: passed for BlissSetupWizard and Settings.
- Full bluejay user build: passed, including image/AVB and full OTA packaging.
- OTA: generated only from sealed 0.2.0 incremental `1784424837`; machine
  inspection passed ZIP integrity, bluejay assertion, A/B payload, exact base,
  post identity, and filename gates.
- Source/resource asserted: actual wizard script references Quilt pages; both
  wallpapers are packaged at 1080×2400; root active requires `su -c id` with
  `uid=0`; no preference is used as active-root proof; updater safeguards and
  touched Quilt branding are present.
- Device-tested: not tested in this unattended environment.
- Emulator-tested: not tested.
- Runtime UI layout, animation, wallpaper application, Magisk patch/restore,
  reboot transitions, and Iconify application remain untested on hardware.
