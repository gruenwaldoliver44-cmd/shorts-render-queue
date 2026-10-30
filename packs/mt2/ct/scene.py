import bpy, math, json, os
from mathutils import Vector
ROOT = os.environ.get('CT_ROOT', '/home/user/mt2')
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
import bmesh, random
from mathutils import Matrix
CYAN = srgb('#22e1fb'); IR = (1.0, 0.12, 0.22); GOLD = srgb('#ffb54c'); GRN = srgb('#3cdc78')
M_floor = mat('floor', srgb('#0b1220'), rough=0.3, coat=0.5)
M_phone = mat('phone', srgb('#14161c'), rough=0.22, metal=0.7, coat=0.7)
M_frame = mat('pframe', srgb('#b4bcc8'), rough=0.18, metal=1.0)
M_pill = mat('pill', srgb('#020203'), rough=0.08, coat=1.0)
M_lens = mat('lens', srgb('#10131c'), rough=0.05, metal=0.3, coat=1.0)
M_face = mat('face', srgb('#3a3f4c'), rough=0.42, coat=0.3)
M_cyan = mat('cyanglow', CYAN, rough=0.4, emit=CYAN, estr=5.0)
M_red = mat('redglow', IR, rough=0.4, emit=IR, estr=8.0)
M_gold = mat('gold', GOLD, rough=0.25, metal=1.0)
M_dark = mat('dark', srgb('#0c0f16'), rough=0.5)
M_paper = mat('paper', srgb('#f2f2f2'), rough=0.6)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (*srgb('#0a1222'), 1); bgn.inputs[1].default_value = 0.2
bpy.ops.mesh.primitive_plane_add(size=400, location=(60, 0, 0)); bpy.context.object.data.materials.append(M_floor)
def emptyo(name, loc, parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e
def area(name, loc, rot, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object; l.name = name; l.data.energy = energy; l.data.size = size; l.data.color = color; return l
def rig(x, k=1.0):
    return [area('key%d' % x, (x - 2.5, -4, 4.5), (R(48), 0, R(-30)), 800 * k, 4, (0.92, 0.95, 1.0)),
            area('rim%d' % x, (x + 2.5, 3, 3.5), (R(-55), 0, R(150)), 900 * k, 3, (0.45, 0.85, 1.0)),
            area('fill%d' % x, (x + 4, -2.5, 2.5), (R(65), 0, R(60)), 200 * k, 5, (0.85, 0.9, 1.0))]
def cyl(name, r, d, loc, m, rot=(0, 0, 0), parent=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth()
    if parent: o.parent = parent
    return o
def tex(name, img, emit=False, estr=1.5, alpha=False, rough=0.5):
    return mat(name, (1, 1, 1), rough=rough, img=TEX + img, img_emit=emit, estr=estr, alpha_img=alpha)
def popin(o, t, s=1.0, dur=0.16):
    kf(o, 'scale', [(0, (0, 0, 0)), (t, (0, 0, 0)), (t + dur, (s * 1.15,) * 3), (t + dur + 0.12, (s,) * 3)])
anchors = {}
def anchor(name, loc, parent=None):
    anchors[name] = emptyo('a_' + name, loc, parent); return anchors[name]
def ekey(m, seq):
    b = m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    for t, v in seq:
        b.default_value = v; b.keyframe_insert('default_value', frame=F(t))
    for fc in all_fcurves(m.node_tree):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
def lkey(l, seq):
    for t, v in seq:
        l.data.energy = v; l.data.keyframe_insert('energy', frame=F(t))
    for fc in all_fcurves(l.data):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
SCR = {}
def phone(name, loc, rot, screens, scale=1.0):
    P = emptyo(name, loc); P.rotation_euler = rot; P.scale = (scale,) * 3
    box(name + '_body', (0.78, 0.09, 1.6), (0, 0, 0), M_phone, bevel=0.07, parent=P)
    box(name + '_rim', (0.8, 0.07, 1.62), (0, 0, 0), M_frame, bevel=0.07, parent=P)
    for key, (img, rng) in screens.items():
        m = SCR.get(img) or tex('s_' + img, img, emit=True, estr=1.3, rough=0.15); SCR[img] = m
        s = plane(name + '_' + key, 0.72, 1.48, (0, -0.0465, 0), m, parent=P); vis(s, rng)
    pill = box(name + '_pill', (0.24, 0.004, 0.065), (0, -0.0487, 0.66), M_pill, bevel=0.03, parent=P)
    for k, (lx, m, r) in enumerate([(-0.07, M_lens, 0.017), (-0.025, M_lens, 0.008), (0.02, M_lens, 0.008), (0.07, M_lens, 0.017)]):
        cyl(name + '_lens%d' % k, r, 0.004, (lx, -0.0505, 0.66), m, rot=(R(90), 0, 0), parent=P, verts=24)
    return P
# ---------------- face relief ----------------
def hval(x, z):
    r2 = (x / 0.42) ** 2 + ((z - 0.65) / 0.6) ** 2
    if r2 >= 1: return None
    v = 0.26 * math.sqrt(1 - r2)
    v += 0.12 * math.exp(-(x / 0.055) ** 2) * (1 / (1 + math.exp(-(z - 0.5) * 40))) * (1 / (1 + math.exp((z - 0.82) * 30)))
    v += 0.04 * math.exp(-((x) ** 2 + (z - 0.53) ** 2) / 0.0012)
    for sx in (-1, 1):
        v -= 0.065 * math.exp(-((x - sx * 0.15) ** 2 + (z - 0.76) ** 2) / 0.005)
        v += 0.02 * math.exp(-((x - sx * 0.2) ** 2 + (z - 0.58) ** 2) / 0.01)
    v += 0.025 * math.exp(-((z - 0.86) ** 2) / 0.0008) * math.exp(-(x / 0.3) ** 2)
    v += 0.03 * math.exp(-((x / 0.12) ** 2) - ((z - 0.42) ** 2) / 0.0012)
    v -= 0.015 * math.exp(-((x / 0.14) ** 2) - ((z - 0.38) ** 2) / 0.0004)
    v += 0.03 * math.exp(-((x / 0.14) ** 2) - ((z - 0.27) ** 2) / 0.003)
    return v
def facemesh(name, step):
    bm = bmesh.new(); idx = {}
    nx = int(1.0 / step) + 1; nz = int(1.3 / step) + 1
    for i in range(nx):
        for j in range(nz):
            x = -0.5 + i * step; z = j * step; v = hval(x, z)
            if v is not None: idx[(i, j)] = bm.verts.new((x, -v, z - 0.65))
    for i in range(nx - 1):
        for j in range(nz - 1):
            q = [idx.get(k) for k in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            if all(q): bm.faces.new(q)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    return o
rnd = random.Random(7)
DOTP = []
for i in range(52):
    for j in range(68):
        x = -0.5 + (i + 0.5) / 52 + rnd.uniform(-0.004, 0.004); z = (j + 0.5) / 68 * 1.3 + rnd.uniform(-0.004, 0.004)
        v = hval(x, z)
        if v is not None: DOTP.append((x, v, z))
def dotsmesh(name, pts, r=0.0055, keys=None):
    """pts: list of basis positions; keys: dict name -> list of positions"""
    bm = bmesh.new(); groups = []
    for p in pts:
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation(p))
        groups.append(res['verts'])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    if keys:
        o.shape_key_add(name='Basis')
        nper = len(groups[0])
        for kn, kp in keys.items():
            sk = o.shape_key_add(name=kn)
            for gi, (p0, p1) in enumerate(zip(pts, kp)):
                d = Vector(p1) - Vector(p0)
                for vi in range(gi * nper, gi * nper + nper):
                    sk.data[vi].co = me.vertices[vi].co + d
    return o
def skey(o, kn, seq, interp='BEZIER'):
    k = o.data.shape_keys.key_blocks[kn]
    for t, v in seq:
        k.value = v; k.keyframe_insert('value', frame=F(t))
    for fc in all_fcurves(o.data.shape_keys):
        for kp in fc.keyframe_points: kp.interpolation = interp
# ================= SET A (x=0): hero phone =================
RA = rig(0)
PA = phone('pa', (0, 0, 1.0), (0, 0, 0), {'idle': ('lock_idle.png', [[0, 0.6], [54.48, 56.6]]), 'scan': ('lock_scan.png', [[0.6, 34.9]]), 'ok': ('lock_ok.png', [[34.9, 35.7]]),
                                          'home': ('home.png', [[35.7, 54.48]]), 'pass': ('passcode.png', [[56.6, None]])})
kf(PA, 'location', [(0, (0, 0.2, 0.35)), (0.95, (0, 0, 1.0)), (54.48, (0, 0, 1.0))])
kf(PA, 'rotation_euler', [(0, (R(-55), 0, R(8))), (0.95, (R(0), 0, 0)), (1.2, (R(2), 0, 0)), (54.48, (0, 0, 0)), (56.5, (0, R(-6), R(-10))), (56.75, (0, R(4), R(6))), (58.4, (0, 0, R(3)))])
LENS = Vector((0.07, -0.06, 1.66))
burst_n = 2400; bp0 = []; bp1 = []
for k in range(burst_n):
    a = rnd.uniform(0, 2 * math.pi); s = math.sqrt(rnd.uniform(0, 1)) * math.tan(R(32)); dist = rnd.uniform(0.25, 3.0)
    dvec = Vector((math.cos(a) * s, -1, math.sin(a) * s)).normalized()
    bp0.append(tuple(LENS + Vector((rnd.uniform(-0.002, 0.002), 0, rnd.uniform(-0.002, 0.002))))); bp1.append(tuple(LENS + dvec * dist))
BU = dotsmesh('burst', bp0, r=0.0035, keys={'out': bp1}); BU.data.materials.append(M_red)
skey(BU, 'out', [(2.08, 0), (3.3, 1)], 'LINEAR'); vis(BU, [[2.08, 3.96]])
glowA = cyl('lensglow', 0.012, 0.002, (0.07, -0.0525, 0.66), M_red, rot=(R(90), 0, 0), parent=PA, verts=24); vis(glowA, [[2.0, 3.96], [9.9, 11.2]])
anchor('dotproj', (0.07, -0.06, 0.66), PA); anchor('ircam', (-0.07, -0.06, 0.66), PA); anchor('flood', (-0.025, -0.06, 0.66), PA); anchor('pa', (0, -0.1, 0.4), PA)
# ================= SET B (x=14): the face =================
X = 14; RB = rig(X)
FB = emptyo('faceB', (X, 0, 0.9))
fs = facemesh('faceS', 0.012); fs.parent = FB; fs.data.materials.append(M_face)
# heat-map face
hm = bpy.data.materials.new('heat'); hm.use_nodes = True; N = hm.node_tree.nodes; L = hm.node_tree.links
for n in list(N): N.remove(n)
o_ = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); L.new(em.outputs[0], o_.inputs[0]); em.inputs[1].default_value = 1.5
tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])
mr = N.new('ShaderNodeMapRange'); mr.inputs[1].default_value = -0.12; mr.inputs[2].default_value = -0.4; L.new(sp.outputs[1], mr.inputs[0])
cr = N.new('ShaderNodeValToRGB'); L.new(mr.outputs[0], cr.inputs[0]); el = cr.color_ramp.elements
el[0].color = (0.02, 0.02, 0.25, 1); el[1].color = (1, 0.95, 0.4, 1)
e1 = el.new(0.35); e1.color = (0.0, 0.55, 1.0, 1); e2 = el.new(0.65); e2.color = (1.0, 0.15, 0.3, 1)
L.new(cr.outputs[0], em.inputs[0])
fh = bpy.data.objects.new('faceH', fs.data.copy()); bpy.context.collection.objects.link(fh); fh.parent = FB; fh.data.materials.clear(); fh.data.materials.append(hm)
vis(fs, [[0, 23.04], [25.26, None]]); vis(fh, [[23.04, 25.26]])
# dots on face (flat basis -> face key)
flat = [(x, -0.30, z - 0.65) for (x, v, z) in DOTP]; onf = [(x, -v - 0.004, z - 0.65) for (x, v, z) in DOTP]
DT = dotsmesh('dots', flat, keys={'face': onf}); DT.parent = FB
M_dots = mat('dotsm', IR, rough=0.4, emit=IR, estr=8.0); DT.data.materials.append(M_dots)
skey(DT, 'face', [(0, 1), (11.18, 1), (11.2, 0), (14.9, 0), (16.3, 1)])
ekey(M_dots, [(0, 8), (5.76, 8), (5.8, 0), (8.25, 0), (8.32, 10), (9.4, 8)])
# net (wireframe grid) flat -> face
bm = bmesh.new(); NI, NJ = 34, 44; vv = {}
for i in range(NI):
    for j in range(NJ):
        x = -0.5 + i / (NI - 1); z = j / (NJ - 1) * 1.3
        vv[(i, j)] = bm.verts.new((x, -0.30, z - 0.65))
