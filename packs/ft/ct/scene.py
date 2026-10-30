import bpy, math, json, os
from mathutils import Vector
ROOT = os.environ.get('CT_ROOT', '/home/user/ft')
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
VI = srgb('#8b5cf6'); AM = srgb('#ffb54c'); WHITE = (1, 1, 1)
M_table = mat('table', srgb('#1a1633'), rough=0.36, coat=0.35)
M_bg = mat('bg', srgb('#0e0b1f'), rough=0.9)
M_phone = mat('phone', srgb('#1b1d24'), rough=0.22, metal=0.7, coat=0.7)
M_frame = mat('pframe', srgb('#9aa0ac'), rough=0.2, metal=1.0)
M_plane = mat('planebody', srgb('#eef0f4'), rough=0.3, coat=0.6)
M_planedark = mat('planedark', srgb('#2a2d38'), rough=0.4, metal=0.3)
M_glass = mat('glass', srgb('#14182a'), rough=0.05, coat=1.0)
M_stand = mat('stand', srgb('#2b2740'), rough=0.3, metal=0.6)
M_cable = mat('cable', VI, rough=0.3, emit=VI, estr=6.0)
M_wood = mat('wood', srgb('#5a3a22'), rough=0.45, coat=0.3)
M_gold = mat('gold', AM, rough=0.25, metal=1.0)
M_paper = mat('paper', srgb('#f4f2fa'), rough=0.7)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (*srgb('#120f26'), 1); bgn.inputs[1].default_value = 0.3
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); bpy.context.object.data.materials.append(M_table)
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 12, 10), rotation=(R(90), 0, 0)); bpy.context.object.data.materials.append(M_bg)
def area(name, loc, rot, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    l = bpy.context.object; l.name = name; l.data.energy = energy; l.data.size = size; l.data.color = color; return l
area('key', (-2.5, -4, 4.5), (R(48), 0, R(-30)), 1000, 4, (1.0, 0.96, 0.92))
area('rim', (2.5, 3, 3.5), (R(-55), 0, R(150)), 900, 3, (0.7, 0.55, 1.0))
area('fill', (4, -2.5, 2.5), (R(65), 0, R(60)), 260, 5, (0.85, 0.9, 1.0))
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
    bv = ob.modifiers.new('bv', 'BEVEL'); bv.width = 0.006; bv.segments = 2
    return ob
def tex(name, img, alpha=False, emit=False, estr=1.5):
    return mat(name, (1, 1, 1), rough=0.55, img=TEX + img, alpha_img=alpha, img_emit=emit, estr=estr)
# ---------- hero phone ----------
PH = emptyo('phone', A['phone_loc'][0][1])
box('ph_body', (0.78, 0.09, 1.6), (0, 0, 0), M_phone, bevel=0.07, parent=PH)
box('ph_band', (0.8, 0.07, 1.58), (0, 0.005, 0), M_frame, bevel=0.06, parent=PH)
for n, rng in A['screens'].items():
    s = plane('scr_' + n, 0.72, 1.49, (0, -0.048, 0), mat('m_' + n, (0, 0, 0), rough=0.12, img=TEX + n + '.png', img_emit=True, estr=1.5, coat=0.6), parent=PH)
    vis(s, [tuple(r) for r in rng])
kf(PH, 'location', [(t, tuple(v)) for t, v in A['phone_loc']])
kf(PH, 'rotation_euler', [(0, (0, 0, 0)), (34.55, (0, 0, 0)), (35.95, (0, 0, R(28))), (45.45, (0, 0, R(28))), (46.4, (0, 0, 0))])
# ---------- airplane model on stand ----------
AP = emptyo('airplane', A['plane_loc']); AP.rotation_euler = (0, 0, R(A['plane_rot']))
cyl('ap_stand', 0.025, 0.55, (0, 0, 0.275), M_stand, parent=AP)
cyl('ap_base', 0.18, 0.03, (0, 0, 0.015), M_stand, parent=AP)
PL = emptyo('plane_body', (0, 0, 0.62)); PL.parent = AP; PL.rotation_euler = (0, R(-6), 0)
cyl('pl_fus', 0.085, 1.3, (0, 0, 0), M_plane, rot=(0, R(90), 0), parent=PL)
sph('pl_nose', 0.085, (0.65, 0, 0), M_plane, scale=(1.6, 1, 1), parent=PL)
bpy.ops.mesh.primitive_cone_add(radius1=0.085, radius2=0.02, depth=0.32, location=(-0.81, 0, 0.02), rotation=(0, R(-90), 0), vertices=48)
o = bpy.context.object; o.data.materials.append(M_plane); bpy.ops.object.shade_smooth(); o.parent = PL
slab('pl_wings', [(0.12, 0.06), (-0.12, 0.72), (-0.24, 0.72), (-0.18, 0.06)], 0.02, M_plane, PL, mirror=True)
slab('pl_tailw', [(-0.66, 0.03), (-0.8, 0.26), (-0.87, 0.26), (-0.84, 0.03)], 0.014, M_plane, PL, mirror=True)
slab('pl_fin', [(-0.62, 0.06), (-0.84, 0.36), (-0.93, 0.36), (-0.9, 0.06)], 0.016, M_planedark, PL, axis='y')
for s in (1, -1):
    cyl('pl_eng%d' % s, 0.05, 0.2, (0.02, s * 0.32, -0.06), M_planedark, rot=(0, R(90), 0), parent=PL)
for k in range(9):
    sph('pl_win%d' % k, 0.012, (0.45 - k * 0.1, -0.083, 0.025), M_glass, parent=PL)
    sph('pl_winb%d' % k, 0.012, (0.45 - k * 0.1, 0.083, 0.025), M_glass, parent=PL)
# ---------- cable between phone and plane ----------
def cable(name, pts, parent=None):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.012; cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(ob); ob.data.materials.append(M_cable)
    if parent: ob.parent = parent
    return ob
p0 = Vector(A['phone_loc'][0][1]) + Vector((0.39, 0, -0.55)); p1 = Vector(A['plane_loc']) + Vector((0, 0, 0.3))
mid = (p0 + p1) / 2 + Vector((0, 0, -0.35))
CAB = cable('cable', [tuple(p0), tuple(mid), tuple(p1)])
vis(CAB, [tuple(r) for r in A['cable_on']])
h0 = cable('cable_a', [tuple(p0), tuple(p0 + Vector((0.18, 0, -0.3))), tuple(p0 + Vector((0.3, -0.05, -p0.z + 0.012)))])
h1 = cable('cable_b', [tuple(p1), tuple(p1 + Vector((-0.12, 0, -0.18))), tuple(p1 + Vector((-0.3, -0.05, -p1.z + 0.012)))])
h0.parent = PH; h0.matrix_parent_inverse = PH.matrix_world.inverted()
vis(h0, [tuple(A['cable_off'])]); vis(h1, [tuple(A['cable_off'])])
# ---------- calendar ----------
CAL = emptyo('cal', A['cal_loc']); CAL.rotation_euler = (0, 0, R(14))
plane('cal_f', 0.3, 0.32, (0, -0.05, 0.16), tex('m_cal', 'cal.png'), rot=(R(75), 0, 0), parent=CAL)
plane('cal_b', 0.3, 0.32, (0, 0.05, 0.16), M_paper, rot=(R(-75), 0, 0), parent=CAL)
popin(CAL, A['cal_t'], 1.0, A['cal_out'])
# ---------- boarding passes ----------
for k, (img, loc, rz) in enumerate([('bp1.png', (-0.72, -0.92, 0.003), 8), ('bp2.png', (-0.42, -1.0, 0.006), -6)]):
    bpz = plane('bp%d' % k, 0.4, 0.168, loc, tex('m_bp%d' % k, img), rot=(0, 0, R(rz)))
    t0 = A['bp_t'] + 0.35 * k
    kf(bpz, 'location', [(0, (loc[0], loc[1], 0.9)), (t0, (loc[0], loc[1], 0.9)), (t0 + 0.3, loc)])
    kf(bpz, 'rotation_euler', [(t0, (R(30), R(-20), R(rz + 40))), (t0 + 0.3, (0, 0, R(rz)))])
    vis(bpz, [(t0, None)])
# ---------- refund form, stamps, email ----------
FORM = plane('form', 0.45, 0.6, tuple(A['form_loc']), tex('m_form', 'form.png'), rot=(0, 0, R(-4)))
vis(FORM, [(A['form_t'], None)])
kf(FORM, 'location', [(0, (A['form_loc'][0], -2.5, 0.003)), (A['form_t'], (A['form_loc'][0], -2.5, 0.003)), (A['form_t'] + 0.4, tuple(A['form_loc']))])
for k, (t, rz, dx, dy) in enumerate(A['stamps']):
    st = plane('stamp%d' % k, 0.4, 0.142, (A['form_loc'][0] + dx, A['form_loc'][1] + dy, 0.006 + 0.002 * k), tex('m_st%d' % k, 'stamp.png', alpha=True), rot=(0, 0, R(rz)))
    kf(st, 'scale', [(0, (0, 0, 0)), (t - 0.08, (0, 0, 0)), (t - 0.07, (1.8, 1.8, 1.8)), (t, (1, 1, 1))], 'LINEAR')
EM = emptyo('email', A['email_loc']); EM.rotation_euler = (0, 0, R(-10))
plane('em_f', 0.42, 0.235, (0, 0, 0.13), tex('m_em', 'email.png'), rot=(R(78), 0, 0), parent=EM)
popin(EM, A['email_t'])
# ---------- tribunal zone ----------
TZ = emptyo('tribunal', A['trib_loc'])
DOC = plane('claim', 0.42, 0.56, (0, 0, 0.002), tex('m_claim', 'claim.png'), rot=(0, 0, R(5)), parent=TZ)
kf(DOC, 'location', [(0, (0, 0, 0.5)), (A['claim_t'] - 0.18, (0, 0, 0.5)), (A['claim_t'], (0, 0, 0.002))])
vis(DOC, [(A['claim_t'] - 0.18, None)])
cyl('gv_block', 0.11, 0.05, (0.42, -0.12, 0.025), M_wood, parent=TZ)
GV = emptyo('gavel', (0.09, -0.12, 0.14)); GV.parent = TZ
cyl('gv_head', 0.055, 0.2, (0, -0.33, 0.0), M_wood, rot=(0, R(90), 0), parent=GV)
cyl('gv_band1', 0.058, 0.02, (0.06, -0.33, 0), M_gold, rot=(0, R(90), 0), parent=GV)
cyl('gv_band2', 0.058, 0.02, (-0.06, -0.33, 0), M_gold, rot=(0, R(90), 0), parent=GV)
cyl('gv_handle', 0.016, 0.34, (0, -0.15, 0.0), M_wood, rot=(R(90), 0, 0), parent=GV)
kf(GV, 'rotation_euler', [(t, (R(a), 0, R(90))) for t, a in A['gavel']])
popin(TZ, A['claim_t'] - 0.25)
QC = emptyo('quote', A['quote_loc'])
plane('q_f', 0.62, 0.434, (0, 0, 0.25), tex('m_q', 'quote.png'), rot=(R(80), 0, 0), parent=QC)
popin(QC, A['quote_t'])
OR = emptyo('order', A['order_loc']); OR.rotation_euler = (0, 0, R(6))
plane('or_f', 0.5, 0.26, (0, 0, 0.14), tex('m_or', 'order.png'), rot=(R(76), 0, 0), parent=OR)
popin(OR, A['order_t'])
# ---------- anchors ----------
anchors = {}
for n, p in A['anchors'].items():
    anchors[n] = emptyo('anc_' + n, tuple(p))
anchors['phone'].parent = PH; anchors['phone'].location = (0, 0, 0.95)
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
