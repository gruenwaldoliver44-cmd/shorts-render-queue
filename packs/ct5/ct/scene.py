# CT5 scratch ticket singletons: store (origin), desk (X=50)
import bpy, os, sys, math, json
from mathutils import Vector, Euler
ROOT = os.environ.get('CT_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/ct')
from common_dl import *
TX = ROOT + '/tex/'
FPS = 24
def F(t): return int(round(t * FPS)) + 1
CFG = json.load(open(ROOT + '/ct/cfg.json'))   # per-asset orientation/size, filled after the probe
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.render.fps = FPS
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
DUR = CFG['dur']; sc.frame_start = 1; sc.frame_end = F(DUR)

def link(o, coll=None): (coll or sc.collection).objects.link(o); return o
def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); link(e); e.location = loc; return e
def key(o, prop, frame, val, interp='BEZIER'):
    setattr(o, prop, val); o.keyframe_insert(prop, frame=frame)
def fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    a = ad.action
    if hasattr(a, 'fcurves') and len(a.fcurves): return list(a.fcurves)
    out = []
    for l in getattr(a, 'layers', []):
        for s in l.strips:
            for cb in s.channelbags: out += list(cb.fcurves)
    return out
def set_interp(idb, mode):
    for fc in fcurves(idb):
        for kp in fc.keyframe_points: kp.interpolation = mode

# ---------- materials ----------
def mat_img(name, img, rough=0.5, metal=0.0, alpha=False, emis=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(TX + img)
    nt.links.new(t.outputs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if alpha: nt.links.new(t.outputs[1], b.inputs['Alpha']); m.blend_method = 'HASHED' if hasattr(m, 'blend_method') else None
    if emis: nt.links.new(t.outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emis
    return m
def mat_col(name, col, rough=0.5, metal=0.0, emis=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col + (1,) if len(col) == 3 else col
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emis: b.inputs['Emission Color'].default_value = col + (1,); b.inputs['Emission Strength'].default_value = emis
    return m
def mat_ph(name, tex, scale=1.0, res='2k'):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['UV'], mp.inputs[0])
    for kind, inp in (('diff', 'Base Color'), ('rough', 'Roughness')):
        p = ph_tex(tex, kind, res)
        if not p: continue
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p)
        if kind != 'diff': t.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs[0], t.inputs[0]); nt.links.new(t.outputs[0], b.inputs[inp])
    p = ph_tex(tex, 'nor_gl', res)
    if p:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p); t.image.colorspace_settings.name = 'Non-Color'
        nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(mp.outputs[0], t.inputs[0]); nt.links.new(t.outputs[0], nm.inputs[1]); nt.links.new(nm.outputs[0], b.inputs['Normal'])
    return m

def plane(name, w, h, loc, mat, rot=(0, 0, 0), subdiv=0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if subdiv:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=subdiv); bpy.ops.object.mode_set(mode='OBJECT')
    o.data.materials.append(mat); return o
def box(name, size, loc, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = o.modifiers.new('bv', 'BEVEL'); m.width = bevel; m.segments = 3
    o.data.materials.append(mat); return o

# ---------- asset placement ----------
def place(k, loc):
    """load a BlenderKit asset, orient/scale from cfg, put its bottom-center at loc. returns (root, objs, mn, mx) in world space"""
    c = CFG['assets'][k]
    r = load_objs(k)
    if not r: raise SystemExit('ASSET FAIL ' + k + ' ' + str(NOTES))
    coll, objs, tops = r
    for o in objs:
        if o.type == 'MESH' and any(h in o.name.lower() for h in c.get('hide', [])): o.hide_render = True; o.hide_viewport = True
    root = bpy.data.objects.new('R_' + k, None); coll.objects.link(root)
    for t in tops: t.parent = root
    root.rotation_euler = [math.radians(a) for a in c.get('rot', (0, 0, 0))]
    bpy.context.view_layer.update()
    mn, mx = bbox([o for o in objs if not o.hide_render]); d = mx - mn
    s = c['size'] / getattr(d, c.get('fit', 'z'))
    root.scale = (s, s, s); bpy.context.view_layer.update()
    mn, mx = bbox([o for o in objs if not o.hide_render])
    ctr = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    root.location = Vector(loc) - ctr; bpy.context.view_layer.update()
    mn, mx = bbox([o for o in objs if not o.hide_render])
    return root, objs, mn, mx
def find(objs, sub):
    for o in objs:
        if sub.lower() in o.name.lower(): return o
    return None

anchors = {}
exec(open(ROOT + '/ct/body.py').read())
exec(open(ROOT + '/ct/tail.py').read())
