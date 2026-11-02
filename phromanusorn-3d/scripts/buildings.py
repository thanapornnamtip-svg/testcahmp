"""อาคารและสิ่งก่อสร้างในโรงเรียน (สร้างในพิกัดท้องถิ่น แล้วนำไปวางด้วย mb.place)

อาคารเรียนเลียนแบบอาคารเรียนมาตรฐาน สพฐ. : อาคาร คสล. มีระเบียงทางเดินด้านหนึ่ง
ห้องเรียนกว้าง 2 ช่วงเสา บันไดที่หัวท้ายอาคาร ผนังช่องลม หลังคาปั้นหยา/จั่ว
"""
import math

PL = 0.45   # ความสูงพื้นยก
H = 3.8     # ความสูงต่อชั้น


def steps(mb, x0, x1, y0, n, d, H, m, sign=1):
    """ขั้นบันได n ขั้น ลงจากขอบชาน (y0, สูง H) ออกไปทาง sign*y โดยไม่ซ้อนทับกัน"""
    for k in range(n):
        ya, yb = y0 + sign * k * d, y0 + sign * (k + 1) * d
        mb.box(x0, min(ya, yb), 0, x1, max(ya, yb), H * (n - k) / (n + 1), m, skip=("nz",))


def window_unit(mb, x0, x1, z0, z1, y, depth=0.2, frame="frame", panes=4, transom=None, sill=True):
    ym = y + depth / 2
    mb.face([(x0, ym, z0), (x1, ym, z0), (x1, ym, z1), (x0, ym, z1)], "glass")
    t = 0.06
    fy0, fy1 = ym - 0.05, ym + 0.05
    mb.box(x0, fy0, z0, x1, fy1, z0 + t, frame)
    mb.box(x0, fy0, z1 - t, x1, fy1, z1, frame)
    mb.box(x0, fy0, z0, x0 + t, fy1, z1, frame, skip=("nz", "pz"))
    mb.box(x1 - t, fy0, z0, x1, fy1, z1, frame, skip=("nz", "pz"))
    for k in range(1, panes):
        x = x0 + (x1 - x0) * k / panes
        mb.box(x - 0.025, fy0, z0, x + 0.025, fy1, z1, frame, skip=("nz", "pz"))
    if transom:
        mb.box(x0, fy0, transom - 0.03, x1, fy1, transom + 0.03, frame)
    if sill:
        mb.box(x0 - 0.05, y - 0.07, z0 - 0.06, x1 + 0.05, y, z0, "concrete_paint")


