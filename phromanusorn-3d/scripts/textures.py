"""สร้างเท็กซ์เจอร์ทั้งหมดของโมเดล (หญ้า หลังคา ลู่วิ่ง ป้ายภาษาไทย ตราโรงเรียน ฯลฯ)
ด้วย numpy + Pillow ทุกภาพต่อกันได้ไร้รอยต่อ (seamless) เพราะสร้างจาก FFT noise

รัน:  python3 scripts/textures.py
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "textures")
os.makedirs(OUT, exist_ok=True)

FONT_B = "/usr/share/fonts/opentype/tlwg/Loma-Bold.otf"
FONT_R = "/usr/share/fonts/opentype/tlwg/Loma.otf"

SCHOOL_TH = "โรงเรียนพรหมานุสรณ์จังหวัดเพชรบุรี"
SCHOOL_EN = "PROMMANUSORN PHETCHABURI SCHOOL"
MOTTO = "วายเมเถว ปุริโส"

BLUE = (33, 64, 140)
BLUE_D = (22, 42, 96)
PINK = (233, 132, 172)
PINK_L = (247, 196, 216)
GOLD = (222, 180, 84)
WHITE = (250, 250, 247)


# ---------------------------------------------------------------- noise helpers
def fbm(h, w=None, beta=2.0, seed=0):
    """periodic 1/f^beta noise in [0,1] (tileable)"""
    w = w or h
    r = np.random.default_rng(seed)
    F = np.fft.fft2(r.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    F = F / f ** (beta / 2.0)
    F[0, 0] = 0
    x = np.real(np.fft.ifft2(F))
    x -= x.min()
    x /= max(x.max(), 1e-9)
    return x


def lerp_col(a, b, t):
    a = np.array(a, np.float32)
    b = np.array(b, np.float32)
    return a + (b - a) * t[..., None]


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def save(img, name, q=90):
    p = os.path.join(OUT, name)
    if name.endswith(".jpg"):
        img.convert("RGB").save(p, quality=q, optimize=True)
    else:
        img.save(p, optimize=True)
    return p


def font(size, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size,
                              layout_engine=ImageFont.Layout.RAQM)


def fit(d, text, max_w, size, bold=True):
    f = font(size, bold)
    while d.textlength(text, font=f) > max_w and size > 10:
        size -= 2
        f = font(size, bold)
    return f


def text_center(d, cx, cy, text, f, fill, stroke=0, stroke_fill=None):
    d.text((cx, cy), text, font=f, fill=fill, anchor="mm",
           stroke_width=stroke, stroke_fill=stroke_fill)


# ---------------------------------------------------------------- ground
def grass(name="grass.jpg", n=1024, seed=1, dark=(58, 92, 36), light=(118, 150, 62)):
    a = 0.55 * fbm(n, beta=2.4, seed=seed) + 0.30 * fbm(n, beta=1.2, seed=seed + 1) \
        + 0.15 * fbm(n, beta=0.0, seed=seed + 2)
    img = lerp_col(dark, light, a)
    return save(to_img(img), name)


def field(name="field.jpg"):
    # สนามฟุตบอล 100 x 60 m + ขอบ 2 m  -> 104 x 64 m, 20 px / m
    W, H, ppm = 104, 64, 20
    w, h = W * ppm, H * ppm
    a = 0.6 * fbm(h, w, beta=2.2, seed=11) + 0.4 * fbm(h, w, beta=0.6, seed=12)
    base = lerp_col((60, 104, 40), (104, 146, 58), a)
    xs = (np.arange(w) / ppm)
    stripe = ((xs // 8).astype(int) % 2 == 0)[None, :]
    base = base * np.where(stripe, 1.07, 0.93)[..., None]
    img = to_img(base)
    d = ImageDraw.Draw(img)
    lw = 3
    def P(x, y):
        return ((x + W / 2) * ppm, (H / 2 - y) * ppm)
    def rect(x0, y0, x1, y1):
        d.rectangle([P(x0, y1), P(x1, y0)], outline=WHITE, width=lw)
    def circ(cx, cy, r, a0=0, a1=360):
        (px, py) = P(cx, cy)
        d.arc([px - r * ppm, py - r * ppm, px + r * ppm, py + r * ppm], a0, a1, fill=WHITE, width=lw)
    rect(-50, -30, 50, 30)
    d.line([P(0, -30), P(0, 30)], fill=WHITE, width=lw)
    circ(0, 0, 9.15)
    for s in (-1, 1):
        rect(min(s * 50, s * 33.5), -20.16, max(s * 50, s * 33.5), 20.16)
        rect(min(s * 50, s * 44.5), -9.16, max(s * 50, s * 44.5), 9.16)
        px, py = P(s * 39, 0)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=WHITE)
        ang = math.degrees(math.acos(5.5 / 9.15))
        if s > 0:
            circ(39, 0, 9.15, 180 - ang, 180 + ang)
        else:
            circ(-39, 0, 9.15, -ang, ang)
    px, py = P(0, 0)
    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=WHITE)
    for cx, cy, a0 in ((-50, -30, 270), (50, -30, 180), (50, 30, 90), (-50, 30, 0)):
        circ(cx, cy, 1, a0, a0 + 90)
    return save(img, name, 88)


def track(name="track.jpg"):
    # u = ตามแนวลู่ (8 m), v = ขวางลู่ 6 ลู่ x 1.22 m = 7.32 m
    n = 512
    a = 0.6 * fbm(n, beta=1.0, seed=21) + 0.4 * fbm(n, beta=0.0, seed=22)
    img = lerp_col((150, 52, 42), (190, 78, 60), a)
    rows = np.arange(n)
    v = 1.0 - rows / n  # v=0 ด้านล่างภาพ
    lw = 0.05 / 7.32
    mask = np.zeros(n, bool)
    for k in range(7):
        mask |= np.abs(v - k / 6.0 * (1 - 2 * lw) - lw) < lw
    img[mask, :, :] = (236, 236, 230)
    return save(to_img(img), name)


def asphalt(name="asphalt.jpg"):
    n = 512
    a = 0.5 * fbm(n, beta=1.6, seed=31) + 0.5 * fbm(n, beta=0.0, seed=32)
    img = lerp_col((46, 47, 50), (82, 83, 86), a)
    r = np.random.default_rng(33).random((n, n))
    img[r > 0.985] += 40
    return save(to_img(img), name)


def concrete(name="concrete.jpg", c0=(150, 148, 140), c1=(196, 193, 185), seed=41):
    n = 512
    a = 0.6 * fbm(n, beta=2.0, seed=seed) + 0.4 * fbm(n, beta=0.3, seed=seed + 1)
    img = lerp_col(c0, c1, a)
    return save(to_img(img), name)


def paving(name="paving.jpg"):
    # บล็อกปูพื้น 0.4 x 0.2 m ต่อกันแบบสลับแนว 512 px = 2 m
    n, ppm = 512, 256
    r = np.random.default_rng(51)
    img = np.zeros((n, n, 3), np.float32)
    bw, bh = int(0.4 * ppm), int(0.2 * ppm)
    noise = fbm(n, beta=0.5, seed=52)
    for row in range(n // bh + 1):
        off = (bw // 2) if row % 2 else 0
        for col in range(-1, n // bw + 1):
            x0 = col * bw + off
            y0 = row * bh
            tone = r.uniform(0.86, 1.08)
            c = np.array((168, 162, 150)) * tone
            if r.random() < 0.18:
                c = np.array((176, 112, 92)) * tone
            xs = slice(max(x0, 0), min(x0 + bw, n))
            ys = slice(max(y0, 0), min(y0 + bh, n))
            img[ys, xs] = c
    img *= (0.9 + 0.2 * noise)[..., None]
    yy, xx = np.mgrid[0:n, 0:n]
    joint_h = (yy % bh) < 2
    off = np.where(((yy // bh) % 2) == 1, bw // 2, 0)
    joint_v = ((xx - off) % bw) < 2
    img[joint_h | joint_v] *= 0.55
    return save(to_img(img), name)


def soil(name="soil.jpg"):
    n = 512
    a = 0.6 * fbm(n, beta=1.8, seed=61) + 0.4 * fbm(n, beta=0.2, seed=62)
    return save(to_img(lerp_col((112, 86, 60), (168, 136, 98), a)), name)


def sand(name="sand.jpg"):
    n = 256
    a = fbm(n, beta=0.8, seed=63)
    return save(to_img(lerp_col((200, 178, 132), (232, 214, 170), a)), name)


def hill(name="hill.jpg"):
    # ป่าบนเขาวัง: เขียวเข้มสลับดิน/หิน
    n = 1024
    a = fbm(n, beta=2.2, seed=71)
    b = fbm(n, beta=1.2, seed=72)
    c = fbm(n, beta=0.3, seed=73)
    green = lerp_col((44, 70, 30), (96, 128, 52), 0.6 * b + 0.4 * c)
    rock = lerp_col((120, 108, 92), (168, 158, 140), c)
    t = np.clip((a - 0.62) * 6, 0, 1)
    img = green * (1 - t[..., None]) + rock * t[..., None]
    return save(to_img(img), name)


def vegbed(name="vegbed.jpg"):
    # แปลงผัก: ดินเป็นร่อง มีต้นผักเป็นแถว (512 px = 2 m)
    n = 512
    base = lerp_col((96, 72, 50), (140, 108, 76), fbm(n, beta=1.0, seed=81))
    img = to_img(base)
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(82)
    for row in range(4):
        y = 64 + row * 128
        for k in range(10):
            x = 26 + k * 51 + r.integers(-6, 6)
            rad = r.integers(14, 22)
            g = (int(r.integers(60, 90)), int(r.integers(120, 160)), int(r.integers(40, 70)))
            d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=g)
            d.ellipse([x - rad // 2, y - rad // 2, x + rad // 3, y + rad // 3],
                      fill=(g[0] + 30, g[1] + 30, g[2] + 20))
    return save(img, name)


# ---------------------------------------------------------------- building materials
def roof_tiles(name, col, seed):
    # กระเบื้องลอน 5 แถว x 5 ลอน ต่อ 1.6 m, v ขึ้นตามความชัน
    n = 512
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    v = (n - 1 - yy) / n * 5.0
    u = xx / n * 5.0
    p = v % 1.0
    shade = 0.62 + 0.38 * (1 - p) ** 0.55
    shade *= 0.86 + 0.14 * np.cos(2 * np.pi * u) ** 2
    shade *= 0.92 + 0.16 * fbm(n, beta=1.2, seed=seed)
    img = np.array(col, np.float32)[None, None, :] * shade[..., None]
    return save(to_img(img), name)


def metal_sheet(name, col, seed, ribs=4):
    # เมทัลชีทลอน (ลอนวิ่งตามแนว v) 512 px = 1 m
    n = 512
    xx = np.arange(n, dtype=np.float32)
    u = xx / n * ribs
    p = u % 1.0
    prof = np.where(p < 0.18, 0.75 + 0.25 * np.sin(p / 0.18 * np.pi), 0.92)
    shade = prof[None, :] * (0.95 + 0.1 * fbm(n, beta=1.5, seed=seed))
    img = np.array(col, np.float32)[None, None, :] * shade[..., None]
    return save(to_img(img), name)


def breeze(name_alpha="breeze.png", name_solid="breeze_solid.jpg"):
    # ช่องลมแบบไทย: บล็อก 0.2 m, 4x4 บล็อกต่อ 0.8 m, 512 px
    n = 512
    b = n // 4
    yy, xx = np.mgrid[0:n, 0:n]
    lx = (xx % b) - b / 2 + 0.5
    ly = (yy % b) - b / 2 + 0.5
    r = np.sqrt(lx * lx + ly * ly)
    hole = r < b * 0.40
    diamond = (np.abs(lx) + np.abs(ly)) < b * 0.20
    cross = (np.abs(lx) < b * 0.045) | (np.abs(ly) < b * 0.045)
    hole = hole & ~diamond & ~cross
    border = (np.abs(lx) > b * 0.46) | (np.abs(ly) > b * 0.46)
    noise = fbm(n, beta=1.0, seed=91)
    col = lerp_col((214, 206, 190), (242, 236, 222), noise)
    col[border] *= 0.82
    alpha = np.where(hole, 0, 255).astype(np.uint8)
    rgba = np.dstack([np.clip(col, 0, 255).astype(np.uint8), alpha])
    Image.fromarray(rgba, "RGBA").save(os.path.join(OUT, name_alpha), optimize=True)
    solid = col.copy()
    solid[hole] = (70, 66, 62)
    save(to_img(solid), name_solid)


def railing(name="railing.png", col=(42, 82, 160)):
    # ราวเหล็กแนวตั้ง 1 m x 1 m
    n = 256
    rgba = np.zeros((n, n, 4), np.uint8)
    rgba[..., :3] = col
    xx = np.arange(n)
    bars = (xx % 32) < 6
    rgba[:, bars, 3] = 255
    rgba[:10, :, 3] = 255
    rgba[-10:, :, 3] = 255
    rgba[n // 2 - 3:n // 2 + 3, :, 3] = 255
    Image.fromarray(rgba, "RGBA").save(os.path.join(OUT, name), optimize=True)


def louvre(name="louvre.png", col=(60, 98, 168)):
    # บานเกล็ดระบายอากาศ (โรงยิม) 1 m
    n = 256
    rgba = np.zeros((n, n, 4), np.uint8)
    yy = np.arange(n)
    p = (yy % 32) / 32.0
    shade = np.where(p < 0.62, 0.75 + 0.35 * p, 0)
    for c in range(3):
        rgba[:, :, c] = np.clip(col[c] * shade[:, None] * 1.1, 0, 255)
    rgba[:, :, 3] = np.where(p < 0.62, 255, 0)[:, None]
    Image.fromarray(rgba, "RGBA").save(os.path.join(OUT, name), optimize=True)


def shutter(name="shutter.jpg"):
    n = 256
    yy = np.arange(n)
    p = (yy % 20) / 20.0
    shade = 0.78 + 0.22 * np.sin(p * np.pi)
    img = np.ones((n, n, 3), np.float32) * np.array((176, 180, 184))[None, None, :]
    img *= shade[:, None, None]
    img *= (0.94 + 0.12 * fbm(n, beta=1.5, seed=101))[..., None]
    return save(to_img(img), name)


def leaves(name, c0, c1, seed):
    n = 512
    a = 0.45 * fbm(n, beta=1.6, seed=seed) + 0.55 * fbm(n, beta=0.2, seed=seed + 1)
    img = lerp_col(c0, c1, a)
    r = np.random.default_rng(seed + 2).random((n, n))
    img[r > 0.97] *= 1.25
    img[r < 0.04] *= 0.6
    return save(to_img(img), name)


def bark(name="bark.jpg"):
    n = 256
    a = fbm(64, 256, beta=1.8, seed=111)
    a = np.array(Image.fromarray((a * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)) / 255.0
    return save(to_img(lerp_col((70, 58, 46), (128, 112, 94), a)), name)


def wood_floor(name="woodfloor.jpg"):
    n = 512
    img = np.zeros((n, n, 3), np.float32)
    r = np.random.default_rng(121)
    pw = 26  # ~0.1 m ต่อแผ่น เมื่อ 512 px = 2 m
    g = fbm(n, beta=1.0, seed=122)
    for i in range(n // pw + 1):
        tone = r.uniform(0.85, 1.1)
        img[:, i * pw:(i + 1) * pw] = np.array((196, 146, 92)) * tone
    img *= (0.9 + 0.2 * g)[..., None]
    img[:, (np.arange(n) % pw) < 1] *= 0.6
    return save(to_img(img), name)


def court_basket(name="court_basket.jpg"):
    # สนามบาส 28 x 15 + ขอบ 2 m -> 32 x 19, 40 px / m
    W, H, ppm = 32, 19, 40
    w, h = W * ppm, H * ppm
    base = lerp_col((52, 108, 82), (70, 128, 98), fbm(h, w, beta=1.0, seed=131))
    img = to_img(base)
    d = ImageDraw.Draw(img)
    def P(x, y):
        return ((x + W / 2) * ppm, (H / 2 - y) * ppm)
    blue = (44, 92, 160)
    # inner court blue
    d.rectangle([P(-14, 7.5), P(14, -7.5)], fill=(58, 118, 92))
    for s in (-1, 1):
        x0, x1 = s * 14, s * (14 - 5.8)
        d.rectangle([P(min(x0, x1), 2.45), P(max(x0, x1), -2.45)], fill=blue)
        cx, cy = P(s * (14 - 5.8), 0)
        d.ellipse([cx - 1.8 * ppm, cy - 1.8 * ppm, cx + 1.8 * ppm, cy + 1.8 * ppm], outline=WHITE, width=3)
        bx, by = P(s * (14 - 1.575), 0)
        R = 6.75 * ppm
        ang = math.degrees(math.asin(6.6 / 6.75))
        if s > 0:
            d.arc([bx - R, by - R, bx + R, by + R], 180 - ang, 180 + ang, fill=WHITE, width=3)
        else:
            d.arc([bx - R, by - R, bx + R, by + R], -ang, ang, fill=WHITE, width=3)
        xs = s * 14
        xe = s * (14 - 1.575) - s * 6.75 * math.cos(math.radians(ang))
        d.line([P(xs, 6.6), P(xe, 6.6)], fill=WHITE, width=3)
        d.line([P(xs, -6.6), P(xe, -6.6)], fill=WHITE, width=3)
        d.rectangle([P(min(x0, x1), 2.45), P(max(x0, x1), -2.45)], outline=WHITE, width=3)
    cx, cy = P(0, 0)
    d.ellipse([cx - 1.8 * ppm, cy - 1.8 * ppm, cx + 1.8 * ppm, cy + 1.8 * ppm], fill=blue, outline=WHITE, width=3)
    d.rectangle([P(-14, 7.5), P(14, -7.5)], outline=WHITE, width=3)
    d.line([P(0, 7.5), P(0, -7.5)], fill=WHITE, width=3)
    return save(img, name, 88)


def court_small(name="court_takraw.jpg"):
    # สนามตะกร้อ 13.4 x 6.1 + ขอบ 1 m
    W, H, ppm = 15.4, 8.1, 50
    w, h = int(W * ppm), int(H * ppm)
    base = lerp_col((44, 96, 150), (58, 112, 168), fbm(h, w, beta=1.0, seed=141))
    img = to_img(base)
    d = ImageDraw.Draw(img)
    def P(x, y):
        return ((x + W / 2) * ppm, (H / 2 - y) * ppm)
    d.rectangle([P(-6.7, 3.05), P(6.7, -3.05)], fill=(206, 96, 82), outline=WHITE, width=3)
    d.line([P(0, 3.05), P(0, -3.05)], fill=WHITE, width=3)
    for s in (-1, 1):
        cx, cy = P(s * 2.45, 0)
        d.arc([cx - 0.9 * ppm, cy - 0.9 * ppm, cx + 0.9 * ppm, cy + 0.9 * ppm], 0, 360, fill=WHITE, width=3)
    return save(img, name, 88)


def curb(name, c1, c2):
    n = 128
    img = np.zeros((n, n, 3), np.uint8)
    img[:, : n // 2] = c1
    img[:, n // 2:] = c2
    return save(Image.fromarray(img), name)


# ---------------------------------------------------------------- signs & symbols
def thai_flag(name="thai_flag.jpg"):
    w, h = 900, 600
    img = Image.new("RGB", (w, h), (165, 25, 49))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 100, w, 500], fill=(244, 245, 248))
    d.rectangle([0, 200, w, 400], fill=(45, 42, 74))
    return save(img, name)


def emblem(name="emblem.png", size=1024):
    """ตราโรงเรียน (แบบจำลอง): ช้างหมอบชูคบเพลิง ในวงกลมสีน้ำเงิน-ชมพู"""
    S = size
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S / 2
    d.ellipse([8, 8, S - 8, S - 8], fill=BLUE, outline=GOLD, width=18)
    d.ellipse([110, 110, S - 110, S - 110], fill=PINK_L, outline=GOLD, width=10)
    k = S / 1000.0
    def sc(pts):
        return [(x * k, y * k) for x, y in pts]
    # เปลวคบเพลิง
    d.polygon(sc([(470, 150), (430, 230), (445, 300), (500, 320), (555, 300), (568, 225), (530, 170), (515, 215)]),
              fill=(242, 140, 40))
    d.polygon(sc([(495, 205), (470, 262), (500, 305), (532, 262)]), fill=(255, 222, 92))
    d.rectangle(sc([(478, 300), (522, 330)]), fill=GOLD)
    d.polygon(sc([(484, 330), (516, 330), (506, 440), (494, 440)]), fill=(150, 96, 52))
    # ช้างหมอบ (หันซ้าย) ชูงวงจับคบเพลิง
    ew = (250, 250, 252)
    eo = BLUE_D
    for x0 in (430, 600):                                                                 # ขาพับ
        d.rounded_rectangle(sc([(x0, 690), (x0 + 120, 772)]), radius=int(34 * k), fill=ew, outline=eo, width=int(6 * k))
    d.ellipse(sc([(380, 520), (790, 750)]), fill=ew, outline=eo, width=int(8 * k))       # ลำตัว
    d.ellipse(sc([(300, 450), (500, 650)]), fill=ew, outline=eo, width=int(8 * k))       # หัว
    d.ellipse(sc([(395, 470), (520, 650)]), fill=(232, 232, 238), outline=eo, width=int(6 * k))  # หู
    d.line(sc([(330, 560), (300, 500), (330, 440), (420, 410), (480, 430)]), fill=eo, width=int(54 * k), joint="curve")
    d.line(sc([(330, 560), (300, 500), (330, 440), (420, 410), (480, 430)]), fill=ew, width=int(38 * k), joint="curve")
    d.ellipse(sc([(372, 520), (392, 540)]), fill=eo)                                     # ตา
    d.line(sc([(352, 600), (318, 618), (300, 606)]), fill=(255, 255, 240), width=int(14 * k))  # งา
    d.line(sc([(790, 640), (830, 700), (820, 740)]), fill=eo, width=int(10 * k))         # หาง
    # แถบคติพจน์
    d.rounded_rectangle(sc([(230, 790), (770, 880)]), radius=int(30 * k), fill=BLUE, outline=GOLD, width=int(6 * k))
    text_center(d, c, 835 * k, MOTTO, font(int(54 * k)), WHITE)
    return save(img, name)


def sign(name, lines, w, h, bg=BLUE, fg=WHITE, border=PINK, sizes=None, gold=False, bw=None):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    bw = bw or max(6, h // 18)
    if border:
        d.rectangle([bw // 2, bw // 2, w - bw // 2, h - bw // 2], outline=border, width=bw)
    sizes = sizes or [int(h * 0.42)] + [int(h * 0.2)] * (len(lines) - 1)
    total = sum(sizes) * 1.25
    y = h / 2 - total / 2 + sizes[0] * 0.62
    for t, s in zip(lines, sizes):
        f = font(s)
        while d.textlength(t, font=f) > w * 0.92 and s > 10:
            s -= 2
            f = font(s)
        text_center(d, w / 2, y, t, f, GOLD if gold else fg)
        y += s * 1.25
    return save(img, name)


def stone_sign(name="sign_stone.jpg"):
    w, h = 2400, 900
    a = fbm(h, w, beta=1.0, seed=151)
    img = to_img(lerp_col((22, 22, 26), (52, 52, 58), a))
    d = ImageDraw.Draw(img)
    em = Image.open(os.path.join(OUT, "emblem.png")).resize((560, 560), Image.LANCZOS)
    img.paste(em, (90, 170), em)
    mw = 1580
    text_center(d, 1500, 290, SCHOOL_TH, fit(d, SCHOOL_TH, mw, 150), GOLD)
    text_center(d, 1500, 470, SCHOOL_EN, fit(d, SCHOOL_EN, mw, 84), GOLD)
    t3 = "สำนักงานเขตพื้นที่การศึกษามัธยมศึกษาเพชรบุรี"
    text_center(d, 1500, 630, t3, fit(d, t3, mw, 70, False), (230, 220, 200))
    t4 = "“ " + MOTTO + " ”  เกิดเป็นคนต้องมีความเพียร"
    text_center(d, 1500, 760, t4, fit(d, t4, mw, 64, False), (230, 220, 200))
    return save(img, name)


def gate_sign(name="sign_gate.jpg"):
    w, h = 3000, 420
    img = Image.new("RGB", (w, h), BLUE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 34], fill=PINK)
    d.rectangle([0, h - 34, w, h], fill=PINK)
    em = Image.open(os.path.join(OUT, "emblem.png")).resize((300, 300), Image.LANCZOS)
    img.paste(em, (60, 60), em)
    img.paste(em, (w - 360, 60), em)
    text_center(d, w / 2, 170, SCHOOL_TH, fit(d, SCHOOL_TH, w - 860, 168), WHITE, stroke=4, stroke_fill=BLUE_D)
    text_center(d, w / 2, 330, SCHOOL_EN, fit(d, SCHOOL_EN, w - 860, 80), PINK_L)
    return save(img, name)


def label_signs():
    for i in range(1, 10):
        sign(f"label_b{i}.jpg", [f"อาคาร {i}"], 640, 220, sizes=[120])
    sign("label_gym.jpg", ["อาคารเฉลิมพระเกียรติ ๘๐ พรรษา", "โรงยิม  " + SCHOOL_TH], 2400, 360,
         sizes=[150, 70])
    sign("label_hall.jpg", ["หอประชุม", SCHOOL_TH], 1600, 360, sizes=[160, 70])
    sign("label_canteen.jpg", ["อาคารอเนกประสงค์ (โรงอาหาร)"], 1800, 260, sizes=[130])
    sign("label_shrine.jpg", ["หลวงพ่อป่าแก้ว"], 800, 200, bg=(120, 20, 24), border=GOLD, gold=True, sizes=[110])
    sign("label_guard.jpg", ["ป้อมยาม"], 500, 180, sizes=[100])
    sign("label_welcome.jpg", ["ยินดีต้อนรับสู่" + SCHOOL_TH], 3200, 260, bg=WHITE, fg=BLUE,
         border=PINK, sizes=[140])
    sign("label_admin.jpg", [SCHOOL_TH], 2600, 260, bg=BLUE, border=GOLD, gold=True, sizes=[150])
    sign("sign_road.jpg", ["ถนนบันไดอิฐ", "BANDAI-IT RD."], 600, 260, bg=(20, 90, 60), border=WHITE, sizes=[100, 54])
    sign("label_stand.jpg", ["อัฒจันทร์ พรหมานุสรณ์"], 1600, 200, sizes=[110])
    # ป้ายเขตโรงเรียน (เหลือง)
    s = 600
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(s / 2, 10), (s - 10, s / 2), (s / 2, s - 10), (10, s / 2)], fill=(250, 204, 20), outline=(20, 20, 20))
    d.polygon([(s / 2, 40), (s - 40, s / 2), (s / 2, s - 40), (40, s / 2)], outline=(20, 20, 20), width=10)
    text_center(d, s / 2, s / 2 - 50, "เขตโรงเรียน", font(78), (20, 20, 20))
    text_center(d, s / 2, s / 2 + 50, "ขับช้าๆ", font(78), (20, 20, 20))
    img.save(os.path.join(OUT, "sign_schoolzone.png"))
    # ป้ายร้านค้าฝั่งตรงข้าม
    shops = [("ร้านถ่ายเอกสาร", (30, 110, 190)), ("เครื่องเขียน", (200, 60, 60)),
             ("ขนมหม้อแกงเมืองเพชร", (190, 120, 30)), ("ก๋วยเตี๋ยวเรือ", (180, 30, 40)),
             ("ข้าวมันไก่", (240, 200, 60)), ("ชานมไข่มุก", (120, 70, 160)),
             ("ร้านซ่อมรถ", (40, 40, 40)), ("ร้านขายยา", (30, 140, 80)),
             ("มินิมาร์ท", (20, 120, 170)), ("ร้านตัดผม", (210, 90, 140)),
             ("ข้าวแกง", (200, 110, 40)), ("ร้านชุดนักเรียน", (30, 70, 150))]
    for i, (t, c) in enumerate(shops):
        light = sum(c) > 450
        sign(f"shop_{i}.jpg", [t], 800, 180, bg=c, fg=(20, 20, 20) if light else WHITE,
             border=WHITE, sizes=[96])
    # ป้ายร้านในโรงอาหาร
    stalls = ["ข้าวแกง", "ก๋วยเตี๋ยว", "ข้าวมันไก่", "ผัดกะเพรา", "น้ำปั่น", "ขนมไทย", "ส้มตำ", "สหกรณ์"]
    img = Image.new("RGB", (len(stalls) * 400, 120), WHITE)
    d = ImageDraw.Draw(img)
    for i, t in enumerate(stalls):
        cols = [(214, 70, 70), (60, 120, 200), (230, 160, 40), (60, 160, 90)]
        d.rectangle([i * 400 + 6, 6, i * 400 + 394, 114], fill=cols[i % 4])
        text_center(d, i * 400 + 200, 60, t, font(64), WHITE)
    save(img, "stalls.jpg")


def facade_banner(name="banner_motto.jpg"):
    w, h = 2400, 300
    img = Image.new("RGB", (w, h), PINK)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 20], fill=BLUE)
    d.rectangle([0, h - 20, w, h], fill=BLUE)
    text_center(d, w / 2, h / 2, "“ " + MOTTO + " ”   เกิดเป็นคนต้องมีความเพียร", font(120), BLUE_D)
    return save(img, name)


def main():
    grass()
    grass("grass_dry.jpg", seed=5, dark=(92, 104, 52), light=(150, 156, 88))
    field()
    track()
    asphalt()
    concrete()
    concrete("concrete_light.jpg", (196, 192, 182), (226, 222, 212), seed=45)
    paving()
    soil()
    sand()
    hill()
    vegbed()
    roof_tiles("roof_blue.jpg", (52, 84, 140), 201)
    roof_tiles("roof_orange.jpg", (178, 88, 52), 202)
    roof_tiles("roof_green.jpg", (52, 110, 70), 203)
    roof_tiles("roof_red.jpg", (160, 44, 38), 204)
    roof_tiles("roof_grey.jpg", (120, 120, 124), 205)
    metal_sheet("metal_blue.jpg", (58, 100, 168), 211)
    metal_sheet("metal_zinc.jpg", (168, 174, 180), 212)
    metal_sheet("metal_pink.jpg", (214, 120, 158), 213)
    breeze()
    railing()
    louvre()
    shutter()
    leaves("leaves.jpg", (34, 62, 22), (98, 138, 48), 221)
    leaves("leaves_light.jpg", (60, 96, 32), (136, 172, 70), 224)
    leaves("leaves_plumeria.jpg", (40, 84, 30), (110, 156, 60), 227)
    bark()
    wood_floor()
    court_basket()
    court_small()
    curb("curb_bw.jpg", (20, 20, 20), (240, 240, 240))
    curb("curb_rw.jpg", (200, 30, 30), (240, 240, 240))
    thai_flag()
    emblem()
    stone_sign()
    gate_sign()
    label_signs()
    facade_banner()
    print("textures ->", OUT, len(os.listdir(OUT)), "files")


if __name__ == "__main__":
    main()
