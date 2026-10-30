# MC4: ARA Libertad held in Ghana for Singer's fund. Harbor (origin), court desk (X=2000), money table (X=2100)
import random, bmesh
random.seed(11)
V = Vector
# ---------- world: daylight sky ----------
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; wn = w.node_tree
bgn = wn.nodes['Background']
hp = ph_hdri('kloofendal_48d_partly_cloudy_puresky', '2k')
if hp:
    et = wn.nodes.new('ShaderNodeTexEnvironment'); et.image = bpy.data.images.load(hp); wn.links.new(et.outputs[0], bgn.inputs[0]); bgn.inputs[1].default_value = 1.0
else:
    sky = wn.nodes.new('ShaderNodeTexSky'); wn.links.new(sky.outputs[0], bgn.inputs[0]); bgn.inputs[1].default_value = 0.3
sc.cycles.samples = 64
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5; sun.angle = math.radians(1.5); sun.color = (1.0, 0.93, 0.82)
so = bpy.data.objects.new('sun', sun); link(so); so.rotation_euler = (math.radians(58), 0, math.radians(-35))
def alight(name, loc, rot, size, energy, col=(1, 1, 1), sy=None, kind='AREA'):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = col
    if kind == 'AREA':
        ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = sy or size
    if kind == 'SPOT': ld.spot_size = size; ld.spot_blend = 0.4
    o = bpy.data.objects.new(name, ld); link(o); o.location = loc; o.rotation_euler = rot; return o
def mat_box(name, tex, scale, tint=None, rough=None, res='2k'):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3
    nt.links.new(tc.outputs['Object'], mp.inputs[0])
    for kind, inp in (('diff', 'Base Color'), ('rough', 'Roughness')):
        p = ph_tex(tex, kind, res)
        if not p: continue
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p); t.projection = 'BOX'; t.projection_blend = 0.2
        if kind != 'diff': t.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs[0], t.inputs[0])
        if kind == 'diff' and tint:
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
            mx.inputs[7].default_value = tint + (1,); nt.links.new(t.outputs[0], mx.inputs[6]); nt.links.new(mx.outputs[2], b.inputs[inp])
        else: nt.links.new(t.outputs[0], b.inputs[inp])
    if not ph_tex(tex, 'diff', res) and tint: b.inputs['Base Color'].default_value = tint + (1,)
    if rough is not None and not ph_tex(tex, 'rough', res): b.inputs['Roughness'].default_value = rough
    return m
def cyl(name, r, d, loc, mat, v=48, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o
def room(name, ctr, size, mat):
    o = box(name, size, ctr, mat)
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free(); return o
def flag(name, tex, w_, h_, loc, rot, amp=0.06):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot); f = bpy.context.active_object; f.name = name
    f.scale = (w_, h_, 1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=24); bpy.ops.object.mode_set(mode='OBJECT')
    m = mat_img(name + 'm', tex, rough=0.7); m.node_tree.nodes['Principled BSDF'].inputs['Sheen Weight'].default_value = 0.4
    f.data.materials.append(m)
    wv = f.modifiers.new('wave', 'WAVE'); wv.height = amp * w_; wv.width = w_ * 0.45; wv.speed = 0.06 * w_; wv.use_normal = False; wv.use_y = False
    wv.start_position_x = -w_ / 2
    f.modifiers.new('ss', 'SUBSURF'); return f
def hide_keys(o, spans):
    """visible only inside spans [(t0,t1)]"""
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    for a, b in spans:
        o.hide_render = False; o.keyframe_insert('hide_render', frame=F(a))
        o.hide_render = True; o.keyframe_insert('hide_render', frame=F(b))

# ================= HARBOR =================
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0)); ocean = bpy.context.active_object; ocean.name = 'ocean'
om = ocean.modifiers.new('ocean', 'OCEAN'); om.spatial_size = 220; om.resolution = 12; om.wave_scale = 0.35; om.choppiness = 0.9
om.repeat_x = 4; om.repeat_y = 4; om.wind_velocity = 9
om.time = 0.0; om.keyframe_insert('time', frame=1); om.time = DUR * 0.8; om.keyframe_insert('time', frame=F(DUR))
for fc in fcurves(ocean):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
wm = bpy.data.materials.new('water'); wm.use_nodes = True; wb = wm.node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.004, 0.022, 0.03, 1); wb.inputs['Roughness'].default_value = 0.07; wb.inputs['IOR'].default_value = 1.33
ocean.data.materials.append(wm); bpy.ops.object.shade_smooth()
ocean.location = (-om.spatial_size * om.repeat_x / 2, -om.spatial_size * om.repeat_y / 2, 0)
SD = CFG['assets']['ship'].get('dir', 1)   # +1: bow points +Y
ship, sobjs, smn, smx = place('ship', (0, 0, -4.0))
print('SHIP bbox', [round(v, 2) for v in smn], [round(v, 2) for v in smx])
dg = bpy.context.evaluated_depsgraph_get()
def ray(o, d):
    hit, loc, nrm, idx, ob, mtx = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), V(o), V(d)); return loc if hit else None