for i in range(NI - 1):
    for j in range(NJ - 1): bm.faces.new([vv[(i, j)], vv[(i + 1, j)], vv[(i + 1, j + 1)], vv[(i, j + 1)]])
men = bpy.data.meshes.new('net'); bm.to_mesh(men); NT = bpy.data.objects.new('net', men); bpy.context.collection.objects.link(NT); NT.parent = FB
NT.shape_key_add(name='Basis'); skn = NT.shape_key_add(name='face')
for k, (i, j) in enumerate([(i, j) for i in range(NI) for j in range(NJ)]):
    x = -0.5 + i / (NI - 1); z = j / (NJ - 1) * 1.3; v = hval(x, z)
    skn.data[k].co = Vector((x, -(v if v is not None else 0.0) - 0.006, z - 0.65))
wf = NT.modifiers.new('wf', 'WIREFRAME'); wf.thickness = 0.0028; wf.use_replace = True
M_net = mat('netm', IR, rough=0.4, emit=IR, estr=3.0); NT.data.materials.append(M_net)
skey(NT, 'face', [(0, 0), (14.9, 0), (16.3, 1)])
kf(NT, 'scale', [(0, (0.02, 0.02, 0.02)), (11.3, (0.02, 0.02, 0.02)), (12.7, (1, 1, 1))])
vis(NT, [[11.2, 16.6]])
kf(DT, 'scale', [(0, (1, 1, 1)), (11.19, (1, 1, 1)), (11.2, (0.02, 0.02, 0.02)), (11.3, (0.02, 0.02, 0.02)), (12.7, (1, 1, 1))])
# stream dots phone -> face (S3)
PB = phone('pb', (X, -2.2, 0.95), (0, 0, R(180)), {'scan': ('lock_scan.png', [[0, None]])})
for c in PB.children: vis(c, [[3.96, 5.78]])
src = Vector((X - 0.07, -2.2 + 0.06, 0.95 + 0.66))
sub = DOTP[::4]
s0 = [tuple(src + Vector((rnd.uniform(-0.01, 0.01), 0, rnd.uniform(-0.01, 0.01))) - Vector((X, 0, 0.9))) for _ in sub]
s1 = [(x, -v - 0.004, z - 0.65) for (x, v, z) in sub]
FL = dotsmesh('fly', s0, r=0.009, keys={'hit': s1}); FL.parent = FB; FL.data.materials.append(M_red)
skey(FL, 'hit', [(4.0, 0), (5.0, 1)], 'LINEAR'); vis(FL, [[3.96, 5.1]])
vis(DT, [[4.95, 5.78], [8.25, 23.04], [31.02, None]])
# scan line
SCN = plane('scan', 1.3, 0.012, (X, -0.45, 1.6), M_cyan, rot=(0, 0, 0)); vis(SCN, [[20.44, 23.04]])
kf(SCN, 'location', [(20.9, (X, -0.45, 1.62)), (22.7, (X, -0.45, 0.2))], 'LINEAR')
SCN.rotation_euler = (R(90), 0, 0)
# turntable for heat face shot, keep straight otherwise
kf(FB, 'rotation_euler', [(23.04, (0, 0, R(-35))), (25.2, (0, 0, R(35))), (25.26, (0, 0, 0))])
FB.rotation_euler = (0, 0, 0)
for fc in all_fcurves(FB):
    for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'
