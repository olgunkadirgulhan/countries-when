"""voice-lib çıktısından güvenilir klipleri seçer: sonraki replik sızmamış ve metin doğru okunmuş olmalı.
Birimler (km/h, °C, km) okununca kelime sayısı artar → sayım öncesi metin açılır.
    python tools/clip_filter.py <artifact_klasörü>   → voices/os/<GÖK_CİSMİ>/<durum>.wav"""
import json, glob, os, re, shutil, sys

UNITS = [(r'km/h', ' kilometers per hour '), (r'°C', ' degrees celsius '), (r'\bkm\b', ' kilometers '), (r'(\d),(\d)', r'\1\2'),
         (r'(\d)\.(\d)', r'\1 point \2'), (r'%', ' percent ')]


def words(s, expand=False):
    if expand:
        for a, b in UNITS:
            s = re.sub(a, b, s)
    return re.findall(r"[\w']+", s.lower())


def ok(text, heard, ratio):
    from difflib import SequenceMatcher
    t, h = words(text, True), words(heard, True)
    sim = max(ratio, SequenceMatcher(None, t, h).ratio())   # birimler açıldıktan sonra benzerlik
    return sim >= 0.75 and len(h) <= len(t) + 2


if __name__ == '__main__':
    A = sys.argv[1]; keep = {}; drop = []
    for m in glob.glob(f'{A}/manifest_cw_*.json'):
        for k, v in json.load(open(m)).items():
            src = f'{A}/{k[4:]}'
            if not os.path.exists(src): continue
            code, sit = k.split('/')[2], k.split('/')[3]
            if ok(v['text'], v['heard'], v['ratio']):
                dst = f'voices/cw/{code}/{sit}'; os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(src, dst)
                keep[code] = keep.get(code, 0) + 1
            else:
                drop.append(f"{code}/{sit}: '{v['text']}' → '{v['heard']}'")
    print(keep, 'toplam', sum(keep.values()), 'elenen', len(drop)); print('\n'.join(drop))
