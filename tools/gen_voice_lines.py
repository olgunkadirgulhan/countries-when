"""src/bank.py → voice_lines.py (gecmiste-sen/tools/voice_lib.py bunu GitHub API'den okur; ülke başına 1 Gemini isteği)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import balls

VOICE = {  # ülke → (Gemini sesi, aksan tarifi) — karakter kişiliği tutarlı kalsın diye sabit
    'US': ('Puck', 'an upbeat American'), 'GB': ('Iapetus', 'a polite British'), 'DE': ('Charon', 'a precise German'),
    'FR': ('Leda', 'a charming French'), 'IT': ('Fenrir', 'an expressive Italian'), 'BR': ('Zephyr', 'a cheerful Brazilian'),
    'JP': ('Kore', 'a polite Japanese'), 'TR': ('Sadaltager', 'a warm Turkish'), 'CA': ('Achird', 'a friendly Canadian'),
    'MX': ('Algenib', 'a lively Mexican'), 'IN': ('Rasalgethi', 'a cheerful Indian'), 'ES': ('Aoede', 'a relaxed Spanish'),
    'KR': ('Laomedeia', 'an energetic Korean'), 'NL': ('Orus', 'a calm Dutch'), 'AR': ('Umbriel', 'a passionate Argentinian'),
    'IE': ('Sulafat', 'a cheerful Irish'),
    'NG': ('Schedar', 'an energetic Nigerian'), 'ID': ('Pulcherrima', 'a friendly Indonesian'), 'PL': ('Algieba', 'a cheerful Polish'),
    'SE': ('Despina', 'a calm Swedish'), 'NO': ('Alnilam', 'a relaxed Norwegian'), 'GR': ('Gacrux', 'a warm Greek'),
    'CH': ('Erinome', 'a precise Swiss'), 'CO': ('Callirrhoe', 'a lively Colombian'),
}
lines = {}
for sit, s in balls.SITUATIONS.items():
    for code, (txt, mood) in s['lines'].items():
        lines.setdefault(code, {})[sit] = (txt, mood)
out = os.path.join(balls.HERE, 'voice_lines.py')
with open(out, 'w', encoding='utf-8') as f:
    f.write('"""ÜRETİLDİ: tools/gen_voice_lines.py (kaynak src/bank.py). Ses: voices/cw/<ÜLKE>/<durum>.wav"""\n')
    f.write(f'VOICE = {json.dumps(VOICE, ensure_ascii=False, indent=1)}\n')
    f.write(f'LINES = {json.dumps(lines, ensure_ascii=False, indent=1)}\n')
print({k: len(v) for k, v in lines.items()})
