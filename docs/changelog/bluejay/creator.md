# QuiltOS 0.3.1 - Real features, not new toggles

Finalized after focused component builds, a complete device build, exact-base
incremental generation, and machine inspection of the signed OTA.

This release doesn't add new code from other ROMs. It connects real,
already-built customization and privacy screens that were shipping inside
QuiltOS but were never reachable from Settings, and removes one piece of dead
duplicate code found during the audit.

- **Diagnostics reporting is now visible and controllable.** QuiltOS has been
  uploading an anonymous, hashed device ID, model, mod version, country, and
  carrier once a day since early builds, with no on/off switch anywhere in
  Settings. Quilt Privacy Guard now has a Diagnostics reporting card that
  opens the real control for it. The collection default has not been changed
  by this release — it is still enabled until you turn it off — but you can
  now see it and turn it off.
- **Charging sounds** are now reachable from Quilt System settings:
  independent wired/wireless charging tone and vibration controls.
- **Display rotation** is now reachable from Quilt Display settings: choose
  which of the four orientations auto-rotate is allowed to use, instead of
  the single on/off toggle.
- **Blissify's community credits page** — team and project links for
  BlissRoms and BlissOS, with a live-fetched roster and a static fallback —
  is now linked from About QuiltOS instead of sitting unreachable.
- Removed a dead duplicate "Input Buttons" screen that had no working entry
  point and would only have confused anyone who found it; the real Buttons
  entry in Quilt Input already covers the same ground.
- Audited three additional dynamic Settings tiles (LiveDisplay, Trust
  interface, Profiles) that AOSP's own tile-injection mechanism should already
  surface on Display, Privacy, and System; confirmed their manifest
  declarations are correct and unaffected by the 0.3.0 dashboard rebuild.

Nothing in this release touches root state, Play Integrity, verified boot, or
any other security gate. QuiltOS remains unrooted by default.
