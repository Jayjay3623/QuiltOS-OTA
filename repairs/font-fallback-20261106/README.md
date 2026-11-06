# Quilt font fallback boot-loop correction

This source addendum covers Pixel 7 (`panther`), Pixel 7 Pro (`cheetah`), and Pixel 6a (`bluejay`). Replacement firmware is still being built and validated. This directory is source code and test evidence, not an installable update or a claim of successful hardware boot testing.

The withdrawn builds are panther 1793892852, cheetah 1793891372, and bluejay 1793896340. Do not install them. Their updater offers are disabled and their release pages carry withdrawal notices.

## Cause and correction

When a selected custom font is unavailable, the fallback can be the mutable `Typeface.DEFAULT` or `SANS_SERIF` placeholder. Runtime font switching previously stored that same placeholder inside its pending reference. Drawing text then recursed indefinitely in `Typeface.getNativeInstance()`.

The patch resolves the concrete font before deriving styles or changing public placeholders. Runtime reference updates also resolve to a concrete font and reject unresolved or cyclic input before changing the existing reference. This preserves font switching while preventing the reference cycle.

## Matching source

Use the existing [three-device source delivery](https://github.com/Jayjay3623/QuiltOS-OTA/releases/tag/sources-native-notices-1793891372-1793892852-1793896340) and its pinned source catalog. The framework source base is `android--frameworks-base-current-source.tar.gz`, SHA-256 `1ebad444313bc5e05f3ae747575710e5a3861f8128721a022773fe0e032355a7`.

Apply `font-cycle-fix.patch` from this directory inside the assembled `frameworks/base` project using `patch -p1 --batch < /path/to/font-cycle-fix.patch`. Existing component licenses remain applicable. The patch updates only `graphics/java/android/graphics/Typeface.java` and `core/tests/coretests/src/android/graphics/TypefaceTest.java`.

`source-patch-base-verification.json` records an exact checksum match between both original files and that published source archive. `source-and-test-evidence.json` pins the original and modified Java sources and patch.

## Validation and limits

The host regression harness extracts and executes the actual Java reference-handling and `changeFont()` methods, stubbing native allocation and the font controller. The original source reproduces `StackOverflowError`; the correction passes self fallback, aliased placeholders, repeated configuration changes, font replacement, and rejection of unresolved/cyclic input. This test is not an Android boot test.

An Android `TypefaceTest` regression also verifies native text measurement. Its host Android test run and final device archive checks remain pending at the time this addendum is first published. Release-specific results must identify the exact new build and archive hashes. No phone restart or installation is part of source preparation.

## Additional build changes

Apply `test-overload-compatibility.patch` inside `frameworks/base` with `patch -p1 --batch`. It disambiguates two existing test calls to the nullable `String` overload of `FontListParser.parse`; it does not change production code. The Ravenwood host runner enables the ROM's experimental `FontController` implementation with `RAVENWOOD_ENABLE_EXP_API=1` and logs its use with `RAVENWOOD_LOG_EXP_API=1`. These settings do not disable assertions or replace the implementation with a mock. A completed test result is still required.

Apply `oem-preopt-product.patch` at the assembled Android source root with `patch -p1 --batch`. It disables shipped preoptimization caches for `libhwinfo`, `RadioConfigLib`, `com.android.hotwordenrollment.common.util`, `google-ril`, and `oemrilhook` on all three products. Their original jars contain embedded DEX and must remain byte-identical to each exact update baseline. Android can generate optimization caches for the installed framework. This avoids shipping regenerated OEM-derived cache bytes or retaining caches compiled against the previous framework.

The packaging verifier requires the scoped `.odex`, `.vdex`, and `.art` files to be absent, verifies the five unchanged jars and their embedded DEX, and records every removed baseline cache separately. All other retained OEM file and symlink checks remain required, as does payload source-copy coverage for retained OEM file data. These checks establish artifact provenance; they are not a grant of commercial redistribution rights or hardware boot evidence.
