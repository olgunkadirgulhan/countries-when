#!/usr/bin/env python3
"""Countries When... video motoru: bayraklı top karakterler (countryball tarzı) aynı duruma ülkelerine göre tepki verir.

Telif yok: karakterler, bayraklar (kodla çizildi), sahneler, müzik ve efektler kodla üretilir; yardımcılar Bloop Bonkers motorundan.
Bir video = plan (durum + 4 ülke + müzik tohumu). Planı run.py seçer.

  python balls.py --preview 2,6,12 [--sit snow] [--countries CA,BR,TR,JP]
"""
import glob, math, os, random, subprocess, sys, wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, S = 1080, 1920, 30, 2
PH = H
FONT = os.path.join(HERE, 'fonts', 'LuckiestGuy-Regular.ttf')
INTRO, TURN, OUTRO = 1.5, 4.0, 3.6
SR = 44100
DARK = (28, 22, 40)

NAMES = {'US': 'USA', 'GB': 'UK', 'DE': 'GERMANY', 'FR': 'FRANCE', 'IT': 'ITALY', 'BR': 'BRAZIL', 'JP': 'JAPAN',
         'TR': 'TURKEY', 'CA': 'CANADA', 'MX': 'MEXICO', 'IN': 'INDIA', 'ES': 'SPAIN', 'KR': 'KOREA',
         'NL': 'NETHERLANDS', 'AR': 'ARGENTINA', 'IE': 'IRELAND',
         'NG': 'NIGERIA', 'ID': 'INDONESIA', 'PL': 'POLAND', 'SE': 'SWEDEN', 'NO': 'NORWAY', 'GR': 'GREECE', 'CH': 'SWITZERLAND',
         'CO': 'COLOMBIA', 'PH': 'PHILIPPINES', 'VN': 'VIETNAM', 'TH': 'THAILAND'}

PLAN = {}


def configure(plan):
    global PLAN
    PLAN = plan


# ---------------------------------------------------------------- yardımcılar (Bloop Bonkers motorundan)
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




# ---------------------------------------------------------------- durumlar
# Kural: dostane, sevimli klişeler (yemek, hava, spor, alışkanlık). Siyaset, savaş, sınır, din YOK.
# her ülke: (replik, ruh hali)  ruh hali: happy shock cool calm cry angry love sleepy shiver
SITUATIONS = {
    'snow': dict(title='COUNTRIES WHEN IT SNOWS', scene='snow', name='Snow', lines={
        'CA': ('Finally! Shorts weather.', 'cool'), 'BR': ('WHAT IS THIS?!', 'shiver'),
        'US': ('School is cancelled!', 'happy'), 'TR': ('Tea time, then.', 'calm'),
        'JP': ('So beautiful...', 'love'), 'MX': ('I am freezing!', 'shiver'),
        'DE': ('Trains still on time.', 'cool'), 'IN': ('My first snow!', 'shock'),
        'IT': ('Pasta will warm me.', 'happy'), 'GB': ('Bit chilly, innit.', 'calm'),
        'ES': ('Back to bed.', 'sleepy'), 'NL': ('Still biking.', 'cool')}),
    'heat': dict(title='COUNTRIES WHEN IT IS 35°C', scene='sun', name='Heatwave', lines={
        'CA': ('I am melting!', 'cry'), 'BR': ('Perfect beach day!', 'cool'),
        'GB': ('Hottest day ever!', 'shock'), 'IN': ('This is winter.', 'cool'),
        'ES': ('Siesta time.', 'sleepy'), 'DE': ('Where is the AC?!', 'angry'),
        'TR': ('Ice cream, please!', 'happy'), 'JP': ('Cold noodles time.', 'happy'),
        'MX': ('Add more chili.', 'cool'), 'US': ('AC on max!', 'happy'),
        'IT': ('Gelato for everyone!', 'love'), 'NL': ('Beach! Oh, rain.', 'cry')}),
    'breakfast': dict(title='COUNTRIES AT BREAKFAST', scene='kitchen', name='Breakfast', lines={
        'GB': ('Full English, please.', 'happy'), 'FR': ('Croissant and coffee.', 'love'),
        'US': ('Pancakes! Ten of them!', 'happy'), 'TR': ('Breakfast takes 3 hours.', 'love'),
        'JP': ('Rice, fish and miso.', 'calm'), 'DE': ('Bread. Lots of bread.', 'cool'),
        'IT': ('Just an espresso.', 'cool'), 'MX': ('Chilaquiles!', 'happy'),
        'IN': ('Chai and paratha!', 'happy'), 'NL': ('Sprinkles on bread!', 'love'),
        'BR': ('Cheese bread!', 'happy'), 'ES': ('Churros!', 'love')}),
    'football': dict(title='COUNTRIES DURING A FOOTBALL FINAL', scene='stadium', name='Football Final', lines={
        'BR': ('Samba time!', 'happy'), 'AR': ('Vamos! Vamos!', 'happy'),
        'DE': ('Efficiency wins.', 'cool'), 'GB': ("It's coming home!", 'love'),
        'US': ("It's called soccer.", 'calm'), 'IT': ('Defense is an art.', 'cool'),
        'ES': ('Tiki-taka!', 'happy'), 'FR': ('Allez les Bleus!', 'happy'),
        'JP': ('We clean the stadium after.', 'calm'), 'KR': ('Fighting!', 'angry'),
        'TR': ('Everyone outside! GOAL!', 'shock'), 'NL': ('Orange everywhere!', 'love'),
        'MX': ('Mexico! Mexico!', 'happy')}),
    'guests': dict(title='COUNTRIES WHEN GUESTS COME OVER', scene='living', name='Guests', lines={
        'TR': ('Eat! Eat more! Tea?', 'love'), 'IT': ('Mamma made pasta for 20.', 'happy'),
        'JP': ('Please take off your shoes.', 'calm'), 'DE': ('You are 2 minutes late.', 'angry'),
        'GB': ('Fancy a cuppa?', 'calm'), 'US': ('Make yourself at home!', 'happy'),
        'MX': ('Mi casa es su casa!', 'love'), 'IN': ('You will not leave hungry.', 'love'),
        'ES': ('Dinner at 10 PM.', 'cool'), 'FR': ('Wine? Cheese? Both.', 'cool'),
        'BR': ('Barbecue party!', 'happy'), 'KR': ('Shoes off, kimchi on!', 'happy')}),
    'newyear': dict(title="COUNTRIES ON NEW YEAR'S EVE", scene='night', name="New Year's Eve", lines={
        'JP': ('Bells and soba.', 'calm'), 'ES': ('Twelve grapes!', 'happy'),
        'BR': ('White clothes, beach!', 'happy'), 'US': ('Ball drop!', 'shock'),
        'GB': ('Big Ben countdown!', 'happy'), 'DE': ('Fireworks! MORE fireworks!', 'shock'),
        'TR': ('Pomegranate and family.', 'love'), 'IT': ('Red socks for luck!', 'happy'),
        'MX': ('Twelve wishes!', 'love'), 'KR': ('Everyone is one year older!', 'shock'),
        'NL': ('Oliebollen!', 'happy'), 'FR': ('Champagne!', 'cool')}),
    'rain': dict(title='COUNTRIES ON A RAINY DAY', scene='rain', name='Rainy Day', lines={
        'GB': ('Just normal weather.', 'calm'), 'IN': ('Monsoon party!', 'happy'),
        'NL': ('Still cycling.', 'cool'), 'BR': ('Rain? Still beach.', 'cool'),
        'JP': ('Umbrella ready.', 'calm'), 'ES': ('Rain? Stay home.', 'sleepy'),
        'DE': ('Raincoat, of course.', 'cool'), 'US': ('Rain delay!', 'cry'),
        'CA': ('Rain or snow, same.', 'calm'), 'TR': ('Tea time again.', 'love')}),
    'monday': dict(title='COUNTRIES ON MONDAY MORNING', scene='city', name='Monday Morning', lines={
        'DE': ('At work since 7.', 'cool'), 'ES': ('Five more minutes...', 'sleepy'),
        'US': ('Coffee. BIG coffee.', 'sleepy'), 'BR': ('Still Carnival in my heart.', 'happy'),
        'GB': ('Tea first.', 'calm'), 'FR': ('Café first.', 'calm'),
        'IT': ('Espresso, then talk.', 'angry'), 'TR': ('Tea, then traffic.', 'calm'),
        'KR': ('Hurry! Hurry!', 'shock'), 'MX': ('Café de olla, vamos.', 'happy'),
        'IN': ('Traffic jam again.', 'cry'), 'JP': ('Work, work, work!', 'shock')}),
    'internet': dict(title='COUNTRIES WHEN THE INTERNET GOES DOWN', scene='living', name='No Internet', lines={
        'KR': ('Impossible! We have the fastest!', 'shock'), 'US': ('I cannot live like this!', 'cry'),
        'JP': ('I will read a book.', 'calm'), 'DE': ('Never worked anyway.', 'cool'),
        'TR': ('Finally, a real chat.', 'happy'), 'GB': ("Let's have tea.", 'calm'),
        'IN': ('Restart the router!', 'angry'), 'BR': ('Football outside!', 'happy'),
        'IT': ('Time for a long lunch.', 'love'), 'NL': ('Biking it is.', 'cool'),
        'ES': ('Siesta time.', 'sleepy'), 'FR': ('Philosophy time.', 'cool')}),
    'birthday': dict(title='COUNTRIES AT A BIRTHDAY PARTY', scene='party', name='Birthday Party', lines={
        'MX': ('Piñata time!', 'happy'), 'TR': ('Cake and tea!', 'love'),
        'KR': ('Seaweed soup!', 'happy'), 'IT': ('Tiramisu!', 'love'),
        'US': ('Giant cake!', 'shock'), 'GB': ('Hip hip hooray!', 'happy'),
        'DE': ('Never celebrate early!', 'angry'), 'JP': ('Cake and karaoke!', 'happy'),
        'BR': ('Brigadeiros!', 'love'), 'IN': ('Sweets for everyone!', 'happy'),
        'NL': ('Congrats to everyone!', 'happy'), 'ES': ('Pull the ears!', 'happy')}),
    'sneeze': dict(title='COUNTRIES WHEN SOMEONE SNEEZES', scene='city', name='Sneeze', lines={
        'DE': ('Gesundheit!', 'cool'), 'US': ('Bless you!', 'happy'), 'ES': ('¡Salud!', 'happy'),
        'TR': ('Çok yaşa!', 'love'), 'IT': ('Salute!', 'happy'), 'FR': ('À tes souhaits!', 'calm'),
        'JP': ('...(polite silence)', 'calm'), 'GB': ('Bless you. Sorry.', 'calm'),
        'BR': ('Saúde!', 'happy'), 'MX': ('¡Salud!', 'happy'), 'NL': ('Gezondheid!', 'cool')}),
    'dinner': dict(title='COUNTRIES AT DINNER TIME', scene='kitchen', name='Dinner Time', lines={
        'ES': ('Dinner at 11 PM!', 'cool'), 'DE': ('Dinner at 6 sharp.', 'cool'),
        'IT': ('Pasta, of course.', 'love'), 'JP': ('Itadakimasu!', 'happy'),
        'TR': ('Everyone at the table!', 'love'), 'US': ('Burgers!', 'happy'),
        'IN': ('Curry with family!', 'love'), 'MX': ('Tacos!', 'happy'), 'FR': ('Three courses!', 'cool'),
        'KR': ('Korean barbecue!', 'happy'), 'BR': ('Rice and beans!', 'happy'), 'GB': ('Fish and chips!', 'happy')}),
}

