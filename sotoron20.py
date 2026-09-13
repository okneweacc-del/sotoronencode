import os
import sys
import ast
import io
import re
import time
import json
import base64
import zlib
import bz2
import lzma
import marshal
import random
import string
import hashlib
import platform
import textwrap
import subprocess
import shutil
import traceback
import importlib
import struct
import binascii
import codecs
import itertools
import functools
import collections
import threading
import queue
import signal
import tempfile
import glob
import fnmatch
import datetime
import uuid
import math
import copy
import logging

IS_WIN = sys.platform.startswith("win")
IS_TERMUX = ("com.termux" in os.environ.get("PREFIX", "") or "termux" in os.environ.get("PREFIX", "").lower())
IS_ANDROID = "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ
IS_LINUX = sys.platform.startswith("linux")
IS_MAC = sys.platform == "darwin"
IS_UNIX = IS_LINUX or IS_MAC

if IS_WIN:
    try:
        os.system("")
    except Exception:
        pass

try:
    if IS_WIN:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)
except Exception:
    pass

def _supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    if IS_WIN:
        return True
    if not hasattr(sys.stdout, "isatty"):
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False

_COLOR_OK = _supports_color()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def lerp(a, b, t):
    return round(a + (b - a) * t)

def multi_gradient(colors_hex, steps):
    stops = [hex_to_rgb(c) for c in colors_hex]
    n = max(len(stops) - 1, 1)
    out = []
    for i in range(steps):
        t = i / max(steps - 1, 1)
        seg = min(int(t * n), n - 1)
        st = (t * n) - seg
        r1, g1, b1 = stops[seg]
        r2, g2, b2 = stops[min(seg + 1, len(stops) - 1)]
        out.append((lerp(r1, r2, st), lerp(g1, g2, st), lerp(b1, b2, st)))
    return out

def colorate(text, colors_hex=("#FFFFFF", "#A259FF", "#3B82F6")):
    if not _COLOR_OK:
        return text
    lines = text.split("\n")
    max_len = max((len(l) for l in lines), default=0)
    grad = multi_gradient(colors_hex, max_len if max_len > 0 else 1)
    out = []
    for line in lines:
        cl = ""
        for i, ch in enumerate(line):
            r, g, b = grad[i % len(grad)]
            cl += f"\033[38;2;{r};{g};{b}m{ch}"
        out.append(cl + "\033[0m")
    return "\n".join(out)

def colorate_vertical(text, colors_hex=("#FFFFFF", "#A259FF", "#3B82F6")):
    if not _COLOR_OK:
        return text
    lines = text.split("\n")
    grad = multi_gradient(colors_hex, max(len(lines), 1))
    return "\n".join(f"\033[38;2;{r};{g};{b}m{line}\033[0m" for (r, g, b), line in zip(grad, lines))

def clear_screen():
    try:
        if IS_WIN:
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        pass

EMOJI_CHARS = (
    "😀😃😄😁😆😅😂🤣☺😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹😣😖"
    "😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐"
    "🥴🤢🤮🤧😷🤒🤕🤑🤠😈👿👹👺🤡💩👻💀☠👽👾🤖🎃😺😸😹😻😼😽🙀😿😾"
)

EMOJI_EXTRA = (
    "🍎🍐🍊🍋🍌🍉🍇🍓🍈🍒🍑🥭🍍🥥🥝🍅🥑🥦🥬🥒🌶🌽🥕🧄🧅🥔🍠"
    "🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🥓🥩🍗🍖🌭🍔🍟🍕🥪🥙🧆🌮🌯🥗🥘"
    "🥫🍝🍜🍲🍛🍣🍱🥟🍤🍙🍚🍘🍥🥠🥮🍢🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭"
    "🍬🍫🍿🍩🍪🌰🥜🍯🥛🍼☕🍵🧃🥤🍶🍺🍻🥂🍷🥃🍸🍹🧉🍾"
)

EMOJI_ANIMALS = (
    "🐶🐱🐭🐹🐰🦊🐻🐼🐨🐯🦁🐮🐷🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🦆🦅🦉"
    "🦇🐺🐗🐴🦄🐝🐛🦋🐌🐞🐜🦟🦗🕷🕸🐢🐍🦎🦂🦀🦞🦐🦑🐙🐠🐟🐡"
)

EMOJI_FACES = (
    "☹☺☻🙂🙃😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚😇🤩🥳🤗🤔🤨😐😑😶"
    "🙄😏😣😥😮🤐😯😪😫😴😌😛😜😝🤤😒😓😔😕🙃🤑😲☹🙁😖😞😟😤😢😭😦"
)

EMOJI_HANDS = "👋🤚🖐✋🖖👌🤏✌🤞🤟🤘🤙👈👉👆🖕👇☝👍👎✊👊🤛🤜👏🙌👐🤲🤝🙏"
EMOJI_SYMBOLS = "❤🧡💛💚💙💜🖤🤍🤎💔❣💕💞💓💗💖💘💝💟☮✝☪🕉☸✡🔯🕎☯"
EMOJI_WEATHER = "☀☁⛅⛈🌤🌥🌦🌧🌨🌩🌪🌫🌬🌈☂☔⚡❄⛄☃🌊💧"
EMOJI_SPACE = "🌍🌎🌏🌐🌑🌒🌓🌔🌕🌖🌗🌘🌙🌚🌛🌜🌝🌞⭐🌟💫✨☄"
EMOJI_SPORT = "⚽⚾🏀🏐🏈🏉🎾🎱🎳🏓🏸🥊🥋⛳⛸🎿🛷🥌🎯🎮🕹"
EMOJI_MUSIC = "🎵🎶🎼🎤🎧🎷🎸🎹🎺🎻🥁"
EMOJI_TRAVEL = "🚗🚕🚙🚌🚎🏎🚓🚑🚒🚐🚚🚛🚜🛴🚲🛵🏍🚨🚔🚍🚘🚖🚡🚠🚟🚃"
EMOJI_OFFICE = "⌚📱📲💻⌨🖥🖨🖱🖲🕹🗜💽💾💿📀📼📷📸📹🎥📽🎞📞☎📟📠📺📻🎙"
EMOJI_CLOTHES = "👕👖🧣🧤🧥🧦👗👘🥻🩱🩲🩳👙👚👛👜👝🎒👞👟🥾🥿👠👡🩰👢👑👒🎩"
EMOJI_BODY = "👣👤👥🗣👶👦👧👨👩👪👫👬👭💏💑"

def _b_cjk(n):
    return "".join(chr(0x4E00 + i) for i in range(n))

def _b_cjk_a(n):
    return "".join(chr(0x3400 + i) for i in range(n))

def _b_cjk_b(n):
    out = []
    for i in range(0x20000, 0x20000 + n):
        try:
            out.append(chr(i))
        except Exception:
            out.append(chr(0x4E00 + i - 0x20000))
    return "".join(out[:n])

def _b_cjk_compat(n):
    out = []
    for i in range(0xF900, 0xFA00):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_hiragana(n):
    out = []
    for i in range(0x3041, 0x3097):
        out.append(chr(i))
    for i in range(0x309B, 0x30A0):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_katakana(n):
    out = []
    for i in range(0x30A1, 0x30FB):
        out.append(chr(i))
    for i in range(0x30FD, 0x3100):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_katakana_p(n):
    out = []
    for i in range(0x31F0, 0x3200):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_hangul(n):
    return "".join(chr(0xAC00 + i) for i in range(n))

def _b_hangul_jamo(n):
    return "".join(chr(0x1100 + i) for i in range(n))

def _b_hangul_compat(n):
    return "".join(chr(0x3131 + i) for i in range(n))

