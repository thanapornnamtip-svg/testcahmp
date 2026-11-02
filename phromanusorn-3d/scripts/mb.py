"""ตัวช่วยสร้าง mesh (MeshBuilder) + ระบบวัสดุ สำหรับ Blender 5.x

ทุกชิ้นส่วนถูกรวมเป็น mesh เดียวต่อกลุ่ม (เช่น 1 อาคาร = 1 object หลายวัสดุ)
เพื่อให้ไฟล์ .glb เบาและเปิดในมือถือได้
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXDIR = os.path.join(ROOT, "textures")

MATS = {}
TS = {}  # เมตรต่อการวนซ้ำ 1 รอบของเท็กซ์เจอร์ (ใช้กับ UV แบบอิงพิกัดโลก)


# ---------------------------------------------------------------- colours
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def col(h, a=1.0):
    if isinstance(h, (tuple, list)):
        r, g, b = h[:3]
        return (_lin(r), _lin(g), _lin(b), a)
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (_lin(r), _lin(g), _lin(b), a)


def _set(node, key, val):
    if key in node.inputs:
        try:
            node.inputs[key].default_value = val
        except Exception:
            pass


def image(name):
    return bpy.data.images.load(os.path.join(TEXDIR, name), check_existing=True)


def mat(name, color="#ffffff", rough=0.7, metal=0.0, tex=None, scale=1.0, clip=False,
        emit=None, emit_str=0.0, spec=0.5, coat=0.0):
    """สร้าง/คืนวัสดุแบบ Principled BSDF (ส่งออก glTF ได้ครบ)"""
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
    if not out.inputs["Surface"].is_linked:
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    _set(bsdf, "Base Color", col(color))
    _set(bsdf, "Roughness", rough)
    _set(bsdf, "Metallic", metal)
    _set(bsdf, "Specular IOR Level", spec)
    if coat:
        _set(bsdf, "Coat Weight", coat)
    if tex:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = image(tex)
        tn.location = (-420, 200)
        nt.links.new(tn.outputs["Color"], bsdf.inputs["Base Color"])
        if clip:
            rn = nt.nodes.new("ShaderNodeMath")
            rn.operation = "ROUND"
            rn.location = (-180, -100)
            nt.links.new(tn.outputs["Alpha"], rn.inputs[0])
            nt.links.new(rn.outputs[0], bsdf.inputs["Alpha"])
    if emit:
        _set(bsdf, "Emission Color", col(emit))
        _set(bsdf, "Emission Strength", emit_str)
    m.diffuse_color = col(color)
    m.roughness = rough
    m.metallic = metal
    TS[name] = scale
    MATS[name] = m
    return m


# ---------------------------------------------------------------- mesh builder
class MB:
    def __init__(self):
        self.v = []
        self.f = []
        self.uv = []
        self.m = []
        self.sm = []
        self.mats = []
        self.mi = {}
        self.T = Matrix.Identity(4)
        self.stack = []

    # transform stack -------------------------------------------------------
    def push(self, loc=(0, 0, 0), rz=0.0, s=None, rx=0.0, ry=0.0):
        self.stack.append(self.T.copy())
        M = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rz, 4, "Z")
        if rx:
            M = M @ Matrix.Rotation(rx, 4, "X")
        if ry:
            M = M @ Matrix.Rotation(ry, 4, "Y")
        if s is not None:
            if isinstance(s, (int, float)):
                s = (s, s, s)
            M = M @ Matrix.Diagonal((s[0], s[1], s[2], 1.0))
        self.T = self.T @ M

    def pop(self):
        self.T = self.stack.pop()

    def _mid(self, name):
        i = self.mi.get(name)
        if i is None:
            i = self.mi[name] = len(self.mats)
            self.mats.append(name)
        return i

    @staticmethod
    def _auto_uv(P, m):
        s = TS.get(m, 1.0)
        n = (P[1] - P[0]).cross(P[2] - P[0])
        if n.length < 1e-12 and len(P) > 3:
            n = (P[2] - P[0]).cross(P[3] - P[0])
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        if az >= ax and az >= ay:
            return [(p.x / s, p.y / s) for p in P]
        if ax >= ay:
            return [(p.y / s, p.z / s) for p in P]
        return [(p.x / s, p.z / s) for p in P]

    # primitives ------------------------------------------------------------
    def face(self, pts, m, uv=None, smooth=False):
        T = self.T
        P = [T @ Vector(p) for p in pts]
        b = len(self.v)
        self.v.extend(P)
        self.f.append(tuple(range(b, b + len(P))))
        self.m.append(self._mid(m))
        self.sm.append(smooth)
        self.uv.append(uv if uv is not None else self._auto_uv(P, m))

    def box(self, x0, y0, z0, x1, y1, z1, m, skip=()):
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        if z0 > z1:
            z0, z1 = z1, z0
        if isinstance(m, str):
            g = lambda k: m
        else:
            def g(k):
                if k in m:
                    return m[k]
                if k in ("px", "nx", "py", "ny") and "side" in m:
                    return m["side"]
                return m.get("all", m.get("side", next(iter(m.values()))))
        F = {
            "nz": [(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)],
            "pz": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
            "ny": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
            "py": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
            "nx": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
            "px": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        }
        for k, pts in F.items():
            if k not in skip:
                self.face(pts, g(k))

    def boxc(self, c, size, m, rz=0.0, skip=()):
        self.push(c, rz)
        sx, sy, sz = size
        self.box(-sx / 2, -sy / 2, -sz / 2, sx / 2, sy / 2, sz / 2, m, skip)
        self.pop()

    def quad_uv(self, p0, p1, p2, p3, m, uv=((0, 0), (1, 0), (1, 1), (0, 1))):
        self.face([p0, p1, p2, p3], m, uv=list(uv))

    def plane_sign(self, center, w, h, m, facing="ny", off=0.0):
        """ป้าย (ภาพ 0..1) ตั้งฉากกับแกน facing"""
        cx, cy, cz = center
        hw, hh = w / 2, h / 2
        if facing == "ny":
            y = cy - off
            pts = [(cx - hw, y, cz - hh), (cx + hw, y, cz - hh), (cx + hw, y, cz + hh), (cx - hw, y, cz + hh)]
        elif facing == "py":
            y = cy + off
            pts = [(cx + hw, y, cz - hh), (cx - hw, y, cz - hh), (cx - hw, y, cz + hh), (cx + hw, y, cz + hh)]
        elif facing == "px":
            x = cx + off
            pts = [(x, cy - hw, cz - hh), (x, cy + hw, cz - hh), (x, cy + hw, cz + hh), (x, cy - hw, cz + hh)]
        else:  # nx
            x = cx - off
            pts = [(x, cy + hw, cz - hh), (x, cy - hw, cz - hh), (x, cy - hw, cz + hh), (x, cy + hw, cz + hh)]
        self.quad_uv(*pts, m)

    def beam(self, p0, p1, w, h, m, up=(0, 0, 1), caps=True):
        p0 = Vector(p0)
        p1 = Vector(p1)
        a = p1 - p0
        if a.length < 1e-6:
            return
        u = a.normalized()
        side = u.cross(Vector(up))
        if side.length < 1e-6:
            side = u.cross(Vector((1, 0, 0)))
        side.normalize()
        vert = side.cross(u).normalized()
        sw, vh = side * (w / 2), vert * (h / 2)
        c0 = [p0 - sw - vh, p0 + sw - vh, p0 + sw + vh, p0 - sw + vh]
        c1 = [p1 - sw - vh, p1 + sw - vh, p1 + sw + vh, p1 - sw + vh]
        for i in range(4):
            j = (i + 1) % 4
            self.face([c0[i], c0[j], c1[j], c1[i]], m)
        if caps:
            self.face([c0[3], c0[2], c0[1], c0[0]], m)
            self.face([c1[0], c1[1], c1[2], c1[3]], m)

    def grid(self, rows, m, smooth=True, closed=True, uvscale=(1.0, 1.0), swap=False):
        T = self.T
        mi = self._mid(m)
        nr, nc = len(rows), len(rows[0])
        base = len(self.v)
        for row in rows:
            self.v.extend(T @ Vector(p) for p in row)
        ncol = nc if closed else nc - 1
        den = nc if closed else nc - 1
        for i in range(nr - 1):
            for j in range(ncol):
                j2 = (j + 1) % nc
                a = base + i * nc + j
                b = base + i * nc + j2
                c = base + (i + 1) * nc + j2
                d = base + (i + 1) * nc + j
                self.f.append((a, b, c, d))
                self.m.append(mi)
                self.sm.append(smooth)
                u0, u1 = j / den * uvscale[0], (j + 1) / den * uvscale[0]
                v0, v1 = i / (nr - 1) * uvscale[1], (i + 1) / (nr - 1) * uvscale[1]
                if swap:
                    self.uv.append([(v0, u0), (v0, u1), (v1, u1), (v1, u0)])
                else:
                    self.uv.append([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])

    def lathe(self, profile, cx, cy, m, seg=24, z0=0.0, smooth=True, caps=True, uvscale=(1.0, 1.0),
              sx=1.0, sy=1.0, phase=0.0, cap_mat=None):
        rows = []
        for r, z in profile:
            rows.append([(cx + sx * r * math.cos(2 * math.pi * j / seg + phase),
                          cy + sy * r * math.sin(2 * math.pi * j / seg + phase), z0 + z) for j in range(seg)])
        self.grid(rows, m, smooth=smooth, closed=True, uvscale=uvscale)
        if caps:
            cm = cap_mat or m
            if profile[0][0] > 1e-6:
                self.face(list(reversed(rows[0])), cm)
            if profile[-1][0] > 1e-6:
                self.face(rows[-1], cm)

    def cyl(self, cx, cy, z0, z1, r, m, seg=12, r2=None, caps=True, smooth=True, cap_mat=None):
        self.lathe([(r, 0.0), (r if r2 is None else r2, z1 - z0)], cx, cy, m, seg=seg, z0=z0,
                   smooth=smooth, caps=caps, cap_mat=cap_mat,
                   uvscale=(2 * math.pi * r / TS.get(m, 1.0), (z1 - z0) / TS.get(m, 1.0)))

    def sphere(self, c, r, m, seg=12, rings=7, scale=(1, 1, 1), smooth=True):
        prof = []
        for i in range(rings + 1):
            a = -math.pi / 2 + math.pi * i / rings
            prof.append((r * math.cos(a), r * math.sin(a)))
        prof[0] = (0.0, prof[0][1])
        prof[-1] = (0.0, prof[-1][1])
        self.push(c, 0.0, scale)
        self.lathe(prof, 0, 0, m, seg=seg, smooth=smooth, caps=False)
        self.pop()

    def tube(self, p0, p1, r0, r1, m, seg=6, caps=False, smooth=True):
        p0 = Vector(p0)
        p1 = Vector(p1)
        a = p1 - p0
        L = a.length
        if L < 1e-6:
            return
        u = a / L
        t = Vector((0, 0, 1)) if abs(u.z) < 0.9 else Vector((1, 0, 0))
        e1 = u.cross(t).normalized()
        e2 = u.cross(e1).normalized()
        rows = []
        for p, r in ((p0, r0), (p1, r1)):
            rows.append([p + (e1 * math.cos(2 * math.pi * j / seg) + e2 * math.sin(2 * math.pi * j / seg)) * r
                         for j in range(seg)])
        # ทิศของ e1,e2 อาจกลับด้าน -> สลับลำดับให้ normal ชี้ออก
        test = (rows[0][1] - rows[0][0]).cross(rows[1][0] - rows[0][0])
        if test.dot(rows[0][0] - p0) < 0:
            rows = [list(reversed(r_)) for r_ in rows]
        self.grid(rows, m, smooth=smooth, closed=True,
                  uvscale=(2 * math.pi * max(r0, 0.05) / TS.get(m, 1.0), L / TS.get(m, 1.0)))
        if caps:
            self.face(list(reversed(rows[0])), m)
            self.face(rows[1], m)

    def prism(self, pts, z0, z1, m, top=None, bottom=None):
        n = len(pts)
        area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
        if area < 0:
            pts = list(reversed(pts))
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            self.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], m)
        self.face([(x, y, z1) for x, y in pts], top or m)
        if bottom:
            self.face([(x, y, z0) for x, y in reversed(pts)], bottom)

    # roofs -----------------------------------------------------------------
    def hip_roof(self, x0, y0, x1, y1, z, h, m, under="soffit", fascia="trim", fh=0.3, ridge=None):
        L, W = x1 - x0, y1 - y0
        if W > L:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            self.push((cx, cy, 0), math.pi / 2)
            self.hip_roof(-W / 2, -L / 2, W / 2, L / 2, z, h, m, under, fascia, fh, ridge)
            self.pop()
            return
        ts = TS.get(m, 1.0)
        yc = (y0 + y1) / 2
        d = W / 2
        s = math.hypot(d, h) / ts
        self.face([(x0, y0, z), (x1, y0, z), (x1 - d, yc, z + h), (x0 + d, yc, z + h)], m,
                  uv=[(0, 0), (L / ts, 0), ((L - d) / ts, s), (d / ts, s)])
        self.face([(x1, y1, z), (x0, y1, z), (x0 + d, yc, z + h), (x1 - d, yc, z + h)], m,
                  uv=[(0, 0), (L / ts, 0), ((L - d) / ts, s), (d / ts, s)])
        self.face([(x0, y1, z), (x0, y0, z), (x0 + d, yc, z + h)], m,
                  uv=[(0, 0), (W / ts, 0), (d / ts, s)])
        self.face([(x1, y0, z), (x1, y1, z), (x1 - d, yc, z + h)], m,
                  uv=[(0, 0), (W / ts, 0), (d / ts, s)])
        if under:
            self.face([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], under)
        if fascia:
            t = 0.04
            self.box(x0 - t, y0 - t, z - fh, x1 + t, y0, z, fascia, skip=("nz", "pz"))
            self.box(x0 - t, y1, z - fh, x1 + t, y1 + t, z, fascia, skip=("nz", "pz"))
            self.box(x0 - t, y0, z - fh, x0, y1, z, fascia, skip=("nz", "pz"))
            self.box(x1, y0, z - fh, x1 + t, y1, z, fascia, skip=("nz", "pz"))
        if ridge:
            self.beam((x0 + d, yc, z + h + 0.04), (x1 - d, yc, z + h + 0.04), 0.32, 0.16, ridge)
            for (cx, cy), (ex, ey) in (((x0, y0), (x0 + d, yc)), ((x0, y1), (x0 + d, yc)),
                                         ((x1, y0), (x1 - d, yc)), ((x1, y1), (x1 - d, yc))):
                self.beam((cx, cy, z + 0.04), (ex, ey, z + h + 0.04), 0.26, 0.12, ridge)

    def gable_roof(self, x0, y0, x1, y1, z, h, m, gable="wall", oh=0.8, eave=0.9, barge="trim",
                   thai=False, finial="gold", ridge=None, gable_inset=0.0):
        """หลังคาจั่ว สันหลังคาตามแกน x; (x0..x1, y0..y1) = แนวผนัง"""
        ts = TS.get(m, 1.0)
        ye0, ye1 = y0 - eave, y1 + eave
        yc = (y0 + y1) / 2
        hw = (y1 - y0) / 2
        slope = h / hw
        ze = z - eave * slope
        xa, xb = x0 - oh, x1 + oh
        s = math.hypot(hw + eave, h) / ts
        Lr = (xb - xa) / ts
        self.face([(xa, ye0, ze), (xb, ye0, ze), (xb, yc, z + h), (xa, yc, z + h)], m,
                  uv=[(0, 0), (Lr, 0), (Lr, s), (0, s)])
        self.face([(xb, ye1, ze), (xa, ye1, ze), (xa, yc, z + h), (xb, yc, z + h)], m,
                  uv=[(0, 0), (Lr, 0), (Lr, s), (0, s)])
        if gable:
            for x, sgn in ((x0 + gable_inset, -1), (x1 - gable_inset, 1)):
                pts = [(x, y1, z), (x, y0, z), (x, yc, z + h)]
                if sgn > 0:
                    pts = [(x, y0, z), (x, y1, z), (x, yc, z + h)]
                self.face(pts, gable)
        if barge:
            bw, bh = (0.22, 0.5) if thai else (0.15, 0.32)
            for x in (xa, xb):
                self.beam((x, ye0, ze), (x, yc, z + h), bw, bh, barge)
                self.beam((x, ye1, ze), (x, yc, z + h), bw, bh, barge)
                if thai:
                    # ช่อฟ้า (ปลายสันหลังคา) และหางหงส์ (ปลายปั้นลม)
                    sgn = -1 if x == xa else 1
                    pts = [(x, yc, z + h), (x + sgn * 0.35, yc, z + h + 0.55), (x + sgn * 0.2, yc, z + h + 1.15),
                           (x - sgn * 0.15, yc, z + h + 1.45)]
                    for a, b in zip(pts[:-1], pts[1:]):
                        self.beam(a, b, 0.16, 0.16, finial)
                    for ye in (ye0, ye1):
                        sy = -1 if ye == ye0 else 1
                        p0 = (x, ye, ze)
                        p1 = (x + sgn * 0.1, ye + sy * 0.35, ze + 0.25)
                        p2 = (x + sgn * 0.05, ye + sy * 0.45, ze + 0.7)
                        self.beam(p0, p1, 0.14, 0.14, finial)
                        self.beam(p1, p2, 0.12, 0.12, finial)
                    # ใบระกา (ฟันเลื่อยตามปั้นลม)
                    n = max(3, int(hw / 0.9))
                    for ye in (ye0, ye1):
                        for k in range(1, n):
                            t = k / n
                            py = ye + (yc - ye) * t
                            pz = ze + (z + h - ze) * t + 0.3
                            self.beam((x, py, pz), (x, py + (0.25 if ye == ye0 else -0.25), pz + 0.42),
                                      0.08, 0.1, finial)
        if ridge:
            self.beam((xa, yc, z + h + 0.05), (xb, yc, z + h + 0.05), 0.3, 0.14, ridge)

    def barrel_roof(self, x0, y0, x1, y1, z, rise, m, seg=24, ends=None):
        """หลังคาโค้ง (โรงยิม) โค้งตามแกน y ยื่นตามแกน x"""
        W = y1 - y0
        R = (W * W / 4 + rise * rise) / (2 * rise)
        zc = z + rise - R
        a0 = math.asin((W / 2) / R)
        pts = []
        for i in range(seg + 1):
            a = -a0 + 2 * a0 * i / seg
            pts.append(((y0 + y1) / 2 + R * math.sin(a), zc + R * math.cos(a)))
        arc = 2 * a0 * R
        ts = TS.get(m, 1.0)
        rows = [[(x1, y, zz) for y, zz in pts], [(x0, y, zz) for y, zz in pts]]
        self.grid(rows, m, smooth=True, closed=False, uvscale=(arc / ts, (x1 - x0) / ts), swap=True)
        if ends:
            for x, rev in ((x0 + 0.6, True), (x1 - 0.6, False)):
                poly = [(x, y, zz) for y, zz in pts]
                self.face(list(reversed(poly)) if rev else poly, ends)

    # finish ----------------------------------------------------------------
    def build(self, name, coll=None, loc=(0, 0, 0), rz=0.0):
        if not self.f:
            return None
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(p) for p in self.v], [], self.f)
        for mn in self.mats:
            me.materials.append(MATS[mn])
        me.polygons.foreach_set("material_index", self.m)
        me.polygons.foreach_set("use_smooth", self.sm)
        uvl = me.uv_layers.new(name="UVMap")
        flat = [c for uvs in self.uv for uv in uvs for c in uv]
        uvl.data.foreach_set("uv", flat)
        me.update()
        ob = bpy.data.objects.new(name, me)
        ob.location = loc
        ob.rotation_euler = (0, 0, rz)
        (coll or bpy.context.scene.collection).objects.link(ob)
        return ob

    def ntris(self):
        return sum(len(f) - 2 for f in self.f)


def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    p = parent or bpy.context.scene.collection
    if c.name not in p.children:
        p.children.link(c)
    return c


def place(L, D, center, facing):
    """คำนวณตำแหน่ง/การหมุนของอาคารที่สร้างในพิกัดท้องถิ่น (x=ความยาว, y=ความลึก, ระเบียงอยู่ที่ y=D)
    facing = ทิศที่ด้านระเบียงหันไป: 'N','S','E','W'"""
    rz = {"N": 0.0, "S": math.pi, "E": -math.pi / 2, "W": math.pi / 2}[facing]
    R = Matrix.Rotation(rz, 3, "Z")
    off = R @ Vector((L / 2, D / 2, 0))
    return (center[0] - off.x, center[1] - off.y, 0.0), rz
