# MT4 smoke detector. Kitchen world at origin, ionization-chamber macro world at X=30 (scaled up ~40x).
import random
random.seed(7)
V = Vector
# ---------- world ----------
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (0.03, 0.035, 0.045, 1); bgn.inputs[1].default_value = 1.0
sc.cycles.samples = 64
sc.cycles.volume_step_rate = 2.0
def alight(name, loc, rot, size, energy, col=(1, 1, 1), shape='RECTANGLE', sy=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.color = col; ld.shape = shape; ld.size = size
    if sy: ld.size_y = sy
    o = bpy.data.objects.new(name, ld); link(o); o.location = loc; o.rotation_euler = rot; return o
def emis(name, col, s):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = col + (1,); e.inputs[1].default_value = s
    nt.links.new(e.outputs[0], nt.nodes['Material Output'].inputs[0]); return m, e
def sphere(name, r, loc, mat, seg=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat)
    bpy.ops.object.shade_smooth(); return o
def cyl(name, r, d, loc, mat, v=64, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o
def interp(o, path_sub, mode):
    for fc in fcurves(o):
        if path_sub in fc.data_path:
            for kp in fc.keyframe_points: kp.interpolation = mode
def smoke_mat(name, dens, col=(0.55, 0.55, 0.57), scale=3.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    pv = nt.nodes.new('ShaderNodeVolumePrincipled'); pv.inputs['Color'].default_value = col + (1,)
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 6
    sg = nt.nodes.new('ShaderNodeTexGradient'); sg.gradient_type = 'SPHERICAL'
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    mul2 = nt.nodes.new('ShaderNodeMath'); mul2.operation = 'MULTIPLY'; mul2.inputs[1].default_value = dens
    cr = nt.nodes.new('ShaderNodeMapRange'); cr.inputs[1].default_value = 0.35; cr.inputs[2].default_value = 0.8
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); nt.links.new(tc.outputs['Object'], sg.inputs['Vector'])
    nt.links.new(nz.outputs[0], cr.inputs[0]); nt.links.new(cr.outputs[0], mul.inputs[0]); nt.links.new(sg.outputs[0], mul.inputs[1])
    nt.links.new(mul.outputs[0], mul2.inputs[0]); nt.links.new(mul2.outputs[0], pv.inputs['Density'])
    nt.links.new(pv.outputs[0], nt.nodes['Material Output'].inputs['Volume']); return m

# ================= KITCHEN =================
kit, kobjs, kmn, kmx = place('kitchen', (0, -0.34, 0))
KY = kmn.y
print('KITCHEN bbox', [round(v, 3) for v in kmn], [round(v, 3) for v in kmx])
H = max(2.7, kmx.z + 0.04)
floor = plane('floor', 7, 7, (0, -2.0, 0), mat_ph('floor', 'laminate_floor_02', scale=4))
ceil = plane('ceil', 7, 7, (0, -2.0, H), mat_col('ceil', (0.86, 0.85, 0.83), rough=0.92), rot=(math.pi, 0, 0))
wm = mat_ph('wall', 'painted_plaster_wall', scale=2)
plane('wback', 7, H, (0, kmx.y + 0.01, H / 2), wm, rot=(math.pi / 2, 0, 0))
plane('wleft', 7, H, (-2.9, -2.0, H / 2), wm, rot=(math.pi / 2, 0, math.pi / 2))
plane('wright', 7, H, (2.9, -2.0, H / 2), wm, rot=(math.pi / 2, 0, math.pi / 2))
plane('wfront', 7, H, (0, -5.4, H / 2), wm, rot=(math.pi / 2, 0, 0))
wmat, _ = emis('window', (1.0, 0.97, 0.93), 2.0)
plane('window', 1.6, 1.3, (-2.885, -1.6, 1.55), wmat, rot=(math.pi / 2, 0, math.pi / 2))
alight('L_window', (-2.6, -1.6, 1.55), (0, math.radians(-90), 0), 1.6, 220, (1.0, 0.96, 0.9), sy=1.3)
alight('L_ceil1', (-0.6, -1.6, H - 0.02), (0, 0, 0), 0.5, 50, (1.0, 0.86, 0.7))
alight('L_ceil2', (1.0, -2.6, H - 0.02), (0, 0, 0), 0.5, 40, (1.0, 0.86, 0.7))
alight('L_fill', (0.5, -4.8, 1.6), (math.radians(80), 0, 0), 2.0, 60, (0.85, 0.9, 1.0))
# counter top via ray casts
dg = bpy.context.evaluated_depsgraph_get()
ctop = None
for x in (0.3, 0.0, 0.6, -0.4, 0.9, -0.8, 1.2):
    hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, V((x, KY + 0.28, 1.25)), V((0, 0, -1)))
    print('RAY', x, hit, [round(v, 3) for v in loc] if hit else None, ob.name if hit else None)
    if hit and 0.7 < loc.z < 1.05 and ctop is None: ctop = V((x, KY + 0.28, loc.z))
if ctop is None: ctop = V((0.3, KY + 0.28, 0.9))
pan, pobjs, pmn, pmx = place('pan', (ctop.x, ctop.y - 0.02, ctop.z + 0.002))
pan.rotation_euler.z = math.radians(-25)
PANC = V(((pmn.x + pmx.x) / 2, (pmn.y + pmx.y) / 2, pmx.z))
# smoke detector on the ceiling
DX, DY = 0.35, KY - 1.15
det, dobjs, dmn, dmx = place('detector', (DX, DY, 0))
det.location.z += H - dmx.z; bpy.context.view_layer.update()
dmn, dmx = bbox([o for o in dobjs if not o.hide_render])
print('DETECTOR', [round(v, 3) for v in dmn], [round(v, 3) for v in dmx])
DC = V(((dmn.x + dmx.x) / 2, (dmn.y + dmx.y) / 2, dmn.z))
ledm, lede = emis('led', (1.0, 0.04, 0.02), 0.0)
led = sphere('led', 0.0035, DC + V((0.028, -0.012, -0.001)), ledm)
for fr in range(F(0.0), F(DUR)):
    t = (fr - 1) / FPS
    on = 0.0
    if 24.4 <= t <= 26.1: on = 60.0 if int((t - 24.4) * 5) % 2 == 0 else 0.0
    elif abs(t - 2.0) < 0.06: on = 25.0
    lede.inputs[1].default_value = on; lede.inputs[1].keyframe_insert('default_value', frame=fr)
# kitchen smoke: rises from the pan and spreads under the ceiling (18-26.2)
ksm = smoke_mat('ksmoke', 0.9, (0.62, 0.62, 0.64), 2.2)
for i in range(7):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=PANC)
    b = bpy.context.active_object; b.name = 'ksm%d' % i; b.data.materials.append(ksm)
    a = i / 7.0
    p0 = PANC + V((random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), 0.05))
    p1 = V((PANC.x + (DC.x - PANC.x) * (0.4 + 0.6 * a) + random.uniform(-0.3, 0.3), PANC.y + (DC.y - PANC.y) * (0.4 + 0.6 * a) + random.uniform(-0.3, 0.3), H - 0.25 - random.uniform(0, 0.25)))
    t0 = 17.6 + i * 0.5
    key(b, 'scale', 1, (0.001,) * 3); key(b, 'scale', F(t0), (0.08,) * 3); key(b, 'scale', F(26.2), (0.32 + 0.05 * i,) * 3)
    key(b, 'location', F(t0), p0); key(b, 'location', F(26.2), p1)
