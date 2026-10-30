import bpy, math, json, os
from mathutils import Vector
ROOT = os.environ.get('CT_ROOT', '/home/user/mc')
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
GOLD = srgb('#e4b85c'); CREAM = srgb('#f3ead6'); EMER = srgb('#0f2a22'); DEEP = srgb('#071712')
M_table = mat('table', srgb('#123328'), rough=0.38, coat=0.35)
M_bg = mat('bg', DEEP, rough=0.9)
M_gold = mat('gold', GOLD, rough=0.25, metal=1.0)
M_tv = mat('tvbody', srgb('#2b2622'), rough=0.45, coat=0.3)
M_tvtrim = mat('tvtrim', srgb('#151311'), rough=0.6)
M_jet = mat('jet', srgb('#7d8790'), rough=0.42, metal=0.35, coat=0.3)
M_jetdark = mat('jetdark', srgb('#3a4148'), rough=0.5, metal=0.3)
M_glass = mat('glass', srgb('#1a2a3a'), rough=0.05, metal=0.2, coat=1.0)
M_can = mat('can', srgb('#1f4fb5'), rough=0.22, metal=0.6, coat=0.5)
M_canlid = mat('canlid', srgb('#c9ced4'), rough=0.2, metal=1.0)
M_paper = mat('paper', CREAM, rough=0.7)
M_brief = mat('brief', srgb('#3b2416'), rough=0.4, coat=0.4)
M_mail = mat('mailbox', srgb('#2d4f8a'), rough=0.35, metal=0.4, coat=0.4)
M_wood = mat('wood', srgb('#5a3a22'), rough=0.45, coat=0.3)
M_glow = mat('glowgold', GOLD, emit=GOLD, estr=4.0)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (*srgb('#0b1f19'), 1); bgn.inputs[1].default_value = 0.3
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); bpy.context.object.data.materials.append(M_table)
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 12, 10), rotation=(R(90), 0, 0)); bpy.context.object.data.materials.append(M_bg)
def area(name, loc, rot, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object; l.name = name; l.data.energy = energy; l.data.size = size; l.data.color = color; return l
area('key', (-2.5, -4, 4.5), (R(48), 0, R(-30)), 900, 4, (1.0, 0.95, 0.88))
area('rim', (2.5, 3, 3.5), (R(-55), 0, R(150)), 700, 3, (1.0, 0.82, 0.5))
area('fill', (4, -2.5, 2.5), (R(65), 0, R(60)), 220, 5, (0.8, 0.9, 1.0))
def emptyo(name, loc):
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e); e.location = loc; return e
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
def popin(o, t, s=1.0, t_out=None):
    seq = [(0, (0, 0, 0)), (t, (0, 0, 0)), (t + 0.16, (s * 1.12,) * 3), (t + 0.28, (s,) * 3)]
    if t_out: seq += [(t_out, (s,) * 3), (t_out + 0.2, (0, 0, 0))]
    kf(o, 'scale', seq)
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
    bv = ob.modifiers.new('bv', 'BEVEL'); bv.width = 0.005; bv.segments = 2
    return ob
# ---------- TV ----------
TV = emptyo('tv', A['tv_loc'])
box('tv_body', (1.25, 0.9, 0.95), (0, 0.1, 0.55), M_tv, bevel=0.08, parent=TV)
box('tv_bezel', (1.08, 0.04, 0.78), (0, -0.36, 0.56), M_tvtrim, bevel=0.03, parent=TV)
for k, x in enumerate((-0.4, 0.4)): box('tv_foot%d' % k, (0.18, 0.5, 0.06), (x, 0.1, 0.03), M_tvtrim, parent=TV)
scr = {}
for n in ('s_ad', 's_ad2', 's_ad3'):
    scr[n] = plane('scr_' + n, 0.96, 0.72, (0, -0.385, 0.56), mat('m_' + n, (0, 0, 0), rough=0.1, img=TEX + n + '.png', img_emit=True, estr=1.6, coat=0.8), parent=TV)
    vis(scr[n], [tuple(r) for r in A['screens'][n]])