def _b_kanji_rad(n):
    out = []
    for i in range(0x2E80, 0x2EF4):
        out.append(chr(i))
    for i in range(0x2F00, 0x2FD6):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_math(n):
    out = []
    for i in range(0x2200, 0x22FF):
        out.append(chr(i))
    for i in range(0x2A00, 0x2AFF):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_arrows(n):
    out = []
    for i in range(0x2190, 0x2200):
        out.append(chr(i))
    for i in range(0x2900, 0x2980):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_box(n):
    out = []
    for i in range(0x2500, 0x2580):
        out.append(chr(i))
    for i in range(0x2580, 0x25A0):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_block(n):
    out = []
    for i in range(0x2580, 0x25A0):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_geom(n):
    out = []
    for i in range(0x25A0, 0x2600):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_cyr(n):
    out = []
    for i in range(0x0410, 0x0450):
        out.append(chr(i))
    for i in range(0x0450, 0x0500):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_cyr_s(n):
    out = []
    for i in range(0x0500, 0x0530):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_greek(n):
    out = []
    for i in range(0x0391, 0x03A2):
        out.append(chr(i))
    for i in range(0x03B1, 0x03CA):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_greek_e(n):
    out = []
    for i in range(0x1F00, 0x1FFF):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_coptic(n):
    out = []
    for i in range(0x2C80, 0x2D00):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_arabic(n):
    out = []
    for i in range(0x0621, 0x064B):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_arabic_s(n):
    out = []
    for i in range(0x0750, 0x0780):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_hebrew(n):
    out = []
    for i in range(0x05D0, 0x05EB):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_thai(n):
    out = []
    for i in range(0x0E01, 0x0E3B):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_lao(n):
    out = []
    for i in range(0x0E81, 0x0EDF):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_tibetan(n):
    out = []
    for i in range(0x0F00, 0x0FDA):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_myanmar(n):
    out = []
    for i in range(0x1000, 0x10A0):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_georgian(n):
    out = []
    for i in range(0x10A0, 0x10C6):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_ethiopic(n):
    out = []
    for i in range(0x1200, 0x1300):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_cherokee(n):
    out = []
    for i in range(0x13A0, 0x13F6):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_ogham(n):
    out = []
    for i in range(0x1680, 0x169D):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_runic(n):
    out = []
    for i in range(0x16A0, 0x16EB):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_mongolian(n):
    out = []
    for i in range(0x1800, 0x18AB):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_braille(n):
    out = []
    for i in range(0x2800, 0x28FF):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_deva(n):
    out = []
    for i in range(0x0905, 0x0940):
        out.append(chr(i))
    for i in range(0x0958, 0x0970):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_bengali(n):
    out = []
    for i in range(0x0985, 0x09FA):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_gurmukhi(n):
    out = []
    for i in range(0x0A05, 0x0A75):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_gujarati(n):
    out = []
    for i in range(0x0A85, 0x0AF9):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_oriya(n):
    out = []
    for i in range(0x0B05, 0x0B77):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_tamil(n):
    out = []
    for i in range(0x0B85, 0x0BFB):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_telugu(n):
    out = []
    for i in range(0x0C05, 0x0C7F):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_kannada(n):
    out = []
    for i in range(0x0C85, 0x0CF2):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_malayalam(n):
    out = []
    for i in range(0x0D05, 0x0D7F):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_sinhala(n):
    out = []
    for i in range(0x0D85, 0x0DF4):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_khmer(n):
    out = []
    for i in range(0x1780, 0x17DD):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_fullwidth(n):
    out = []
    for i in range(0xFF01, 0xFF5F):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_halfwidth(n):
    out = []
    for i in range(0xFF61, 0xFFE0):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_numeric(n):
    out = []
    for i in range(0x2460, 0x2500):
        out.append(chr(i))
    for i in range(0x2150, 0x2190):
        out.append(chr(i))
    for i in range(0x2070, 0x209D):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_special(n):
    pool = []
    for i in range(0x2600, 0x2700):
        pool.append(chr(i))
    for i in range(0x2700, 0x27C0):
        pool.append(chr(i))
    pool = list(dict.fromkeys(pool))
    while len(pool) < n:
        pool.append(chr(0x4E00 + (len(pool) - 100)))
    return "".join(pool[:n])

def _b_dingbats(n):
    out = []
    for i in range(0x2700, 0x27C0):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_misc(n):
    out = []
    for i in range(0x2600, 0x2700):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_supp_arrows(n):
    out = []
    for i in range(0x2B00, 0x2C00):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_currency(n):
    out = []
    for i in range(0x20A0, 0x20D0):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_letterlike(n):
    out = []
    for i in range(0x2100, 0x2150):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_glagolitic(n):
    out = []
    for i in range(0x2C00, 0x2C60):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_armenian(n):
    out = []
    for i in range(0x0531, 0x0589):
        out.append(chr(i))
    while len(out) < n:
        out.append(chr(0x4E00 + (len(out) - 100)))
    return "".join(out[:n])

def _b_mixed():
    pool = (list(EMOJI_CHARS)
            + [chr(0x4E00 + i) for i in range(60)]
            + [chr(0x3041 + i) for i in range(50)]
            + [chr(0x30A1 + i) for i in range(50)]
            + [chr(0xAC00 + i) for i in range(60)]
            + [chr(0x0410 + i) for i in range(36)])
    random.shuffle(pool)
    return "".join(pool[:256])

def _b_mixed2():
    pool = (list(EMOJI_EXTRA)
            + [chr(0x4E00 + i) for i in range(80)]
            + [chr(0x2190 + i) for i in range(40)]
            + [chr(0x2500 + i) for i in range(40)]
            + [chr(0x0391 + i) for i in range(40)]
            + [chr(0x0E01 + i) for i in range(56)])
    random.shuffle(pool)
    return "".join(pool[:256])

def _b_mixed3():
    pool = (list(EMOJI_CHARS) + list(EMOJI_EXTRA)
            + [chr(0x4E00 + i) for i in range(60)]
            + [chr(0x3041 + i) for i in range(40)])
    random.shuffle(pool)
    return "".join(pool[:256])

def _b_mixed4():
    pool = (list(EMOJI_ANIMALS) + list(EMOJI_FACES)
            + [chr(0x4E00 + i) for i in range(80)])
    random.shuffle(pool)
    while len(pool) < 256:
        pool.append(chr(0x4E00 + len(pool)))
    return "".join(pool[:256])

def _b_mixed5():
    pool = (list(EMOJI_SYMBOLS) + list(EMOJI_WEATHER)
            + list(EMOJI_SPACE)
            + [chr(0x4E00 + i) for i in range(80)])
    random.shuffle(pool)
    while len(pool) < 256:
        pool.append(chr(0x4E00 + len(pool)))
    return "".join(pool[:256])

def _b_mixed6():
    pool = (list(EMOJI_SPORT) + list(EMOJI_MUSIC)
            + list(EMOJI_TRAVEL) + list(EMOJI_OFFICE)
            + [chr(0x4E00 + i) for i in range(60)])
    random.shuffle(pool)
    while len(pool) < 256:
        pool.append(chr(0x4E00 + len(pool)))
    return "".join(pool[:256])

def _b_mixed7():
    pool = (list(EMOJI_CLOTHES) + list(EMOJI_BODY)
            + [chr(0x4E00 + i) for i in range(80)])
    random.shuffle(pool)
    while len(pool) < 256:
        pool.append(chr(0x4E00 + len(pool)))
    return "".join(pool[:256])

def _b_pure_emoji():
    pool = list(EMOJI_CHARS) + list(EMOJI_EXTRA)
    seen = []
    for c in pool:
        if c not in seen:
            seen.append(c)
        if len(seen) == 256:
            break
    if len(seen) < 256:
        for i in range(0x4E00, 0x4E00 + (256 - len(seen))):
            seen.append(chr(i))
    return "".join(seen[:256])

def _b_pure_faces():
    pool = list(EMOJI_FACES) + list(EMOJI_CHARS)
    seen = list(dict.fromkeys(pool))
    if len(seen) < 256:
        for i in range(0x4E00, 0x4E00 + (256 - len(seen))):
            seen.append(chr(i))
    return "".join(seen[:256])

def _b_pure_hands():
    pool = list(EMOJI_HANDS)
    seen = list(dict.fromkeys(pool))
    if len(seen) < 256:
        for i in range(0x4E00, 0x4E00 + (256 - len(seen))):
            seen.append(chr(i))
    return "".join(seen[:256])

def _b_pure_animals():
    pool = list(EMOJI_ANIMALS)
    seen = list(dict.fromkeys(pool))
    if len(seen) < 256:
        for i in range(0x4E00, 0x4E00 + (256 - len(seen))):
            seen.append(chr(i))
    return "".join(seen[:256])

def _b_pure_symbols():
    pool = list(EMOJI_SYMBOLS)
    seen = list(dict.fromkeys(pool))
    if len(seen) < 256:
        for i in range(0x4E00, 0x4E00 + (256 - len(seen))):
            seen.append(chr(i))
    return "".join(seen[:256])

_ALPHA_CACHE = {}

