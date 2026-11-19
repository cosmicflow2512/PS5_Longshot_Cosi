"""Check that vk_framegen.cpp drains the recorder ring (B_DIRECT) before direct driver recording into cmd.

With RX_VK_RECORDER=thread, vk_work.h calls (such as vkCmdPipelineBarrier2) enqueue packets for the recorder
thread while external generators (PS5_MihawkGen's fg_record_generate) record directly into the same VkCommandBuffer
through loaded driver pointers. Without rec::boundary(B_DIRECT), both threads race on the command buffer and
trigger GPU_FAULT_BAD_COMMAND_ASYNC (0xa0d0c006) on PS5.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_function(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth, at = 1, brace + 1
    while depth:
        if source[at] == "{":
            depth += 1
        elif source[at] == "}":
            depth -= 1
        at += 1
    return source[start:at]


def main() -> int:
    src = (ROOT / "gpu/vk/vk_framegen.cpp").read_text(encoding="utf-8")
    body = extract_function(src, "bool neural_frames(")
    layout_pos = body.index("neural_layout(")
    boundary_pos = body.index("::mkwvk::rec::boundary(::mkwvk::rec::B_DIRECT)")
    gen_pos = body.index("fg_record_generate(")
    if not (layout_pos < boundary_pos < gen_pos):
        raise SystemExit(
            f"FAIL: B_DIRECT boundary order wrong in neural_frames "
            f"(layout={layout_pos}, boundary={boundary_pos}, gen={gen_pos})"
        )
    print("ok: vk_framegen.cpp neural_frames drains recorder (B_DIRECT) before fg_record_generate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
