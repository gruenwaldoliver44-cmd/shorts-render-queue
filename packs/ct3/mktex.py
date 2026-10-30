from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random, numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/tex')
def F(p, s): return ImageFont.truetype(p, s)
def ct(d, y, t, f, fill, W, x0=0):
    w = d.textlength(t, font=f); d.text((x0 + (W - w) / 2, y), t, font=f, fill=fill)
# 1 warranty sticker: silver holographic, small print, printed border
W, H = 1200, 400
base = np.zeros((H, W, 3), np.float32)
xx, yy = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
for c, ph in enumerate((0, 2.1, 4.2)):
    base[..., c] = 0.80 + 0.035 * np.sin(18 * xx + 9 * yy + ph) + 0.02 * np.sin(55 * xx - 30 * yy + ph) + 0.06 * np.sin(7 * xx)
im = Image.fromarray((np.clip(base, 0, 1) * 255).astype('uint8')); d = ImageDraw.Draw(im)
d.rectangle([10, 10, W - 10, H - 10], outline=(60, 60, 70), width=6)
ct(d, 70, 'WARRANTY VOID', F('Inter800.ttf', 118), (25, 25, 30), W)
ct(d, 220, 'IF REMOVED', F('Inter800.ttf', 110), (25, 25, 30), W)
for k in range(9):
    d.line([(60 + k * 125, 370), (110 + k * 125, 370)], fill=(80, 80, 90), width=3)
im.save('sticker.png')
# sticker back (white adhesive)
Image.new('RGB', (600, 200), (225, 225, 220)).save('sticker_back.png')
# 2 warranty booklet page
W, H = 1240, 1754; im = Image.new('RGB', (W, H), (246, 244, 238)); d = ImageDraw.Draw(im)
d.text((110, 120), 'LIMITED WARRANTY', font=F('Inter800.ttf', 80), fill=(20, 20, 24))
d.text((110, 230), 'Consumer rights under federal law', font=F('Inter500.ttf', 40), fill=(80, 80, 88))
rnd = random.Random(3)
y = 340
for blk in range(9):
    for ln in range(5):
        wl = rnd.randint(700, 1020); d.rectangle([110, y, 110 + wl, y + 16], fill=(150, 150, 158)); y += 34
    y += 30
d.rectangle([100, 1180, 1140, 1300], fill=(255, 236, 120))
d.text((120, 1200), 'Magnuson-Moss Warranty Act', font=F('Inter800.ttf', 54), fill=(20, 20, 24))
d.text((120, 1262), 'Enacted 1975 · 15 U.S.C. § 2302(c)', font=F('Inter500.ttf', 30), fill=(60, 60, 66))
im.save('booklet.png')
# 3 FTC letters with addressee
for name in ('SONY', 'MICROSOFT', 'NINTENDO', 'HYUNDAI'):
    W, H = 1240, 1754; im = Image.new('RGB', (W, H), (250, 250, 247)); d = ImageDraw.Draw(im)
    d.ellipse([100, 100, 260, 260], outline=(30, 50, 90), width=8); ct(d, 160, 'FTC', F('Inter800.ttf', 50), (30, 50, 90), 160, 100)
    d.text((300, 120), 'FEDERAL TRADE COMMISSION', font=F('Inter800.ttf', 54), fill=(30, 50, 90))
    d.text((300, 190), 'Washington, D.C. · April 2018', font=F('Inter500.ttf', 34), fill=(90, 90, 100))
    d.text((110, 360), 'TO:', font=F('Inter700.ttf', 44), fill=(90, 90, 100))
    d.text((110, 420), name, font=F('Inter800.ttf', 190), fill=(15, 15, 20))
    d.text((110, 680), 'WARNING LETTER', font=F('Inter800.ttf', 70), fill=(190, 30, 40))
    rnd = random.Random(len(name)); y = 820
    for ln in range(16):
        wl = rnd.randint(750, 1020); d.rectangle([110, y, 110 + wl, y + 16], fill=(160, 160, 168)); y += 40
    d.text((110, 1560), 'RECREATION · NOT THE ORIGINAL DOCUMENT', font=F('Mono500.ttf', 28), fill=(140, 140, 150))
    im.save('letter_%s.png' % name.lower())
# 4 receipt
W, H = 600, 1500; im = Image.new('RGB', (W, H), (250, 250, 246)); d = ImageDraw.Draw(im)
ct(d, 50, "JOE'S AUTO REPAIR", F('Mono700.ttf', 44), (20, 20, 20), W)
ct(d, 110, 'INDEPENDENT SHOP', F('Mono500.ttf', 30), (60, 60, 60), W)
rows = [('OIL CHANGE', '39.99'), ('5W-30 SYNTH 5QT', 'incl.'), ('OIL FILTER', 'incl.'), ('', ''), ('TOTAL', '$39.99')]
y = 230
for a, b in rows:
    d.text((40, y), a, font=F('Mono700.ttf', 36), fill=(20, 20, 20)); w = d.textlength(b, font=F('Mono700.ttf', 36)); d.text((W - 40 - w, y), b, font=F('Mono700.ttf', 36), fill=(20, 20, 20)); y += 70
d.text((40, y + 20), 'MILEAGE 48,215', font=F('Mono500.ttf', 30), fill=(60, 60, 60))
d.text((40, y + 70), 'DATE 10/30', font=F('Mono500.ttf', 30), fill=(60, 60, 60))
for k in range(40): d.rectangle([40 + k * 13, 1300, 40 + k * 13 + (6 if k % 3 else 10), 1420], fill=(20, 20, 20))
im.save('receipt.png')
# 5 dealer invoice
W, H = 1240, 1754; im = Image.new('RGB', (W, H), (248, 248, 250)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, W, 180], fill=(18, 28, 48)); d.text((80, 50), 'DEALER SERVICE CENTER', font=F('Inter800.ttf', 64), fill=(255, 255, 255))
d.text((80, 260), 'REPAIR ORDER', font=F('Inter700.ttf', 48), fill=(40, 40, 50))
rows = [('Oil & filter change', '$89.95'), ('Multi-point inspection', '$29.00'), ('Shop supplies', '$11.00')]
y = 400
for a, b in rows:
    d.text((80, y), a, font=F('Inter500.ttf', 50), fill=(30, 30, 36)); w = d.textlength(b, font=F('Inter700.ttf', 50)); d.text((W - 80 - w, y), b, font=F('Inter700.ttf', 50), fill=(30, 30, 36)); y += 110
d.line([(80, y + 20), (W - 80, y + 20)], fill=(40, 40, 50), width=4)
d.text((80, y + 60), 'TOTAL', font=F('Inter800.ttf', 80), fill=(20, 20, 24)); w = d.textlength('$129.95', font=F('Inter800.ttf', 110)); d.text((W - 80 - w, y + 40), '$129.95', font=F('Inter800.ttf', 110), fill=(190, 30, 40))
im.save('invoice.png')
# 6 stamp imprint HONORED (alpha)
im = Image.new('RGBA', (1000, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle([14, 14, 986, 346], 30, outline=(30, 140, 70, 235), width=24); ct(d, 70, 'HONORED', F('Inter800.ttf', 190), (30, 140, 70, 235), 1000)
im = im.filter(ImageFilter.GaussianBlur(1.2)); im.save('stamp_honored.png')
print('tex ok')
