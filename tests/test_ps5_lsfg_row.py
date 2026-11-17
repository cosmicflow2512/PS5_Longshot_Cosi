"""On the console the Frame generation by row offers Lossless Scaling, with the player's own Lossless.dll there.

gpu/vk/lsfg is PS5SX2's port of the Eden emulator's lsfg-vk (PROVENANCE.md); its shaders are read from the player's file.
gpu/vk/fg_by.h says which of the console's two generators a value asks for, never both at once; compiled here alone.

python -I -B tests/test_ps5_lsfg_row.py [--cxx g++]
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

RUN_ALL_ARGS = ["--cxx", "{cxx}"]

ROOT = Path(__file__).resolve().parents[1]
VK = ROOT / "gpu" / "vk"


def compiled(fixture, cxx):
    with tempfile.TemporaryDirectory(prefix="fg-by-") as tmp:
        cpp = Path(tmp) / "fixture.cpp"
        cpp.write_text(fixture, encoding="utf-8")
        for define in ([], ["-D__PROSPERO__"]):
            subprocess.run([cxx, "-std=c++20", "-Wall", "-Wextra", "-Werror", "-fsyntax-only", "-I", str(VK)] + define +
                           [str(cpp)], check=True)


def checked(checks, passed):
    bad = [why for ok, why in checks if not ok]
    if bad:
        raise SystemExit("FAIL: " + "; ".join(bad))
    print("PASS: " + passed)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cxx", default="g++")
    a = p.parse_args()
    framegen = (VK / "vk_framegen.cpp").read_text(encoding="utf-8")
    menu = (VK / "vk_menu.cpp").read_text(encoding="utf-8")
    compiled(r"""#include "fg_by.h"
using namespace mkwvk::fg_by;
#ifdef __PROSPERO__
static_assert(kMost == kLossless, "the console's row goes up to Lossless Scaling");
static_assert(kLossless == 4, "after PS5_MihawkGen's 3: 2 is upstream's FSR 3.1 FG");
#else
static_assert(kMost == kBuiltIn, "the PC's row is as it was");
#endif
static_assert(!wants_lossless(kAuto) && !wants_lossless(kBuiltIn) && !wants_lossless(kMihawk) && wants_lossless(kLossless));
static_assert(wants_network(kAuto, false) && wants_network(kMihawk, false), "the network at its own value");
static_assert(!wants_network(kBuiltIn, false) && !wants_network(kBuiltIn, true), "Built-in: neither of the two");
static_assert(!wants_network(kLossless, true), "never the network and the chain at once");
static_assert(wants_network(kLossless, false), "the file not read: the network's frames, not none");
int main() { return 0; }
""", a.cxx)
    files = sorted(f.name for f in (VK / "lsfg").iterdir())
    spdx = [f for f in files if f.endswith((".cpp", ".h")) and "SPDX-License-Identifier: GPL-3.0-or-later" not in
            (VK / "lsfg" / f).read_text(encoding="utf-8")]
    build = (ROOT / "ps5" / "build.py").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "PS5.md").read_text(encoding="utf-8")
    checked([
        ("PROVENANCE.md" in files and "github.com/Swordpdf/PS5SX2" in (VK / "lsfg" / "PROVENANCE.md").read_text(encoding="utf-8"),
         "gpu/vk/lsfg has no PROVENANCE.md naming where it came from"),
        (not spdx, "files of gpu/vk/lsfg without their SPDX line: " + ", ".join(spdx)),
        ("LONGSHOT_LSFG" in build, "ps5/build.py does not compile gpu/vk/lsfg"),
        ("if (!fg_by::wants_lossless(fg.by)) return false;" in framegen, "Lossless Scaling's chain is not asked for by the row"),
        ("framegen_lossless_file() ? fg_by::kMost : fg_by::kMihawk" in menu,
         "without a Lossless.dll the row still offers Lossless Scaling"),
        ("Lossless.dll" in docs and "PS5SX2" in docs and "lsfg-vk" in docs, "docs/PS5.md does not say where the file goes and whose the code is"),
    ], "the console's Lossless Scaling: offered with the file there, one generator at a time, its origin recorded")


if __name__ == "__main__":
    main()
