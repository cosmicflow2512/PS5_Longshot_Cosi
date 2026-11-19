/* PS5: the console's own language (Settings > System > Language), as the game's language when the player has not picked one
   (host/nn_applet.c desired_language, gpu/vk/vk_menu_i18n.cpp). */
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

int sceSystemServiceParamGetInt(int32_t param_id, int32_t *value);
#define SYSTEM_PARAM_LANG 1   /* (SCE_SYSTEM_SERVICE_PARAM_ID_LANG) */

/* The game's code for the console's language id (the PS4/PS5 SCE_SYSTEM_PARAM_LANG_* numbers); NULL for one the game does
   not have (Finnish, Swedish, Danish, Norwegian, Turkish, Arabic, Czech, Hungarian, Greek, Romanian, Thai, Vietnamese,
   Indonesian, Ukrainian, ...): English then. Portuguese (Portugal) is given Portuguese (Brazil), the game's only Portuguese,
   as the PC builder's system_language does (nx2/make_game.py) */
static const char *const codes[] = {
    [0] = "ja",      [1] = "en-US",  [2] = "fr",      [3] = "es",     [4] = "de",      [5] = "it",
    [6] = "nl",      [7] = "pt-BR",  [8] = "ru",      [9] = "ko",     [10] = "zh-Hant", [11] = "zh-Hans",
    [16] = "pl",     [17] = "pt-BR", [18] = "en-GB",  [20] = "es-419", [22] = "fr-CA",
};

/* The game's code for the console's language, or NULL (English) when the game does not have it or it cannot be read; *id: the
   console's number for it (-1 when unread) */
const char *hos_ps5_console_language(int *id) {
    int32_t lang = -1;
    if (sceSystemServiceParamGetInt(SYSTEM_PARAM_LANG, &lang) < 0) lang = -1;
    /* (HOS_PS5_LANG_ID=<number>: a test run's console language, to see another one's answer without changing the console's) */
    const char *test = getenv("HOS_PS5_LANG_ID");
    if (test && *test) lang = atoi(test);
    if (id) *id = lang;
    if (lang < 0 || (size_t)lang >= sizeof codes / sizeof *codes) return NULL;
    return codes[lang];
}