def school_block(mb, L, D, floors, *, bay=4.5, corridor=3.0, roof="hip", roof_mat="roof_blue",
                 wall="wall_cream", trim="trim_pink", parapet="breeze", open_ground=False, stairs=True,
                 label=None, label_both=False, frame="frame", roof_pitch=0.55, ridge="ridge",
                 sunshade=True, lobby=None, door="door"):
    """อาคารเรียน: x = 0..L (ความยาว), y = 0..D (ผนังหลัง y=0, ขอบระเบียง y=D)"""
    n = max(1, round(L / bay))
    bay = L / n
    Dc = D - corridor
    yw = Dc - 0.2

    def zf(i):
        return PL + i * H
    zt = zf(floors)
    lob = set(range(*lobby)) if lobby else set()

    # ฐาน + บันไดขึ้นระเบียง
    mb.box(-0.3, -0.3, 0, L + 0.3, D + 0.35, PL, {"pz": "floor_tile", "all": "plinth"}, skip=("nz",))
    for xc in (L * 0.25, L * 0.75):
        steps(mb, xc - 1.6, xc + 1.6, D + 0.35, 3, 0.3, PL, "plinth")
    # พื้นชั้นบน
    for i in range(1, floors):
        z = zf(i)
        mb.box(-0.15, -0.15, z - 0.28, L + 0.15, D + 0.15, z, {"pz": "floor_tile", "nz": "ceiling", "side": trim})
    # เสา
    for k in range(n + 1):
        x = min(max(k * bay, 0.2), L - 0.2)
        mb.box(x - 0.2, D - 0.42, PL, x + 0.2, D - 0.02, zt - 0.28, "column", skip=("nz", "pz"))
        mb.box(x - 0.22, -0.14, PL, x + 0.22, 0.05, zt - 0.28, "column", skip=("nz", "pz"))
    # ผนังแต่ละชั้น
    for i in range(floors):
        z0, z1 = zf(i), zf(i + 1) - 0.28
        ground_open = open_ground and i == 0
        for k in range(n):
            x0, x1 = k * bay, (k + 1) * bay
            if i == 0 and k in lob:
                # โถงกระจกชั้นล่าง
                for yy in (0.0, yw):
                    window_unit(mb, x0 + 0.2, x1 - 0.2, z0, z1 - 0.2, yy, 0.2, frame="frame", panes=3, sill=False)
                    mb.box(x0, yy, z1 - 0.2, x1, yy + 0.2, z1, wall)
                continue
            if ground_open:
                continue
            # ผนังหลัง (หน้าต่างบานใหญ่ + ช่องแสงด้านบน)
            mb.box(x0, 0, z0, x1, 0.2, z0 + 0.9, wall, skip=("nz",))
            mb.box(x0, 0, z0 + 2.55, x1, 0.2, z1, wall, skip=("pz",))
            mb.box(x0, 0, z0 + 0.9, x0 + 0.4, 0.2, z0 + 2.55, wall, skip=("nz", "pz"))
            mb.box(x1 - 0.4, 0, z0 + 0.9, x1, 0.2, z0 + 2.55, wall, skip=("nz", "pz"))
            window_unit(mb, x0 + 0.4, x1 - 0.4, z0 + 0.9, z0 + 2.55, 0.0, 0.2, frame=frame, panes=4,
                        transom=z0 + 2.05)
            # ผนังด้านระเบียง: ประตู 2 บานต่อห้อง + หน้าต่าง + ช่องลม
            mb.box(x0, yw, z0 + 2.2, x1, Dc, z0 + 2.6, "breeze_solid", skip=("nz", "pz"))
            mb.box(x0, yw, z0 + 2.6, x1, Dc, z1, wall, skip=("pz",))
            if k % 2 == 0:
                segs = [(x0, x0 + 0.4, "s"), (x0 + 0.4, x0 + 1.4, "d"), (x0 + 1.4, x0 + 1.8, "s"),
                        (x0 + 1.8, x1 - 0.3, "w"), (x1 - 0.3, x1, "s")]
            else:
                segs = [(x0, x0 + 0.3, "s"), (x0 + 0.3, x1 - 1.8, "w"), (x1 - 1.8, x1 - 1.4, "s"),
                        (x1 - 1.4, x1 - 0.4, "d"), (x1 - 0.4, x1, "s")]
            for a, b, kind in segs:
                if kind == "s":
                    mb.box(a, yw, z0, b, Dc, z0 + 2.2, wall, skip=("nz", "pz"))
                elif kind == "d":
                    mb.box(a, yw + 0.06, z0, b, yw + 0.12, z0 + 2.2, door, skip=("nz",))
                else:
                    mb.box(a, yw, z0, b, Dc, z0 + 1.0, wall, skip=("nz",))
                    window_unit(mb, a, b, z0 + 1.0, z0 + 2.2, yw, 0.2, frame=frame, panes=3, sill=False)
        if not ground_open:
            # ผนังกั้นห้อง + กระดาน + ผนังหัวท้าย
            for c in range(2, n, 2):
                x = c * bay
                mb.box(x - 0.1, 0.2, z0, x + 0.1, yw, z1, "wall_in", skip=("nz", "pz"))
                mb.box(x + 0.1, 1.5, z0 + 0.9, x + 0.14, yw - 1.0, z0 + 2.1, "chalkboard", skip=("nz", "pz"))
            mb.box(0, 0.2, z0, 0.2, yw, z1, wall, skip=("nz", "pz"))
            mb.box(L - 0.2, 0.2, z0, L, yw, z1, wall, skip=("nz", "pz"))
        if sunshade and not ground_open:
            mb.box(-0.1, -0.75, z0 + 2.6, L + 0.1, 0.0, z0 + 2.72, "concrete_paint")
        # ราวระเบียง
        if i >= 1:
            for k in range(n):
                xa, xb = k * bay + 0.2, (k + 1) * bay - 0.2
                if parapet == "breeze":
                    mb.box(xa, D - 0.3, z0, xb, D - 0.16, z0 + 0.85, "breeze", skip=("nz", "pz"))
                    mb.box(xa - 0.02, D - 0.34, z0 + 0.85, xb + 0.02, D - 0.12, z0 + 0.97, trim)
                elif parapet == "rail":
                    mb.box(xa, D - 0.3, z0, xb, D - 0.14, z0 + 0.3, wall, skip=("nz",))
                    mb.box(xa, D - 0.24, z0 + 0.3, xb, D - 0.2, z0 + 1.0, "railing", skip=("nz", "pz"))
                    mb.box(xa, D - 0.28, z0 + 1.0, xb, D - 0.16, z0 + 1.07, "steel_blue")
                else:
                    mb.box(xa, D - 0.3, z0, xb, D - 0.14, z0 + 0.95, wall, skip=("nz",))
                    mb.box(xa, D - 0.33, z0 + 0.55, xb, D - 0.11, z0 + 0.72, trim, skip=())
    # บันไดหัวท้าย
    if stairs:
        for xs0, xs1, side in ((-4.0, 0.0, "nx"), (L, L + 4.0, "px")):
            mb.box(xs0, 0, 0, xs1, D, zt, {"side": wall, "pz": "concrete"}, skip=("nz",))
            if side == "nx":
                mb.box(xs0 - 0.04, 0.9, PL + 1.0, xs0, D - 0.9, zt - 0.8, "breeze_solid", skip=("px",))
            else:
                mb.box(xs1, 0.9, PL + 1.0, xs1 + 0.04, D - 0.9, zt - 0.8, "breeze_solid", skip=("nx",))
            for yy in (-0.08, D - 0.42):
                xa = xs0 - 0.08 if side == "nx" else xs1 - 0.42
                mb.box(xa, yy, 0, xa + 0.5, yy + 0.5, zt, trim, skip=("nz", "pz"))
            for i in range(floors):
                z0 = zf(i)
                mb.face([(xs1 - 0.5, D + 0.01, z0), (xs0 + 0.5, D + 0.01, z0), (xs0 + 0.5, D + 0.01, z0 + 2.4),
                         (xs1 - 0.5, D + 0.01, z0 + 2.4)], "dark")
            if label and (side == "nx" or label_both):
                if side == "nx":
                    mb.plane_sign((xs0 - 0.07, D / 2, zt - 1.3), 3.2, 1.1, label, facing="nx")
                else:
                    mb.plane_sign((xs1 + 0.07, D / 2, zt - 1.3), 3.2, 1.1, label, facing="px")
    # คานรอบหลังคา + หลังคา
    rx0, rx1 = (-4.0, L + 4.0) if stairs else (0.0, L)
    mb.box(rx0 - 0.15, -0.15, zt - 0.28, rx1 + 0.15, D + 0.15, zt + 0.3,
           {"side": trim, "pz": "concrete", "nz": "ceiling"})
    zr = zt + 0.3
    if roof == "hip":
        h = (D / 2 + 1.0) * roof_pitch
        mb.hip_roof(rx0 - 1.0, -1.0, rx1 + 1.0, D + 1.0, zr, h, roof_mat, under="soffit", fascia="trim_white",
                    ridge=ridge)
    elif roof in ("gable", "thai"):
        h = (D / 2) * (roof_pitch if roof == "gable" else 0.95)
        mb.gable_roof(rx0, 0, rx1, D, zr, h, roof_mat, gable=wall, oh=0.9, eave=1.0,
                      barge="trim_white" if roof == "gable" else "gold", thai=(roof == "thai"), ridge=ridge)
    return zt


