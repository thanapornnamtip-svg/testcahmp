"""เรนเดอร์ภาพจากกล้องทุกตัวในไฟล์ .blend -> renders/*.jpg

รัน:  python3 scripts/render.py [--samples 64] [--scale 100] [ชื่อกล้อง ...]
"""
import argparse
import os
import sys
import time

import bpy
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(ROOT, "output", "phromanusorn.blend")
OUT = os.path.join(ROOT, "renders")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("cams", nargs="*")
    a = ap.parse_args(argv)
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    sc = bpy.context.scene
    sc.cycles.samples = a.samples
    sc.render.resolution_percentage = a.scale
    cams = sorted(o.name for o in bpy.data.objects if o.type == "CAMERA")
    if a.cams:
        cams = [c for c in cams if c in a.cams]
    for name in cams:
        sc.camera = bpy.data.objects[name]
        if name.endswith("Plan"):
            sc.render.resolution_x, sc.render.resolution_y = 1600, 1150
        else:
            sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
        png = os.path.join(OUT, name + ".png")
        sc.render.filepath = png
        t = time.time()
        bpy.ops.render.render(write_still=True)
        jpg = os.path.join(OUT, name.replace("CAM_", "") + ".jpg")
        Image.open(png).convert("RGB").save(jpg, quality=90, optimize=True)
        os.remove(png)
        print(f"{name}: {time.time() - t:.0f}s -> {jpg}", flush=True)


if __name__ == "__main__":
    main()
