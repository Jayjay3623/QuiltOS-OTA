# QuiltOS Creator 0.2.0 — Changelog

Delivered as an incremental update from 0.1.9 (bluejay / Pixel 6a).

## Fixed: Privacy area crash

- Opening the QuiltOS Privacy pages could crash Settings. Root cause: the
  Privacy Guard grid and Permission timeline screens embedded a Material
  toolbar that depends on AppCompat/Material theme attributes, which do not
  exist in the platform theme Settings pages run under — the screen crashed
  the moment it was opened. Those screens now use the same plain layout idiom
  as the rest of the QuiltOS settings (the system-provided app bar handles the
  title and back navigation), and the timeline cards were rebuilt the same way.
- Camera/microphone kill-switch actions now report the correct source
  ("Settings") to the system's sensor-privacy service.

## Privacy pages audited

- Every QuiltOS privacy page was audited for invalid platform APIs, missing
  resources, null preferences, and lifecycle issues. All surviving controls
  either perform their stated action (sensor kill switches, captive-portal
  switch) or link to the authoritative platform setting (network privacy,
  camera/mic indicators, clipboard). No control was hidden or removed.

## New: Pixel Call Screen readiness (honest)

- A Pixel Call Screening readiness page (Settings → QuiltOS → About) explains
  truthfully (this is guidance for the official feature, not a redesigned phone
  calling or incoming-call screen):
  the official Google Phone app, its support library, and the Pixel 6a feature
  declarations all ship in QuiltOS — nothing more is needed on the ROM side.
  Whether Call Screen actually appears is decided by Google's server-side
  provisioning (device certification, account language/region, carrier).
  QuiltOS does not spoof device identity, boot state, or integrity signals to
  force it, so there is no toggle — the page links to the Google Phone app's
  own settings, which are the authoritative place to check.

## Notes

- This is an incremental over 0.1.9. Devices on 0.1.8 or older must first
  sideload 0.1.9 (its updater fix is what makes in-device OTA work at all).
- The crash fix is verified in source and by rebuild; like 0.1.9, it has not
  yet been smoke-tested on a physical phone. If anything still misbehaves,
  report it and it will be fixed in a point update.
