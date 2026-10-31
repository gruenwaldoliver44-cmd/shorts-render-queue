# FT4 Psyche. Space set at origin (asteroid), Earth far away, spacecraft flies in; gold table room at X=5000.
import random, bmesh
random.seed(5)
V = Vector
# ---------- world: black space with stars ----------
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; nt = w.node_tree
for n in list(nt.nodes):
    if n.type != 'OUTPUT_WORLD': nt.nodes.remove(n)
tc = nt.nodes.new('ShaderNodeTexCoord'); vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 420
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900
lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.035
mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 4.0
m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 160.0
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs[0].default_value = (1, 1, 1, 1)
nt.links.new(tc.outputs['Generated'], vo.inputs['Vector']); nt.links.new(tc.outputs['Generated'], nz.inputs['Vector'])
nt.links.new(vo.outputs['Distance'], lt.inputs[0]); nt.links.new(nz.outputs[0], pw.inputs[0])
nt.links.new(lt.outputs[0], mul.inputs[0]); nt.links.new(pw.outputs[0], mul.inputs[1]); nt.links.new(mul.outputs[0], m2.inputs[0])
nt.links.new(m2.outputs[0], bg.inputs[1]); nt.links.new(bg.outputs[0], nt.nodes['World Output'].inputs[0])
sc.cycles.samples = 64
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 6.0; sun.angle = math.radians(0.6); sun.color = (1.0, 0.97, 0.92)
so = bpy.data.objects.new('sun', sun); link(so); so.rotation_euler = V((0.62, 0.68, -0.38)).to_track_quat('-Z', 'Y').to_euler()
fill = bpy.data.lights.new('fill', 'SUN'); fill.energy = 0.25; fill.color = (0.55, 0.7, 1.0)
fo = bpy.data.objects.new('fill', fill); link(fo); fo.rotation_euler = V((-0.5, -0.3, 0.6)).to_track_quat('-Z', 'Y').to_euler()
def cyl(name, r, d, loc, mat, v=48, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o
def emis(name, col, s):
    m = bpy.data.materials.new(name); m.use_nodes = True; t = m.node_tree
    for n in list(t.nodes):
        if n.type != 'OUTPUT_MATERIAL': t.nodes.remove(n)
    e = t.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = col + (1,); e.inputs[1].default_value = s
    t.links.new(e.outputs[0], t.nodes['Material Output'].inputs[0]); return m, e
def parent(c, p): c.parent = p; c.matrix_parent_inverse = p.matrix_world.inverted()

# ================= ASTEROID PSYCHE =================
ast, aobjs, amn, amx = place('asteroid', (0, 0, 0))
AC = (amn + amx) / 2
ast.location -= V((AC.x, AC.y, AC.z)); bpy.context.view_layer.update()
amn, amx = bbox(aobjs); AC = (amn + amx) / 2; AR = (amx - amn).length / 2
print('AST', [round(v, 2) for v in amn], [round(v, 2) for v in amx])
# metal-rich surface: dark rock with metallic glints
am = bpy.data.materials.new('psyche'); am.use_nodes = True; t = am.node_tree; b = t.nodes['Principled BSDF']
tcn = t.nodes.new('ShaderNodeTexCoord'); n1 = t.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.35; n1.inputs['Detail'].default_value = 10
vr = t.nodes.new('ShaderNodeTexVoronoi'); vr.inputs['Scale'].default_value = 3.0
cr = t.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (0.05, 0.048, 0.045, 1); cr.color_ramp.elements[1].color = (0.36, 0.33, 0.3, 1)
fl = t.nodes.new('ShaderNodeMath'); fl.operation = 'LESS_THAN'; fl.inputs[1].default_value = 0.12
mt = t.nodes.new('ShaderNodeMath'); mt.operation = 'MAXIMUM'; mt.inputs[1].default_value = 0.45
rg = t.nodes.new('ShaderNodeMapRange'); rg.inputs[3].default_value = 0.65; rg.inputs[4].default_value = 0.2
bp = t.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6
t.links.new(tcn.outputs['Object'], n1.inputs['Vector']); t.links.new(tcn.outputs['Object'], vr.inputs['Vector'])
t.links.new(n1.outputs[0], cr.inputs[0]); t.links.new(cr.outputs[0], b.inputs['Base Color'])
# v2: no voronoi metal dots (rendered as black polka dots). Uniform metal-rich rock + fine grit bump.
n2 = t.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 7.0; n2.inputs['Detail'].default_value = 14
t.links.new(tcn.outputs['Object'], n2.inputs['Vector'])
cr.color_ramp.elements[0].color = (0.035, 0.033, 0.03, 1); cr.color_ramp.elements[1].color = (0.30, 0.28, 0.25, 1)
b.inputs['Metallic'].default_value = 0.55
t.links.new(n2.outputs[0], rg.inputs[0]); rg.inputs[3].default_value = 0.35; rg.inputs[4].default_value = 0.62; t.links.new(rg.outputs[0], b.inputs['Roughness'])
ad = t.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'; t.links.new(n1.outputs[0], ad.inputs[0]); m3 = t.nodes.new('ShaderNodeMath'); m3.operation = 'MULTIPLY'; m3.inputs[1].default_value = 0.35
t.links.new(n2.outputs[0], m3.inputs[0]); t.links.new(m3.outputs[0], ad.inputs[1])
t.links.new(ad.outputs[0], bp.inputs['Height']); t.links.new(bp.outputs[0], b.inputs['Normal'])
for o in aobjs:
    if o.type == 'MESH':
        o.data.materials.clear(); o.data.materials.append(am)
key(ast, 'rotation_euler', 1, (0.2, 0.1, 0.0)); key(ast, 'rotation_euler', F(DUR), (0.2 + 0.35, 0.1, 1.1))
for fc in fcurves(ast):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
anchors['ast'] = empty('a_ast', (0, 0, 0))
# ================= EARTH (far) =================
EP = V((-420, 1500, -160))
earth, eobjs, emn, emx = place('earth', EP)
EC = (emn + emx) / 2; ER = (emx.x - emn.x) / 2
key(earth, 'rotation_euler', 1, (0, 0, 0)); key(earth, 'rotation_euler', F(DUR), (0, 0, 0.25))
for fc in fcurves(earth):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
atm = cyl('atm_dummy', 0.01, 0.01, (0, 0, -9999), mat_col('x', (0, 0, 0)))
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=ER * 1.025, location=EC); atmo = bpy.context.active_object; atmo.name = 'atmosphere'
amat = bpy.data.materials.new('atmo'); amat.use_nodes = True; at = amat.node_tree
for n in list(at.nodes):
    if n.type != 'OUTPUT_MATERIAL': at.nodes.remove(n)
