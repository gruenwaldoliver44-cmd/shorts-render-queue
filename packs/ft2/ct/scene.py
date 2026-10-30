import bpy, math, json, os
from mathutils import Vector
ROOT = os.environ.get('CT_ROOT', '/home/user/ft2')
TEX = ROOT + '/tex/'; FONT = TEX + 'DMSerif.ttf'
FPS = 24
def F(t): return int(round(t * FPS)) + 1
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
SH = json.load(open(ROOT + '/ct/shots.json')); A = SH['anim']
sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = F(A['end'])
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = 10; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.04
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transmission_bounces = 2
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.blur_glossy = 1.0
sc.render.use_motion_blur = False
sc.render.resolution_x = 720; sc.render.resolution_y = 1280
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception as e: print('look skip', e)
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 95
def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)
def mat(name, color, rough=0.5, metal=0.0, emit=None, estr=0.0, img=None, coat=0.0, img_emit=False, alpha_img=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal; b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
    if img:
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = bpy.data.images.load(img)
        if img_emit:
            nt.links.new(tn.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = estr or 1.5
            b.inputs['Base Color'].default_value = (0, 0, 0, 1)
        else:
            nt.links.new(tn.outputs['Color'], b.inputs['Base Color'])
        if alpha_img:
            nt.links.new(tn.outputs['Alpha'], b.inputs['Alpha'])
    return m
def box(name, size, loc, m, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        md = o.modifiers.new('bv', 'BEVEL'); md.width = bevel; md.segments = 3
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def plane(name, w, h, loc, m, rot=(math.radians(90), 0, 0), parent=None):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (w, h, 1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def all_fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    act = ad.action
    if hasattr(act, 'fcurves') and len(act.fcurves): return list(act.fcurves)
    out = []
    for layer in getattr(act, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out
def set_interp(idb, kind):
    for fc in all_fcurves(idb):
        for kp in fc.keyframe_points: kp.interpolation = kind
def kf(o, prop, seq, interp='BEZIER'):
    for t, v in seq:
        setattr(o, prop, v); o.keyframe_insert(prop, frame=F(t))
    set_interp(o, interp)
def vis(o, ranges):
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    for a, b in ranges:
        o.hide_render = False; o.keyframe_insert('hide_render', frame=F(a))
        if b is not None:
            o.hide_render = True; o.keyframe_insert('hide_render', frame=F(b))
    set_interp(o, 'CONSTANT')
R = math.radians
import random
VI = srgb('#8b5cf6'); AM = srgb('#ffb54c'); RED = srgb('#ff5064'); GRN = srgb('#50dc8c')
M_floor = mat('floor', srgb('#120e26'), rough=0.28, coat=0.5)
M_phone = mat('phone', srgb('#1b1d24'), rough=0.22, metal=0.7, coat=0.7)
M_frame = mat('pframe', srgb('#9aa0ac'), rough=0.2, metal=1.0)
M_gold = mat('gold', AM, rough=0.22, metal=1.0)
M_vi = mat('viglow', VI, rough=0.4, emit=VI, estr=5.0)
M_am = mat('amglow', AM, rough=0.4, emit=AM, estr=5.0)
M_red = mat('redglow', RED, rough=0.4, emit=RED, estr=5.0)
M_dark = mat('dark', srgb('#100c1e'), rough=0.5)
M_tower = mat('tower', srgb('#181530'), rough=0.3, metal=0.4)
M_win = mat('towerwin', srgb('#ffcf8a'), rough=0.4, emit=srgb('#ffcf8a'), estr=2.5)
M_pig = mat('pig', srgb('#f2a7b8'), rough=0.35, coat=0.5)
M_house = mat('house', srgb('#e9e0cc'), rough=0.6); M_roof = mat('roof', srgb('#7a2e24'), rough=0.6); M_mtn = mat('mtn', srgb('#2a2a40'), rough=0.8); M_snow = mat('snow', srgb('#f0f0f6'), rough=0.6)
M_road = mat('road', srgb('#3a3540'), rough=0.7)
M_glassw = mat('housewin', srgb('#ffd38a'), rough=0.4, emit=srgb('#ffd38a'), estr=3.0)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (*srgb('#0e0b1f'), 1); bgn.inputs[1].default_value = 0.22
bpy.ops.mesh.primitive_plane_add(size=500, location=(60, 0, 0)); bpy.context.object.data.materials.append(M_floor)
def emptyo(name, loc, parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e
def area(name, loc, rot, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object; l.name = name; l.data.energy = energy; l.data.size = size; l.data.color = color; return l
def rig(x, k=1.0):
    return [area('key%d' % x, (x - 2.5, -4, 4.5), (R(48), 0, R(-30)), 900 * k, 4, (1.0, 0.95, 0.9)),
            area('rim%d' % x, (x + 2.5, 3, 3.5), (R(-55), 0, R(150)), 900 * k, 3, (0.7, 0.55, 1.0)),
            area('fill%d' % x, (x + 4, -2.5, 2.5), (R(65), 0, R(60)), 220 * k, 5, (0.85, 0.9, 1.0))]
def cyl(name, r, d, loc, m, rot=(0, 0, 0), parent=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o
def cone(name, r1, r2, d, loc, m, rot=(0, 0, 0), parent=None, verts=32):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o
def sph(name, r, loc, m, scale=(1, 1, 1), parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    o = bpy.context.object; o.name = name; o.scale = scale; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o
def tex(name, img, emit=False, estr=1.5, alpha=False, rough=0.5):
    return mat(name, (1, 1, 1), rough=rough, img=TEX + img, img_emit=emit, estr=estr, alpha_img=alpha)
def popin(o, t, s=1.0, dur=0.16):
    kf(o, 'scale', [(0, (0, 0, 0)), (t, (0, 0, 0)), (t + dur, (s * 1.15,) * 3), (t + dur + 0.12, (s,) * 3)])
anchors = {}
def anchor(name, loc, parent=None):
    anchors[name] = emptyo('a_' + name, loc, parent); return anchors[name]
SCR = {}
def phone(name, loc, rot, screens, scale=1.0):
    P = emptyo(name, loc); P.rotation_euler = rot; P.scale = (scale,) * 3
    box(name + '_body', (0.78, 0.09, 1.6), (0, 0, 0), M_phone, bevel=0.07, parent=P)
    box(name + '_rim', (0.8, 0.07, 1.62), (0, 0, 0), M_frame, bevel=0.07, parent=P)
    for key, (img, rng) in screens.items():
        m = SCR.get(img) or tex('s_' + img, img, emit=True, estr=1.3, rough=0.15); SCR[img] = m
        s = plane(name + '_' + key, 0.72, 1.48, (0, -0.0465, 0), m, parent=P); vis(s, rng)
    return P
rnd = random.Random(3)
# ================= SET A (x=0): wallet phone + coins =================
rig(0)
PA = phone('pa', (-0.15, 0, 1.0), (R(3), 0, R(8)), {'w7': ('w7.png', [[0, 3.12]]), 'w5': ('w5.png', [[3.12, 3.6]]), 'w3': ('w3.png', [[3.6, 4.0]]), 'w1': ('w1.png', [[4.0, 4.4]]),
                                                  'wx': ('wx.png', [[4.4, 51.68]]), 'wc': ('wcode.png', [[51.68, 54.72]]), 'wch': ('wchoice.png', [[54.72, None]])})
kf(PA, 'location', [(0, (-0.15, 0, 1.0)), (0.25, (-0.15, 0, 1.0)), (0.38, (-0.15, 0, 1.08)), (0.55, (-0.15, 0, 1.0)), (4.35, (-0.15, 0, 1.0)), (4.45, (-0.15, 0, 1.04)), (4.6, (-0.15, 0, 1.0))])
COINS = []
for k in range(9):
    c = cyl('coin%d' % k, 0.2, 0.04, (0.62, -0.25, 0.02 + k * 0.042), M_gold, verts=48); COINS.append(c)
    kf(c, 'scale', [(0, (1, 1, 1)), (4.4 + k * 0.04, (1, 1, 1)), (4.6 + k * 0.04, (0, 0, 0))])
    vis(c, [[0, 51.68]])
for k in range(60):
    p = sph('dust%d' % k, 0.012, (0.62, -0.25, 0.2), M_am)
    d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 0.4), rnd.uniform(0.2, 1.4))).normalized() * rnd.uniform(0.4, 1.0)
    t0 = 4.42 + rnd.uniform(0, 0.3)
    kf(p, 'location', [(t0, (0.62, -0.25, 0.1 + rnd.uniform(0, 0.35))), (t0 + 0.8, tuple(Vector((0.62, -0.25, 0.25)) + d))])
    kf(p, 'scale', [(0, (0, 0, 0)), (t0, (0, 0, 0)), (t0 + 0.05, (1, 1, 1)), (t0 + 0.8, (0, 0, 0))])
anchor('pa', (0, -0.1, 0.5), PA); anchor('coins', (0.62, -0.25, 0.45)); anchor('btn', (-0.17, -0.1, -0.42), PA)
# ================= SET B (x=14): Shenzhen night + red envelopes =================
X = 14; rig(X, 0.35)
area('cityglow', (X, 6, 3), (R(-70), 0, 0), 1500, 10, (1.0, 0.35, 0.4))
for k in range(26):
    h = rnd.uniform(2.5, 9.0); wdt = rnd.uniform(0.6, 1.3); px = X + rnd.uniform(-7, 7); py = rnd.uniform(3, 9)
    box('tw%d' % k, (wdt, wdt, h), (px, py, h / 2), M_tower)
    for j in range(int(h / 0.5)):
        if rnd.random() < 0.55: box('twin%d_%d' % (k, j), (wdt * 0.8, 0.02, 0.1), (px, py - wdt / 2 - 0.01, 0.3 + j * 0.5), M_win)
M_env = tex('envm', 'env.png', rough=0.5); M_envb = mat('envback', srgb('#b40e20'), rough=0.5)
def envelope(name, loc, s=0.35):
    E = emptyo(name, loc)
    plane(name + 'f', 0.5 * s, 0.76 * s, (0, -0.002, 0), M_env, parent=E); plane(name + 'b', 0.5 * s, 0.76 * s, (0, 0.002, 0), M_envb, rot=(R(-90), 0, 0), parent=E)
    return E
for k in range(150):
    ex, ey = X + rnd.uniform(-3.2, 3.2), rnd.uniform(-1.2, 2.5); t0 = rnd.uniform(7.0, 9.8)
    E = envelope('env%d' % k, (ex, ey, 7))
    kf(E, 'location', [(0, (ex, ey, 9)), (t0, (ex, ey, 7.5)), (t0 + 2.6, (ex + rnd.uniform(-0.6, 0.6), ey, 0.05))], 'LINEAR')
    kf(E, 'rotation_euler', [(t0, (R(rnd.uniform(0, 360)), R(rnd.uniform(0, 360)), 0)), (t0 + 2.6, (R(rnd.uniform(400, 900)), R(rnd.uniform(200, 600)), R(rnd.uniform(0, 360))))], 'LINEAR')
HE = envelope('envhero', (X, -1.5, 1.4), s=1.0)
kf(HE, 'rotation_euler', [(10.6, (R(-10), R(-25), R(-30))), (12.9, (R(-4), R(10), R(18)))])
kf(HE, 'location', [(10.6, (X - 0.1, -1.5, 1.5)), (12.9, (X + 0.05, -1.5, 1.35))])
vis(HE, [[10.6, 12.9]]); [vis(c, [[10.6, 12.9]]) for c in HE.children]
anchor('city', (X, 4, 4)); anchor('envhero', (0, -0.05, 0.3), HE)
# ================= SET C (x=28): calendar + ring =================
X = 28; rig(X, 0.6)
plane('cal', 3.5, 1.05, (X, 0, 1.4), tex('calm', 'cal.png', emit=True, estr=1.2))
HL = plane('calhl', 0.47, 0.75, (X - 1.5, -0.01, 1.32), M_am)
seq = [(12.9, X - 1.48)]
for k in range(7): seq.append((13.6 + k * 0.24, X - 1.48 + k * 0.49))
kf(HL, 'location', [(t, (x, -0.012, 1.32)) for t, x in seq], 'CONSTANT'); vis(HL, [[13.6, 16.1]])
EC = envelope('envcal', (X + 1.48, -0.15, 1.36), s=0.75)
kf(EC, 'scale', [(0, (1, 1, 1)), (15.25, (1, 1, 1)), (15.4, (1.15, 1.15, 1.15)), (15.75, (0, 0, 0))])
for k in range(30):
    p = sph('ash%d' % k, 0.01, (X + 1.48, -0.2, 1.36), M_red); t0 = 15.3 + rnd.uniform(0, 0.3)
    d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 0), rnd.uniform(0, 1.5))).normalized() * rnd.uniform(0.3, 0.8)
    kf(p, 'location', [(t0, (X + 1.48, -0.2, 1.36)), (t0 + 0.7, tuple(Vector((X + 1.48, -0.2, 1.36)) + d))]); kf(p, 'scale', [(0, (0, 0, 0)), (t0, (0, 0, 0)), (t0 + 0.05, (1, 1, 1)), (t0 + 0.7, (0, 0, 0))])
RG = X + 6
for nm, m, end, r in (('ringbg', M_dark, 1.0, 0.05), ('ring', M_am, 0.92, 0.06)):
    bpy.ops.curve.primitive_bezier_circle_add(radius=1.1, location=(RG, 0, 1.5), rotation=(R(90), 0, 0)); cu = bpy.context.object; cu.name = nm
    cu.data.bevel_depth = r; cu.data.materials.append(m)
    if nm == 'ring':
        cu.data.bevel_factor_end = 0; cu.data.keyframe_insert('bevel_factor_end', frame=F(16.2)); cu.data.bevel_factor_end = 0.92; cu.data.keyframe_insert('bevel_factor_end', frame=F(17.3))
anchor('cal18', (X + 1.48, -0.1, 1.9)); anchor('ring', (RG, 0, 1.5))
# ================= SET D (x=42): the programmable coin =================
X = 42; rig(X, 0.7)
CT_ = emptyo('coinT', (X, 0, 1.5)); CB = emptyo('coinB', (X, 0, 1.5))
cyl('cT', 0.75, 0.08, (0, 0, 0.04), M_gold, parent=CT_, verts=96); cyl('cB', 0.75, 0.08, (0, 0, -0.04), M_gold, parent=CB, verts=96)
bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.02, location=(0, 0, 0.082)); o = bpy.context.object; o.data.materials.append(M_vi); o.parent = CT_
CHIP = emptyo('chip', (X, 0, 1.5)); box('chipb', (0.5, 0.5, 0.06), (0, 0, 0), M_dark, bevel=0.01, parent=CHIP); plane('chipt', 0.44, 0.44, (0, 0, 0.031), M_vi, rot=(0, 0, 0), parent=CHIP)
for s in range(4):
    for q in range(6):
        a = (q - 2.5) * 0.07; loc = [(a, -0.28, 0), (a, 0.28, 0), (-0.28, a, 0), (0.28, a, 0)][s]
        box('cpin%d_%d' % (s, q), (0.025, 0.08, 0.012) if s < 2 else (0.08, 0.025, 0.012), loc, M_gold, parent=CHIP)
for E_ in (CT_, CB, CHIP):
    kf(E_, 'rotation_euler', [(18.46, (R(70), 0, R(-20))), (22.0, (R(62), 0, R(30))), (26.76, (R(55), 0, R(80)))])
kf(CT_, 'location', [(18.46, (X, 0, 1.5)), (22.0, (X, 0, 1.5)), (22.5, (X, -0.25, 2.15)), (25.88, (X, -0.25, 2.15)), (26.2, (X, -0.1, 1.55)), (26.76, (X, -0.1, 1.55))])
kf(CB, 'location', [(18.46, (X, 0, 1.5)), (22.0, (X, 0, 1.5)), (22.5, (X, 0.25, 0.85)), (25.88, (X, 0.25, 0.85)), (26.2, (X, 0.1, 1.45)), (26.76, (X, 0.1, 1.45))])
CHIP.scale = (0, 0, 0); kf(CHIP, 'scale', [(0, (0, 0, 0)), (22.1, (0, 0, 0)), (22.4, (1.1, 1.1, 1.1)), (22.5, (1, 1, 1)), (25.9, (1, 1, 1)), (26.1, (0, 0, 0))])
# rule icons
PIN = emptyo('icpin', (X - 1.1, -0.6, 2.4)); sph('pinh', 0.14, (0, 0, 0.2), M_vi, parent=PIN); cone('pinc', 0.14, 0, 0.3, (0, 0, 0.0), M_vi, rot=(R(180), 0, 0), parent=PIN); popin(PIN, 23.2)
BAG = emptyo('icbag', (X + 1.15, -0.6, 2.35)); box('bagb', (0.32, 0.18, 0.34), (0, 0, 0), M_am, bevel=0.02, parent=BAG)
bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.012, location=(0, 0, 0.2), rotation=(R(90), 0, 0)); o = bpy.context.object; o.data.materials.append(M_am); o.parent = BAG; popin(BAG, 24.32)
HG = emptyo('ichg', (X, -0.7, 0.55)); cone('hg1', 0.16, 0.01, 0.26, (0, 0, 0.14), M_frame, parent=HG); cone('hg2', 0.01, 0.16, 0.26, (0, 0, -0.14), M_frame, parent=HG)
sand = cone('hgs', 0.12, 0.01, 0.16, (0, 0, -0.18), M_red, parent=HG); popin(HG, 25.5)
kf(HG, 'rotation_euler', [(25.7, (0, 0, 0)), (26.0, (0, R(180), 0))])
anchor('coin', (X, -0.3, 1.9)); anchor('pin', (X - 1.1, -0.6, 2.7)); anchor('bag', (X + 1.15, -0.6, 2.6)); anchor('hg', (X, -0.7, 0.85))
# ================= SET E (x=56): piggy bank + shops =================
X = 56; rig(X)
PG = emptyo('pig', (X, 0.3, 0.55))
sph('pigb', 0.5, (0, 0, 0), M_pig, scale=(1.25, 1, 0.95), parent=PG)
cyl('snout', 0.16, 0.12, (-0.66, 0, 0.0), M_pig, rot=(0, R(90), 0), parent=PG)
for s in (-1, 1):
    cone('ear%d' % s, 0.1, 0.0, 0.18, (-0.35, s * 0.22, 0.45), M_pig, rot=(0, R(-20), 0), parent=PG)
    for f in (-1, 1): cyl('leg%d%d' % (s, f), 0.09, 0.3, (f * 0.35, s * 0.25, -0.42), M_pig, parent=PG)
    sph('eye%d' % s, 0.035, (-0.52, s * 0.15, 0.2), M_dark, parent=PG)
box('slot', (0.25, 0.04, 0.02), (0.05, 0, 0.48), M_dark, parent=PG)
kf(PG, 'rotation_euler', [(0, (0, 0, R(-25))), (29.4, (0, 0, R(-25))), (29.5, (R(4), 0, R(-25))), (29.65, (R(-3), 0, R(-25))), (29.8, (0, 0, R(-25)))])
CN = cyl('dropcoin', 0.13, 0.03, (X + 0.05, 0.3, 2.2), M_gold, rot=(R(90), 0, 0))
kf(CN, 'location', [(28.9, (X + 0.05, 0.3, 2.2)), (29.4, (X + 0.05, 0.3, 1.08)), (29.75, (X + 0.9, 0.0, 1.6)), (30.4, (X + 3.5, -0.4, 1.2))])
kf(CN, 'rotation_euler', [(28.9, (R(90), 0, 0)), (29.4, (R(90), 0, R(20))), (30.4, (R(90), R(720), R(200)))])
for k in range(10):
    c = cyl('fly%d' % k, 0.1, 0.025, (X - 1.0, -0.2, 1.2), M_gold, rot=(R(90), 0, 0)); t0 = 30.0 + k * 0.08
    kf(c, 'location', [(t0, (X - 0.6, -0.5 + rnd.uniform(-0.2, 0.2), 1.0 + rnd.uniform(-0.2, 0.4))), (t0 + 0.6, (X + 3.5, -0.5, 1.2 + rnd.uniform(-0.3, 0.3)))], 'LINEAR')
    vis(c, [[t0, t0 + 0.62]])
SX = X + 9
for k in range(4):
    sx = SX + (k - 1.5) * 1.3
    box('shop%d' % k, (1.15, 1.0, 1.4), (sx, 0, 0.7), M_house, bevel=0.02)
    box('awn%d' % k, (1.2, 0.35, 0.06), (sx, -0.62, 1.15), M_roof, bevel=0.01)
    sg = plane('shopsign%d' % k, 0.9, 0.24, (sx, -0.505, 1.3), tex('shopm%d' % k, 'shop%d.png' % k, emit=True, estr=0.05))
    wn = plane('shopwin%d' % k, 0.8, 0.6, (sx, -0.505, 0.55), M_dark)
    on = plane('shopwinon%d' % k, 0.8, 0.6, (sx, -0.507, 0.55), M_glassw); t0 = 31.7 + k * 0.42; vis(on, [[t0, None]])
    m_ = bpy.data.materials['shopm%d' % k]; b_ = m_.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    b_.default_value = 0.05; b_.keyframe_insert('default_value', frame=F(t0)); b_.default_value = 2.0; b_.keyframe_insert('default_value', frame=F(t0 + 0.12))
anchor('pig', (X, 0.3, 1.3)); anchor('shops', (SX, -0.5, 1.9))
# ================= SET F (x=70): Woergl 1932 =================
X = 100; rig(X, 0.7)
area('dusk', (X - 6, -3, 4), (R(60), 0, R(-60)), 1200, 8, (1.0, 0.65, 0.4))
for k in range(5):
    cone('mtn%d' % k, rnd.uniform(3, 5), 0, rnd.uniform(4, 6.5), (X + (k - 2) * 4.2 + rnd.uniform(-1, 1), 12, 2.5), M_mtn, verts=6)
    cone('snow%d' % k, 1.1, 0, 1.3, (X + (k - 2) * 4.2, 12, 5.0), M_snow, verts=6)
HOUSES = []
for k in range(12):
    hx = X + (k % 6 - 2.5) * 1.5 + rnd.uniform(-0.2, 0.2); hy = 2.0 + (k // 6) * 2.2 + rnd.uniform(-0.3, 0.3)
    box('hs%d' % k, (1.0, 0.9, 0.8), (hx, hy, 0.4), M_house, bevel=0.02)
    cone('rf%d' % k, 0.85, 0, 0.6, (hx, hy, 1.1), M_roof, verts=4, rot=(0, 0, R(45)))
    plane('hw%d' % k, 0.2, 0.22, (hx - 0.2, hy - 0.455, 0.45), M_glassw)
    HOUSES.append((hx, hy))
box('church', (1.0, 1.0, 2.6), (X + 0.2, 4.6, 1.3), M_house, bevel=0.02); cone('spire', 0.7, 0, 1.6, (X + 0.2, 4.6, 3.4), M_roof, verts=4, rot=(0, 0, R(45)))
for k in range(9):
    t = box('road%d' % k, (0.9, 0.9, 0.02), (X - 4 + k * 0.95, 0.6, 0.012), M_road); popin(t, 46.2 + k * 0.1)
SN = emptyo('scrip', (X, -1.2, 1.4))
plane('scripp', 1.2, 0.64, (0, 0, 0), tex('scripm', 'scrip.png', rough=0.6), parent=SN)
plane('scripb', 1.2, 0.64, (0, 0.003, 0), mat('scripback', srgb('#d9c79c'), rough=0.7), rot=(R(-90), 0, 0), parent=SN)
kf(SN, 'location', [(34.22, (X + 0.8, -1.0, 4.2)), (35.6, (X + 0.8, -1.0, 4.2)), (37.6, (X, -1.2, 1.4)), (44.0, (X, -1.2, 1.4)), (44.04, (X, -1.2, -5)), (48.76, (X, -1.2, -5)), (48.8, (X, -1.2, 1.4))])
kf(SN, 'rotation_euler', [(35.6, (R(60), R(40), R(30))), (36.4, (R(-10), R(-20), R(-10))), (37.6, (0, 0, R(-3))), (44.0, (0, 0, R(2)))])
for k in range(12):
    st = plane('stmp%d' % k, 0.058, 0.075, (-0.6 + (120 + k * 82 + 35) / 1200 * 1.2, -0.004, 0.32 - 515 / 640 * 0.64), tex('stampm', 'stampt.png', rough=0.5) if k == 0 else bpy.data.materials['stampm'], parent=SN)
    popin(st, 41.6 + k * 0.17, dur=0.08)
BN = emptyo('banned', (-0.02, -0.008, 0.02), SN); BN.rotation_euler = (0, 0, R(-10))
plane('bannedp', 1.0, 0.32, (0, 0, 0), tex('bannedm', 'banned.png', alpha=True), parent=BN)
kf(BN, 'scale', [(0, (0, 0, 0)), (50.28, (0, 0, 0)), (50.36, (1.6, 1.6, 1.6)), (50.46, (0.95, 0.95, 0.95)), (50.52, (1, 1, 1))])
for k in range(8):
    fn = emptyo('fnote%d' % k, (X, 0, 1)); plane('fnp%d' % k, 0.4, 0.21, (0, 0, 0), bpy.data.materials['scripm'], parent=fn)
    a, b = HOUSES[k], HOUSES[(k * 5 + 3) % 12]; t0 = 44.1 + k * 0.12
    kf(fn, 'location', [(t0, (a[0], a[1] - 0.6, 0.9)), (t0 + 0.4, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.6, 2.0)), (t0 + 0.8, (b[0], b[1] - 0.6, 0.9))])
    kf(fn, 'rotation_euler', [(t0, (R(80), 0, 0)), (t0 + 0.8, (R(80), R(360), R(90)))])
    for c in [fn] + list(fn.children): vis(c, [[t0, t0 + 0.85]])
anchor('scrip', (0, -0.02, 0.2), SN); anchor('village', (X, 2.5, 2.0)); anchor('road', (X, 0.6, 0.3))
# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); bpy.context.collection.objects.link(cam); sc.camera = cam
tg = emptyo('camtgt', (0, 0, 1))
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36
for (t0, t1, p0, g0, l0, p1, g1, l1) in SH['shots']:
    f0, f1 = F(t0), F(t1) - 1
    for idb, prop, a, b in ((cam, 'location', p0, p1), (tg, 'location', g0, g1), (cd, 'lens', l0, l1)):
        setattr(idb, prop, a); idb.keyframe_insert(prop, frame=f0)
        setattr(idb, prop, b); idb.keyframe_insert(prop, frame=f1)
for idb in (cam, tg, cd):
    for fc in all_fcurves(idb):
        kps = sorted(fc.keyframe_points, key=lambda k: k.co.x)
        for i, kp in enumerate(kps):
            kp.interpolation = 'BEZIER' if i % 2 == 0 else 'CONSTANT'
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
cd.dof.use_dof = True; cd.dof.focus_object = tg; cd.dof.aperture_fstop = 3.2
FST = {int(k): v for k, v in SH.get('fst', {}).items()}
if FST:
    for i, sh in enumerate(SH['shots']):
        cd.dof.aperture_fstop = FST.get(i, 3.2); cd.dof.keyframe_insert('aperture_fstop', frame=F(sh[0]))
    for fc in all_fcurves(cd):
        if 'fstop' in fc.data_path:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/ct/scene.blend')
from bpy_extras.object_utils import world_to_camera_view
proj = {}
for fr in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(fr)
    proj[fr] = {n: [round(c.x, 4), round(1 - c.y, 4), round(c.z, 3)] for n, e in anchors.items() for c in [world_to_camera_view(sc, cam, e.matrix_world.translation)]}
json.dump(proj, open(ROOT + '/ct/proj.json', 'w'))
print('SCENE OK', sc.frame_end)
