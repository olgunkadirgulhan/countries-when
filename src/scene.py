

# ---------------------------------------------------------------- sahneler (arka planlar kodla çizilir)
def vgrad(w, h, c1, c2):
    t = np.linspace(0, 1, h)[:, None, None]
    return (np.array(c1, float) * (1 - t) + np.array(c2, float) * t) * np.ones((1, w, 1))


@lru_cache(None)
def scene_bg(kind):
    w, h = L(W), L(H)
    gy = int(h * 0.70)
    if kind == 'snow':
        a = vgrad(w, h, (170, 205, 240), (225, 238, 250))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        for k, (cx, r, c) in enumerate(((200, 520, (205, 222, 240)), (820, 600, (215, 230, 245)), (520, 700, (235, 243, 252)))):
            d.ellipse(box(cx - r, H * 0.70 - r * 0.45, cx + r, H * 0.70 + r * 0.55), fill=c)
        d.rectangle([0, gy, w, h], fill=(245, 249, 255))
        for x in (140, 930):
            d.polygon([(L(x), L(H * 0.70 - 260)), (L(x - 90), L(H * 0.70)), (L(x + 90), L(H * 0.70))], fill=(60, 120, 90))
            d.polygon([(L(x), L(H * 0.70 - 260)), (L(x - 40), L(H * 0.70 - 150)), (L(x + 40), L(H * 0.70 - 150))], fill=(250, 252, 255))
    elif kind == 'sun':
        a = vgrad(w, h, (90, 175, 245), (190, 228, 250))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        d.rectangle([0, gy - L(60), w, gy], fill=(40, 150, 210))
        d.rectangle([0, gy, w, h], fill=(244, 214, 150))
        for x in range(0, W, 120):
            d.arc(box(x, H * 0.70 - 85, x + 120, H * 0.70 - 35), 200, 340, fill=(200, 235, 250), width=L(5))
    elif kind == 'rain':
        a = vgrad(w, h, (95, 105, 125), (150, 158, 172))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        for cx, cy, r in ((200, 300, 160), (420, 260, 190), (700, 320, 170), (920, 270, 150)):
            d.ellipse(box(cx - r, cy - r * 0.6, cx + r, cy + r * 0.6), fill=(120, 128, 145))
        d.rectangle([0, gy, w, h], fill=(80, 88, 100))
        for x in (160, 560, 900):
            d.ellipse(box(x - 120, H * 0.80, x + 120, H * 0.80 + 30), fill=(110, 125, 150))
    elif kind == 'night':
        a = vgrad(w, h, (10, 12, 40), (45, 35, 90))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        rnd = random.Random(3)
        for _ in range(90):
            x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd.uniform(1.5, 4)
            d.ellipse(box(x - r, y - r, x + r, y + r), fill=(255, 255, 230))
        for i, (x0, bw, bh) in enumerate(((0, 160, 420), (150, 120, 560), (260, 180, 380), (430, 140, 640), (560, 170, 470),
                                           (720, 130, 520), (840, 240, 400))):
            d.rectangle(box(x0, H * 0.70 - bh, x0 + bw, H * 0.70), fill=(25, 22, 50))
            for wy in range(int(H * 0.70 - bh + 30), int(H * 0.70) - 30, 55):
                for wx in range(x0 + 20, x0 + bw - 25, 45):
                    if rnd.random() < 0.45: d.rectangle(box(wx, wy, wx + 18, wy + 24), fill=(255, 220, 120))
        d.rectangle([0, gy, w, h], fill=(30, 28, 55))
    elif kind == 'stadium':
        a = vgrad(w, h, (25, 30, 70), (60, 70, 120))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        d.polygon([(0, L(H * 0.18)), (w, L(H * 0.18)), (w, gy), (0, gy)], fill=(45, 45, 70))
        rnd = random.Random(5)
        for _ in range(900):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.2, H * 0.68)
            d.ellipse(box(x - 7, y - 7, x + 7, y + 7), fill=rnd.choice([(230, 80, 80), (255, 210, 60), (80, 150, 240), (240, 240, 240), (90, 200, 120)]))
        d.rectangle([0, gy, w, h], fill=(60, 160, 70))
        for k in range(6):
            d.rectangle(box(0, H * 0.70 + k * 100, W, H * 0.70 + k * 100 + 50), fill=(70, 172, 80))
        d.line(box(0, H * 0.70 + 10, W, H * 0.70 + 10), fill=(240, 240, 240), width=L(8))
        for x in (60, 1020):
            d.rectangle(box(x - 6, 80, x + 6, H * 0.18), fill=(200, 200, 210))
            d.ellipse(box(x - 50, 40, x + 50, 110), fill=(255, 255, 220))
    elif kind == 'city':
        a = vgrad(w, h, (255, 190, 140), (255, 225, 190))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        rnd = random.Random(8)
        x = 0
        while x < W:
            bw, bh = rnd.uniform(110, 200), rnd.uniform(350, 800)
            col = rnd.choice([(120, 110, 150), (150, 120, 140), (110, 120, 160), (170, 140, 150)])
            d.rectangle(box(x, H * 0.70 - bh, x + bw, H * 0.70), fill=col)
            for wy in range(int(H * 0.70 - bh + 30), int(H * 0.70) - 30, 60):
                for wx in range(int(x + 18), int(x + bw - 30), 48):
                    d.rectangle(box(wx, wy, wx + 22, wy + 30), fill=(255, 235, 190) if rnd.random() < 0.5 else (90, 90, 120))
            x += bw + 8
        d.rectangle([0, gy, w, h], fill=(110, 110, 120))
        for k in range(0, W, 160):
            d.rectangle(box(k, H * 0.83, k + 90, H * 0.83 + 16), fill=(240, 240, 240))
    elif kind == 'park':   # 2026-10-25 yeni ortam: park (çimen, ağaçlar, bank)
        a = vgrad(w, h, (120, 195, 245), (200, 232, 250))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        for cx, cy, r in ((230, 260, 90), (330, 240, 110), (800, 300, 100)):
            d.ellipse(box(cx - r, cy - r * 0.55, cx + r, cy + r * 0.55), fill=(250, 252, 255))
        d.ellipse(box(-300, H * 0.58, W * 0.6, H * 0.85), fill=(120, 190, 100))
        d.ellipse(box(W * 0.4, H * 0.6, W + 300, H * 0.86), fill=(105, 178, 92))
        for x, tw in ((120, 150), (930, 170), (520, 120)):
            d.rectangle(box(x - 16, H * 0.70 - 230, x + 16, H * 0.70), fill=(120, 80, 50))
            d.ellipse(box(x - tw, H * 0.70 - 230 - tw * 1.3, x + tw, H * 0.70 - 230 + tw * 0.5), fill=(70, 150, 80))
        d.rectangle([0, gy, w, h], fill=(110, 185, 95))
        d.rounded_rectangle(box(380, H * 0.70 - 120, 700, H * 0.70 - 90), radius=L(8), fill=(150, 100, 60))
    elif kind == 'office':   # açık ofis: pencere şeridi, masalar, monitörler
        a = vgrad(w, h, (215, 222, 232), (185, 194, 208))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        for x0 in range(40, W, 260):
            d.rectangle(box(x0, 180, x0 + 220, 620), fill=(170, 210, 240), outline=(240, 244, 250), width=L(10))
            d.rectangle(box(x0 + 20, 470, x0 + 70, 620), fill=(120, 140, 170))
            d.rectangle(box(x0 + 100, 400, x0 + 160, 620), fill=(110, 128, 160))
        d.rectangle([0, gy, w, h], fill=(120, 125, 140))
        for x0 in (40, 600):
            d.rectangle(box(x0, H * 0.70 - 150, x0 + 440, H * 0.70 - 125), fill=(235, 235, 240))
            d.rounded_rectangle(box(x0 + 140, H * 0.70 - 330, x0 + 300, H * 0.70 - 200), radius=L(8), fill=(40, 44, 60))
            d.rectangle(box(x0 + 150, H * 0.70 - 320, x0 + 290, H * 0.70 - 212), fill=(90, 160, 220))
            d.rectangle(box(x0 + 210, H * 0.70 - 200, x0 + 230, H * 0.70 - 150), fill=(40, 44, 60))
    elif kind == 'airport':   # terminal: dev cam, uçak, kalkış tabelası
        a = vgrad(w, h, (100, 170, 230), (190, 220, 245))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        d.rectangle(box(0, H * 0.52, W, H * 0.70), fill=(150, 150, 160))
        px, py = 560, 520
        d.ellipse(box(px - 300, py - 45, px + 300, py + 45), fill=(245, 246, 250))
        d.polygon([(L(px - 40), L(py)), (L(px + 120), L(py + 170)), (L(px + 190), L(py + 170)), (L(px + 90), L(py))], fill=(225, 228, 236))
        d.polygon([(L(px + 220), L(py - 20)), (L(px + 300), L(py - 170)), (L(px + 330), L(py - 170)), (L(px + 300), L(py))], fill=(220, 70, 70))
        for x0 in range(0, W + 1, 180):
            d.rectangle(box(x0 - 8, 0, x0 + 8, H * 0.70), fill=(70, 80, 95))
        d.rectangle(box(0, 0, W, 60), fill=(70, 80, 95))
        d.rounded_rectangle(box(80, 110, 470, 300), radius=L(10), fill=(25, 28, 40))
        for k in range(5):
            d.rectangle(box(100, 130 + k * 34, 300, 150 + k * 34), fill=(255, 200, 60))
            d.rectangle(box(320, 130 + k * 34, 450, 150 + k * 34), fill=(120, 230, 140) if k % 2 else (240, 90, 80))
        d.rectangle([0, gy, w, h], fill=(200, 200, 205))
        for y in range(int(H * 0.70) + 70, H, 110):
            d.line(box(0, y, W, y), fill=(180, 180, 188), width=L(4))
    elif kind == 'market':   # süpermarket rafları
        a = vgrad(w, h, (245, 245, 240), (220, 222, 218))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        rnd = random.Random(21)
        for y0 in (180, 360, 540):
            d.rectangle(box(0, y0 + 130, W, y0 + 145), fill=(150, 150, 160))
            x = 10
            while x < W:
                bw, bh = rnd.uniform(40, 80), rnd.uniform(70, 125)
                d.rounded_rectangle(box(x, y0 + 130 - bh, x + bw, y0 + 130), radius=L(6),
                                    fill=rnd.choice([(230, 80, 70), (250, 200, 60), (80, 160, 230), (110, 200, 120), (240, 140, 60), (180, 110, 200)]))
                x += bw + 6
        d.rectangle(box(0, 90, W, 150), fill=(60, 150, 90))
        d.rectangle([0, gy, w, h], fill=(225, 225, 228))
        for x in range(0, W, 120):
            d.line(box(x, H * 0.70, x - 120, H), fill=(205, 205, 210), width=L(3))
    else:  # kitchen, living, party (iç mekân)
        wall = {'kitchen': (245, 230, 200), 'living': (205, 225, 240), 'party': (250, 215, 235)}.get(kind, (230, 230, 230))
        a = vgrad(w, h, wall, tuple(int(c * 0.86) for c in wall))
        img = Image.fromarray(a.astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
        d.rectangle([0, gy, w, h], fill=(190, 140, 95))
        for y in range(int(H * 0.70) + 60, H, 90):
            d.line(box(0, y, W, y), fill=(165, 118, 78), width=L(4))
        d.rectangle(box(0, H * 0.70 - 18, W, H * 0.70 + 4), fill=(250, 245, 238))
        if kind == 'kitchen':
            for x0 in (60, 330, 600, 870):
                d.rounded_rectangle(box(x0, 230, x0 + 200, 520), radius=L(10), fill=(250, 250, 245), outline=(180, 170, 160), width=L(4))
            for yy in range(560, int(H * 0.70) - 30, 70):
                for xx in range(0, W, 70):
                    d.rectangle(box(xx, yy, xx + 66, yy + 66), outline=tuple(int(c * 0.9) for c in wall), width=L(3))
        elif kind == 'living':
            d.rounded_rectangle(box(660, 300, 980, 560), radius=L(10), fill=(250, 250, 248))
            d.rectangle(box(676, 316, 964, 544), fill=(160, 210, 245))
            d.rounded_rectangle(box(60, 1020, 470, 1260), radius=L(40), fill=(200, 90, 90))
            d.rounded_rectangle(box(40, 960, 140, 1260), radius=L(40), fill=(180, 75, 75))
            d.rounded_rectangle(box(390, 960, 490, 1260), radius=L(40), fill=(180, 75, 75))
        else:
            for k in range(14):
                x = k * 80
                d.polygon([(L(x), L(260)), (L(x + 80), L(260)), (L(x + 40), L(340))],
                          fill=[(255, 90, 120), (255, 210, 60), (80, 170, 255), (120, 220, 130)][k % 4])
            d.line(box(0, 260, W, 260), fill=(120, 80, 60), width=L(5))
    return img


def effects(img, kind, t):
    d = ImageDraw.Draw(img)
    if kind == 'snow':
        rnd = random.Random(11)
        for j in range(70):
            x0, sp, r = rnd.uniform(0, W), rnd.uniform(90, 200), rnd.uniform(5, 13)
            y = (rnd.uniform(0, H) + t * sp) % H; x = x0 + 25 * math.sin(t * 1.3 + j)
            d.ellipse(box(x - r, y - r, x + r, y + r), fill=(255, 255, 255))
    elif kind == 'rain':
        rnd = random.Random(12)
        for j in range(90):
            x0, sp = rnd.uniform(0, W + 200), rnd.uniform(1300, 1800)
            y = (rnd.uniform(0, H) + t * sp) % H; x = x0 - y * 0.15
            d.line(box(x, y, x - 8, y + 46), fill=(200, 215, 240), width=L(3))
    elif kind == 'sun':
        put_sphere(img, (255, 230, 90), 880, 480, 200 + 12 * math.sin(t * 3), 200 + 12 * math.sin(t * 3), 0.2)
    elif kind == 'night':
        for j in range(3):
            t0 = (t + j * 1.1) % 3.3
            cx, cy = 200 + 330 * j, 300 + 120 * (j % 2)
            col = [(255, 90, 120), (255, 220, 70), (120, 200, 255)][j]
            if t0 < 1.4:
                for k in range(16):
                    a = k / 16 * 2 * math.pi; r = 40 + 230 * t0
                    x, y = cx + math.cos(a) * r, cy + math.sin(a) * r + 60 * t0 * t0
                    s_ = 12 * (1 - t0 / 1.4) + 2
                    d.ellipse(box(x - s_, y - s_, x + s_, y + s_), fill=col)
    elif kind == 'party':
        rnd = random.Random(13)
        for j in range(40):
            x0, sp = rnd.uniform(0, W), rnd.uniform(150, 300)
            y = (rnd.uniform(0, H) + t * sp) % H; x = x0 + 30 * math.sin(t * 2 + j)
            col = [(255, 90, 120), (255, 210, 60), (80, 170, 255), (120, 220, 130)][j % 4]
            d.rectangle(box(x - 8, y - 5, x + 8, y + 5), fill=col)
    elif kind == 'stadium':
        rnd = random.Random(14)
        for j in range(25):
            if (t * 4 + j) % 3 < 0.3:
                x, y = rnd.uniform(0, W), rnd.uniform(H * 0.2, H * 0.6)
                d.ellipse(box(x - 9, y - 9, x + 9, y + 9), fill=(255, 255, 255))


# ---------------------------------------------------------------- countryball
@lru_cache(64)
def flag_img(code):
    return Image.open(os.path.join(HERE, 'flags', f'{code}.png')).convert('RGB')


@lru_cache(64)
def ball_sprite(code, d, tint=None):
    """Bayrak dokulu, ışıklı top (d piksel, S ölçekli). tint: (r,g,b,alfa) üst renk (ör. üşüme = mavi)."""
    n = L(d)
    fl = flag_img(code)
    fw = int(n * 1.45)
    fl = fl.resize((fw, n), Image.LANCZOS).crop(((fw - n) // 2, 0, (fw - n) // 2 + n, n))
    a = np.asarray(fl, float) / 255
    y, x = np.mgrid[0:n, 0:n].astype(float)
    x = (x + 0.5) / n * 2 - 1; y = (y + 0.5) / n * 2 - 1
    dd = x * x + y * y; z = np.sqrt(np.clip(1 - dd, 0, 1))
    lam = np.clip(x * -0.45 + y * -0.6 + z * 0.66, 0, 1)
    shade = 0.55 + 0.55 * lam
    sp = np.clip(x * -0.3 + y * -0.45 + z * 0.84, 0, 1) ** 45 * 0.55
    rgb = np.clip(a * shade[..., None] + sp[..., None], 0, 1)
    if tint:
        rgb = rgb * (1 - tint[3]) + np.array(tint[:3]) / 255 * tint[3]
    alpha = np.clip((1 - np.sqrt(dd)) * n * 0.5, 0, 1)
    im = Image.fromarray(np.dstack([rgb * 255, alpha * 255]).astype(np.uint8))
    ImageDraw.Draw(im).ellipse([1, 1, n - 2, n - 2], outline=(20, 20, 25, 255), width=max(2, int(n * 0.022)))
    return im


def eyes(img, cx, cy, d, mood, t, look=(0.0, 0.0)):
    dr = ImageDraw.Draw(img)
    ew, eh = d * 0.17, d * 0.21
    big = mood in ('shock', 'shiver')
    if big: ew, eh = d * 0.21, d * 0.26
    lw = max(3, L(d * 0.016))
    for s in (-1, 1):
        ex, ey = cx + s * d * 0.19, cy - d * 0.06
        if mood == 'cool':
            continue
        if mood == 'happy':
            dr.arc(box(ex - ew / 2, ey - eh * 0.2, ex + ew / 2, ey + eh * 0.8), 200, 340, fill=(255, 255, 255), width=L(d * 0.05))
            dr.arc(box(ex - ew / 2 - 3, ey - eh * 0.2 - 3, ex + ew / 2 + 3, ey + eh * 0.8 + 3), 200, 340, fill=(20, 20, 25), width=lw)
            continue
        if mood == 'sleepy':
            dr.line(box(ex - ew / 2, ey + eh * 0.1, ex + ew / 2, ey + eh * 0.1), fill=(20, 20, 25), width=L(d * 0.02))
            continue
        if mood == 'love':   # beyaz kenarlı kalp (kırmızı bayraklarda da görünsün)
            for dx in (-0.22, 0.22):
                put_sphere(img, (255, 255, 255), ex + dx * ew, ey - eh * 0.15, ew * 0.78, ew * 0.78, 0.0)
            dr.polygon([(L(ex - ew * 0.66), L(ey - eh * 0.08)), (L(ex + ew * 0.66), L(ey - eh * 0.08)), (L(ex), L(ey + eh * 0.66))],
                       fill=(255, 255, 255))
            for dx in (-0.22, 0.22):
                put_sphere(img, (235, 45, 75), ex + dx * ew, ey - eh * 0.15, ew * 0.6, ew * 0.6, 0.5)
            dr.polygon([(L(ex - ew * 0.52), L(ey - eh * 0.05)), (L(ex + ew * 0.52), L(ey - eh * 0.05)), (L(ex), L(ey + eh * 0.5))],
                       fill=(235, 45, 75))
            continue
        dr.ellipse(box(ex - ew / 2, ey - eh / 2, ex + ew / 2, ey + eh / 2), fill=(255, 255, 255), outline=(20, 20, 25), width=lw)
        pr = ew * (0.16 if big else 0.28)
        px, py = ex + look[0] * ew * 0.22, ey + look[1] * eh * 0.22
        dr.ellipse(box(px - pr, py - pr, px + pr, py + pr), fill=(20, 20, 25))
        if mood == 'calm':   # yarı kapalı göz kapağı
            dr.chord(box(ex - ew / 2 - 2, ey - eh / 2 - 2, ex + ew / 2 + 2, ey + eh / 2 + 2), 180, 360, fill=(20, 20, 25))
        if mood == 'angry':
            dr.line(box(ex - s * ew * 0.6, ey - eh * 0.75, ex + s * ew * 0.5, ey - eh * 0.4), fill=(20, 20, 25), width=L(d * 0.03))
        if mood == 'cry':
            k = (t * 2) % 1
            put_sphere(img, (110, 180, 250), ex, ey + eh * 0.6 + k * d * 0.25, d * 0.05, d * 0.08, 0.8)
    if mood == 'cool':  # güneş gözlüğü
        dr.rounded_rectangle(box(cx - d * 0.36, cy - d * 0.14, cx + d * 0.36, cy + d * 0.02), radius=L(d * 0.05), fill=(15, 15, 20))
        dr.line(box(cx - d * 0.30, cy - d * 0.10, cx - d * 0.18, cy - d * 0.10), fill=(120, 120, 130), width=L(d * 0.015))


def ball(img, code, cx, cy, d, mood='normal', t=0.0, squash=0.0, look=(0.0, 0.0)):
    put_shadow(img, cx, cy + d * 0.5, d * 0.9, d * 0.16)
    tint = (120, 180, 255, 0.25) if mood == 'shiver' else (255, 60, 40, 0.18) if mood == 'angry' else None
    spr = ball_sprite(code, int(d), tint)
    if squash:
        spr = spr.resize((int(spr.width * (1 + squash)), int(spr.height * (1 - squash))), Image.BILINEAR)
    put(img, spr, cx, cy + d * squash * 0.5)
    eyes(img, cx, cy + d * squash * 0.4, d, mood, t, look)
    if mood == 'sleepy':
        for j in range(3):
            u = (t * 0.7 + j / 3) % 1
            put_text(img, 'Z', cx + d * 0.45 + 40 * u, cy - d * 0.5 - 120 * u, 40 + 30 * u, (255, 255, 255), scale=min(1, u * 4) * (1 - u) * 1.6)
    if mood == 'shiver':
        put_text(img, 'BRRR', cx + d * 0.55, cy - d * 0.55, 54, (190, 225, 255), rot=10)


# ---------------------------------------------------------------- konuşma balonu (aksanlı harfler için yedek yazı tipi)
FONT2 = os.path.join(HERE, 'fonts', 'Anton-Regular.ttf')


@lru_cache(None)
def font_for(text, sz):
    f = ImageFont.truetype(FONT, sz)
    notdef = f.getmask('￿').getbbox()
    missing = any(f.getmask(ch).getbbox() == notdef for ch in set(text) if not ch.isspace() and ord(ch) > 127)
    return ImageFont.truetype(FONT2, sz) if missing and os.path.exists(FONT2) else f


def wrap(txt, f, maxw):
    words, lines, cur = txt.split(), [], ''
    for w in words:
        nxt = (cur + ' ' + w).strip()
        if f.getlength(nxt) <= maxw: cur = nxt
        else: lines.append(cur); cur = w
    lines.append(cur)
    return [l for l in lines if l]


def bubble(img, txt, cx, cy, tail_to, k):
    if k <= 0.01: return
    f = font_for(txt, L(74))
    lines = wrap(txt, f, L(860))
    lh = f.getbbox('Ag')[3] + L(10)
    tw = max(f.getlength(l) for l in lines); th = lh * len(lines)
    pad = L(40)
    layer = Image.new('RGBA', (int(tw + 2 * pad + L(20)), int(th + 2 * pad + L(70))), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([L(6), L(6), tw + 2 * pad, th + 2 * pad], radius=L(44), fill=(255, 255, 255), outline=(20, 20, 25), width=L(6))
    bx = (tw + 2 * pad) / 2
    d.polygon([(bx - L(40), th + 2 * pad - L(4)), (bx + L(40), th + 2 * pad - L(4)), (bx + L(10) * (1 if tail_to >= 0 else -1), th + 2 * pad + L(60))],
              fill=(255, 255, 255), outline=(20, 20, 25))
    d.rectangle([bx - L(36), th + 2 * pad - L(12), bx + L(36), th + 2 * pad - L(2)], fill=(255, 255, 255))
    for i, ln in enumerate(lines):
        d.text(((tw + 2 * pad) / 2 - f.getlength(ln) / 2 + L(4), pad + i * lh), ln, font=f, fill=(25, 25, 30))
    s = back(k)
    lay = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.BILINEAR)
    img.paste(lay, (int(L(cx) - lay.width / 2), int(L(cy) - lay.height)), lay)


SCENES = ('snow', 'sun', 'rain', 'night', 'stadium', 'city', 'kitchen', 'living', 'party', 'park', 'office', 'airport', 'market')
