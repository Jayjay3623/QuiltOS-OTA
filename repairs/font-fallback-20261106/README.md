# Quilt font fallback boot-loop correction

This source addendum covers Pixel 7 (`panther`), Pixel 7 Pro (`cheetah`), and Pixel 6a (`bluejay`). All three replacement target archives have been rebuilt and checked; OTA packaging and final release validation are still in progress. This directory is source code and test evidence, not an installable update or a claim of successful hardware boot testing.

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

The Android `TypefaceTest` suite ran under Ravenwood on 2026-11-06: eight tests passed, zero failed, and the existing serialization test was assumption-skipped because `SharedMemory` is unsupported in this host environment. The new `testRuntimeFontFallbackCannotCreatePlaceholderCycle` passed and executed native `Paint.measureText`. `ravenwood-native-test-result.json` contains the raw test result; `ravenwood-native-verification.json` binds the source, test jar, host support patch, runner and logs by checksum. This is native host runtime evidence, not physical hardware boot or installation evidence. No phone was rebooted, powered off or flashed for this validation.

## Additional build changes

Apply `test-overload-compatibility.patch` inside `frameworks/base` with `patch -p1 --batch`. It disambiguates two existing test calls to the nullable `String` overload of `FontListParser.parse`; it does not change production code. The Ravenwood host runner enables the ROM's experimental `FontController` implementation with `RAVENWOOD_ENABLE_EXP_API=1` and logs its use with `RAVENWOOD_LOG_EXP_API=1`. These settings do not disable assertions or replace the implementation with a mock. The completed native test result is recorded above.

Apply `oem-preopt-product.patch` at the assembled Android source root with `patch -p1 --batch`. It disables shipped preoptimization caches for `libhwinfo`, `RadioConfigLib`, `com.android.hotwordenrollment.common.util`, `google-ril`, and `oemrilhook` on all three products. Their original jars contain embedded DEX and must remain byte-identical to each exact update baseline. Android can generate optimization caches for the installed framework. This avoids shipping regenerated OEM-derived cache bytes or retaining caches compiled against the previous framework.

The packaging verifier requires the scoped `.odex`, `.vdex`, and `.art` files to be absent, verifies the five unchanged jars and their embedded DEX, and records every removed baseline cache separately. All other retained OEM file and symlink checks remain required, as does payload source-copy coverage for retained OEM file data. These checks establish artifact provenance; they are not a grant of commercial redistribution rights or hardware boot evidence.

## Reproducing the native host test

After the source patches above, apply `ravenwood-host-support.patch` inside `frameworks/base` with `patch -p1 --batch`. This host-only policy retains the real Quilt `GamePropsSpoofService` and `ApplicationPackageManager.registerSpoofSettingsObserver` implementations during application initialization. It does not alter production Java or suppress font assertions. HostStubGen already retains generated synthetic lambda methods.

On the isolated Linux build/test host, supply `SYSTEM/framework/org.lineageos.platform-res.apk` from the validated panther target archive at `/system/framework/org.lineageos.platform-res.apk`, readable by the test user. The ROM's `AssetManager` expects this absolute resource path. The exact fixture is 301131 bytes, SHA-256 `b128a53238193f3991fb7aeda4cced0c7faafab71ba23321fffeca713ff3aa3f`; its source archive hash is recorded in `ravenwood-native-verification.json`. This fixture setup is for the cloud test host, not an attached Android device.

With `OUT_DIR` pointing to the panther host build output, source `build/envsetup.sh`, select `quilt_panther-cp2a-user`, and run:

```sh
RAVENWOOD_ENABLE_EXP_API=1 RAVENWOOD_LOG_EXP_API=1 \
  atest --host --no-metrics --disable-upload-result -j4 \
  FrameworksCoreTestsRavenwood:android.graphics.TypefaceTest
```

Do not interpret the test runner's generic “1 device” summary as a physical installation: this invocation uses `--host` and the x86_64 Ravenwood module.
