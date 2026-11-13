"""Cut sprites from pose sheets with clean edges (erode + colour decontamination against white)."""
from PIL import Image
import numpy as np, json
from scipy import ndimage as ni
from seg import seg
P = '../engine/public/'
SJ = '../engine/src/sprites.json'
S = {}; BOX = {}

def split_blob(m, k):
    """split a merged mask into k parts at the emptiest columns"""
    col = m.sum(0).astype(float); W = len(col); cuts = []
    sm = ni.uniform_filter1d(col, 15)
    for j in range(1, k):
        lo, hi = int(W * (j / k - 0.18)), int(W * (j / k + 0.18))
        c = lo + int(np.argmin(sm[lo:hi])); cuts.append(c)
    edges = [0] + cuts + [W]
    return [(edges[i], edges[i + 1]) for i in range(k)]

def save(a, mask, x0, y0, nm, src, bx):
    ys, xs = np.where(mask)
    yy0, yy1, xx0, xx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    m = mask[yy0:yy1, xx0:xx1]; rgb = a[y0 + yy0:y0 + yy1, x0 + xx0:x0 + xx1].astype(float)
    m = ni.binary_erosion(m, iterations=1)
    al = np.clip(ni.gaussian_filter(m.astype(float), 0.8), 0, 1)
    # decontaminate: remove white bleeding at semi-transparent edge
    A = np.maximum(al, 1e-3)[..., None]
    rgb = np.clip((rgb - (1 - A) * 255) / A, 0, 255)
    rgb = np.where(al[..., None] > 0.98, a[y0 + yy0:y0 + yy1, x0 + xx0:x0 + xx1], rgb)
    im = Image.fromarray(np.dstack([rgb, al * 255]).astype('uint8'), 'RGBA')
    im.save(P + nm + '.png')
    S[nm] = [round(im.width * 700 / im.height), 700]
    BOX[nm] = (src, int(x0 + xx0), int(x0 + xx1), int(y0 + yy0), int(y0 + yy1))

def cut(src, names):
    a, L, o = seg(src)
    assert len(o) == sum(1 if not isinstance(n, list) else 1 for n in names), (src, len(o), len(names))
    for q, nm in zip(o, names):
        if nm is None: continue
        sl = (slice(q['y0'], q['y1']), slice(q['x0'], q['x1']))
        m = (L == q['i'])[sl]
        if isinstance(nm, list):
            for (c0, c1), n2 in zip(split_blob(m, len(nm)), nm):
                mm = np.zeros_like(m); mm[:, c0:c1] = m[:, c0:c1]
                lab, n = ni.label(mm)
                if n > 1:
                    sz = ni.sum(mm, lab, range(1, n + 1)); mm = lab == (1 + int(np.argmax(sz)))
                save(a, mm, q['x0'], q['y0'], n2, src, None)
        else:
            save(a, m, q['x0'], q['y0'], nm, src, None)

cut('c_you.png', 'yo_stand yo_phone yo_walkR1 yo_walkR2 yo_eat yo_shock yo_head yo_laptop yo_anx yo_shrug'.split() + [['yo_rice', 'yo_cross']] + 'yo_point yo_relief'.split())
cut('c_you2.png', 'yo_wl1 yo_wl2 yo_wl3 yo_wl4 yo_wf1 yo_wf2 yo_reach yo_pull yo_rise yo_sitdn yo_type yo_lean yo_call yo_bag yo_frown'.split())
cut('c_lend.png', 'ld_aw ld_bw ld_cw ld_aread ld_bstick ld_ccross ld_cwrite te_cart te_scratch'.split() + [['tr_coll', 'tr_woman']] + 'cu_rattle cu_old'.split())
cut('c_lend2.png', 'ld_aR1 ld_bR1 ld_ahand ld_awatch ld_bR2 ld_bpress ld_bturn ld_cR1 ld_cpoint ld_cphone ld_ctray te_box te_hands te_floor'.split())
cut('c_trj.png', 'tr_type tr_turn tr_hands tr_talk jw_talk jw_point cu2_walk cu2_sad'.split())
cut('c_trj2.png', 'tr_ear tr_lean tr_rub tr_slam jw_hold jw_scale cu2_shock cu2_leave'.split())
cut('c_bkc.png', 'bk_write bk_turn bk_arms bkcu_shake cp_cards cp_laugh sl_a sl_b'.split())
cut('c_bkc2.png', 'bk_wipe bk_sack bk_lean bkcu_leave cp_throw pp_card cp_stand sl_a2 sl_b2'.split())
cut('c_tm.png', ['tl_peek', ['tl_calm', 'tl_walk'], 'tl_talk', 'wk_sign', 'el_fix', 'mg_talk', 'mg_paper'])
cut('c_tm2.png', 'tl_door tl_nerv mg_sad mg_sigh wk_carry wk_shrug el_switch el_down'.split())
cut('c_ext.png', 'dl_1 dl_2 dl_3 dl_4 cr_1 cr_2 cr_3 cr_4'.split())
cut('c_ext2.png', 'dl_1b dl_2b dl_3b dl_4b cr_1b cr_2b cr_3b cr_4b'.split())
cut('c_props.png', 'pp_phone pp_laptop pp_sandwich pp_chain pp_scalebox pp_flour pp_cards pp_clip pp_sticker pp_box pp_rice pp_bread pp_sign pp_env'.split())
json.dump(S, open(SJ, 'w')); json.dump(BOX, open('box.json', 'w'))
print(len(S))