lw = at.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
cp = at.nodes.new('ShaderNodeMath'); cp.operation = 'POWER'; cp.inputs[1].default_value = 3.0
es = at.nodes.new('ShaderNodeEmission'); es.inputs[0].default_value = (0.3, 0.55, 1.0, 1); es.inputs[1].default_value = 3.0
tr = at.nodes.new('ShaderNodeBsdfTransparent'); mx = at.nodes.new('ShaderNodeMixShader')
at.links.new(lw.outputs['Facing'], cp.inputs[0]); at.links.new(cp.outputs[0], mx.inputs[0]); at.links.new(tr.outputs[0], mx.inputs[1]); at.links.new(es.outputs[0], mx.inputs[2])
at.links.new(mx.outputs[0], at.nodes['Material Output'].inputs[0]); atmo.data.materials.append(amat); bpy.ops.object.shade_smooth()
anchors['earth'] = empty('a_earth', EC)
# ================= SPACECRAFT (procedural, Psyche-like) =================
gold = bpy.data.materials.new('mli'); gold.use_nodes = True; gt = gold.node_tree; gb = gt.nodes['Principled BSDF']
gb.inputs['Base Color'].default_value = (1.0, 0.62, 0.18, 1); gb.inputs['Metallic'].default_value = 1.0; gb.inputs['Roughness'].default_value = 0.28
gn = gt.nodes.new('ShaderNodeTexNoise'); gn.inputs['Scale'].default_value = 9.0; gn.inputs['Detail'].default_value = 8; gbp = gt.nodes.new('ShaderNodeBump'); gbp.inputs['Strength'].default_value = 0.35
gt.links.new(gn.outputs[0], gbp.inputs['Height']); gt.links.new(gbp.outputs[0], gb.inputs['Normal'])
cell = bpy.data.materials.new('cells'); cell.use_nodes = True; ct_ = cell.node_tree; cb = ct_.nodes['Principled BSDF']
br = ct_.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 12.0; br.inputs['Mortar Size'].default_value = 0.012; br.offset = 0.0
br.inputs['Color1'].default_value = (0.015, 0.025, 0.07, 1); br.inputs['Color2'].default_value = (0.02, 0.035, 0.09, 1); br.inputs['Mortar'].default_value = (0.6, 0.6, 0.62, 1)
tcc = ct_.nodes.new('ShaderNodeTexCoord'); ct_.links.new(tcc.outputs['UV'], br.inputs['Vector']); ct_.links.new(br.outputs[0], cb.inputs['Base Color'])
cb.inputs['Metallic'].default_value = 0.4; cb.inputs['Roughness'].default_value = 0.18
alu = mat_col('alu', (0.8, 0.8, 0.82), rough=0.25, metal=1.0)
whitepaint = mat_col('whitep', (0.85, 0.85, 0.83), rough=0.45)
SCP = V((60, -40, 6))
craft = empty('craft', SCP)
parts = []
parts.append(box('bus', (2.2, 2.2, 2.6), SCP, gold, bevel=0.03))
for sgn in (-1, 1):
    boom = cyl('boom', 0.06, 2.6, SCP + V((sgn * 2.4, 0, 0.2)), alu, v=16, rot=(0, math.pi / 2, 0)); parts.append(boom)
    wc = SCP + V((sgn * 5.4, 0, 0.2))
    for (dx, dz) in ((0, 0), (2.25, 0), (-2.25, 0), (0, 2.25), (0, -2.25)):
        q = V((dx, 0, dz)); q.rotate(Euler((0, math.radians(45), 0)))
        p = plane('panel', 2.2, 2.2, wc + q, cell, rot=(math.pi / 2, math.radians(45), 0)); parts.append(p)
        fr = box('pframe', (2.24, 0.04, 2.24), wc + q + V((0, 0.03, 0)), alu); fr.rotation_euler = (0, math.radians(45), 0); parts.append(fr)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0, location=SCP + V((0, -1.4, 0.6))); dish = bpy.context.active_object
