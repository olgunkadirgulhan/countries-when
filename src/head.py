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
         'NL': 'NETHERLANDS', 'AR': 'ARGENTINA'}

PLAN = {}


def configure(plan):
    global PLAN
    PLAN = plan


# ---------------------------------------------------------------- yardımcılar (Bloop Bonkers motorundan)
