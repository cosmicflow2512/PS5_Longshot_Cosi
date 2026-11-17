"""The console's Frame generation by row: Built-in FG and MihawkGen.

On the console the row had the PC's two values, Auto and Built-in FG: PS5_MihawkGen's network could not be turned off or
named in the menu, and at the Frame generation row's Auto the frames it made were noted as no one's, so the row and the FPS
counter named no generator. gpu/vk/fg_by.h has the row's values and which of them asks for the network; it is compiled here
alone, for the PC and for the console.

python -I -B tests/test_ps5_framegen_by.py [--cxx g++]
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
static_assert(kAuto == 0 && kBuiltIn == 1, "the PC's two values keep their numbers: options files have them");
#ifdef __PROSPERO__
static_assert(kLeast == kBuiltIn && kMost >= kMihawk && kDefault == kMihawk, "the console's row: no Auto, the network by default");
static_assert(kFsr3 == 2 && kMihawk == 3, "the console's values come after upstream's FSR 3.1 FG, which is 2 there");
static_assert(step_over(kBuiltIn + 1, 1) == kMihawk && step_over(kMihawk - 1, -1) == kBuiltIn && step_over(kMihawk, 1) == kMihawk,
              "the row steps over the number that is not a value here");
static_assert(known(kFsr3) == kDefault && known(kBuiltIn) == kBuiltIn && known(kMihawk) == kMihawk, "a file's 2 is the default");
#else
static_assert(kLeast == kAuto && kMost == kBuiltIn && kDefault == kAuto, "the PC's row is as it was");
#endif
int main() { return 0; }
""", a.cxx)
    checked([
        ("r.lo = fg_by::kLeast" in menu, "the menu's row is not the console's values"),
        ("v = fg_by::step_over(v, dir)" in menu, "the menu's row stops at 2, which is not a value on the console"),
        ('"MihawkGen FG"' in menu, "the console's network has no name in the menu"),
        ("fg.by == by" in framegen, "a change of the row does not make the generators again"),
        ("fg_by::wants_network(fg.by" in framegen, "the network is loaded whatever the row names"),
        ("note_maker(flow ? FgMaker::BuiltIn : who)" in framegen, "Auto's frames by the console's generator are not noted"),
        ("atoi(eq + 1) < fg_by::kLeast) opts.framegen_by = fg_by::kDefault" in menu,
         "a file's Auto is not the network's on the console"),
    ], "the console's Frame generation by row: its values, the network only where asked, its frames noted")


if __name__ == "__main__":
    main()
