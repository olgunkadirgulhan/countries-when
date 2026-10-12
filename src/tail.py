

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
        place(vo, base + 0.5, exclaim(code, mood, PLAN['seed'] + k))
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