# 2026-10-12: tekrar riskine karşı 14 durum daha (toplam 26)
SITUATIONS.update({
    'traffic': dict(title='COUNTRIES IN A TRAFFIC JAM', scene='city', name='Traffic Jam', lines={
        'IN': ('Honk honk honk!', 'happy'), 'DE': ('Stay in your lane.', 'angry'), 'IT': ('I will make my own lane!', 'angry'),
        'JP': ('Silent and patient.', 'calm'), 'US': ('Bigger truck, no problem.', 'cool'), 'TR': ('Simit seller! Over here!', 'happy'),
        'GB': ('Sorry, after you.', 'calm'), 'BR': ('Music up, windows down!', 'happy'), 'MX': ('Tacos from the car.', 'love'),
        'NL': ('I took the bike.', 'cool'), 'KR': ('Hurry, hurry!', 'shock'), 'FR': ('Croissant break.', 'calm')}),
    'exam': dict(title='COUNTRIES THE NIGHT BEFORE AN EXAM', scene='living', name='Exam Night', lines={
        'KR': ('Studying since 5 AM.', 'shock'), 'IN': ('Chai and books all night!', 'cool'), 'US': ('Who needs sleep?', 'cry'),
        'JP': ('Notes are color coded.', 'calm'), 'BR': ('Tomorrow is a new day.', 'sleepy'), 'DE': ('Plan made weeks ago.', 'cool'),
        'TR': ('Mom made tea. Again.', 'love'), 'IT': ('Pasta for brain power.', 'happy'), 'ES': ('Siesta first.', 'sleepy'),
        'GB': ('Keep calm and revise.', 'calm'), 'FR': ('Philosophy exam? Easy.', 'cool'), 'MX': ('Coffee number five.', 'shock')}),
    'vacation': dict(title='COUNTRIES ON SUMMER VACATION', scene='sun', name='Summer Vacation', lines={
        'DE': ('Towel on the chair at 6 AM.', 'cool'), 'GB': ('Sunburn in ten minutes.', 'cry'), 'US': ('Disney again!', 'happy'),
        'TR': ('Whole family, one car!', 'love'), 'JP': ('Two hundred photos.', 'happy'), 'IT': ('August? Everyone at the beach.', 'cool'),
        'BR': ('Beach every day!', 'happy'), 'IN': ('Family trip! All 30 of us.', 'happy'), 'FR': ('Whole August off.', 'cool'),
        'ES': ('Tourists everywhere!', 'shock'), 'NL': ('Camping with the caravan.', 'happy'), 'CA': ('Lake and canoe.', 'calm')}),
    'coffee': dict(title='COUNTRIES ORDERING COFFEE', scene='kitchen', name='Coffee Order', lines={
        'IT': ('Espresso. Standing up.', 'cool'), 'US': ('Venti iced caramel, extra shot!', 'happy'), 'TR': ('Turkish coffee, read my cup!', 'love'),
        'FR': ('Café crème, s\'il vous plaît.', 'calm'), 'GB': ('Actually, tea please.', 'calm'), 'BR': ('Cafezinho!', 'happy'),
        'JP': ('Canned coffee from a machine.', 'happy'), 'KR': ('Iced Americano. Even in winter.', 'cool'),
        'IN': ('Filter coffee!', 'happy'), 'MX': ('Café de olla!', 'love'), 'ES': ('Café con leche.', 'calm'),
        'DE': ('Filter coffee. Black.', 'cool')}),
    'wedding': dict(title='COUNTRIES AT A WEDDING', scene='party', name='Wedding', lines={
        'IN': ('Three days of dancing!', 'happy'), 'TR': ('Pin money on the bride!', 'love'), 'IT': ('Ten-course dinner!', 'love'),
        'US': ('Open bar!', 'happy'), 'GB': ('Speeches, then tea.', 'calm'), 'MX': ('Mariachi band!', 'happy'),
        'JP': ('Envelope with new bills.', 'calm'), 'DE': ('Start at 2 PM sharp.', 'cool'), 'BR': ('Party until sunrise!', 'happy'),
        'KR': ('Photos with everyone.', 'happy'), 'ES': ('Dinner at midnight!', 'cool'), 'FR': ('Wine, cheese, wine.', 'love')}),
    'battery': dict(title='COUNTRIES WHEN THE PHONE IS AT 1%', scene='living', name='Phone at 1%', lines={
        'US': ('Nooo! My streak!', 'cry'), 'KR': ('Power bank, always.', 'cool'), 'JP': ('Charger in my bag.', 'calm'),
        'IN': ('Borrow a charger from a neighbor!', 'happy'), 'TR': ('Who has a charger?!', 'shock'), 'DE': ('Phone off. Problem solved.', 'cool'),
        'BR': ('Dancing to save battery.', 'happy'), 'GB': ('Brilliant. Just brilliant.', 'calm'), 'IT': ('Call mamma, quick!', 'shock'),
        'MX': ('One more video...', 'sleepy'), 'FR': ('Back to paper maps.', 'calm'), 'ES': ('Siesta for the phone too.', 'sleepy')}),
    'lost': dict(title='COUNTRIES WHEN THEY GET LOST', scene='city', name='Lost', lines={
        'US': ('GPS says turn left. Into a lake.', 'shock'), 'JP': ('Ask a stranger politely.', 'calm'), 'DE': ('I have a paper map.', 'cool'),
        'TR': ('Ask the shop owner, he knows!', 'happy'), 'IT': ('Follow the smell of pasta.', 'love'), 'GB': ('Sorry, which way is north?', 'calm'),
        'BR': ('Lost? Make new friends!', 'happy'), 'IN': ('Everyone gives different directions!', 'shock'), 'FR': ('Not lost. Exploring.', 'cool'),
        'MX': ('Follow the music!', 'happy'), 'KR': ('Subway app, always.', 'cool'), 'NL': ('Follow the bike lane.', 'calm')}),
    'spicy': dict(title='COUNTRIES EATING SPICY FOOD', scene='kitchen', name='Spicy Food', lines={
        'MX': ('Not spicy at all.', 'cool'), 'IN': ('Mild. Very mild.', 'cool'), 'KR': ('Fire noodles! Easy!', 'happy'),
        'GB': ('Pepper is spicy enough.', 'cry'), 'DE': ('Water! WATER!', 'shock'), 'US': ('Hot wings challenge!', 'shock'),
        'TR': ('More chili flakes please.', 'happy'), 'JP': ('Wasabi... too much!', 'cry'), 'IT': ('A little chili oil.', 'calm'),
        'BR': ('Hot sauce on everything!', 'happy'), 'NL': ('Mayo, please.', 'calm'), 'FR': ('Too spicy for my wine.', 'angry')}),
    'momcalls': dict(title='COUNTRIES WHEN MOM CALLS', scene='living', name='Mom Calls', lines={
        'IT': ('Yes mamma, I ate!', 'love'), 'TR': ('Did you wear a jacket?', 'love'), 'IN': ('Video call with all relatives!', 'happy'),
        'MX': ('Sí, mamá. Sí, mamá.', 'calm'), 'US': ('Call you back, mom!', 'cool'), 'KR': ('Did you eat rice?', 'love'),
        'BR': ('Mom! I miss you!', 'love'), 'GB': ('All fine, mum. Weather is bad.', 'calm'), 'DE': ('Scheduled call, 6 PM.', 'cool'),
        'JP': ('I am working hard, mom.', 'calm'), 'ES': ('Two hours later...', 'sleepy'), 'FR': ('Oui, maman.', 'calm')}),
    'gym': dict(title='COUNTRIES AT THE GYM', scene='city', name='Gym', lines={
        'US': ('Protein shake time!', 'happy'), 'BR': ('Leg day, every day!', 'cool'), 'DE': ('Sets, reps, schedule.', 'cool'),
        'IT': ('Gym? Look good first.', 'love'), 'KR': ('Cardio at 6 AM.', 'shock'), 'JP': ('Clean the machine after.', 'calm'),
        'TR': ('Then kebab, of course.', 'happy'), 'GB': ('Gym, then pub.', 'happy'), 'IN': ('Yoga is better.', 'calm'),
        'MX': ('Tacos give energy!', 'happy'), 'NL': ('I biked here. Done.', 'cool'), 'FR': ('Sport? Non.', 'sleepy')}),
    'queue': dict(title='COUNTRIES WAITING IN LINE', scene='city', name='Waiting in Line', lines={
        'GB': ('Perfect queue. Lovely.', 'love'), 'JP': ('Line for the new bakery.', 'calm'), 'DE': ('Take a number.', 'cool'),
        'IT': ('What line?', 'happy'), 'IN': ('Line? Everyone at once!', 'shock'), 'US': ('Is there a drive-thru?', 'cool'),
        'TR': ('My cousin works here!', 'happy'), 'BR': ('Making friends in the line.', 'happy'), 'KR': ('Online booking. No line.', 'cool'),
        'FR': ('Complaining while waiting.', 'angry'), 'ES': ('Line for churros!', 'love'), 'MX': ('Line for tacos!', 'love')}),
    'payday': dict(title='COUNTRIES ON PAYDAY', scene='city', name='Payday', lines={
        'US': ('Online shopping cart, full!', 'happy'), 'DE': ('Straight to savings.', 'cool'), 'IT': ('New shoes!', 'love'),
        'TR': ('Bills, bills, bills.', 'cry'), 'JP': ('Save for next month.', 'calm'), 'BR': ('Barbecue for everyone!', 'happy'),
        'IN': ('Gold for mom!', 'love'), 'GB': ('Pub round on me!', 'happy'), 'KR': ('Chicken and beer night!', 'happy'),
        'MX': ('Taco party!', 'happy'), 'ES': ('Tapas night!', 'happy'), 'FR': ('Fancy dinner.', 'cool')}),
    'tea': dict(title='COUNTRIES WHEN SOMEONE OFFERS TEA', scene='kitchen', name='Tea Time', lines={
        'GB': ('Milk first? NEVER.', 'angry'), 'TR': ('Tenth glass, please!', 'love'), 'IN': ('Masala chai!', 'happy'),
        'JP': ('Matcha ceremony.', 'calm'), 'US': ('Iced and sweet, please.', 'happy'), 'KR': ('Barley tea!', 'happy'),
        'DE': ('Herbal tea. For health.', 'cool'), 'IT': ('Tea? I want espresso.', 'shock'), 'MX': ('Hot chocolate instead.', 'love'),
        'BR': ('Mate? Let us share!', 'happy'), 'FR': ('Tea... how British.', 'cool'), 'NL': ('Tea and a cookie.', 'calm')}),
    'halloween': dict(title='COUNTRIES ON HALLOWEEN', scene='night', name='Halloween', lines={
        'US': ('Candy! All the candy!', 'happy'), 'MX': ('Day of the Dead is coming!', 'love'), 'GB': ('Pumpkin carving!', 'happy'),
        'JP': ('Best costume parade!', 'happy'), 'DE': ('Too loud.', 'angry'), 'TR': ('What is this holiday?', 'shock'),
        'IE': ('We invented it!', 'cool'), 'CA': ('Trick or treat in the snow.', 'shiver'), 'KR': ('Costume party!', 'happy'),
        'IT': ('Pasta in a pumpkin!', 'love'), 'BR': ('Party, of course!', 'happy'), 'IN': ('Sweets? I have Diwali!', 'happy')}),
})

