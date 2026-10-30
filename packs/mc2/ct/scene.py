import bpy, math, json, os
from mathutils import Vector
ROOT = os.environ.get('CT_ROOT', '/home/user/mc2')
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
GOLD = srgb('#e7b65a'); CREAM = srgb('#f4ecda'); RED = srgb('#d6283a'); GRN = srgb('#5adc78')
M_floor = mat('floor', srgb('#17121f'), rough=0.3, coat=0.5)
M_dark = mat('dark', srgb('#0e0c14'), rough=0.5)
M_gold = mat('gold', GOLD, rough=0.22, metal=1.0)
M_goldglow = mat('goldglow', GOLD, rough=0.3, emit=GOLD, estr=4.0)
M_plane = mat('planebody', srgb('#eef0f4'), rough=0.3, coat=0.6)
M_planedark = mat('planedark', srgb('#2a2d38'), rough=0.4, metal=0.3)
M_glass = mat('glass', srgb('#14182a'), rough=0.05, coat=1.0)
M_cloud = mat('cloud', srgb('#f3e6dc'), rough=0.95, emit=srgb('#ffd9b0'), estr=0.25)
M_wood = mat('wood', srgb('#5a3a22'), rough=0.45, coat=0.3)
M_desk = mat('desk', srgb('#2a2f3c'), rough=0.35, coat=0.4)
M_paper = mat('paper', srgb('#f4f0e4'), rough=0.7)
M_bread = mat('bread', srgb('#d9a35a'), rough=0.7); M_lett = mat('lett', srgb('#5fae3c'), rough=0.6); M_tom = mat('tom', srgb('#d83a2c'), rough=0.35, coat=0.4); M_cheese = mat('cheese', srgb('#f2c23a'), rough=0.5)
M_plate = mat('plate', srgb('#f6f6f2'), rough=0.2, coat=0.8)
M_seat = mat('seat', srgb('#3a2430'), rough=0.6)
M_seat2 = mat('seat2', srgb('#c9b28a'), rough=0.5)
M_red = mat('redglow', RED, rough=0.4, emit=RED, estr=5.0)
M_grn = mat('grnglow', GRN, rough=0.4, emit=GRN, estr=4.0)
M_arc = mat('arc', GOLD, rough=0.4, emit=GOLD, estr=2.5)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (*srgb('#140f1c'), 1); bgn.inputs[1].default_value = 0.25
bpy.ops.mesh.primitive_plane_add(size=500, location=(60, 0, 0)); bpy.context.object.data.materials.append(M_floor)
def emptyo(name, loc, parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e
def area(name, loc, rot, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object; l.name = name; l.data.energy = energy; l.data.size = size; l.data.color = color; return l
def rig(x, k=1.0):
    area('key%d' % x, (x - 2.5, -4, 4.5), (R(48), 0, R(-30)), 900 * k, 4, (1.0, 0.92, 0.82))
    area('rim%d' % x, (x + 2.5, 3, 3.5), (R(-55), 0, R(150)), 900 * k, 3, (1.0, 0.78, 0.5))
    area('fill%d' % x, (x + 4, -2.5, 2.5), (R(65), 0, R(60)), 220 * k, 5, (0.85, 0.85, 1.0))
def cyl(name, r, d, loc, m, rot=(0, 0, 0), parent=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=verts)
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
def slab(name, pts, th, m, parent, axis='z', mirror=False):
    verts = []; faces = []
    for sgn in ((1, -1) if mirror else (1,)):
        b = len(verts); n = len(pts)
        for off in (-th / 2, th / 2):
            for (u, v) in pts:
                if axis == 'z': verts.append((u, sgn * v, off))
                else: verts.append((u, off, v))
        faces.append(list(range(b, b + n))[::-1]); faces.append(list(range(b + n, b + 2 * n)))
        for i in range(n):
            j = (i + 1) % n; faces.append([b + i, b + j, b + n + j, b + n + i])
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); ob.data.materials.append(m); ob.parent = parent
    bv = ob.modifiers.new('bv', 'BEVEL'); bv.width = 0.006; bv.segments = 2
    return ob
anchors = {}
def anchor(name, loc, parent=None):
    anchors[name] = emptyo('a_' + name, loc, parent); return anchors[name]
M_pass = tex('passm', 'pass.png', rough=0.25); M_comp = tex('compm', 'comp.png', rough=0.25)
def cardobj(name, loc, m, parent=None):
    C = emptyo(name, loc, parent)
    box(name + '_b', (0.86, 0.54, 0.01), (0, 0, 0), M_gold, bevel=0.004, parent=C)
    plane(name + '_f', 0.85, 0.53, (0, 0, 0.0052), m, rot=(0, 0, 0), parent=C)
    return C
# ================= SET A (x=0): the pass =================
rig(0)
box('pedA', (1.6, 1.2, 0.6), (0, 0.2, 0.3), M_dark, bevel=0.02)
CA = cardobj('cardA', (0, 0, 0.9), M_pass)
kf(CA, 'location', [(0, (0.6, -1.2, 1.9)), (0.55, (0, 0, 0.95)), (2.3, (0, 0, 0.95)), (5.9, (0, 0, 0.95)), (8.6, (0, 0, 0.95)), (17.3, (-0.25, 0, 0.95)), (24.3, (-0.25, 0, 0.95))])
kf(CA, 'rotation_euler', [(0, (R(80), R(200), R(-60))), (0.55, (R(62), 0, R(-8))), (2.3, (R(58), 0, R(4))), (5.92, (R(65), 0, R(-10))), (8.6, (R(60), 0, R(6))), (17.36, (R(55), 0, R(-6))), (24.3, (R(55), 0, R(2)))])
CC = cardobj('cardC', (0.35, -0.1, 0.97), M_comp)
kf(CC, 'location', [(0, (2.5, -0.5, 1.2)), (21.4, (2.5, -0.5, 1.2)), (21.9, (0.3, -0.12, 1.0)), (24.3, (0.3, -0.12, 1.0))])
kf(CC, 'rotation_euler', [(21.4, (R(30), R(90), 0)), (21.9, (R(55), 0, R(10))), (24.3, (R(55), 0, R(14)))])
SOLD = emptyo('soldtag', (0.55, -0.35, 1.3))
plane('soldp', 0.6, 0.24, (0, 0, 0), tex('soldm', 'sold.png', emit=True, estr=1.3), parent=SOLD)
popin(SOLD, 7.25); vis(SOLD, [[7.2, 8.66]])
for c in SOLD.children: vis(c, [[7.2, 8.66]])
anchor('card', (0, 0, 0.3), CA); anchor('comp', (0, 0, 0.3), CC); anchor('sold', (0, -0.02, 0), SOLD)
# ================= SET B (x=14): the jet over clouds =================
X = 200
area('sun%d' % X, (X - 6, -6, 6), (R(55), 0, R(-45)), 2500, 8, (1.0, 0.8, 0.55)); area('sky%d' % X, (X + 4, 4, 5), (R(-50), 0, R(140)), 900, 8, (0.6, 0.7, 1.0))
rnd = random.Random(5)
for k in range(70):
    sph('cl%d' % k, rnd.uniform(0.7, 1.6), (X + rnd.uniform(-12, 12), rnd.uniform(-1.5, 8), rnd.uniform(-0.6, 0.0)), M_cloud, scale=(1.6, 1.2, 0.45))
AP = emptyo('jet', (X, 0, 1.7)); AP.scale = (2.4, 2.4, 2.4)
PL = emptyo('jet_body', (0, 0, 0), AP)
cyl('pl_fus', 0.085, 1.3, (0, 0, 0), M_plane, rot=(0, R(90), 0), parent=PL)
sph('pl_nose', 0.085, (0.65, 0, 0), M_plane, scale=(1.6, 1, 1), parent=PL)
bpy.ops.mesh.primitive_cone_add(radius1=0.085, radius2=0.02, depth=0.32, location=(-0.81, 0, 0.02), rotation=(0, R(-90), 0), vertices=48)
o = bpy.context.object; o.data.materials.append(M_plane); bpy.ops.object.shade_smooth(); o.parent = PL
slab('pl_wings', [(0.12, 0.06), (-0.12, 0.72), (-0.24, 0.72), (-0.18, 0.06)], 0.02, M_plane, PL, mirror=True)
slab('pl_tailw', [(-0.66, 0.03), (-0.8, 0.26), (-0.87, 0.26), (-0.84, 0.03)], 0.014, M_plane, PL, mirror=True)
slab('pl_fin', [(-0.62, 0.06), (-0.84, 0.36), (-0.93, 0.36), (-0.9, 0.06)], 0.016, M_gold, PL, axis='y')
for s in (1, -1): cyl('pl_eng%d' % s, 0.05, 0.2, (0.02, s * 0.32, -0.06), M_planedark, rot=(0, R(90), 0), parent=PL)
for k in range(9):
    sph('pl_win%d' % k, 0.012, (0.45 - k * 0.1, -0.083, 0.025), M_glass, parent=PL); sph('pl_winb%d' % k, 0.012, (0.45 - k * 0.1, 0.083, 0.025), M_glass, parent=PL)
box('pl_stripe', (1.1, 0.172, 0.012), (-0.05, 0, -0.015), M_gold, parent=PL)
kf(AP, 'location', [(2.26, (X - 5.5, 0, 1.7)), (5.92, (X + 5.0, 0, 2.1))], 'LINEAR')
kf(AP, 'rotation_euler', [(2.26, (R(-6), R(-4), 0)), (3.8, (R(8), R(-3), 0)), (5.92, (R(-4), R(-6), 0))])
anchor('jet', (0, 0, 0.3), AP)
# ================= SET C (x=28): the gate =================
X = 28; rig(X)
box('desk', (2.2, 0.8, 1.05), (X, 0.3, 0.525), M_desk, bevel=0.03)
box('desktop', (2.3, 0.9, 0.05), (X, 0.3, 1.075), M_wood, bevel=0.01)
SG = plane('gatesign', 2.0, 0.8, (X, 1.6, 2.3), tex('gatem', 'gate.png', emit=True, estr=1.6))
box('gatepost', (0.08, 0.08, 1.9), (X - 0.9, 1.62, 0.95), M_planedark); box('gatepost2', (0.08, 0.08, 1.9), (X + 0.9, 1.62, 0.95), M_planedark)
SCN = emptyo('scanner', (X + 0.5, 0.1, 1.1)); box('scb', (0.36, 0.3, 0.12), (0, 0, 0.06), M_planedark, bevel=0.02, parent=SCN)
scg = plane('scglow', 0.3, 0.24, (0, 0, 0.122), M_grn, rot=(0, 0, 0), parent=SCN); vis(scg, [[0, 45.6]])
scr = plane('scred', 0.3, 0.24, (0, 0, 0.123), M_red, rot=(0, 0, 0), parent=SCN); vis(scr, [[45.6, None]])
CG = cardobj('cardG', (X - 0.2, 0.0, 1.11), M_pass)
CG.rotation_euler = (0, 0, R(8))
# 8.66-12.62: card yanked at 10.06 to the left; 42.82+: card on scanner, stamped
kf(CG, 'location', [(8.66, (X - 0.2, 0.0, 1.11)), (10.0, (X - 0.2, 0.0, 1.11)), (10.18, (X - 0.4, 0.0, 1.16)), (10.6, (X - 4.5, -0.3, 1.5)), (42.8, (X - 4.5, -0.3, 1.5)), (42.82, (X + 0.5, 0.1, 1.24)), (60, (X + 0.5, 0.1, 1.24))])
kf(CG, 'rotation_euler', [(10.0, (0, 0, R(8))), (10.6, (R(20), R(-40), R(60))), (42.8, (R(20), R(-40), R(60))), (42.82, (0, 0, R(-6))), (60, (0, 0, R(-6)))])
string = cyl('yank', 0.004, 3.0, (X - 1.8, 0.0, 1.13), mat('strm', srgb('#d8cfb8'), rough=0.9), rot=(0, R(90), 0)); vis(string, [[9.6, 10.7]])
kf(string, 'location', [(9.6, (X - 1.8, 0.0, 1.13)), (10.0, (X - 1.8, 0.0, 1.13)), (10.6, (X - 6.1, -0.3, 1.5))])
RV = emptyo('revoked', (X + 0.5, 0.1, 1.26)); RV.rotation_euler = (0, 0, R(-14))
plane('revp', 0.86, 0.28, (0, 0, 0), tex('revm', 'revoked.png', alpha=True, rough=0.5), rot=(0, 0, 0), parent=RV)
kf(RV, 'scale', [(0, (0, 0, 0)), (45.8, (0, 0, 0)), (45.88, (1.6, 1.6, 1.6)), (45.98, (0.95, 0.95, 0.95)), (46.05, (1, 1, 1))])
anchor('gate', (X, 1.6, 2.3)); anchor('cardG', (X + 0.5, 0.1, 1.3)); anchor('desk', (X - 0.2, 0, 1.2))
# ================= SET D (x=42): globe with flight arcs =================
X = 42; rig(X, 0.4)
GL = emptyo('globe', (X, 0, 1.6))
sph('globe_s', 1.2, (0, 0, 0), tex('globem', 'globe.png', emit=True, estr=0.9, rough=0.4), parent=GL)
kf(GL, 'rotation_euler', [(24.24, (0, 0, R(0))), (37.5, (0, 0, R(70)))], 'LINEAR')
rnd = random.Random(9)
def sphpt(lat, lon, r=1.205):
    return Vector((r * math.cos(lat) * math.cos(lon), r * math.cos(lat) * math.sin(lon), r * math.sin(lat)))
ARCS = []
for k in range(260):
    a = sphpt(R(rnd.uniform(10, 55)), R(rnd.uniform(-130, -60))) if k % 3 else sphpt(R(41.9), R(-87.6))
    b = sphpt(R(rnd.uniform(-30, 60)), R(rnd.uniform(-160, 40)))
    mid = (a + b) / 2; h = 1.205 + 0.15 + (a - b).length * 0.35; mid = mid.normalized() * h
    cu = bpy.data.curves.new('arc%d' % k, 'CURVE'); cu.dimensions = '3D'; sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    for p, co in zip(sp.bezier_points, (a, mid, b)): p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
    cu.bevel_depth = 0.004 if k > 12 else 0.008
    ob = bpy.data.objects.new('arc%d' % k, cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(M_arc); ob.parent = GL
    t0 = 24.5 + k * 0.03 if k < 12 else 33.8 + (k - 12) * 0.012
    cu.bevel_factor_end = 0; cu.keyframe_insert('bevel_factor_end', frame=F(t0)); cu.bevel_factor_end = 1; cu.keyframe_insert('bevel_factor_end', frame=F(t0 + 0.6))
anchor('globe', (X, -1.25, 2.4)); anchor('chicago', (0, 0, 0), GL); anchors['chicago'].location = sphpt(R(41.9), R(-87.6))
# ================= SET E (x=56): sandwich + seats =================
X = 56; rig(X)
TT = box('tray', (1.2, 0.8, 0.04), (X, 0, 0.9), M_seat2, bevel=0.01)
cyl('plate', 0.32, 0.03, (X, 0, 0.935), M_plate, verts=64)
layers = [('b1', M_bread, 0.035), ('lt', M_lett, 0.02), ('tm', M_tom, 0.02), ('ch', M_cheese, 0.015), ('b2', M_bread, 0.035)]
z = 0.955
for k, (nm, m, th) in enumerate(layers):
    L = box('sw_' + nm, (0.38, 0.38, th), (X, 0, z + th / 2), m, bevel=0.012)
    t = 28.35 + k * 0.2
    kf(L, 'location', [(0, (X, 0, z + th / 2 + 1.6)), (t, (X, 0, z + th / 2 + 1.6)), (t + 0.18, (X, 0, z + th / 2)), (t + 0.24, (X, 0, z + th / 2 + 0.015)), (t + 0.3, (X, 0, z + th / 2))])
    z += th
FLAG = emptyo('flag', (X + 0.05, 0, z)); cyl('flagstick', 0.004, 0.22, (0, 0, 0.11), M_paper, parent=FLAG)
plane('flagp', 0.16, 0.1, (0.08, 0, 0.19), mat('flagm', CREAM, rough=0.6), parent=FLAG); popin(FLAG, 29.4)
anchor('sandwich', (X, 0, 1.25))
for k, sx in enumerate((-0.75, 0.75)):
    S = emptyo('seat%d' % k, (X + sx, 2.4, 0))
    box('st_base%d' % k, (1.1, 1.0, 0.5), (0, 0, 0.25), M_seat, bevel=0.06, parent=S)
    box('st_back%d' % k, (1.1, 0.3, 1.3), (0, 0.45, 0.95), M_seat, bevel=0.08, parent=S)
    box('st_arm%d' % k, (0.12, 1.0, 0.25), (0.55, 0, 0.6), M_seat2, bevel=0.03, parent=S)
CS = cardobj('cardS', (X - 0.75, 2.2, 0.56), M_comp)
kf(CS, 'location', [(30.0, (X - 0.75, 2.2, 0.56)), (31.0, (X - 0.75, 2.2, 0.56)), (31.6, (X, 2.0, 1.6)), (32.2, (X + 0.75, 2.2, 0.56))])
kf(CS, 'rotation_euler', [(31.0, (0, 0, R(10))), (31.6, (R(180), R(30), R(90))), (32.2, (R(360), 0, R(-15)))])
anchor('seatR', (X + 0.75, 2.2, 1.0)); anchor('seatL', (X - 0.75, 2.2, 1.0))
# ================= SET F (x=70): cash =================
X = 70; rig(X)
M_cash = tex('cashm', 'cash.png', rough=0.6); M_cashside = mat('cashside', srgb('#d6e0cf'), rough=0.8)
def bundle(name, loc):
    B = emptyo(name, loc); box(name + 'b', (0.3, 0.13, 0.06), (0, 0, 0.03), M_cashside, bevel=0.004, parent=B)
    plane(name + 't', 0.3, 0.13, (0, 0, 0.0605), M_cash, rot=(0, 0, 0), parent=B); return B
k = 0
for j in range(5):
    for i in range(5):
        B = bundle('s250_%d' % k, (X - 1.0 + (i % 5) * 0.0 + (i - 2) * 0.31, -0.2 + 0.0, 0.0 + j * 0.062)); popin(B, 15.1 + k * 0.04); vis(B, [[15.0, 17.36]])
        for c in B.children: vis(c, [[15.0, 17.36]])
        k += 1
k = 0
for j in range(10):
    for i in range(10):
        B = bundle('m_%d' % k, (X + 1.2 + (i % 5 - 2) * 0.31, -0.2 + (i // 5) * 0.14, j * 0.062))
        popin(B, 39.2 + k * 0.016, dur=0.1)
        for c in B.children: vis(c, [[38.9, 42.82]])
        k += 1
anchor('cash250', (X - 1.0, -0.2, 0.6)); anchor('cash1m', (X + 1.2, -0.1, 0.9))
# ================= SET G (x=84): reservation board =================
X = 84; rig(X, 0.5)
BA = plane('boardA', 2.8, 2.0, (X, 0.5, 1.6), tex('boardam', 'board_a.png', emit=True, estr=1.4))
BB = plane('boardB', 2.8, 2.0, (X, 0.49, 1.6), tex('boardbm', 'board_b.png', emit=True, estr=1.4))
vis(BA, [[0, 49.4]]); vis(BB, [[49.4, None]])
kf(BB, 'scale', [(49.4, (1, 0.05, 1)), (49.6, (1, 1.04, 1)), (49.7, (1, 1, 1))])
box('boardframe', (3.0, 0.12, 2.2), (X, 0.58, 1.6), M_planedark, bevel=0.02)
anchor('board', (X + 0.9, 0.4, 1.9))
# ================= SET H (x=98): contract + gavel =================
X = 98; rig(X)
box('tableH', (3.0, 2.0, 0.8), (X, 0.4, 0.4), M_wood, bevel=0.02)
CT_ = plane('contract', 0.9, 1.2, (X - 0.2, 0.2, 0.805), tex('contm', 'contract.png', rough=0.6), rot=(0, 0, R(4)))
CH11 = emptyo('ch11', (X - 0.2, 0.0, 0.82)); CH11.rotation_euler = (0, 0, R(12))
plane('ch11p', 0.86, 0.28, (0, 0, 0), tex('ch11m', 'ch11.png', alpha=True), rot=(0, 0, 0), parent=CH11)
kf(CH11, 'scale', [(0, (0, 0, 0)), (55.1, (0, 0, 0)), (55.18, (1.6, 1.6, 1.6)), (55.28, (0.95, 0.95, 0.95)), (55.35, (1, 1, 1))])
GV = emptyo('gavel', (X + 0.75, 0.2, 0.83))
GH = emptyo('gavelhead', (0, 0, 0), GV)
cyl('gv_head', 0.09, 0.32, (0, 0, 0.09), M_wood, rot=(R(90), 0, 0), parent=GH); cyl('gv_handle', 0.025, 0.55, (0.28, 0, 0.09), M_wood, rot=(0, R(90), 0), parent=GH)
cyl('gv_block', 0.16, 0.05, (0, 0, 0.025), M_wood, parent=GV)
GH.location = (0, 0, 0.05)
kf(GH, 'rotation_euler', [(0, (0, R(-35), 0)), (53.1, (0, R(-35), 0)), (53.36, (0, R(0), 0)), (53.44, (0, R(-6), 0)), (53.52, (0, 0, 0))])
CH_ = cardobj('cardH', (X + 0.4, -0.3, 0.81), M_pass); CH_.rotation_euler = (0, 0, R(-12))
kf(CH_, 'location', [(56.8, (X + 0.4, -0.3, 0.81)), (57.0, (X + 0.55, -0.6, 0.85)), (57.4, (X + 0.6, -1.05, 0.2)), (57.5, (X + 0.6, -1.08, 0.006))])
kf(CH_, 'rotation_euler', [(56.8, (0, 0, R(-12))), (57.4, (R(-70), R(20), R(-20))), (57.5, (0, 0, R(-30)))])
anchor('contract', (X - 0.2, 0.2, 0.9)); anchor('gavel', (X + 0.75, 0.2, 1.1))
# ================= SET I (x=112): the scale =================
X = 112; rig(X)
cyl('sc_base', 0.35, 0.06, (X, 0, 0.03), M_gold); cyl('sc_post', 0.04, 1.6, (X, 0, 0.8), M_gold)
BEAM = emptyo('beam', (X, 0, 1.6)); cyl('sc_beam', 0.03, 2.2, (0, 0, 0), M_gold, rot=(0, R(90), 0), parent=BEAM)
pans = []
for sx in (-1, 1):
    P = emptyo('pan%d' % sx, (X + sx * 1.05, 0, 1.0))
    cyl('pan_d%d' % sx, 0.38, 0.03, (0, 0, 0), M_gold, parent=P)
    for a in range(3):
        an = R(a * 120); cyl('pan_s%d_%d' % (sx, a), 0.005, 0.62, (math.cos(an) * 0.18, math.sin(an) * 0.18, 0.3), M_gold, rot=(R(-16) * math.sin(an), R(16) * math.cos(an), 0), parent=P)
    pans.append(P)
cardobj('cardI', (0, 0, 0.03), M_pass, parent=pans[0]).rotation_euler = (0, 0, R(20))
for j in range(4):
    for i in range(3):
        B = bundle('pm_%d_%d' % (i, j), (0, 0, 0)); B.parent = pans[1]; B.location = ((i - 1) * 0.0, (i - 1) * 0.14, 0.02 + j * 0.062); B.scale = (0.9, 0.9, 0.9)
tilt = [(57.76, 0.0), (58.3, 9), (58.9, -7), (59.5, 5), (60.1, -3), (60.6, 1)]
kf(BEAM, 'rotation_euler', [(t, (0, R(a), 0)) for t, a in tilt])
for sx, P in zip((-1, 1), pans):
    kf(P, 'location', [(t, (X + sx * 1.05 * math.cos(R(a)), 0, 1.0 - sx * 1.05 * math.sin(R(a)))) for t, a in tilt])
anchor('panL', (X - 1.05, 0, 1.4)); anchor('panR', (X + 1.05, 0, 1.6))
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