# beard dots (build modifier)
bp = []
for k in range(1400):
    x = rnd.uniform(-0.36, 0.36); z = rnd.uniform(0.08, 0.5)
    v = hval(x, z)
    if v is None or (abs(x) < 0.09 and 0.36 < z < 0.47): continue
    if z > 0.48 - 0.25 * (abs(x) / 0.36) ** 0.5 + 0.0: continue
    bp.append((x, -v - 0.012 - rnd.uniform(0, 0.02), z - 0.65))
BD = dotsmesh('beard', bp, r=0.006); BD.parent = FB; M_beard = mat('beardm', CYAN, rough=0.4, emit=CYAN, estr=6.0); BD.data.materials.append(M_beard)
bd = BD.modifiers.new('build', 'BUILD'); bd.frame_start = F(44.6); bd.frame_duration = F(46.6) - F(44.6); bd.use_random_order = True; bd.seed = 3
vis(BD, [[44.5, 47.54]])
# lighting cues for darkness + flood
for l, base in zip(RB, (800, 900, 200)):
    lkey(l, [(0, base), (31.12, base), (31.3, base * 0.02), (41.0, base * 0.02), (41.12, base * 0.25), (43.0, base * 0.25), (43.04, base)])
bpy.ops.object.light_add(type='SPOT', location=(X - 0.2, -2.6, 1.7)); FLD = bpy.context.object; FLD.data.spot_size = R(40); FLD.data.spot_blend = 0.6; FLD.data.color = (0.75, 0.35, 1.0)
FLD.rotation_euler = (R(80), 0, R(-4)); lkey(FLD, [(0, 0), (32.5, 0), (32.9, 900), (36.2, 900), (36.28, 0)])
anchor('face', (0, -0.2, 0.5), FB); anchor('nose', (0, -0.42, -0.08), FB); anchor('eye', (-0.15, -0.2, 0.11), FB); anchor('chin', (0, -0.3, -0.42), FB); anchor('fcenter', (0, -0.3, 0.0), FB)
# ================= SET C (x=28): photo vs shape =================
X = 28; rig(X)
PH = emptyo('photoP', (X, 0, 0.5))
pc = plane('photo', 0.6, 0.8, (0, -0.0, 0.4), tex('photom', 'photo.png', rough=0.5), parent=PH)
box('photoback', (0.62, 0.008, 0.82), (0, 0.006, 0.4), M_paper, parent=PH)
pd = dotsmesh('pdots', [(x * 0.6, -0.01, (z / 1.3) * 0.8) for (x, v, z) in DOTP[::2]], r=0.0035); pd.parent = PH; pd.data.materials.append(M_red)
vis(pd, [[27.6, None]])
kf(PH, 'location', [(25.26, (X - 0.62, 0, 0.5)), (27.14, (X - 0.62, 0, 0.5)), (27.16, (X, 0, 0.5))], 'CONSTANT')
kf(PH, 'rotation_euler', [(0, (0, 0, 0)), (30.3, (0, 0, 0)), (30.62, (R(-92), 0, 0)), (30.72, (R(-86), 0, 0)), (30.8, (R(-90), 0, 0))])
FC = bpy.data.objects.new('faceC', fh.data); bpy.context.collection.objects.link(FC); FC.location = (X + 0.55, 0, 0.9); vis(FC, [[25.26, 27.16]])
kf(FC, 'rotation_euler', [(25.26, (0, 0, R(20))), (26.3, (0, 0, R(20))), (27.1, (0, 0, R(-40)))])
PC = phone('pc', (X, -1.5, 0.9), (0, 0, R(180)), {'scan': ('lock_scan.png', [[0, 28.5]]), 'fail': ('lock_fail.png', [[28.5, None]])}, scale=0.8)
for c in PC.children: vis(c, [[27.16, None]])
sh = [(0, (0, 0, R(180))), (28.5, (0, 0, R(180)))]
for i in range(7): sh.append((28.55 + i * 0.06, (0, 0, R(180 + (4 if i % 2 else -4) * (1 - i / 8)))))
sh.append((29.0, (0, 0, R(180)))); kf(PC, 'rotation_euler', sh)
anchor('photo', (0, -0.02, 0.75), PH); anchor('faceC', (X + 0.55, -0.3, 1.3)); anchor('pc', (0, 0.1, 0.5), PC)
# ================= SET D (x=42): chip + math =================
X = 42; rig(X, 0.5)
CH = emptyo('chip', (X, 0, 0.1))
box('chipb', (1.0, 1.0, 0.12), (0, 0, 0), M_dark, bevel=0.02, parent=CH)
plane('chipt', 0.92, 0.92, (0, 0, 0.0605), tex('chipm', 'chip.png', emit=True, estr=1.0), rot=(0, 0, 0), parent=CH)
for s in range(4):
    for q in range(10):
        a = (q - 4.5) * 0.09
        loc = [(a, -0.56, -0.02), (a, 0.56, -0.02), (-0.56, a, -0.02), (0.56, a, -0.02)][s]
        box('cp%d_%d' % (s, q), (0.035, 0.12, 0.02) if s < 2 else (0.12, 0.035, 0.02), loc, M_gold, parent=CH)
