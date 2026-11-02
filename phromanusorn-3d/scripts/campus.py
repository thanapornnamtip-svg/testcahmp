"""ผังโรงเรียน พื้นที่ ~40 ไร่ (300 x 216 m) + ถนนบันไดอิฐ + ตึกแถวฝั่งตรงข้าม + เขาวัง (พระนครคีรี)

พิกัดโลก: หน่วยเมตร, +x = ตะวันออก, +y = เหนือ, จุด (0,0) = กลางโรงเรียน
หมายเหตุ: ตำแหน่งอาคารเป็นการจัดวางโดยประมาณ (ไม่มีแผนที่ดาวเทียมในการสร้าง)
"""
import math
import random

import buildings as B
from mb import MB, collection, place

R = random.Random(20250101)

CAMPUS = (-150.0, -108.0, 150.0, 108.0)
FLAG = (95.0, -4.0)
TRACK_C = (-52.0, -6.0)
TRACK_S, TRACK_R, LANE = 80.0, 32.0, 1.22
KW_C = (-30.0, 390.0)                       # ศูนย์กลางเขาวัง
KW_PEAKS = [(-260.0, 402.0, 50.0), (-40.0, 396.0, 55.0), (150.0, 380.0, 38.0)]   # x, y, ความสูงยอด (เพิ่มจากฐาน)

OCC = [
    (66, -48, 90, 40), (74, 42, 126, 62), (76, -66, 124, -50), (81, -104, 121, -74),
    (-147, 60, -85, 76), (-83, 60, -17, 76), (-19, 60, 73, 76), (-147, -84, -81, -69), (-83, -84, -26, -69),
    (-24, -108, 40, -58), (-12, 77, 48, 104), (53, 87, 63, 97), (-144, 84, -92, 100), (-90, 78, -18, 106),
    (-133, -47, 29, 35), (28, -24, 68, 12), (-1, 38, 35, 50), (84, -48, 126, 40), (124, -108, 133, 106),
    (132, -11, 150, 1), (133, -104, 148, -42), (133, 44, 149, 106), (135, 16, 147, 28), (140, -28, 146, -20),
    (139, 2, 145, 8), (-142, 56, 72, 61), (-142, -70, -26, -64), (62, 12, 68, 58), (62, -66, 68, -24),
    (-93, -57, -11, -48), (-72, 37, -56, 42),
]


def free(x, y, r=0.0, rects=OCC):
    for x0, y0, x1, y1 in rects:
        if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
            return False
    return True


# ====================================================================== ground & roads
def ground(coll):
    g = MB()
    S = 1600
    g.face([(-S, -S, -0.05), (S, -S, -0.05), (S, S, -0.05), (-S, S, -0.05)], "grass_dry")
    g.build("Ground_Town", coll)
    g = MB()
    F = 14000
    for a, b, c, d in (((-F, -F), (F, -F), (S, -S), (-S, -S)), ((F, -F), (F, F), (S, S), (S, -S)),
                       ((F, F), (-F, F), (-S, S), (S, S)), ((-F, F), (-F, -F), (-S, -S), (-S, S))):
        g.face([(a[0], a[1], -0.4), (b[0], b[1], -0.4), (c[0], c[1], -0.06), (d[0], d[1], -0.06)], "far_ground")
    g.build("Ground_Far", coll)
    g = MB()
    x0, y0, x1, y1 = CAMPUS
    g.face([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], "grass")
    g.build("Ground_Campus", coll)

    p = MB()   # ลาน / ถนนภายใน
    def slab(x0, y0, x1, y1, z, m):
        p.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], m)
    slab(84, -48, 125, 40, 0.03, "paving")                  # ลานหน้าเสาธง
    slab(125, -106, 132, 104, 0.04, "asphalt")              # ถนนภายใน
    slab(132, -10, 150.6, 0, 0.04, "asphalt")               # ทางเข้า
    slab(133, 44, 149, 106, 0.035, "concrete")              # ที่จอดรถครู
    slab(133, -104, 149, -42, 0.035, "concrete")            # ที่จอดรถนักเรียน
    slab(-12, 104, 48, 107, 0.03, "concrete")
    slab(40, -104, 80, -66, 0.02, "grass")
    slab(66, -48, 84, 40, 0.025, "paving")
    slab(-1, 38, 35, 50, 0.02, "concrete")
    # สนามบาส 2 สนาม (แกนยาวเหนือ-ใต้)
    for cx in (38.5, 57.5):
        p.quad_uv((cx + 9.5, -22, 0.045), (cx + 9.5, 10, 0.045), (cx - 9.5, 10, 0.045), (cx - 9.5, -22, 0.045),
                  "court_basket")
    # สนามตะกร้อ
    for cx in (8.0, 26.0):
        p.quad_uv((cx - 7.7, 39.95, 0.045), (cx + 7.7, 39.95, 0.045), (cx + 7.7, 48.05, 0.045),
                  (cx - 7.7, 48.05, 0.045), "court_takraw")
    # หลุมกระโดดไกล
    p.box(-72, 38, 0, -62, 41, 0.06, {"pz": "sand", "all": "concrete_paint"}, skip=("nz",))
    p.face([(-62, 38.9, 0.04), (-30, 38.9, 0.04), (-30, 40.1, 0.04), (-62, 40.1, 0.04)], "track")
    p.build("Paving", coll)

    r = MB()   # ถนนสาธารณะ
    def rs(x0, y0, x1, y1, z, m):
        r.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], m)
    rs(153, -520, 165, 520, 0.0, "asphalt")                  # ถนนบันไดอิฐ
    rs(-520, 110, 153, 116, -0.01, "asphalt")                # ซอยด้านเหนือ (เชิงเขาวัง)
    rs(-520, -116, 153, -110, -0.01, "asphalt")              # ซอยด้านใต้
    rs(-158, -110, -152, 110, -0.012, "asphalt")             # ซอยด้านตะวันตก
    for x0, x1 in ((150.6, 153.0), (165.0, 167.6)):
        r.box(x0, -520, 0, x1, 520, 0.15, {"pz": "paving", "all": "kerb"}, skip=("nz",))
    # ขอบทางขาวดำ / แดงขาว (หน้าโรงเรียนห้ามจอด)
    for y0, y1, m in ((-520, -40, "curb_bw"), (-40, 30, "curb_rw"), (30, 520, "curb_bw")):
        r.box(152.85, y0, 0.0, 153.05, y1, 0.18, m, skip=("nz",))
        r.box(164.95, y0, 0.0, 165.15, y1, 0.18, m, skip=("nz",))
    # เส้นจราจร
    y = -520.0
    while y < 520:
        if not (-14 < y < 4):
            rs(158.9, y, 159.1, y + 3.0, 0.03, "road_white")
        y += 9.0
    rs(153.4, -520, 153.55, 520, 0.03, "road_white")
    rs(164.45, -520, 164.6, 520, 0.03, "road_white")
    for k in range(11):   # ทางม้าลายหน้าประตูโรงเรียน
        x = 153.6 + k * 1.05
        rs(x, -9.0, x + 0.55, -3.0, 0.035, "road_white")
    for yy in (-12.0, 0.6):
        rs(153.4, yy, 164.6, yy + 0.3, 0.035, "road_white")
    r.build("Roads", coll)


