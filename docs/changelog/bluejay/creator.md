# QuiltOS Creator 0.1.8 — Changelog

Delivered as an incremental update from 0.1.7 (bluejay / Pixel 6a).

## Privacy Guard (Settings → QuiltOS → Privacy)

- **Sensor controls** — system-backed camera and microphone kill switches (via the
  platform SensorPrivacyManager), plus a per-app sensor block list.
- **Camera & mic indicator** — surfaces Android's authoritative camera/microphone
  access indicators and links to the platform Privacy controls (no fake toggle).
- **Permission timeline** — shows when apps last used camera, microphone, or location,
  read from the system's own access records.
- **Network privacy** — direct links to the real platform controls: Private DNS,
  per-network Wi-Fi MAC randomization, per-app network & data, and unused-app
  auto-revoke.
- **Connectivity hardening** — a real switch that turns the system captive-portal
  connectivity check off or back on (writes the actual system setting). With it off,
  some Wi-Fi sign-in pages may need to be opened manually.
- **Clipboard guard** — explains Android's built-in clipboard protections and links to
  Privacy controls.

## Root & Security (Settings → QuiltOS → Root & Security)

- Reports Magisk **manager** and **runtime** status separately and truthfully. The
  device is treated as unrooted unless a real Magisk runtime responds — manager
  presence alone does not enable root.
- Guided, **optional** Magisk boot-image patch workflow (patch a copy of the exact
  matching boot image, install only with an unlocked bootloader, recovery guidance,
  and a clearly supported stay-unrooted path). QuiltOS never patches the active boot
  image or grants root automatically.

## Branding

- QuiltOS branding across the QuiltOS settings dashboard (Privacy, Root & Security,
  the QuiltOS about page, and themable icons).

## Deliberately not included

- No prop spoofing and no app-based root hiding. These exist to defeat integrity and
  detection checks; QuiltOS does not ship them.

## Note

This is an incremental over 0.1.7; install 0.1.7 first if you are on an older build.
The new privacy screens are wired to real Android system controls, but their on-device
behavior has not been smoke-tested on hardware in this build.