# ================= CHAMBER WORLD =================
CX = V((30, 0, 0))
alight('C_key', CX + V((-1.4, -1.6, 2.0)), (math.radians(45), 0, math.radians(-40)), 1.4, 260, (1.0, 0.95, 0.9))
alight('C_rim', CX + V((1.6, 1.4, 1.2)), (math.radians(-60), 0, math.radians(140)), 1.0, 220, (0.6, 0.75, 1.0))
alight('C_low', CX + V((0.0, -2.2, 0.15)), (math.radians(88), 0, 0), 2.0, 40, (0.9, 0.9, 1.0))
plane('C_back', 12, 6, CX + V((0, 3.0, 2.0)), mat_col('cback', (0.012, 0.014, 0.02), rough=0.6), rot=(math.pi / 2, 0, 0))
plane('C_floor', 12, 12, CX + V((0, 0, -0.07)), mat_col('cfloor', (0.01, 0.011, 0.014), rough=0.35))
pcb = box('pcb', (2.6, 2.2, 0.06), CX + V((0, 0.2, -0.03)), mat_col('pcb', (0.015, 0.09, 0.05), rough=0.35), bevel=0.01)
# copper traces carrying the current
tm = bpy.data.materials.new('trace'); tm.use_nodes = True; tb = tm.node_tree.nodes['Principled BSDF']
tb.inputs['Base Color'].default_value = (0.75, 0.42, 0.2, 1); tb.inputs['Metallic'].default_value = 1.0; tb.inputs['Roughness'].default_value = 0.3
tb.inputs['Emission Color'].default_value = (1.0, 0.75, 0.35, 1)
TR = []
for (a, b) in (((0.62, -0.1), (1.2, -0.1)), ((1.2, -0.1), (1.2, -0.75)), ((-0.62, 0.15), (-1.2, 0.15)), ((-1.2, 0.15), (-1.2, -0.7))):
    mx_, my_ = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    TR.append(box('trace', (abs(a[0] - b[0]) + 0.03, abs(a[1] - b[1]) + 0.03, 0.006), CX + V((mx_, my_, 0.003)), tm))
