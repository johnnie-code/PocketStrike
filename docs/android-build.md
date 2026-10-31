# Sideload build

Manual workflow template: `ci/android-build.yml`. Move it to
`.github/workflows/build.yml` once the GitHub credential has `workflow` scope.
The supplied OAuth credential rejects workflow-file pushes; no CI run has been
started. Do not publish a GitHub Release for these builds.

Pinned SDK: Flutter 3.47.9 stable, revision
`c197ca5199e9ee5661e865596c9c07294dfab51c`, verified locally with Dart 3.13.7.
This satisfies pubspec's actual `^3.12.2` requirement. The README's Flutter 3.29
minimum does not describe a sufficient bundled Dart version. The lockfile has
been refreshed for the four SDK-pinned test/math dependencies of this Flutter.
Java 17, Gradle 9.1.0, AGP 9.0.1, Kotlin plugin declaration 2.3.20,
Flutter NDK 28.2.13676358, CMake 3.22.1; minSdk 26.

There was no existing CI or repository-owned CMake configuration. The app
Gradle file has no ABI filters or splits. Flutter's split command requests
armeabi-v7a, arm64-v8a and x86_64, but the locked hosted native dependency
`llama_flutter_android` 0.2.6 has an ARM64-only filter in
`android/build.gradle.kts`, plus unconditional ARM64 options there and in
`android/CMakeLists.txt`. Thus an ARM32 Flutter shell alone is not evidence of
an ARM32 llama engine.

After `flutter pub get --enforce-lockfile`, run
`python3 scripts/enable_llama_abis.py` once on the fresh dependency cache.
It checks exact patch targets, enables all three ABIs and makes ARM64 flags
conditional. It also limits native compilation concurrency. The dependency
archive is hash-pinned by pubspec.lock. The script intentionally fails if
already applied or upstream contents change. Use a fresh package cache when
repeating the full workflow.

Build with `flutter build apk --release --split-per-abi`. Inspect the APKs'
`lib/` directories, including `libllama_jni.so`, before distributing them.
No model weights are bundled. Release currently uses the project's debug
signing configuration; a separately generated key will not update an install
signed by somebody else's key. Back up app data before uninstalling a prior
installation.
