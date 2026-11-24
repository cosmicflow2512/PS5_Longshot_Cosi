"""Every function gpu/vk/vk_fsr4.h declares has a definition in vk_fsr4.cpp's __PROSPERO__ block, the only part the PS5
compiles: v3.2.0 added fsr4_model_env, fsr4_lite_available, fsr4_set_model and fsr4_prepare_shaders to the header and the
PC block, and v3.2.0-ps5.2's link stopped on them (undefined symbol, referenced by menu/upscaler.cpp, vk_menu.cpp and
vk_main.cpp)."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VK = os.path.join(ROOT, "gpu", "vk")
with open(os.path.join(VK, "vk_fsr4.h"), encoding="utf-8") as f:
    header = f.read()
with open(os.path.join(VK, "vk_fsr4.cpp"), encoding="utf-8") as f:
    src = f.read()

names = re.findall(r"^[A-Za-z_][\w:<>* ]*?\b(fsr4_\w+)\(", header, re.M)
ps5 = src.split("#ifdef __PROSPERO__", 1)[1].split("\n#else", 1)[0]
missing = [n for n in names if not re.search(r"^[A-Za-z_][\w:<>* ]*?\b%s\([^;]*\)\s*\{" % n, ps5, re.M)]
ok = bool(names) and not missing
print("ps5_fsr4_symbols: %d declared%s" % (len(names), "" if ok else "; not defined for the PS5: " + ", ".join(missing)))
print("ps5_fsr4_symbols: " + ("OK" if ok else "FAILED"))
sys.exit(0 if ok else 1)
