# CT4 slot predictors: casino aisle (x=0), circuit macro (x=40), analysis desk (x=80)
P = dict(scr_z=1.23, scr_w=0.50, scr_h=0.30, scr_x=-0.02, deck_z=0.95, deck_y=0.16, btn_x=0.18)
SW = SH = None
# ---------- world ----------
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']; bgn.inputs[0].default_value = (0.012, 0.010, 0.014, 1); bgn.inputs[1].default_value = 1.0
sc.cycles.samples = 64
# ---------- casino aisle ----------
def uv_scale(o, s):
    for d in o.data.uv_layers.active.data: d.uv = d.uv * s
floor = plane('floor', 30, 30, (0, 0, 0), mat_img('carpet', 'carpet.png', rough=0.92)); uv_scale(floor, 18)
ceil = plane('ceil', 30, 30, (0, 0, 3.4), mat_col('ceil', (0.02, 0.018, 0.02), rough=0.8), rot=(math.pi, 0, 0))
hero, hobjs, hmn, hmx = place('slot', (0, 0, 0))
FRONT_Y = hmn.y
for m in bpy.data.materials:
    if m.name in ('777',) and m.use_nodes:
        b = m.node_tree.nodes.get('Principled BSDF')
        if b:
            tx = [n for n in m.node_tree.nodes if n.type == 'TEX_IMAGE']
            if tx: m.node_tree.links.new(tx[0].outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 2.5
def dup(objs, root, loc, rz):
    r = bpy.data.objects.new('D_' + root.name, None); sc.collection.objects.link(r)
    mp = {}
    for o in objs:
        c = o.copy(); sc.collection.objects.link(c); mp[o] = c
    for o, c in mp.items():
        if o.parent in mp: c.parent = mp[o.parent]
        elif o.parent is None or o.parent == root: c.parent = r
    r.location = root.location; r.scale = root.scale
    bpy.context.view_layer.update()
    piv = bpy.data.objects.new('PV', None); sc.collection.objects.link(piv); r.parent = piv
    piv.location = loc; piv.rotation_euler = (0, 0, rz)
    return piv
for i, x in enumerate((-2.6, -1.3, 1.3, 2.6, 3.9, -3.9)):
    dup(hobjs, hero, (x, 0, 0), 0)
for i, x in enumerate((-2.6, -1.3, 0, 1.3, 2.6)):
    dup(hobjs, hero, (x, -3.6, 0), math.pi)
# warm lights over the aisle
def area(name, loc, size, energy, col, rot=(0, 0, 0)):
    l = bpy.data.lights.new(name, 'AREA'); l.size = size; l.energy = energy; l.color = col
    o = bpy.data.objects.new(name, l); link(o); o.location = loc; o.rotation_euler = rot; return o
for x in (-2.6, 0, 2.6):
    area('ov%d' % x, (x, -1.6, 3.2), 1.2, 260, (1.0, 0.78, 0.55))
key = area('key', (-1.2, -2.2, 1.9), 0.6, 90, (1.0, 0.85, 0.7), rot=(math.radians(70), 0, math.radians(-30)))
rim = area('rim', (1.4, 0.8, 2.2), 0.8, 120, (0.4, 0.55, 1.0), rot=(math.radians(-60), 0, math.radians(150)))
# ---------- reels overlay on hero screen ----------
reel_objs = []
def reel_mat(i):
    m = bpy.data.materials.new('reel%d' % i); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(TX + 'reel.png'); t.extension = 'REPEAT'
    mp.inputs['Scale'].default_value = (1.0, 1.0, 1)
    nt.links.new(tc.outputs['UV'], mp.inputs[0]); nt.links.new(mp.outputs[0], t.inputs[0])
    nt.links.new(t.outputs[0], b.inputs['Base Color']); nt.links.new(t.outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 0.18
    b.inputs['Roughness'].default_value = 0.35
    return m, mp
REELS = []
for i in range(3):
    x = P['scr_x'] + (i - 1) * P['scr_w'] / 3
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.12, depth=P['scr_w'] / 3 * 0.82, location=(x, FRONT_Y + 0.12 + 0.045, P['scr_z'] - 0.02), rotation=(0, math.pi / 2, 0))
    c = bpy.context.active_object; c.name = 'reel%d' % i
    m, mp = reel_mat(i); c.data.materials.append(m)
    REELS.append((c, mp))
# spin schedule: (t_start, t_stop) per spin; reel offset in symbol units, stops on '7' (index 0/2/5 -> use 0)
def spin_keys(mp, i, t0, t1, n_sym):
    f0, f1 = F(t0), F(t1 + i * 0.18)
    cur = mp.inputs['Location'].default_value[1]
    cur = mp.inputs['Location'].default_value[0]
    mp.inputs['Location'].keyframe_insert('default_value', index=0, frame=f0)
    mp.inputs['Location'].default_value[0] = cur + n_sym / 8.0
    mp.inputs['Location'].keyframe_insert('default_value', index=0, frame=f1)
for (t0, t1) in ((1.86, 3.3), (5.2, 6.4), (20.6, 22.0), (29.6, 33.4)):
    for i, (c, mp) in enumerate(REELS): spin_keys(mp, i, t0, t1, 16 + 8 * i)
# ---------- phone on the deck ----------
ph, pobjs, pmn, pmx = place('phone', (P['scr_x'] - 0.14, FRONT_Y - P['deck_y'] + 0.05, P['deck_z']))
PH0 = ph.location.copy()
def scr_plane(name, img, parent, size, z):
    m = mat_img('m_' + name, img, rough=0.2, emis=1.6)
    o = plane(name, size[0], size[1], (0, 0, 0), m); o.parent = parent; o.location = (0, 0, z); return o
PH_SCR = {}
for nm, img in (('lock', 'scr_lock.png'), ('rec', 'scr_rec.png'), ('times', 'scr_times.png')):
    o = plane('ps_' + nm, 0.138, 0.066, (0, 0, 0), mat_img('m_' + nm, img, rough=0.15, emis=1.4))
    o.rotation_euler = (0, 0, -math.pi / 2); o.location = ((pmn.x + pmx.x) / 2, (pmn.y + pmx.y) / 2, pmx.z + 0.0006)
    o.parent = ph; o.matrix_parent_inverse = ph.matrix_world.inverted()
    PH_SCR[nm] = o
def show(o, frames_on):
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    for a, b in frames_on:
        o.hide_render = False; o.keyframe_insert('hide_render', frame=F(a))
        o.hide_render = True; o.keyframe_insert('hide_render', frame=F(b))
    set_interp(o, 'CONSTANT')
show(PH_SCR['lock'], [(0, 9.8), (19.8, 34.5)])
show(PH_SCR['rec'], [(9.8, 14.3)])
show(PH_SCR['times'], [(17.5, 19.8)])
# phone buzz: tiny rotation jitter on the buzz words
def buzz(t, dur=0.45):
    f0 = F(t); n = int(dur * FPS)
    for k in range(n + 1):
        ph.rotation_euler[2] = (0.04 if k % 2 else -0.04) if k < n else 0
        ph.keyframe_insert('rotation_euler', index=2, frame=f0 + k)
for t in (0.25, 4.8, 20.3, 21.2): buzz(t)
# phone lifts up to film (9.8-14.3): stands up facing the screen
ph.keyframe_insert('location', frame=F(10.2)); ph.keyframe_insert('rotation_euler', frame=F(10.2))
ph.location = PH0 + Vector((0.07, -0.35, P['scr_z'] - P['deck_z'] - 0.05)); ph.rotation_euler = (math.radians(80), 0, 0)
ph.keyframe_insert('location', frame=F(10.9)); ph.keyframe_insert('rotation_euler', frame=F(10.9))
ph.keyframe_insert('location', frame=F(17.0)); ph.keyframe_insert('rotation_euler', frame=F(17.0))
ph.location = PH0; ph.rotation_euler = (0, 0, 0)
ph.keyframe_insert('location', frame=F(17.6)); ph.keyframe_insert('rotation_euler', frame=F(17.6))
# ---------- spin button on deck ----------
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.032, depth=0.022, location=(P['scr_x'] + P['btn_x'], FRONT_Y - P['deck_y'], P['deck_z'] + 0.014))
btn = bpy.context.active_object; btn.name = 'spinbtn'
bv = btn.modifiers.new('bv', 'BEVEL'); bv.width = 0.009; bv.segments = 6
sub = btn.modifiers.new('ss', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
bm = bpy.data.materials.new('btn'); bm.use_nodes = True; bb = bm.node_tree.nodes['Principled BSDF']
bb.inputs['Base Color'].default_value = (0.8, 0.03, 0.02, 1); bb.inputs['Roughness'].default_value = 0.08
bb.inputs['Coat Weight'].default_value = 1.0; bb.inputs['Emission Color'].default_value = (1, 0.08, 0.03, 1); bb.inputs['Emission Strength'].default_value = 0.6
btn.data.materials.append(bm)
bpy.ops.mesh.primitive_torus_add(major_radius=0.036, minor_radius=0.0055, location=(btn.location.x, btn.location.y, P['deck_z'] + 0.004))
ring = bpy.context.active_object; ring.name = 'btnring'
rm = bpy.data.materials.new('chrome'); rm.use_nodes = True; rb = rm.node_tree.nodes['Principled BSDF']
rb.inputs['Base Color'].default_value = (0.9, 0.9, 0.92, 1); rb.inputs['Metallic'].default_value = 1.0; rb.inputs['Roughness'].default_value = 0.12
ring.data.materials.append(rm)
for t in (1.6, 4.95, 20.55, 21.45):
    z0 = btn.location.z
    btn.keyframe_insert('location', index=2, frame=F(t) - 2)
    btn.location.z = z0 - 0.012; btn.keyframe_insert('location', index=2, frame=F(t) + 1)
    btn.location.z = z0; btn.keyframe_insert('location', index=2, frame=F(t) + 5)
# ---------- payout chips falling into tray ----------
ch, cobjs, cmn, cmx = place('chips', (P['scr_x'], FRONT_Y - 0.18, P['deck_z'] - 0.42))
# ---------- money pile grows (26.4-29.3) ----------
MONEY = []
mo, mobjs, mmn, mmx = place('money', (P['scr_x'] + 0.2, FRONT_Y - 0.16, P['deck_z'] + 0.001))
MS0 = mo.scale.copy(); mo.scale = MS0 * 0.001; mo.keyframe_insert('scale', frame=1); mo.keyframe_insert('scale', frame=F(26.3)); mo.scale = MS0; mo.keyframe_insert('scale', frame=F(26.3) + 4)
for k in range(9):
    piv = dup(mobjs, mo, (0.03 * (k % 3) - 0.03, 0.0, 0.042 * (k + 1)), 0.05 * k)
    piv.scale = (0.001, 0.001, 0.001); piv.keyframe_insert('scale', frame=1); piv.keyframe_insert('scale', frame=F(26.4 + k * 0.28))
    piv.scale = (1, 1, 1); piv.keyframe_insert('scale', frame=F(26.4 + k * 0.28) + 4)
# ---------- security dome above the aisle ----------
cm, cmobjs, _, _ = place('cam', (0.0, -1.7, 3.36)); cm.rotation_euler = (math.pi, 0, 0)
# ---------- circuit macro (x=40) ----------
circ, ciobjs, cimn, cimx = place('circuit', (40, 0, 0.0))
hexm = bpy.data.materials.new('hex'); hexm.use_nodes = True; nt = hexm.node_tree; b = nt.nodes['Principled BSDF']
tc = nt.nodes.new('ShaderNodeTexCoord'); mp_hex = nt.nodes.new('ShaderNodeMapping'); t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(TX + 'hex.png'); t.extension = 'REPEAT'
nt.links.new(tc.outputs['UV'], mp_hex.inputs[0]); nt.links.new(mp_hex.outputs[0], t.inputs[0])
nt.links.new(t.outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 2.5; b.inputs['Base Color'].default_value = (0, 0, 0, 1)
nt.links.new(t.outputs[0], b.inputs['Alpha'])
hx = plane('hexstream', 0.7, 1.2, (40, 0.0, cimx.z + 0.03), hexm)
mp_hex.inputs['Location'].keyframe_insert('default_value', index=1, frame=F(5.7)); mp_hex.inputs['Location'].default_value[1] = 0.8; mp_hex.inputs['Location'].keyframe_insert('default_value', index=1, frame=F(9.7))
area('cl', (40, -0.3, 0.9), 0.5, 30, (0.6, 1.0, 0.8), rot=(math.radians(20), 0, 0))
# ---------- analysis desk (x=80) ----------
st, stobjs, smn, smx = place('setup', (80, 0, 0))
gm = mat_img('graph', 'graph.png', rough=0.3, emis=1.8)
scr_g = plane('graphscr', 0.72, 0.405, ((smn.x + smx.x) / 2, smn.y + 0.25, smn.z + 1.1), gm, rot=(math.radians(90), 0, 0))
plane('deskfloor', 8, 8, (80, 0, -0.001), mat_col('df', (0.03, 0.03, 0.035), rough=0.6))
area('dk', (80, -1.5, 2.2), 1.5, 120, (0.7, 0.8, 1.0), rot=(math.radians(50), 0, 0))
anchors['screen'] = empty('a_screen', (P['scr_x'], FRONT_Y, P['scr_z']))
anchors['phone'] = empty('a_phone', ((pmn.x + pmx.x) / 2, (pmn.y + pmx.y) / 2, pmx.z))
anchors['dome'] = empty('a_dome', (0, -1.7, 3.3))
anchors['money'] = empty('a_money', (P['scr_x'] + 0.2, FRONT_Y - 0.16, P['deck_z'] + 0.3))
