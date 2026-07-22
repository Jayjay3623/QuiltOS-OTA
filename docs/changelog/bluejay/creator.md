# QuiltOS 0.2.6 — Assistant Repair

- Rebuilt Quilt Assistant as a stable, permission-safe system component.
- Added clear local-assistant capability status instead of claiming unavailable model support.
- Restricted Assistant shortcuts to visible Android Settings pages; Android remains responsible for user confirmation.
- Removed broad privileged permissions, silent setting changes, background collection, and incompatible model downloads.
- Fixed Assistant launch, message-list rendering, resources, and manifest declarations.
- Removed the global missing-dependency workaround and verified Quilt Assistant, Settings, and the complete Bluejay ROM build.

Quilt Assistant in this release is a local Settings navigator. On-device generative inference remains disabled until QuiltOS has a verified ExecuTorch `.pte` model, matching tokenizer, and provenance checks.
