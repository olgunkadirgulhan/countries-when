"""Kanal görselleri (motorun kendi topları ve sahnesiyle): banner 2560x1440, profil 800x800, filigran 150x150."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import balls as B
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(B.HERE, 'channel'); os.makedirs(OUT, exist_ok=True)
B.configure(dict(situation='snow', countries=['US'], seed=1))


def ball_img(code, d, mood):
    im = Image.new('RGBA', (B.L(d * 1.3), B.L(d * 1.3)), (0, 0, 0, 0))
    B.ball(im, code, d * 0.65, d * 0.62, d, mood, 0.3)
    im = im.resize((int(d * 1.3), int(d * 1.3)), Image.LANCZOS)
    return im


def text(d, xy, s, size, fill):
    f = ImageFont.truetype(B.FONT, size)
    d.text(xy, s, font=f, fill=fill, anchor='mm', stroke_width=max(3, size // 11), stroke_fill=(28, 22, 40))


bg = B.scene_bg('city').convert('RGB').resize((2560, 4551)).crop((0, 1500, 2560, 2940))
banner = bg.copy(); d = ImageDraw.Draw(banner)
row = [('US', 'happy'), ('BR', 'love'), ('JP', 'calm'), ('TR', 'happy'), ('DE', 'cool'), ('IT', 'love'), ('GB', 'calm'), ('MX', 'happy')]
for i, (c, m) in enumerate(row):
    b = ball_img(c, 150, m); x = 1280 - 4 * 190 + i * 190
    banner.paste(b, (int(x - b.width / 2), 860 - b.height // 2), b)
text(d, (1280, 600), 'COUNTRYBALL CHAOS', 150, (255, 255, 255))
text(d, (1280, 1000), 'WHICH ONE IS YOUR COUNTRY?', 64, (255, 230, 60))
banner.save(os.path.join(OUT, 'banner_2560x1440.png'))
prof = Image.new('RGB', (800, 800), (255, 214, 80)); d = ImageDraw.Draw(prof)
for (c, m, x, y, s) in (('TR', 'happy', 250, 470, 360), ('US', 'love', 560, 470, 360), ('BR', 'cool', 400, 250, 300)):
    b = ball_img(c, s, m); prof.paste(b, (int(x - b.width / 2), int(y - b.height / 2)), b)
prof.save(os.path.join(OUT, 'profile_800.png'))
w = ball_img('US', 120, 'happy').resize((150, 150), Image.LANCZOS); w.save(os.path.join(OUT, 'watermark_150.png'))
banner.resize((1280, 720)).save(os.path.join(B.HERE, 'output', 'banner_preview.png'))
print('ok')