def admin_portico(mb, L, D, floors, roof_mat="roof_blue"):
    """มุขหน้าอาคารอำนวยการ: หน้าจั่วทรงไทย ตราโรงเรียน ป้ายชื่อโรงเรียน"""
    zt = PL + floors * H
    cx = L / 2
    y0, y1 = D, D + 6.5
    mb.box(cx - 8.5, y0, 0, cx + 8.5, y1, PL, {"pz": "floor_tile", "all": "plinth"}, skip=("nz",))
    steps(mb, cx - 6, cx + 6, y1, 4, 0.35, PL, "plinth")
    for x in (cx - 7.2, cx - 2.4, cx + 2.4, cx + 7.2):
        mb.cyl(x, y1 - 0.8, PL, zt, 0.42, "column", seg=16)
        mb.box(x - 0.6, y1 - 1.4, PL, x + 0.6, y1 - 0.2, PL + 0.5, "trim_white")
        mb.box(x - 0.6, y1 - 1.4, zt - 0.6, x + 0.6, y1 - 0.2, zt - 0.3, "gold")
    # คานป้ายชื่อ + ป้าย
    zb = PL + H - 0.2
    mb.box(cx - 8.2, y1 - 1.3, zb - 0.6, cx + 8.2, y1 - 0.3, zb + 0.9, {"side": "trim_blue", "all": "trim_blue"})
    mb.plane_sign((cx, y1 - 0.28, zb + 0.15), 14.5, 1.3, "label_admin", facing="py")
    mb.box(cx - 8.2, y1 - 1.3, zt - 0.3, cx + 8.2, y1 - 0.2, zt + 0.3, "trim_pink")
    # หลังคาจั่วทรงไทย (สันหลังคาตั้งฉากกับอาคาร)
    mb.push((cx, (y0 - 1.0 + y1) / 2, 0), math.pi / 2)
    half = (y1 - y0 + 1.0) / 2
    mb.gable_roof(-half, -8.2, half, 8.2, zt + 0.3, 6.2, roof_mat, gable="wall_white", oh=0.7, eave=0.9,
                  barge="gold", thai=True, finial="gold", ridge="ridge", gable_inset=0.0)
    mb.pop()
    # ตราโรงเรียนบนหน้าจั่ว
    mb.plane_sign((cx, y1 + 0.03, zt + 0.3 + 2.3), 3.4, 3.4, "emblem", facing="py")
    mb.box(cx - 8.2, y1 - 0.05, zt + 0.3, cx + 8.2, y1 + 0.02, zt + 0.55, "gold")
    # ป้ายต้อนรับ + คติพจน์บนระเบียงชั้น 2
    zr2 = PL + 1 * H
    mb.plane_sign((cx - 19.5, D + 0.02, zr2 + 0.42), 15.0, 1.2, "label_welcome", facing="py", off=0.0)
    mb.plane_sign((cx + 19.5, D + 0.02, zr2 + 0.42), 15.0, 1.6, "banner_motto", facing="py", off=0.0)


def lobby_canopy(mb, L, D, label):
    cx = L / 2
    mb.box(cx - 6, D, PL + 3.4, cx + 6, D + 4.0, PL + 3.8, {"side": "trim_blue", "pz": "concrete", "nz": "ceiling"})
    for x in (cx - 5.6, cx + 5.6):
        mb.cyl(x, D + 3.6, PL, PL + 3.4, 0.22, "steel_white", seg=10)
    mb.plane_sign((cx, D + 4.02, PL + 3.6), 3.0, 0.4, label, facing="py")
    mb.plane_sign((cx, D + 4.03, PL + 3.6), 1.1, 0.38, label, facing="py")


