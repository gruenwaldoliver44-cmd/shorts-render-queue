# CT5 scratch-ticket singletons. Store counter (origin), study desk (X=50).
import random
random.seed(5)
V = Vector
TJ = json.load(open(TX + 'ticket.json'))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (0.02, 0.022, 0.026, 1); bgn.inputs[1].default_value = 1.0
sc.cycles.samples = 64
def alight(name, loc, rot, size, energy, col=(1, 1, 1), sy=None, kind='AREA'):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = col
    if kind == 'AREA': ld.shape = 'RECTANGLE'; ld.size = size; ld.size_y = sy or size
    if kind == 'SPOT': ld.spot_size = size; ld.spot_blend = 0.5
    o = bpy.data.objects.new(name, ld); link(o); o.location = loc; o.rotation_euler = rot; return o
def emis(name, col, s):
    m = bpy.data.materials.new(name); m.use_nodes = True; t = m.node_tree
    for n in list(t.nodes):
        if n.type != 'OUTPUT_MATERIAL': t.nodes.remove(n)
    e = t.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = col + (1,); e.inputs[1].default_value = s
    t.links.new(e.outputs[0], t.nodes['Material Output'].inputs[0]); return m
def cyl(name, r, d, loc, mat, v=48, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o
def mat_box(name, tex, scale, tint=None, rough=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3
    nt.links.new(tc.outputs['Object'], mp.inputs[0]); ok = False
    for kind, inp in (('diff', 'Base Color'), ('rough', 'Roughness')):
        p = ph_tex(tex, kind, '2k')
        if not p: continue
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p); t.projection = 'BOX'; t.projection_blend = 0.2
        if kind != 'diff': t.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs[0], t.inputs[0])
        if kind == 'diff' and tint:
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
            mx.inputs[7].default_value = tint + (1,); nt.links.new(t.outputs[0], mx.inputs[6]); nt.links.new(mx.outputs[2], b.inputs[inp])
        else: nt.links.new(t.outputs[0], b.inputs[inp])
        if kind == 'diff': ok = True
    if not ok and tint: b.inputs['Base Color'].default_value = tint + (1,)
    if rough is not None: b.inputs['Roughness'].default_value = rough
    return m
def pop(o, t_in=None, t_out=None, s1=1.0):
    o.scale = (0.001,) * 3 if t_in else (s1,) * 3; o.keyframe_insert('scale', frame=1)
    if t_in: o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=F(t_in)); o.scale = (s1 * 1.15,) * 3; o.keyframe_insert('scale', frame=F(t_in) + 3); o.scale = (s1,) * 3; o.keyframe_insert('scale', frame=F(t_in) + 6)
    if t_out: o.scale = (s1,) * 3; o.keyframe_insert('scale', frame=F(t_out)); o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=F(t_out) + 4)

