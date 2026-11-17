// (PS5) The Frame generation by row on the console: which of its generators makes a set's frames. Nothing of Vulkan here:
// tests/test_ps5_framegen_by.py compiles it alone.
#pragma once

namespace mkwvk::fg_by {

// (the row's values, the options file's frame_generation_by. 0 and 1 are the PC's two. The console adds its own and its
// row has no Auto: beside the Frame generation row's a player read the two as one. A file's 0 is kDefault there)
enum : int { kAuto = 0, kBuiltIn = 1, kFsr3 = 2, kMihawk = 3 };
#ifdef __PROSPERO__
inline constexpr int kLeast = kBuiltIn, kMost = kMihawk, kDefault = kMihawk;
#else
inline constexpr int kLeast = kAuto, kMost = kBuiltIn, kDefault = kAuto;
#endif
// (2 is FSR 3.1 FG's on this row in upstream Longshot since its 983d607b (2026-11-17), which this tree does not have yet.
// The console's own values come after it, so a file written now means the same once the port has upstream's row. Until
// then nothing makes frames at 2: the console's row steps over it, and a 2 from a file or a variable is kDefault)
/// The row's value a step from its neighbour lands on: `by` itself, or the next one that way when it is kFsr3
constexpr int step_over(int by, int dir) { return by == kFsr3 ? by + (dir > 0 ? 1 : -1) : by; }
/// A number from a file or a variable, as a value of this build's row
constexpr int known(int by) { return by == kFsr3 ? kDefault : by; }

constexpr const char* name(int by) {
    return by == kBuiltIn ? "Built-in" : by == kMihawk ? "MihawkGen" : "Auto";
}

/// PS5_MihawkGen's network is asked for: at its own value, and at the PC's Auto (a console's file from before the
/// row had its values). At the renderer's own it is not loaded: its images are the game's memory then
constexpr bool wants_network(int by) { return by == kAuto || by == kMihawk; }

}   // namespace mkwvk::fg_by
