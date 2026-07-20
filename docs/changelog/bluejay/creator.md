# QuiltOS Creator 0.2.4 — Changelog

Delivered as an incremental update from 0.2.1 (bluejay / Pixel 6a). There was
no public 0.2.2 or 0.2.3.

## New: QuiltOS Intelligence (opt-in, local-only)

- A new "QuiltOS Intelligence" area with a master switch that is OFF by
  default, individual feature switches, a 7/30-day retention choice, and a
  one-tap "clear suggestion history" action. Nothing is computed until you
  opt in, and nothing ever leaves the phone.
- One live suggestion ships in this release: **storage suggestions**. It reads
  only this phone's own disk-space statistics (no app content, no contacts,
  no messages, no location, no network) and, when free space runs low,
  suggests the safe cache cleaner with a plain-language rationale. When space
  is healthy it says so instead of inventing advice.
- The "cast at a familiar time" idea is present only as a recorded preference;
  it does not yet produce suggestions and says so. Address suggestions are
  shown as truthfully unavailable — no open local component can provide them,
  so there is no fake toggle.

## New: safe cache cleaner

- Settings → QuiltOS → Maintenance offers a confirmed one-tap cleanup of
  application caches using the platform's cache-only API. It never touches
  app data, accounts, logins, media, or downloads, reports how many packages
  were cleaned and how many were unavailable, and shows the approximate space
  freed (measured as the change in free space, so concurrent activity can
  affect the number slightly).

## Root workflow improvements

- The boot-image verification step now also computes and displays the
  selected file's SHA-256 so you can compare it with the value in these
  release notes before patching in Magisk. The verdict is shown once and
  never stored.
- Root is reported "active" only after a live root shell actually answers as
  uid 0 — a su binary that merely prints a version is not treated as root.
  Root remains off by default; there is no live root toggle, and nothing is
  flashed automatically.

## What's New & release notes

- After an update finishes and the phone completes its first boot on the new
  build, QuiltOS shows a one-time notification linking to these notes. An
  ordinary reboot, a failed update, or first-time setup never shows it.
- The same versioned notes are always reachable from Settings → QuiltOS and
  from the System Updater's new "What's new on this device" menu item (works
  offline; the online changelog link remains too).

## Investigated honestly, not changed

- **NFC tag reading**: there is no bluejay-specific NFC configuration in the
  buildable source (the NFC stack is stock AOSP plus Google's signed vendor
  HAL), and no reproducible failure evidence was available in this
  environment. Per this release's own evidence rule, no speculative NFC
  change was made. If you can reproduce a scan failure, capture it and it
  will be diagnosed against real evidence.
- **Bliss branding**: an audit found no remaining user-visible BlissROM text
  in Settings. Icon artwork was checked by resource name only; a visual pass
  on hardware is still pending.

## Verification honesty

- Everything above is **source-implemented and source-asserted**; the build
  compiled cleanly and all seven machine OTA gates passed. **None of it has
  been tested on a physical phone yet** — including the cache cleaner's
  reclaimed-space figure, the storage suggestion, the What's New gate, and
  the root verification flow. Compilation is not runtime proof; if something
  misbehaves on hardware, report it for a point fix.
- This is an incremental over 0.2.1; devices on older builds must update
  sequentially (0.1.9 → 0.2.0 → 0.2.1 → 0.2.4).
