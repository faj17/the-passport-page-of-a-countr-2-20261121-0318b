#!/usr/bin/env python3
"""Build entry.png: an invented passport spread for the Republic of Zembla.

Draws a two-page open passport spread with PIL: a data page (portrait,
personal data, MRZ with correct check digits) and a visa page (one Talveria
visa plus entry/exit stamps from neighbouring Karvostan and Talveria).
All dates are mutually consistent: issued 12 JUN 2023, travel Sep 2024 and
Mar 2025, expiry 11 JUN 2033. Run: python3 generate.py -> entry.png
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FDIR = "/usr/share/fonts/truetype/dejavu"

def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
MONO = "DejaVuSansMono.ttf"
MONO_B = "DejaVuSansMono-Bold.ttf"

W, H = 1024, 724
NAVY = (31, 58, 95)
NAVY_D = (20, 38, 64)
INK = (28, 32, 40)
GREY = (110, 116, 124)
PAGE = (246, 241, 228)
PAGE_R = (238, 232, 216)
GOLD = (176, 141, 58)
RED = (138, 47, 43)

# ---------------------------------------------------------------- MRZ
def check_digit(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[ch] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)

def mrz_lines():
    line1 = ("P<ZMB" + "VOSS<<ELENA<MARA").ljust(44, "<")
    doc = "ZM4829137"
    dob = "940314"
    exp = "330611"
    pers = "<" * 14
    body = (doc + check_digit(doc) + "ZMB" + dob + check_digit(dob) + "F"
            + exp + check_digit(exp) + pers + check_digit(pers))
    line2 = body + check_digit(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2

# ---------------------------------------------------------------- helpers
def spaced(draw, xy, text, fnt, fill, tracking=2):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x

def center(draw, cx, y, text, fnt, fill, tracking=0):
    if tracking:
        w = sum(draw.textlength(c, font=fnt) + tracking for c in text) - tracking
        x = cx - w / 2
        for ch in text:
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += draw.textlength(ch, font=fnt) + tracking
    else:
        w = draw.textlength(text, font=fnt)
        draw.text((cx - w / 2, y), text, font=fnt, fill=fill)

def guilloche(draw, box, color, step=9):
    x0, y0, x1, y1 = box
    for k in range(0, (y1 - y0) // step + 1):
        yb = y0 + k * step
        pts = []
        for x in range(x0, x1 + 1, 6):
            pts.append((x, yb + 3.5 * math.sin((x - x0) / 34.0 + k * 0.9)))
        draw.line(pts, fill=color, width=1)

def coat_of_arms(draw, cx, cy, r):
    """Gold shield with a kestrel silhouette on a navy disc."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY, outline=GOLD, width=2)
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
                 outline=GOLD, width=1)
    # shield
    s = r * 0.62
    shield = [(cx - s, cy - s * 0.55), (cx + s, cy - s * 0.55),
              (cx + s, cy + s * 0.25),
              (cx, cy + s * 0.95), (cx - s, cy + s * 0.25)]
    draw.polygon(shield, fill=(232, 214, 150), outline=GOLD)
    # kestrel: body + raised wing + head, in navy
    draw.polygon([(cx - 2, cy - s * 0.28), (cx + s * 0.52, cy - s * 0.62),
                  (cx + s * 0.30, cy - s * 0.05), (cx + s * 0.42, cy + s * 0.30),
                  (cx + s * 0.05, cy + s * 0.42), (cx - s * 0.28, cy + s * 0.30),
                  (cx - s * 0.34, cy - s * 0.05)], fill=NAVY_D)
    draw.ellipse([cx + s * 0.30, cy - s * 0.42, cx + s * 0.52, cy - s * 0.20],
                 fill=NAVY_D)
    # crown above shield
    draw.polygon([(cx - s * 0.55, cy - s * 0.62), (cx - s * 0.28, cy - s * 0.95),
                  (cx, cy - s * 0.68), (cx + s * 0.28, cy - s * 0.95),
                  (cx + s * 0.55, cy - s * 0.62)], fill=GOLD)

