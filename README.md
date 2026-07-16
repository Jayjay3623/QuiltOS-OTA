# QuiltOS OTA repository

This directory is the public, static OTA control plane for QuiltOS. It is
designed to be published as `Jayjay3623/QuiltOS-OTA`. The updater reads the
small JSON manifests directly from `raw.githubusercontent.com`; GitHub Pages is
optional and may later provide prettier changelog pages.

## Initial setup

1. Create the public repository and push this directory.
2. Keep manifests under `/docs/api/v1/<device>/<channel>/<incremental>.json`.
3. Leave a build's manifest empty until its exact successor OTA passes every
   release gate.
4. Never send Codex a GitHub token, Cloudflare
   secret, OTA signing private key, wallet seed, or recovery phrase.

## Layout

- `docs/api/v1/bluejay/creator/<incremental>.json`: response for one exact
  installed Creator build.
- `docs/api/v1/bluejay/creator/index.json`: informational latest-build response;
  current clients do not use it for incremental selection.
- `docs/changelog/bluejay/creator.md`: human-readable release notes.
- `schema/update.schema.json`: the supported manifest contract.

The manifest remains empty until the package has passed clean-install, update,
boot-success, connectivity, and rollback tests. Publishing metadata is the final
release action, not the first.

## Package hosting

Use a GitHub Release asset for an incremental OTA below GitHub's 2 GiB per-file
limit. Use a public Cloudflare R2 Standard bucket for full/oversized OTAs and
put only the immutable HTTPS object URL in the manifest. The SHA-256 digest is
also used as `id`.

## Safety model

The updater verifies the Android OTA package signature before applying its A/B
payload to the inactive slot. Boot failure fallback protects the system slots;
it does not automatically roll back app data or user files. Data checkpoints and
wallet recovery verification are separate, explicit workflows.
