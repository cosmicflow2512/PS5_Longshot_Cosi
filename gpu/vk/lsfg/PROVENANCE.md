# gpu/vk/lsfg

Lossless Scaling's frame generation (LSFG) on plain Vulkan and VMA, 26 files copied from
[PS5SX2](https://github.com/Swordpdf/PS5SX2) `ps5/coreorbis/orbis-shims/lsfg` at 5d94db4e73 (GPL-3.0-or-later; copyright and
SPDX lines kept). PS5SX2's is the Eden emulator's (git.eden-emu.dev, 67bada77f8a4), which is lsfg-vk's.

Nothing of Lossless Scaling is here: its compute shaders are read at run time from the player's own `Lossless.dll`.

Changed here: `lsfg_vk.h` takes Vulkan from Longshot's loader (`../vk_loader.h`) under `LONGSHOT_LSFG`. `lsfg_backend.h/.cpp`: `RecordShared` and `RecordGeneration` (a frame at the chain's moment nearest to the one asked,
for Auto and for 3x and 4x), and every generation slot's target is the one output. Nothing else.
The adapter is in `gpu/vk/vk_framegen.cpp` (`lsfg_feed`, `lsfg_take`); `ps5/build.py` compiles the folder.

Outside this folder, written for Longshot: the adapter in `gpu/vk/vk_framegen.cpp` that feeds the chain each of the
game's frames and takes its frames into the sets the display thread shows, at the moments Auto and 2x to 4x ask
for; the Frame generation by row's value, shown only with a `Lossless.dll` there (`gpu/vk/vk_menu.cpp`,
`gpu/vk/fg_by.h`); PS5_MihawkGen's network in its place where the file cannot be read; and the steps by the
console's free memory, which let the chain go. `docs/PS5.md` says where the file goes.
