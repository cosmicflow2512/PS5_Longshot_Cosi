"""The giants' pieces on the PS5 go through f_'s loop, never preserve_none: the PS5's Clang (23) reports
__has_attribute(preserve_none) but refuses the convention for x86_64-sie-ps5 ("calling convention is not supported for this
target"), so v3.2.0-ps5.1's builder stopped at 79 of 94 chunks. nx2/split_giants.py DIRECT_IF leaves __PROSPERO__ out."""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "nx2"))
import split_giants as SG  # noqa: E402

fails = []


def check(ok, what):
    if not ok:
        fails.append(what)
        print("FAIL: " + what)


check("!defined(__PROSPERO__)" in SG.DIRECT_IF, "split_giants.py DIRECT_IF leaves the PS5 out: %s" % SG.DIRECT_IF)
cc = shutil.which("clang")
if cc:
    for target, want in (("x86_64-sie-ps5", "TRAMPOLINE"),):
        r = subprocess.run([cc, "-target", target, "-E", "-P", "-x", "c", "-"],
                           input=SG.DIRECT_IF + "\nDIRECT\n#else\nTRAMPOLINE\n#endif\n", capture_output=True, text=True)
        check(r.returncode == 0 and want in r.stdout.split(), "%s for %s: %s %s" % (want, target, r.stdout, r.stderr[-300:]))
print("ps5_split_direct: " + ("FAILED" if fails else "OK"))
sys.exit(1 if fails else 0)
