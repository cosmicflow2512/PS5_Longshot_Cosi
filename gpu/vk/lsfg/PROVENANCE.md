# gpu/vk/lsfg

Four files of PS5SX2's Lossless Scaling frame generation (`ps5/coreorbis/orbis-shims/lsfg` at 5d94db4e73,
GPL-3.0-or-later, copyright and SPDX lines kept), changed for Longshot. The other 22, unmodified, are in
`third_party/lsfg` (its `PROVENANCE.md` has where they come from: PS5SX2, from the Eden emulator, from lsfg-vk).
`ps5/build.py` puts this folder before `third_party/lsfg` on the include path, so `#include "lsfg_vk.h"` there finds the
one here.

Changed here:

- `lsfg_vk.h`: Vulkan through Longshot's loader (`../vk_loader.h`) and VMA, under `LONGSHOT_LSFG`.
- `lsfg_vk.cpp`: the chain's images and upload buffers through `vk_vma.cpp` (`lsfg_vma_image`, `lsfg_vma_upload`), with
  the renderer's memory priority.
- `lsfg_backend.h/.cpp`: `RecordShared` and `RecordGeneration` (a frame at the chain's moment nearest to the one asked,
  for Auto and for 3x and 4x), and every generation slot's target is the one output.

The adapter is in `gpu/vk/vk_framegen.cpp` (`lsfg_feed`, `lsfg_take`).
