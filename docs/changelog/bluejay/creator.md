# QuiltOS 0.3.0 - First Run and Reliability

Finalized after focused component builds, a complete device build, exact-base
incremental generation, and machine inspection of the signed OTA.

- A redesigned Quilt welcome screen with a subtle blue-white surface, centered start action, and accessible emergency and accessibility controls.
- A connected QuiltOS first-run experience that preserves the complete Google setup flow.
- Reachable light/dark Quilt wallpaper, optional root preparation, Iconify, and update-policy choices.
- A rebuilt Quilt Settings home with Privacy, Root, Iconify, Assistant, Intelligence, Maintenance, and About QuiltOS.
- Safer Privacy history loading that cannot block the Settings UI and fails gracefully when AppOps data is unavailable.
- Safer QuiltAssistant navigation with proper day/night surfaces and truthful supported actions.
- Safer updater install handling when a downloaded file disappears, an A/B payload is malformed, update_engine rejects it, or the update record changes during a callback.
- Supported ART speed-profile optimization for newly installed apps.
- QuiltOS branding, release notes, firmware graphics, accessibility, and daily-driver polish.

QuiltOS remains unrooted by default. The root page reports real Magisk/runtime state and guides an optional patched-boot workflow; it does not fake or silently grant root. Pixel 6a fingerprint remains the secure biometric path because the device has no secure face-authentication HAL.