hx = []
for y in (-10, -5, 0, 5, 10):
    for z in (1.0, 2.5):
        h = ray((40, y, z), (-1, 0, 0))
        if h is not None: hx.append(h.x)
HULL_X = max(hx) if hx else 6.0
DECK_Z = None
for zz in [1.0 + 0.5 * i for i in range(30)]:
    hits = [ray((40, y, zz), (-1, 0, 0)) for y in (-8, 0, 8)]
    xs = [h.x for h in hits if h is not None]
    if not xs or max(xs) < HULL_X - 2.0:
        DECK_Z = zz - 0.6; break
if DECK_Z is None or not (1.0 < DECK_Z < 14): DECK_Z = 4.5
dz = DECK_Z
print('HULL_X', round(HULL_X, 2), 'DECK_Z', round(DECK_Z, 2), dz)
SHIP0 = ship.location.copy()
QX = HULL_X + 1.6          # quay edge
QZ = 2.4
quay = box('quay', (40, 260, 6.0), (QX + 20, 0, QZ - 3.0), mat_box('concrete', 'concrete_floor_worn_001', 0.25, tint=(0.75, 0.74, 0.72), rough=0.85))
fender_m = mat_col('fender', (0.02, 0.02, 0.02), rough=0.8)
for y in range(-60, 61, 10):
    cyl('fender', 0.45, 2.2, (QX - 0.2, y, QZ - 1.6), fender_m, v=24, rot=(0, 0, 0))
iron = mat_col('iron', (0.03, 0.03, 0.035), rough=0.45, metal=1.0)
BOL = []
for y in (-30, -12, 12, 30):
    b = cyl('bollard', 0.32, 0.8, (QX + 1.1, y, QZ + 0.4), iron, v=32); cyl('bcap', 0.42, 0.12, (QX + 1.1, y, QZ + 0.85), iron, v=32)
    BOL.append(V((QX + 1.1, y, QZ + 0.6)))
# warehouses + cranes as a skyline on the quay
shed_m = mat_col('shed', (0.55, 0.57, 0.6), rough=0.6, metal=0.3)
for i, y in enumerate((-90, -55, 55, 95)):
    box('shed', (22, 30, 10 + 3 * (i % 2)), (QX + 30, y, QZ + 5 + 1.5 * (i % 2)), shed_m)
crane_m = mat_col('crane', (0.75, 0.25, 0.08), rough=0.5, metal=0.5)
for y in (-75, 70):
    for dx in (0, 9):
        box('cleg', (0.8, 0.8, 30), (QX + 6 + dx, y, QZ + 15), crane_m)
    box('cboom', (48, 1.6, 2.2), (QX - 6, y, QZ + 31), crane_m)
