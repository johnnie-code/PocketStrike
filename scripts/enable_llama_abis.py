"""Patch the locked llama_flutter_android 0.2.6 package for ARM32 builds.

Run after pub get. Fail on upstream changes rather than silently skipping patches.
"""
import json
from pathlib import Path
from urllib.parse import urlparse, unquote

config = Path('.dart_tool/package_config.json').resolve()
packages = json.loads(config.read_text())['packages']
package = next(p for p in packages if p['name'] == 'llama_flutter_android')
uri = urlparse(package['rootUri'])
root = Path(unquote(uri.path)) if uri.scheme == 'file' else config.parent / unquote(uri.path)


def replace(relative, old, new):
    path = root / relative
    text = path.read_text()
    if text.count(old) != 1:
        raise RuntimeError(f'Expected exactly one patch target in {path}: {old}')
    path.write_text(text.replace(old, new))


replace('android/build.gradle.kts',
        'abiFilters.addAll(listOf("arm64-v8a"))',
        'abiFilters.addAll(listOf("arm64-v8a", "armeabi-v7a", "x86_64"))')
replace('android/build.gradle.kts',
        '"-DGGML_CPU_AARCH64=ON",',
        '"-DGGML_CPU_AARCH64=OFF", "-DCMAKE_JOB_POOLS=compile_pool=2", '
        '"-DCMAKE_JOB_POOL_COMPILE=compile_pool",')
replace('android/build.gradle.kts',
        '"-DGGML_DOTPROD=ON"', '"-DGGML_DOTPROD=OFF"')
replace('android/CMakeLists.txt',
        'set(GGML_CPU_AARCH64 ON CACHE BOOL "Enable ARM64 support")\nset(GGML_DOTPROD ON CACHE BOOL "Enable ARM NEON dot product")',
        '''if(ANDROID_ABI STREQUAL "arm64-v8a")
    set(GGML_CPU_AARCH64 ON CACHE BOOL "Enable ARM64 support" FORCE)
else()
    set(GGML_CPU_AARCH64 OFF CACHE BOOL "Enable ARM64 support" FORCE)
endif()
set(GGML_DOTPROD OFF CACHE BOOL "Portable CPU support" FORCE)''')
print(f'Enabled ARM64, ARM32 and x86_64 in {root}')
