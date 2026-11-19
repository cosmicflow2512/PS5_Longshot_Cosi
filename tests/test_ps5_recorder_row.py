"""On the console the Threaded rendering row's On is the recorder thread alone, and Auto is Off.

The render thread hung a base PS5 (its buffer pools have no mirrors: a replay behind the game reads memory the game has
moved on from), while the recorder thread alone ran (#40). Source checks, no game and no compiler.

python -I -B tests/test_ps5_recorder_row.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    replay = (ROOT / "gpu" / "vk" / "vk_replay.cpp").read_text(encoding="utf-8")
    menu = (ROOT / "gpu" / "vk" / "vk_menu.cpp").read_text(encoding="utf-8")
    host = (ROOT / "host" / "hos_main.c").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "PS5.md").read_text(encoding="utf-8")
    mode = replay[replay.index("int render_thread_mode() {"):]
    mode = mode[:mode.index("\n}\n")]
    checks = [
        # (longshot v3: the row's answer is threaded::Choice, a half for each thread; on the console On keeps the recorder's
        # half alone and Auto is Off)
        (bool(re.search(r"#ifdef __PROSPERO__\n(?:\s*//[^\n]*\n)*\s*if \(threaded::auto_picked\(c\)\) \{\n"
                        r"\s*c = threaded::Choice\{false, false, threaded::Why::AutoUnsafe\};", menu)),
         "Auto is not Off on the console"),
        (bool(re.search(r"#ifdef __PROSPERO__\n(?:.*\n){0,12}?\s*if \(c\.why == threaded::Why::On\) c\.render_thread = false;", menu)),
         "the console's row can start the render thread"),
        ("menu_render_thread()" in mode, "render_thread_mode does not read the row's render thread half"),
        ("rec::g_setting_thread = menu_recorder_thread" in replay, "the row's On does not reach the recorder"),
        ('{"RX_VK_DESC_POOL_DIV", "8"}' in host, "the console's descriptor pools are no longer an eighth"),
        ("RX_VK_RECORDER" not in host, "hos_main.c sets a recorder switch on the console"),
        ("## Threaded rendering" in docs and "recorder thread alone" in docs, "docs/PS5.md does not say what On is there"),
    ]
    bad = [why for ok, why in checks if not ok]
    if bad:
        raise SystemExit("FAIL: " + "; ".join(bad))
    print("PASS: the console's Threaded rendering: On is the recorder thread alone, Auto is Off")


if __name__ == "__main__":
    main()
