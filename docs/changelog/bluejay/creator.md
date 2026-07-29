# QuiltOS 0.3.2 - Duplicate Device Intelligence package removed

This is a maintenance release. It does not add new features.

Every QuiltOS build shipped to date (0.1.8 through 0.3.1) installed the
Google Device Intelligence Network component **twice**: once as the
build-matched copy from the bluejay vendor tree, and once as the generic
copy pulled in by full GApps, under names that Soong treated as distinct
packages. Both 23 MB copies were present in `product/priv-app/` on every
release. 0.3.2 removes the redundant generic copy; only the build-matched
copy is installed, saving roughly 23 MB and removing a source of package
duplication.

Nothing else has changed. No screens, defaults, or behavior are different
in this release, and nothing in it touches root state, Play Integrity,
verified boot, or any other security gate. QuiltOS remains unrooted by
default.

QuiltOS's Android 17 upgrade remains in progress in a separate workstream
and is not part of this release. Android 17 is not yet buildable on the
current upstream LineageOS branch, and BlissROM does not yet have an
Android 17 branch to build the QuiltOS feature set on top of; shipping it
today would mean losing QuiltOS's existing customization and privacy
features, not gaining new ones. This device stays on the current,
fully-featured Android 16 base until that work is ready.
