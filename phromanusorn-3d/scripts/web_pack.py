"""แปลง .glb เป็น glTF JSON + ข้อมูล base64 แบ่งเป็นไฟล์ .txt สำหรับหน้าเว็บ (web/index.html)

โฮสต์บางแห่งไม่ให้บริการไฟล์ .glb จึงแยกเป็นไฟล์ข้อความที่เบราว์เซอร์โหลดได้แน่นอน
แล้วให้หน้าเว็บประกอบกลับเป็น GLB ในหน่วยความจำ

รัน:  python3 scripts/web_pack.py      -> web/data/school.gltf.json, school.bin.N.txt, school-lite...
"""
import base64
import json
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "web", "data")
PART = 12_000_000  # ตัวอักษรต่อไฟล์ (หาร 4 ลงตัว เพื่อถอดรหัสแต่ละส่วนแยกกันได้)


def pack(glb_path, name):
    data = open(glb_path, "rb").read()
    magic, _ver, length = struct.unpack_from("<III", data, 0)
    assert magic == 0x46546C67, "not a GLB"
    off, js, bin_ = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        off += 8
        chunk = data[off:off + clen]
        off += clen
        if ctype == 0x4E4F534A:
            js = chunk
        elif ctype == 0x004E4942:
            bin_ = chunk
    gltf = json.loads(js.decode("utf-8").rstrip(" \x00"))
    b64 = base64.b64encode(bin_).decode("ascii")
    parts = [b64[i:i + PART] for i in range(0, len(b64), PART)]
    gltf.setdefault("extras", {})["webParts"] = {"count": len(parts), "binLength": len(bin_), "chars": len(b64)}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".gltf.json"), "w") as f:
        json.dump(gltf, f, separators=(",", ":"), ensure_ascii=False)
    for i, p in enumerate(parts, 1):
        with open(os.path.join(OUT, f"{name}.bin.{i}.txt"), "w") as f:
            f.write(p)
    print(f"{name}: json + {len(parts)} part(s), {len(b64) / 1e6:.1f} M chars")


def main():
    src = os.path.join(ROOT, "output")
    pack(os.path.join(src, "phromanusorn_web.glb"), "school")
    pack(os.path.join(src, "phromanusorn_lite.glb"), "school-lite")


if __name__ == "__main__":
    main()