# 2026-10-13: kullanıcı "tekrar olmasın, oyuncuları ve replikleri artır" → 8 yeni ülke, 26 durumun hepsinde (208 replik).
# Kural aynı: dostane klişe, siyaset/din/gerçek kişi YOK.
_NEW = {
    'snow': {'SE': ('Lagom snow. Just right.', 'calm'), 'NO': ('Born with skis on!', 'cool'), 'PL': ('Soup weather!', 'happy'),
             'CH': ('Ski lift, please.', 'cool'), 'NG': ('Snow?! Never seen it!', 'shock'), 'ID': ('Is this ice cream?', 'shock'),
             'GR': ('Snow? In Greece?!', 'shiver'), 'CO': ('So cold! Hot chocolate!', 'shiver')},
    'heat': {'NG': ('Normal Tuesday.', 'cool'), 'ID': ('Still humid. Always humid.', 'calm'), 'GR': ('Beach and souvlaki!', 'happy'),
             'SE': ('Everyone to the lake!', 'happy'), 'NO': ('Finally, 25 degrees!', 'love'), 'CH': ('Swim in the lake!', 'happy'),
             'PL': ('Ice cream and lemonade!', 'happy'), 'CO': ('Perfect weather, as always.', 'cool')},
    'breakfast': {'SE': ('Crispbread and cheese.', 'calm'), 'NO': ('Brown cheese on bread!', 'love'), 'PL': ('Scrambled eggs, extra butter.', 'happy'),
                  'CH': ('Muesli, of course.', 'cool'), 'NG': ('Akara and pap!', 'happy'), 'ID': ('Nasi goreng!', 'love'),
                  'GR': ('Yogurt with honey.', 'love'), 'CO': ('Arepa and hot chocolate!', 'happy')},
    'football': {'NG': ('Super Eagles! Fly!', 'happy'), 'CO': ('Goal! Dance party!', 'happy'), 'GR': ('We won Euro 2004!', 'love'),
                 'PL': ('Kick it harder!', 'angry'), 'SE': ('Calm... GOAL! Okay.', 'shock'), 'NO': ('Ski season is better.', 'cool'),
                 'CH': ('Neutral. Both teams win.', 'calm'), 'ID': ('Badminton is better!', 'cool')},
    'guests': {'GR': ('Eat! You look thin!', 'love'), 'NG': ('Jollof for everyone!', 'happy'), 'ID': ('Shoes off, please!', 'calm'),
               'PL': ('Have some more soup!', 'love'), 'SE': ('Fika time! Coffee and buns.', 'happy'), 'NO': ('Coffee? Always coffee.', 'calm'),
               'CO': ('My house is your house!', 'love'), 'CH': ('Fondue for everyone!', 'happy')},
    'newyear': {'GR': ('Cake with a hidden coin!', 'happy'), 'CO': ('Run around the block with a suitcase!', 'happy'),
                'PL': ('Dance till morning!', 'happy'), 'SE': ('Fireworks over the water!', 'love'), 'NO': ('Fireworks in the snow!', 'shiver'),
                'CH': ('Midnight, exactly on time.', 'cool'), 'NG': ('Party till sunrise!', 'happy'), 'ID': ('Fireworks and satay!', 'love')},
    'rain': {'NO': ('Rain? Just weather.', 'cool'), 'SE': ('No bad weather, only bad clothes.', 'calm'), 'NG': ('Rainy season again!', 'calm'),
             'ID': ('Monsoon mode on.', 'cool'), 'GR': ('Rain? So rare!', 'shock'), 'PL': ('Stay home, eat soup.', 'sleepy'),
             'CH': ('Even the rain is on time.', 'calm'), 'CO': ('Afternoon rain, every day.', 'calm')},
    'monday': {'SE': ('Fika at 10. Good.', 'calm'), 'CH': ('Train at 7:03. Exactly.', 'cool'), 'NO': ('Hiking after work.', 'happy'),
               'PL': ('Coffee. Lots of coffee.', 'sleepy'), 'NG': ('Traffic first, then work.', 'angry'), 'GR': ('Monday? Slowly, slowly.', 'sleepy'),
               'CO': ('Little black coffee first!', 'happy'), 'ID': ('Motorbike to work!', 'cool')},
    'internet': {'SE': ('We have fast fiber.', 'cool'), 'NO': ('Time for a hike!', 'happy'), 'CH': ('Read a book.', 'calm'),
                 'GR': ('Back to the taverna!', 'happy'), 'PL': ('Board game time!', 'happy'), 'NG': ('Generator on!', 'cool'),
                 'ID': ('Hotspot from my phone!', 'cool'), 'CO': ('Let us dance instead!', 'happy')},
    'birthday': {'SE': ('Green princess cake!', 'love'), 'NO': ('Sing the birthday song!', 'happy'), 'PL': ('Sto lat! Sto lat!', 'happy'),
                 'GR': ('Name day is bigger!', 'cool'), 'NG': ('Jollof party!', 'happy'), 'ID': ('Nasi tumpeng!', 'love'),
                 'CO': ('Dance until midnight!', 'happy'), 'CH': ('Swiss chocolate cake!', 'love')},
    'sneeze': {'SE': ('Prosit!', 'calm'), 'NO': ('Prosit!', 'calm'), 'PL': ('Na zdrowie!', 'happy'), 'GR': ('Gia sou!', 'happy'),
               'NG': ('Bless you!', 'happy'), 'ID': ('Bless you, friend!', 'love'), 'CO': ('Salud!', 'happy'), 'CH': ('Gesundheit!', 'calm')},
    'dinner': {'SE': ('Meatballs, of course.', 'happy'), 'NO': ('Salmon tonight.', 'love'), 'PL': ('Pierogi!', 'love'),
               'GR': ('Moussaka at 10 PM!', 'happy'), 'NG': ('Jollof rice!', 'love'), 'ID': ('Rice with everything.', 'calm'),
               'CO': ('Bandeja paisa!', 'happy'), 'CH': ('Fondue again!', 'love')},
    'traffic': {'NG': ('Danfo bus, let us go!', 'cool'), 'ID': ('Motorbikes everywhere!', 'shock'), 'GR': ('Honk once, smile twice.', 'happy'),
                'CO': ('Not my driving day!', 'cool'), 'SE': ('Calm and in line.', 'calm'), 'NO': ('Electric car, quiet jam.', 'calm'),
                'CH': ('The train was faster.', 'cool'), 'PL': ('Roadworks again!', 'angry')},
    'exam': {'PL': ('Coffee and flashcards!', 'sleepy'), 'SE': ('Study group fika!', 'happy'), 'NO': ('Study, then sauna.', 'calm'),
             'GR': ('Study by the sea.', 'cool'), 'NG': ('Read till sunrise!', 'angry'), 'ID': ('Borrow my cousin\'s notes!', 'happy'),
             'CO': ('Study with music!', 'happy'), 'CH': ('Precise schedule. Done.', 'cool')},
    'vacation': {'SE': ('Summer house by the lake!', 'love'), 'NO': ('Cabin in the mountains!', 'love'), 'PL': ('Baltic Sea, here we go!', 'happy'),
                 'GR': ('We are the vacation.', 'cool'), 'NG': ('Visit grandma\'s village!', 'love'), 'ID': ('Bali is home!', 'cool'),
                 'CO': ('Caribbean coast!', 'happy'), 'CH': ('Hiking the Alps!', 'happy')},
    'coffee': {'SE': ('Fika! Coffee and a cinnamon bun.', 'love'), 'NO': ('Black. Very black.', 'cool'), 'CO': ('Our coffee is the best!', 'love'),
               'GR': ('Frappe, please!', 'happy'), 'PL': ('Coffee with cake.', 'happy'), 'ID': ('Kopi tubruk!', 'happy'),
               'NG': ('Tea, actually.', 'calm'), 'CH': ('Espresso, on time.', 'cool')},
    'wedding': {'GR': ('Smash the plates!', 'happy'), 'NG': ('Spray money on the dancers!', 'happy'), 'ID': ('Two thousand guests!', 'shock'),
                'PL': ('A two day party!', 'happy'), 'SE': ('Speeches. Many speeches.', 'sleepy'), 'NO': ('A tower of ring cakes!', 'love'),
                'CO': ('Dance till 6 AM!', 'happy'), 'CH': ('A very punctual party.', 'cool')},
    'battery': {'NG': ('Power bank, always ready!', 'cool'), 'ID': ('Charge it at the food stall!', 'happy'), 'SE': ('Fully charged. Planned.', 'cool'),
                'NO': ('Phone? I am hiking.', 'calm'), 'CH': ('Still 90 percent. Swiss.', 'cool'), 'PL': ('Find a socket!', 'shock'),
                'GR': ('Charge it at the cafe!', 'calm'), 'CO': ('One percent, one last song!', 'happy')},
    'lost': {'SE': ('Ask nicely. Very nicely.', 'calm'), 'NO': ('Follow the trail signs.', 'cool'), 'CH': ('Swiss map. Never lost.', 'cool'),
             'PL': ('Call grandma.', 'happy'), 'GR': ('Follow the smell of souvlaki.', 'love'), 'NG': ('Ask the bus conductor!', 'happy'),
             'ID': ('Ask the bike taxi driver!', 'happy'), 'CO': ('Ask anyone, they will walk you there!', 'love')},
    'spicy': {'NG': ('Pepper soup! Not hot.', 'cool'), 'ID': ('Sambal on everything!', 'love'), 'SE': ('Black pepper is spicy.', 'shock'),
              'NO': ('Ketchup is spicy, right?', 'shock'), 'PL': ('Horseradish counts!', 'cool'), 'GR': ('A little chili oil.', 'calm'),
              'CO': ('Hot sauce on the side.', 'cool'), 'CH': ('Mustard. Enough.', 'calm')},
    'momcalls': {'GR': ('Did you eat?!', 'shock'), 'PL': ('Come for Sunday dinner!', 'love'), 'NG': ('Call your aunty!', 'angry'),
                 'ID': ('When are you getting married?', 'shock'), 'CO': ('My son, are you okay?', 'love'), 'SE': ('Hej mamma!', 'happy'),
                 'NO': ('I am on a hike, Mom.', 'calm'), 'CH': ('She called at exactly six.', 'cool')},
    'gym': {'SE': ('Gym, then sauna.', 'calm'), 'NO': ('Mountains are my gym.', 'cool'), 'PL': ('Leg day every day!', 'angry'),
            'GR': ('Training like the ancient Olympians!', 'cool'), 'NG': ('Football is my cardio!', 'happy'), 'ID': ('Badminton workout!', 'happy'),
            'CO': ('Dance class counts!', 'happy'), 'CH': ('Hiking counts too.', 'calm')},
    'queue': {'CH': ('Perfect order.', 'cool'), 'SE': ('Take a number. Wait.', 'calm'), 'NO': ('Quiet line. Very quiet.', 'calm'),
              'PL': ('The line is the party.', 'happy'), 'GR': ('Line? Everyone, come in!', 'happy'), 'NG': ('Who is next? Me!', 'cool'),
              'ID': ('Polite line, big smiles.', 'happy'), 'CO': ('Chat with everyone in line!', 'love')},
    'payday': {'SE': ('Save it. Lagom.', 'calm'), 'NO': ('Save it for the cabin.', 'calm'), 'CH': ('Straight into the bank.', 'cool'),
               'PL': ('Big grocery haul!', 'happy'), 'GR': ('Taverna tonight!', 'happy'), 'NG': ('Owambe party!', 'happy'),
               'ID': ('Mall time!', 'love'), 'CO': ('Arepas for everyone!', 'happy')},
    'tea': {'NG': ('Tea with lots of milk!', 'happy'), 'ID': ('Sweet jasmine tea!', 'love'), 'SE': ('Coffee, please.', 'calm'),
            'NO': ('Coffee, actually.', 'calm'), 'PL': ('Tea with lemon!', 'happy'), 'GR': ('Mountain tea!', 'love'),
            'CO': ('Sugar cane drink!', 'happy'), 'CH': ('Herbal tea, of course.', 'calm')},
    'halloween': {'SE': ('We dress up at Easter!', 'cool'), 'NO': ('Trick or treat in the snow!', 'shiver'), 'PL': ('Candles for the ancestors.', 'calm'),
                  'GR': ('Halloween? Tell me more!', 'shock'), 'NG': ('Costume party!', 'happy'), 'ID': ('Spooky stories night!', 'shock'),
                  'CO': ('Kids go trick or treating!', 'happy'), 'CH': ('Pumpkin soup!', 'love')},
}
for _k, _v in _NEW.items():
    SITUATIONS[_k]['lines'].update(_v)

