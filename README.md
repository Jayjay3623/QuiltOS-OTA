# QuiltOS OTA repository

This directory is the public, static OTA control plane for QuiltOS. It is
designed to be published as `Jayjay3623/QuiltOS-OTA`. The updater reads the
small JSON manifests directly from `raw.githubusercontent.com`; GitHub Pages is
optional and may later provide prettier changelog pages.

## Pixel 7 Pro: full Quilt Updater preview

The [cheetah 1792829003 prerelease](https://github.com/Jayjay3623/QuiltOS-OTA/releases/tag/cheetah-1792829003) includes the full updater and a separately installable Settings update.

1. On an existing QuiltOS cheetah privacy build, install **Quilt-Updater-Settings-v39.apk** from that release as an update to the built-in Settings app.
2. Open **Quilt Updater**, choose **Check for updates**, then **Download update**. Progress shows bytes, percentage, speed and time remaining; downloads can be paused and resumed.
3. After verification, connect power and reach 50% battery before selecting **Install now**.
4. Choose when to restart after installation finishes.

The new app reads `docs/api/v2/cheetah/privacy/<installed-build>.json`. Its check/download/install/restart steps are separate. Legacy v1 feeds are unchanged. Automatic checks and private local bug summaries do not automatically install an OS or upload reports.

This is an experimental Android 17 preview signed with development keys. Cloud software, APK, AVB and whole OTA/payload signature checks passed, and GitHub asset SHA-256 digests match the cloud files. Physical phone UI/update-path and long-term reboot stability remain unverified. Banking/contactless are unverified; Google Wallet is unsupported. Do not relock the bootloader. The production release gates described below remain distinct from this experimental preview.

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