mpts = DOTP[::6]
m0 = [(X + x * 0.8, -v * 0.8, 1.0 + (z - 0.65) * 0.8 + 0.5) for (x, v, z) in mpts]
cols = 24
m1 = [(X - 0.6 + (k % cols) * (1.2 / cols), 0.0, 1.9 - (k // cols) * 0.06) for k in range(len(mpts))]
m2 = [(X + rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), 0.17) for _ in mpts]
MT = dotsmesh('math', m0, r=0.006, keys={'col': m1, 'in': m2}); MT.data.materials.append(M_cyan)
skey(MT, 'col', [(37.0, 0), (38.3, 1)]); skey(MT, 'in', [(39.1, 0), (39.9, 1)])
MT.data.shape_keys.key_blocks['in'].relative_key = MT.data.shape_keys.key_blocks['col']
vis(MT, [[36.28, 40.1]])
CG = plane('chipglow', 1.1, 1.1, (X, 0, 0.003), mat('grng', GRN, emit=GRN, estr=5.0), rot=(0, 0, 0)); vis(CG, [[40.2, 41.12]])
anchor('chip', (X, 0, 0.3)); anchor('math', (X, 0, 1.6))
# ================= SET E (x=56): wall of faces =================
X = 120; rig(X, 0.6)
lw = facemesh('faceLow', 0.05); lw.data.materials.append(M_face); lw.location = (X - 14.5 * 1.15, 0, 0.9)
a1 = lw.modifiers.new('ax', 'ARRAY'); a1.count = 30; a1.use_relative_offset = False; a1.use_constant_offset = True; a1.constant_offset_displace = (1.15, 0, 0)
a2 = lw.modifiers.new('az', 'ARRAY'); a2.count = 18; a2.use_relative_offset = False; a2.use_constant_offset = True; a2.constant_offset_displace = (0, 0, 1.45)
RF = bpy.data.objects.new('faceRed', lw.data); bpy.context.collection.objects.link(RF); RF.modifiers.clear()
RF.data = lw.data; RF.location = (X + 0.575, -0.01, 0.9 + 3 * 1.45)
M_rf = mat('redface', IR, rough=0.4, emit=IR, estr=3.0)
RF.data = RF.data.copy(); RF.data.materials.clear(); RF.data.materials.append(M_rf)
anchor('redface', (X + 0.575, -0.3, 0.9 + 3 * 1.45 + 0.7))
# ================= SET F (x=70): evil twin =================
X = 70; rig(X)
T1 = bpy.data.objects.new('twin1', fs.data); bpy.context.collection.objects.link(T1); T1.location = (X - 0.58, 0, 0.9)
T2 = bpy.data.objects.new('twin2', fs.data); bpy.context.collection.objects.link(T2); T2.location = (X + 0.58, 0, 0.9)
for k, sx in enumerate((-1, 1)):
    bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.0, depth=0.24, location=(X + 0.58 + sx * 0.2, -0.05, 1.62), rotation=(0, R(sx * 22), 0))
    hn = bpy.context.object; hn.name = 'horn%d' % k; hn.data.materials.append(M_red); bpy.ops.object.shade_smooth(); popin(hn, 53.4 + k * 0.08)
anchor('twin1', (X - 0.58, -0.3, 1.5)); anchor('twin2', (X + 0.58, -0.3, 1.7))
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
