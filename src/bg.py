@lru_cache(None)
def background(wall, room='living'):
    w, h = L(W), L(PH)
    yy = np.arange(h)[:, None] / S; xx = np.arange(w)[None, :] / S
    k = 0.84 + 0.2 * (yy / FLOOR)
    if room == 'bedroom':      # puantiyeli duvar kâğıdı
        stripe = ((((xx + 30 * ((yy // 60) % 2)) % 60 - 30) ** 2 + ((yy % 60) - 30) ** 2) < 49) * 0.06
    elif room == 'office':
        stripe = 0.0 * xx
    elif room == 'bathroom':   # tam duvar fayans
        stripe = (((xx % 60) < 3) | ((yy % 60) < 3)) * -0.10 + 0.0 * yy
    elif room == 'garage':     # beton paneller
        stripe = ((xx // 160) % 2) * -0.03 + (((xx % 160) < 3) * -0.08) + 0.0 * yy
    elif room == 'arcade':     # karanlık + neon şeritler
        stripe = -0.5 + (((yy % 120) < 6) * 0.9) + 0.0 * xx
    elif room == 'studio':     # akustik sünger
        stripe = ((((xx % 50) - 25) ** 2 + ((yy % 50) - 25) ** 2) < 200) * -0.12 - 0.15
    elif room == 'greenhouse': # cam paneller
        stripe = (((xx % 140) < 5) | ((yy % 140) < 5)) * 0.18 + 0.05 + 0.0 * yy
    elif room == 'spaceship':  # metal paneller + perçin
        stripe = (((xx % 180) < 4) | ((yy % 120) < 4)) * -0.2 + ((((xx % 180) - 14) ** 2 + ((yy % 120) - 14) ** 2) < 20) * -0.3 - 0.1
    elif room == 'hotel':      # geniş altın çizgiler
        stripe = (((xx // 45) % 3) == 0) * 0.08 + ((yy > 420) & (yy < 430)) * -0.3
    elif room == 'library':    # ahşap lambri
        stripe = ((xx % 90) < 4) * -0.18 + (yy > 380) * -0.10
    elif room == 'gym':
        stripe = ((yy > 360) & (yy < 400)) * 0.25 + 0.0 * xx
    elif room == 'diner':      # alt duvar dama
        stripe = ((yy > 380) & (((xx // 50) + (yy // 50)) % 2 == 0)) * -0.35 + 0.0 * xx
    elif room == 'cafe':       # tuğla
        stripe = (((yy % 40) < 4) | (((xx + 40 * ((yy // 40) % 2)) % 80) < 4)) * -0.16 + ((xx * 7 + (yy // 40) * 13) % 5 == 0) * 0.0
    elif room == 'kitchen':    # alt duvarda fayans
        stripe = ((yy > 380) & (((xx % 70) < 3) | ((yy % 70) < 3))) * -0.12
    else:
        stripe = ((xx // 60) % 2 == 0) * 0.035
    rgb_w = np.array(wall, float) * (k + stripe)[..., None]
    fy = np.clip((yy - FLOOR) / (PH - FLOOR), 0, 1)
    rgb_f = np.array(FLOORS.get(room, FLOORS['living']), float) * (0.8 + 0.28 * fy)[..., None] * np.ones_like(xx)[..., None]
    rgb = np.where((yy < FLOOR)[..., None], rgb_w, rgb_f)
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for y in (628, 662, 706, 760, 826):
        d.line(box(0, y, W, y), fill=(150, 100, 60), width=L(2))
    d.rectangle(box(0, FLOOR - 18, W, FLOOR + 2), fill=(246, 240, 232))
    d.line(box(0, FLOOR + 2, W, FLOOR + 2), fill=(170, 150, 130), width=L(3))
    d.rounded_rectangle(box(660, 60, 960, 330), radius=L(14), fill=(250, 250, 248))
    for i in range(0, 250):
        d.line(box(676, 76 + i, 944, 76 + i), fill=lerpc((120, 190, 250), (205, 235, 255), i / 250))
    for cx_, cy_, s in ((740, 150, 1.0), (880, 230, 0.7)):
        for dx, dy, r in ((-30, 8, 26), (0, 0, 36), (32, 8, 26)):
            d.ellipse(box(cx_ + dx * s - r * s, cy_ + dy * s - r * s, cx_ + dx * s + r * s, cy_ + dy * s + r * s), fill=(255, 255, 255))
    if room == 'office':       # pencerede şehir
        for k_, (bx, bh) in enumerate(((690, 120), (740, 170), (800, 90), (850, 150), (905, 110))):
            d.rectangle(box(bx, 326 - bh, bx + 44, 326), fill=(150, 165, 190))
            for wy in range(int(326 - bh + 12), 316, 26):
                d.rectangle(box(bx + 10, wy, bx + 18, wy + 10), fill=(255, 240, 170)); d.rectangle(box(bx + 26, wy, bx + 34, wy + 10), fill=(255, 240, 170))
    d.rectangle(box(806, 76, 814, 314), fill=(250, 250, 248)); d.rectangle(box(676, 195, 944, 203), fill=(250, 250, 248))
    if room == 'kitchen':      # üst dolap
        for x0 in (40, 190):
            d.rounded_rectangle(box(x0, 50, x0 + 140, 260), radius=L(8), fill=(245, 245, 240), outline=(170, 160, 150), width=L(3))
            d.rounded_rectangle(box(x0 + 110, 140, x0 + 120, 190), radius=L(4), fill=(150, 150, 160))
    elif room == 'bedroom':    # yıldızlı poster
        d.rounded_rectangle(box(70, 80, 250, 300), radius=L(6), fill=(60, 50, 110))
        for sx_, sy_, r_ in ((120, 140, 10), (200, 120, 7), (160, 220, 14), (220, 260, 6), (100, 270, 8)):
            d.ellipse(box(sx_ - r_, sy_ - r_, sx_ + r_, sy_ + r_), fill=(255, 230, 120))
        d.ellipse(box(170, 140, 230, 200), fill=(250, 245, 220)); d.ellipse(box(188, 132, 244, 188), fill=(60, 50, 110))
    elif room == 'bathroom':   # ayna
        d.ellipse(box(60, 60, 260, 320), fill=(200, 200, 205)); d.ellipse(box(74, 74, 246, 306), fill=(200, 230, 245))
        d.line(box(110, 120, 150, 90), fill=(255, 255, 255), width=L(8)); d.line(box(110, 170, 190, 100), fill=(255, 255, 255), width=L(6))
    elif room == 'garage':     # alet panosu
        d.rectangle(box(40, 70, 300, 330), fill=(175, 140, 100))
        for yh in range(85, 330, 24):
            for xh in range(55, 300, 24): d.ellipse(box(xh - 3, yh - 3, xh + 3, yh + 3), fill=(120, 95, 70))
        d.rectangle(box(80, 110, 92, 230), fill=(120, 80, 50)); d.rectangle(box(62, 100, 110, 130), fill=(110, 110, 120))
        d.rectangle(box(170, 110, 182, 260), fill=(150, 150, 160)); d.ellipse(box(158, 92, 194, 128), outline=(150, 150, 160), width=L(10))
        d.rounded_rectangle(box(220, 120, 280, 280), radius=L(8), fill=(220, 60, 50))
    elif room == 'arcade':     # oyun makinesi
        d.rounded_rectangle(box(60, 60, 280, 360), radius=L(16), fill=(30, 20, 60), outline=(80, 220, 255), width=L(6))
        d.rectangle(box(90, 100, 250, 220), fill=(20, 200, 140)); d.rectangle(box(110, 130, 140, 150), fill=(255, 230, 60))
        d.ellipse(box(180, 150, 210, 180), fill=(255, 80, 150))
        for x in (110, 150, 190, 230): d.ellipse(box(x - 12, 260, x + 12, 284), fill=(255, 80, 150) if x % 80 else (80, 220, 255))
    elif room == 'studio':     # ON AIR
        d.rounded_rectangle(box(70, 150, 300, 250), radius=L(14), fill=(200, 30, 40), outline=(255, 120, 120), width=L(6))
        f_ = font(L(54)); tw = d.textlength('ON AIR', font=f_); d.text((L(185) - tw / 2, L(176)), 'ON AIR', font=f_, fill=(255, 255, 255))
    elif room == 'greenhouse': # asılı saksılar
        for x, yb in ((110, 210), (230, 260)):
            d.line(box(x, 40, x, yb - 40), fill=(90, 70, 50), width=L(4))
            d.rounded_rectangle(box(x - 40, yb - 40, x + 40, yb + 10), radius=L(10), fill=(200, 100, 60))
            for k in range(5): d.ellipse(box(x - 60 + k * 26, yb - 70 + (k % 2) * 16, x - 20 + k * 26, yb - 30 + (k % 2) * 16), fill=(70, 170, 80))
    elif room == 'spaceship':  # lomboz + kontrol paneli
        d.ellipse(box(684, 64, 936, 336), fill=(12, 12, 32), outline=(170, 175, 190), width=L(16))
        for k in range(14):
            r_ = random.Random(k); sx_, sy_ = r_.uniform(720, 900), r_.uniform(100, 300); rr = r_.uniform(2, 5)
            d.ellipse(box(sx_ - rr, sy_ - rr, sx_ + rr, sy_ + rr), fill=(255, 255, 230))
        d.ellipse(box(820, 220, 880, 280), fill=(230, 120, 70))
        d.rounded_rectangle(box(50, 120, 300, 280), radius=L(12), fill=(50, 55, 70))
        for k in range(8): d.ellipse(box(75 + (k % 4) * 55, 150 + (k // 4) * 60, 105 + (k % 4) * 55, 180 + (k // 4) * 60), fill=[(255, 80, 80), (80, 220, 120), (255, 220, 60), (80, 170, 255)][k % 4])
    elif room == 'hotel':      # altın çerçeveli tablo
        d.rectangle(box(60, 80, 290, 300), fill=(200, 160, 60)); d.rectangle(box(78, 98, 272, 282), fill=(70, 110, 150))
        d.polygon([(L(78), L(282)), (L(150), L(170)), (L(200), L(230)), (L(272), L(150)), (L(272), L(282))], fill=(60, 130, 90))
    elif room == 'library':    # büyük kitaplık
        d.rectangle(box(30, 40, 320, 360), fill=(95, 60, 40))
        for shelf in (40, 120, 200, 280):
            d.rectangle(box(30, shelf + 72, 320, shelf + 80), fill=(70, 45, 30))
            x = 40
            for j in range(9):
                bw = 20 + (j * 7 + shelf) % 12; bh = 50 + (j * 13 + shelf) % 18
                d.rectangle(box(x, shelf + 72 - bh, x + bw, shelf + 72), fill=[(150, 50, 50), (50, 90, 150), (190, 150, 60), (60, 120, 80), (110, 70, 140)][(j + shelf // 40) % 5])
                x += bw + 4
    elif room == 'gym':        # motivasyon posteri
        d.rounded_rectangle(box(50, 70, 290, 320), radius=L(8), fill=(30, 30, 35), outline=(255, 210, 50), width=L(6))
        for i_, (tx, sz_) in enumerate((('NO', 40), ('PAIN', 46), ('NO', 40), ('GAIN', 46))):
            f_ = font(L(sz_)); tw = d.textlength(tx, font=f_)
            d.text((L(170) - tw / 2, L(95 + i_ * 54)), tx, font=f_, fill=(255, 210, 50) if i_ % 2 else (255, 255, 255))
    elif room == 'diner':      # neon tabela
        d.rounded_rectangle(box(70, 150, 310, 290), radius=L(20), fill=(40, 30, 50), outline=(255, 80, 150), width=L(8))
        f_ = font(L(76)); tw = d.textlength('EAT', font=f_)
        d.text((L(190) - tw / 2, L(176)), 'EAT', font=f_, fill=(255, 120, 190))
    elif room == 'cafe':       # tebeşir menü
        d.rounded_rectangle(box(40, 70, 300, 330), radius=L(8), fill=(120, 80, 50))
        d.rectangle(box(54, 84, 286, 316), fill=(40, 50, 45))
        bloop_menu = [(170, 120, 'MENU'), (170, 190, 'coffee ~ 3'), (170, 240, 'cake ~ 4'), (170, 290, 'tea ~ 2')]
        for x_, y_, tx in bloop_menu:
            f_ = font(L(30 if tx == 'MENU' else 22)); tw = d.textlength(tx, font=f_)
            d.text((L(x_) - tw / 2, L(y_) - L(16)), tx, font=f_, fill=(235, 235, 225))
    elif room == 'office':     # kitaplık
        d.rectangle(box(50, 60, 280, 340), fill=(130, 90, 60))
        for shelf in (60, 150, 240):
            d.rectangle(box(50, shelf + 82, 280, shelf + 90), fill=(100, 65, 40))
            x = 62
            for j in range(7):
                bw = 22 + (j * 7) % 13; bh = 58 + (j * 11) % 20
                d.rectangle(box(x, shelf + 82 - bh, x + bw, shelf + 82), fill=[(200, 70, 70), (70, 120, 200), (240, 190, 60), (90, 170, 110), (160, 100, 190)][(j + shelf) % 5])
                x += bw + 5
    else:
        d.rounded_rectangle(box(60, 90, 240, 240), radius=L(6), fill=(120, 80, 50))
        d.rectangle(box(74, 104, 226, 226), fill=(170, 220, 240))
        d.polygon([(L(74), L(226)), (L(130), L(150)), (L(170), L(200)), (L(200), L(170)), (L(226), L(226))], fill=(90, 170, 90))
        d.ellipse(box(180, 118, 210, 148), fill=(255, 210, 60))
    put_shadow(img, (TX0 + TX1) / 2, GY + 6, 470, 46)
    for x in (TX0 + 30, TX1 - 30):
        put(img, cyl((120, 72, 40), 26, 250, 6), x, 690)
    d.rounded_rectangle(box(TX0 - 12, TTOP - 10, TX1 + 12, TTOP + 14), radius=L(10), fill=(212, 148, 92))
    d.rounded_rectangle(box(TX0 - 12, TTOP + 8, TX1 + 12, TTOP + 40), radius=L(8), fill=(150, 90, 50))
    d.line(box(TX0 - 4, TTOP + 10, TX1 + 4, TTOP + 10), fill=(230, 175, 120), width=L(3))
    return img