def gym(mb, L=60.0, W=42.0, eave=9.0, rise=6.5):
    """อาคารเฉลิมพระเกียรติ ๘๐ พรรษา (โรงยิม) ด้านหน้าหัน +y"""
    mb.box(-0.6, -0.6, 0, L + 0.6, W + 0.6, 0.35, {"pz": "floor_tile", "all": "plinth"}, skip=("nz",))
    cx, cy = L / 2, W / 2
    mb.quad_uv((cx - 16, cy - 9.5, 0.37), (cx + 16, cy - 9.5, 0.37), (cx + 16, cy + 9.5, 0.37),
               (cx - 16, cy + 9.5, 0.37), "court_basket")
    nxs = 10
    for k in range(nxs + 1):
        x = k * L / nxs
        for y in (0.0, W):
            mb.box(x - 0.3, y - 0.3, 0.35, x + 0.3, y + 0.3, eave, "steel_blue", skip=("nz", "pz"))
    # ผนังเตี้ย + ช่องประตู
    mb.box(0, -0.15, 0.35, L, 0.15, 1.8, "wall_white")
    for a, b in ((0, cx - 6), (cx + 6, L)):
        mb.box(a, W - 0.15, 0.35, b, W + 0.15, 1.8, "wall_white")
    mb.box(-0.15, 0, 0.35, 0.15, W, 1.8, "wall_white")
    mb.box(L - 0.15, 0, 0.35, L + 0.15, W, 1.8, "wall_white")
    for z0, z1 in ((0.35, 0.6),):
        mb.box(-0.18, -0.18, z0, L + 0.18, 0.0, z1, "trim_pink", skip=("nz",))
    # บานเกล็ดด้านบน
    mb.box(0, -0.06, 1.8, L, 0.06, eave - 0.7, "louvre", skip=("nz", "pz"))
    mb.box(0, W - 0.06, 1.8, L, W + 0.06, eave - 0.7, "louvre", skip=("nz", "pz"))
    mb.box(-0.06, 0, 1.8, 0.06, W, eave - 0.7, "louvre", skip=("nz", "pz"))
    mb.box(L - 0.06, 0, 1.8, L + 0.06, W, eave - 0.7, "louvre", skip=("nz", "pz"))
    # คานรอบ
    mb.box(-0.35, -0.35, eave - 0.7, L + 0.35, 0.25, eave, "trim_pink")
    mb.box(-0.35, W - 0.25, eave - 0.7, L + 0.35, W + 0.35, eave, "trim_pink")
    mb.box(-0.35, 0.25, eave - 0.7, 0.25, W - 0.25, eave, "trim_pink")
    mb.box(L - 0.25, 0.25, eave - 0.7, L + 0.35, W - 0.25, eave, "trim_pink")
    # หลังคาโค้ง + หน้าจั่วโค้ง
    mb.barrel_roof(-1.5, -1.8, L + 1.5, W + 1.8, eave, rise, "metal_blue", seg=28)
    R = ((W + 3.6) ** 2 / 4 + rise * rise) / (2 * rise)
    zc = eave + rise - R
    for x in (0.0, L):
        pts = []
        for i in range(21):
            y = i / 20 * W
            dy = y - cy
            pts.append((x, y, max(eave, zc + math.sqrt(max(R * R - dy * dy, 0))) - 0.05))
        mb.face(pts + [(x, W, eave), (x, 0, eave)], "louvre")
    # ป้ายด้านหน้า + กันสาดทางเข้า
    mb.box(cx - 8, W + 0.3, eave - 3.2, cx + 8, W + 0.5, eave - 0.8, "trim_blue")
    mb.plane_sign((cx, W + 0.52, eave - 2.0), 15.0, 2.25, "label_gym", facing="py")
    mb.box(cx - 7, W, 3.6, cx + 7, W + 4.5, 3.9, {"side": "trim_white", "pz": "metal_blue", "nz": "ceiling"})
    for x in (cx - 6.6, cx + 6.6):
        mb.cyl(x, W + 4.2, 0.35, 3.6, 0.18, "steel_white", seg=10)
    # อัฒจันทร์ในอาคาร + แป้นบาส
    for s in range(5):
        mb.box(6, 0.3 + 0.8 * (4 - s), 0.35, L - 6, 0.3 + 0.8 * (5 - s), 0.35 + 0.45 * (s + 1),
               {"pz": "trim_blue" if s % 2 else "trim_pink", "all": "concrete_paint"}, skip=("nz",))
    for sx in (-1, 1):
        hoop(mb, cx + sx * 14.6, cy, facing=-sx)


def hoop(mb, x, y, facing=1, z0=0.35):
    """แป้นบาส facing = ทิศที่แป้นหันไป (+1 = +x)"""
    px = x - facing * 1.2
    mb.box(px - 0.1, y - 0.1, z0, px + 0.1, y + 0.1, z0 + 3.4, "steel_blue", skip=("nz",))
    mb.beam((px, y, z0 + 3.2), (x - facing * 0.1, y, z0 + 3.35), 0.12, 0.12, "steel_blue")
    bx = x
    mb.box(bx - 0.03, y - 0.9, z0 + 2.9, bx + 0.03, y + 0.9, z0 + 3.95, "trim_white")
    mb.box(bx + facing * 0.04 - 0.01, y - 0.3, z0 + 3.05, bx + facing * 0.04 + 0.01, y + 0.3, z0 + 3.5, "mb_red")
    rx = bx + facing * 0.3
    pts = [(rx + 0.23 * math.cos(a * math.pi / 4), y + 0.23 * math.sin(a * math.pi / 4), z0 + 3.05) for a in range(9)]
    for a, b in zip(pts[:-1], pts[1:]):
        mb.beam(a, b, 0.03, 0.03, "mb_red")


def canteen(mb, L=60.0, W=24.0, h=5.5):
    """อาคารอเนกประสงค์/โรงอาหาร: โถงเปิดโล่ง หลังคาเหล็ก"""
    mb.box(-0.3, -0.3, 0, L + 0.3, W + 0.3, 0.3, {"pz": "floor_tile", "all": "plinth"}, skip=("nz",))
    for k in range(11):
        x = k * L / 10
        for y in (0.0, W / 2, W):
            mb.cyl(x, y, 0.3, h, 0.16, "steel_white", seg=10, caps=False)
    mb.box(-0.4, -0.2, h - 0.5, L + 0.4, 0.2, h, "trim_blue")
    mb.box(-0.4, W - 0.2, h - 0.5, L + 0.4, W + 0.2, h, "trim_blue")
    mb.gable_roof(0, 0, L, W, h, 3.2, "metal_blue", gable="louvre", oh=1.2, eave=1.6, barge="steel_white",
                  ridge="steel_white")
    mb.gable_roof(0, W / 2 - 1.4, L, W / 2 + 1.4, h + 3.2 + 0.6, 0.6, "metal_blue", gable=None, oh=0.4,
                  eave=0.5, barge=None)
    for x in (0.0, L):
        mb.face([(x, W / 2 - 1.2, h + 3.0), (x, W / 2 + 1.2, h + 3.0), (x, W / 2 + 1.2, h + 3.6),
                 (x, W / 2 - 1.2, h + 3.6)], "louvre")
    # โต๊ะ-ม้านั่ง
    for i in range(9):
        for j in range(5):
            tx = 3.5 + i * 6.3
            ty = 2.5 + j * 3.4
            mb.box(tx, ty, 0.72, tx + 3.0, ty + 0.8, 0.77, "bench_stone")
            mb.box(tx + 1.3, ty + 0.3, 0.3, tx + 1.7, ty + 0.5, 0.72, "bench_stone", skip=("nz", "pz"))
            for by in (ty - 0.45, ty + 0.95):
                mb.box(tx, by, 0.43, tx + 3.0, by + 0.3, 0.47, "bench_stone")
                mb.box(tx + 1.35, by + 0.1, 0.3, tx + 1.65, by + 0.2, 0.43, "bench_stone", skip=("nz", "pz"))
    # ซุ้มร้านค้าด้านหลัง
    mb.box(1.0, W - 3.2, 0.3, L - 1.0, W - 0.2, 3.0, {"side": "wall_white", "pz": "concrete"})
    mb.box(1.0, W - 4.3, 0.3, L - 1.0, W - 3.2, 1.2, {"side": "steel", "pz": "steel"})
    mb.plane_sign((L / 2, W - 3.22, 2.45), 40.0, 1.5, "stalls", facing="ny")
    mb.box(1.0, W - 4.6, 3.0, L - 1.0, W - 3.2, 3.15, "trim_pink")
    mb.plane_sign((L / 2, -0.25, h - 0.25), 12.0, 1.7, "label_canteen", facing="ny")