dish.scale = (0.9, 0.25, 0.9); dish.data.materials.append(whitepaint); bpy.ops.object.shade_smooth(); parts.append(dish)
mag = cyl('magboom', 0.04, 3.4, SCP + V((0, 1.1, 2.9)), alu, v=12, rot=(0, 0, 0)); parts.append(mag)
ring_m = mat_col('thr', (0.2, 0.2, 0.22), rough=0.4, metal=1.0)
thr = cyl('thruster', 0.32, 0.22, SCP + V((0, 0, -1.42)), ring_m); parts.append(thr)
hm, he = emis('hall', (0.35, 0.6, 1.0), 40.0)
glow = cyl('hallglow', 0.24, 0.02, SCP + V((0, 0, -1.54)), hm); parts.append(glow)
# plume: emissive cone volume
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.25, radius2=1.2, depth=5.0, location=SCP + V((0, 0, -4.05))); plume = bpy.context.active_object; plume.name = 'plume'
pm = bpy.data.materials.new('plume'); pm.use_nodes = True; pt = pm.node_tree
for n in list(pt.nodes):
    if n.type != 'OUTPUT_MATERIAL': pt.nodes.remove(n)
ev = pt.nodes.new('ShaderNodeEmission'); ev.inputs[0].default_value = (0.3, 0.55, 1.0, 1)
gr = pt.nodes.new('ShaderNodeTexGradient'); tco = pt.nodes.new('ShaderNodeTexCoord'); mpp = pt.nodes.new('ShaderNodeMapping')
mpp.inputs['Rotation'].default_value = (0, math.radians(90), 0); mpp.inputs['Location'].default_value = (0, 0, 0.5)
mr = pt.nodes.new('ShaderNodeMapRange'); mr.inputs[1].default_value = 0.0; mr.inputs[2].default_value = 1.0; mr.inputs[3].default_value = 0.0; mr.inputs[4].default_value = 0.7
pt.links.new(tco.outputs['Generated'], mpp.inputs[0]); pt.links.new(mpp.outputs[0], gr.inputs[0]); pt.links.new(gr.outputs[0], mr.inputs[0]); pt.links.new(mr.outputs[0], ev.inputs[1])
pt.links.new(ev.outputs[0], pt.nodes['Material Output'].inputs['Volume']); plume.data.materials.append(pm); parts.append(plume)
for p in parts: parent(p, craft)
craft.rotation_euler = (math.radians(-90), 0, 0)   # thruster faces -Y: flies +Y
# flight: cruising (13.4-16.8) then approach towards Psyche (16.8-18.7)
key(craft, 'location', F(4.4), SCP + V((0, -60, 0))); key(craft, 'location', F(7.6), SCP + V((0, -42, 0))); key(craft, 'location', F(22.9), SCP + V((0, -20, 0))); key(craft, 'location', F(25.5), SCP)
for fc in fcurves(craft):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
hide_list = parts
anchors['craft'] = empty('a_craft', SCP)
# ================= GOLD TABLE (X=5000) =================
GC = V((5000, 0, 0))
o = box('groom', (8, 8, 4.5), GC + V((0, 1, 2.25)), mat_col('groomm', (0.012, 0.011, 0.012), rough=0.8))
bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
vel = bpy.data.materials.new('velvet'); vel.use_nodes = True; vb = vel.node_tree.nodes['Principled BSDF']
vb.inputs['Base Color'].default_value = (0.06, 0.012, 0.016, 1); vb.inputs['Roughness'].default_value = 0.9; vb.inputs['Sheen Weight'].default_value = 1.0; vb.inputs['Sheen Tint'].default_value = (0.8, 0.3, 0.35, 1)
box('gtable', (3.0, 2.0, 0.06), GC + V((0, 0.3, 0.77)), vel)
TT = GC + V((0, 0, 0.80))
goldm = bpy.data.materials.new('gold'); goldm.use_nodes = True; gb2 = goldm.node_tree.nodes['Principled BSDF']
gb2.inputs['Base Color'].default_value = (1.0, 0.72, 0.28, 1); gb2.inputs['Metallic'].default_value = 1.0; gb2.inputs['Roughness'].default_value = 0.16
for t, c, r in ((0, (1.0, 0.72, 0.28), 0.16), (29.4, (1.0, 0.72, 0.28), 0.16), (30.5, (0.62, 0.55, 0.45), 0.42)):
    gb2.inputs['Base Color'].default_value = c + (1,); gb2.inputs['Base Color'].keyframe_insert('default_value', frame=F(t))
    gb2.inputs['Roughness'].default_value = r; gb2.inputs['Roughness'].keyframe_insert('default_value', frame=F(t))
