"""The .nup romfs answers the doubled separator the game asks its voice streams with.

The game asks its voices as content:/Voice/Resource//Stream/<name>.bwav (the same doubled
separator that dropped them on Windows long paths, MagicBeanDev/Longshot issues #1298 and
#982); nup_romfs_find hashes the whole path string, and the table it looks in was walked
from canonical single-slash paths, so on main every such request answers "not found" and
the dubbing is silent on the console. This authors a synthetic package (no game data) with
one Voice/Resource/Stream file, compiles the real reader, and checks both paths find it.
"""
import argparse
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

RUN_ALL_ARGS = ["--cc", "gcc"]

ROOT = Path(__file__).resolve().parents[1]


def synth_nup(path):
    """One title, its romfs: root/Voice/Resource/Stream/x.bwav, all names plain."""
    names = [b"Voice", b"Resource", b"Stream", b"x.bwav"]
    offs, strings = [], b""
    for n in names:
        offs.append(len(strings))
        strings += n
    nd, nf = 4, 1                       # dirs: 0=root 1=Voice 2=Resource 3=Stream; file 0 = x.bwav
    kids = [1, 2, 3, nd]                 # each folder holds the next one; Stream holds the file
    dirs_at = 0x80 + 0x30 + 0x40 * 1
    files_at = dirs_at + 24 * nd
    kids_at = files_at + 80 * nf
    strings_at = kids_at + 4 * len(kids)
    blob = bytearray(strings_at + len(strings))
    blob[0:4] = b"NUP\x01"
    blob[0x80:0x84] = b"TOC\x01"
    struct.pack_into("<I", blob, 0x84, 1)                 # one title
    struct.pack_into("<Q", blob, 0x88, nd)
    struct.pack_into("<Q", blob, 0x90, nf)
    struct.pack_into("<Q", blob, 0x98, strings_at - 0x80)
    struct.pack_into("<Q", blob, 0xA0, len(strings))
    struct.pack_into("<I", blob, 0xB0 + 16, 0)            # its romfs root: dir 0
    struct.pack_into("<I", blob, 0xB0 + 20, 131072)       # its version: the newest
    for d in range(nd):
        rec = dirs_at + 24 * d
        name_off, name_len = (0, 0) if d == 0 else (offs[d - 1], len(names[d - 1]))
        struct.pack_into("<IIII", blob, rec, name_off, name_len, d, 1)   # first, count
    frec = files_at
    struct.pack_into("<II", blob, frec, offs[3], len(names[3]))
    struct.pack_into("<QQQ", blob, frec + 8, 6, len(blob), 6)            # size, offset, stored
    blob[frec + 64] = 0                                    # codec: plain
    for k, child in enumerate(kids):
        struct.pack_into("<I", blob, kids_at + 4 * k, child)
    blob[strings_at:] = strings
    path.write_bytes(bytes(blob))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', default='gcc')
    parser.add_argument('--source', type=Path, default=ROOT / 'host/ps5/nup_romfs.c')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="nup-double-slash-") as tmp:
        folder = Path(tmp)
        package = folder / "fixture.nup"
        synth_nup(package)
        exe = folder / "fixture.exe"
        build = subprocess.run([args.cc, "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                                 str(ROOT / "tests/nup_double_slash_test.c"), "-lzstd", "-o", str(exe)],
                                capture_output=True, text=True)
        if build.returncode != 0:
            if "zstd.h" in build.stderr:
                print("SKIP: no zstd headers on this PC: " + build.stderr.splitlines()[0])
                return
            sys.exit("compile failed:\n" + build.stderr)
        run = subprocess.run([str(exe), str(package)], text=True, capture_output=True)
        sys.stdout.write(run.stdout)
        if run.returncode != 0:
            sys.exit("FAIL (exit %d): %s" % (run.returncode, run.stderr.strip()))
        print("PASS: the doubled separator finds the file")


if __name__ == "__main__":
    main()
