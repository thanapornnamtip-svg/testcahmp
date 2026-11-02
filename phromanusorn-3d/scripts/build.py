"""สร้างโมเดล 3D โรงเรียนพรหมานุสรณ์จังหวัดเพชรบุรี ทั้งฉาก แล้วบันทึก/ส่งออกไฟล์

รัน (ต้องมี: pip install bpy==5.2.3):
    python3 scripts/textures.py      # สร้างเท็กซ์เจอร์และป้ายภาษาไทย
    python3 scripts/build.py         # สร้างฉาก -> output/*.blend, *.glb, *.fbx, *.obj
    python3 scripts/render.py        # เรนเดอร์ภาพจากกล้องทุกตัว -> renders/*.png
"""
import math
import os
import shutil
import subprocess
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402

import campus as SITE  # noqa: E402
import materials  # noqa: E402
import scene_setup as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

CAMERAS = [
    # name, location, target, lens, ortho_scale
    ("CAM_01_Overview", (340, -300, 200), (-10, 35, 8), 34, None),
    ("CAM_02_Gate", (166.6, -44, 1.7), (147, -3, 5.0), 24, None),
    ("CAM_03_Assembly", (136, 30, 15), (86, -8, 5), 28, None),
    ("CAM_04_Field", (-52, -178, 52), (-52, 45, 4), 28, None),
    ("CAM_05_KhaoWang", (30, -30, 22), (-40, 395, 62), 30, None),
    ("CAM_06_Shrine", (149, 32, 2.6), (140.5, 21.5, 3.2), 26, None),
    ("CAM_07_Plan", (0, 0, 900), (0, 0, 0), 50, 335),
    ("CAM_08_Gym", (75, -30, 30), (5, -86, 4), 28, None),
]


def web_glb(src, dst, compress=True):
    """ทำ .glb สำหรับเว็บ/มือถือด้วย gltfpack (meshopt) ถ้ามีในเครื่อง"""
    exe = os.environ.get("GLTFPACK") or shutil.which("gltfpack")
    cmd = [exe] if exe else ["npx", "--yes", "gltfpack@1.3.0"]
    flags = (["-cc", "-vpf", "-vtf"] if compress else ["-vp", "16", "-vt", "14"]) + ["-kn"]
    try:
        subprocess.run(cmd + ["-i", src, "-o", dst] + flags, check=True, timeout=900)
        print("saved", dst, f"{os.path.getsize(dst) / 1e6:.1f} MB")
    except Exception as e:  # ไม่มี gltfpack ก็ข้ามไป
        print("skip web glb:", e)


def stats():
    tris = 0
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            me = ob.data
            me.calc_loop_triangles()
            tris += len(me.loop_triangles)
    return tris


def main():
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "Prommanusorn_Phetchaburi"
    sc.unit_settings.system = "METRIC"
    materials.define_all()
    SITE.build_all()
    print(f"geometry built in {time.time() - t0:.1f}s, triangles = {stats():,}")

    S.setup_world()
    S.setup_sun()
    S.setup_render()
    cams = bpy.data.collections.new("Cameras")
    sc.collection.children.link(cams)
    for name, loc, tgt, lens, ortho in CAMERAS:
        S.add_camera(name, loc, tgt, lens, ortho, coll=cams)
    sc.camera = bpy.data.objects["CAM_01_Overview"]

    # ข้อมูลอ้างอิงในไฟล์
    sc["school"] = "โรงเรียนพรหมานุสรณ์จังหวัดเพชรบุรี (Prommanusorn Phetchaburi School)"
    sc["location"] = "278 ถนนบันไดอิฐ ต.คลองกระแชง อ.เมืองเพชรบุรี จ.เพชรบุรี 76000 (13.10408 N, 99.93717 E)"
    sc["note"] = "ตำแหน่งอาคารเป็นการจัดวางโดยประมาณ หน่วย: เมตร, +Y = ทิศเหนือ"

    # glTF (.glb) ฉบับเต็ม
    glb = os.path.join(OUT, "phromanusorn.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_cameras=False, export_lights=False,
                              export_apply=True, export_yup=True, export_image_format="AUTO")
    print("saved", glb, f"{os.path.getsize(glb) / 1e6:.1f} MB")
    web_glb(glb, os.path.join(OUT, "phromanusorn_web.glb"), compress=True)
    # ฉบับเบา (ไม่บีบอัด ไม่มีบ้าน/ต้นไม้/พื้นรอบนอก) สำรองไว้สำหรับเบราว์เซอร์ที่ถอดรหัส meshopt ไม่ได้
    for name in ("Houses", "Trees_Around", "Ground_Far", "Ground_Town", "DistantMountains"):
        bpy.data.objects[name].hide_set(True)
    lite_raw = os.path.join(OUT, "_lite_raw.glb")
    bpy.ops.export_scene.gltf(filepath=lite_raw, export_format="GLB", export_cameras=False, export_lights=False,
                              export_apply=True, export_yup=True, export_image_format="AUTO", use_visible=True)
    for ob in bpy.data.objects:
        ob.hide_set(False)
    web_glb(lite_raw, os.path.join(OUT, "phromanusorn_lite.glb"), compress=False)
    os.remove(lite_raw)

    # FBX (ฝังเท็กซ์เจอร์)
    fbx = os.path.join(OUT, "phromanusorn.fbx")
    bpy.ops.export_scene.fbx(filepath=fbx, path_mode="COPY", embed_textures=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y")
    print("saved", fbx, f"{os.path.getsize(fbx) / 1e6:.1f} MB")

    # OBJ + MTL + textures (zip)
    objdir = os.path.join(OUT, "obj")
    os.makedirs(objdir, exist_ok=True)
    objp = os.path.join(objdir, "phromanusorn.obj")
    bpy.ops.wm.obj_export(filepath=objp, path_mode="COPY", export_materials=True, export_triangulated_mesh=False,
                          forward_axis="NEGATIVE_Z", up_axis="Y")
    zp = os.path.join(OUT, "phromanusorn_obj.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(objdir)):
            z.write(os.path.join(objdir, fn), fn)
    shutil.rmtree(objdir)
    print("saved", zp, f"{os.path.getsize(zp) / 1e6:.1f} MB")

    # บันทึก .blend (ฝังรูปทั้งหมดในไฟล์ เปิดได้ทันทีโดยไม่ต้องมีโฟลเดอร์ textures)
    blend = os.path.join(OUT, "phromanusorn.blend")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    print("saved", blend, f"{os.path.getsize(blend) / 1e6:.1f} MB")
    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
