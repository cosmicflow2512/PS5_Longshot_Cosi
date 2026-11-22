/* PS5: <malloc.h> for the code that still asks for it (third_party/reshade_fx's effect_symbol_table.cpp, for alloca).
   The payload SDK's own stops the compile ("replaced by <stdlib.h>", as FreeBSD's); ps5/build.py puts this folder
   before the SDK's for ReShade FX's files alone, so third_party/ stays as its PROVENANCE.md has it. */
#pragma once
#include <stdlib.h>
#ifndef alloca
#define alloca(size) __builtin_alloca(size)
#endif
