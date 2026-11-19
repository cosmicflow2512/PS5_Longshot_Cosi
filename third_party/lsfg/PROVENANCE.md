# lsfg

Lossless Scaling's frame generation (LSFG) on plain Vulkan and VMA: 23 of the 26 files of
[PS5SX2](https://github.com/Swordpdf/PS5SX2) `ps5/coreorbis/orbis-shims/lsfg` at 5d94db4e731fcbde4cb4f0f4a16fefe6f05daf12,
unmodified. PS5SX2's are the Eden emulator's (git.eden-emu.dev, 67bada77f8a4), which are
[lsfg-vk](https://github.com/PancakeTAS/lsfg-vk)'s. GPL-3.0-or-later: each file keeps its copyright and SPDX lines;
`COPYING.GPLv3` is PS5SX2's own license text (the repository's root, so `local:` below).

Nothing of Lossless Scaling is here: its compute shaders are read at run time from the player's own `Lossless.dll`
(`lossless_dll.cpp`) and renumbered (`lsfg_translate.cpp`), not decompiled.

The other three, `lsfg_vk.h`, `lsfg_backend.h` and `lsfg_backend.cpp`, are changed for Longshot and are in `gpu/vk/lsfg`
(its `PROVENANCE.md`): `ps5/build.py` puts that folder first on the include path, so these files' `#include "lsfg_vk.h"`
finds Longshot's. Built for the PS5 alone (`ps5/build.py`, `LONGSHOT_LSFG`); the adapter is `gpu/vk/vk_framegen.cpp`.

upstream: https://github.com/Swordpdf/PS5SX2/archive/5d94db4e731fcbde4cb4f0f4a16fefe6f05daf12.tar.gz
upstream-sha256: 01d8576c17bbd99cef80ba35acf7163e3d0f9b31cd2cbb6a7d9b01efae9b53b8
upstream-root: PS5SX2-5d94db4e731fcbde4cb4f0f4a16fefe6f05daf12/ps5/coreorbis/orbis-shims/lsfg
local: COPYING.GPLv3

tree-sha256: 556c77f8736bce878c319173a05e4205a5762c6566a70c9b68becb00d6be9041