# 2026-10-14: Bloop izleyicisinin %53'ü GD Asya (ID/PH/VN/TH/MY) → Filipinler, Vietnam, Tayland (26 durumun hepsi).
_NEW2 = {
    'snow': {'PH': ('Snow? Only in movies!', 'shock'), 'VN': ('Snow in Sa Pa! Wow!', 'shock'), 'TH': ('Snow? Never in Bangkok!', 'shock')},
    'heat': {'PH': ('Halo-halo time!', 'happy'), 'VN': ('Iced coffee, please!', 'cool'), 'TH': ('Mango sticky rice time!', 'happy')},
    'breakfast': {'PH': ('Garlic rice and eggs!', 'love'), 'VN': ('Pho for breakfast!', 'love'), 'TH': ('Rice soup, please.', 'calm')},
    'football': {'PH': ('Basketball is life!', 'cool'), 'VN': ('Motorbike parade after the win!', 'happy'), 'TH': ('Muay Thai is better!', 'cool')},
    'guests': {'PH': ('Eat first! Come, eat!', 'love'), 'VN': ('Have some tea and fruit!', 'love'), 'TH': ('Smile and greet them!', 'love')},
    'newyear': {'PH': ('Round fruits for good luck!', 'happy'), 'VN': ('Lunar New Year is the big one!', 'cool'), 'TH': ('Water fight in April!', 'happy')},
    'rain': {'PH': ('Typhoon? We are used to it.', 'cool'), 'VN': ('Raincoat on the motorbike!', 'cool'), 'TH': ('Rainy season. Normal.', 'calm')},
    'monday': {'PH': ('Jeepney to work!', 'cool'), 'VN': ('Iced coffee and go!', 'cool'), 'TH': ('Tuk-tuk to work!', 'cool')},
    'internet': {'PH': ('Karaoke instead!', 'happy'), 'VN': ('Find a cafe with wifi!', 'happy'), 'TH': ('Street market time!', 'happy')},
    'birthday': {'PH': ('Noodles for a long life!', 'love'), 'VN': ('Sing and eat cake!', 'happy'), 'TH': ('Cake and karaoke!', 'happy')},
    'sneeze': {'PH': ('Bless you!', 'happy'), 'VN': ('Bless you!', 'calm'), 'TH': ('Bless you!', 'calm')},
    'dinner': {'PH': ('Rice with everything!', 'happy'), 'VN': ('Rice and fish sauce!', 'love'), 'TH': ('Pad Thai!', 'love')},
    'traffic': {'PH': ('Traffic again... nap time.', 'sleepy'), 'VN': ('A sea of motorbikes!', 'shock'), 'TH': ('Bangkok traffic. Patience.', 'sleepy')},
    'exam': {'PH': ('Group study with snacks!', 'happy'), 'VN': ('Study all night!', 'sleepy'), 'TH': ('Study at the cafe.', 'calm')},
    'vacation': {'PH': ('Island hopping!', 'love'), 'VN': ('Ha Long Bay!', 'love'), 'TH': ('Beach in Phuket!', 'love')},
    'coffee': {'PH': ('Strong barako coffee!', 'cool'), 'VN': ('Egg coffee!', 'love'), 'TH': ('Thai iced tea!', 'love')},
    'wedding': {'PH': ('The money dance!', 'happy'), 'VN': ('Hundreds of guests!', 'happy'), 'TH': ('Pour water on our hands!', 'love')},
    'battery': {'PH': ('Power bank in the bag!', 'cool'), 'VN': ('Charge it at the cafe!', 'calm'), 'TH': ('Charger at the corner shop!', 'calm')},
    'lost': {'PH': ('Ask the tricycle driver!', 'happy'), 'VN': ('Ask the street food lady!', 'happy'), 'TH': ('Ask with a big smile!', 'happy')},
    'spicy': {'PH': ('Sweet spaghetti, please!', 'love'), 'VN': ('Fresh chili, please!', 'cool'), 'TH': ('Thai spicy? So brave!', 'cool')},
    'momcalls': {'PH': ('Did you eat already?', 'love'), 'VN': ('Come home for the New Year!', 'love'), 'TH': ('Did you eat rice?', 'love')},
    'gym': {'PH': ('Basketball counts!', 'happy'), 'VN': ('Morning exercise in the park!', 'happy'), 'TH': ('Muay Thai training!', 'angry')},
    'queue': {'PH': ('Polite line, with snacks.', 'calm'), 'VN': ('Fast! Motorbike speed!', 'cool'), 'TH': ('Calm line, big smiles.', 'calm')},
    'payday': {'PH': ('Family dinner out!', 'happy'), 'VN': ('Street food feast!', 'happy'), 'TH': ('Night market shopping!', 'happy')},
    'tea': {'PH': ('Ginger tea!', 'calm'), 'VN': ('Green tea, always!', 'calm'), 'TH': ('Thai milk tea!', 'love')},
    'halloween': {'PH': ('Visit family and light candles.', 'calm'), 'VN': ('Mid-Autumn is our festival!', 'cool'), 'TH': ('Ghost movies all night!', 'shock')},
}
for _k, _v in _NEW2.items():
    SITUATIONS[_k]['lines'].update(_v)


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

