from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/tex')
def F(p, s): return ImageFont.truetype(p, s)
def ct(d, y, t, f, fill, W, x0=0):
    w = d.textlength(t, font=f); d.text((x0 + (W - w) / 2, y), t, font=f, fill=fill)
# reel strip: 8 symbols stacked vertically, symbol 0 = red 7
syms = [('7', (230, 30, 40)), ('BAR', (30, 30, 30)), ('7', (230, 30, 40)), ('$', (20, 140, 60)), ('BAR', (30, 30, 30)), ('7', (230, 30, 40)), ('*', (230, 170, 20)), ('$', (20, 140, 60))]
W, Hs = 400, 400; im = Image.new('RGB', (W, Hs * len(syms)), (245, 240, 228)); d = ImageDraw.Draw(im)
for i, (s, c) in enumerate(syms):
    y = i * Hs; d.line([(0, y), (W, y)], fill=(200, 190, 170), width=6)
    f = F('Inter800.ttf', 260 if s != 'BAR' else 140)
    if s == 'BAR':
        d.rounded_rectangle([60, y + 130, 340, y + 270], 20, fill=c); ct(d, y + 140, 'BAR', f, (245, 240, 228), W)
    else: ct(d, y + 40, s, f, c, W)
im.save('reel.png')
# phone screens
def phone(name, lines, rec=False, buzz=False):
    W, H = 1179, 2556; im = Image.new('RGB', (W, H), (8, 8, 12)); d = ImageDraw.Draw(im)
    if rec:
        d.rectangle([0, 0, W, H], fill=(20, 18, 24)); d.ellipse([80, 160, 150, 230], fill=(235, 40, 50)); d.text((180, 150), 'REC  00:41', font=F('Inter700.ttf', 70), fill=(255, 255, 255))
        for k in range(3):
            x = 120 + k * 330; d.rounded_rectangle([x, 900, x + 280, 1500], 30, fill=(245, 240, 228)); ct(d, 1050, '7', F('Inter800.ttf', 300), (230, 30, 40), 280, x)
        d.rounded_rectangle([100, 2100, W - 100, 2300], 60, fill=(40, 120, 255)); ct(d, 2150, 'Uploading…', F('Inter700.ttf', 80), (255, 255, 255), W)
    else:
        ct(d, 260, '21:47', F('Inter700.ttf', 260), (255, 255, 255), W)
        y = 800
        for t in lines:
            d.rounded_rectangle([70, y, W - 70, y + 220], 50, fill=(40, 40, 52)); d.text((130, y + 30), 'PRESS', font=F('Mono700.ttf', 60), fill=(255, 210, 80)); d.text((130, y + 110), t, font=F('Mono700.ttf', 80), fill=(255, 255, 255)); y += 260
    im.save(name)
phone('scr_lock.png', ['in 0.25 s'])
phone('scr_rec.png', [], rec=True)
phone('scr_times.png', ['+00:03.412', '+00:07.905', '+00:12.388', '+00:16.871'])
# monitor graph (St Petersburg analysis)
W, H = 1920, 1080; im = Image.new('RGB', (W, H), (10, 14, 22)); d = ImageDraw.Draw(im)
for x in range(0, W, 80): d.line([(x, 0), (x, H)], fill=(24, 30, 44))
for y in range(0, H, 80): d.line([(0, y), (W, y)], fill=(24, 30, 44))
rnd = random.Random(4); pts = [(x, 540 + int(300 * __import__('math').sin(x / 140.0) * __import__('math').cos(x / 410.0))) for x in range(0, W, 8)]
d.line(pts, fill=(80, 200, 255), width=6)
for k, x in enumerate((420, 780, 1140, 1500)):
    d.line([(x, 120), (x, 980)], fill=(255, 200, 60), width=5); d.text((x + 12, 120), 'SPIN %d' % (k + 1), font=F('Mono700.ttf', 44), fill=(255, 200, 60))
d.text((40, 30), 'PRNG MODEL · MACHINE #7', font=F('Mono700.ttf', 52), fill=(140, 160, 190))
im.save('graph.png')
# carpet pattern
W = 1024; im = Image.new('RGB', (W, W), (70, 12, 20)); d = ImageDraw.Draw(im)
for i in range(0, W, 128):
    for j in range(0, W, 128):
        d.ellipse([i + 20, j + 20, i + 108, j + 108], outline=(150, 100, 30), width=8); d.ellipse([i + 54, j + 54, i + 74, j + 74], fill=(20, 60, 80))
im = im.filter(ImageFilter.GaussianBlur(1.5)); im.save('carpet.png')
# number stream for "formula"
W, H = 1024, 2048; im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im); rnd = random.Random(7)
for y in range(0, H, 64):
    s = ' '.join('%08X' % rnd.getrandbits(32) for _ in range(3)); d.text((20, y), s, font=F('Mono500.ttf', 44), fill=(60, 255, 160))
im.save('hex.png')
print('tex ok')