_ALPHA_MAP = {
    "emoji_cjk": lambda: EMOJI_CHARS + _b_cjk(256 - len(EMOJI_CHARS)),
    "cjk_only": lambda: _b_cjk(256),
    "cjk_ext_a": lambda: _b_cjk_a(256),
    "cjk_ext_b": lambda: _b_cjk_b(256),
    "cjk_compat": lambda: _b_cjk_compat(256),
    "hiragana": lambda: _b_hiragana(256),
    "katakana": lambda: _b_katakana(256),
    "katakana_phonetic": lambda: _b_katakana_p(256),
    "hangul": lambda: _b_hangul(256),
    "hangul_jamo": lambda: _b_hangul_jamo(256),
    "hangul_compat": lambda: _b_hangul_compat(256),
    "kanji_radicals": lambda: _b_kanji_rad(256),
    "math_symbols": lambda: _b_math(256),
    "arrows": lambda: _b_arrows(256),
    "supplement_arrows": lambda: _b_supp_arrows(256),
    "box_drawing": lambda: _b_box(256),
    "block_elements": lambda: _b_block(256),
    "geometric_shapes": lambda: _b_geom(256),
    "cyrillic": lambda: _b_cyr(256),
    "cyrillic_supp": lambda: _b_cyr_s(256),
    "greek": lambda: _b_greek(256),
    "greek_ext": lambda: _b_greek_e(256),
    "coptic": lambda: _b_coptic(256),
    "arabic": lambda: _b_arabic(256),
    "arabic_supp": lambda: _b_arabic_s(256),
    "hebrew": lambda: _b_hebrew(256),
    "thai": lambda: _b_thai(256),
    "lao": lambda: _b_lao(256),
    "tibetan": lambda: _b_tibetan(256),
    "myanmar": lambda: _b_myanmar(256),
    "georgian": lambda: _b_georgian(256),
    "ethiopic": lambda: _b_ethiopic(256),
    "cherokee": lambda: _b_cherokee(256),
    "ogham": lambda: _b_ogham(256),
    "runic": lambda: _b_runic(256),
    "mongolian": lambda: _b_mongolian(256),
    "braille": lambda: _b_braille(256),
    "devanagari": lambda: _b_deva(256),
    "bengali": lambda: _b_bengali(256),
    "gurmukhi": lambda: _b_gurmukhi(256),
    "gujarati": lambda: _b_gujarati(256),
    "oriya": lambda: _b_oriya(256),
    "tamil": lambda: _b_tamil(256),
    "telugu": lambda: _b_telugu(256),
    "kannada": lambda: _b_kannada(256),
    "malayalam": lambda: _b_malayalam(256),
    "sinhala": lambda: _b_sinhala(256),
    "khmer": lambda: _b_khmer(256),
    "fullwidth": lambda: _b_fullwidth(256),
    "halfwidth": lambda: _b_halfwidth(256),
    "numeric": lambda: _b_numeric(256),
    "special": lambda: _b_special(256),
    "dingbats": lambda: _b_dingbats(256),
    "misc_symbols": lambda: _b_misc(256),
    "currency": lambda: _b_currency(256),
    "letterlike": lambda: _b_letterlike(256),
    "glagolitic": lambda: _b_glagolitic(256),
    "armenian": lambda: _b_armenian(256),
    "pure_emoji": lambda: _b_pure_emoji(),
    "pure_faces": lambda: _b_pure_faces(),
    "pure_hands": lambda: _b_pure_hands(),
    "pure_animals": lambda: _b_pure_animals(),
    "pure_symbols": lambda: _b_pure_symbols(),
    "mixed": lambda: _b_mixed(),
    "mixed2": lambda: _b_mixed2(),
    "mixed3": lambda: _b_mixed3(),
    "mixed4": lambda: _b_mixed4(),
    "mixed5": lambda: _b_mixed5(),
    "mixed6": lambda: _b_mixed6(),
    "mixed7": lambda: _b_mixed7(),
}

ALPHA_NAMES = sorted(_ALPHA_MAP.keys())

def _make_alpha(kind):
    if kind in _ALPHA_CACHE:
        return _ALPHA_CACHE[kind]
    fn = _ALPHA_MAP.get(kind)
    if fn is None:
        fn = _ALPHA_MAP["emoji_cjk"]
    a = fn()
    a = a[:256]
    while len(a) < 256:
        a += chr(0x4E00 + len(a))
    _ALPHA_CACHE[kind] = a
    return a

JP_WORDS = ["こんにちは", "世界", "日本語", "テスト", "データ", "システム", "プログラム", "コード", "ファイル", "エラー", "デバッグ", "最強", "保護", "難読化", "解析", "実行", "暗号化", "復号", "起動", "終了", "構造", "仕組み", "処理", "結果", "開発", "研究", "技術", "情報", "計算", "記憶", "容量", "性能", "速度", "品質", "向上", "安全"]
CN_WORDS = ["你好", "世界", "中文", "测试", "数据", "系统", "程序", "代码", "文件", "错误", "调试", "最强", "保护", "混淆", "分析", "执行", "加密", "解密", "启动", "结束", "结构", "机制", "处理", "结果", "反调试", "反破解", "反注入", "反编译", "反跟踪", "反钩子", "网络安全", "信息安全", "代码保护", "逆向工程", "静态分析"]
KR_WORDS = ["안녕하세요", "세계", "한국어", "테스트", "데이터", "시스템", "프로그램", "코드", "파일", "오류", "디버그", "최강", "보호", "난독화", "분석", "실행", "암호화", "복호화", "시작", "종료", "구조", "메커니즘", "처리", "결과", "개발", "연구", "기술", "정보"]
RU_WORDS = ["привет", "мир", "русский", "тест", "данные", "система", "программа", "код", "файл", "ошибка", "отладка", "сильнейший", "защита", "обфускация", "анализ", "выполнение", "шифрование"]
AR_WORDS = ["مرحبا", "عالم", "العربية", "اختبار", "بيانات", "نظام", "برنامج", "كود", "ملف", "خطأ", "تصحيح", "أقوى", "حماية", "تشفير"]
TH_WORDS = ["สวัสดี", "โลก", "ภาษาไทย", "ทดสอบ", "ข้อมูล", "ระบบ", "โปรแกรม", "โค้ด", "ไฟล์", "ข้อผิดพลาด", "ดีบัก", "แข็งแกร่ง"]
HI_WORDS = ["नमस्ते", "दुनिया", "हिन्दी", "परीक्षण", "डेटा", "सिस्टम", "प्रोग्राम", "कोड", "फ़ाइल", "त्रुटि", "डीबग", "सबसे मजबूत"]
HE_WORDS = ["שלום", "עולם", "עברית", "בדיקה", "נתונים", "מערכת", "תוכנית", "קוד", "קובץ", "שגיאה", "ניפוי", "חזק"]
GR_WORDS = ["γεια", "κόσμος", "ελληνικά", "δοκιμή", "δεδομένα", "σύστημα", "πρόγραμμα", "κώδικας", "αρχείο", "σφάλμα", "προστασία"]
VI_WORDS = ["xin chào", "thế giới", "tiếng việt", "kiểm tra", "dữ liệu", "hệ thống", "chương trình", "mã", "tệp", "lỗi", "gỡ lỗi"]

def rand_junk_comment():
    out = []
    for _ in range(random.randint(8, 28)):
        k = random.choice(["e", "j", "c", "k", "r", "a", "t", "h", "i", "b", "g", "v", "x"])
        if k == "e":
            out.append(random.choice(EMOJI_CHARS))
        elif k == "j":
            out.append(random.choice(JP_WORDS))
        elif k == "c":
            out.append(random.choice(CN_WORDS))
        elif k == "k":
            out.append(random.choice(KR_WORDS))
        elif k == "r":
            out.append(random.choice(RU_WORDS))
        elif k == "a":
            out.append(random.choice(AR_WORDS))
        elif k == "t":
            out.append(random.choice(TH_WORDS))
        elif k == "i":
            out.append(random.choice(HI_WORDS))
        elif k == "b":
            out.append(random.choice(HE_WORDS))
        elif k == "g":
            out.append(random.choice(GR_WORDS))
        elif k == "v":
            out.append(random.choice(VI_WORDS))
        elif k == "h":
            out.append("".join(random.choices("0123456789abcdef", k=random.randint(6, 14))))
        else:
            out.append("".join(random.choices(string.ascii_letters + string.digits, k=random.randint(4, 12))))
    return "".join(out)

def rand_junk_code(n_lines):
    out = []
    for _ in range(n_lines):
        v = "_" + "".join(random.choices(string.ascii_letters + string.digits, k=10))
        kind = random.randint(0, 22)
        if kind == 0:
            val = str(random.randint(-10 ** 9, 10 ** 9))
        elif kind == 1:
            val = repr("".join(random.choices(string.ascii_letters, k=20)))
        elif kind == 2:
            val = f"{random.random():.12f}"
        elif kind == 3:
            val = "[" + ",".join(str(random.randint(0, 999)) for _ in range(10)) + "]"
        elif kind == 4:
            val = "{" + ",".join(f'"{random.choice(string.ascii_lowercase)}":{random.randint(0,9)}' for _ in range(6)) + "}"
        elif kind == 5:
            val = "(" + ",".join(str(random.randint(0, 9)) for _ in range(5)) + ")"
        elif kind == 6:
            val = f"0x{random.randint(0, 0xFFFFFFFF):X}"
        elif kind == 7:
            val = f"b'{''.join(random.choices('0123456789abcdef', k=16))}'"
        elif kind == 8:
            val = f"{random.randint(1, 999)} ** 2"
        elif kind == 9:
            val = f"({random.randint(1, 99)} << {random.randint(1, 8)})"
        elif kind == 10:
            val = f"sum(range({random.randint(1, 50)}))"
        elif kind == 11:
            val = f"len({repr(''.join(random.choices(string.ascii_letters, k=20)))})"
        elif kind == 12:
            val = f"bin({random.randint(0, 0xFF)})"
        elif kind == 13:
            val = f"oct({random.randint(0, 0xFF)})"
        elif kind == 14:
            val = f"abs(-{random.randint(1, 999)})"
        elif kind == 15:
            val = f"divmod({random.randint(1, 99)}, {random.randint(1, 9)})"
        elif kind == 16:
            val = f"int({random.random():.6f} * 1000)"
        elif kind == 17:
            val = f"str({random.randint(1, 999)}).zfill(6)"
        elif kind == 18:
            val = f"list(range({random.randint(1, 20)}))"
        elif kind == 19:
            val = f"tuple(range({random.randint(1, 20)}))"
        elif kind == 20:
            val = f"sorted([{random.randint(1, 999)}, {random.randint(1, 999)}])"
        elif kind == 21:
            val = f"hash({random.randint(1, 999)})"
        else:
            val = f"chr({random.randint(65, 90)})"
        out.append(f"{v} = {val}")
    return "\n".join(out)

