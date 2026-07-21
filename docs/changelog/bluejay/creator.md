# QuiltOS Creator 0.2.5 — Changelog

Delivered as an incremental update from 0.2.1 (bluejay / Pixel 6a). There was
no public 0.2.2 or 0.2.3.

## New: Quilt Assistant

- A new "Quilt Assistant" in Quilt Settings changes common settings with a
  required confirm step: toggle dark theme (applied directly), and jump to
  battery saver, Do Not Disturb, network privacy, and the privacy dashboard.
- It is honest about what it is: **rule-based, not a chatbot.** Every direct
  change asks you to confirm first; nothing happens automatically. The screen
  states plainly that it runs in rule-based mode.
- Groundwork for an optional on-device model is in place (the intended runtime
  is ExecuTorch, which ships in the platform source). QuiltOS bundles **no**
  model, so free-text understanding is honestly reported as unavailable until a
  verified local model is installed; the assistant never fabricates responses.

## New: expanded local intelligence

- QuiltOS Intelligence adds a "night comfort" suggestion that reads only the
  phone's local clock (no location, no network, no app content) and suggests
  dark theme late at night. Like the existing storage suggestion, it is opt-in,
  gated behind the master switch, and pruned by your retention setting.

## Notes & honesty

- The versioned release notes are updated to 0.2.5 and remain reachable from
  Settings → QuiltOS and the System Updater.
- This is an incremental over 0.2.1; devices on older builds update
  sequentially (… → 0.2.1 → 0.2.4 → 0.2.5).
- Everything here is **source-implemented and source-asserted**, and the build
  compiled cleanly with all machine OTA gates passing, but **none of it has
  been tested on a physical phone yet** — including the assistant's actions and
  the night-comfort suggestion. Compilation is not runtime proof; report any
  hardware misbehavior for a point fix.
- Deliberately not done: a real free-text/LLM assistant (needs a sourced,
  hardware-verified on-device model — a future release, for which this is the
  honest scaffold), and the Pixel 7 / S24 ports (the request marks them out of
  scope for this update). "25 features" was not padded with placebo toggles;
  QuiltOS ships what it can do truthfully.
