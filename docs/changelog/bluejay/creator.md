# QuiltOS Creator 0.1.9 — Changelog

Delivered as an incremental update from 0.1.8 (bluejay / Pixel 6a).

## Fixed: in-device OTA downloads

- The updater's download directory `/data/quiltos_updates` was never created on
  the device, so in-device update downloads could not start ("destination file
  doesn't exist, can't resume" loop). 0.1.9 creates the directory at boot with
  the same ownership, permissions, and SELinux label model Android already uses
  for OTA packages (`ota_package_file`, the same approach LineageOS uses for
  `/data/lineageos_updates`).
- No security posture change: SELinux stays enforcing, and the updater and
  update_engine use access rules that already existed in the shipped policy.
  Nothing was disabled or bypassed.

## Fixed: Termux breaking after updates

- The bundled Termux app was packaged with a flag (`preprocessed`) that stopped
  the platform from extracting its native bootstrap library, so Termux could
  crash with a dlopen failure after an OTA. The flag is removed; the built
  package now contains `libtermux-bootstrap.so` correctly.

## Notes

- This is an incremental over 0.1.8; install 0.1.8 first if you are on an older
  build.
- A device already on 0.1.7/0.1.8 still has the broken updater, so this one
  update must be installed by sideloading (or via a full image). From 0.1.9
  onward, in-device OTA downloads are expected to work.
- The fix is verified in source and in the built image (init script, SELinux
  file context, and permissions chain all confirmed), but it has **not yet been
  smoke-tested on a physical phone**. If the updater still misbehaves on
  hardware, report it and it will be fixed in a point update.