def rand_junk_func(n_funcs):
    out = []
    for _ in range(n_funcs):
        fn = "_fn_" + "".join(random.choices(string.ascii_letters, k=8))
        arg = "_a_" + "".join(random.choices(string.ascii_letters, k=4))
        arg2 = "_b_" + "".join(random.choices(string.ascii_letters, k=4))
        kind = random.randint(0, 15)
        if kind == 0: body = f"return {arg} + {random.randint(1, 999)}"
        elif kind == 1: body = f"return str({arg}) * {random.randint(1, 5)}"
        elif kind == 2: body = f"return [{arg}, {random.randint(0, 99)}]"
        elif kind == 3: body = f"return {{'k': {arg}, 'v': {random.randint(0, 99)}}}"
        elif kind == 4: body = f"return len(str({arg}))"
        elif kind == 5: body = f"return {arg} if {arg} else {random.randint(0, 99)}"
        elif kind == 6: body = f"return ({arg}, {random.randint(0, 9)})"
        elif kind == 7: body = f"return {arg} * {random.randint(2, 9)}"
        elif kind == 8: body = f"return {arg} - {random.randint(1, 99)}"
        elif kind == 9: body = f"return {arg} // 2"
        elif kind == 10: body = f"return bool({arg})"
        elif kind == 11: body = f"return {arg} or {arg2}"
        elif kind == 12: body = f"return {arg} and {arg2}"
        elif kind == 13: body = f"return [{arg}, {arg2}]"
        elif kind == 14: body = f"return {arg} ^ {random.randint(1, 255)}"
        else: body = f"return {arg}"
        out.append(f"def {fn}({arg}, {arg2}=None):\n    {body}\n")
    return "\n".join(out)

def rand_junk_class(n_classes):
    out = []
    for _ in range(n_classes):
        cn = "_Cls_" + "".join(random.choices(string.ascii_letters, k=8))
        mn = "_m_" + "".join(random.choices(string.ascii_letters, k=6))
        mn2 = "_n_" + "".join(random.choices(string.ascii_letters, k=6))
        mn3 = "_o_" + "".join(random.choices(string.ascii_letters, k=6))
        arg = "_x_" + "".join(random.choices(string.ascii_letters, k=3))
        out.append(
            f"class {cn}:\n"
            f"    def __init__(self, {arg}=None):\n"
            f"        self.v = {arg}\n"
            f"    def {mn}(self):\n"
            f"        return self.v\n"
            f"    def {mn2}(self):\n"
            f"        return len(str(self.v))\n"
            f"    def {mn3}(self, other):\n"
            f"        return (self.v, other)\n"
        )
    return "\n".join(out)

def rand_id(n=8):
    return "_s20_" + "".join(random.choices(string.ascii_letters, k=n))

class StringObf(ast.NodeTransformer):
    def __init__(self, key=None):
        self.key = key if key is not None else random.randint(1, 255)
    def visit_Constant(self, node):
        if isinstance(node.value, str) and len(node.value) > 0:
            codes = [ord(c) ^ self.key for c in node.value]
            v = rand_id()
            body = ast.Call(
                func=ast.Attribute(value=ast.Constant(value=""), attr="join"),
                args=[ast.GeneratorExp(
                    elt=ast.Call(
                        func=ast.Name("chr", ast.Load()),
                        args=[ast.BinOp(
                            left=ast.Name(v, ast.Load()),
                            op=ast.BitXor(),
                            right=ast.Constant(self.key))],
                        keywords=[]),
                    generators=[ast.comprehension(
                        target=ast.Name(v, ast.Store()),
                        iter=ast.List([ast.Constant(x) for x in codes], ast.Load()),
                        ifs=[], is_async=0)]
                )], keywords=[])
            return ast.copy_location(body, node)
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            k = random.randint(1, 99999)
            body = ast.BinOp(
                left=ast.BinOp(left=ast.Constant(node.value + k), op=ast.Sub(), right=ast.Constant(k)),
                op=ast.Add(), right=ast.Constant(0))
            return ast.copy_location(body, node)
        return node

class StringObf2(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str) and len(node.value) > 0:
            codes = [ord(c) + 0x80 for c in node.value]
            v = rand_id()
            body = ast.Call(
                func=ast.Attribute(value=ast.Constant(value=""), attr="join"),
                args=[ast.GeneratorExp(
                    elt=ast.Call(
                        func=ast.Name("chr", ast.Load()),
                        args=[ast.BinOp(
                            left=ast.Name(v, ast.Load()),
                            op=ast.Sub(),
                            right=ast.Constant(0x80))],
                        keywords=[]),
                    generators=[ast.comprehension(
                        target=ast.Name(v, ast.Store()),
                        iter=ast.List([ast.Constant(x) for x in codes], ast.Load()),
                        ifs=[], is_async=0)]
                )], keywords=[])
            return ast.copy_location(body, node)
        return node

class StringObf3(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str) and len(node.value) > 0:
            b = node.value.encode("utf-8")
            codes = list(b)
            v = rand_id()
            body = ast.Call(
                func=ast.Attribute(value=ast.Constant(value=b""), attr="join"),
                args=[ast.GeneratorExp(
                    elt=ast.Call(
                        func=ast.Name("bytes", ast.Load()),
                        args=[ast.List([ast.Name(v, ast.Load())], ast.Load())],
                        keywords=[]),
                    generators=[ast.comprehension(
                        target=ast.Name(v, ast.Store()),
                        iter=ast.List([ast.Constant(x) for x in codes], ast.Load()),
                        ifs=[], is_async=0)]
                )], keywords=[])
            body2 = ast.Call(func=ast.Attribute(value=body, attr="decode"), args=[ast.Constant("utf-8")], keywords=[])
            return ast.copy_location(body2, node)
        return node

class StringObf4(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str) and len(node.value) > 0:
            codes = [ord(c) - 0x40 for c in node.value]
            v = rand_id()
            body = ast.Call(
                func=ast.Attribute(value=ast.Constant(value=""), attr="join"),
                args=[ast.GeneratorExp(
                    elt=ast.Call(
                        func=ast.Name("chr", ast.Load()),
                        args=[ast.BinOp(
                            left=ast.Name(v, ast.Load()),
                            op=ast.Add(),
                            right=ast.Constant(0x40))],
                        keywords=[]),
                    generators=[ast.comprehension(
                        target=ast.Name(v, ast.Store()),
                        iter=ast.List([ast.Constant(x) for x in codes], ast.Load()),
                        ifs=[], is_async=0)]
                )], keywords=[])
            return ast.copy_location(body, node)
        return node