# mooring ropes ship -> bollards (tight while held)
rope_m = mat_col('rope', (0.55, 0.45, 0.3), rough=0.9)
ROPES = []
for i, by in enumerate((-30, -12, 12, 30)):
    cu = bpy.data.curves.new('rope%d' % i, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.07; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(1)
    a = V((HULL_X - 0.3, by * 0.8, DECK_Z + 0.6)); b = BOL[i]
    for p, c in zip(sp.bezier_points, (a, b)):
        p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    ro = bpy.data.objects.new('rope%d' % i, cu); link(ro); ro.data.materials.append(rope_m); ROPES.append(ro)
    hide_keys(ro, [(3.9 + 0.12 * i, 20.35)])
# ship motion: sails in (0-4.0), held (4.0-20.3), leaves (20.3-)
def shipkey(t, dy):
    ship.location = SHIP0 + V((0, dy, 0)); ship.keyframe_insert('location', frame=F(t))
shipkey(0.0, -SD * 34); shipkey(4.0, 0); shipkey(20.3, 0); shipkey(DUR, SD * 28)
for fc in fcurves(ship):
    kps = sorted(fc.keyframe_points, key=lambda k: k.co.x)
    for i, kp in enumerate(kps): kp.interpolation = 'BEZIER'; kp.easing = 'EASE_OUT' if i == 0 else 'EASE_IN'
# Argentine flag on a pole at the stern
STERN_Y = (smn.y if SD > 0 else smx.y) + SD * 5.0
pole = cyl('pole', 0.08, 7.0, (0, STERN_Y, DECK_Z + 3.5), iron, v=16); pole.parent = ship; pole.matrix_parent_inverse = ship.matrix_world.inverted()
fl = flag('flag_ar', 'flag_ar.png', 3.6, 2.4, (0, STERN_Y - SD * 1.85, DECK_Z + 5.6), (math.pi / 2, 0, math.pi / 2), amp=0.08)
fl.parent = ship; fl.matrix_parent_inverse = ship.matrix_world.inverted()
anchors['ship'] = empty('a_ship', (0, 0, DECK_Z + 6))
anchors['flag'] = empty('a_flag', (0, STERN_Y, DECK_Z + 5.6))

# ================= COURT DESK (X=2000) =================
CC = V((2000, 0, 0))
room('court', CC + V((0, 1.0, 2.2)), (9, 9, 4.4), mat_box('panel', 'wood_planks_dirt', 0.6, tint=(0.35, 0.2, 0.12), rough=0.5))
desk_m = mat_box('desk', 'wood_table_001', 0.8, tint=(0.55, 0.33, 0.2), rough=0.35)
box('desk', (2.6, 1.1, 0.08), CC + V((0, 0, 0.76)), desk_m, bevel=0.01)
box('deskfront', (2.6, 0.06, 0.74), CC + V((0, -0.52, 0.37)), desk_m)
DT = CC + V((0, 0, 0.80))
block = cyl('soundblock', 0.085, 0.045, DT + V((0.05, -0.12, 0.0225)), mat_box('blockm', 'wood_table_001', 2.0, tint=(0.4, 0.22, 0.12), rough=0.3), v=48)
GH = CFG['assets']['gavel'].get('head', 1)
gav, gobjs, gmn, gmx = place('gavel', (0, 0, 0))
GL = gmx.x - gmn.x
piv = empty('gpivot', DT + V((0.05 - GH * (GL - 0.07), -0.12, 0.03)))
gav.location += piv.location - V((gmn.x if GH > 0 else gmx.x, (gmn.y + gmx.y) / 2, gmn.z)) + V((0, 0, 0.045)); bpy.context.view_layer.update()
gav.parent = piv; gav.matrix_parent_inverse = piv.matrix_world.inverted()
def strike(t):
    for dt, ang in ((-0.45, 0), (-0.2, -GH * 38), (-0.02, 0), (0.12, -GH * 6), (0.25, 0)):
        piv.rotation_euler = (0, math.radians(ang), 0); piv.keyframe_insert('rotation_euler', frame=F(t + dt))
for t in (15.9, 19.72, 22.06, 23.24): strike(t)
# desk flags: Ghana court, then the international tribunal
for name, tex, spans in (('fgh', 'flag_gh.png', [(0, 19.2)]), ('fun', 'flag_blue.png', [(19.2, DUR)])):
    pl = cyl(name + 'pole', 0.006, 0.42, DT + V((-0.9, 0.25, 0.21)), mat_col('chrome', (0.9, 0.9, 0.9), rough=0.15, metal=1.0), v=12)
    f = flag(name, tex, 0.27, 0.18, DT + V((-0.9 + 0.14, 0.25, 0.33)), (math.pi / 2, 0, 0), amp=0.05)
    for o in (pl, f): hide_keys(o, spans)
# growing pile of legal papers (21.5-24.4: fifteen years)
pm = mat_img('paperm', 'paper.png', rough=0.8)
for i in range(70):
    p = plane('paper', 0.21, 0.28, DT + V((0.75 + random.uniform(-0.02, 0.02), 0.05 + random.uniform(-0.02, 0.02), 0.002 + i * 0.0035)), pm, rot=(0, 0, random.uniform(-0.12, 0.12)))
    t = 21.3 + i * 0.045 if i > 6 else 0
    key(p, 'scale', 1, (1, 1, 1) if i <= 6 else (0.001,) * 3)
    if i > 6: key(p, 'scale', F(t), (0.001,) * 3); key(p, 'scale', F(t) + 1, (1, 1, 1))
    for fc in fcurves(p):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
alight('ck', CC + V((-1.6, -1.8, 2.6)), (math.radians(50), 0, math.radians(-38)), 1.2, 160, (1.0, 0.86, 0.68))
alight('cr', CC + V((1.8, 1.6, 2.2)), (math.radians(-55), 0, math.radians(140)), 1.0, 90, (0.7, 0.8, 1.0))
alight('cf', CC + V((0, -3.0, 1.5)), (math.radians(80), 0, 0), 2.0, 40, (1.0, 0.95, 0.9))
anchors['gavel'] = empty('a_gavel', DT + V((0.05, -0.12, 0.05)))

# ================= MONEY TABLE (X=2100) =================
MC = V((2100, 0, 0))
room('vault', MC + V((0, 1.0, 2.2)), (10, 10, 4.4), mat_col('vwall', (0.03, 0.028, 0.026), rough=0.7))
box('table', (3.2, 2.4, 0.08), MC + V((0, 0.4, 0.76)), mat_box('tablem', 'wood_table_001', 0.8, tint=(0.25, 0.14, 0.08), rough=0.3), bevel=0.01)
TT = MC + V((0, 0, 0.80))
mon, mobjs, mmn, mmx = place('money', TT + V((0, 0, 0)))
BH = mmx.z - mmn.z; BW = mmx.x - mmn.x; BD = mmx.y - mmn.y
def bundle(target):
    r = bpy.data.objects.new('bun', None); link(r); r.location = TT
    bpy.context.view_layer.update()
    for o in mobjs:
        if o.type != 'MESH': continue
        mw = o.matrix_world.copy(); c = o.copy(); link(c); c.hide_render = False
        c.parent = r; c.matrix_parent_inverse.identity(); c.matrix_world = r.matrix_world.inverted() @ mw if False else mw
    r.location = target; return r
def pop(o, t_in=None, t_out=None):
    o.scale = (0.001,) * 3 if t_in else (1, 1, 1); o.keyframe_insert('scale', frame=1)
    if t_in: o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=F(t_in)); o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=F(t_in) + 2)
    if t_out: o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=F(t_out)); o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=F(t_out) + 2)
    for fc in fcurves(o):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