def hall(mb, W=26.0, L=40.0, Hh=9.0, roof_mat="roof_orange"):
    """หอประชุม: x = 0..W, y = 0..L, ด้านหน้า +y"""
    mb.box(-0.4, -0.4, 0, W + 0.4, L + 0.4, 0.6, {"pz": "floor_tile", "all": "plinth"}, skip=("nz",))
    mb.box(0, 0, 0.6, W, L, Hh, "wall_cream", skip=("nz", "pz"))
    for k in range(11):
        y = 1.5 + k * (L - 3) / 10
        for x, fac in ((-0.02, "nx"), (W + 0.02, "px")):
            if k < 10:
                yc = y + (L - 3) / 20
                mb.plane_sign((x, yc, 4.0), 1.8, 5.4, "glass", facing=fac)
            xx = -0.25 if fac == "nx" else W
            mb.box(xx, y - 0.25, 0.6, xx + 0.25, y + 0.25, Hh, "trim_pink", skip=("nz", "pz"))
    mb.box(-0.3, -0.3, Hh - 0.6, W + 0.3, L + 0.3, Hh, "trim_blue")
    mb.push((W / 2, L / 2, 0), math.pi / 2)
    mb.gable_roof(-L / 2, -W / 2, L / 2, W / 2, Hh, W / 2 * 0.8, roof_mat, gable="wall_white", oh=1.2,
                  eave=1.3, barge="gold", thai=True, finial="gold", ridge="ridge")
    mb.pop()
    # มุขด้านหน้า
    y0, y1 = L, L + 6.0
    mb.box(W / 2 - 8, y0, 0, W / 2 + 8, y1, 0.6, {"pz": "floor_tile", "all": "plinth"}, skip=("nz",))
    steps(mb, W / 2 - 6, W / 2 + 6, y1, 3, 0.4, 0.6, "plinth")
    for x in (W / 2 - 7, W / 2 - 2.5, W / 2 + 2.5, W / 2 + 7):
        mb.cyl(x, y1 - 0.7, 0.6, 7.2, 0.35, "column", seg=14)
    mb.box(W / 2 - 7.6, y0, 7.2, W / 2 + 7.6, y1, 7.8, "trim_blue")
    mb.plane_sign((W / 2, y1 + 0.02, 7.5), 11.0, 0.55, "label_hall", facing="py")
    mb.push((W / 2, (y0 + y1) / 2, 0), math.pi / 2)
    mb.gable_roof(-3.0, -7.6, 3.0, 7.6, 7.8, 4.2, roof_mat, gable="wall_white", oh=0.5, eave=0.6, barge="gold",
                  thai=True, finial="gold")
    mb.pop()
    mb.plane_sign((W / 2, y1 + 0.03, 9.3), 2.6, 2.6, "emblem", facing="py")
    for x in (W / 2 - 4.5, W / 2 - 0.9, W / 2 + 2.7):
        mb.box(x, L - 0.05, 0.6, x + 1.8, L + 0.02, 3.4, "door_blue", skip=("nz",))


def buddha(mb, cx, cy, z, s=1.0):
    """พระพุทธรูปปางสมาธิ (แบบเรียบง่าย) หันหน้าไป +y"""
    mb.push((cx, cy, z), 0.0, s)
    mb.lathe([(0.95, 0), (1.0, 0.12), (0.85, 0.2), (0.95, 0.32), (0.7, 0.42), (0.0, 0.42)], 0, 0, "gold",
             seg=24, caps=True)
    mb.sphere((0, 0.08, 0.58), 0.85, "gold", seg=16, rings=6, scale=(1.0, 0.55, 0.22))
    mb.lathe([(0.0, 0.0), (0.4, 0.02), (0.44, 0.22), (0.43, 0.46), (0.38, 0.6), (0.2, 0.68), (0.1, 0.72),
              (0.0, 0.72)], 0, -0.05, "gold", seg=16, z0=0.62, sx=1.0, sy=0.72, caps=False)
    for sx in (-1, 1):
        mb.tube((sx * 0.4, -0.02, 1.2), (sx * 0.47, 0.12, 0.86), 0.1, 0.09, "gold", seg=8)
        mb.tube((sx * 0.47, 0.12, 0.86), (sx * 0.12, 0.3, 0.74), 0.09, 0.08, "gold", seg=8)
    mb.sphere((0, 0.02, 1.52), 0.2, "gold", seg=14, rings=7, scale=(1.0, 1.05, 1.12))
    mb.sphere((0, 0.0, 1.74), 0.11, "gold", seg=10, rings=5)
    mb.lathe([(0.06, 0.0), (0.03, 0.15), (0.0, 0.3)], 0, 0.0, "gold", seg=10, z0=1.8, caps=False)
    for sx in (-1, 1):
        mb.sphere((sx * 0.2, 0.0, 1.48), 0.06, "gold", seg=8, rings=4, scale=(0.5, 1.0, 2.0))
    mb.pop()