# ---------- jet (toy model) ----------
JET = emptyo('jet', (0, 0, 0))
J = emptyo('jetbody', (0, 0, 0)); J.parent = JET
cyl('j_fus', 0.075, 0.95, (0, 0, 0), M_jet, rot=(0, R(90), 0), parent=J)
bpy.ops.mesh.primitive_cone_add(radius1=0.075, radius2=0.0, depth=0.32, location=(0.635, 0, 0), rotation=(0, R(90), 0), vertices=48)
o = bpy.context.object; o.data.materials.append(M_jet); bpy.ops.object.shade_smooth(); o.parent = J
sph('j_canopy', 0.07, (0.3, 0, 0.06), M_glass, scale=(2.2, 0.8, 0.9), parent=J)
slab('j_wings', [(0.14, 0.05), (-0.16, 0.5), (-0.3, 0.5), (-0.22, 0.05)], 0.022, M_jet, J, mirror=True)
slab('j_tailw', [(-0.36, 0.04), (-0.5, 0.24), (-0.58, 0.24), (-0.55, 0.04)], 0.016, M_jet, J, mirror=True)
slab('j_fin', [(-0.3, 0.06), (-0.55, 0.3), (-0.62, 0.3), (-0.56, 0.06)], 0.016, M_jet, J, axis='y')
for s in (1, -1):
    cyl('j_intake%d' % s, 0.05, 0.28, (0.14, s * 0.1, 0.0), M_jetdark, rot=(0, R(90), 0), parent=J)
cyl('j_nozzle', 0.055, 0.08, (-0.5, 0, 0), M_jetdark, rot=(0, R(90), 0), parent=J)
TAG = plane('tag', 0.56, 0.288, (0.05, -0.2, -0.27), mat('m_tag', (1, 1, 1), rough=0.5, img=TEX + 'tag7m.png', alpha_img=True), rot=(R(90), 0, R(58)), parent=JET)
bpy.ops.mesh.primitive_cylinder_add(radius=0.003, depth=0.16, location=(0.05, -0.12, -0.1), rotation=(R(35), 0, 0)); st = bpy.context.object; st.data.materials.append(M_gold); st.parent = JET
vis(TAG, [tuple(A['tag_on'])]); vis(st, [tuple(A['tag_on'])])
kf(JET, 'location', [(t, tuple(v)) for t, v in A['jet_loc']])
kf(JET, 'rotation_euler', [(t, tuple(v)) for t, v in A['jet_rot']])
kf(JET, 'scale', [(t, (v, v, v)) for t, v in A['jet_scale']])
for k in range(0, int(A['end'] * 2) + 2):
    t = k * 0.5; J.location = (0, 0, 0.012 * math.sin(k * 1.7)); J.rotation_euler = (R(2.5 * math.sin(k * 1.3)), 0, 0)
    J.keyframe_insert('location', frame=F(t)); J.keyframe_insert('rotation_euler', frame=F(t))
# ---------- name card ----------
CARD = emptyo('card', A['card_loc']); CARD.rotation_euler = (0, 0, R(-12))
plane('card_f', 0.5, 0.233, (0, -0.06, 0.11), mat('m_card', (1, 1, 1), rough=0.6, img=TEX + 'card.png'), rot=(R(68), 0, 0), parent=CARD)
plane('card_b', 0.5, 0.233, (0, 0.06, 0.11), M_paper, rot=(R(-68), 0, 0), parent=CARD)
popin(CARD, A['card_t'])
# ---------- can tower ----------
CAN = emptyo('cans', A['cans_loc'])
(t0c, n0), (t1c, n1) = A['can_count'][-2], A['can_count'][-1]
for k in range(n1):
    cn = cyl('can%d' % k, 0.066, 0.24, (0, 0, 0.12 + 0.245 * k), M_can, parent=CAN, verts=32)
    a2 = cn.modifiers.new('arr2', 'ARRAY'); a2.use_relative_offset = False; a2.use_constant_offset = True; a2.constant_offset_displace = (0.14, 0, 0); a2.count = 3
    a3 = cn.modifiers.new('arr3', 'ARRAY'); a3.use_relative_offset = False; a3.use_constant_offset = True; a3.constant_offset_displace = (0, 0.14, 0); a3.count = 3
    u = k / max(n1 - 1, 1); tk = t0c + (t1c - t0c) * (u ** 0.7)
    vis(cn, [(tk, A['cans_on'][1])])