def portrait(draw, box):
    """Stylised flat ID portrait of a woman, dark hair, navy jacket."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # backdrop: pale blue-grey gradient bands
    for i in range(h):
        t = i / h
        c = tuple(int(168 + (196 - 168) * t) for _ in range(3))
        c = (c[0], c[1] + 6, min(255, c[2] + 18))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)
    cx = (x0 + x1) / 2
    skin = (232, 184, 141)
    skin_d = (214, 164, 122)
    hair = (58, 40, 30)
    # shoulders / jacket
    draw.polygon([(x0 + 8, y1), (x0 + 34, y0 + h * 0.74),
                  (cx - 26, y0 + h * 0.70), (cx + 26, y0 + h * 0.70),
                  (x1 - 34, y0 + h * 0.74), (x1 - 8, y1)],
                 fill=(38, 52, 84))
    draw.polygon([(cx - 26, y0 + h * 0.70), (cx, y0 + h * 0.80),
                  (cx + 26, y0 + h * 0.70), (cx + 14, y0 + h * 0.66),
                  (cx - 14, y0 + h * 0.66)], fill=(240, 238, 230))
    # neck
    draw.rectangle([cx - 13, y0 + h * 0.58, cx + 13, y0 + h * 0.72], fill=skin_d)
    # hair mass behind the face (bob to the shoulders)
    draw.ellipse([cx - 34, y0 + h * 0.04, cx + 34, y0 + h * 0.70], fill=hair)
    # neck again, in front of the hair so skin shows below the chin
    draw.rectangle([cx - 13, y0 + h * 0.58, cx + 13, y0 + h * 0.72], fill=skin_d)
    # face
    draw.ellipse([cx - 29, y0 + h * 0.16, cx + 29, y0 + h * 0.62], fill=skin)
    # side wedges of hair framing the face (centre-parted bob)
    draw.polygon([(cx - 30, y0 + h * 0.16), (cx - 21, y0 + h * 0.16),
                  (cx - 25, y0 + h * 0.46), (cx - 30, y0 + h * 0.52)], fill=hair)
    draw.polygon([(cx + 30, y0 + h * 0.16), (cx + 21, y0 + h * 0.16),
                  (cx + 25, y0 + h * 0.46), (cx + 30, y0 + h * 0.52)], fill=hair)
    # ears
    draw.ellipse([cx - 34, y0 + h * 0.32, cx - 28, y0 + h * 0.46], fill=skin)
    draw.ellipse([cx + 28, y0 + h * 0.32, cx + 34, y0 + h * 0.46], fill=skin)
    # eyebrows
    draw.arc([cx - 22, y0 + h * 0.30, cx - 6, y0 + h * 0.38], 200, 340,
             fill=(70, 48, 36), width=2)
    draw.arc([cx + 6, y0 + h * 0.30, cx + 22, y0 + h * 0.38], 200, 340,
             fill=(70, 48, 36), width=2)
    # eyes
    for ex in (cx - 14, cx + 14):
        draw.ellipse([ex - 6, y0 + h * 0.38, ex + 6, y0 + h * 0.425],
                     fill=(250, 250, 248), outline=(90, 70, 55))
        draw.ellipse([ex - 3, y0 + h * 0.39, ex + 3, y0 + h * 0.42],
                     fill=(46, 32, 24))
    # nose
    draw.line([(cx, y0 + h * 0.43), (cx - 2, y0 + h * 0.50), (cx + 3, y0 + h * 0.51)],
              fill=(198, 148, 108), width=2)
    # lips
    draw.polygon([(cx - 9, y0 + h * 0.55), (cx + 9, y0 + h * 0.55),
                  (cx + 6, y0 + h * 0.575), (cx - 6, y0 + h * 0.575)],
                 fill=(176, 96, 88))
    draw.line([(cx - 9, y0 + h * 0.555), (cx + 9, y0 + h * 0.555)],
              fill=(140, 70, 64), width=1)
    # laminate shine
    shine = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    sd.polygon([(w * 0.15, 0), (w * 0.45, 0), (w * 0.05, h), (-w * 0.25, h)],
               fill=(255, 255, 255, 26))
    return shine

def stamp_layer(size, draw_fn, angle):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, size)
    return layer.rotate(angle, resample=Image.BICUBIC, expand=True)

def rect_stamp(d, size, color, lines, title_size=15, sub_size=11):
    w, h = size
    d.rounded_rectangle([4, 4, w - 5, h - 5], radius=8, outline=color, width=3)
    d.rounded_rectangle([9, 9, w - 10, h - 10], radius=5, outline=color, width=1)
    y = 12
    for i, (txt, fnt, sz) in enumerate(lines):
        f = font(SANS_B if i == 1 else SANS, sz)
        center(d, w / 2, y, txt, f, color)
        y += sz + 4

def round_stamp(d, size, color, top, mid, bottom, date):
    w, h = size
    cx, cy = w / 2, h / 2
    d.ellipse([4, 4, w - 5, h - 5], outline=color, width=3)
    d.ellipse([12, 12, w - 13, h - 13], outline=color, width=1)
    f1 = font(SANS_B, 13)
    f2 = font(SANS_B, 16)
    f3 = font(SANS, 9)
    center(d, cx, 22, top, f1, color)
    center(d, cx, 46, mid, f2, color)
    center(d, cx, 74, date, font(MONO_B, 14), color)
    center(d, cx, 93, bottom, f3, color)
    # stars
    for sx in (cx - 34, cx + 34):
        d.text((sx - 4, 52), "*", font=font(SANS_B, 16), fill=color)

# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), (35, 39, 45))
    # desk mat
    d0 = ImageDraw.Draw(img)
    d0.rectangle([10, 8, W - 10, H - 8], fill=(44, 49, 56))
    # page shadows
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rectangle([34, 30, 506, 710], fill=(0, 0, 0, 140))
    sd.rectangle([530, 30, 1002, 710], fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))

    # ---- left page: data page
    pg = Image.new("RGB", (472, 680), PAGE)
    d = ImageDraw.Draw(pg)
    guilloche(d, (14, 200, 458, 600), (214, 222, 234))
    d.rectangle([10, 10, 461, 669], outline=NAVY, width=2)
    d.rectangle([15, 15, 456, 664], outline=(150, 158, 170), width=1)
    coat_of_arms(d, 236, 62, 34)
    center(d, 236, 104, "REPUBLIC OF ZEMBLA", font(SERIF_B, 25), NAVY)
    center(d, 236, 134, "PASSPORT", font(SERIF_B, 30), NAVY_D, tracking=6)
    center(d, 236, 168, "PASSEPORT", font(SANS, 11), GREY, tracking=4)
    d.line([(60, 192), (412, 192)], fill=NAVY, width=1)
    d.line([(60, 195), (412, 195)], fill=GOLD, width=1)

    # photo
    px0, py0, px1, py1 = 34, 210, 184, 400
    d.rectangle([px0 - 3, py0 - 3, px1 + 3, py1 + 3], outline=NAVY, width=2)
    photo = Image.new("RGB", (px1 - px0, py1 - py0), (180, 190, 205))
    pd = ImageDraw.Draw(photo)
    shine = portrait(pd, (0, 0, px1 - px0, py1 - py0))
    photo.paste(Image.alpha_composite(photo.convert("RGBA"), shine).convert("RGB"), (0, 0))
    pg.paste(photo, (px0, py0))

    # data fields
    fx = 202
    def field(y, label, value, value_x=None, value_font=None):
        d.text((fx, y), label, font=font(SANS, 9), fill=GREY)
        d.text((value_x or fx, y + 12), value,
               font=value_font or font(SANS_B, 15), fill=INK)
    field(210, "TYPE / CODE / No.", "")
    d.text((fx, 222), "P", font=font(SANS_B, 15), fill=INK)
    d.text((fx + 34, 222), "ZMB", font=font(SANS_B, 15), fill=INK)
    d.text((fx + 92, 222), "ZM4829137", font=font(SANS_B, 15), fill=INK)
    field(248, "SURNAME / NOM", "VOSS")
    field(286, "GIVEN NAMES / PRÉNOMS", "ELENA MARA")
    field(324, "NATIONALITY / NATIONALITÉ", "ZEMBLAN")
    field(362, "DATE OF BIRTH", "14 MAR 1994")
    d.text((fx + 150, 362), "SEX", font=font(SANS, 9), fill=GREY)
    d.text((fx + 150, 374), "F", font=font(SANS_B, 15), fill=INK)
    field(400, "PLACE OF BIRTH", "ONHAVA, ZEMBLA")
    field(438, "DATE OF ISSUE", "12 JUN 2023")
    d.text((fx + 150, 438), "EXPIRY", font=font(SANS, 9), fill=GREY)
    d.text((fx + 150, 450), "11 JUN 2033", font=font(SANS_B, 15), fill=INK)
    field(476, "AUTHORITY", "MINISTRY OF THE INTERIOR — ONHAVA",
          value_font=font(SANS_B, 12))

    # endorsement
    d.rounded_rectangle([34, 516, 438, 556], radius=3, outline=RED, width=1)
    d.text((44, 523), "ENDORSEMENT:", font=font(SANS_B, 10), fill=RED)
    d.text((44, 537), "NOT VALID FOR TRAVEL TO THE OSTLAND PROTECTORATE",
           font=font(SANS_B, 10), fill=RED)
    # signature
    sig = Image.new("RGBA", (180, 34), (0, 0, 0, 0))
    sdd = ImageDraw.Draw(sig)
    pts = [(4, 24), (22, 8), (40, 22), (58, 6), (76, 20), (96, 10),
           (112, 22), (128, 8), (146, 20), (162, 12), (176, 20)]
    sdd.line(pts, fill=(30, 40, 90, 230), width=2, joint="curve")
    sdd.line([(10, 26), (170, 26)], fill=(30, 40, 90, 180), width=1)
    pg.paste(Image.alpha_composite(pg.convert("RGBA"), Image.new("RGBA", pg.size, (0, 0, 0, 0))).convert("RGB"), (0, 0))
    pg.paste(sig, (34, 566), sig)
    d.text((34, 600), "HOLDER'S SIGNATURE", font=font(SANS, 8), fill=GREY)
    d.text((400, 600), "2", font=font(SANS, 10), fill=GREY)

    # MRZ strip
    d.rectangle([24, 618, 448, 662], fill=(232, 228, 216))
    l1, l2 = mrz_lines()
    d.text((30, 624), l1, font=font(MONO, 15), fill=INK)
    d.text((30, 644), l2, font=font(MONO, 15), fill=INK)
    img.paste(pg, (28, 22))

    # ---- right page: visas
    pg2 = Image.new("RGB", (472, 680), PAGE_R)
    d2 = ImageDraw.Draw(pg2)
    # faint watermark shield
    wm = Image.new("RGBA", pg2.size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.ellipse([236 - 110, 300, 236 + 110, 520], outline=(31, 58, 95, 26), width=3)
    wd.polygon([(236 - 62, 330), (236 + 62, 330), (236 + 62, 400),
                (236, 470), (236 - 62, 400)], outline=(31, 58, 95, 26))
    pg2.paste(Image.alpha_composite(pg2.convert("RGBA"), wm).convert("RGB"), (0, 0))
    d2 = ImageDraw.Draw(pg2)
    d2.rectangle([10, 10, 461, 669], outline=NAVY, width=2)
    d2.rectangle([15, 15, 456, 664], outline=(150, 158, 170), width=1)
    center(d2, 236, 30, "VISAS", font(SERIF_B, 24), NAVY, tracking=4)
    center(d2, 236, 60, "VISA — VISA", font(SANS, 10), GREY, tracking=3)
    d2.text((428, 30), "5", font=font(SANS, 10), fill=GREY)
    d2.line([(60, 84), (412, 84)], fill=NAVY, width=1)

    # visa sticker
    vx0, vy0, vx1, vy1 = 34, 100, 438, 246
    d2.rectangle([vx0, vy0, vx1, vy1], fill=(250, 247, 238), outline=NAVY, width=2)
    d2.rectangle([vx0, vy0, vx1, vy0 + 30], fill=NAVY)
    d2.text((vx0 + 12, vy0 + 7), "VISA — TALVERIA", font=font(SANS_B, 14), fill=(245, 242, 230))
    d2.text((vx1 - 128, vy0 + 9), "No. TV-2025-011847", font=font(MONO, 10), fill=(200, 208, 220))
    vrows = [("TYPE", "SINGLE ENTRY", "VALID FROM", "01 MAR 2025"),
             ("ENTRIES", "1", "VALID UNTIL", "31 MAR 2025"),
             ("ISSUED AT", "ONHAVA, 18 FEB 2025", "STAY", "30 DAYS")]
    vy = vy0 + 42
    for a, av, b, bv in vrows:
        d2.text((vx0 + 12, vy), a, font=font(SANS, 9), fill=GREY)
        d2.text((vx0 + 12, vy + 11), av, font=font(SANS_B, 12), fill=INK)
        d2.text((vx0 + 218, vy), b, font=font(SANS, 9), fill=GREY)
        d2.text((vx0 + 218, vy + 11), bv, font=font(SANS_B, 12), fill=INK)
        vy += 30
    d2.text((vx0 + 12, vy + 2), "REMARKS:  EMPLOYMENT PROHIBITED",
            font=font(SANS_B, 11), fill=RED)
    # fee stamp overlapping the visa
    fee = stamp_layer((140, 64), lambda dd, sz: rect_stamp(
        dd, sz, (138, 47, 43, 220),
        [("CONSULAR FEE", None, 11), ("40 KR — PAID", None, 13),
         ("18 FEB 2025", None, 10)]), -8)
    pg2.paste(fee, (322, 216), fee)

    # stamps
    def paste_stamp(layer, pos):
        pg2.paste(layer, pos, layer)

    s1 = stamp_layer((190, 92), lambda dd, sz: rect_stamp(
        dd, sz, (43, 76, 155, 215),
        [("KARVOSTAN", None, 15), ("ARRIVAL", None, 14),
         ("03 SEP 2024", None, 12), ("DRAVEN • BORDER POST", None, 10)]), -7)
    paste_stamp(s1, (36, 272))
    s2 = stamp_layer((190, 92), lambda dd, sz: rect_stamp(
        dd, sz, (43, 76, 155, 215),
        [("KARVOSTAN", None, 15), ("DEPARTURE", None, 14),
         ("17 SEP 2024", None, 12), ("DRAVEN • BORDER POST", None, 10)]), 6)
    paste_stamp(s2, (246, 282))
    s3 = stamp_layer((132, 132), lambda dd, sz: round_stamp(
        dd, sz, (107, 63, 160, 215), "TALVERIA", "ARRIVAL", "KARVOS AIRPORT",
        "02 MAR 2025"), -10)
    paste_stamp(s3, (44, 396))
    s4 = stamp_layer((132, 132), lambda dd, sz: round_stamp(
        dd, sz, (107, 63, 160, 215), "TALVERIA", "DEPARTURE", "KARVOS AIRPORT",
        "21 MAR 2025"), 8)
    paste_stamp(s4, (196, 408))
    s5 = stamp_layer((132, 132), lambda dd, sz: round_stamp(
        dd, sz, (46, 107, 79, 215), "ZEMBLA", "ARRIVAL", "ONHAVA AIRPORT",
        "21 MAR 2025"), -4)
    paste_stamp(s5, (330, 396))
    s6 = stamp_layer((200, 66), lambda dd, sz: rect_stamp(
        dd, sz, (120, 90, 60, 215),
        [("REGISTERED — ONHAVA POLICE", None, 10),
         ("22 MAR 2025", None, 12),
         ("RESIDENCE 90 DAYS", None, 9)]), 3)
    paste_stamp(s6, (52, 556))
    d2.text((330, 640), "32 PAGES", font=font(SANS, 8), fill=GREY)
    img.paste(pg2, (524, 22))

    # gutter shadow
    gs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gs)
    gd.rectangle([508, 22, 524, 702], fill=(0, 0, 0, 70))
    gs = gs.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img.convert("RGBA"), gs).convert("RGB")

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} {img.size} {os.path.getsize(out)} bytes")
    return out

if __name__ == "__main__":
    build()