NB = 9
SX_, SY_ = BW + 0.05, BD + 0.07
def spot_xy(c, r): return TT + V(((c + 0.5) * SX_, r * SY_, 0))
GRID = [(c, r) for r in range(3) for c in range(-2, 2)]
HERO = (0, 0)
for (c, r) in GRID:
    for k in range(NB):
        b = bundle(spot_xy(c, r) + V((0, 0, k * BH)))
        if (c, r) != HERO and k >= 3: pop(b, None, 12.25 + 0.03 * (NB - k) + 0.05 * (c + 2 + r * 4))
        else: pop(b)
# growth: from one claim to a wall of money (27.4-31.2)
EXTRA = [(c, r) for r in range(-1, 5) for c in range(-4, 4) if (c, r) not in GRID]
for i, (c, r) in enumerate(EXTRA):
    for k in range(NB + 4):
        pop(bundle(spot_xy(c, r) + V((0, 0, k * BH))), 27.4 + i * 0.05 + k * 0.03)
for (c, r) in GRID:
    if (c, r) == HERO: continue
    for k in range(3, NB + 4):
        pop(bundle(spot_xy(c, r) + V((0, 0, k * BH))), 28.0 + 0.02 * k + 0.04 * (c + 2 + r * 4))
for k in range(NB, NB + 4):
    pop(bundle(spot_xy(0, 0) + V((0, 0, k * BH))), 27.3 + 0.05 * k)
for o in mobjs: o.hide_render = True
mon.location += V((0, 0, -50))
HC = TT + V(((BW + 0.05) / 2, 0, NB * BH / 2))
spot = alight('hero_spot', HC + V((0, -0.2, 2.4)), (math.radians(5), 0, 0), math.radians(28), 0, (1.0, 0.88, 0.7), kind='SPOT')
for t, e in ((0, 0), (13.6, 0), (13.8, 900), (DUR, 900)):
    spot.data.energy = e; spot.data.keyframe_insert('energy', frame=F(t))
alight('mk', MC + V((-1.8, -2.0, 2.4)), (math.radians(48), 0, math.radians(-40)), 1.4, 140, (1.0, 0.9, 0.75))
alight('mr', MC + V((2.0, 2.2, 1.8)), (math.radians(-55), 0, math.radians(140)), 1.2, 110, (0.6, 0.75, 1.0))
for t, e in ((0, 140), (13.6, 140), (13.8, 50), (26.3, 50), (26.6, 140)):
    bpy.data.lights['mk'].energy = e; bpy.data.lights['mk'].keyframe_insert('energy', frame=F(t))
anchors['hero'] = empty('a_hero', HC)