def shrine(mb):
    """ศาลาหลวงพ่อป่าแก้ว (พระพุทธรูปประจำโรงเรียน) หันหน้า +y"""
    mb.box(-4, -4, 0, 4, 4, 0.9, {"pz": "floor_tile", "all": "trim_white"}, skip=("nz",))
    mb.box(-4.1, -4.1, 0, 4.1, 4.1, 0.25, "trim_pink", skip=("nz",))
    steps(mb, -1.6, 1.6, 4.1, 3, 0.35, 0.9, "trim_white")
    for x0, x1, y0, y1 in ((-4, -1.6, 3.8, 4.0), (1.6, 4, 3.8, 4.0), (-4, -3.8, -3.8, 3.8), (3.8, 4, -3.8, 3.8),
                           (-4, 4, -4, -3.8)):
        mb.box(x0, y0, 0.9, x1, y1, 1.5, "trim_white")
        mb.box(x0 - 0.03, y0 - 0.03, 1.5, x1 + 0.03, y1 + 0.03, 1.58, "gold")
    for x in (-3.4, 3.4):
        for y in (-3.4, 3.4):
            mb.box(x - 0.22, y - 0.22, 0.9, x + 0.22, y + 0.22, 4.5, "trim_white", skip=("nz",))
            mb.box(x - 0.3, y - 0.3, 4.1, x + 0.3, y + 0.3, 4.5, "gold")
    mb.box(-3.6, -3.6, 4.5, 3.6, 3.6, 4.75, "red_lacquer")
    mb.hip_roof(-4.7, -4.7, 4.7, 4.7, 4.75, 1.9, "roof_orange", under="red_lacquer", fascia="gold", fh=0.25,
                ridge="gold")
    mb.push((0, 0, 0), math.pi / 2)
    mb.gable_roof(-2.6, -2.2, 2.6, 2.2, 6.0, 2.7, "roof_green", gable="red_lacquer", oh=0.35, eave=0.5,
                  barge="gold", thai=True, finial="gold", ridge="gold")
    mb.pop()
    mb.box(-2.2, -2.2, 4.75, 2.2, 2.2, 6.05, "red_lacquer", skip=("nz",))
    # ผนังหลัง + ฐานชุกชี + พระพุทธรูป
    mb.box(-2.6, -3.5, 0.9, 2.6, -3.2, 4.1, "red_lacquer")
    mb.box(-1.2, -2.6, 0.9, 1.2, -1.0, 1.7, {"side": "red_lacquer", "pz": "gold"})
    mb.box(-1.35, -2.7, 0.9, 1.35, -0.9, 1.05, "gold")
    buddha(mb, 0, -1.85, 1.7, 1.15)
    mb.plane_sign((0, 3.62, 4.32), 2.2, 0.55, "label_shrine", facing="py")
    # แจกันดอกไม้/พวงมาลัย
    for x in (-0.9, 0.9):
        mb.cyl(x, -0.6, 0.9, 1.3, 0.12, "gold", seg=10)
        mb.sphere((x, -0.6, 1.42), 0.2, "flower_yellow", seg=8, rings=5)


def guardhouse(mb):
    mb.box(0, 0, 0, 3.2, 3.2, 0.3, "plinth", skip=("nz",))
    mb.box(0.1, 0.1, 0.3, 3.1, 3.1, 1.2, "wall_white", skip=("nz", "pz"))
    for x0, y0, x1, y1 in ((0.1, 0.1, 3.1, 0.2), (0.1, 3.0, 3.1, 3.1), (0.1, 0.1, 0.2, 3.1), (3.0, 0.1, 3.1, 3.1)):
        mb.box(x0, y0, 1.2, x1, y1, 2.4, "glass_light", skip=("nz", "pz"))
    for x in (0.1, 3.0):
        for y in (0.1, 3.0):
            mb.box(x, y, 0.3, x + 0.1, y + 0.1, 2.8, "trim_blue", skip=("nz",))
    mb.box(0.0, 0.0, 2.4, 3.2, 3.2, 2.8, "trim_pink")
    mb.hip_roof(-0.6, -0.6, 3.8, 3.8, 2.8, 1.1, "roof_blue", fascia="trim_white", ridge="ridge")
    mb.plane_sign((3.25, 1.6, 2.6), 1.2, 0.32, "label_guard", facing="px")


def gate(mb):
    """ประตูโรงเรียน: แนวรั้วอยู่ที่ x=0 ถนนอยู่ด้าน +x ช่องทางเข้าตามแกน y (-6.5..6.5)"""
    for yc in (-7.6, 7.6):
        mb.box(-1.1, yc - 1.1, 0, 1.1, yc + 1.1, 5.2, {"side": "wall_white", "pz": "trim_blue"}, skip=("nz",))
        mb.box(-1.18, yc - 1.18, 0, 1.18, yc + 1.18, 0.9, "trim_pink", skip=("nz",))
        mb.box(-1.2, yc - 1.2, 5.2, 1.2, yc + 1.2, 5.45, "trim_blue")
        mb.plane_sign((1.12, yc, 3.2), 1.5, 1.5, "emblem", facing="px")
        mb.plane_sign((-1.12, yc, 3.2), 1.5, 1.5, "emblem", facing="nx")
    mb.box(-0.7, -8.7, 5.45, 0.7, 8.7, 7.0, "trim_blue")
    mb.box(-0.75, -8.75, 6.95, 0.75, 8.75, 7.15, "trim_pink")
    mb.plane_sign((0.72, 0, 6.22), 15.0, 1.4, "sign_gate", facing="px")
    mb.plane_sign((-0.72, 0, 6.22), 15.0, 1.4, "sign_gate", facing="nx")
    # หลังคาทรงไทยเล็กบนซุ้มประตู
    mb.push((0, 0, 0), math.pi / 2)
    mb.gable_roof(-8.2, -0.75, 8.2, 0.75, 7.15, 1.3, "roof_blue", gable="trim_blue", oh=0.3, eave=0.55,
                  barge="gold", thai=True, finial="gold", ridge="gold")
    mb.pop()
    # ประตูเหล็กบานเลื่อน (เปิดอยู่)
    for y0, y1 in ((8.7, 15.2), (-15.2, -8.7)):
        mb.box(-1.6, y0, 0.08, -1.5, y1, 2.0, "railing", skip=())
        mb.box(-1.62, y0, 1.95, -1.48, y1, 2.05, "steel_blue")
        mb.box(-1.62, y0, 0.05, -1.48, y1, 0.15, "steel_blue")