rng = np.random.default_rng(1)
def t_arr(d): return np.arange(int(SR * d)) / SR
def noise(d): return rng.uniform(-1, 1, int(SR * d))
def dec(d, k): return np.exp(-t_arr(d) * k)
def lpf(x, k): return np.convolve(x, np.ones(k) / k, mode='same') if k > 1 else x
def bell(d, p=1.0): return np.sin(np.linspace(0, np.pi, int(SR * d))) ** p
def osc(freq, shape='sine'):
    ph = 2 * np.pi * np.cumsum(freq) / SR
    if shape == 'saw': return 2 * ((ph / (2 * np.pi)) % 1) - 1
    return np.sin(ph)
def sweep(f0, f1, d, shape='sine'): return osc(np.geomspace(f0, f1, int(SR * d)), shape)


def sfx(name, dur=None):
    if name == 'pop': x, g = sweep(900, 240, 0.09) * dec(0.09, 35), 0.6
    elif name == 'crunch':
        n = noise(0.18); m = (rng.uniform(0, 1, len(n) // 220 + 1) > 0.45).repeat(220)[:len(n)]
        x, g = lpf(n, 2) * m * dec(0.18, 14), 0.55
    elif name == 'gulp': x, g = sweep(420, 140, 0.16) * bell(0.16), 0.7
    elif name == 'burp':
        s = sweep(95, 70, 0.7, 'saw') * (1 + 0.5 * noise(0.7)); x, g = lpf(s, 18) * bell(0.7, 0.5), 1.0
    elif name == 'ring':
        tt = t_arr(dur); x = (np.sin(2 * np.pi * 1750 * tt) + 0.6 * np.sin(2 * np.pi * 2630 * tt)) * (np.sin(2 * np.pi * 22 * tt) > 0); g = 0.22
    elif name == 'ring_weak':
        x = osc(np.linspace(1500, 1000, int(SR * 0.3))) * (np.sin(2 * np.pi * 18 * t_arr(0.3)) > 0) * dec(0.3, 5); g = 0.12
    elif name == 'click': x, g = np.diff(noise(0.02), prepend=0) * dec(0.02, 200), 0.5
    elif name in ('smash', 'bonk'):
        d = 0.6 if name == 'smash' else 0.35
        th = sweep(110 if name == 'smash' else 160, 40, d) * dec(d, 6)
        nz = lpf(noise(d), 3) * dec(d, 9)
        cl = sum(np.sin(2 * np.pi * f * t_arr(d)) * dec(d, k) for f, k in ((523, 7), (787, 9), (1187, 11)))
        x, g = th + 0.7 * nz + 0.25 * cl, 1.0 if name == 'smash' else 0.85
    elif name in ('whoosh', 'whoosh_s'):
        d = 0.4 if name == 'whoosh' else 0.22; x = lpf(noise(d), 10) * bell(d, 2); g = 0.6 if name == 'whoosh' else 0.3
    elif name == 'squirt': x, g = lpf(noise(0.2), 5) * dec(0.2, 10) + 0.3 * sweep(700, 250, 0.2) * dec(0.2, 15), 0.5
    elif name == 'slurp':
        tt = t_arr(dur); n = lpf(noise(dur), 6) * (0.6 + 0.4 * np.sin(2 * np.pi * 8 * tt))
        s = osc(220 + 70 * np.sin(2 * np.pi * 6 * tt)); x, g = (n * 1.5 + 0.35 * s) * bell(dur, 0.3), 0.55
    elif name == 'ahh':
        tt = t_arr(0.8); f = 170 * (1 - 0.15 * tt / 0.8) + 4 * np.sin(2 * np.pi * 5.5 * tt)
        x, g = lpf(osc(f, 'saw'), 9) * bell(0.8, 0.4), 0.7
    elif name == 'inhale': x, g = lpf(noise(dur), 4) * np.linspace(0, 1, int(SR * dur)) ** 2, 0.6
    elif name == 'blow': x, g = lpf(noise(dur), 12) * bell(dur, 0.5), 0.8
    elif name == 'splat': x, g = sweep(80, 40, 0.5) * dec(0.5, 8) + 3 * lpf(noise(0.5), 20) * dec(0.5, 10), 1.0
    elif name == 'horn':
        tt = t_arr(0.55); x, g = lpf(osc(520 + 30 * np.sin(2 * np.pi * 6 * tt), 'saw'), 5) * bell(0.55, 0.3), 0.3
    elif name == 'clap': x, g = np.diff(noise(0.08), prepend=0) * dec(0.08, 60), 0.45
    elif name == 'sting':
        x = lpf(osc(np.full(int(SR * 0.9), 110.0), 'saw') + osc(np.full(int(SR * 0.9), 55.6), 'saw'), 6) * dec(0.9, 3.5)
        x += 0.5 * np.sin(2 * np.pi * 55 * t_arr(0.9)) * dec(0.9, 3); g = 0.55
    elif name == 'ding':
        x = np.sin(2 * np.pi * 1320 * t_arr(0.9)) * dec(0.9, 5) + 0.4 * np.sin(2 * np.pi * 2640 * t_arr(0.9)) * dec(0.9, 8); g = 0.35
    elif name == 'boing':
        tt = t_arr(0.5); x, g = osc(180 + 300 * tt + 40 * np.sin(2 * np.pi * 18 * tt)) * dec(0.5, 5), 0.4
    elif name == 'yawn':
        tt = t_arr(0.9); f = np.linspace(330, 190, len(tt)) + 6 * np.sin(2 * np.pi * 5 * tt)
        x, g = (osc(f) + 0.3 * lpf(noise(0.9), 8)) * bell(0.9, 0.6), 0.3
    elif name == 'psst': x, g = np.diff(noise(0.25), prepend=0) * dec(0.25, 9), 0.4
    elif name == 'fizz': x, g = np.diff(noise(dur), prepend=0) * (rng.uniform(0, 1, int(SR * dur)) > 0.6) * dec(dur, 1.5), 0.45
    elif name == 'rattle':
        tt = t_arr(dur); x, g = lpf(noise(dur), 3) * (np.sin(2 * np.pi * 15 * tt) > 0.3), 0.45
    elif name == 'lick': x, g = lpf(noise(0.14), 4) * bell(0.14) + 0.4 * sweep(300, 700, 0.14) * bell(0.14), 0.45
    elif name == 'freeze':
        tt = t_arr(1.2); x = sum(np.sin(2 * np.pi * f * (1 - 0.25 * tt / 1.2) * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * (9 + j) * tt))
                                for j, f in enumerate((2100, 2650, 3150, 3700))) * dec(1.2, 2); g = 0.3
    elif name == 'bang': x, g = sweep(150, 40, 0.4) * dec(0.4, 8) + lpf(noise(0.4), 2) * dec(0.4, 14), 1.0
    elif name == 'carve':
        tt = t_arr(0.28); x, g = lpf(noise(0.28), 3) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * tt)) * bell(0.28), 0.4
    else: raise ValueError(name)
    return x / (np.abs(x).max() + 1e-9) * g


