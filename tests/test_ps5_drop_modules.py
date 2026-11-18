"""The console lets go of the shader modules of the programs prepared at start (gpu/vk/vk_draw.cpp pipeline_cache_play).

The rule is the one for a PC with 20 GB of RAM or less (linux_pressure.h), and it was compiled for Linux alone: on the
console the modules of the 2,183 programs read from the program cache held about 300 MiB of the heap for the session.

python -I -B tests/test_ps5_drop_modules.py [--cxx g++]
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

RUN_ALL_ARGS = ["--cxx", "{cxx}"]

ROOT = Path(__file__).resolve().parents[1]

FIXTURE = r"""#include <cstdint>
#include <cstring>
#include "linux_pressure.h"
static_assert((16ull << 30) <= linux_pressure::kModuleDropMaxRam, "the console's 16 GB are under the rule's line");
int main() {}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cxx", default="g++")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "drop.cpp"
        src.write_text(FIXTURE, encoding="utf-8")
        subprocess.run([args.cxx, "-std=c++20", "-fsyntax-only", "-I", str(ROOT / "gpu" / "vk"), str(src)], check=True)
    draw = (ROOT / "gpu" / "vk" / "vk_draw.cpp").read_text(encoding="utf-8")
    at = draw.index("void pipeline_cache_play() {")
    body = draw[at:draw.index("\n}\n", at)]
    checks = [
        ("#if defined(__linux__) || defined(__PROSPERO__)" in body, "the modules' release is not compiled for the console"),
        ("#ifdef __PROSPERO__" in body and "total_bytes = 16ull << 30;" in body, "the console does not say how much memory it has"),
        (0 <= body.find("total_bytes = 16ull << 30;") < body.find("linux_pressure::should_drop_modules("),
         "the console's memory is not given before the rule is asked"),
        ("program_cache_drop_modules()" in body, "the modules are not let go"),
        ("#if defined(__linux__) || defined(__PROSPERO__)\n        if (!p.compute && wanted_variants.count(mix(p.key, p.variant))) "
         "program_cache_note_built(p);" in draw, "the console does not note the programs whose pipelines were prepared"),
    ]
    bad = [why for ok, why in checks if not ok]
    if bad:
        raise SystemExit("FAIL: " + "; ".join(bad))
    print("PASS: the console lets go of the prepared programs' shader modules when play begins")


if __name__ == "__main__":
    main()
