# 2D assets for the AquaSentinel Creative Experience "A night on the Godavari".
# All PNG with transparency, 1920 x 1080 overlays or small UI pieces, in the finale deck's visual language.
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = r'C:\Users\dell\OneDrive\Desktop\AquaSentinel\10_VIRTUAL_STORYTELLER\02_CXP_2D_assets'
os.makedirs(OUT, exist_ok=True)
F = r'C:\Windows\Fonts'
TEAL, NAVY, RED, GREEN, AMBER, WHITE = (14, 124, 134), (9, 31, 46), (229, 56, 59), (43, 182, 115), (244, 180, 0), (255, 255, 255)


def font(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(F, name), size)
    if wght and name == 'bahnschrift.ttf':
        try:
            f.set_variation_by_axes([wght, 100])
        except Exception:
            pass
    return f


H1 = lambda s: font('bahnschrift.ttf', s, 600)
H2 = lambda s: font('bahnschrift.ttf', s, 400)
TX = lambda s: font('segoeui.ttf', s)
TXB = lambda s: font('seguisb.ttf', s)
EMO = lambda s: font('seguiemj.ttf', s)


def save(img, name):
    img.save(os.path.join(OUT, name)); print('wrote', name, img.size)


def rrect(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def glass(size, box, r=28, alpha=200, col=NAVY):
    """Dark translucent panel with a soft shadow."""
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    sh = Image.new('RGBA', size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle(
        [box[0] + 8, box[1] + 12, box[2] + 8, box[3] + 12], r, fill=(0, 0, 0, 110))
    layer = Image.alpha_composite(layer, sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(layer).rounded_rectangle(box, r, fill=col + (alpha,))
    return layer


W, H = 1920, 1080

# ---------- 00 title card (full frame, opaque gradient so it can also be a slide) ----------
img = Image.new('RGBA', (W, H))
d = ImageDraw.Draw(img)
for y in range(H):  # dusk sky -> river
    t = y / H
    c = tuple(int(a + (b - a) * t) for a, b in zip((22, 46, 78), (6, 64, 74)))
    d.line([(0, y), (W, y)], fill=c + (255,))
for i in range(14):  # river shimmer lines
    y = 760 + i * 22; d.line([(160 + i * 30, y), (W - 200 - i * 40, y)], fill=(120, 200, 210, 40 + i * 6), width=2)
d.ellipse([W - 420, 150, W - 300, 270], fill=(255, 214, 140, 255))  # setting sun / moon
d.text((160, 300), 'AquaSentinel', font=H1(150), fill=WHITE)
d.text((166, 470), 'A river that raises its own alarm.', font=H2(64), fill=(170, 230, 235))
d.text((166, 570), 'A night on the Godavari  ·  Kopargaon, Maharashtra', font=TX(38), fill=(220, 232, 240))
rrect(d, [166, 680, 560, 770], 45, GREEN + (255,)); d.text((215, 693), 'Start', font=H1(56), fill=WHITE); d.polygon([(400, 703), (400, 747), (440, 725)], fill=WHITE)
d.text((166, 960), 'Team Sanjivani Hero\'s Journey  ·  AAKRUTI 2026  ·  India Geo Finale', font=TX(30), fill=(190, 205, 215))
save(img, '00_title_card_1920x1080.png')

# ---------- 01-08 act banners (lower-left overlay, transparent) ----------
ACTS = [
    ('1', 'Dusk at the bridge', 'A float on a guide pole reads the river every 15 minutes.', GREEN),
    ('2', 'The river rises', 'No anchors, no motor: the river lifts it up to 2 m.', TEAL),
    ('3', '02:00 - a spill passes', 'Red in one cycle. The SMS goes out.  (illustration)', RED),
    ('4', 'It keeps the evidence', 'A sample of that water, bottled at the moment of the spill.', AMBER),
    ('5', 'Serviced from the bridge', 'The carriage gate opens; the sensor cartridge lifts out.', TEAL),
    ('6', 'Inside the sentinel', '66 parts, assembled and simulated in SOLIDWORKS.', TEAL),
    ('7', 'Proof on the table', 'Our 1:5 LIVE model, printed around the real sensors.', GREEN),
    ('8', 'See it life-size', 'Scan the code and place AquaSentinel in front of you.', TEAL),
]
for n, title, line, col in ACTS:
    img = glass((W, H), (70, 800, 1240, 1010), 30, 205)
    d = ImageDraw.Draw(img)
    rrect(d, [70, 800, 92, 1010], 8, col + (255,))
    d.ellipse([120, 830, 210, 920], fill=col + (255,))
    d.text((165, 875), n, font=H1(58), fill=WHITE, anchor='mm')
    d.text((240, 828), title, font=H1(64), fill=WHITE)
    d.text((242, 925), line, font=TX(36), fill=(205, 225, 235))
    save(img, f'0{n}_act_banner_{title.split(" -")[0].replace(" ", "_").replace(":", "")}.png')

# ---------- SMS alert card (phone) ----------
PW, PH = 760, 1240
img = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
rrect(d, [10, 10, PW - 10, PH - 10], 80, (20, 20, 24, 255), (70, 70, 80, 255), 6)
rrect(d, [40, 40, PW - 40, PH - 40], 60, (238, 242, 246, 255))
rrect(d, [PW // 2 - 90, 58, PW // 2 + 90, 92], 17, (20, 20, 24, 255))
d.text((80, 120), '02:07', font=H1(110), fill=NAVY)
d.text((84, 250), 'Friday, 20 November', font=TX(34), fill=(90, 100, 110))
rrect(d, [70, 330, PW - 70, 1040], 36, WHITE + (255,), (210, 216, 224, 255), 2)
d.ellipse([100, 360, 170, 430], fill=RED + (255,)); d.text((135, 395), '!', font=H1(52), fill=WHITE, anchor='mm')
d.text((190, 362), 'AquaSentinel  ·  SMS', font=TXB(32), fill=NAVY)
d.text((190, 402), 'now', font=TX(26), fill=(120, 130, 140))
msg = [('ALERT - Godavari, Kopargaon bridge', TXB(34), RED),
       ('Event: INDUSTRIAL DISCHARGE', TXB(32), NAVY),
       ('pH 9.4   ·   dissolved solids 1,850 ppm', TX(30), NAVY),
       ('2 of 3 readings out of range', TX(30), NAVY),
       ('Beacon: RED', TX(30), NAVY),
       ('Sample bottle sealed at 02:06', TX(30), NAVY),
       ('Action: check the water-works intake', TX(30), NAVY)]
y = 470
for t, f, c in msg:
    d.text((100, y), t, font=f, fill=c); y += 62 if f.size > 31 else 54
d.text((100, 960), 'Illustration of the alert the officer receives', font=TX(24), fill=(140, 140, 150))
d.text((PW // 2, 1120), 'Swipe to open', font=TX(28), fill=(110, 120, 130), anchor='mm')
save(img, '10_sms_alert_phone_760x1240.png')

# ---------- status chips ----------
for name, txt, col in (('11_status_NORMAL', 'NORMAL  ·  water OK', GREEN), ('12_status_ALERT', 'ALERT  ·  spill detected', RED),
                       ('13_tag_illustration', 'illustration', (110, 110, 120)), ('14_status_SAMPLING', 'SAMPLING  ·  bottle 1', AMBER)):
    f = H1(44) if 'tag' not in name else TX(32)
    w = int(d.textlength(txt, font=f)) + (110 if 'tag' not in name else 50)
    img = Image.new('RGBA', (w, 90 if 'tag' not in name else 60), (0, 0, 0, 0)); d2 = ImageDraw.Draw(img)
    rrect(d2, [0, 0, w - 1, img.height - 1], img.height // 2, col + (235,))
    if 'tag' not in name:
        d2.ellipse([24, 30, 54, 60], fill=WHITE); d2.text((74, 45), txt, font=f, fill=WHITE, anchor='lm')
    else:
        d2.text((w // 2, 30), txt, font=f, fill=WHITE, anchor='mm')
    save(img, name + '.png')

# ---------- river level gauge ----------
GW, GH = 300, 760
img = glass((GW + 40, GH + 40), (10, 10, GW, GH), 24, 190); d = ImageDraw.Draw(img)
d.text((GW // 2 + 5, 50), 'RIVER LEVEL', font=TXB(30), fill=WHITE, anchor='mm')
x0, y0, y1 = 110, 110, GH - 60
d.rectangle([x0, y0, x0 + 40, y1], fill=(255, 255, 255, 40))
d.rectangle([x0, y0 + (y1 - y0) * 0.15, x0 + 40, y1], fill=TEAL + (230,))
for i, lab in enumerate(['+2.0 m', '+1.5', '+1.0', '+0.5', '0']):
    yy = y0 + (y1 - y0) * (0.15 + 0.2125 * i)
    d.line([(x0 + 44, yy), (x0 + 70, yy)], fill=WHITE, width=3)
    d.text((x0 + 80, yy), lab, font=TX(30), fill=WHITE, anchor='lm')
save(img, '15_river_level_gauge.png')

# ---------- buttons ----------
BTN = [('Start', '▶️', GREEN), ('Rise', '⬆️', TEAL), ('Spill', '⚠️', RED), ('Sample', '🧪', AMBER), ('Service', '🔧', TEAL),
       ('Inside', '🔍', TEAL), ('Model', '🔄', GREEN), ('Restart', '🔁', (90, 100, 115))]
for i, (lab, ic, col) in enumerate(BTN, 1):
    img = Image.new('RGBA', (360, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, [0, 0, 359, 109], 55, col + (240,), WHITE + (255,), 4)
    try:
        d.text((62, 55), ic, font=EMO(46), fill=WHITE, anchor='mm', embedded_color=True)
    except Exception:
        d.text((62, 55), ic, font=TXB(46), fill=WHITE, anchor='mm')
    d.text((112, 55), lab, font=H1(50), fill=WHITE, anchor='lm')
    save(img, f'2{i}_button_{lab}.png')

# ---------- exploded-view callouts ----------
CALL = [('Pontoon hulls', 'roto-moulded PE, foam-filled; 143 mm freeboard'),
        ('Guide carriage', '8 rollers ride the pole; gate opens for service'),
        ('Sensor well + cartridge', 'pH · dissolved solids · turbidity · water temp.'),
        ('Power + control pod', 'Raspberry Pi decides on board, no cloud'),
        ('Autosampler', 'bottles the water at the moment of the spill'),
        ('Beacon', 'green = normal, red = spill, seen from the bank'),
        ('Solar canopy', 'charges the battery, shades the pod')]
for i, (t, s) in enumerate(CALL, 1):
    img = glass((900, 190), (10, 10, 860, 160), 22, 215); d = ImageDraw.Draw(img)
    rrect(d, [10, 10, 26, 160], 6, AMBER + (255,))
    d.text((50, 30), t, font=H1(50), fill=WHITE)
    d.text((52, 100), s, font=TX(30), fill=(205, 225, 235))
    save(img, f'3{i}_callout_{t.split(" ")[0]}.png')

# ---------- outro card with a QR slot ----------
img = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H; c = tuple(int(a + (b - a) * t) for a, b in zip((6, 64, 74), (9, 31, 46))); d.line([(0, y), (W, y)], fill=c + (255,))
d.text((160, 220), 'See it life-size.', font=H1(120), fill=WHITE)
d.text((166, 380), 'Scan the code with your phone camera and place\nAquaSentinel on the table in front of you.', font=TX(44), fill=(205, 230, 235), spacing=14)
rrect(d, [1260, 220, 1760, 720], 30, WHITE + (255,)); d.text((1510, 470), 'QR code\n(added after the\nhosting decision)', font=TX(36), fill=(150, 150, 160), anchor='mm', align='center')
d.text((166, 860), 'AquaSentinel  ·  Team Sanjivani Hero\'s Journey  ·  AAKRUTI 2026', font=TX(32), fill=(190, 205, 215))
save(img, '40_outro_AR_card_1920x1080.png')