def track(coll):
    """ลู่วิ่ง 6 ลู่ รอบสนามฟุตบอล"""
    m = MB()
    cx, cy = TRACK_C
    hs = TRACK_S / 2

    def ring(Rr, n_st=18, n_arc=28):
        pts = []
        for i in range(n_st):
            pts.append((-hs + TRACK_S * i / n_st, -Rr))
        for i in range(n_arc):
            a = -math.pi / 2 + math.pi * i / n_arc
            pts.append((hs + Rr * math.cos(a), Rr * math.sin(a)))
        for i in range(n_st):
            pts.append((hs - TRACK_S * i / n_st, Rr))
        for i in range(n_arc):
            a = math.pi / 2 + math.pi * i / n_arc
            pts.append((-hs + Rr * math.cos(a), Rr * math.sin(a)))
        return pts
    m.push((cx, cy, 0.035))
    radii = [TRACK_R + 6 * LANE - LANE * i for i in range(7)]
    rows = [[(x, y, 0) for x, y in ring(rr)] for rr in radii]
    per = 2 * TRACK_S + 2 * math.pi * (TRACK_R + 3 * LANE)
    m.grid(rows, "track", smooth=False, closed=True, uvscale=(per / 8.0, 1.0))
    rows = [[(x, y, 0.02) for x, y in ring(TRACK_R)], [(x, y, 0.02) for x, y in ring(TRACK_R - 0.12)]]
    m.grid(rows, "road_white", smooth=False, closed=True)
    rows = [[(x, y, 0.0) for x, y in ring(TRACK_R + 6 * LANE + 1.2)], [(x, y, 0.0) for x, y in ring(TRACK_R + 6 * LANE)]]
    m.grid(rows, "concrete", smooth=False, closed=True)
    # สนามหญ้า (เส้นสนาม)
    m.quad_uv((-52, -32, -0.015), (52, -32, -0.015), (52, 32, -0.015), (-52, 32, -0.015), "field")
    m.pop()
    B.goal(m, cx - 50, cy, facing=1)
    B.goal(m, cx + 50, cy, facing=-1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.beam((cx + sx * 50, cy + sy * 30, 0), (cx + sx * 50, cy + sy * 30, 1.5), 0.03, 0.03, "steel_white")
            m.face([(cx + sx * 50, cy + sy * 30, 1.5), (cx + sx * 50 + 0.4 * sx, cy + sy * 30, 1.5),
                    (cx + sx * 50 + 0.4 * sx, cy + sy * 30, 1.2), (cx + sx * 50, cy + sy * 30, 1.2)], "mb_red")
    m.build("Track_Field", coll)


# ====================================================================== buildings
def place_block(coll, name, L, D, floors, center, facing, extra=None, **kw):
    mb = MB()
    B.school_block(mb, L, D, floors, **kw)
    if extra:
        extra(mb, L, D, floors)
    loc, rz = place(L, D, center, facing)
    return mb.build(name, coll, loc, rz)


def all_buildings(coll):
    # อาคาร 1 อาคารอำนวยการ หันหน้าไปทางตะวันออก (ลานหน้าเสาธง / ถนนบันไดอิฐ)
    place_block(coll, "B1_Admin", 76, 12, 3, (74, -4), "E", label="label_b1", corridor=3.2,
                extra=B.admin_portico, roof="hip", roof_mat="roof_blue", wall="wall_white",
                trim="trim_pink", parapet="breeze")
    # แถวเหนือ (ระเบียงหันลงใต้สู่สนาม)
    place_block(coll, "B2", 50, 11, 3, (-116, 67.5), "S", label="label_b2", roof="hip",
                roof_mat="roof_orange", wall="wall_cream", trim="trim_blue", parapet="solid", frame="frame_wood",
                door="door")
    place_block(coll, "B3", 54, 11, 3, (-50, 67.5), "S", label="label_b3", roof="gable",
                roof_mat="roof_blue", wall="wall_white", trim="trim_pink", parapet="breeze", open_ground=True,
                roof_pitch=0.6)
    place_block(coll, "B4", 81, 11, 4, (27, 67.5), "S", label="label_b4", label_both=True, roof="hip",
                roof_mat="roof_blue", wall="wall_pinkish", trim="trim_blue", parapet="breeze")
    # แถวใต้ (ระเบียงหันขึ้นเหนือสู่สนาม)
    place_block(coll, "B5", 54, 11, 4, (-114, -76.5), "N", label="label_b5", roof="hip",
                roof_mat="roof_blue", wall="wall_bluish", trim="trim_pink", parapet="rail")
    place_block(coll, "B6", 45, 11, 3, (-55, -76.5), "N", label="label_b6", roof="hip",
                roof_mat="roof_orange", wall="wall_cream", trim="trim_pink", parapet="solid", frame="frame_wood")
    # อาคาร 7 (อาคารปฏิบัติการ 2 ชั้น) มุมตะวันตกเฉียงเหนือ
    place_block(coll, "B7", 40, 10, 2, (-118, 92), "S", label="label_b7", roof="gable",
                roof_mat="roof_grey", wall="wall_cream", trim="trim_blue", parapet="rail", corridor=2.6)
    # อาคาร 8 (4 ชั้น) ด้านใต้ของลานเสาธง
    place_block(coll, "B8", 36, 11, 4, (100, -58), "N", label="label_b8", label_both=True, roof="hip",
                roof_mat="roof_blue", wall="wall_white", trim="trim_pink", parapet="breeze")
    # อาคาร 9 (อาคาร 5 ชั้น ปี 2557) ด้านเหนือของลานเสาธง มีโถงกระจก
    place_block(coll, "B9", 40, 16, 5, (100, 52), "S", label="label_b9", label_both=True, roof="hip",
                roof_mat="roof_blue", wall="wall_white", trim="trim_blue", parapet="rail", corridor=3.0,
                lobby=(3, 6), roof_pitch=0.5,
                extra=lambda mb, L, D, f: B.lobby_canopy(mb, L, D, "label_b9"))
    # โรงยิม อาคารเฉลิมพระเกียรติ ๘๐ พรรษา
    mb = MB()
    B.gym(mb)
    loc, rz = place(60, 42, (8, -85), "N")
    mb.build("Gym_80Phansa", coll, loc, rz)
    # โรงอาหาร / อาคารอเนกประสงค์
    mb = MB()
    B.canteen(mb, 56, 22)
    mb.build("Canteen", coll, (-10, 80, 0), 0.0)
    # หอประชุม หันหน้าไปทางตะวันตก
    mb = MB()
    B.hall(mb, 26, 30)
    mb.build("Hall", coll, (119, -102, 0), math.pi / 2)
    # หอถังสูง
    mb = MB()
    B.water_tower(mb)
    mb.build("WaterTower", coll, (58, 92, 0), 0.0)
    # ศาลาหลวงพ่อป่าแก้ว หันหน้าออกถนน (ตะวันออก)
    mb = MB()
    B.shrine(mb)
    mb.build("Shrine_LuangPhoPaKaeo", coll, (141, 22, 0), -math.pi / 2)
    # ป้อมยาม + ซุ้มประตู + ป้ายหินชื่อโรงเรียน
    mb = MB()
    B.guardhouse(mb)
    mb.build("GuardHouse", coll, (139.8, 2.5, 0), 0.0)
    mb = MB()
    B.gate(mb)
    mb.build("MainGate", coll, (150.0, -5.0, 0), 0.0)
    mb = MB()
    mb.box(-0.6, -3.6, 0, 0.6, 3.6, 0.5, "trim_pink", skip=("nz",))
    mb.box(-0.45, -3.4, 0.5, 0.45, 3.4, 3.2, {"side": "trim_blue", "pz": "gold"})
    mb.plane_sign((0.46, 0, 1.85), 6.6, 2.48, "sign_stone", facing="px")
    for y in (-3.0, 3.0):
        mb.sphere((1.4, y, 0.5), 0.7, "hedge", seg=8, rings=5, scale=(1, 1, 0.75))
    mb.build("SchoolSign", coll, (144.0, -24.0, 0), 0.0)
    # เสาธง
    mb = MB()
    B.flagpole(mb)
    mb.build("Flagpole", coll, (FLAG[0], FLAG[1], 0.03), 0.0)


def structures(coll):
    m = MB()
    # รั้ว
    x0, y0, x1, y1 = CAMPUS
    B.fence_run(m, (x0, y0), (x1, y0), "x")
    B.fence_run(m, (x0, y1), (x1, y1), "x")
    B.fence_run(m, (x0, y0), (x0, y1), "y")
    B.fence_run(m, (x1, y0), (x1, y1), "y", gaps=((-15.3, 5.3),))
    # ทางเดินมีหลังคา
    for (ax, ay), L, rz in (((-141.0, 58.5), 212.0, 0.0), ((-141.0, -67.0), 114.0, 0.0),
                            ((65.0, 13.0), 44.0, math.pi / 2), ((65.0, -65.0), 40.0, math.pi / 2),
                            ((90.0, 41.0), 32.0, 0.0)):
        m.push((ax, ay, 0.02), rz)
        B.walkway(m, L)
        m.pop()
    # อัฒจันทร์ (หันหน้าขึ้นเหนือ)
    m.push((-12.0, -49.5, 0), math.pi)
    B.grandstand(m, 80.0)
    m.pop()
    # แป้นบาส + ตาข่ายตะกร้อ
    for cx in (38.5, 57.5):
        for sy in (-1, 1):
            m.push((cx, -6 + sy * 14.6, 0.045), math.pi / 2)
            B.hoop(m, 0, 0, facing=-sy, z0=0.0)
            m.pop()
    for cx in (8.0, 26.0):
        B.takraw_net(m, cx, 44.0, 7.6)
    # โรงจอดรถจักรยานยนต์นักเรียน + โรงจอดรถครู
    m.push((146.0, -102.0, 0.035), math.pi / 2)
    B.shed(m, 56.0, 7.0)
    m.pop()
    m.push((147.5, 48.0, 0.035), math.pi / 2)
    B.shed(m, 54.0, 6.0, roof="metal_blue")
    m.pop()
    # แปลงเกษตร
    for i in range(9):
        for j in range(2):
            bx = -86 + i * 7.4
            by = 81 + j * 12
            m.box(bx, by, 0, bx + 5.6, by + 9.5, 0.22, {"pz": "vegbed", "all": "soil"}, skip=("nz",))
    m.box(-90, 78, 0, -18, 78.3, 1.1, "railing")
    # โต๊ะม้าหิน
    for x, y in ((-120, 46), (-108, 46), (-96, 46), (-40, 46), (-28, 46), (-140, -58), (-128, -58),
                 (46, -72), (56, -80), (70, -72), (46, -94), (66, -96), (76, 52), (40, 22), (58, 22),
                 (92, 36), (118, 36), (92, -44), (118, -44), (-6, 102), (46, 108 - 10)):
        B.stone_table(m, x, y, R.random() * math.pi)
    # ป้ายถนน + ป้ายเขตโรงเรียน + เสาไฟฟ้า
    for x, y, rot in ((151.9, -60.0, 0.0), (166.4, 60.0, math.pi)):
        m.cyl(x, y, 0.15, 3.2, 0.05, "steel", seg=8)
        m.push((x, y, 2.6), rot)
        m.plane_sign((0.06, 0, 0), 1.2, 1.2, "sign_schoolzone", facing="px")
        m.pop()
    m.cyl(151.9, 12.0, 0.15, 3.6, 0.05, "steel", seg=8)
    m.plane_sign((151.9, 12.0, 3.25), 1.6, 0.7, "sign_road", facing="px", off=0.06)
    m.build("SiteStructures", coll)

    m = MB()   # เสาไฟฟ้า + สายไฟริมถนนบันไดอิฐ
    poles = []
    y = -300.0
    while y <= 300:
        if not (-20 < y < 10):
            poles.append(y)
        y += 38.0
    for y in poles:
        x = 151.6
        m.cyl(x, y, 0.15, 10.5, 0.17, "pole_concrete", seg=8, r2=0.12)
        m.box(x - 0.08, y - 1.0, 9.6, x + 0.08, y + 1.0, 9.75, "pole_concrete")
        m.beam((x, y, 8.8), (x + 1.8, y, 8.4), 0.08, 0.08, "steel")
        m.box(x + 1.6, y - 0.25, 8.1, x + 2.3, y + 0.25, 8.35, "steel")
        m.face([(x + 1.6, y - 0.22, 8.08), (x + 2.3, y - 0.22, 8.08), (x + 2.3, y + 0.22, 8.08), (x + 1.6, y + 0.22, 8.08)],
               "lamp")
    for i in range(len(poles) - 1):
        ya, yb = poles[i], poles[i + 1]
        for dx, dz in ((-0.8, 9.75), (0.0, 9.75), (0.8, 9.75), (0.0, 8.6)):
            pts = []
            for k in range(7):
                t = k / 6
                pts.append((151.6 + dx, ya + (yb - ya) * t, dz - 0.9 * 4 * t * (1 - t)))
            for a, b in zip(pts[:-1], pts[1:]):
                m.beam(a, b, 0.025, 0.025, "cable", caps=False)
    m.build("PowerLines", coll)


# ====================================================================== vegetation
def rain_tree(m, x, y, s=1.0):
    th = 2.6 * s
    m.tube((x, y, 0), (x, y, th), 0.45 * s, 0.34 * s, "bark", seg=7)
    n = R.randint(4, 6)
    tips = []
    for i in range(n):
        a = 2 * math.pi * i / n + R.uniform(-0.3, 0.3)
        d = R.uniform(2.6, 4.2) * s
        tip = (x + d * math.cos(a), y + d * math.sin(a), th + R.uniform(2.2, 3.2) * s)
        m.tube((x, y, th - 0.2), tip, 0.26 * s, 0.1 * s, "bark", seg=6)
        tips.append(tip)
    blobs = tips + [(x, y, th + 3.4 * s)]
    for (bx, by, bz) in blobs:
        r = R.uniform(3.0, 4.2) * s
        m.sphere((bx + R.uniform(-0.5, 0.5), by + R.uniform(-0.5, 0.5), bz + 0.8 * s), r,
                 "leaves" if R.random() < 0.7 else "leaves_light", seg=9, rings=5, scale=(1.0, 1.0, 0.5))


def blob_tree(m, x, y, s=1.0):
    r = R.uniform(2.4, 3.6) * s
    m.tube((x, y, 0), (x, y, 2.0 * s), 0.2 * s, 0.15 * s, "bark", seg=4)
    m.sphere((x, y, 2.0 * s + r * 0.55), r, "leaves" if R.random() < 0.6 else "leaves_light", seg=6, rings=4,
             scale=(1, 1, 0.8))


def round_tree(m, x, y, s=1.0):
    th = 1.8 * s
    m.tube((x, y, 0), (x, y, th + 1.0 * s), 0.22 * s, 0.15 * s, "bark", seg=6)
    for k in range(R.randint(3, 5)):
        a = R.uniform(0, 2 * math.pi)
        d = R.uniform(0.4, 1.4) * s
        m.sphere((x + d * math.cos(a), y + d * math.sin(a), th + R.uniform(1.6, 2.6) * s), R.uniform(1.6, 2.3) * s,
                 "leaves_light" if R.random() < 0.5 else "leaves", seg=8, rings=5, scale=(1, 1, 0.85))


def plumeria(m, x, y, s=1.0):
    """ต้นลีลาวดี (ต้นไม้ประจำโรงเรียน): กิ่งอวบแตกเป็นง่าม ใบรวมเป็นกระจุกที่ปลายกิ่ง ดอกขาวเหลือง"""
    flower = R.choice(["flower_white", "flower_white", "flower_yellow", "flower_pink"])
    trunk_top = (x, y, 1.1 * s)
    m.tube((x, y, 0), trunk_top, 0.17 * s, 0.14 * s, "bark_plumeria", seg=7)

    def branch(p, ang, elev, length, r, depth):
        dx = math.cos(ang) * math.cos(elev)
        dy = math.sin(ang) * math.cos(elev)
        dz = math.sin(elev)
        q = (p[0] + dx * length, p[1] + dy * length, p[2] + dz * length)
        m.tube(p, q, r, r * 0.8, "bark_plumeria", seg=6)
        if depth == 0:
            rosette(q)
            return
        for k in range(R.choice([2, 2, 3])):
            branch(q, ang + R.uniform(-0.8, 0.8), min(1.3, elev + R.uniform(-0.2, 0.35)),
                   length * R.uniform(0.65, 0.85), r * 0.75, depth - 1)

    def rosette(q):
        for ring, n, lift, lmul in ((0, 9, 0.18, 1.0), (1, 6, 0.75, 0.75)):
            for k in range(n):
                a = 2 * math.pi * (k + 0.5 * ring) / n + R.uniform(-0.2, 0.2)
                L = R.uniform(0.6, 0.8) * s * lmul
                wdt = 0.15 * s * lmul
                ca, sa = math.cos(a), math.sin(a)
                ch = math.cos(lift)
                sh = math.sin(lift)
                tip = (q[0] + ca * L * ch, q[1] + sa * L * ch, q[2] + sh * L - 0.08 * L)
                mid = (q[0] + ca * L * 0.45 * ch, q[1] + sa * L * 0.45 * ch, q[2] + sh * L * 0.5)
                left = (mid[0] - sa * wdt, mid[1] + ca * wdt, mid[2])
                right = (mid[0] + sa * wdt, mid[1] - ca * wdt, mid[2])
                m.face([q, right, tip, left], "leaves_plumeria",
                       uv=[(0.5, 0.0), (1.0, 0.45), (0.5, 1.0), (0.0, 0.45)])
        for k in range(3):
            a = 2 * math.pi * k / 3 + R.uniform(0, 1)
            m.sphere((q[0] + 0.1 * math.cos(a) * s, q[1] + 0.1 * math.sin(a) * s, q[2] + 0.16 * s), 0.09 * s,
                     flower, seg=4, rings=2)

    n0 = R.choice([3, 3, 4])
    a0 = R.uniform(0, 2 * math.pi)
    for k in range(n0):
        branch(trunk_top, a0 + 2 * math.pi * k / n0 + R.uniform(-0.3, 0.3), R.uniform(0.55, 0.85),
               R.uniform(0.9, 1.2) * s, 0.12 * s, 2)


def palm(m, x, y, s=1.0):
    h = R.uniform(8.0, 10.0) * s
    m.tube((x, y, 0), (x, y, h * 0.5), 0.3 * s, 0.33 * s, "palm_trunk", seg=8)
    m.tube((x, y, h * 0.5), (x, y, h), 0.33 * s, 0.24 * s, "palm_trunk", seg=8)
    m.tube((x, y, h), (x, y, h + 1.8 * s), 0.25 * s, 0.22 * s, "crownshaft", seg=8)
    top = (x, y, h + 1.8 * s)
    n = 15
    for k in range(n):
        a = 2 * math.pi * k / n + R.uniform(-0.15, 0.15)
        ca, sa = math.cos(a), math.sin(a)
        L = R.uniform(3.4, 4.2) * s
        up = R.uniform(1.0, 2.0)
        prev = None
        for i in range(9):
            t = i / 8
            px = top[0] + ca * L * t
            py = top[1] + sa * L * t
            pz = top[2] + up * s * t - (up + 1.6) * s * t * t
            w = 0.8 * s * math.sin(math.pi * min(1, t * 1.05 + 0.04))
            cur = ((px, py, pz), w)
            if prev:
                (p0, w0), (p1, w1) = prev, cur
                for sgn in (-1, 1):
                    l0 = (p0[0] - sa * w0 * sgn, p0[1] + ca * w0 * sgn, p0[2] - 0.45 * w0)
                    l1 = (p1[0] - sa * w1 * sgn, p1[1] + ca * w1 * sgn, p1[2] - 0.45 * w1)
                    m.face([p0, p1, l1, l0], "palm_leaf", uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
            prev = cur


def vegetation(coll):
    m = MB()
    # ลีลาวดี: สนามหน้า ลานเสาธง รอบศาลา ริมทางเดิน
    plum = [(136, 34), (146, 34), (136, 12), (147, 11), (134, -18), (136, -32), (146, -36), (134, 38),
            (88, 38), (95, 38), (102, 38), (109, 38), (116, 38), (122, 38),
            (88, -46), (95, -46), (102, -46), (109, -46), (116, -46), (122, -46),
            (83, -30), (83, -20), (83, 14), (83, 24), (84, 30), (84, -38),
            (-10, 54), (-30, 54), (-60, 54), (-90, 54), (-120, 54), (10, -62), (-140, 50), (72, 46),
            (60, -62), (40, -62), (-128, -62), (-100, -62)]
    for x, y in plum:
        plumeria(m, x + R.uniform(-0.6, 0.6), y + R.uniform(-0.6, 0.6), R.uniform(1.3, 1.6))
    # ปาล์มริมทางเข้า
    for x in (134.5, 139.0, 143.5, 148.0):
        palm(m, x, -12.5)
        palm(m, x, 2.5)
    m.build("Plumeria_Palms", coll)

    t = MB()
    # จามจุรี/ต้นไม้ใหญ่รอบสนาม และพื้นที่ว่างในโรงเรียน (เลือกตำแหน่งว่างอัตโนมัติ)
    cand = []
    for gx in range(-144, 150, 10):
        for gy in range(-104, 106, 10):
            x = gx + R.uniform(-3, 3)
            y = gy + R.uniform(-3, 3)
            cand.append((x, y))
    placed = []
    for x, y in cand:
        if not (CAMPUS[0] + 3 < x < CAMPUS[2] - 3 and CAMPUS[1] + 3 < y < CAMPUS[3] - 3):
            continue
        if not free(x, y, 5.0):
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < 81 for px, py in placed + plum):
            continue
        placed.append((x, y))
        if R.random() < 0.55:
            rain_tree(t, x, y, R.uniform(0.85, 1.15))
        else:
            round_tree(t, x, y, R.uniform(1.0, 1.4))
    # แถวต้นไม้ริมรั้ว
    for x in range(-144, 146, 11):
        for y in (-104.5, 104.5):
            if free(x, y, 3.0):
                round_tree(t, x + R.uniform(-1, 1), y, R.uniform(0.9, 1.2))
    for y in range(-100, 104, 11):
        if free(-146, y, 2.5):
            round_tree(t, -146, y + R.uniform(-1, 1), R.uniform(0.9, 1.2))
    t.build("Trees_Campus", coll)

    h = MB()   # ไม้พุ่ม / รั้วต้นไม้
    for x0, y0, x1, y1 in ((84.5, -47.5, 124.5, -46.8), (84.5, 39.0, 124.5, 39.7), (132.5, 14, 133.2, 40),
                           (132.5, -40, 133.2, -14), (-140, 61.2, -88, 61.8), (-74, 61.2, -24, 61.8),
                           (-10, 61.2, 64, 61.8), (-140, -71.8, -88, -71.2), (-74, -71.8, -36, -71.2)):
        h.box(x0, y0, 0, x1, y1, 0.75, "hedge", skip=("nz",))
    for k in range(16):
        a = 2 * math.pi * k / 16
        h.sphere((FLAG[0] + 4.6 * math.cos(a), FLAG[1] + 4.6 * math.sin(a), 0.35), 0.55, "hedge", seg=7, rings=4,
                 scale=(1, 1, 0.8))
    for x, y in ((136, 28), (146, 28), (137, 16), (146, 17), (148, -30), (138, -26)):
        h.sphere((x, y, 0.4), 0.9, "hedge", seg=8, rings=5, scale=(1, 1, 0.7))
    h.build("Hedges", coll)
    return placed


# ====================================================================== people
def person(m, x, y, rot, kind="boy_long", top="shirt_white"):
    m.push((x, y, 0.03), rot)
    sk = "skin" if R.random() < 0.6 else "skin2"
    if kind == "girl":
        m.box(-0.12, -0.05, 0, -0.03, 0.05, 0.52, sk, skip=("nz",))
        m.box(0.03, -0.05, 0, 0.12, 0.05, 0.52, sk, skip=("nz",))
        m.box(-0.13, -0.07, 0, -0.02, 0.09, 0.08, "black", skip=("nz",))
        m.box(0.02, -0.07, 0, 0.13, 0.09, 0.08, "black", skip=("nz",))
        m.lathe([(0.27, 0.0), (0.19, 0.45)], 0, 0, "navy", seg=8, z0=0.5, sy=0.75, caps=True)
    else:
        leg = "khaki" if kind == "boy_short" else "navy"
        top_leg = 0.62 if kind == "boy_short" else 0.0
        if kind == "boy_short":
            m.box(-0.12, -0.05, 0, -0.03, 0.05, 0.62, sk, skip=("nz",))
            m.box(0.03, -0.05, 0, 0.12, 0.05, 0.62, sk, skip=("nz",))
        m.box(-0.13, -0.06, top_leg, -0.01, 0.06, 0.95, leg, skip=("nz",))
        m.box(0.01, -0.06, top_leg, 0.13, 0.06, 0.95, leg, skip=("nz",))
        m.box(-0.13, -0.07, 0, -0.02, 0.1, 0.08, "black", skip=("nz",))
        m.box(0.02, -0.07, 0, 0.13, 0.1, 0.08, "black", skip=("nz",))
    m.box(-0.18, -0.1, 0.92, 0.18, 0.1, 1.43, top)
    for sx in (-1, 1):
        m.box(sx * 0.18, -0.06, 1.18, sx * 0.25, 0.06, 1.42, top)
        m.box(sx * 0.185, -0.045, 0.86, sx * 0.24, 0.045, 1.18, sk)
    m.box(-0.045, -0.04, 1.43, 0.045, 0.04, 1.5, sk)
    m.sphere((0, 0.0, 1.6), 0.11, sk, seg=6, rings=4, scale=(1, 1, 1.12))
    m.sphere((0, -0.02, 1.64), 0.118, "hair", seg=6, rings=3, scale=(1, 1, 0.95 if kind != "girl" else 1.05))
    if kind == "girl":
        m.box(-0.11, -0.1, 1.42, 0.11, -0.02, 1.64, "hair")
    m.pop()


def people(coll):
    m = MB()
    # นักเรียนเข้าแถวหน้าเสาธง (หันหน้าไปทางเสาธง/อาคาร 1)
    rot = math.pi / 2
    kinds = ["boy_short", "boy_long", "girl", "girl"]
    for k in range(19):
        y = -31.5 + k * 3.4
        kind = kinds[k % 4]
        for j in range(14):
            x = 103.0 + j * 1.05 + R.uniform(-0.08, 0.08)
            person(m, x, y + R.uniform(-0.08, 0.08), rot + R.uniform(-0.12, 0.12),
                   kind if R.random() > 0.08 else R.choice(kinds))
    # ครูหน้าแถว
    for x, y, c in ((101.0, -8.0, "teacher_1"), (101.0, 0.0, "teacher_2"), (101.5, 12.0, "teacher_3"),
                    (101.5, -20.0, "teacher_1"), (118, 32.5, "teacher_2")):
        person(m, x, y, -math.pi / 2, "boy_long" if c != "teacher_2" else "girl", top=c)
    # นักเรียนเดินเล่น / เล่นกีฬา
    for x, y in ((38, -10), (40, -2), (36, 2), (55, -12), (58, -4), (60, 4), (8, 42), (9, 46), (26, 42), (25, 46),
                 (-40, 20), (-60, -20), (-46, -6), (-70, 4), (-20, 10), (10, 90), (20, 86), (30, 92), (0, 88),
                 (-60, 46), (-58, 47), (-30, -60), (-31, -61), (140, -60), (141, -66), (128, 20), (128, -30)):
        person(m, x + R.uniform(-1, 1), y + R.uniform(-1, 1), R.uniform(0, 2 * math.pi), R.choice(kinds))
    # ยามหน้าป้อม
    person(m, 146.0, 5.5, -math.pi / 2, "boy_long", top="teacher_1")
    m.build("Students_Teachers", coll)


# ====================================================================== vehicles
def car(m, x, y, rot, colr):
    m.push((x, y, 0.04), rot)
    m.box(-2.2, -0.86, 0.3, 2.2, 0.86, 0.85, colr)
    m.box(-1.2, -0.78, 0.85, 1.0, 0.78, 1.38, "glass")
    m.box(-1.1, -0.74, 1.38, 0.9, 0.74, 1.45, colr)
    m.box(1.0, -0.8, 0.85, 1.25, 0.8, 0.9, colr)
    for sx in (-1.35, 1.35):
        for sy in (-0.8, 0.8):
            m.tube((sx, sy - 0.12, 0.32), (sx, sy + 0.12, 0.32), 0.32, 0.32, "tire", seg=10, caps=True)
    m.box(2.2, -0.7, 0.55, 2.23, -0.4, 0.7, "lamp")
    m.box(2.2, 0.4, 0.55, 2.23, 0.7, 0.7, "lamp")
    m.pop()


def motorbike(m, x, y, rot, colr):
    m.push((x, y, 0.04), rot)
    for sx in (-0.62, 0.62):
        m.tube((sx, -0.05, 0.29), (sx, 0.05, 0.29), 0.29, 0.29, "tire", seg=10, caps=True)
    m.box(-0.55, -0.15, 0.4, 0.45, 0.15, 0.72, colr)
    m.box(-0.6, -0.14, 0.72, 0.1, 0.14, 0.82, "black")
    m.beam((0.62, 0, 0.3), (0.42, 0, 1.0), 0.06, 0.06, "chrome")
    m.beam((0.42, -0.35, 1.02), (0.42, 0.35, 1.02), 0.04, 0.04, "black")
    m.box(0.35, -0.12, 0.75, 0.6, 0.12, 0.98, colr)
    m.pop()


def vehicles(coll):
    m = MB()
    cols = ["car_white", "car_silver", "car_red", "car_blue", "car_black", "car_grey", "car_white", "car_silver"]
    for k in range(13):
        car(m, 143.5, 50.5 + k * 3.9 + R.uniform(-0.2, 0.2), math.pi + R.uniform(-0.04, 0.04), R.choice(cols))
    for k in range(8):
        car(m, 136.0, 54 + k * 6.0, R.uniform(-0.05, 0.05), R.choice(cols))
    mbs = ["mb_red", "mb_black", "mb_blue", "mb_white", "mb_pink", "mb_black", "mb_red"]
    for row in range(2):
        for k in range(64):
            x = 141.0 + row * 2.2
            y = -101.0 + k * 0.85
            if R.random() < 0.88:
                motorbike(m, x + R.uniform(-0.1, 0.1), y, (math.pi if row else 0.0) + R.uniform(-0.15, 0.15),
                          R.choice(mbs))
    for k in range(16):
        motorbike(m, 135.5, -100 + k * 0.9, R.uniform(-0.2, 0.2), R.choice(mbs))
    # รถบนถนน
    for x, y, rot, c in ((156.0, -60, math.pi / 2, "car_white"), (162.0, 40, -math.pi / 2, "car_red"),
                         (156.0, 120, math.pi / 2, "car_grey"), (162.0, -150, -math.pi / 2, "car_blue")):
        car(m, x, y, rot, c)
    for x, y, rot in ((156.4, -28, math.pi / 2), (161.6, 70, -math.pi / 2), (156.5, 20, math.pi / 2)):
        motorbike(m, x, y, rot, R.choice(mbs))
    m.build("Vehicles", coll)


# ====================================================================== surroundings
def shophouse(m, x0, y0, floors, colr, sign, w=4.0, d=12.0):
    """ตึกแถว หน้าร้านหันไปทาง -x (ถนน)"""
    h = 3.4 * floors
    m.box(x0, y0, 0, x0 + d, y0 + w, h, {"side": colr, "pz": "concrete"}, skip=("nz",))
    front = [(x0 - 0.03, y0 + w - 0.3, 0.15), (x0 - 0.03, y0 + 0.3, 0.15), (x0 - 0.03, y0 + 0.3, 2.9),
             (x0 - 0.03, y0 + w - 0.3, 2.9)]
    if R.random() < 0.35:
        m.face(front, "shutter")          # ร้านปิด (ประตูเหล็กม้วน)
    else:
        m.face(front, "dark")             # ร้านเปิด
        m.box(x0 - 0.9, y0 + 0.5, 0.0, x0 - 0.1, y0 + w - 0.5, 0.8, "steel")
    m.box(x0 - 1.2, y0, 3.0, x0, y0 + w, 3.15, "concrete_paint")
    m.plane_sign((x0 - 1.22, y0 + w / 2, 3.6), w - 0.4, 0.9, sign, facing="nx")
    for f in range(1, floors):
        z = 3.4 * f
        m.face([(x0 - 0.02, y0 + w - 0.5, z + 0.9), (x0 - 0.02, y0 + 0.5, z + 0.9), (x0 - 0.02, y0 + 0.5, z + 2.6),
                (x0 - 0.02, y0 + w - 0.5, z + 2.6)], "glass")
        m.box(x0 - 0.8, y0 + 0.1, z, x0, y0 + w - 0.1, z + 0.12, "concrete_paint")
        m.box(x0 - 0.8, y0 + 0.1, z + 0.12, x0 - 0.75, y0 + w - 0.1, z + 1.0, "railing")
    m.box(x0 - 0.1, y0, h, x0 + d, y0 + w, h + 0.8, colr, skip=("nz",))


def house(m, x, y, rot, s=1.0):
    m.push((x, y, 0), rot)
    w, d = R.uniform(7, 10) * s, R.uniform(8, 12) * s
    wall = R.choice(["wall_cream", "wall_white", "sh_0", "sh_1", "sh_3", "sh_5"])
    roofm = R.choice(["roof_orange", "roof_grey", "roof_red", "roof_blue", "roof_green"])
    fl = 1 if R.random() < 0.6 else 2
    hh = 3.0 * fl
    m.box(0, 0, 0, w, d, 0.4, "concrete", skip=("nz",))
    m.box(0.2, 0.2, 0.4, w - 0.2, d - 0.2, hh + 0.4, wall, skip=("nz",))
    for k in range(int(w // 3)):
        xx = 1.0 + k * 3
        for f in range(fl):
            m.face([(xx, 0.17, 1.3 + f * 3), (xx + 1.4, 0.17, 1.3 + f * 3), (xx + 1.4, 0.17, 2.6 + f * 3),
                    (xx, 0.17, 2.6 + f * 3)], "glass")
    m.hip_roof(-0.5, -0.5, w + 0.5, d + 0.5, hh + 0.4, min(w, d) * 0.3, roofm, fascia="trim_white")
    m.pop()


def surroundings(coll):
    m = MB()
    # ตึกแถวฝั่งตรงข้ามถนน
    k = 0
    for y0, y1 in ((-150, -66), (-56, 26), (36, 120), (130, 214)):
        y = y0
        while y + 4 <= y1:
            shophouse(m, 168.6, y, R.choice([2, 2, 3, 3, 4]), "sh_%d" % R.randrange(8), "shop_%d" % (k % 12))
            y += 4.0
            k += 1
    # บ้านพักอาศัยรอบ ๆ
    h = MB()
    spots = []
    for gx in range(-560, 560, 26):
        for gy in range(-560, 560, 26):
            x = gx + R.uniform(-6, 6)
            y = gy + R.uniform(-6, 6)
            if -170 < x < 200 and -125 < y < 125:
                continue
            if 150 < x < 215 and -170 < y < 230:
                continue
            if ((x - KW_C[0]) / 470) ** 2 + ((y - KW_C[1]) / 270) ** 2 < 1.0:
                continue
            if abs(y - 113) < 10 or abs(y + 113) < 10 or abs(x - 159) < 14 or abs(x + 155) < 10:
                continue
            if R.random() < 0.55:
                spots.append((x, y))
    for x, y in spots:
        house(h, x, y, R.choice([0, math.pi / 2, math.pi, -math.pi / 2]) + R.uniform(-0.08, 0.08))
    t = MB()
    for gx in range(-700, 700, 21):
        for gy in range(-700, 700, 21):
            x = gx + R.uniform(-7, 7)
            y = gy + R.uniform(-7, 7)
            if -158 < x < 170 and -116 < y < 116:
                continue
            if 150 < x < 185 and -160 < y < 220:
                continue
            if ((x - KW_C[0]) / 450) ** 2 + ((y - KW_C[1]) / 250) ** 2 < 1.0:
                continue
            if any((x - sx) ** 2 + (y - sy) ** 2 < 64 for sx, sy in spots[-400:] if abs(sx - x) < 9):
                continue
            if abs(x - 159) < 9 or abs(y - 113) < 5 or abs(y + 113) < 5:
                continue
            if R.random() < 0.42:
                if R.random() < 0.04:
                    palm(t, x, y, R.uniform(0.7, 0.9))
                else:
                    blob_tree(t, x, y, R.uniform(0.9, 1.4))
    m.build("Shophouses", coll)
    h.build("Houses", coll)
    t.build("Trees_Around", coll)


# ====================================================================== Khao Wang (Phra Nakhon Khiri)
def kw_height(x, y):
    cx, cy = KW_C
    r2 = ((x - cx) / 430.0) ** 2 + ((y - cy) / 245.0) ** 2
    base = 34.0 * max(0.0, 1.0 - r2) ** 1.25
    h = base
    for px, py, ph in KW_PEAKS:
        d2 = ((x - px) / 100.0) ** 2 + ((y - py) / 85.0) ** 2
        h += ph * math.exp(-d2 * 1.6) * min(1.0, max(0.0, (1 - r2) * 3))
    h += (2.2 * math.sin(x * 0.031 + 1.3) * math.cos(y * 0.027 + 0.4) + 1.3 * math.sin(x * 0.071 + y * 0.053)) \
        * min(1.0, h / 25.0)
    for px, py, ph in KW_PEAKS:
        d = math.hypot(x - px, y - py)
        rf = 26.0
        if d < rf + 18:
            t = min(1.0, max(0.0, (d - rf) / 18.0))
            t = t * t * (3 - 2 * t)
            hc = kw_peak_top(px, py, ph)
            h = h * t + hc * (1 - t)
    return h - 0.25


_PEAK_CACHE = {}


def kw_peak_top(px, py, ph):
    key = (px, py)
    if key not in _PEAK_CACHE:
        cx, cy = KW_C
        r2 = ((px - cx) / 430.0) ** 2 + ((py - cy) / 245.0) ** 2
        h = 34.0 * max(0.0, 1.0 - r2) ** 1.25
        for qx, qy, qh in KW_PEAKS:
            d2 = ((px - qx) / 100.0) ** 2 + ((py - qy) / 85.0) ** 2
            h += qh * math.exp(-d2 * 1.6) * min(1.0, max(0.0, (1 - r2) * 3))
        _PEAK_CACHE[key] = h
    return _PEAK_CACHE[key]


def bell_chedi(m, x, y, z, s=1.0, mat="chedi_white"):
    prof = [(13, 0), (13, 1.4), (11.6, 1.4), (11.6, 2.8), (10.3, 2.8), (10.3, 4.1), (9.3, 4.1), (9.3, 5.0),
            (9.6, 5.6), (9.8, 7.5), (9.5, 9.6), (8.7, 11.8), (7.4, 13.6), (5.6, 15.0), (3.4, 16.0), (0.0, 16.2)]
    m.lathe([(r * s, h * s) for r, h in prof], x, y, mat, seg=32, z0=z)
    m.box(x - 2.8 * s, y - 2.8 * s, z + 15.8 * s, x + 2.8 * s, y + 2.8 * s, z + 18.4 * s, mat)
    rings = []
    zz = 18.4
    r = 2.1
    while r > 0.3:
        rings += [(r, zz), (r * 0.86, zz + 0.25), (r * 0.9, zz + 0.55)]
        zz += 0.6
        r *= 0.88
    rings.append((0.0, zz + 2.5))
    m.lathe([(rr * s, hh * s) for rr, hh in rings[:-1]], x, y, mat, seg=16, z0=z, caps=False)
    m.lathe([(0.3 * s, zz * s), (0.0, (zz + 3.0) * s)], x, y, "gold", seg=12, z0=z, caps=True)


def prang(m, x, y, z, s=1.0, mat="prang_red"):
    prof = [(4.6, 0), (4.6, 2.6), (4.0, 2.6), (4.0, 4.8), (3.5, 5.0), (3.5, 7.0), (3.3, 9.0), (3.0, 10.2),
            (2.6, 11.6), (2.1, 13.0), (1.5, 14.2), (0.8, 15.2), (0.3, 16.0), (0.0, 16.4)]
    m.lathe([(r * s, h * s) for r, h in prof], x, y, mat, seg=12, z0=z, phase=math.pi / 12)
    m.lathe([(0.12 * s, 16.0 * s), (0.0, 18.5 * s)], x, y, "gold", seg=8, z0=z)
    for k in range(4):
        a = k * math.pi / 2
        m.box(x + math.cos(a) * 4.6 * s - 1.2 * s, y + math.sin(a) * 4.6 * s - 1.2 * s, z,
              x + math.cos(a) * 4.6 * s + 1.2 * s, y + math.sin(a) * 4.6 * s + 1.2 * s, z + 4.0 * s, mat)


def thai_hall(m, x, y, z, L, W, rot, wall="palace_wall", roof="roof_orange", tiers=2, h=6.0):
    m.push((x, y, z), rot)
    m.box(-L / 2 - 1.0, -W / 2 - 1.0, -1.5, L / 2 + 1.0, W / 2 + 1.0, 0.6, {"pz": "floor_tile", "all": "wall_white"})
    m.box(-L / 2, -W / 2, 0.6, L / 2, W / 2, h, wall, skip=("nz",))
    for k in range(int(L // 3)):
        xx = -L / 2 + 1.5 + k * 3
        m.face([(xx - 0.5, -W / 2 - 0.02, 1.8), (xx + 0.5, -W / 2 - 0.02, 1.8), (xx + 0.5, -W / 2 - 0.02, 4.4),
                (xx - 0.5, -W / 2 - 0.02, 4.4)], "door")
        m.face([(xx + 0.5, W / 2 + 0.02, 1.8), (xx - 0.5, W / 2 + 0.02, 1.8), (xx - 0.5, W / 2 + 0.02, 4.4),
                (xx + 0.5, W / 2 + 0.02, 4.4)], "door")
    for t in range(tiers):
        sh = 1.0 - 0.18 * t
        m.gable_roof(-L / 2 * sh, -W / 2, L / 2 * sh, W / 2, h + t * 1.6, W / 2 * 1.0, roof,
                     gable="red_lacquer", oh=0.6, eave=1.4 - 0.4 * t, barge="gold", thai=(t == tiers - 1),
                     finial="gold", ridge="gold")
    m.pop()


def khao_wang(coll):
    # ภูมิประเทศ
    tm = MB()
    xs = [x for x in range(-520, 470, 6)]
    ys = [y for y in range(132, 672, 6)]
    rows = [[(x, y, max(-0.3, kw_height(x, y))) for x in xs] for y in ys]
    tm.grid(rows, "hill", smooth=True, closed=False, uvscale=((xs[-1] - xs[0]) / 60.0, (ys[-1] - ys[0]) / 60.0))
    tm.build("KhaoWang_Terrain", coll)
    # ต้นไม้บนเขา
    tr = MB()
    for i in range(1700):
        x = R.uniform(-470, 420)
        y = R.uniform(150, 640)
        h = kw_height(x, y)
        if h < 2.0:
            continue
        if any(math.hypot(x - px, y - py) < 34 for px, py, _ in KW_PEAKS):
            continue
        r = R.uniform(3.2, 6.5)
        tr.sphere((x, y, h + r * 0.55), r, "leaves" if R.random() < 0.6 else "leaves_light", seg=6, rings=3,
                  scale=(1, 1, 0.8))
    tr.build("KhaoWang_Trees", coll)
    # สิ่งก่อสร้างบนยอดเขา
    m = MB()
    (wx, wy, wh), (mx, my, mh), (ex, ey, eh) = KW_PEAKS
    # ยอดกลาง: พระธาตุจอมเพชร (เจดีย์ทรงระฆังสีขาว)
    zm = kw_peak_top(mx, my, mh) - 0.25
    m.box(mx - 22, my - 22, zm - 12, mx + 22, my + 22, zm + 0.3, {"pz": "paving", "all": "rock"})
    bell_chedi(m, mx, my, zm + 0.3, 1.25)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        bell_chedi(m, mx + 17 * math.cos(a), my + 17 * math.sin(a), zm + 0.3, 0.22)
    thai_hall(m, mx, my - 26, zm - 1.0, 16, 9, 0.0, roof="roof_orange", tiers=2, h=5.0)
    # ยอดตะวันตก: พระราชวัง (พระที่นั่งเพชรภูมิไพโรจน์, หอชัชวาลเวียงชัย, พระที่นั่งเวชยันตวิเชียรปราสาท)
    zw = kw_peak_top(wx, wy, wh) - 0.25
    m.box(wx - 34, wy - 28, zw - 14, wx + 34, wy + 28, zw + 0.3, {"pz": "paving", "all": "rock"})
    for x0, y0, x1, y1 in ((wx - 34, wy - 28, wx + 34, wy - 27), (wx - 34, wy + 27, wx + 34, wy + 28),
                           (wx - 34, wy - 28, wx - 33, wy + 28), (wx + 33, wy - 28, wx + 34, wy + 28)):
        m.box(x0, y0, zw + 0.3, x1, y1, zw + 3.2, "palace_wall")
        L = max(x1 - x0, y1 - y0)
        n = int(L / 2.2)
        for k in range(n):
            t = (k + 0.5) / n
            cx_ = x0 + (x1 - x0) * t if x1 - x0 > 2 else (x0 + x1) / 2
            cy_ = y0 + (y1 - y0) * t if y1 - y0 > 2 else (y0 + y1) / 2
            m.box(cx_ - 0.5, cy_ - 0.5, zw + 3.2, cx_ + 0.5, cy_ + 0.5, zw + 4.0, "palace_wall")
    m.box(wx - 14, wy - 6, zw + 0.3, wx + 14, wy + 6, zw + 7.5, "palace_wall", skip=("nz",))
    for k in range(10):
        xx = wx - 12.6 + k * 2.8
        m.face([(xx - 0.6, wy - 6.02, zw + 1.6), (xx + 0.6, wy - 6.02, zw + 1.6), (xx + 0.6, wy - 6.02, zw + 5.2),
                (xx - 0.6, wy - 6.02, zw + 5.2)], "door_blue")
    m.hip_roof(wx - 15.5, wy - 7.5, wx + 15.5, wy + 7.5, zw + 7.5, 4.2, "roof_orange", fascia="trim_white",
               ridge="ridge")
    # หอชัชวาลเวียงชัย (หอดูดาว ทรงกระบอกหลังคาโดม)
    hx, hy = wx + 20, wy - 12
    m.cyl(hx, hy, zw + 0.3, zw + 13.0, 3.4, "palace_wall", seg=24)
    m.cyl(hx, hy, zw + 12.6, zw + 13.4, 3.7, "trim_white", seg=24)
    m.sphere((hx, hy, zw + 13.4), 3.3, "chedi_white", seg=20, rings=8, scale=(1, 1, 0.9))
    m.cyl(hx, hy, zw + 16.2, zw + 18.0, 0.7, "palace_wall", seg=12, r2=0.5)
    for k in range(6):
        a = k * math.pi / 3
        m.face([(hx + 3.42 * math.cos(a - 0.12), hy + 3.42 * math.sin(a - 0.12), zw + 5),
                (hx + 3.42 * math.cos(a + 0.12), hy + 3.42 * math.sin(a + 0.12), zw + 5),
                (hx + 3.42 * math.cos(a + 0.12), hy + 3.42 * math.sin(a + 0.12), zw + 8),
                (hx + 3.42 * math.cos(a - 0.12), hy + 3.42 * math.sin(a - 0.12), zw + 8)], "dark")
    # พระที่นั่งเวชยันตวิเชียรปราสาท (ปราสาทยอดปรางค์สีขาว)
    px_, py_ = wx - 20, wy + 12
    m.box(px_ - 6, py_ - 6, zw + 0.3, px_ + 6, py_ + 6, zw + 7.0, "palace_wall")
    for rz in (0.0, math.pi / 2):
        m.push((px_, py_, 0), rz)
        m.gable_roof(-7.5, -3.2, 7.5, 3.2, zw + 7.0, 3.0, "roof_grey", gable="palace_wall", oh=0.5, eave=0.8,
                     barge="gold", thai=True, finial="gold")
        m.pop()
    prang(m, px_, py_, zw + 9.6, 0.7, mat="chedi_white")
    # ยอดตะวันออก: วัดพระแก้ว (พระอุโบสถ, พระปรางค์แดง, พระสุทธเสลเจดีย์)
    ze = kw_peak_top(ex, ey, eh) - 0.25
    m.box(ex - 26, ey - 24, ze - 12, ex + 26, ey + 24, ze + 0.3, {"pz": "paving", "all": "rock"})
    thai_hall(m, ex - 6, ey - 8, ze + 0.3, 20, 10, 0.0, roof="roof_orange", tiers=2, h=6.0)
    prang(m, ex + 14, ey + 10, ze + 0.3, 1.0)
    bell_chedi(m, ex - 14, ey + 12, ze + 0.3, 0.7)
    m.build("KhaoWang_Landmarks", coll)


# ====================================================================== distant mountains (เทือกเขาตะนาวศรี ด้านตะวันตก)
def distant_hills(coll):
    m = MB()
    rows = []
    rr = [3800 + 450 * i for i in range(14)]
    for r in rr:
        row = []
        for k in range(120):
            th = 2 * math.pi * k / 120
            w = max(0.0, -math.cos(th) + 0.25) / 1.25       # สูงทางตะวันตก ต่ำทางตะวันออก (อ่าวไทย)
            prof = 0.55 + 0.25 * math.sin(3 * th + 1.0) + 0.2 * math.sin(7 * th + 2.3) + 0.12 * math.sin(13 * th)
            bump = math.sin(math.pi * (r - rr[0]) / (rr[-1] - rr[0])) ** 1.5
            h = 520.0 * w * prof * bump + 40 * math.sin(r * 0.004 + th * 5) * bump
            row.append((r * math.cos(th), r * math.sin(th), max(-1.0, h)))
        rows.append(row)
    rows = list(reversed(rows))
    m.grid(rows, "mountain_far", smooth=True, closed=True)
    m.build("DistantMountains", coll)


def details(coll):
    m = MB()
    # แปลงดอกไม้รอบลานเสาธงและหน้าอาคาร
    fl = ["flower_pink", "flower_yellow", "flower_white", "mb_red"]
    for x0, y0, x1, y1 in ((86, 30.5, 98, 32.5), (110, 30.5, 122, 32.5), (86, -42.5, 98, -40.5), (110, -42.5, 122, -40.5),
                           (134, 30, 140, 32), (134, -38, 140, -36), (88.5, -15, 89.5, 7)):
        m.box(x0, y0, 0, x1, y1, 0.3, {"pz": "soil", "all": "trim_white"}, skip=("nz",))
        nx_, ny_ = max(1, int((x1 - x0) / 0.5)), max(1, int((y1 - y0) / 0.5))
        for i in range(nx_):
            for j in range(ny_):
                cx_ = x0 + (i + 0.5) * (x1 - x0) / nx_
                cy_ = y0 + (j + 0.5) * (y1 - y0) / ny_
                m.sphere((cx_, cy_, 0.42), 0.2, "hedge", seg=5, rings=3)
                if R.random() < 0.7:
                    m.sphere((cx_ + R.uniform(-0.1, 0.1), cy_ + R.uniform(-0.1, 0.1), 0.6), 0.09,
                             fl[(i // 3 + j) % 4], seg=5, rings=3)
    # ถังขยะแยกประเภท 4 สี
    bins = ["trim_blue", "flower_yellow", "hedge", "mb_red"]
    for bx, by in ((-12, 92), (47, 92), (126.2, 34), (126.2, -42), (84.5, 34), (30, -26), (-60, 50), (-100, -62)):
        for k, c in enumerate(bins):
            m.cyl(bx + k * 0.55 if bx < 120 else bx, by + (0 if bx < 120 else k * 0.55), 0.0, 0.9, 0.24, c, seg=10)
    # ม้านั่งริมทางเดิน
    for x in range(-136, 64, 12):
        m.box(x, 55.4, 0.42, x + 1.8, 55.8, 0.48, "bench_stone")
        for dx in (0.2, 1.6):
            m.box(x + dx - 0.05, 55.45, 0, x + dx + 0.05, 55.75, 0.42, "bench_stone", skip=("nz",))
    # เสาไฟในโรงเรียน
    for y in range(-100, 104, 18):
        m.cyl(124.3, y, 0.0, 6.5, 0.07, "steel_white", seg=8)
        m.beam((124.3, y, 6.4), (125.6, y, 6.6), 0.06, 0.06, "steel_white")
        m.box(125.4, y - 0.18, 6.45, 126.0, y + 0.18, 6.65, "steel_white")
    # ศาลาที่พักผู้โดยสารริมถนน
    m.box(165.8, 24, 0.15, 167.4, 30, 0.2, "concrete")
    for yy in (24.2, 29.8):
        m.box(166.9, yy - 0.06, 0.2, 167.1, yy + 0.06, 2.7, "steel_blue")
    m.box(165.4, 23.8, 2.7, 167.6, 30.2, 2.82, "metal_blue")
    m.box(167.2, 24.2, 0.2, 167.3, 29.8, 2.1, "glass_light")
    m.box(166.3, 24.6, 0.55, 167.0, 29.4, 0.62, "steel")
    # รถสองแถวเพชรบุรี
    for x, y, rot, c in ((156.2, -110.0, math.pi / 2, "car_blue"), (161.8, 150.0, -math.pi / 2, "mb_white")):
        m.push((x, y, 0.04), rot)
        m.box(-2.6, -0.9, 0.35, 2.6, 0.9, 1.0, c)
        m.box(1.0, -0.85, 1.0, 2.0, 0.85, 1.55, "glass")
        m.box(1.1, -0.85, 1.55, 2.0, 0.85, 1.65, c)
        m.box(-2.6, -0.92, 1.0, 0.95, 0.92, 1.1, "steel")
        for yy in (-0.9, 0.9):
            for xx in (-2.5, -0.2, 0.9):
                m.box(xx, yy - 0.04, 1.1, xx + 0.08, yy + 0.04, 2.05, "steel")
        m.box(-2.7, -1.0, 2.05, 1.0, 1.0, 2.15, c)
        for sx in (-1.7, 1.6):
            for sy in (-0.82, 0.82):
                m.tube((sx, sy - 0.13, 0.36), (sx, sy + 0.13, 0.36), 0.36, 0.36, "tire", seg=10, caps=True)
        m.pop()
    m.build("Details", coll)


# ====================================================================== all
def build_all():
    c_bld = collection("Buildings")
    c_site = collection("Site")
    c_veg = collection("Vegetation")
    c_ppl = collection("People")
    c_veh = collection("Vehicles")
    c_sur = collection("Surroundings")
    c_kw = collection("KhaoWang")
    ground(c_site)
    track(c_site)
    all_buildings(c_bld)
    structures(c_site)
    vegetation(c_veg)
    people(c_ppl)
    vehicles(c_veh)
    surroundings(c_sur)
    details(c_site)
    distant_hills(c_sur)
    khao_wang(c_kw)
