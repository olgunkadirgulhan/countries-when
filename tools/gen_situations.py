"""Yeni durum (senaryo) üretici — Orbit Squad ve Countryball Chaos için ortak (2026-11-07).

Kural: her durum Shorts'ta yalnız bir kez kullanılır (run.py). Elle yazmak 6 ay yetmez (günde 3 = 540 durum), bu yüzden
haftalık iş akışı (gen-situations.yml) havuzu hep TARGET kadar önde tutar:
  1) Gemini yeni durumlar yazar (katı JSON, izinli sahne/ruh hali/karakter kodlarıyla)
  2) Orbit: ikinci Gemini geçişi her repliği NASA bilgisine göre doğrular; şüpheli replik atılır
     Countryball: siyaset/din/savaş/hakaret/kalıp yargı aşağılama yasak + kelime filtresi + ikinci geçiş güvenlik kontrolü
  3) Var olan başlık/ad/anahtar ile çakışan atılır; en az 5 replik ve 3 farklı ruh hali şartı
  4) src/bank_auto.json'a eklenir → bank.py çalışırken okur; voice_lines.py yeniden üretilir (voice-lib bunu okur)
    python tools/gen_situations.py [--target 90] [--max-new 30] [--dry-run]
"""
import json, os, re, sys, time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
ORBIT = (HERE / 'orbit.py').exists()
if ORBIT:
    import orbit as balls  # noqa: E402
else:
    import balls  # noqa: E402
import run  # noqa: E402

AUTO = HERE / 'src' / 'bank_auto.json'
MOODS = ['happy', 'shock', 'cool', 'calm', 'cry', 'angry', 'love', 'sleepy', 'shiver']
MODELS = ('gemini-flash-latest', 'gemini-3.5-flash', 'gemini-flash-lite-latest')

if ORBIT:
    WHO = ('planets, moons and dwarf planets of our solar system as cartoon characters ("Orbit Squad"). '
           'EVERY line must be a REAL, well-established space fact (NASA level), with rounded numbers, told as a joke. '
           'If a fact is uncertain, say "maybe" or skip it. No politics, religion, violence or scary content.')
    TITLE_HINT = 'Titles start with "PLANETS" (e.g. "PLANETS WHEN THE WIFI IS SLOW", "PLANETS AT A JOB INTERVIEW").'
else:
    WHO = ('countries as friendly cartoon balls ("Countryballs"). Lines are light, affectionate jokes about everyday '
           'culture: food, habits, weather, sports, holidays, manners. NEVER politics, wars, history conflicts, religion, '
           'borders, leaders, poverty, crime, alcohol abuse, or insulting stereotypes. Nothing a person from that '
           'country would find hurtful. Family-friendly, 13+.')
    TITLE_HINT = 'Titles start with "COUNTRIES" (e.g. "COUNTRIES AT THE AIRPORT", "COUNTRIES WHEN THE WIFI IS SLOW").'
BANNED = re.compile(r'\b(war|bomb|terror|nazi|dictator|president|prime minister|religio|god|allah|jesus|church|mosque|'
                    r'poor|poverty|crime|drunk|kill|dead|die|hate|stupid|dirty|lazy|cheap people|border|invade|army|gun)\w*',
                    re.I)


def gemini(prompt, temp=0.9):
    key = os.environ['GEMINI_API_KEY']
    last = None
    for model in MODELS:
        for attempt in range(3):
            try:
                r = requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                                  params={'key': key}, timeout=180,
                                  json={'contents': [{'parts': [{'text': prompt}]}],
                                        'generationConfig': {'temperature': temp, 'responseMimeType': 'application/json'}})
                if r.status_code == 429:
                    time.sleep(20 * (attempt + 1)); continue
                r.raise_for_status()
                return json.loads(r.json()['candidates'][0]['content']['parts'][0]['text'])
            except Exception as e:  # noqa: BLE001
                last = e; time.sleep(5)
    raise SystemExit(f'Gemini başarısız: {last}')


def load_auto():
    return json.loads(AUTO.read_text(encoding='utf-8')) if AUTO.exists() else {}


def fresh_count():
    used = run.short_sits(run.load())
    return sum(1 for s in balls.SITUATIONS if s not in used)