def fence_run(mb, a, b, axis="x", gaps=(), pillar=3.0):
    """รั้วโรงเรียน: กำแพงเตี้ย + ราวเหล็ก + เสาทุก 3 m  (a,b) = จุดเริ่ม/จบ แนวตรง"""
    (xa, ya), (xb, yb) = a, b
    L = abs(xb - xa) if axis == "x" else abs(yb - ya)
    lo = min(xa, xb) if axis == "x" else min(ya, yb)
    c = ya if axis == "x" else xa
    segs = [(lo, lo + L)]
    for g0, g1 in gaps:
        new = []
        for s0, s1 in segs:
            if g1 <= s0 or g0 >= s1:
                new.append((s0, s1))
            else:
                if g0 > s0:
                    new.append((s0, g0))
                if g1 < s1:
                    new.append((g1, s1))
        segs = new

    def bx(u0, u1, v0, v1, z0, z1, m, skip=()):
        if axis == "x":
            mb.box(u0, v0, z0, u1, v1, z1, m, skip)
        else:
            mb.box(v0, u0, z0, v1, u1, z1, m, skip)
    for s0, s1 in segs:
        bx(s0, s1, c - 0.12, c + 0.12, 0, 0.65, "wall_white", skip=("nz",))
        bx(s0, s1, c - 0.14, c + 0.14, 0.65, 0.75, "trim_pink")
        bx(s0, s1, c - 0.03, c + 0.03, 0.75, 2.0, "railing", skip=("nz", "pz"))
        bx(s0, s1, c - 0.05, c + 0.05, 1.98, 2.05, "steel_blue")
        n = max(1, int((s1 - s0) / pillar))
        for k in range(n + 1):
            u = s0 + (s1 - s0) * k / n
            bx(u - 0.17, u + 0.17, c - 0.17, c + 0.17, 0, 2.2, "wall_white", skip=("nz", "pz"))
            bx(u - 0.22, u + 0.22, c - 0.22, c + 0.22, 2.2, 2.32, "trim_blue")


def flagpole(mb, phase=0.0):
    mb.box(-3.2, -3.2, 0, 3.2, 3.2, 0.35, {"pz": "paving", "all": "trim_pink"}, skip=("nz",))
    mb.box(-2.2, -2.2, 0.35, 2.2, 2.2, 0.7, {"pz": "floor_tile", "all": "trim_blue"})
    mb.box(-1.2, -1.2, 0.7, 1.2, 1.2, 1.05, {"pz": "floor_tile", "all": "trim_white"})
    mb.cyl(0, 0, 1.05, 17.0, 0.13, "steel_white", seg=12, r2=0.07)
    mb.sphere((0, 0, 17.15), 0.17, "gold", seg=10, rings=6)
    rows = []
    W, Hf, ztop = 2.7, 1.8, 16.75
    for i in range(4):
        z = ztop - Hf + Hf * i / 3
        row = []
        for j in range(14):
            t = j / 13
            row.append((0.12 + W * t, 0.28 * math.sin(2 * math.pi * (1.1 * t) + phase) * t, z))
        rows.append(row)
    mb.grid(rows, "flag", smooth=True, closed=False)
    mb.beam((0.13, 0, ztop + 0.05), (0.13, 0, 1.2), 0.012, 0.012, "steel", caps=False)


def water_tower(mb, h=16.0):
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.beam((sx * 2.4, sy * 2.4, 0), (sx * 1.5, sy * 1.5, h), 0.4, 0.4, "concrete_paint")
    for z in (4.0, 8.0, 12.0):
        t = z / h
        r = 2.4 - 0.9 * t
        for a, b in (((-r, -r), (r, -r)), ((r, -r), (r, r)), ((r, r), (-r, r)), ((-r, r), (-r, -r))):
            mb.beam((a[0], a[1], z), (b[0], b[1], z), 0.25, 0.3, "concrete_paint")
    mb.box(-2.0, -2.0, h - 0.3, 2.0, 2.0, h, "concrete_paint")
    mb.cyl(0, 0, h, h + 4.2, 2.7, "trim_pink", seg=24, caps=True)
    mb.cyl(0, 0, h + 1.7, h + 2.5, 2.73, "trim_blue", seg=24, caps=False)
    mb.lathe([(2.8, 0), (2.8, 0.15), (0.4, 1.3), (0.0, 1.35)], 0, 0, "trim_blue", seg=24, z0=h + 4.2)
    for k in range(int(h / 0.4)):
        z = k * 0.4 + 0.3
        mb.beam((2.0, -0.25, z), (2.0, 0.25, z), 0.04, 0.04, "steel")
    mb.beam((2.0, -0.25, 0), (2.0, -0.25, h), 0.05, 0.05, "steel")
    mb.beam((2.0, 0.25, 0), (2.0, 0.25, h), 0.05, 0.05, "steel")


