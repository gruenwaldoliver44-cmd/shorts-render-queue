# Occluders (fg_*.png), cleaned sets (chairs/stools removed) and cut props from sets.
import numpy as np, cv2, json
from PIL import Image, ImageDraw, ImageFilter
P = 'public/'
def load(n): return np.array(Image.open(P + n + '.jpg').convert('RGB'))
def poly_mask(size, polys, blur=.8):
    m = Image.new('L', size, 0); d = ImageDraw.Draw(m)
    for p in polys: d.polygon([tuple(q) for q in p], fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur))
R = lambda x, y, w, h: [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
def fg(src, name, polys):
    im = Image.open(P + src + '.jpg').convert('RGBA'); im.putalpha(poly_mask(im.size, polys)); im.save(P + name + '.png')
def inpaint(src, dst, polys, keep=()):
    a = load(src); m = np.array(poly_mask((1920, 1080), polys, 0))
    if keep: m[np.array(poly_mask((1920, 1080), keep, 0)) > 0] = 0
    m = cv2.dilate((m > 0).astype('uint8') * 255, np.ones((7, 7), np.uint8))
    o = cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA); Image.fromarray(o).save(P + dst + '.jpg', quality=93)

# kitchen: remove the chair (seated sprites bring their own), table becomes an occluder
TABLE = [R(585, 604, 768, 84), R(640, 686, 660, 40), R(606, 686, 46, 350), R(1283, 686, 46, 350), R(688, 686, 36, 228), R(1212, 686, 36, 228)]
a = load('s_kitchen').astype(float); km = np.array(poly_mask((1920, 1080), TABLE, 0)) > 0
xl, xr = 856, 1076
for y in range(496, 915):
    def side(x0, x1):
        c = a[y, x0:x1].reshape(-1, 3); c = c[c.mean(1) > 120]
        return np.median(c, 0) if len(c) else a[y, x0]
    L, Rr = side(xl - 14, xl), side(xr, xr + 14)
    for x in range(xl + 1, xr):
        if not km[y, x] or 596 <= y <= 606: q = (x - xl) / (xr - xl); a[y, x] = L * (1 - q) + Rr * q
Image.fromarray(a.astype('uint8')).save(P + 's_kitchen2.jpg', quality=93)
fg('s_kitchen2', 'fg_kitchen', TABLE)
# jeweler: counter in front of the jeweler
fg('s_jewel', 'fg_jewel', [[(688, 518), (1920, 536), (1920, 1080), (720, 1080), (700, 930)]])
# bakery counter (with the bread on top)
fg('s_bakery', 'fg_bakery', [[(652, 545), (1626, 545), (1626, 862), (652, 862)], R(720, 510, 300, 60), R(1290, 480, 300, 80)])
# ship: remove the three stools, keep the table
#inpaint('s_ship', 's_ship2', [R(826, 700, 80, 102), R(972, 738, 94, 106), R(1056, 700, 80, 98)], keep=[R(893, 646, 156, 160)])
# tokyo desk prop: centre desk without monitors and keyboard
a = load('s_tokyo'); crop = a[672:990, 656:1262].copy()
band = np.zeros(crop.shape[:2], np.uint8); band[0:70, :] = 255
dark = (crop.mean(2) < 95).astype(np.uint8) * 255; m = cv2.dilate(dark & band, np.ones((5, 5), np.uint8))
crop = cv2.inpaint(crop, m, 7, cv2.INPAINT_TELEA)
top = np.array([170., 110., 80.]); crop[6:60, 4:602] = top; crop[2:7, 2:604] = (28, 22, 20); crop[60:66, 2:604] = (28, 22, 20); crop[2:66, 2:7] = (28, 22, 20); crop[2:66, 599:604] = (28, 22, 20)
for y in range(8, 58): crop[y, 6:600] = np.clip(top * (1.06 - 0.12 * y / 58), 0, 255)
alpha = np.zeros(crop.shape[:2], np.uint8); cv2.fillPoly(alpha, [np.array([(2, 2), (604, 2), (604, 64), (594, 64), (594, 316), (532, 316), (532, 228), (78, 228), (78, 316), (16, 316), (16, 64), (2, 64)])], 255)
alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
Image.fromarray(np.dstack([crop, alpha])).save(P + 'pp_desk.png')
SP = json.load(open('src/sprites.json')); SP['pp_desk'] = [round(606 * 700 / 318), 700]; json.dump(SP, open('src/sprites.json', 'w'))
print('ok')