def generate(n, existing):
    codes = {c: balls.NAMES[c] for c in balls.NAMES}
    titles = sorted(v['title'] for v in balls.SITUATIONS.values())
    prompt = f"""You write short comedy skits for a YouTube Shorts channel about {WHO}
Each skit = one SITUATION; 7-10 characters each say ONE short reaction line (max 9 words), different moods.
{TITLE_HINT}
Already used titles (do NOT repeat or paraphrase these):
{json.dumps(titles, ensure_ascii=False)}

Characters (code: name): {json.dumps(codes, ensure_ascii=False)}
Scenes allowed: {json.dumps(list(balls.SCENES))}
Moods allowed: {json.dumps(MOODS)}

Write {n} NEW, varied, funny situations (everyday life, seasons, school, work, food, tech, sports, holidays, travel...).
Return JSON: a list of objects:
{{"key": "short_snake_case_id", "title": "UPPERCASE TITLE", "name": "Short Name", "scene": "<scene>",
  "lines": {{"<CODE>": ["line", "<mood>"], ...}}}}
Use at least 3 different moods per situation. Use only the given codes."""
    out = gemini(prompt)
    return out if isinstance(out, list) else out.get('situations', [])


def verify(sits):
    """İkinci geçiş: Orbit = bilgi doğruluğu, Countryball = güvenlik. Kalacak (key, code) çiftleri döner."""
    flat = [{'key': s['key'], 'code': c, 'line': l[0]} for s in sits for c, l in s['lines'].items()]
    if ORBIT:
        ask = ('You are a strict NASA fact checker. For each item, decide if the space fact in "line" (about the body '
               '"code", see names) is accurate with rounded numbers. Jokes are fine; the factual claim must be true. '
               'If unsure, mark false.')
    else:
        ask = ('You are a strict brand-safety reviewer for a family YouTube channel. For each item, decide if the line about '
               'country "code" is friendly, light and not insulting, political, religious, violent or a hurtful stereotype. '
               'If unsure, mark false.')
    prompt = (f'{ask}\nNames: {json.dumps(balls.NAMES)}\nItems: {json.dumps(flat, ensure_ascii=False)}\n'
              'Return JSON list of objects {"key":..., "code":..., "ok": true|false}.')
    res = gemini(prompt, temp=0.0)
    return {(r['key'], r['code']) for r in res if r.get('ok') is True}


def clean(sits, existing):
    seen_t = {run.tkey(v['title']) for v in balls.SITUATIONS.values()}
    seen_n = {v['name'].lower() for v in balls.SITUATIONS.values()}
    good = {}
    for s in sits:
        try:
            k = re.sub(r'[^a-z0-9_]', '', str(s['key']).lower())[:24]
            title = str(s['title']).upper().strip()
            name = str(s['name']).strip()[:28]
            scene = s['scene'] if s.get('scene') in balls.SCENES else balls.SCENES[0]
            if not k or k in existing or k in balls.SITUATIONS or k in good: continue
            if run.tkey(title) in seen_t or name.lower() in seen_n: continue
            if BANNED.search(title): continue
            lines = {}
            for c, l in (s.get('lines') or {}).items():
                if c not in balls.NAMES or not isinstance(l, (list, tuple)) or len(l) < 2: continue
                txt, mood = str(l[0]).strip(), str(l[1]).strip().lower()
                if mood not in MOODS or not (3 <= len(txt) <= 55) or BANNED.search(txt): continue
                lines[c] = (txt, mood)
            if len(lines) >= 5 and len({m for _, m in lines.values()}) >= 3:
                good[k] = dict(title=title, scene=scene, name=name, lines=lines)
                seen_t.add(run.tkey(title)); seen_n.add(name.lower())
        except Exception:  # noqa: BLE001
            continue
    return good


def main():
    a = sys.argv[1:]
    target = int(a[a.index('--target') + 1]) if '--target' in a else 90
    max_new = int(a[a.index('--max-new') + 1]) if '--max-new' in a else 30
    auto = load_auto()
    have = fresh_count()
    need = min(max_new, max(0, target - have))
    print(f'kullanılmamış durum: {have}, hedef: {target} → üretilecek: {need}')
    added = {}
    tries = 0
    while len(added) < need and tries < 6:
        tries += 1
        batch = generate(min(12, need - len(added) + 3), {**auto, **added})
        cand = clean(batch, {**auto, **added})
        if not cand: continue
        ok = verify([dict(key=k, lines={c: list(l) for c, l in v['lines'].items()}) for k, v in cand.items()])
        for k, v in cand.items():
            v['lines'] = {c: l for c, l in v['lines'].items() if (k, c) in ok}
            if len(v['lines']) >= 5 and len({m for _, m in v['lines'].values()}) >= 3 and len(added) < need:
                added[k] = v
        print(f'  tur {tries}: {len(cand)} aday, toplam eklenen {len(added)}')
    if not added:
        print('yeni durum yok'); return
    for k, v in added.items():
        print(f"  + {k}: {v['title']} ({len(v['lines'])} replik)")
    if '--dry-run' in a: return
    auto.update({k: dict(v, lines={c: list(l) for c, l in v['lines'].items()}) for k, v in added.items()})
    AUTO.write_text(json.dumps(auto, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'✓ {len(added)} durum eklendi → {AUTO.name} (toplam otomatik: {len(auto)})')


if __name__ == '__main__':
    main()
