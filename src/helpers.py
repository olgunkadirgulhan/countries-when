def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def seg(t, a, b): return clamp((t - a) / (b - a))
def sm(u): u = clamp(u); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
def lerpc(c1, c2, u): return tuple(int(round(lerp(a, b, u))) for a, b in zip(c1, c2))
def lp(a, b, u): return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
def back(u):
    u = clamp(u); c = 1.7; v = u - 1
    return 1 + (c + 1) * v ** 3 + c * v ** 2
def spring(t, amp=1.0, f=9.0, damp=6.0):
    return amp * math.exp(-damp * t) * math.sin(f * t) if t > 0 else 0.0
def rotv(x, y, ang):  # saat yönünde (ekran koordinatı)
    a = math.radians(ang)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
def L(v): return int(round(v * S))
def box(x0, y0, x1, y1): return [L(x0), L(y0), L(x1), L(y1)]


# ---------------------------------------------------------------- 3B sprite'lar
LIGHT = np.array([-0.45, -0.6, 0.66]); LIGHT /= np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0]); HALF /= np.linalg.norm(HALF)


@lru_cache(64)
def sphere_base(color, spec=0.5):
    n = 640
    y, x = np.mgrid[0:n, 0:n].astype(float)
    x = (x + 0.5) / n * 2 - 1; y = (y + 0.5) / n * 2 - 1
    d = x * x + y * y; z = np.sqrt(np.clip(1 - d, 0, 1))
    lam = np.clip(x * LIGHT[0] + y * LIGHT[1] + z * LIGHT[2], 0, 1)
    shade = 0.40 + 0.68 * lam
    rim = np.clip(1 - z, 0, 1) ** 3 * 0.15
    bounce = np.clip(y, 0, 1) * (1 - z) * 0.22
    sp = np.clip(x * HALF[0] + y * HALF[1] + z * HALF[2], 0, 1) ** 60 * spec
    c = np.array(color, float) / 255
    rgb = c * shade[..., None] + (bounce + rim)[..., None] * np.array([1.0, 0.95, 0.9]) * c + sp[..., None]
    a = np.clip((1 - np.sqrt(d)) * n * 0.5, 0, 1)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 1) * 255, a * 255]).astype(np.uint8))


def sphere(color, w, h, spec=0.5):
    return sphere_base(tuple(color), spec).resize((max(1, L(w)), max(1, L(h))), Image.BILINEAR)


@lru_cache(None)
def cyl(color, w, h, rad=0, spec=0.35):
    pw, ph = L(w), L(h)
    x = (np.arange(pw) + 0.5) / pw * 2 - 1
    z = np.sqrt(np.clip(1 - x * x, 0, 1))
    lam = np.clip(x * LIGHT[0] + z * LIGHT[2] + 0.25, 0, 1)
    shade = 0.42 + 0.6 * lam
    sp = np.clip(x * HALF[0] + z * HALF[2], 0, 1) ** 30 * spec
    row = np.clip(np.array(color, float) / 255 * shade[:, None] + sp[:, None], 0, 1)
    vy = np.linspace(1.06, 0.9, ph)[:, None, None]
    rgb = np.clip(row[None, :, :] * vy, 0, 1) * 255
    m = Image.new('L', (pw, ph), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=L(rad), fill=255)
    im = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); im.putalpha(m)
    return im


@lru_cache(None)
def shadow_base():
    m = Image.new('L', (256, 128), 0); ImageDraw.Draw(m).ellipse([24, 24, 232, 104], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(14))
    im = Image.new('RGBA', (256, 128), (0, 0, 0, 0)); im.putalpha(m.point(lambda a: int(a * 0.4)))
    return im


def put(img, spr, cx, cy):
    img.paste(spr, (int(round(cx * S - spr.width / 2)), int(round(cy * S - spr.height / 2))), spr)
def put_sphere(img, color, cx, cy, w, h, spec=0.5): put(img, sphere(color, w, h, spec), cx, cy)
def put_rot(img, spr, cx, cy, ang):
    put(img, spr.rotate(-ang, resample=Image.BICUBIC, expand=True) if ang else spr, cx, cy)
def put_shadow(img, cx, cy, w, h):
    put(img, shadow_base().resize((max(1, L(w)), max(1, L(h))), Image.BILINEAR), cx, cy)
def fade(spr, k):
    s = spr.copy(); s.putalpha(spr.getchannel('A').point(lambda a: int(a * k))); return s
def scaled(spr, s):
    return spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BILINEAR)


def particles(img, seed, t0, tt, n, origin, vx, vy, g, colors, size, life=2.0, emit=0.0):
    """Basit fizik parçacıkları. emit>0 ise parçacıklar emit saniye boyunca sırayla çıkar."""
    rnd = random.Random(seed)
    for k in range(n):
        te = t0 + (emit * k / n if emit else 0)
        c = rnd.choice(colors); ux, uy = rnd.uniform(*vx), rnd.uniform(*vy); s = rnd.uniform(*size)
        age = tt - te
        if 0 <= age < life:
            x = origin[0] + ux * age; y = origin[1] + uy * age + 0.5 * g * age * age
            if -60 < y < PH + 60: put_sphere(img, c, x, y, s, s, 0.6)


# ---------------------------------------------------------------- yazı
@lru_cache(None)
def font(sz): return ImageFont.truetype(FONT, sz)


@lru_cache(None)
def text_spr(txt, sz, fill, stroke=DARK):
    sw = max(2, sz // 9); f = font(sz); bb = f.getbbox(txt, stroke_width=sw)
    im = Image.new('RGBA', (bb[2] - bb[0] + 6, bb[3] - bb[1] + 6), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((3 - bb[0], 3 - bb[1]), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im


def put_text_px(img, txt, x, y, sz, fill, scale=1.0, rot=0, max_w=None):
    if scale <= 0.02: return
    spr = text_spr(txt, sz, fill)
    if max_w and spr.width > max_w: scale *= max_w / spr.width
    if scale != 1: spr = scaled(spr, scale)
    if rot: spr = spr.rotate(-rot, resample=Image.BICUBIC, expand=True)
    img.paste(spr, (int(x - spr.width / 2), int(y - spr.height / 2)), spr)


def put_text(img, txt, cx, cy, sz, fill, scale=1.0, rot=0, max_w=None):
    put_text_px(img, txt, L(cx), L(cy), L(sz), fill, scale, rot, L(max_w) if max_w else None)


# ---------------------------------------------------------------- sahne
ROOMS = ('living', 'kitchen', 'bedroom', 'office', 'bathroom', 'garage', 'cafe', 'library', 'gym', 'diner', 'arcade', 'studio', 'greenhouse', 'spaceship', 'hotel')
FLOORS = {'living': (196, 138, 88), 'kitchen': (214, 204, 186), 'bedroom': (176, 120, 150), 'office': (150, 152, 165),
          'bathroom': (225, 228, 238), 'garage': (128, 128, 134), 'cafe': (150, 100, 70),
          'library': (120, 80, 55), 'gym': (70, 72, 80), 'diner': (235, 235, 235),
          'arcade': (60, 42, 80), 'studio': (105, 90, 82), 'greenhouse': (150, 132, 100), 'spaceship': (140, 145, 158), 'hotel': (150, 40, 52)}