for t, v in ((0, 0.0), (17.7, 0.0), (18.3, 2.5), (23.3, 2.5), (23.95, 0.0)):
    tb.inputs['Emission Strength'].default_value = v; tb.inputs['Emission Strength'].keyframe_insert('default_value', frame=F(t))
chip = box('chip', (0.42, 0.42, 0.06), CX + V((1.2, -0.95, 0.03)), mat_col('chip', (0.02, 0.02, 0.022), rough=0.5), bevel=0.01)
# chamber: perforated metal can, cut open towards the camera (-Y)
can = cyl('can', 0.6, 0.66, CX + V((0, 0, 0.33)), mat_col('canm', (0.7, 0.7, 0.72), rough=0.3, metal=1.0), v=96)
lid = cyl('lid', 0.6, 0.02, CX + V((0, 0, 0.66)), can.data.materials[0], v=96)
import bmesh
for o in (can, lid):
    me = o.data; bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y < -0.02], context='FACES')
    bm.to_mesh(me); bm.free()
    so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.02
cm = can.data.materials[0]; nt = cm.node_tree; bsdf = nt.nodes['Principled BSDF']
tc = nt.nodes.new('ShaderNodeTexCoord'); vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 14.0
lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'GREATER_THAN'; lt.inputs[1].default_value = 0.22
nt.links.new(tc.outputs['Object'], vo.inputs['Vector']); nt.links.new(vo.outputs['Distance'], lt.inputs[0]); nt.links.new(lt.outputs[0], bsdf.inputs['Alpha'])
steel = mat_col('steel', (0.8, 0.8, 0.82), rough=0.18, metal=1.0)
bot = cyl('bottom_plate', 0.46, 0.03, CX + V((0, 0, 0.07)), steel)
top = cyl('top_plate', 0.46, 0.03, CX + V((0, 0, 0.54)), steel)
for o in (bot, top):
    bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.008; bv.segments = 3
holder = cyl('holder', 0.13, 0.05, CX + V((0, 0, 0.11)), mat_col('holder', (0.35, 0.35, 0.37), rough=0.4, metal=1.0))
amm = bpy.data.materials.new('americium'); amm.use_nodes = True; ab = amm.node_tree.nodes['Principled BSDF']
ab.inputs['Base Color'].default_value = (0.95, 0.78, 0.45, 1); ab.inputs['Metallic'].default_value = 1.0; ab.inputs['Roughness'].default_value = 0.22
ab.inputs['Emission Color'].default_value = (1.0, 0.7, 0.35, 1); ab.inputs['Emission Strength'].default_value = 0.25
am = cyl('americium', 0.09, 0.014, CX + V((0, 0, 0.142)), amm)
bv = am.modifiers.new('bv', 'BEVEL'); bv.width = 0.004; bv.segments = 3
pin = cyl('pin', 0.022, 0.6, CX + V((0.5, 0.25, 0.27)), steel)
arm = box('arm', (0.14, 0.04, 0.02), CX + V((0.44, 0.25, 0.555)), steel)
AMC = CX + V((0, 0, 0.15))
# glow pulse on "radioactive"/"americium"
for t, v in ((0, 0.25), (8.4, 0.25), (8.8, 1.8), (10.0, 0.6), (26.0, 0.6), (27.0, 1.4)):
    ab.inputs['Emission Strength'].default_value = v; ab.inputs['Emission Strength'].keyframe_insert('default_value', frame=F(t))
