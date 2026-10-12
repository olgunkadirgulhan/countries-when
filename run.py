"""Bir Short üret ve yükle: durum + 4 ülke seç (tekrar etmez) -> render -> YouTube -> history.json.

  python run.py --no-upload
"""
import json, os, random, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import balls  # noqa: E402

HISTORY = HERE / 'history.json'
# ABD/İngilizce izleyici: büyük izleyici kitlesi olan ülkeler daha sık
WEIGHT = {'US': 3, 'GB': 2, 'CA': 2, 'IN': 2, 'BR': 2, 'MX': 2, 'DE': 1.5, 'JP': 1.5, 'TR': 1.5, 'FR': 1.2, 'IT': 1.2,
          'ES': 1.2, 'KR': 1.2, 'NL': 1, 'AR': 1}
# 2026-10-12 trend ölçümü: 'countryballs' araması son 30 günde medyan 4.9M izlenme; 'countries when' ifadesi 305 → başlıkta countryballs
TITLES = ['Countryballs: {t} 😂 #countryballs', '{t} 🌍 #countryballs', 'Countryballs When {s} 💀',
          '{t} (Which One Are You?) #countryballs', 'POV: {t} 😂 #countryballs', 'Countryball Memes: {t} 🤣']


def load():
    return json.loads(HISTORY.read_text()) if HISTORY.exists() else {'videos': []}


def pick_plan(hist, rnd):
    past = hist['videos'][-12:]
    recent_sits = [v['situation'] for v in past[-6:]]
    sits = [s for s in balls.SITUATIONS if s not in recent_sits] or list(balls.SITUATIONS)
    sit = rnd.choice(sits)
    pool = list(balls.SITUATIONS[sit]['lines'])
    seen = {tuple(sorted(v['countries'])) for v in hist['videos'] if v['situation'] == sit}
    for _ in range(100):
        left, cs = list(pool), []
        while len(cs) < 4:
            c = rnd.choices(left, weights=[WEIGHT.get(x, 1) for x in left])[0]
            cs.append(c); left.remove(c)
        moods = {balls.SITUATIONS[sit]['lines'][c][1] for c in cs}
        if tuple(sorted(cs)) not in seen and len(moods) >= 3:   # tepkiler çeşitli olsun
            break
    return dict(situation=sit, countries=cs, seed=rnd.randrange(10 ** 6))


def metadata(plan, hist, rnd):
    s = balls.SITUATIONS[plan['situation']]
    t = s['title'].title().replace("'S", "'s").replace('°C', '°C')
    used = {v['title'] for v in hist['videos']}
    short_s = t.replace('Countries ', '', 1)
    opts = [x.format(t=t, s=short_s) for x in TITLES]; rnd.shuffle(opts)
    title = next((x for x in opts if x not in used), opts[0] + f' #{len(hist["videos"]) + 1}')
    names = [balls.NAMES[c].title() if balls.NAMES[c] not in ('USA', 'UK') else balls.NAMES[c] for c in plan['countries']]
    lines = '\n'.join(f'{balls.NAMES[c].title() if balls.NAMES[c] not in ("USA", "UK") else balls.NAMES[c]}: '
                      f'"{s["lines"][c][0]}"' for c in plan['countries'])
    desc = (f'{t}! Which one is YOUR country? Comment below 👇\n\n{lines}\n\n'
            'Friendly, funny country stereotypes. New Countries When... Shorts every day 🌍\n\n'
            '#shorts #countryballs #countryball #memes #animation')
    tags = ['countryballs', 'countryball', 'countryballs animation', 'countryball memes', 'countries when', 'country stereotypes', 'funny countries', 'countryball animation',
            s['name'].lower(), 'animation', 'shorts'] + [n.lower() for n in names]
    return title, desc, tags


def main():
    no_upload = '--no-upload' in sys.argv
    hist = load(); rnd = random.Random()
    plan = pick_plan(hist, rnd)
    title, desc, tags = metadata(plan, hist, rnd)
    key = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    print(f'plan: {plan}\ntitle: {title}', flush=True)
    out = HERE / 'output' / key
    mp4 = balls.render_video(plan, str(out))
    (out / 'meta.json').write_text(json.dumps(dict(plan=plan, title=title, description=desc, tags=tags), indent=2))
    if no_upload:
        print('render ok (yükleme yok):', mp4); return
    import upload
    if not upload.configured():
        sys.exit('YouTube secrets yok')
    print('kanal:', upload.check_channel())
    privacy = os.environ.get('YT_PRIVACY') or 'private'
    vid = upload.upload(mp4, title, desc, tags, privacy, category='23')
    print(f'yüklendi: https://youtube.com/shorts/{vid} ({privacy})')
    pl = HERE / 'playlists.json'
    if pl.exists() and json.loads(pl.read_text()).get('all'):
        try: upload.add_to_playlist(json.loads(pl.read_text())['all'], vid)
        except Exception as e: print('playlist:', e)
    hist['videos'].append(dict(id=vid, date=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'), kind='short',
                               title=title, privacy=privacy, **plan))
    HISTORY.write_text(json.dumps(hist, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