# ---------- rules sheet + notepad ----------
RU = plane('rules', 0.6, 0.8, tuple(A['rules_loc']), mat('m_rules', (1, 1, 1), rough=0.6, img=TEX + 'rules.png'), rot=(0, 0, R(4)))
kf(RU, 'location', [(t, tuple(v)) for t, v in A['rules_anim']])
for i, (sx, sy, px, py) in enumerate([(0.55, 0.01, 0, 0.075), (0.55, 0.01, 0, -0.075), (0.01, 0.16, 0.27, 0), (0.01, 0.16, -0.27, 0)]):
    hb = box('rules_hl%d' % i, (sx, sy, 0.004), (0, 0, 0), M_glow); hb.parent = RU; hb.location = (px, -0.119 + py, 0.003)
    vis(hb, [tuple(A['hl_on'])])
NP = plane('notepad', 0.55, 0.67, tuple(A['np_loc']), mat('m_np', (1, 1, 1), rough=0.6, img=TEX + 'notepad.png'), rot=(0, 0, R(-5)))
kf(NP, 'location', [(t, tuple(v)) for t, v in A['np_anim']])
# ---------- investors, check, envelope, mailbox ----------
for k in range(5):
    bx, by = A['brief_loc'][k]
    b = emptyo('brief%d' % k, (bx, by, 0))
    box('br_body%d' % k, (0.22, 0.07, 0.16), (0, 0, 0.08), M_brief, bevel=0.015, parent=b)
    box('br_h%d' % k, (0.08, 0.015, 0.03), (0, 0, 0.175), M_gold, parent=b)
    b.rotation_euler = (0, 0, R(-8 + 4 * k))
    popin(b, A['brief_t'] + 0.11 * k, 1.0, A['brief_out'])
CHK = plane('check', 0.5, 0.22, (0, 0, 0), mat('m_check', (1, 1, 1), rough=0.55, img=TEX + 'check.png'), rot=(R(80), 0, 0))
kf(CHK, 'location', [(t, tuple(v)) for t, v in A['check_anim']])
kf(CHK, 'rotation_euler', [(t, tuple(v)) for t, v in A['check_rot']])
vis(CHK, [tuple(A['check_on'])])
ENV = plane('env', 0.42, 0.245, (0, 0, 0), mat('m_env', (1, 1, 1), rough=0.6, img=TEX + 'env.png'), rot=(R(80), 0, 0))
kf(ENV, 'location', [(t, tuple(v)) for t, v in A['env_anim']])
kf(ENV, 'rotation_euler', [(t, tuple(v)) for t, v in A['env_rot']])
vis(ENV, [tuple(A['env_on'])])
MB = emptyo('mailbox', A['mb_loc'])
box('mb_post', (0.06, 0.06, 0.45), (0, 0, 0.225), M_tvtrim, parent=MB)
box('mb_box', (0.3, 0.42, 0.24), (0, 0, 0.56), M_mail, bevel=0.06, parent=MB)
box('mb_slot', (0.18, 0.01, 0.025), (0, -0.212, 0.6), M_tvtrim, parent=MB)
box('mb_flag', (0.02, 0.03, 0.16), (0.16, 0.05, 0.62), mat('flagred', srgb('#c0392b'), rough=0.4), parent=MB)
popin(MB, A['mb_t'], 1.0, A['mb_out'])
for k in range(5):
    cp = plane('coupon%d' % k, 0.24, 0.12, (0, 0, 0), mat('m_cp%d' % k, (1, 1, 1), rough=0.5, img=TEX + 'coupon.png'), rot=(R(60), 0, 0))
    e0 = Vector(A['coupon_from']); t0 = A['coupon_t'] + 0.06 * k
    ang = R(-60 + 30 * k); d = Vector((math.cos(ang) * 0.35, -0.15 - 0.05 * k, 0))
    kf(cp, 'location', [(t0, tuple(e0)), (t0 + 0.25, tuple(e0 + d * 0.6 + Vector((0, 0, 0.3)))), (t0 + 0.6, tuple(e0 + d + Vector((0, 0, 0.004 + 0.002 * k))))])
    kf(cp, 'rotation_euler', [(t0, (R(60), 0, 0)), (t0 + 0.6, (0, 0, R(-30 + 17 * k)))])
    vis(cp, [(t0, A['coupon_off'])])
