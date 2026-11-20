/* PS5: what an earlier Longshot title ID left on the console, taken over at the first start under this one.
 *
 * Longshot was PPSA99025 (and PPSA99198 in cosmicflow2512's fork) until it took an ID of its own (ps5/sce_sys/param.json): PPSA99025 is also Need for Speed:
 * Underground's (reUndr), and two titles of one ID install over each other (issue #29). A player who installs the new title
 * keeps the old folder, /data/homebrew/PPSA99025, beside it. The first start under the new ID, before anything of the game
 * opens a file:
 *  - copies the player's saves (user/) and settings (longshot_options.ini, language.txt) from the old folder, each file only
 *    where the new folder has none, so nothing the new title has is overwritten and the old folder keeps its own;
 *  - moves the old folder's caches (cache/, the translated shaders; radv-shader-cache/, the driver's pipelines: ~2.3 GB and
 *    a 20-minute first start) into the new one, by a rename on the same disk, where the new folder has none yet; so too the
 *    files the player put there (lossless/, their Lossless.dll; fsr4/, AMD FSR 4's assets);
 *  - leaves /app0/migrated.txt, so it is done once, and moved_to_<new ID>.txt in the old folder; says so on the screen.
 * Only an old folder that is Longshot's (its param.json's contentId names PS5LONGSHOT) is touched: reUndr's PPSA99025 never.
 * HOS_PS5_NO_MIGRATE=1: nothing taken over. */
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

/* (this fork's PPSA99198, v3.0.0-ps5.x up to ps5.6, first: a console that had both keeps the newer's saves and caches) */
static const char *const kOldIds[] = {"PPSA99198", "PPSA99025"};
#define HOMEBREW "/data/homebrew/"

/* a param.json's "titleId" value, into out (empty: none) */
static void title_id_of(const char *param, char *out, size_t n) {
    out[0] = 0;
    FILE *f = fopen(param, "rb");
    if (!f) return;
    char buf[8192];
    const size_t got = fread(buf, 1, sizeof buf - 1, f);
    fclose(f);
    buf[got] = 0;
    const char *at = strstr(buf, "\"titleId\"");
    if (!at || !(at = strchr(at + 9, '"'))) return;
    at++;
    size_t i = 0;
    while (at[i] && at[i] != '"' && i + 1 < n) out[i] = at[i], i++;
    out[i] = 0;
}
static int is_longshot(const char *folder) {
    char p[512];
    snprintf(p, sizeof p, "%s/sce_sys/param.json", folder);
    FILE *f = fopen(p, "rb");
    if (!f) return 0;
    char buf[8192];
    const size_t got = fread(buf, 1, sizeof buf - 1, f);
    fclose(f);
    buf[got] = 0;
    return strstr(buf, "PS5LONGSHOT") != NULL;
}
static int exists(const char *p) {
    struct stat st;
    return stat(p, &st) == 0;
}
/* src to dst, a file, written whole (one write: the console's file calls cost ~60 ms each); 0 when done */
static int copy_file(const char *src, const char *dst) {
    FILE *in = fopen(src, "rb");
    if (!in) return -1;
    fseek(in, 0, SEEK_END);
    const long size = ftell(in);
    fseek(in, 0, SEEK_SET);
    char *data = size > 0 ? malloc((size_t)size) : NULL;
    int ok = size >= 0 && (size == 0 || (data && fread(data, 1, (size_t)size, in) == (size_t)size));
    fclose(in);
    if (ok) {
        char tmp[600];
        snprintf(tmp, sizeof tmp, "%s.migrating", dst);
        FILE *out = fopen(tmp, "wb");
        ok = out && (size == 0 || fwrite(data, 1, (size_t)size, out) == (size_t)size);
        if (out) ok = (fclose(out) == 0) && ok;
        ok = ok && rename(tmp, dst) == 0;
        if (!ok) unlink(tmp);
    }
    free(data);
    return ok ? 0 : -1;
}
/* every file under src that dst lacks, copied; folders made as needed. *copied, *kept: how many */
static void copy_missing(const char *src, const char *dst, int *copied, int *kept) {
    DIR *d = opendir(src);
    if (!d) return;
    mkdir(dst, 0777);
    for (struct dirent *e; (e = readdir(d));) {
        if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, "..")) continue;
        char s[600], t[600];
        snprintf(s, sizeof s, "%s/%s", src, e->d_name);
        snprintf(t, sizeof t, "%s/%s", dst, e->d_name);
        struct stat st;
        if (stat(s, &st) != 0) continue;
        if (S_ISDIR(st.st_mode)) {
            copy_missing(s, t, copied, kept);
        } else if (exists(t)) {
            (*kept)++;
        } else if (copy_file(s, t) == 0) {
            (*copied)++;
        } else {
            fprintf(stderr, "[ps5] migrate: %s not copied (%s)\n", s, strerror(errno));
        }
    }
    closedir(d);
}