class BoolObf(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            if node.value:
                body = ast.Compare(
                    left=ast.BinOp(left=ast.Constant(1), op=ast.Add(), right=ast.Constant(0)),
                    ops=[ast.Eq()], comparators=[ast.Constant(1)])
            else:
                body = ast.Compare(
                    left=ast.BinOp(left=ast.Constant(1), op=ast.Add(), right=ast.Constant(1)),
                    ops=[ast.Eq()], comparators=[ast.Constant(1)])
            return ast.copy_location(body, node)
        return node

class BoolObf2(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            if node.value:
                body = ast.Compare(left=ast.Constant(2), ops=[ast.Gt()], comparators=[ast.Constant(1)])
            else:
                body = ast.Compare(left=ast.Constant(1), ops=[ast.Gt()], comparators=[ast.Constant(2)])
            return ast.copy_location(body, node)
        return node

class BoolObf3(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            if node.value:
                body = ast.Compare(left=ast.Constant(0), ops=[ast.Eq()], comparators=[ast.Constant(0)])
            else:
                body = ast.Compare(left=ast.Constant(1), ops=[ast.Eq()], comparators=[ast.Constant(0)])
            return ast.copy_location(body, node)
        return node

class BinOpObf(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Add):
            k = random.randint(1, 999)
            wrap = ast.BinOp(
                left=ast.BinOp(left=node, op=ast.Add(), right=ast.Constant(k)),
                op=ast.Sub(), right=ast.Constant(k))
            return ast.copy_location(wrap, node)
        if isinstance(node.op, ast.Mult):
            k = random.randint(1, 9)
            wrap = ast.BinOp(
                left=ast.BinOp(left=node, op=ast.Mult(), right=ast.Constant(k)),
                op=ast.FloorDiv(), right=ast.Constant(k))
            return ast.copy_location(wrap, node)
        return node

class SubObf(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Sub):
            k = random.randint(1, 999)
            wrap = ast.BinOp(
                left=ast.BinOp(left=node, op=ast.Sub(), right=ast.Constant(k)),
                op=ast.Add(), right=ast.Constant(k))
            return ast.copy_location(wrap, node)
        return node

class FloorDivObf(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.FloorDiv):
            k = random.randint(2, 9)
            wrap = ast.BinOp(
                left=ast.BinOp(left=node, op=ast.Mult(), right=ast.Constant(k)),
                op=ast.FloorDiv(), right=ast.Constant(k))
            return ast.copy_location(wrap, node)
        return node

class ModObf(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Mod):
            k = random.randint(2, 9)
            wrap = ast.BinOp(
                left=ast.BinOp(left=node, op=ast.Add(), right=ast.Constant(k)),
                op=ast.Mod(), right=ast.Constant(k))
            return ast.copy_location(wrap, node)
        return node

class BitXorObf(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.BitXor):
            k = random.randint(1, 999)
            wrap = ast.BinOp(
                left=ast.BinOp(left=node, op=ast.BitXor(), right=ast.Constant(k)),
                op=ast.BitXor(), right=ast.Constant(k))
            return ast.copy_location(wrap, node)
        return node

class LShiftObf(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.LShift):
            k = random.randint(1, 4)
            wrap = ast.BinOp(
                left=ast.BinOp(left=node, op=ast.LShift(), right=ast.Constant(k)),
                op=ast.RShift(), right=ast.Constant(k))
            return ast.copy_location(wrap, node)
        return node

class CompareObf(ast.NodeTransformer):
    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
            left = node.left
            right = node.comparators[0]
            new_node = ast.Compare(
                left=ast.BinOp(left=left, op=ast.Add(), right=ast.Constant(0)),
                ops=[ast.Eq()],
                comparators=[ast.BinOp(left=right, op=ast.Add(), right=ast.Constant(0))])
            return ast.copy_location(new_node, node)
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.NotEq):
            left = node.left
            right = node.comparators[0]
            new_node = ast.Compare(
                left=ast.BinOp(left=left, op=ast.Add(), right=ast.Constant(0)),
                ops=[ast.NotEq()],
                comparators=[ast.BinOp(left=right, op=ast.Add(), right=ast.Constant(0))])
            return ast.copy_location(new_node, node)
        return node

class CompareObf2(ast.NodeTransformer):
    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.Lt):
            left = node.left
            right = node.comparators[0]
            new_node = ast.Compare(
                left=ast.BinOp(left=left, op=ast.Add(), right=ast.Constant(0)),
                ops=[ast.Lt()],
                comparators=[ast.BinOp(left=right, op=ast.Add(), right=ast.Constant(0))])
            return ast.copy_location(new_node, node)
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.Gt):
            left = node.left
            right = node.comparators[0]
            new_node = ast.Compare(
                left=ast.BinOp(left=left, op=ast.Add(), right=ast.Constant(0)),
                ops=[ast.Gt()],
                comparators=[ast.BinOp(left=right, op=ast.Add(), right=ast.Constant(0))])
            return ast.copy_location(new_node, node)
        return node

class UnaryObf(ast.NodeTransformer):
    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.USub):
            if isinstance(node.operand, ast.Constant):
                return ast.copy_location(ast.Constant(-node.operand.value), node)
        if isinstance(node.op, ast.UAdd):
            if isinstance(node.operand, ast.Constant):
                return ast.copy_location(ast.Constant(+node.operand.value), node)
        return node

class InvertObf(ast.NodeTransformer):
    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Invert):
            if isinstance(node.operand, ast.Constant) and isinstance(node.operand.value, int):
                return ast.copy_location(ast.Constant(~node.operand.value), node)
        return node

class NotObf(ast.NodeTransformer):
    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Not):
            inner = node.operand
            new_node = ast.UnaryOp(op=ast.Not(), operand=ast.UnaryOp(op=ast.Not(), operand=inner))
            return ast.copy_location(new_node, node)
        return node

def apply_ast_layers(src_bytes, intensity):
    try:
        tree = ast.parse(src_bytes.decode("utf-8"))
    except Exception:
        return src_bytes
    key = random.randint(1, 255)
    tree = StringObf(key).visit(tree)
    tree = BoolObf().visit(tree)
    if intensity >= 2:
        tree = BinOpObf().visit(tree)
        tree = SubObf().visit(tree)
        tree = FloorDivObf().visit(tree)
        tree = ModObf().visit(tree)
        tree = BitXorObf().visit(tree)
        tree = LShiftObf().visit(tree)
    if intensity >= 3:
        tree = CompareObf().visit(tree)
        tree = CompareObf2().visit(tree)
        tree = NotObf().visit(tree)
        tree = UnaryObf().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree).encode("utf-8")
    except Exception:
        return src_bytes

def _xor(data, key):
    return bytes(b ^ key for b in data)

def pack_payload(src_bytes, xor_key, alpha, depth):
    data = src_bytes
    if depth >= 1: data = zlib.compress(data, 9)
    if depth >= 2: data = bz2.compress(data, 9)
    if depth >= 3: data = lzma.compress(data, preset=9)
    if depth >= 4: data = _xor(data, xor_key)
    if depth >= 5: data = base64.b64encode(data)
    if depth >= 6: data = data[::-1]
    if depth >= 7: data = base64.b64encode(data)
    if depth >= 8: data = base64.a85encode(data)
    return "".join(alpha[b] for b in data)

def build_runtime(xor_key, alpha_repr, blob_repr, hash_hex, depth):
    dc = ["_d = _alpha_rev_apply(_p, _ALPHA)"]
    if depth >= 8: dc.append("_d = _b64.a85decode(_d)")
    if depth >= 7: dc.append("_d = _b64.b64decode(_d)")
    if depth >= 6: dc.append("_d = _d[::-1]")
    if depth >= 5: dc.append("_d = _b64.b64decode(_d)")
    if depth >= 4: dc.append(f"_d = bytes(b ^ {xor_key} for b in _d)")
    if depth >= 3: dc.append("_d = _lzma.decompress(_d)")
    if depth >= 2: dc.append("_d = _bz2.decompress(_d)")
    if depth >= 1: dc.append("_d = _zlib.decompress(_d)")
    dc.append("return _marshal.loads(_d)")
    body = "\n    ".join(dc)
    return f'''import sys as _sys
import os as _os
import io as _io
import time as _time
import base64 as _b64
import zlib as _zlib
import bz2 as _bz2
import lzma as _lzma
import marshal as _marshal
import hashlib as _hl

_ALPHA = {alpha_repr}
_BLOB = {blob_repr}
_KEY = {xor_key}
_HASH = "{hash_hex}"
_DEPTH = {depth}

def _alpha_rev_apply(_p, _a):
    _rev = {{c: i for i, c in enumerate(_a)}}
    return bytes(_rev[c] for c in _p if c in _rev)

def _patch_sys_aliases():
    _aliases = ("tempfile", "io", "random", "time", "json", "re", "math", "string", "hashlib", "base64", "zlib", "bz2", "lzma", "marshal", "platform", "subprocess", "shutil", "glob", "fnmatch", "struct", "binascii", "codecs", "itertools", "functools", "collections", "threading", "queue", "signal", "uuid", "copy", "logging", "typing", "socket", "ssl", "urllib", "http", "datetime", "pathlib", "sqlite3", "csv", "xml", "html", "email", "smtplib", "ctypes", "multiprocessing", "concurrent", "asyncio")
    for _a in _aliases:
        if not hasattr(_sys, _a):
            try: setattr(_sys, _a, __import__(_a))
            except Exception: pass

def _check_env():
    if _sys.gettrace() is not None: _sys.exit(1)
    try:
        for _m in list(_sys.modules):
            _ml = _m.lower()
            if ("pydevd" in _ml or "debugpy" in _ml or "ptvsd" in _ml or _ml in ("pdb", "idlelib", "frida", "uncompyle6", "decompyle3", "pycdc", "unpyc", "decompyle")):
                _sys.exit(1)
    except Exception: pass
    try:
        if _os.environ.get("PYTHONINSPECT"): _sys.exit(1)
        if _os.environ.get("PYTHONBREAKPOINT"): _sys.exit(1)
        if _sys.flags.interactive: _sys.exit(1)
    except Exception: pass

def _dec(_p):
    {body}

def _run():
    _t0 = _time.time()
    _check_env()
    _patch_sys_aliases()
    try: _code = _dec(_BLOB)
    except Exception as _e:
        _sys.stderr.write("[sotoron20] decode failed: " + str(_e) + "\\n")
        _sys.exit(1)
    if _time.time() - _t0 > 180: _sys.exit(1)
    try: exec(_code, globals(), globals())
    except AttributeError as _e:
        _sys.stderr.write("[sotoron20] AttributeError: " + str(_e) + "\\n")
        _sys.exit(1)

_run()
'''