# ---------- court ----------
CT_ = emptyo('court', A['court_loc'])
DOC = plane('court_doc', 0.5, 0.66, (0, 0.05, 0.002), mat('m_court', (1, 1, 1), rough=0.6, img=TEX + 'court.png'), rot=(0, 0, R(6)), parent=CT_)
kf(DOC, 'location', [(t, tuple(v)) for t, v in A['doc_anim']])
cyl('gv_block', 0.11, 0.05, (0.42, -0.1, 0.025), M_wood, parent=CT_)
GV = emptyo('gavel', (0.09, -0.1, 0.14)); GV.parent = CT_
cyl('gv_head', 0.055, 0.2, (0, -0.33, 0.0), M_wood, rot=(0, R(90), 0), parent=GV)
cyl('gv_band1', 0.058, 0.02, (0.06, -0.33, 0), M_gold, rot=(0, R(90), 0), parent=GV)
cyl('gv_band2', 0.058, 0.02, (-0.06, -0.33, 0), M_gold, rot=(0, R(90), 0), parent=GV)
cyl('gv_handle', 0.016, 0.34, (0, -0.15, 0.0), M_wood, rot=(R(90), 0, 0), parent=GV)
kf(GV, 'rotation_euler', [(t, (R(a), 0, R(90))) for t, a in A['gavel']])
popin(CT_, A['court_t'], 1.0)
# ---------- anchors ----------
anchors = {}
for n, p in A['anchors'].items():
    anchors[n] = emptyo('anc_' + n, tuple(p))
anchors['jet'].parent = JET; anchors['jet'].location = (0.05, 0, 0.22)
# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); bpy.context.collection.objects.link(cam); sc.camera = cam
tg = emptyo('camtgt', (0, 0, 0)); tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36
keys = SH['cam']
for i, k in enumerate(keys):
    f = F(k['t'])
    if k.get('cut') and i > 0:
        p = keys[i - 1]
        cam.location = p['pos']; cam.keyframe_insert('location', frame=f - 1); tg.location = p['tgt']; tg.keyframe_insert('location', frame=f - 1); cd.lens = p['lens']; cd.keyframe_insert('lens', frame=f - 1)
    cam.location = k['pos']; cam.keyframe_insert('location', frame=f)
    tg.location = k['tgt']; tg.keyframe_insert('location', frame=f)
    cd.lens = k['lens']; cd.keyframe_insert('lens', frame=f)
for idb in (cam, tg, cd):
    for fc in all_fcurves(idb):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.handle_left_type = 'AUTO_CLAMPED'; kp.handle_right_type = 'AUTO_CLAMPED'
cd.dof.use_dof = True; cd.dof.focus_object = tg; cd.dof.aperture_fstop = 4.0
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/ct/scene.blend')
from bpy_extras.object_utils import world_to_camera_view
proj = {}
for fr in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(fr)
    proj[fr] = {n: [round(c.x, 4), round(1 - c.y, 4), round(c.z, 3)] for n, e in anchors.items() for c in [world_to_camera_view(sc, cam, e.matrix_world.translation)]}
json.dump(proj, open(ROOT + '/ct/proj.json', 'w'))
print('SCENE OK', sc.frame_end)