def goldbar(loc, rz=0.0):
    bm = bmesh.new(); L, W, Hh, L2, W2 = 0.116, 0.053, 0.03, 0.104, 0.042
    vs = [bm.verts.new(v) for v in ((-L/2, -W/2, 0), (L/2, -W/2, 0), (L/2, W/2, 0), (-L/2, W/2, 0), (-L2/2, -W2/2, Hh), (L2/2, -W2/2, Hh), (L2/2, W2/2, Hh), (-L2/2, W2/2, Hh))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([vs[i] for i in f])
    me = bpy.data.meshes.new('bar'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('bar', me); link(ob); ob.location = loc; ob.rotation_euler = (0, 0, rz); me.materials.append(goldm)
    bv = ob.modifiers.new('bv', 'BEVEL'); bv.width = 0.003; bv.segments = 3
    return ob
BARS = []
for lay in range(4):
    nx, ny = 4 - lay, 3 - min(lay, 2)
    for i in range(nx):
        for j in range(ny):
            BARS.append(goldbar(TT + V(((i - (nx - 1) / 2) * 0.118, 0.25 + (j - (ny - 1) / 2) * 0.056, lay * 0.031)), 0))
# flood of bars (24.4-25.7): metal stops being rare
for i in range(160):
    ang = random.uniform(0, 2 * math.pi); rr = random.uniform(0.25, 1.3)
    b = goldbar(TT + V((rr * math.cos(ang), 0.3 + rr * math.sin(ang) * 0.7, random.uniform(0, 0.12))), random.uniform(0, math.pi))
    t0 = 20.0 + random.uniform(0, 1.6)
    key(b, 'scale', 1, (0.001,) * 3); key(b, 'scale', F(t0), (0.001,) * 3); key(b, 'scale', F(t0) + 2, (1, 1, 1))
    zt = b.location.z; key(b, 'location', F(t0), b.location + V((0, 0, 0.5))); key(b, 'location', F(t0) + 5, V((b.location.x, b.location.y, zt)))
    for fc in fcurves(b):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if 'scale' in fc.data_path else 'BEZIER'
rng, robjs, rmn, rmx = place('ring', TT + V((-0.12, -0.12, 0.0)))
for o in robjs:
    if o.type == 'MESH' and len(o.data.materials) == 0: o.data.materials.append(goldm)
RC = (rmn + rmx) / 2
def L(name, loc, rot, size, energy, col, kind='AREA'):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = col
    if kind == 'AREA': ld.size = size
    ob = bpy.data.objects.new(name, ld); link(ob); ob.location = loc; ob.rotation_euler = rot; return ob
gk = L('gk', GC + V((-1.4, -1.6, 2.2)), (math.radians(48), 0, math.radians(-40)), 1.2, 180, (1.0, 0.85, 0.65))
gr_ = L('gr', GC + V((1.6, 1.8, 1.6)), (math.radians(-55), 0, math.radians(140)), 1.0, 120, (1.0, 0.8, 0.6))
for t, e, c in ((0, 180, (1.0, 0.85, 0.65)), (29.4, 180, (1.0, 0.85, 0.65)), (30.5, 70, (0.75, 0.82, 1.0))):
    gk.data.energy = e; gk.data.keyframe_insert('energy', frame=F(t)); gk.data.color = c; gk.data.keyframe_insert('color', frame=F(t))
anchors['bars'] = empty('a_bars', TT + V((0, 0.25, 0.06)))
anchors['ring'] = empty('a_ring', RC)