def build(src_bytes, xor_key=None, alpha_key="emoji_cjk", depth=8, intensity=2, junk_level=2, add_banner=False, junk_funcs=0, junk_classes=0, header_extra=True, min_lines=2000):
    if xor_key is None:
        xor_key = random.randint(1, 255)
    alpha = _make_alpha(alpha_key)
    src_ast = apply_ast_layers(src_bytes, intensity)
    compiled = marshal.dumps(compile(src_ast, "<sotoron20>", "exec"))
    blob = pack_payload(compiled, xor_key, alpha, depth)
    hash_hex = hashlib.sha256(compiled).hexdigest()
    header = (
        "# -*- coding: utf-8 -*-\n"
        "# SOTORON20 OBFUSCATED PAYLOAD\n"
        "# Author : sotoron20\n"
        "# Github : https://github.com/okneweacc-del\n"
    )
    if header_extra:
        header += (
            f"# build id : {uuid.uuid4().hex}\n"
            f"# timestamp: {datetime.datetime.now().isoformat()}\n"
            f"# platform : {sys.platform}\n"
            f"# python   : {platform.python_version()}\n"
            f"# layers   : {depth}\n"
            f"# alphabet : {alpha_key}\n"
        )
    runtime = build_runtime(xor_key, repr(alpha), repr(blob), hash_hex, depth)
    runtime_lines = runtime.count("\n") + 1
    header_lines = header.count("\n") + 1
    base_lines = runtime_lines + header_lines
    target = min_lines if min_lines and min_lines > base_lines else base_lines + 500
    junk_line_count = max(50, target - base_lines)
    junk_lines = []
    for _ in range(junk_line_count):
        junk_lines.append("# " + rand_junk_comment())
    junk_code = rand_junk_code(max(200, junk_line_count // 3))
    junk_fn = rand_junk_func(junk_funcs) if junk_funcs else ""
    junk_cls = rand_junk_class(junk_classes) if junk_classes else ""
    banner_txt = "print()" if add_banner else ""
    body = header + "\n".join(junk_lines) + "\n" + junk_code + "\n" + junk_fn + "\n" + junk_cls + "\n" + banner_txt + "\n" + runtime
    return body

BANNER = r"""
   _____ ____  ______ ____  ____  _   __ ____  ____
  / ___// __ \/_  __// __ \/ __ \/ | / // __ \/ __ \
  \__ \/ / / / / /  / / / / /_/ /  |/ // / / / / / /
 ___/ / /_/ / / /  / /_/ / _, _/ /|  // /_/ / /_/ /
/____/\____/ /_/   \____/_/ |_/_/ |_//_____/\____/
"""

def print_banner():
    print(colorate_vertical(BANNER, ("#FFFFFF", "#A259FF", "#3B82F6", "#00E5FF")))
    print(colorate("  sotoron20 obfuscator", ("#FFFFFF", "#A259FF", "#3B82F6")))
    print(colorate("  github.com/okneweacc-del", ("#3B82F6", "#00E5FF")))
    print(colorate(f"  platform : {'windows' if IS_WIN else ('termux' if IS_TERMUX else 'unix')}", ("#888888",)))
    print(colorate(f"  python   : {platform.python_version()}", ("#888888",)))
    print(colorate(f"  alphabets: {len(ALPHA_NAMES)}", ("#888888",)))
    print()

def _ask(prompt, default=None):
    try:
        v = input(colorate(f"  {prompt}", ("#A259FF", "#3B82F6")))
        v = v.strip()
        if not v and default is not None:
            return default
        return v
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

def _ask_choice(prompt, choices, default=None):
    cs = "/".join(choices[:8])
    while True:
        v = _ask(f"{prompt} [{cs}...] ({default}): ", default=default)
        if v in choices:
            return v
        if v == "" and default:
            return default
        print(colorate("  invalid, try again", ("#FF4444",)))

def _ask_int(prompt, lo, hi, default=None):
    while True:
        v = _ask(f"{prompt} ({lo}-{hi})", default=str(default) if default is not None else None)
        try:
            n = int(v)
            if lo <= n <= hi:
                return n
        except ValueError:
            pass
        print(colorate("  invalid, try again", ("#FF4444",)))

PRESETS = {
    "fast":     {"depth": 4, "intensity": 1, "junk_level": 1, "alpha": "emoji_cjk", "jf": 0, "jc": 0},
    "normal":   {"depth": 6, "intensity": 2, "junk_level": 2, "alpha": "emoji_cjk", "jf": 0, "jc": 0},
    "strong":   {"depth": 8, "intensity": 2, "junk_level": 2, "alpha": "mixed", "jf": 5, "jc": 3},
    "extreme":  {"depth": 8, "intensity": 3, "junk_level": 3, "alpha": "emoji_cjk", "jf": 15, "jc": 10},
    "paranoid": {"depth": 8, "intensity": 3, "junk_level": 3, "alpha": "mixed5", "jf": 25, "jc": 20},
    "insane":   {"depth": 8, "intensity": 3, "junk_level": 3, "alpha": "mixed6", "jf": 40, "jc": 30},
    "bloated":  {"depth": 8, "intensity": 3, "junk_level": 3, "alpha": "pure_emoji", "jf": 60, "jc": 40},
    "nuke":     {"depth": 8, "intensity": 3, "junk_level": 3, "alpha": "pure_animals", "jf": 100, "jc": 60},
}

def list_alphabets():
    print()
    print(colorate("  available alphabets:", ("#A259FF",)))
    keys = sorted(ALPHA_NAMES)
    for i in range(0, len(keys), 4):
        chunk = keys[i:i + 4]
        print("    " + "  ".join(f"{k:<20}" for k in chunk))
    print()

def interactive_main():
    clear_screen()
    print_banner()
    while True:
        f = _ask("input file: ")
        if not f:
            continue
        f = f.strip('"').strip("'")
        if os.path.isfile(f):
            break
        print(colorate(f"  not found: {f}", ("#FF4444",)))
    default_out = "sotoron20-" + os.path.basename(f)
    outp = _ask(f"output file ({default_out}): ", default=default_out)
    if not outp:
        outp = default_out
    print()
    print(colorate("  presets:", ("#A259FF",)))
    keys = list(PRESETS.keys())
    for i, k in enumerate(keys, 1):
        print(colorate(f"    {i}. {k}", ("#3B82F6",)))
    print(colorate("    0. custom", ("#3B82F6",)))
    preset_in = _ask(f"choose preset (0-{len(keys)}) (3): ", default="3")
    preset_map = {str(i + 1): k for i, k in enumerate(keys)}
    preset_name = preset_map.get(preset_in, "strong")
    if preset_in == "0":
        list_alphabets()
        alpha_key = _ask_choice("alphabet", list(ALPHA_NAMES), default="emoji_cjk")
        depth = _ask_int("encode depth", 1, 8, default=8)
        intensity = _ask_int("ast intensity", 1, 3, default=2)
        junk = _ask_int("junk level", 1, 3, default=2)
        jf = _ask_int("junk functions", 0, 200, default=0)
        jc = _ask_int("junk classes", 0, 200, default=0)
    else:
        p = PRESETS[preset_name]
        alpha_key = p["alpha"]
        depth = p["depth"]
        intensity = p["intensity"]
        junk = p["junk_level"]
        jf = p["jf"]
        jc = p["jc"]
    min_lines = _ask_int("min lines output", 500, 10000, default=2000)
    banner_choice = _ask_choice("show loading line", ["y", "n"], default="n")
    xor_in = _ask("xor key (1-255, blank=random): ", default="")
    try:
        xor_key = int(xor_in) if xor_in else random.randint(1, 255)
        xor_key = max(1, min(255, xor_key))
    except ValueError:
        xor_key = random.randint(1, 255)
    print()
    print(colorate("  [*] reading...", ("#00E5FF",)))
    with open(f, "rb") as fp:
        src = fp.read()
    print(colorate(f"  [*] input  : {f}  ({len(src)} bytes)", ("#00E5FF",)))
    print(colorate("  [*] building...", ("#00E5FF",)))
    t0 = time.time()
    try:
        out = build(src, xor_key=xor_key, alpha_key=alpha_key, depth=depth, intensity=intensity, junk_level=junk, add_banner=(banner_choice == "y"), junk_funcs=jf, junk_classes=jc, min_lines=min_lines)
    except Exception as e:
        print(colorate(f"  [!] build failed: {e}", ("#FF4444",)))
        traceback.print_exc()
        sys.exit(1)
    with open(outp, "w", encoding="utf-8") as fp:
        fp.write(out)
    out_size = os.path.getsize(outp)
    ratio = out_size / max(len(src), 1)
    dt = time.time() - t0
    print(colorate(f"  [*] output : {outp}  ({out_size} bytes)", ("#00E5FF",)))
    print(colorate(f"  [*] ratio  : x{ratio:.2f}", ("#00E5FF",)))
    print(colorate(f"  [*] time   : {dt:.2f}s", ("#00E5FF",)))
    print(colorate("  [+] done", ("#00FF88",)))
    print()
    verify = _ask_choice("verify syntax of output", ["y", "n"], default="y")
    if verify == "y":
        try:
            with open(outp, "r", encoding="utf-8") as fp:
                compile(fp.read(), outp, "exec")
            print(colorate("  [+] syntax OK", ("#00FF88",)))
        except SyntaxError as e:
            print(colorate(f"  [!] syntax error: {e}", ("#FF4444",)))

def cli_main(argv):
    if len(argv) < 3:
        print(colorate("  usage: sotoron20.py <input> <output> [alpha] [depth 1-8] [ast 1-3] [junk 1-3]", ("#A259FF", "#3B82F6")))
        sys.exit(1)
    inp = argv[1]
    outp = argv[2]
    alpha_key = argv[3] if len(argv) > 3 else "emoji_cjk"
    depth = int(argv[4]) if len(argv) > 4 else 8
    intensity = int(argv[5]) if len(argv) > 5 else 2
    junk = int(argv[6]) if len(argv) > 6 else 2
    if alpha_key not in ALPHA_NAMES:
        alpha_key = "emoji_cjk"
    depth = max(1, min(8, depth))
    intensity = max(1, min(3, intensity))
    junk = max(1, min(3, junk))
    if not os.path.isfile(inp):
        print(colorate(f"  [!] not found: {inp}", ("#FF4444",)))
        sys.exit(1)
    print_banner()
    with open(inp, "rb") as fp:
        src = fp.read()
    t0 = time.time()
    out = build(src, alpha_key=alpha_key, depth=depth, intensity=intensity, junk_level=junk)
    with open(outp, "w", encoding="utf-8") as fp:
        fp.write(out)
    print(colorate(f"  [+] {outp}  {os.path.getsize(outp)} bytes  {time.time() - t0:.2f}s", ("#00FF88",)))

def self_test():
    sample = "def hello(name):\n    print('hello ' + name)\n    return len(name) + 42\nhello('sotoron20')\n".encode("utf-8")
    print(colorate("  [*] self test...", ("#00E5FF",)))
    fails = []
    for a in ALPHA_NAMES:
        for d in (1, 3, 5, 8):
            try:
                out = build(sample, alpha_key=a, depth=d, intensity=1, junk_level=1, add_banner=False, min_lines=100)
                compile(out, "<test>", "exec")
            except Exception as e:
                fails.append((a, d, str(e)))
    if fails:
        for a, d, e in fails:
            print(colorate(f"  [!] fail alpha={a} depth={d}: {e}", ("#FF4444",)))
        return False
    print(colorate("  [+] all pass", ("#00FF88",)))
    return True

def list_all_alphabets_cmd():
    print_banner()
    for k in sorted(ALPHA_NAMES):
        v = _make_alpha(k)
        print(f"    {k:<20} len={len(v)}  first={v[:3]!r}")
    print()

def main():
    argv = sys.argv
    if len(argv) == 2 and argv[1] in ("--test", "-t"):
        print_banner()
        self_test()
        return
    if len(argv) == 2 and argv[1] in ("--list", "-l"):
        list_all_alphabets_cmd()
        return
    if len(argv) == 2 and argv[1] in ("--help", "-h"):
        print_banner()
        print("    python sotoron20.py                       # interactive")
        print("    python sotoron20.py in.py out.py         # cli default")
        print("    python sotoron20.py in.py out.py emoji_cjk 8 2 2")
        print("    python sotoron20.py --test               # self test")
        print("    python sotoron20.py --list               # list alphabets")
        return
    if len(argv) >= 3:
        cli_main(argv)
    else:
        interactive_main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        sys.exit(1)

_GEN_001 = {"k": 1, "v": "sotoron20"}
_GEN_002 = {"k": 2, "v": "sotoron20"}
_GEN_003 = {"k": 3, "v": "sotoron20"}
_GEN_004 = {"k": 4, "v": "sotoron20"}
_GEN_005 = {"k": 5, "v": "sotoron20"}
_GEN_006 = {"k": 6, "v": "sotoron20"}
_GEN_007 = {"k": 7, "v": "sotoron20"}
_GEN_008 = {"k": 8, "v": "sotoron20"}
_GEN_009 = {"k": 9, "v": "sotoron20"}
_GEN_010 = {"k": 10, "v": "sotoron20"}
_GEN_011 = {"k": 11, "v": "sotoron20"}
_GEN_012 = {"k": 12, "v": "sotoron20"}
_GEN_013 = {"k": 13, "v": "sotoron20"}
_GEN_014 = {"k": 14, "v": "sotoron20"}
_GEN_015 = {"k": 15, "v": "sotoron20"}
_GEN_016 = {"k": 16, "v": "sotoron20"}
_GEN_017 = {"k": 17, "v": "sotoron20"}
_GEN_018 = {"k": 18, "v": "sotoron20"}
_GEN_019 = {"k": 19, "v": "sotoron20"}
_GEN_020 = {"k": 20, "v": "sotoron20"}
_GEN_021 = {"k": 21, "v": "sotoron20"}
_GEN_022 = {"k": 22, "v": "sotoron20"}
_GEN_023 = {"k": 23, "v": "sotoron20"}
_GEN_024 = {"k": 24, "v": "sotoron20"}
_GEN_025 = {"k": 25, "v": "sotoron20"}
_GEN_026 = {"k": 26, "v": "sotoron20"}
_GEN_027 = {"k": 27, "v": "sotoron20"}
_GEN_028 = {"k": 28, "v": "sotoron20"}
_GEN_029 = {"k": 29, "v": "sotoron20"}
_GEN_030 = {"k": 30, "v": "sotoron20"}
_GEN_031 = {"k": 31, "v": "sotoron20"}
_GEN_032 = {"k": 32, "v": "sotoron20"}
_GEN_033 = {"k": 33, "v": "sotoron20"}
_GEN_034 = {"k": 34, "v": "sotoron20"}
_GEN_035 = {"k": 35, "v": "sotoron20"}
_GEN_036 = {"k": 36, "v": "sotoron20"}
_GEN_037 = {"k": 37, "v": "sotoron20"}
_GEN_038 = {"k": 38, "v": "sotoron20"}
_GEN_039 = {"k": 39, "v": "sotoron20"}
_GEN_040 = {"k": 40, "v": "sotoron20"}
_GEN_041 = {"k": 41, "v": "sotoron20"}
_GEN_042 = {"k": 42, "v": "sotoron20"}
_GEN_043 = {"k": 43, "v": "sotoron20"}
_GEN_044 = {"k": 44, "v": "sotoron20"}
_GEN_045 = {"k": 45, "v": "sotoron20"}
_GEN_046 = {"k": 46, "v": "sotoron20"}
_GEN_047 = {"k": 47, "v": "sotoron20"}
_GEN_048 = {"k": 48, "v": "sotoron20"}
_GEN_049 = {"k": 49, "v": "sotoron20"}
_GEN_050 = {"k": 50, "v": "sotoron20"}
_GEN_051 = {"k": 51, "v": "sotoron20"}
_GEN_052 = {"k": 52, "v": "sotoron20"}
_GEN_053 = {"k": 53, "v": "sotoron20"}
_GEN_054 = {"k": 54, "v": "sotoron20"}
_GEN_055 = {"k": 55, "v": "sotoron20"}
_GEN_056 = {"k": 56, "v": "sotoron20"}
_GEN_057 = {"k": 57, "v": "sotoron20"}
_GEN_058 = {"k": 58, "v": "sotoron20"}
_GEN_059 = {"k": 59, "v": "sotoron20"}
_GEN_060 = {"k": 60, "v": "sotoron20"}
_GEN_061 = {"k": 61, "v": "sotoron20"}
_GEN_062 = {"k": 62, "v": "sotoron20"}
_GEN_063 = {"k": 63, "v": "sotoron20"}
_GEN_064 = {"k": 64, "v": "sotoron20"}
_GEN_065 = {"k": 65, "v": "sotoron20"}
_GEN_066 = {"k": 66, "v": "sotoron20"}
_GEN_067 = {"k": 67, "v": "sotoron20"}
_GEN_068 = {"k": 68, "v": "sotoron20"}
_GEN_069 = {"k": 69, "v": "sotoron20"}
_GEN_070 = {"k": 70, "v": "sotoron20"}
_GEN_071 = {"k": 71, "v": "sotoron20"}
_GEN_072 = {"k": 72, "v": "sotoron20"}
_GEN_073 = {"k": 73, "v": "sotoron20"}
_GEN_074 = {"k": 74, "v": "sotoron20"}
_GEN_075 = {"k": 75, "v": "sotoron20"}
_GEN_076 = {"k": 76, "v": "sotoron20"}
_GEN_077 = {"k": 77, "v": "sotoron20"}
_GEN_078 = {"k": 78, "v": "sotoron20"}
_GEN_079 = {"k": 79, "v": "sotoron20"}
_GEN_080 = {"k": 80, "v": "sotoron20"}
_GEN_081 = {"k": 81, "v": "sotoron20"}
_GEN_082 = {"k": 82, "v": "sotoron20"}
_GEN_083 = {"k": 83, "v": "sotoron20"}
_GEN_084 = {"k": 84, "v": "sotoron20"}
_GEN_085 = {"k": 85, "v": "sotoron20"}
_GEN_086 = {"k": 86, "v": "sotoron20"}
_GEN_087 = {"k": 87, "v": "sotoron20"}
_GEN_088 = {"k": 88, "v": "sotoron20"}
_GEN_089 = {"k": 89, "v": "sotoron20"}
_GEN_090 = {"k": 90, "v": "sotoron20"}
_GEN_091 = {"k": 91, "v": "sotoron20"}
_GEN_092 = {"k": 92, "v": "sotoron20"}
_GEN_093 = {"k": 93, "v": "sotoron20"}
_GEN_094 = {"k": 94, "v": "sotoron20"}
_GEN_095 = {"k": 95, "v": "sotoron20"}
_GEN_096 = {"k": 96, "v": "sotoron20"}
_GEN_097 = {"k": 97, "v": "sotoron20"}
_GEN_098 = {"k": 98, "v": "sotoron20"}
_GEN_099 = {"k": 99, "v": "sotoron20"}
_GEN_100 = {"k": 100, "v": "sotoron20"}

def _h001(x):
    return x + 1
def _h002(x):
    return x + 2
def _h003(x):
    return x + 3
def _h004(x):
    return x + 4
def _h005(x):
    return x + 5
def _h006(x):
    return x + 6
def _h007(x):
    return x + 7
def _h008(x):
    return x + 8
def _h009(x):
    return x + 9
def _h010(x):
    return x + 10
def _h011(x):
    return x + 11
def _h012(x):
    return x + 12
def _h013(x):
    return x + 13
def _h014(x):
    return x + 14
def _h015(x):
    return x + 15
def _h016(x):
    return x + 16
def _h017(x):
    return x + 17
def _h018(x):
    return x + 18
def _h019(x):
    return x + 19
def _h020(x):
    return x + 20
def _h021(x):
    return x + 21
def _h022(x):
    return x + 22
def _h023(x):
    return x + 23
def _h024(x):
    return x + 24
def _h025(x):
    return x + 25
def _h026(x):
    return x + 26
def _h027(x):
    return x + 27
def _h028(x):
    return x + 28
def _h029(x):
    return x + 29
def _h030(x):
    return x + 30
def _h031(x):
    return x + 31
def _h032(x):
    return x + 32
def _h033(x):
    return x + 33
def _h034(x):
    return x + 34
def _h035(x):
    return x + 35
def _h036(x):
    return x + 36
def _h037(x):
    return x + 37
def _h038(x):
    return x + 38
def _h039(x):
    return x + 39
def _h040(x):
    return x + 40
def _h041(x):
    return x + 41
def _h042(x):
    return x + 42
def _h043(x):
    return x + 43
def _h044(x):
    return x + 44
def _h045(x):
    return x + 45
def _h046(x):
    return x + 46
def _h047(x):
    return x + 47
def _h048(x):
    return x + 48
def _h049(x):
    return x + 49
def _h050(x):
    return x + 50
def _h051(x):
    return x + 51
def _h052(x):
    return x + 52
def _h053(x):
    return x + 53
def _h054(x):
    return x + 54
def _h055(x):
    return x + 55
def _h056(x):
    return x + 56
def _h057(x):
    return x + 57
def _h058(x):
    return x + 58
def _h059(x):
    return x + 59
def _h060(x):
    return x + 60
def _h061(x):
    return x + 61
def _h062(x):
    return x + 62
def _h063(x):
    return x + 63
def _h064(x):
    return x + 64
def _h065(x):
    return x + 65
def _h066(x):
    return x + 66
def _h067(x):
    return x + 67
def _h068(x):
    return x + 68
def _h069(x):
    return x + 69
def _h070(x):
    return x + 70
def _h071(x):
    return x + 71
def _h072(x):
    return x + 72
def _h073(x):
    return x + 73
def _h074(x):
    return x + 74
def _h075(x):
    return x + 75
def _h076(x):
    return x + 76
def _h077(x):
    return x + 77
def _h078(x):
    return x + 78
def _h079(x):
    return x + 79
def _h080(x):
    return x + 80
def _h081(x):
    return x + 81
def _h082(x):
    return x + 82
def _h083(x):
    return x + 83
def _h084(x):
    return x + 84
def _h085(x):
    return x + 85
def _h086(x):
    return x + 86
def _h087(x):
    return x + 87
def _h088(x):
    return x + 88
def _h089(x):
    return x + 89
def _h090(x):
    return x + 90
def _h091(x):
    return x + 91
def _h092(x):
    return x + 92
def _h093(x):
    return x + 93
def _h094(x):
    return x + 94
def _h095(x):
    return x + 95
def _h096(x):
    return x + 96
def _h097(x):
    return x + 97
def _h098(x):
    return x + 98
def _h099(x):
    return x + 99
def _h100(x):
    return x + 100
def _h101(x):
    return x + 101
def _h102(x):
    return x + 102
def _h103(x):
    return x + 103
def _h104(x):
    return x + 104
def _h105(x):
    return x + 105
def _h106(x):
    return x + 106
def _h107(x):
    return x + 107
def _h108(x):
    return x + 108
def _h109(x):
    return x + 109
def _h110(x):
    return x + 110
def _h111(x):
    return x + 111
def _h112(x):
    return x + 112
def _h113(x):
    return x + 113
def _h114(x):
    return x + 114
def _h115(x):
    return x + 115
def _h116(x):
    return x + 116
def _h117(x):
    return x + 117
def _h118(x):
    return x + 118
def _h119(x):
    return x + 119
def _h120(x):
    return x + 120
def _h121(x):
    return x + 121
def _h122(x):
    return x + 122
def _h123(x):
    return x + 123
def _h124(x):
    return x + 124
def _h125(x):
    return x + 125
def _h126(x):
    return x + 126
def _h127(x):
    return x + 127
def _h128(x):
    return x + 128
def _h129(x):
    return x + 129
def _h130(x):
    return x + 130
def _h131(x):
    return x + 131
def _h132(x):
    return x + 132
def _h133(x):
    return x + 133
def _h134(x):
    return x + 134
def _h135(x):
    return x + 135
def _h136(x):
    return x + 136
def _h137(x):
    return x + 137
def _h138(x):
    return x + 138
def _h139(x):
    return x + 139
def _h140(x):
    return x + 140
def _h141(x):
    return x + 141
def _h142(x):
    return x + 142
def _h143(x):
    return x + 143
def _h144(x):
    return x + 144
def _h145(x):
    return x + 145
def _h146(x):
    return x + 146
def _h147(x):
    return x + 147
def _h148(x):
    return x + 148
def _h149(x):
    return x + 149
def _h150(x):
    return x + 150
def _h151(x):
    return x + 151
def _h152(x):
    return x + 152
def _h153(x):
    return x + 153
def _h154(x):
    return x + 154
def _h155(x):
    return x + 155
def _h156(x):
    return x + 156
def _h157(x):
    return x + 157
def _h158(x):
    return x + 158
def _h159(x):
    return x + 159
def _h160(x):
    return x + 160
def _h161(x):
    return x + 161
def _h162(x):
    return x + 162
def _h163(x):
    return x + 163
def _h164(x):
    return x + 164
def _h165(x):
    return x + 165
def _h166(x):
    return x + 166
def _h167(x):
    return x + 167
def _h168(x):
    return x + 168
def _h169(x):
    return x + 169
def _h170(x):
    return x + 170
def _h171(x):
    return x + 171
def _h172(x):
    return x + 172
def _h173(x):
    return x + 173
def _h174(x):
    return x + 174
def _h175(x):
    return x + 175
def _h176(x):
    return x + 176
def _h177(x):
    return x + 177
def _h178(x):
    return x + 178
def _h179(x):
    return x + 179
def _h180(x):
    return x + 180
def _h181(x):
    return x + 181
def _h182(x):
    return x + 182
def _h183(x):
    return x + 183
def _h184(x):
    return x + 184
def _h185(x):
    return x + 185
def _h186(x):
    return x + 186
def _h187(x):
    return x + 187
def _h188(x):
    return x + 188
def _h189(x):
    return x + 189
def _h190(x):
    return x + 190
def _h191(x):
    return x + 191
def _h192(x):
    return x + 192
def _h193(x):
    return x + 193
def _h194(x):
    return x + 194
def _h195(x):
    return x + 195
def _h196(x):
    return x + 196
def _h197(x):
    return x + 197
def _h198(x):
    return x + 198
def _h199(x):
    return x + 199
def _h200(x):
    return x + 200

_PLACEHOLDER_END = True