# ---------- alpha particles: fired constantly from the americium into the air gap ----------
alm, _ = emis('alpha', (1.0, 0.42, 0.18), 30.0)
def pulse_pool(prefix, n, mat, r, t_start, t_end, period, life, src_fn, dst_fn):
    for i in range(n):
        o = sphere('%s%d' % (prefix, i), r, AMC, mat, seg=10)
        o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=1)
        t = t_start + period * i / n
        while t < t_end:
            s, d = src_fn(t), dst_fn(t)
            if d is None: t += period; continue
            fa, fb = F(t), F(t + life)
            o.location = s; o.keyframe_insert('location', frame=fa)
            o.scale = (1,) * 3; o.keyframe_insert('scale', frame=fa)
            o.location = d; o.keyframe_insert('location', frame=fb)
            o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=fb + 1)
            t += period
        interp(o, 'location', 'LINEAR'); interp(o, 'scale', 'CONSTANT')
def a_src(t): return AMC + V((random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), 0.0))
def a_dst(t):
    ang = random.uniform(0, 2 * math.pi); rr = random.uniform(0.05, 0.38)
    return CX + V((rr * math.cos(ang), rr * math.sin(ang), random.uniform(0.28, 0.5)))
pulse_pool('alpha', 26, alm, 0.006, 11.7, DUR, 0.42, 0.25, a_src, a_dst)
# ---------- smoke drifting into the chamber (20.1+) ----------
csm = smoke_mat('csmoke', 6.0, (0.5, 0.5, 0.52), 3.5)
SMK = []
for i in range(6):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=CX)
    b = bpy.context.active_object; b.name = 'csm%d' % i; b.data.materials.append(csm)
    dst = CX + V((random.uniform(-0.3, 0.3), random.uniform(-0.1, 0.3), random.uniform(0.2, 0.45)))
    src = dst + V((-1.3 - random.uniform(0, 0.4), random.uniform(-0.2, 0.2), random.uniform(-0.05, 0.05)))
    t0 = 20.1 + i * 0.22
    key(b, 'scale', 1, (0.001,) * 3); key(b, 'scale', F(t0), (0.08,) * 3); key(b, 'scale', F(t0 + 1.6), (0.2,) * 3); key(b, 'scale', F(DUR), (0.24,) * 3)
    key(b, 'location', F(t0), src); key(b, 'location', F(t0 + 1.8), dst); key(b, 'location', F(DUR), dst + V((0.08, 0.05, 0.03)))
    SMK.append(dst)
# ---------- electrons up to the top plate, ions down: the current ----------
elm, _ = emis('electron', (0.25, 0.65, 1.0), 18.0)
ionm, _ = emis('ion', (0.75, 0.35, 1.0), 9.0)
PAIRS = []
def gap_pt():
    ang = random.uniform(0, 2 * math.pi); rr = math.sqrt(random.random()) * 0.38
    return CX + V((rr * math.cos(ang), rr * math.sin(ang), random.uniform(0.2, 0.48)))
for i in range(34):
    e = sphere('el%d' % i, 0.005, AMC, elm, seg=8); io = sphere('ion%d' % i, 0.009, AMC, ionm, seg=10)
    for o in (e, io): o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=1)
    t = 15.3 + 0.9 * i / 34
    while t < 23.3:
        p = gap_pt(); fa = F(t)
        stuck = t > 21.7
        if stuck:
            c = SMK[random.randrange(len(SMK))] if SMK else p
            de, di, le, li = c + V((random.uniform(-0.08, 0.08), random.uniform(-0.08, 0.08), random.uniform(-0.05, 0.05))), c, 0.7, 0.7
        else:
            de, di, le, li = V((p.x, p.y, CX.z + 0.522)), V((p.x, p.y, CX.z + 0.088)), 0.45, 0.85
        for o, d, l in ((e, de, le), (io, di, li)):
            o.location = p; o.keyframe_insert('location', frame=fa)
            o.scale = (1,) * 3; o.keyframe_insert('scale', frame=fa)
            o.location = d; o.keyframe_insert('location', frame=F(t + l))
            o.scale = ((0.6,) * 3 if stuck else (0.001,) * 3); o.keyframe_insert('scale', frame=F(t + l) + 1)
            if stuck: o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=F(24.2))
        if stuck: break
        t += 0.9
    for o in (e, io): interp(o, 'location', 'LINEAR'); interp(o, 'scale', 'CONSTANT')

anchors['det'] = empty('a_det', DC)
anchors['pan'] = empty('a_pan', PANC)
anchors['am'] = empty('a_am', AMC)
anchors['trace'] = empty('a_trace', CX + V((1.2, -0.4, 0.0)))