def walkway(mb, L, w=3.0, h=2.8, roof="metal_blue"):
    """ทางเดินมีหลังคา: x = 0..L, y = -w/2..w/2"""
    mb.box(0, -w / 2, 0, L, w / 2, 0.08, "paving", skip=("nz",))
    n = max(1, int(L / 3.5))
    for k in range(n + 1):
        x = k * L / n
        for y in (-w / 2 + 0.15, w / 2 - 0.15):
            mb.box(x - 0.06, y - 0.06, 0.08, x + 0.06, y + 0.06, h, "steel_white", skip=("nz", "pz"))
    mb.box(0, -w / 2, h - 0.12, L, -w / 2 + 0.12, h, "steel_white")
    mb.box(0, w / 2 - 0.12, h - 0.12, L, w / 2, h, "steel_white")
    mb.gable_roof(0, -w / 2 + 0.15, L, w / 2 - 0.15, h, 0.55, roof, gable=None, oh=0.0, eave=0.3,
                  barge=None)


def shed(mb, L, w=6.0, h=2.8, roof="metal_zinc"):
    """โรงจอดรถ: หลังคาเพิงหมาแหงน x = 0..L, y = 0..w"""
    mb.box(0, 0, 0, L, w, 0.06, "concrete", skip=("nz",))
    n = max(1, int(L / 4))
    for k in range(n + 1):
        x = k * L / n
        mb.box(x - 0.07, 0.15, 0.06, x + 0.07, 0.29, h + 0.6, "steel_blue", skip=("nz", "pz"))
        mb.box(x - 0.07, w - 0.29, 0.06, x + 0.07, w - 0.15, h, "steel_blue", skip=("nz", "pz"))
        mb.beam((x, -0.4, h + 0.68), (x, w + 0.4, h - 0.12), 0.08, 0.14, "steel_blue")
    ts = 1.0
    s = math.hypot(w + 0.8, 0.8)
    mb.face([(L + 0.3, -0.4, h + 0.72), (-0.3, -0.4, h + 0.72), (-0.3, w + 0.4, h - 0.08), (L + 0.3, w + 0.4, h - 0.08)],
            roof, uv=[(0, 0), (L / ts, 0), (L / ts, s / ts), (0, s / ts)])


def grandstand(mb, L=70.0, nsteps=6):
    """อัฒจันทร์: ด้านหน้า y=0 ขั้นบันไดสูงขึ้นไปทาง +y"""
    dpt = 0.85
    for s in range(nsteps):
        mb.box(0, s * dpt, 0, L, (s + 1) * dpt, 0.45 * (s + 1),
               {"pz": "trim_blue" if s % 2 == 0 else "trim_pink", "all": "concrete_paint"}, skip=("nz",))
    D = nsteps * dpt
    for k in range(8):
        x = k * L / 7
        mb.box(x - 0.15, D - 0.1, 0, x + 0.15, D + 0.2, 7.2, "steel_white", skip=("nz",))
        mb.beam((x, D + 0.05, 7.1), (x, -1.2, 6.0), 0.18, 0.4, "steel_white")
    mb.face([(L + 0.5, -1.4, 6.05), (-0.5, -1.4, 6.05), (-0.5, D + 0.4, 7.35), (L + 0.5, D + 0.4, 7.35)], "metal_blue",
            uv=[(0, 0), (L + 1, 0), (L + 1, D + 1.9), (0, D + 1.9)])
    mb.box(-0.5, D + 0.2, 6.4, L + 0.5, D + 0.4, 7.4, "trim_blue")
    mb.plane_sign((L / 2, D + 0.42, 6.9), 9.0, 1.1, "label_stand", facing="py")
    mb.box(0, D, 0, L, D + 0.1, 3.0, "wall_white")


def stone_table(mb, x, y, rot=0.0):
    """โต๊ะม้าหิน (ชุดโต๊ะหินอ่อน 4 ที่นั่ง)"""
    mb.push((x, y, 0), rot)
    mb.cyl(0, 0, 0, 0.72, 0.13, "bench_stone", seg=10, caps=False)
    mb.cyl(0, 0, 0.72, 0.78, 0.6, "bench_stone", seg=16)
    for k in range(4):
        a = k * math.pi / 2
        mb.cyl(0.95 * math.cos(a), 0.95 * math.sin(a), 0, 0.44, 0.19, "bench_stone", seg=10)
    mb.pop()


def goal(mb, x, y, facing=1):
    """ประตูฟุตบอล 7.32 x 2.44 m  facing = ทิศที่หน้าประตูหันไป (+1 = +x)"""
    d = -facing * 1.8
    for yy in (y - 3.66, y + 3.66):
        mb.box(x - 0.06, yy - 0.06, 0, x + 0.06, yy + 0.06, 2.44, "steel_white", skip=("nz",))
        mb.beam((x, yy, 2.44), (x + d, yy, 0.6), 0.05, 0.05, "steel_white")
        mb.beam((x + d, yy, 0.6), (x + d, yy, 0.0), 0.05, 0.05, "steel_white")
    mb.box(x - 0.06, y - 3.72, 2.38, x + 0.06, y + 3.72, 2.5, "steel_white")
    mb.beam((x + d, y - 3.66, 0.05), (x + d, y + 3.66, 0.05), 0.05, 0.05, "steel_white")


def takraw_net(mb, x, y, length=7.0):
    for yy in (y - length / 2, y + length / 2):
        mb.box(x - 0.04, yy - 0.04, 0, x + 0.04, yy + 0.04, 1.6, "steel", skip=("nz",))
    mb.box(x - 0.01, y - length / 2, 0.85, x + 0.01, y + length / 2, 1.52, "railing", skip=())
