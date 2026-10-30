import bpy, math, json, os
from mathutils import Vector
ROOT = os.environ.get('CT_ROOT', '/home/user/ct2')
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
    o = bpy.context.object; o.name = name; o.scale = size; bpy.ops.object.transform_apply(scale=True)
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
GD = srgb('#0b1f19'); CREAM = srgb('#efe6d2'); MINT = srgb('#5df8b6'); GOLD = srgb('#e7b65a'); RED = srgb('#ff5e75'); APPG = srgb('#10844a')
M_floor = mat('floor', srgb('#0f2a22'), rough=0.28, coat=0.5)
M_phone = mat('phone', srgb('#111614'), rough=0.22, metal=0.7, coat=0.7)
M_frame = mat('pframe', srgb('#a9b2ae'), rough=0.2, metal=1.0)
M_paper = mat('paper', srgb('#f4f0e4'), rough=0.75)
M_bag = mat('bag', srgb('#b98a55'), rough=0.85)
M_shelf = mat('shelf', srgb('#d9d2c0'), rough=0.5, coat=0.2)
M_dark = mat('dark', srgb('#0a120f'), rough=0.5)
M_mint = mat('mintglow', MINT, rough=0.4, emit=MINT, estr=6.0)
M_minthalf = mat('mintsoft', MINT, rough=0.4, emit=MINT, estr=1.6)
M_red = mat('redglow', RED, rough=0.4, emit=RED, estr=5.0)
M_gold = mat('gold', GOLD, rough=0.25, metal=1.0)
M_pin = mat('pinmetal', srgb('#c9ced0'), rough=0.18, metal=1.0)
M_green = mat('instagreen', APPG, rough=0.3, coat=0.6)
M_printer = mat('printer', srgb('#e8e6e0'), rough=0.35, coat=0.4)
M_string = mat('string', srgb('#d8cfb8'), rough=0.9)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (*srgb('#0b2019'), 1); bgn.inputs[1].default_value = 0.22
bpy.ops.mesh.primitive_plane_add(size=400, location=(60, 0, 0)); bpy.context.object.data.materials.append(M_floor)
def emptyo(name, loc, parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e
def area(name, loc, rot, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object; l.name = name; l.data.energy = energy; l.data.size = size; l.data.color = color; return l
def rig(x, k=1.0):
    area('key%d' % x, (x - 2.5, -4, 4.5), (R(48), 0, R(-30)), 900 * k, 4, (1.0, 0.95, 0.88))
    area('rim%d' % x, (x + 2.5, 3, 3.5), (R(-55), 0, R(150)), 800 * k, 3, (0.55, 1.0, 0.8))
    area('fill%d' % x, (x + 4, -2.5, 2.5), (R(65), 0, R(60)), 220 * k, 5, (0.85, 0.95, 1.0))
def cyl(name, r, d, loc, m, rot=(0, 0, 0), parent=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o
def sph(name, r, loc, m, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o
def tex(name, img, emit=False, estr=1.5, alpha=False, rough=0.5):
    m = mat(name, (1, 1, 1), rough=rough, img=TEX + img, img_emit=emit, estr=estr, alpha_img=alpha)
    return m
def popin(o, t, s=1.0, t_out=None, dur=0.16):
    seq = [(0, (0, 0, 0)), (t, (0, 0, 0)), (t + dur, (s * 1.15,) * 3), (t + dur + 0.12, (s,) * 3)]
    if t_out: seq += [(t_out, (s,) * 3), (t_out + 0.18, (0, 0, 0))]
    kf(o, 'scale', seq)
anchors = {}
def anchor(name, loc, parent=None):
    anchors[name] = emptyo('a_' + name, loc, parent); return anchors[name]
SCR = {}
def phone(name, loc, rot, screens, scale=1.0):
    P = emptyo(name, loc); P.rotation_euler = rot; P.scale = (scale,) * 3
    box(name + '_body', (0.78, 0.09, 1.6), (0, 0, 0), M_phone, bevel=0.07, parent=P)
    box(name + '_rim', (0.8, 0.07, 1.62), (0, 0, 0), M_frame, bevel=0.07, parent=P)
    for key, (img, rng) in screens.items():
        m = SCR.get(img) or tex('s_' + img, img, emit=True, estr=1.4, rough=0.15)
        SCR[img] = m
        s = plane(name + '_' + key, 0.7, 1.45, (0, -0.0465, 0), m, parent=P); vis(s, rng)
    return P
# ================= SET A (x=0): hero phones =================
rig(0)
A_ = SH['anim']
PN = phone('pn', (-0.48, 0, 1.02), (R(4), 0, R(9)), {'cart': ('scr_n.png', [[0, 4.2], [6.3, 53.6]]), 'lock': ('lock_n.png', [[4.2, 6.3]])})
PY = phone('py', (0.48, 0, 1.02), (R(4), 0, R(-9)), {'cart': ('scr_y.png', [[0, 4.2], [6.3, 6.72]]), 'lock': ('lock_y.png', [[4.2, 6.3]]), 'hi': ('scr_yhi.png', [[6.72, 53.6]]), 'buy': ('scr_buy.png', [[53.6, None]])})
kf(PN, 'location', [(0, (-0.48, 0, 1.0)), (0.3, (-0.48, 0, 1.0)), (0.42, (-0.48, 0, 1.08)), (0.6, (-0.48, 0, 1.0)), (7.7, (-0.48, 0, 1.0)), (7.85, (-0.48, 0, 1.13)), (8.0, (-0.48, 0, 1.0)), (8.12, (-0.48, 0, 1.09)), (8.26, (-0.48, 0, 1.0))])
kf(PY, 'location', [(0, (0.48, 0, 1.0)), (0.32, (0.48, 0, 1.0)), (0.44, (0.48, 0, 1.08)), (0.62, (0.48, 0, 1.0)), (53.6, (0.48, 0, 1.0)), (53.62, (0.0, 0, 1.0))], 'LINEAR')
wob = [(0, (R(4), 0, R(-9))), (6.7, (R(4), 0, R(-9)))]
for i in range(8):
    wob.append((6.74 + i * 0.07, (R(4), R(3.5 if i % 2 else -3.5) * (1 - i / 9), R(-9))))
wob += [(7.4, (R(4), 0, R(-9))), (53.6, (R(4), 0, R(-9))), (53.62, (R(2), 0, 0))]
kf(PY, 'rotation_euler', wob)
for c in PN.children:
    if c.name in ('pn_body', 'pn_rim'): vis(c, [[0, 53.6]])
anchor('pn', (0, -0.1, 0.95), PN); anchor('py', (0, -0.1, 0.95), PY); anchor('pyprice', (-0.12, -0.1, -0.05), PY); anchor('buybtn', (0, -0.1, -0.52), PY)
# ================= SET B (x=12): map =================
X = 12; rig(X, 0.6)
mp = plane('map', 6, 6, (X, 0, 0.002), tex('mapm', 'map.png', emit=True, estr=0.8), rot=(0, 0, 0))
store = emptyo('store', (X, 0.6, 0))
cyl('st_base', 0.32, 0.04, (0, 0, 0.02), M_minthalf, parent=store)
pin = emptyo('pin', (X, 0.6, 0))
sph('pin_head', 0.2, (0, 0, 0.75), M_mint, parent=pin)
bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0.0, depth=0.55, location=(0, 0, 0.45), rotation=(R(180), 0, 0)); o = bpy.context.object; o.data.materials.append(M_mint); o.parent = pin
kf(pin, 'location', [(0, (X, 0.6, 1.5)), (2.75, (X, 0.6, 1.5)), (3.0, (X, 0.6, 0)), (3.08, (X, 0.6, 0.12)), (3.16, (X, 0.6, 0))])
for nm, hx, hy in (('hn', -1.6, -1.4), ('hy', 1.7, -1.2)):
    H = emptyo(nm, (X + hx, hy, 0))
    box(nm + 'b', (0.5, 0.5, 0.42), (0, 0, 0.21), M_shelf, bevel=0.02, parent=H)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.42, depth=0.3, location=(0, 0, 0.57), rotation=(0, 0, R(45))); o = bpy.context.object; o.data.materials.append(M_dark); o.parent = H
    cu = bpy.data.curves.new(nm + 'rt', 'CURVE'); cu.dimensions = '3D'; sp = cu.splines.new('BEZIER'); sp.bezier_points.add(1)
    for p, co in zip(sp.bezier_points, [(X + hx, hy + 0.3, 0.05), (X, 0.6, 0.05)]):
        p.co = co; p.handle_left_type = p.handle_right_type = 'AUTO'
    cu.bevel_depth = 0.035; ob = bpy.data.objects.new(nm + 'rt', cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(M_mint)
    cu.bevel_factor_end = 0.0; cu.keyframe_insert('bevel_factor_end', frame=F(2.7)); cu.bevel_factor_end = 1.0; cu.keyframe_insert('bevel_factor_end', frame=F(3.5))
anchor('store', (X, 0.6, 1.2)); anchor('hn', (X - 1.6, -1.4, 0.9)); anchor('hy', (X + 1.7, -1.2, 0.9))
# ================= SET C (x=24): report =================
X = 24; rig(X)
RP = emptyo('report', (X, 0, 1.25))
plane('rep', 1.35, 1.8, (0, 0, 0), tex('repm', 'report.png', rough=0.6), parent=RP)
box('repback', (1.37, 0.01, 1.82), (0, 0.008, 0), M_paper, parent=RP)
kf(RP, 'rotation_euler', [(8.6, (R(-25), R(-30), R(40))), (9.25, (R(4), R(2), R(-6))), (11.1, (R(2), 0, R(-3)))])
kf(RP, 'location', [(8.6, (X + 1.2, -1.0, 2.6)), (9.25, (X, 0, 1.25)), (11.1, (X, 0, 1.25))])
anchor('rep', (0, -0.05, 1.0), RP)
# ================= SET D (x=36): grid of 437 phones =================
X = 36; rig(X, 0.45)
import bmesh
NX, NY, SP = 19, 23, 0.62
bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
bmb = bmesh.new()
import random
rnd = random.Random(11)
for i in range(NX):
    for j in range(NY):
        cx = (i - (NX - 1) / 2) * SP; cy = (j - (NY - 1) / 2) * SP * 1.75
        bmesh.ops.create_cube(bmb, size=1.0, matrix=__import__('mathutils').Matrix.Translation((cx, cy, 0.03)) @ __import__('mathutils').Matrix.Diagonal((0.42, 0.86, 0.05, 1)))
        v = rnd.randrange(8); u0, u1 = v / 8 + 0.004, (v + 1) / 8 - 0.004
        vs = [bm.verts.new((cx + dx * 0.19, cy + dy * 0.4, 0.056)) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f = bm.faces.new(vs)
        for lp, uv in zip(f.loops, ((u0, 0.505), (u1, 0.505), (u1, 0.995), (u0, 0.995))): lp[uvl].uv = uv
me = bpy.data.meshes.new('gridscr'); bm.to_mesh(me); GS = bpy.data.objects.new('gridscr', me); bpy.context.collection.objects.link(GS); GS.location = (X, 0, 0)
meb = bpy.data.meshes.new('gridbody'); bmb.to_mesh(meb); GB = bpy.data.objects.new('gridbody', meb); bpy.context.collection.objects.link(GB); GB.location = (X, 0, 0); GB.data.materials.append(M_phone)
# grid screen shader
gm = bpy.data.materials.new('gridm'); gm.use_nodes = True; nt = gm.node_tree; N = nt.nodes; L = nt.links
for n in list(N): N.remove(n)
out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); L.new(em.outputs[0], out.inputs[0])
uvn = N.new('ShaderNodeUVMap'); img = bpy.data.images.load(TEX + 'atlas.png')
t0 = N.new('ShaderNodeTexImage'); t0.image = img; t1 = N.new('ShaderNodeTexImage'); t1.image = img
off = N.new('ShaderNodeVectorMath'); off.operation = 'ADD'; off.inputs[1].default_value = (0, -0.5, 0)
L.new(uvn.outputs[0], t0.inputs[0]); L.new(uvn.outputs[0], off.inputs[0]); L.new(off.outputs[0], t1.inputs[0])
geo = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
def val(name, seq):
    v = N.new('ShaderNodeValue'); v.name = name; v.label = name
    for t, x in seq:
        v.outputs[0].default_value = x; v.outputs[0].keyframe_insert('default_value', frame=F(t))
    return v
# light-up radius (distance from centre), flip x threshold, shutdown y threshold
dx = N.new('ShaderNodeMath'); dx.operation = 'SUBTRACT'; L.new(sep.outputs[0], dx.inputs[0]); dx.inputs[1].default_value = X
vlen = N.new('ShaderNodeCombineXYZ'); L.new(dx.outputs[0], vlen.inputs[0]); L.new(sep.outputs[1], vlen.inputs[1])
ln = N.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; L.new(vlen.outputs[0], ln.inputs[0])
onr = val('onr', [(0, -1), (11.08, 0.5), (13.6, 14)])
c_on = N.new('ShaderNodeMath'); c_on.operation = 'LESS_THAN'; L.new(ln.outputs[1], c_on.inputs[0]); L.new(onr.outputs[0], c_on.inputs[1])
flx = val('flx', [(0, -8), (15.5, -8), (16.7, 8)])
c_fl = N.new('ShaderNodeMath'); c_fl.operation = 'LESS_THAN'; L.new(dx.outputs[0], c_fl.inputs[0]); L.new(flx.outputs[0], c_fl.inputs[1])
offy = val('offy', [(0, -12), (42.9, -12), (44.0, 12)])
c_off = N.new('ShaderNodeMath'); c_off.operation = 'GREATER_THAN'; L.new(sep.outputs[1], c_off.inputs[0]); L.new(offy.outputs[0], c_off.inputs[1])
mixc = N.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; L.new(c_fl.outputs[0], mixc.inputs['Factor']); L.new(t0.outputs[0], mixc.inputs[6]); L.new(t1.outputs[0], mixc.inputs[7])
m1 = N.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; L.new(c_on.outputs[0], m1.inputs[0]); L.new(c_off.outputs[0], m1.inputs[1])
dim = val('dim', [(0, 2.4), (39.9, 2.4), (40.1, 0.7), (42.5, 0.7), (42.6, 2.0)])
m2 = N.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; L.new(m1.outputs[0], m2.inputs[0]); L.new(dim.outputs[0], m2.inputs[1])
L.new(mixc.outputs[2], em.inputs[0]); L.new(m2.outputs[0], em.inputs[1])
for fc in all_fcurves(gm.node_tree):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
GS.data.materials.append(gm)
# FTC spotlight
bpy.ops.object.light_add(type='SPOT', location=(X, -2, 5)); SPOT = bpy.context.object; SPOT.data.energy = 0; SPOT.data.spot_size = R(26); SPOT.data.spot_blend = 0.4; SPOT.data.color = (1, 0.97, 0.9)
kf(SPOT.data, 'energy', [(39.9, 0), (40.05, 6000), (44.5, 6000), (44.6, 0)])
kf(SPOT, 'rotation_euler', [(40.0, (R(-25), R(-20), 0)), (41.3, (R(-5), R(25), 0)), (42.5, (R(20), R(-5), 0)), (44.5, (R(5), 0, 0))])
anchor('grid', (X, 0, 0.4)); anchor('gridc', (X + 0.31, 0.54, 0.06))
# ================= SET E (x=48): shelf =================
X = 48; rig(X)
box('shelfb', (3.6, 0.7, 0.06), (X, 0, 0.6), M_shelf, bevel=0.01); box('shelfedge', (3.6, 0.04, 0.12), (X, -0.36, 0.6), M_dark)
BOXES = []
for k, (img, px) in enumerate([('box_crackers.png', -1.25), ('box_cereal.png', -0.42), ('box_coffee.png', 0.42), ('box_pasta.png', 1.25)]):
    B = emptyo('bx%d' % k, (X + px, 0, 0.63))
    box('bxb%d' % k, (0.6, 0.22, 0.86), (0, 0, 0.43), M_paper, parent=B)
    plane('bxf%d' % k, 0.6, 0.86, (0, -0.1115, 0.43), tex('bxm%d' % k, img, rough=0.4), parent=B)
    BOXES.append(B)
TAGM = {}
def tagobj(name, img, loc, rot=(R(90), 0, 0), s=0.42, parent=None):
    m = TAGM.get(img) or tex('tg_' + img, img, alpha=True, rough=0.5); TAGM[img] = m
    T = emptyo(name, loc, parent); T.rotation_euler = rot
    plane(name + 'p', s * 1.76, s, (0, 0, 0), m, rot=(0, 0, 0), parent=T)
    return T
sets = {0: ['tag0.png', 'tag2.png', 'tag4.png'], 1: ['tag_a.png', 'tag_b.png'], 2: ['tag_c.png', 'tag_d.png'], 3: ['tag_e.png']}
times = {0: [17.2, 17.9, 18.3], 1: [17.35, 18.05], 2: [17.5, 18.2], 3: [17.65]}
for k, imgs in sets.items():
    for n, img in enumerate(imgs):
        T = tagobj('st%d_%d' % (k, n), img, (X + [-1.25, -0.42, 0.42, 1.25][k] + n * 0.07, -0.42 - n * 0.03, 0.42 - n * 0.0 + 0.0), rot=(R(90), R(-4 + n * 5), 0), s=0.24)
        T.location.z = 0.42 + n * 0.16
        popin(T, times[k][n])
# five prices fan around crackers box
for n in range(5):
    ang = R(-62 + n * 31); rr = 0.78
    T = tagobj('fan%d' % n, 'tag%d.png' % n, (X - 1.25 + math.sin(ang) * rr, -0.55, 1.08 + math.cos(ang) * rr * 0.62), rot=(R(90), -ang * 0.35, 0), s=0.26)
    popin(T, 20.25 + n * 0.21)
anchor('shelf', (X, -0.3, 1.7)); anchor('crackers', (X - 1.25, -0.3, 1.95)); anchor('b4', (X + 1.25, -0.3, 1.55))
# ================= SET F (x=60): AI network + chip =================
X = 60; rig(X, 0.35)
CH = emptyo('chip', (X, 0, 0.12))
box('chipb', (1.1, 1.1, 0.14), (0, 0, 0), M_dark, bevel=0.02, parent=CH)
plane('chipt', 1.0, 1.0, (0, 0, 0.0705), tex('chipm', 'chip.png', emit=True, estr=1.2), rot=(0, 0, 0), parent=CH)
for s in range(4):
    for q in range(10):
        a = (q - 4.5) * 0.1
        loc = [(a, -0.62, -0.02), (a, 0.62, -0.02), (-0.62, a, -0.02), (0.62, a, -0.02)][s]
        box('pin%d_%d' % (s, q), (0.04, 0.14, 0.02) if s < 2 else (0.14, 0.04, 0.02), loc, M_gold, parent=CH)
rnd = random.Random(4); NODES = []
for k in range(40):
    p = Vector((X + rnd.uniform(-2.6, 2.6), rnd.uniform(-1.0, 3.0), rnd.uniform(0.8, 3.2)))
    s = sph('nd%d' % k, rnd.uniform(0.035, 0.07), p, M_mint if k % 3 else M_minthalf); NODES.append(s)
    popin(s, 22.15 + k * 0.035, 1.0)
def link(a, b, name, m):
    d = b - a; L_ = d.length
    o = cyl(name, 0.008, L_, (a + b) / 2, m, verts=8)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = d.to_track_quat('Z', 'Y'); return o
EDGES = []
for k in range(40):
    for j in range(k + 1, 40):
        if (NODES[k].location - NODES[j].location).length < 1.3 and len(EDGES) < 90:
            EDGES.append((k, j)); link(NODES[k].location, NODES[j].location, 'ed%d_%d' % (k, j), M_minthalf)
for n, (k, j) in enumerate(EDGES[:24]):
    pz = sph('pulse%d' % n, 0.035, NODES[k].location, M_red)
    t0 = 22.4 + (n % 8) * 0.35; a, b = NODES[k].location.copy(), NODES[j].location.copy()
    kf(pz, 'location', [(t0, a), (t0 + 0.5, b), (t0 + 1.4, a), (t0 + 1.9, b), (t0 + 2.8, a)], 'LINEAR')
# Instacart block with socket
IB = emptyo('iblock', (X + 2.6, 0, 0))
box('ib1', (1.5, 2.6, 0.32), (0, 0, 0.16), M_green, bevel=0.03, parent=IB)
box('ibsock', (1.16, 1.16, 0.05), (-0.0, 0.0, 0.335), M_dark, parent=IB)
kf(CH, 'location', [(25.3, (X, 0, 0.12)), (25.9, (X + 1.3, 0, 1.0)), (26.45, (X + 2.6, 0, 0.42)), (26.55, (X + 2.6, 0, 0.36))])
kf(CH, 'rotation_euler', [(25.3, (0, 0, 0)), (25.9, (R(-15), R(10), R(30))), (26.45, (0, 0, R(0))), (27.2, (0, 0, 0))])
glow = plane('ibglow', 1.6, 2.7, (X + 2.6, 0, 0.004), M_mint, rot=(0, 0, 0)); vis(glow, [[26.5, 27.3]])
anchor('chip', (X, 0, 0.6)); anchor('iblock', (X + 2.6, 0, 1.1))
# ================= SET G (x=72): price tests on five phones =================
X = 72; rig(X)
TG = []
for k in range(5):
    px = X + (k - 2) * 1.0
    box('ped%d' % k, (0.62, 0.62, 0.5), (px, 0, 0.25), M_shelf, bevel=0.02)
    p = phone('tp%d' % k, (px, 0, 0.5 + 0.8 * 0.6), (0, 0, 0), {'s': ('scr_n.png', [[0, None]])}, scale=0.6)
    TG.append(p)
    seq = ['tag0.png', 'tag1.png', 'tag2.png', 'tag3.png', 'tag4.png']
    steps = [27.6 + k * 0.18, 28.6 + k * 0.22, 29.6 + k * 0.2, 30.7 + k * 0.15, 31.4 + k * 0.12]
    for n, img in enumerate(seq):
        T = tagobj('tt%d_%d' % (k, n), img, (px + 0.2, -0.18, 1.62), rot=(R(90), R(8), 0), s=0.22)
        end = steps[n + 1] if n + 1 < len(steps) else None
        vis(T, [[steps[n], end]])
        for c in T.children: vis(c, [[steps[n], end]])
        kf(T, 'scale', [(steps[n], (0.6, 0.6, 0.6)), (steps[n] + 0.12, (1.12,) * 3), (steps[n] + 0.22, (1, 1, 1))])
# last phone gives up and falls backwards at 32.3
P4 = TG[4]
kf(P4, 'rotation_euler', [(32.1, (0, 0, 0)), (32.25, (R(-8), 0, 0)), (32.65, (R(92), 0, 0)), (32.75, (R(84), 0, 0)), (32.85, (R(90), 0, 0))])
kf(P4, 'location', [(32.1, P4.location.copy()), (32.65, (P4.location.x, 0.45, 0.56)), (32.85, (P4.location.x, 0.45, 0.55))])
anchor('row', (X, 0, 1.9)); anchor('p4tag', (X + 2.2, -0.2, 1.9)); anchor('p2', (X, -0.2, 1.75))
# ================= SET H (x=84): bags + receipt printer =================
X = 84; rig(X)
for k, (bx, s) in enumerate([(-1.1, 1.0), (-0.35, 1.0), (0.4, 0.7), (0.95, 0.7)]):
    Bg = emptyo('bag%d' % k, (X + bx, 0.2, 0))
    box('bagb%d' % k, (0.55 * s, 0.34 * s, 0.75 * s), (0, 0, 0.375 * s), M_bag, bevel=0.01, parent=Bg)
    for q in range(2):
        img = ['box_crackers.png', 'box_cereal.png', 'box_coffee.png', 'box_pasta.png'][(k + q) % 4]
        bb = emptyo('bagi%d_%d' % (k, q), ((q - 0.5) * 0.2 * s, -0.02, 0.62 * s), Bg); bb.rotation_euler = (0, R(-8 + q * 14), 0)
        box('bagib%d_%d' % (k, q), (0.2 * s, 0.1 * s, 0.34 * s), (0, 0, 0.17 * s), M_paper, parent=bb)
        plane('bagif%d_%d' % (k, q), 0.2 * s, 0.34 * s, (0, -0.0505 * s, 0.17 * s), tex('bgm%d_%d' % (k, q), img, rough=0.4), parent=bb)
    popin(Bg, 33.25 + k * 0.17)
PR = emptyo('printer', (X + 2.6, 1.0, 0))
box('prb', (1.3, 0.9, 0.55), (0, 0, 0.275), M_printer, bevel=0.06, parent=PR)
box('prslot', (1.08, 0.08, 0.03), (0, -0.452, 0.36), M_dark, parent=PR)
RC = emptyo('receipt', (X + 2.6, 1.0, 0.0))
rcp = plane('rcp', 1.0, 4.8, (0, 0, 0), tex('rcm', 'receipt.png', rough=0.7), rot=(0, 0, R(180)), parent=RC); vis(rcp, [[35.25, None]])
# receipt (texture top = header) slides out of printer along -y; header leads
kf(RC, 'location', [(35.25, (X + 2.6, 2.4, 0.012)), (37.2, (X + 2.6, -1.85, 0.012)), (38.1, (X + 2.6, -1.95, 0.012))])
anchor('bags', (X - 0.1, 0.2, 1.2)); anchor('rctotal', (X + 2.6, 0.15, 0.05))
# ================= SET I (x=96): dice =================
X = 96; rig(X)
DM = [tex('die%d' % n, 'die%d.png' % n, rough=0.35) for n in range(1, 7)]
def die(name):
    bpy.ops.mesh.primitive_cube_add(size=0.5); o = bpy.context.object; o.name = name
    for m in DM: o.data.materials.append(m)
    for i, p in enumerate(o.data.polygons): p.material_index = i
    me = o.data; uvl = me.uv_layers.active.data
    for p in me.polygons:
        for li, uv in zip(p.loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))): uvl[li].uv = uv
    md = o.modifiers.new('bv', 'BEVEL'); md.width = 0.04; md.segments = 4; md.limit_method = 'ANGLE'
    return o
D1 = die('d1'); D2 = die('d2')
kf(D1, 'location', [(38.1, (X - 1.6, -0.6, 1.6)), (38.5, (X - 0.7, -0.2, 0.25)), (38.75, (X - 0.4, -0.1, 0.7)), (39.05, (X - 0.3, 0, 0.25)), (39.3, (X - 0.28, 0, 0.32)), (39.45, (X - 0.27, 0, 0.25))])
kf(D1, 'rotation_euler', [(38.1, (R(30), R(60), 0)), (38.5, (R(160), R(140), R(40))), (39.05, (R(270), R(180), R(70))), (39.45, (R(270), R(180), R(80)))])
kf(D2, 'location', [(38.1, (X + 1.7, -0.4, 1.9)), (38.55, (X + 0.8, 0, 0.25)), (38.85, (X + 0.55, 0.05, 0.62)), (39.15, (X + 0.35, 0.1, 0.25)), (39.35, (X + 0.33, 0.1, 0.3)), (39.5, (X + 0.32, 0.1, 0.25))])
kf(D2, 'rotation_euler', [(38.1, (R(-20), R(30), R(10))), (38.55, (R(-150), R(-90), R(50))), (39.15, (R(-180), R(-180), R(85))), (39.5, (R(-180), R(-180), R(95)))])
anchor('dice', (X, 0, 0.9))
# ================= SET J (x=108): the tag + NY warning =================
X = 108; rig(X, 0.35)
area('redrim', (X + 1.5, 1.5, 2.2), (R(-60), 0, R(140)), 0, 2, (1, 0.25, 0.3))
kf(bpy.data.objects['redrim'].data, 'energy', [(44.6, 0), (45.3, 900), (46.0, 300), (46.6, 900), (49.4, 600)])
HT = emptyo('htag', (X, 0, 1.3))
T = tagobj('bigtag', 'tag_ny.png', (0, 0, 0), rot=(R(90), 0, 0), s=0.75, parent=HT)
cyl('tstring', 0.006, 1.6, (-0.62, 0.0, 0.8), M_string, rot=(0, R(-22), 0), parent=HT)
kf(HT, 'rotation_euler', [(44.6, (0, 0, R(-14))), (46.0, (0, 0, R(10))), (47.6, (0, 0, R(-6))), (49.3, (0, 0, R(4))), (51.5, (0, 0, R(-2))), (55.6, (0, 0, 0))])
WN = emptyo('warn', (0.2, -0.02, -0.12), HT)
plane('warnp', 0.98, 0.46, (0, 0, 0), tex('warnm', 'warn.png', rough=0.4), parent=WN)
WN.rotation_euler = (0, 0, 0)
kf(WN, 'scale', [(0, (0, 0, 0)), (49.42, (0, 0, 0)), (49.52, (1.25, 1.25, 1.25)), (49.62, (0.97, 0.97, 0.97)), (49.7, (1, 1, 1))])
kf(WN, 'rotation_euler', [(49.42, (0, R(-14), 0)), (49.55, (0, R(-3), 0))])
anchor('htag', (0, -0.05, 0.62), HT); anchor('warn', (0.2, -0.05, 0.2), HT)
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
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/ct/scene.blend')
from bpy_extras.object_utils import world_to_camera_view
proj = {}
for fr in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(fr)
    proj[fr] = {n: [round(c.x, 4), round(1 - c.y, 4), round(c.z, 3)] for n, e in anchors.items() for c in [world_to_camera_view(sc, cam, e.matrix_world.translation)]}
json.dump(proj, open(ROOT + '/ct/proj.json', 'w'))
print('SCENE OK', sc.frame_end)