TW, TH = 0.075, 0.12
def ticket_mat(name, scratch=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.42; b.inputs['Coat Weight'].default_value = 0.25
    t1 = nt.nodes.new('ShaderNodeTexImage'); t1.image = bpy.data.images.load(TX + 'ticket_cov.png')
    if not scratch:
        nt.links.new(t1.outputs[0], b.inputs['Base Color']); return m, None
    t2 = nt.nodes.new('ShaderNodeTexImage'); t2.image = bpy.data.images.load(TX + 'ticket_rev.png')
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9.0; nz.inputs['Detail'].default_value = 8
    gx = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['UV'], gx.inputs[0])
    # reveal sweeps left->right with ragged edge: factor = (u*0.8 + noise*0.35) < reveal
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY_ADD'; m1.inputs[1].default_value = 0.8
    nt.links.new(gx.outputs[0], m1.inputs[0]); nt.links.new(tc.outputs['UV'], nz.inputs['Vector'])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 0.35; nt.links.new(nz.outputs[0], m2.inputs[0]); nt.links.new(m2.outputs[0], m1.inputs[2])
    rv = nt.nodes.new('ShaderNodeValue'); rv.outputs[0].default_value = 0.0
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; nt.links.new(m1.outputs[0], lt.inputs[0]); nt.links.new(rv.outputs[0], lt.inputs[1])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; nt.links.new(lt.outputs[0], mx.inputs['Factor'])
    nt.links.new(t1.outputs[0], mx.inputs[6]); nt.links.new(t2.outputs[0], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    return m, rv
def ticket(name, loc, mat, rz=0.0):
    o = plane(name, TW, TH, loc, mat, rot=(0, 0, rz))
    so = o.modifiers.new('so', 'SOLIDIFY'); so.thickness = 0.0004; so.offset = -1
    return o
def tpos(t, u, v, dz=0.0006):
    """world point of ticket-texture coords (u from left, v from top)"""
    return t.matrix_world @ V(((u - 0.5) * TW, (0.5 - v) * TH, dz))

# ================= STORE =================
floor = plane('floor', 10, 10, (0, 0, 0), mat_box('tiles', 'floor_tiles_06', 1.2, tint=(0.85, 0.85, 0.85), rough=0.3))
wall = plane('wall', 10, 4, (0, 3.2, 2), mat_col('wallm', (0.75, 0.72, 0.66), rough=0.8), rot=(math.pi / 2, 0, 0))
dr, _, _, _ = place('drinks', (-1.0, 2.6, 0)); rw, _, _, _ = place('raw', (1.1, 2.6, 0))
cmat = mat_box('counterw', 'wood_table_001', 1.0, tint=(0.55, 0.38, 0.25), rough=0.35)
box('counter', (1.7, 0.62, 0.95), (0, 0, 0.475), cmat, bevel=0.01)
box('countertop', (1.78, 0.68, 0.035), (0, 0, 0.967), mat_col('ctop', (0.08, 0.08, 0.085), rough=0.25), bevel=0.004)
CT = 0.985
reg, _, _, _ = place('register', (-0.55, 0.05, CT))
# ticket dispenser: acrylic case with 6 slots, tickets fanned out the front
acr = bpy.data.materials.new('acrylic'); acr.use_nodes = True; ab = acr.node_tree.nodes['Principled BSDF']
ab.inputs['Transmission Weight'].default_value = 1.0; ab.inputs['Roughness'].default_value = 0.05; ab.inputs['IOR'].default_value = 1.49
DX, DY = 0.3, 0.12
box('dispenser', (0.5, 0.16, 0.2), (DX, DY, CT + 0.1), acr, bevel=0.006)
store_mat, _ = ticket_mat('tk_store')
SLOTS = []
for i in range(6):
    x = DX - 0.21 + i * 0.084
    stack = []
    for k in range(6):
        t = ticket('stk', (x, DY - 0.02 - k * 0.0012, CT + 0.07), store_mat)
        t.rotation_euler = (math.radians(80), 0, 0); stack.append(t)
    SLOTS.append(stack)
# one ticket slides out of slot 2 (7.6-8.5)
slid = SLOTS[2][0]
key(slid, 'location', F(6.2), slid.location.copy()); key(slid, 'location', F(7.0), slid.location + V((0, -0.11, -0.045)))
# the game is pulled (28.6+): all tickets vanish slot by slot
for i, stack in enumerate(SLOTS):
    for k, t in enumerate(stack):
        if t is slid: continue
        pop(t, None, 25.0 + 0.08 * i + 0.02 * k)
# hero ticket lying on the counter + coin
hero = ticket('hero', (0.02, -0.16, CT + 0.0004), store_mat, rz=math.radians(-8))
coin_m = mat_col('coinm', (0.78, 0.78, 0.8), rough=0.22, metal=1.0)
coin = cyl('coin', 0.0121, 0.00175, (0, 0, 0), coin_m, v=96)
bv = coin.modifiers.new('bv', 'BEVEL'); bv.width = 0.0004; bv.segments = 2
LAT = tpos(hero, 0.5, 0.24)
key(coin, 'location', 1, LAT + V((0.09, -0.05, 0.05))); key(coin, 'rotation_euler', 1, (math.radians(70), 0, math.radians(20)))
key(coin, 'location', F(3.1), LAT + V((0.03, 0.0, 0.012))); key(coin, 'rotation_euler', F(3.1), (math.radians(40), 0, math.radians(10)))
key(coin, 'location', F(4.0), LAT + V((0.03, 0.0, 0.013)))
for z_ in range(3):
    plane('tube', 1.4, 0.12, (-0.4 + z_ * 0.6, 0.4 - z_ * 0.9, 3.0), emis('tubem', (1.0, 0.97, 0.92), 3.5), rot=(math.pi, 0, 0))
alight('S_key', (-0.6, -0.9, 1.9), (math.radians(40), 0, math.radians(-30)), 0.8, 70, (1.0, 0.92, 0.82))
alight('S_fill', (0.9, -1.4, 1.4), (math.radians(65), 0, math.radians(35)), 1.2, 30, (0.85, 0.9, 1.0))
alight('S_top', (0, 0.3, 2.8), (0, 0, 0), 2.0, 110, (1.0, 0.97, 0.92))
anchors['hero'] = empty('a_hero', tpos(hero, 0.5, 0.5))
anchors['disp'] = empty('a_disp', (DX, DY, CT + 0.12))

# ================= DESK (X=50) =================
DC = V((50, 0, 0))
room = box('droom', (6, 6, 3.2), DC + V((0, 1, 1.6)), mat_col('droomm', (0.05, 0.045, 0.04), rough=0.9))
import bmesh
bm = bmesh.new(); bm.from_mesh(room.data); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(room.data); bm.free()
box('desk', (1.4, 0.75, 0.04), DC + V((0, 0.1, 0.76)), mat_box('deskw', 'wood_table_001', 1.2, tint=(0.5, 0.32, 0.2), rough=0.3), bevel=0.004)
DT = 0.78
lamp, _, _, _ = place('lamp', DC + V((-0.42, 0.32, DT)))
ph, _, pmn, pmx = place('phone', DC + V((0.42, 0.22, DT)))
PHC = (pmn + pmx) / 2
nb, _, _, _ = place('notebook', DC + V((-0.2, 0.05, DT)))
desk_mat, REV = ticket_mat('tk_desk', scratch=True)
dt = ticket('dticket', DC + V((0.08, -0.08, DT + 0.0004)), desk_mat, rz=math.radians(4))
mk, mobjs, mmn, mmx = place('marker', DC + V((0.2, -0.12, DT)))
for t, v in ((0, 0.0), (18.2, 0.0), (19.1, 1.2)):
    REV.outputs[0].default_value = v; REV.outputs[0].keyframe_insert('default_value', frame=F(t))
# marker circles appear one by one on the singletons, the winning row last
cm = bpy.data.materials.new('circle'); cm.use_nodes = True; ct_ = cm.node_tree; cb = ct_.nodes['Principled BSDF']
ci = ct_.nodes.new('ShaderNodeTexImage'); ci.image = bpy.data.images.load(TX + 'circle.png')
ct_.links.new(ci.outputs[0], cb.inputs['Base Color']); ct_.links.new(ci.outputs[1], cb.inputs['Alpha']); cb.inputs['Roughness'].default_value = 0.6
others = [p for p in TJ['singles'] if p not in TJ['win']]
order = others + TJ['win']
for i, (u, v) in enumerate(order):
    c = plane('circ', 0.016, 0.013, tpos(dt, u, v, 0.0007), cm, rot=(0, 0, dt.rotation_euler.z))
    pop(c, 13.55 + i * 0.18)
# strike line through the winning row (20.6)
(u0, v0), (u2, v2) = TJ['win'][0], TJ['win'][2]
mid = (tpos(dt, u0, v0, 0.0009) + tpos(dt, u2, v2, 0.0009)) / 2
line = plane('winline', 0.034, 0.0009, mid, emis('linem', (0.85, 0.05, 0.05), 1.2), rot=(0, 0, dt.rotation_euler.z))
line.scale = (0.001, 1, 1); line.keyframe_insert('scale', frame=1); line.keyframe_insert('scale', frame=F(17.0))
line.scale = (1, 1, 1); line.keyframe_insert('scale', frame=F(17.3))
alight('D_lamp', DC + V((-0.3, 0.2, DT + 0.45)), (0, 0, 0), 0.25, 30, (1.0, 0.82, 0.55))
alight('D_key', DC + V((-0.7, -0.8, 1.7)), (math.radians(42), 0, math.radians(-38)), 0.7, 45, (1.0, 0.86, 0.68))
alight('D_rim', DC + V((0.8, 0.9, 1.4)), (math.radians(-55), 0, math.radians(140)), 0.8, 45, (0.6, 0.75, 1.0))
anchors['dticket'] = empty('a_dt', tpos(dt, 0.5, 0.5))
anchors['win'] = empty('a_win', tpos(dt, 0.735, 0.71875))
anchors['latex'] = empty('a_lat', tpos(dt, 0.5, 0.24))
anchors['phone'] = empty('a_phone', PHC + V((0, 0, 0.08)))