void hos_ps5_notify(const char *text);   /* (host/ps5/win32_ps5.c) */

void hos_ps5_migrate_old_id(void) {
    const char *off = getenv("HOS_PS5_NO_MIGRATE");
    if ((off && *off == '1') || exists("/app0/migrated.txt")) return;
    char own[32];
    title_id_of("/app0/sce_sys/param.json", own, sizeof own);
    if (!own[0]) return;
    char here[128];   /* (this title's folder as the disk has it: a rename from the old folder stays on that disk, /app0 is a
                         mount of it) */
    snprintf(here, sizeof here, HOMEBREW "%s", own);
    for (size_t k = 0; k < sizeof kOldIds / sizeof *kOldIds; k++) {
        if (!strcmp(own, kOldIds[k])) continue;
        char old[128];
        snprintf(old, sizeof old, HOMEBREW "%s", kOldIds[k]);
        if (!exists(old) || !is_longshot(old)) continue;
        int copied = 0, kept = 0, moved = 0;
        char s[256], t[256];
        snprintf(s, sizeof s, "%s/user", old);
        copy_missing(s, "/app0/user", &copied, &kept);
        for (const char *const *n = (const char *const[]){"longshot_options.ini", "language.txt", NULL}; *n; n++) {
            snprintf(s, sizeof s, "%s/%s", old, *n);
            snprintf(t, sizeof t, "/app0/%s", *n);
            if (!exists(s)) continue;
            if (exists(t)) kept++;
            else if (copy_file(s, t) == 0) copied++;
        }
        if (exists(here)) {
            for (const char *const *n = (const char *const[]){"cache", "radv-shader-cache", "lossless", "fsr4", NULL}; *n; n++) {
                snprintf(s, sizeof s, "%s/%s", old, *n);
                snprintf(t, sizeof t, "%s/%s", here, *n);
                if (!exists(s) || exists(t)) continue;
                if (rename(s, t) == 0) moved++;
                else fprintf(stderr, "[ps5] migrate: %s not moved (%s)\n", s, strerror(errno));
            }
        }
        fprintf(stderr, "[ps5] migrate: from %s: %d files copied (saves and settings), %d already here and kept, %d cache folders "
                "and player folders moved (HOS_PS5_NO_MIGRATE=1: none)\n", old, copied, kept, moved);
        snprintf(t, sizeof t, "%s/moved_to_%s.txt", old, own);
        FILE *f = fopen(t, "w");
        if (f) {
            fprintf(f, "Longshot is %s now: its saves and settings were copied to /data/homebrew/%s and its caches moved there.\n"
                       "This folder can be deleted.\n", own, own);
            fclose(f);
        }
        f = fopen("/app0/migrated.txt", "w");
        if (f) {
            fprintf(f, "%s: %d copied, %d kept, %d cache folders moved\n", old, copied, kept, moved);
            fclose(f);
        }
        if (copied || moved) {
            char note[400];
            snprintf(note, sizeof note, "Longshot has a new title ID (%s). Your saves and settings were brought over from the old "
                     "one (%s); its folder can be deleted.", own, kOldIds[k]);
            hos_ps5_notify(note);
        }
        return;
    }
    FILE *f = fopen("/app0/migrated.txt", "w");   /* (nothing to take over: not looked for again) */
    if (f) {
        fputs("nothing to take over\n", f);
        fclose(f);
    }
}