def music(dur, seed):
    rnd = random.Random(seed)
    bpm = rnd.choice([116, 120, 124, 128, 132]); beat = 60 / bpm; key = rnd.randint(-3, 3)
    out = np.zeros(int(SR * dur) + SR)
    def mf(m): return 440 * 2 ** ((m + key - 69) / 12)
    def pluck(f, d, k, bright):
        tt = t_arr(d); return (np.sin(2 * np.pi * f * tt) + bright * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * k)
    def add(t0, x):
        i0 = int(t0 * SR); out[i0:i0 + len(x)] += x[:max(0, len(out) - i0)]
    prog = rnd.choice([[48, 45, 41, 43], [48, 43, 45, 41], [45, 41, 48, 43], [48, 41, 43, 48]])
    penta = [60, 62, 64, 67, 69, 72, 74, 76]; bright = rnd.uniform(0.2, 0.5)
    motif = [None if rnd.random() < 0.3 else rnd.choice(penta) for _ in range(16)]
    motif2 = [m if (m is None or rnd.random() < 0.6) else rnd.choice(penta) for m in motif]
    for b in range(int(dur / beat) + 1):
        t0 = b * beat; bar = b // 4; root = prog[bar % 4]
        add(t0, 0.9 * pluck(mf(root if b % 2 == 0 else root + 7), 0.35, 7, 0.35))
        if b % 2 == 0: add(t0, 0.8 * sweep(130, 45, 0.18) * dec(0.18, 18))
        else: add(t0, 0.25 * lpf(noise(0.12), 2) * dec(0.12, 30))
        add(t0 + beat / 2, 0.12 * np.diff(noise(0.03), prepend=0) * dec(0.03, 120))
        mot = motif if (bar // 2) % 2 == 0 else motif2
        for h in (0, 1):
            n = mot[(b * 2 + h) % 16]
            if n is not None: add(t0 + h * beat / 2, 0.32 * pluck(mf(n), 0.25, 11, bright))
    out = out[:int(SR * dur)]
    out *= np.clip((dur - t_arr(dur)) / 0.6, 0, 1)
    return out / np.abs(out).max() * 0.22




# ---------------------------------------------------------------- zaman çizelgesi
STAGE = (540, 1010)
BIG = 500
SLOTS4 = [(170, 1660), (400, 1660), (680, 1660), (910, 1660)]
FINAL4 = [(300, 830), (780, 830), (300, 1330), (780, 1330)]


def total(plan=None):
    return INTRO + TURN * len((plan or PLAN)['countries']) + OUTRO


def turn_pose(k, lt, code, mood):
    """k. ülkenin sahnedeki konumu/ölçüsü (lt: tur içi saniye)."""
    if lt < 0.55:   # sağdan zıplayarak gelir
        u = sm(lt / 0.55)
        x = lerp(1300, STAGE[0], u); y = STAGE[1] - 260 * math.sin(math.pi * u)
        return x, y, BIG, 0.0
    if lt < TURN - 0.6:
        tt = lt - 0.55
        sq = 0.08 * abs(math.sin(tt * 6)) if mood in ('happy', 'love') else 0.0
        jit = 7 * math.sin(lt * 60) if mood == 'shiver' else (5 * math.sin(lt * 45) if mood == 'angry' else 0.0)
        hop = 120 * abs(math.sin(tt * 4.5)) if mood in ('shock', 'happy') and tt < 1.4 else 0.0
        sway = 25 * math.sin(tt * 2) if mood in ('calm', 'sleepy', 'cool') else 0.0
        return STAGE[0] + jit + sway, STAGE[1] - hop, BIG, sq
    u = sm((lt - (TURN - 0.6)) / 0.6)   # sıraya geçer
    sx, sy = SLOTS4[k]
    return lerp(STAGE[0], sx, u), lerp(STAGE[1], sy, u), lerp(BIG, 190, u), 0.0


def title_band(img, txt, t, t0):
    k = back(seg(t, t0, t0 + 0.3))
    f = font(L(84)); lines = wrap(txt, f, L(980))
    for i, ln in enumerate(lines):
        put_text(img, ln, W / 2, 150 + i * 95, 84, (255, 230, 60) if i == len(lines) - 1 else (255, 255, 255), scale=k)


def name_tag(img, name, x, y, k=1.0, size=60):
    put_text(img, name, x, y, size, (255, 255, 255), scale=k)


def render_frame(i):
    T = i / FPS
    sit = SITUATIONS[PLAN['situation']]
    codes = PLAN['countries']; n = len(codes)
    img = scene_bg(sit['scene']).copy()
    effects(img, sit['scene'], T)
    # koyu üst bant (başlık okunsun)
    band = Image.new('RGBA', (L(W), L(330)), (20, 18, 35, 170)); img.alpha_composite(band, (0, 0))
    title_band(img, sit['title'], T, 0.0)
    end = INTRO + TURN * n
    if T < INTRO:
        put_text(img, f'{n} COUNTRIES', W / 2, 900, 110, (255, 255, 255), scale=back(seg(T, 0.35, 0.7)), rot=-4)
        put_text(img, 'WHICH ONE IS YOU?', W / 2, 1040, 80, (255, 230, 60), scale=back(seg(T, 0.6, 0.95)), rot=3)
    elif T < end:
        k = int((T - INTRO) // TURN); lt = T - INTRO - k * TURN
        for j in range(k):   # sıradakiler
            sx, sy = SLOTS4[j]
            ball(img, codes[j], sx, sy, 190, sit['lines'][codes[j]][1], T, look=(0.6 if sx < STAGE[0] else -0.6, -0.5))
        code = codes[k]; line, mood = sit['lines'][code]
        x, y, d, sq = turn_pose(k, lt, code, mood)
        lv = speech_levels(str(PLAN.get('seed')) + PLAN['situation'] + ','.join(codes))
        sq += 0.07 * float(lv[min(len(lv) - 1, i)])   # konuşurken sese göre esner
        ball(img, code, x, y, d, mood if lt >= 0.45 else 'normal', T, sq, look=(0, 0))
        if 0.45 <= lt < TURN - 0.55:
            bubble(img, line, STAGE[0], 690, 0, seg(lt, 0.45, 0.7) * (1 - seg(lt, TURN - 0.75, TURN - 0.55)))
            name_tag(img, NAMES[code], STAGE[0], 1330, back(seg(lt, 0.5, 0.75)), 76)
    else:
        lt = T - end
        for j, code in enumerate(codes):
            sx, sy = SLOTS4[j]; fx, fy = FINAL4[j]
            u = sm(seg(lt, 0.0, 0.6))
            x, y, d = lerp(sx, fx, u), lerp(sy, fy, u), lerp(190, 330, u)
            y -= 40 * abs(math.sin(lt * 5 + j)) * u
            ball(img, code, x, y, d, 'happy', T)
            if u > 0.9: name_tag(img, NAMES[code], x, y + d * 0.68, 1.0, 50)
        s = back(seg(lt, 0.4, 0.75)) * (1 + 0.04 * math.sin(lt * 7))
        put_text(img, 'WHICH ONE IS', W / 2, 1640, 96, (255, 255, 255), scale=s, rot=-3)
        put_text(img, 'YOUR COUNTRY?', W / 2, 1760, 110, (255, 230, 60), scale=s, rot=3)
    return img.convert('RGB').reduce(S)


@lru_cache(2)
def _first_frame(key):
    return render_frame(0)


def render_frame_loop(i):
    """Shorts başa sarar: son 0.45 sn ilk kareye karışır (kesintisiz döngü)."""
    T = i / FPS; tot = total(); f = render_frame(i)
    if T > tot - 0.45:
        f = Image.blend(f, _first_frame(str(PLAN.get('seed'))), seg(T, tot - 0.45, tot))
    return f


def _frame_bytes(i): return render_frame_loop(i).tobytes()


# ---------------------------------------------------------------- ses
@lru_cache(None)
def load_clip(f):
    with wave.open(f) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        sr = w.getframerate()
    if sr != SR:
        x = np.interp(np.arange(0, len(x), sr / SR), np.arange(len(x)), x)
    nz = np.nonzero(np.abs(x) > 0.02)[0]
    return x[max(0, nz[0] - 200):nz[-1] + 800] if len(nz) else None


MOOD_KIND = {'happy': 'yay', 'love': 'yay', 'shock': 'yell', 'shiver': 'yell', 'cry': 'yell', 'angry': 'yell',
             'cool': 'hm', 'calm': 'hm', 'sleepy': 'hm', 'normal': 'hm'}


def exclaim(code, mood, seed):
    """Ülkeye özgü perde + duruma uygun anime ünlemi (kütüphane: voices/zephyr_ex, voices/puck_ex)."""
    lib = 'zephyr_ex' if sum(map(ord, code)) % 2 else 'puck_ex'
    kind = MOOD_KIND.get(mood, 'hm')
    files = sorted(glob.glob(os.path.join(HERE, 'voices', lib, f'{kind}_*.wav'))) or \
        sorted(glob.glob(os.path.join(HERE, 'voices', lib, '*.wav')))
    if not files: return None
    x = load_clip(files[random.Random(f'{seed}{code}').randrange(len(files))])
    if x is None: return None
    r = 0.9 + (sum(map(ord, code)) % 9) * 0.04   # ülke başına perde
    x = np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x)
    return x / (np.abs(x).max() + 1e-9) * 0.7


def line_clip(sit, code):
    """Ülkenin bu durumdaki repliği (kendi aksanıyla): voices/cw/<ÜLKE>/<durum>.wav; yoksa None → anime ünlemi."""
    f = os.path.join(HERE, 'voices', 'cw', code, f'{sit}.wav')
    x = load_clip(f) if os.path.exists(f) else None
    if x is None: return None
    x = x[:int(SR * (TURN - 1.1))]
    return x / (np.abs(x).max() + 1e-9) * 0.85


@lru_cache(4)
def speech_levels(key):
    """Konuşan topun kare başına ses seviyesi (konuşurken zıplar)."""
    sit = PLAN['situation']; nf = int(total() * FPS) + 2; lv = np.zeros(nf); hop = SR // FPS
    for k, code in enumerate(PLAN['countries']):
        x = line_clip(sit, code)
        if x is None: continue
        m = len(x) // hop
        rms = np.sqrt((x[:m * hop].reshape(m, hop) ** 2).mean(axis=1))
        i0 = int((INTRO + k * TURN + 0.5) * FPS); seg_ = lv[i0:i0 + m]; seg_ += rms[:len(seg_)]
    return lv / (lv.max() + 1e-9)


def ambience(kind, dur):
    tt = t_arr(dur)
    if kind == 'rain': return lpf(noise(dur), 2) * 0.12
    if kind == 'snow': return lpf(noise(dur), 40) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * tt)) * 0.18
    if kind == 'stadium': return lpf(noise(dur), 12) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * tt)) * 0.22
    if kind == 'party': return lpf(noise(dur), 20) * 0.06
    return np.zeros(len(tt))


