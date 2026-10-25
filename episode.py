"""Uzun bölüm (yatay 16:9, TV/masaüstü): 10 yeni durum, her biri bu bölüm için ayrı plan (Shorts'ta hiç kullanılmamış
durum + ülke dörtlüsü, hepsi sesli). Dikey sahne ortada, solda durum, sağda ülkelerin replikleri; açıklamada
bölüm zaman damgaları. Yatay video Shorts sayılmaz → izlenme süresi YPP'nin 4.000 saatine yazılır.

  python episode.py [--no-upload]
"""
import json
import os
import random
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import balls as orbit  # noqa: E402
import run  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

OW, OH = 1920, 1080
PARTS = int(os.environ.get('EP_PARTS') or 10)
CARD = 2.5
FF = None
YELLOW, WHITE = (255, 230, 60), (255, 255, 255)


def ff(*args):
    subprocess.run([FF, '-y', '-loglevel', 'error', *args], check=True)


def strip(t):
    return re.sub('[\U0001F000-\U0001FFFF☀-➿‍️]', '', t).strip()


def font(sz):
    return ImageFont.truetype(orbit.FONT, sz)


def text(d, xy, s, sz, fill, anchor='mm', maxw=None):
    f = font(sz)
    lines = [s] if not maxw else orbit.wrap(s, f, maxw)
    lh = sz * 1.15
    y0 = xy[1] - lh * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        d.text((xy[0], y0 + i * lh), ln, font=f, fill=fill, anchor=anchor, stroke_width=max(3, sz // 12), stroke_fill=(20, 16, 34))


def background(kind):
    """Dikey sahne arka planının yıldızlı üst kısmı yatay kadraja (yanlar dolsun)."""
    bg = orbit.scene_bg(kind).convert('RGB')
    w = bg.width; h = int(w * OH / OW)
    return bg.crop((0, 0, w, h)).resize((OW, OH), Image.LANCZOS)


def panel_png(path, k, n, plan):
    s = orbit.SITUATIONS[plan['situation']]
    img = background(s['scene'])
    dark = Image.new('RGBA', (OW, OH), (10, 8, 26, 120)); img = Image.alpha_composite(img.convert('RGBA'), dark)
    d = ImageDraw.Draw(img)
    text(d, (330, 300), f'#{k}', 120, YELLOW)
    text(d, (330, 560), strip(s['title']).replace('PLANETS', 'PLANETS').title(), 54, WHITE, maxw=560)
    text(d, (330, 900), f'{k} / {n}', 40, (190, 190, 230))
    text(d, (OW - 330, 170), 'HOW EACH COUNTRY REACTS', 46, YELLOW)
    for i, c in enumerate(plan['countries']):
        y = 300 + i * 190
        text(d, (OW - 330, y), orbit.NAMES[c], 40, YELLOW)
        text(d, (OW - 330, y + 62), s['lines'][c][0], 34, WHITE, maxw=520)
    img.convert('RGB').save(path)


def card_mp4(path, lines, kind='city', seconds=CARD):
    img = background(kind); d = ImageDraw.Draw(img)
    for s, y, sz, col in lines:
        text(d, (OW // 2, y), s, sz, col, maxw=1600)
    png = str(path) + '.png'; img.save(png)
    ff('-loop', '1', '-i', png, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', str(seconds),
       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', str(orbit.FPS), '-c:a', 'aac', '-ar', '44100', '-ac', '2', '-shortest', str(path))


def part(out, k, n, plan):
    raw = orbit.render_video(plan, str(out / f'raw{k}'))
    pan = out / f'panel{k}.png'; panel_png(pan, k, n, plan)
    dst = out / f'part{k}.mp4'
    ff('-loop', '1', '-i', str(pan), '-i', raw, '-filter_complex',
       f'[1:v]scale=-2:{OH}[v];[0:v][v]overlay=(W-w)/2:0:shortest=1,format=yuv420p[o]',
       '-map', '[o]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-r', str(orbit.FPS),
       '-c:a', 'aac', '-ar', '44100', '-ac', '2', str(dst))
    return dst


def dur(mp4):
    r = subprocess.run([FF, '-i', str(mp4)], capture_output=True, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def stamp(t):
    t = int(t); return f'{t // 60}:{t % 60:02d}'


def main():
    global FF
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
    no_upload = '--no-upload' in sys.argv
    hist = run.load()
    eps = [v for v in hist['videos'] if v.get('kind') == 'episode']
    if eps and not no_upload:
        last = datetime.strptime(eps[-1]['date'], '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last < timedelta(days=1.5):
            print(f'son bölüm {eps[-1]["date"]}: 1,5 gün dolmadı, atlandı'); return
    rnd = random.Random()
    sim = {'videos': list(hist['videos'])}; plans = []
    for _ in range(PARTS * 4):
        if len(plans) == PARTS: break
        p = run.pick_plan(sim, rnd, mode='episode')
        if p is None: break
        sim['videos'].append(dict(kind='episode-part', situation=p['situation'], countries=p['countries']))
        if p['situation'] in {q['situation'] for q in plans}: continue   # bölümde aynı konu iki kez olmasın
        plans.append(p)
    if len(plans) < min(6, PARTS):
        print(f'sesli yeni plan yetmiyor ({len(plans)}) → bölüm atlandı'); return
    n_ep = len(eps) + 1
    out = HERE / 'output' / f'episode-{n_ep}'; out.mkdir(parents=True, exist_ok=True)
    names = [orbit.SITUATIONS[p['situation']]['name'] for p in plans]
    files = []
    intro = out / 'intro.mp4'
    card_mp4(intro, [('COUNTRYBALL CHAOS', 380, 140, WHITE), (f'EPISODE {n_ep}', 560, 90, YELLOW),
                     (f'{len(plans)} SITUATIONS, EVERY COUNTRY REACTS', 720, 56, WHITE)], 'city')
    files.append(intro)
    chapters = [('0:00', 'Intro')]; t = CARD
    for k, p in enumerate(plans, 1):
        orbit.configure(p)
        f = part(out, k, len(plans), p); files.append(f)
        chapters.append((stamp(t), strip(orbit.SITUATIONS[p['situation']]['title']).title()))
        t += dur(f)
        print(f'bölüm parçası {k}/{len(plans)}: {p}', flush=True)
    outro = out / 'outro.mp4'
    card_mp4(outro, [('WHICH ONE IS YOUR COUNTRY?', 420, 100, YELLOW), ('Tell us in the comments!', 600, 64, WHITE),
                     ('New countryball videos every day', 760, 56, WHITE)], 'night', 4.0)
    files.append(outro); chapters.append((stamp(t), 'Which one is your country?'))
    lst = out / 'list.txt'; lst.write_text(''.join(f"file '{f}'\n" for f in files))
    mp4 = out / 'episode.mp4'
    ff('-f', 'concat', '-safe', '0', '-i', str(lst), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
       '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(mp4))
    # kapak: ilk planın son sıralama karesi + başlık
    orbit.configure(plans[0])
    th = orbit.render_frame(int((orbit.total() - 1.0) * orbit.FPS)).resize((608, 1080))
    thumb = background('city'); thumb.paste(th, ((OW - 608) // 2, 0)); d = ImageDraw.Draw(thumb)
    text(d, (330, 420), 'COUNTRIES', 100, WHITE); text(d, (330, 580), 'WHEN...', 130, YELLOW)
    text(d, (OW - 330, 500), f'EPISODE {n_ep}', 90, WHITE)
    thumb = thumb.resize((1280, 720)); thumb.save(out / 'thumb.png')
    title = rnd.choice([f'Countryballs: {len(plans)} Situations, Every Country Reacts 🌍 | Episode {n_ep}',
                        f'Countries When... {", ".join(names[:3])} & More 😂 Countryball Episode {n_ep}',
                        f'Countryball Chaos Episode {n_ep}: How Countries React to {len(plans)} Situations 🌍'])[:100]
    facts = '\n'.join(f'{c[0]} {c[1]}' for c in chapters)
    desc = (f'Countryball Chaos episode {n_ep}: {len(plans)} everyday situations, and every country reacts in its own '
            '(very friendly) way.\n\n' + facts +
            '\n\nWhich one is YOUR country? Comment below 👇\n\n#countryballs #countryball #animation #memes')
    tags = ['countryballs', 'countryball', 'countryballs animation', 'countryball memes', 'countries when',
            'country stereotypes', 'funny countries', 'animation'] + [x.lower() for x in names[:6]]
    (out / 'meta.json').write_text(json.dumps(dict(title=title, description=desc, plans=plans), indent=1, ensure_ascii=False))
    print(f'bölüm hazır: {mp4} ({stamp(dur(mp4))})\n{title}', flush=True)
    if no_upload:
        return
    import upload
    privacy = os.environ.get('YT_PRIVACY') or 'private'
    vid = upload.upload(str(mp4), title, desc, tags, privacy, category='23')
    print(f'yüklendi: https://youtu.be/{vid} ({privacy})', flush=True)
    try:
        upload.set_thumbnail(vid, str(out / 'thumb.png'))
    except Exception as e:  # noqa: BLE001 — kanal doğrulanmamışsa kapak yüklenemez
        print('kapak atlandı:', str(e)[:150])
    pl = json.loads((HERE / 'playlists.json').read_text()) if (HERE / 'playlists.json').exists() else {}
    if pl.get('all'):
        try: upload.add_to_playlist(pl['all'], vid)
        except Exception as e: print('playlist:', e)  # noqa: E701
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    hist['videos'].append(dict(id=vid, date=now, kind='episode', title=title, privacy=privacy, situation='episode', countries=[]))
    for p in plans:   # bölümde kullanılan dörtlüler Shorts'ta tekrar edilmesin
        hist['videos'].append(dict(id=vid, date=now, kind='episode-part', situation=p['situation'], countries=p['countries']))
    run.HISTORY.write_text(json.dumps(hist, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
