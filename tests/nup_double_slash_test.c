/* The real .nup reader (host/ps5/nup_romfs.c) against a synthetic package: the doubled
   separator the game asks its voice streams with must find the same file the canonical
   single-slash path does. No game data: the package is authored here, with one file. */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <stdio.h>
#include "../host/ps5/nup_romfs.c"

static void expect(const char *path, int64_t *out) {
    *out = nup_romfs_find(path, NULL, NULL);
    printf("%s -> %lld\n", path, (long long)*out);
}

int main(int argc, char **argv) {
    if (argc < 2) { puts("usage: nup_double_slash_test <package.nup>"); return 2; }
    if (!nup_romfs_open(argv[1])) { puts("open: the package did not load"); return 2; }
    int64_t canonical = -1, doubled = -1;
    expect("/nup/romfs/Voice/Resource/Stream/x.bwav", &canonical);
    if (canonical < 0) { puts("the canonical path was not found: the fixture is wrong"); return 3; }
    expect("/nup/romfs/Voice/Resource//Stream/x.bwav", &doubled);
    if (doubled != canonical) { puts("the doubled separator was not found: the voices stay silent"); return 1; }
    puts("ok: the doubled separator finds the file");
    return 0;
}