def build_audio(path):
    tot = total(); n = int(SR * tot); mus = music(tot, PLAN['seed'])
    sit = SITUATIONS[PLAN['situation']]
    mix = np.zeros(n); vo = np.zeros(n)
    def place(arr, t0, x):
        if x is None: return
        i0 = int(t0 * SR); arr[i0:i0 + len(x)] += x[:max(0, n - i0)]
    place(mix, 0.0, ambience(sit['scene'], tot))
    for t0 in (0.0, 0.4, 0.7): place(mix, t0, sfx('pop'))
    for k, code in enumerate(PLAN['countries']):
        base = INTRO + k * TURN; mood = sit['lines'][code][1]
        place(mix, base, sfx('whoosh_s')); place(mix, base + 0.5, sfx('boing'))
        ln = line_clip(PLAN['situation'], code)
        place(vo, base + 0.5, ln if ln is not None else exclaim(code, mood, PLAN['seed'] + k))
        place(mix, base + TURN - 0.6, sfx('whoosh_s'))
    end = INTRO + TURN * len(PLAN['countries'])
    place(mix, end, sfx('ding')); place(mix, end + 0.4, sfx('clap')); place(mix, end + 0.55, sfx('clap'))
    env = np.convolve(np.abs(vo), np.ones(int(SR * 0.25)) / int(SR * 0.25), mode='same')
    duck = 1 - 0.6 * np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    mix = mus[:n] * duck + mix + vo
    mix *= np.clip((tot - t_arr(tot)[:n]) / 0.25, 0, 1)
    mix = mix / np.abs(mix).max() * 0.92
    pcm = (np.repeat(mix[:, None], 2, axis=1) * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- video
def render_video(plan, out_dir, workers=None):
    configure(plan)
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, 'audio.wav'); mp4 = os.path.join(out_dir, 'video.mp4')
    build_audio(wav)
    nf = int(total() * FPS)
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium',
           '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=configure, initargs=(plan,)) as pool:
        for i, buf in enumerate(pool.imap(_frame_bytes, range(nf), chunksize=6)):
            p.stdin.write(buf)
            if i % 150 == 0: print(f'  frame {i}/{nf}', flush=True)
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError('ffmpeg failed')
    os.remove(wav)
    return mp4


def _arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


if __name__ == '__main__':
    plan = dict(situation=_arg('--sit', 'snow'), countries=_arg('--countries', 'CA,BR,TR,JP').split(','), seed=1)
    out = os.path.join(HERE, 'output', 'preview')
    if '--preview' in sys.argv:
        configure(plan); os.makedirs(out, exist_ok=True)
        for s in _arg('--preview', '3').split(','):
            render_frame(int(float(s) * FPS)).save(os.path.join(out, f'p_{s}.png'))
        print('preview ok')
    else:
        print(render_video(plan, out))
