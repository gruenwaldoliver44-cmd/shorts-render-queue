# Machine Times: "The internet lies on the ocean floor" (16:9, 25 fps, Blender 5.2 / Eevee). Build: Blender -b -P cable.py -- save
import bpy, bmesh, math, os, sys, json, uuid, random, time, urllib.request, urllib.parse
from mathutils import Vector, Matrix, Euler
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "save"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cable_common as C
HOME = os.environ.get("AGENT_HOME", os.path.expanduser("~/ShortsRenderAgent"))
ADIR = os.path.join(HOME, "assets"); os.makedirs(ADIR, exist_ok=True)
NOTES = []
random.seed(7)
T0 = time.time()
FPS = C.FPS
def F(t): return C.fr(t)
D = math.radians
# ================================================================ helpers
def setattr_safe(obj, attr, val):
    try: setattr(obj, attr, val); return True
    except Exception: return False

def sock(node, key):
    s = node.inputs.get(key)
    if s is None: s = next((x for x in node.inputs if x.identifier == key), None)
    return s

def SV(node, key, val):
    try:
        s = sock(node, key) if isinstance(key, str) else node.inputs[key]
        if s is None or not hasattr(s, "default_value"):
            NOTES.append("SV skip %s.%s" % (node.bl_idname, key)); return None
        dv = s.default_value
        if hasattr(dv, "__len__"):
            v = tuple(val) if hasattr(val, "__len__") else (val,) * len(dv)
            k = len(dv); v = v[:k] if len(v) >= k else v + (1.0,) * (k - len(v))
            s.default_value = v
        else:
            s.default_value = type(dv)(val) if isinstance(dv, (int, float, bool)) else val
        return s
    except Exception as e:
        NOTES.append("SV err %s %s" % (key, type(e).__name__)); return None

PREFS = bpy.context.preferences.edit
def K(idb, path, frame, interp="LINEAR", index=-1):
    try:
        PREFS.keyframe_new_interpolation_type = interp
    except Exception: pass
    try:
        idb.keyframe_insert(path, frame=frame, index=index)
    except TypeError:
        idb.keyframe_insert(path, frame=frame)
    except Exception as e:
        NOTES.append("K err %s %s" % (path, type(e).__name__))

def KV(s, frame, val, interp="LINEAR"):
    """keyframe a node socket default_value"""
    if s is None: return
    try:
        dv = s.default_value
        if hasattr(dv, "__len__"):
            v = tuple(val) if hasattr(val, "__len__") else (val,) * len(dv)
            v = v[:len(dv)] if len(v) >= len(dv) else v + (1.0,) * (len(dv) - len(v))
            s.default_value = v
        else:
            s.default_value = val
        K(s, "default_value", frame, interp)
    except Exception as e:
        NOTES.append("KV err %s" % type(e).__name__)

def merge_ranges(ranges, gap=0.05):
    out = []
    for a, b in sorted(ranges):
        if out and a <= out[-1][1] + gap: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out

def vis(o, ranges, pad=1):
    """object renders only inside the given time ranges (seconds)"""
    o.hide_render = True; K(o, "hide_render", 1, "CONSTANT")
    for (a, b) in merge_ranges(ranges):
        o.hide_render = False; K(o, "hide_render", max(1, F(a) - pad), "CONSTANT")
        o.hide_render = True; K(o, "hide_render", F(b) + pad, "CONSTANT")
    o.hide_viewport = False

ROOT = bpy.context.scene.collection
def link(o, coll=None):
    (coll or ROOT).objects.link(o); return o

def new_mesh_obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return link(bpy.data.objects.new(name, me))

def prim(kind, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), smooth=True, **kw):
    fn = {"sphere": bpy.ops.mesh.primitive_uv_sphere_add, "cyl": bpy.ops.mesh.primitive_cylinder_add,
          "cube": bpy.ops.mesh.primitive_cube_add, "plane": bpy.ops.mesh.primitive_plane_add,
          "torus": bpy.ops.mesh.primitive_torus_add, "cone": bpy.ops.mesh.primitive_cone_add,
          "ico": bpy.ops.mesh.primitive_ico_sphere_add, "grid": bpy.ops.mesh.primitive_grid_add}[kind]
    fn(location=loc, rotation=rot, **kw)
    o = bpy.context.active_object; o.name = name; o.scale = scale
    if smooth and kind in ("sphere", "cyl", "torus", "cone", "ico"):
        try: bpy.ops.object.shade_smooth()
        except Exception: pass
    return o

def apply_scale(o):
    for x in bpy.context.selected_objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

def setmat(o, m):
    o.data.materials.clear(); o.data.materials.append(m); return o

# ================================================================ materials
MATS = {}
def mat(name, col=(0.8, 0.8, 0.8), rough=0.5, metal=0.0, emit=None, es=0.0, alpha=1.0, coat=0.0,
        trans=0.0, ior=1.45, film=0.0, film_ior=1.6, spec=0.5):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    SV(b, "Base Color", (*col, 1)); SV(b, "Roughness", rough); SV(b, "Metallic", metal)
    if coat: SV(b, "Coat Weight", coat)
    if trans: SV(b, "Transmission Weight", trans); SV(b, "IOR", ior)
    if film: SV(b, "Thin Film Thickness", film); SV(b, "Thin Film IOR", film_ior)
    SV(b, "Emission Color", (*(emit or (0, 0, 0)), 1)); SV(b, "Emission Strength", es)
    if alpha < 1: SV(b, "Alpha", alpha); setattr_safe(m, "surface_render_method", "BLENDED")
    MATS[name] = m
    return m

def bsdf(m): return m.node_tree.nodes.get("Principled BSDF")

def emat(name, col, strength, alpha=None, solid=False, soft=0.0):
    """emission material. solid=True: opaque emitter (text, filament). Otherwise additive glow
    (transparent + emission): invisible when the strength is 0. alpha scales the glow."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    SV(em, "Color", (*col, 1))
    if solid:
        SV(em, "Strength", strength)
        nt.links.new(em.outputs[0], out.inputs["Surface"])
        MATS[name] = m
        return m, sock(em, "Strength")
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; SV(mul, 0, strength); SV(mul, 1, 1.0 if alpha is None else alpha)
    if soft:
        lw = N.new("ShaderNodeLayerWeight"); SV(lw, "Blend", 0.5)
        inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; SV(inv, 0, 1.0); nt.links.new(lw.outputs["Facing"], inv.inputs[1])
        pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; nt.links.new(inv.outputs[0], pw.inputs[0]); SV(pw, 1, soft)
        m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; nt.links.new(mul.outputs[0], m2.inputs[0]); nt.links.new(pw.outputs[0], m2.inputs[1])
        nt.links.new(m2.outputs[0], em.inputs["Strength"])
    else:
        nt.links.new(mul.outputs[0], em.inputs["Strength"])
    tr = N.new("ShaderNodeBsdfTransparent"); ad = N.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], ad.inputs[0]); nt.links.new(em.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs["Surface"])
    setattr_safe(m, "surface_render_method", "BLENDED")
    MATS[name] = m
    return m, mul.inputs[0]

def beam_mat(name, col, strength, axis="Z", fade=None):
    """emissive beam with an animatable 'front' (object-space coordinate along axis):
    visible where coord < front; optional fade (a, b): fully bright below a, gone above b. Returns (mat, front socket, strength socket)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); em = N.new("ShaderNodeEmission")
    tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader")
    tc = N.new("ShaderNodeTexCoord"); sp = N.new("ShaderNodeSeparateXYZ")
    Lk.new(tc.outputs["Object"], sp.inputs[0])
    cmp = N.new("ShaderNodeMath"); cmp.operation = "LESS_THAN"
    Lk.new(sp.outputs[axis], cmp.inputs[0]); SV(cmp, 1, 1e6)
    fac = cmp.outputs[0]
    if fade:
        mr = N.new("ShaderNodeMapRange"); setattr_safe(mr, "interpolation_type", "SMOOTHSTEP")
        Lk.new(sp.outputs[axis], mr.inputs[0]); SV(mr, 1, fade[0]); SV(mr, 2, fade[1]); SV(mr, 3, 1.0); SV(mr, 4, 0.0)
        mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        Lk.new(cmp.outputs[0], mul.inputs[0]); Lk.new(mr.outputs[0], mul.inputs[1]); fac = mul.outputs[0]
    SV(em, "Color", (*col, 1))
    st = N.new("ShaderNodeMath"); st.operation = "MULTIPLY"; SV(st, 0, strength)
    Lk.new(fac, st.inputs[1]); Lk.new(st.outputs[0], em.inputs["Strength"])
    ad = N.new("ShaderNodeAddShader"); N.remove(mx)
    Lk.new(tr.outputs[0], ad.inputs[0]); Lk.new(em.outputs[0], ad.inputs[1])
    Lk.new(ad.outputs[0], out.inputs["Surface"])
    setattr_safe(m, "surface_render_method", "BLENDED")
    return m, cmp.inputs[1], st.inputs[0]

# ================================================================ downloads (BlenderKit / Poly Haven)
UA = {"User-Agent": "blenderkit/3.21.3 (Blender 5.2.3)", "accept": "application/json"}
def get_key():
    for name, ad in bpy.context.preferences.addons.items():
        if "blenderkit" in name.lower():
            return getattr(ad.preferences, "api_key", "") or ""
    return ""
KEY = get_key()
BKP = os.path.join(HERE, "bk.json")
BK = json.load(open(BKP)) if os.path.exists(BKP) else {}

def fetch(url, path, timeout=600):
    req = urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(path + ".part", "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)
    os.replace(path + ".part", path)

def bk_file(key):
    if key not in BK: NOTES.append("noBK " + key); return None
    aid, durl = BK[key]
    p = os.path.join(ADIR, "bk_" + aid + ".blend")
    if os.path.exists(p) and os.path.getsize(p) > 1000: return p
    errs = []
    for host_url in [durl, durl.replace("www.blenderkit.com", "api.blenderkit.com")]:
        try:
            h = dict(UA); h["Authorization"] = "Bearer " + KEY
            q = host_url + "?" + urllib.parse.urlencode({"scene_uuid": str(uuid.uuid4())})
            r = urllib.request.urlopen(urllib.request.Request(q, headers=h), timeout=60)
            fp = json.loads(r.read().decode())["filePath"]
            fetch(fp, p)
            return p
        except Exception as e:
            errs.append(type(e).__name__ + ":" + str(getattr(e, "code", ""))[:6])
    NOTES.append("BK " + key + " " + "/".join(errs))
    return None

PH = "https://dl.polyhaven.org/file/ph-assets/"
def ph_hdri(name):
    p = os.path.join(ADIR, "ph_%s_2k.hdr" % name)
    if not os.path.exists(p):
        try: fetch(PH + "HDRIs/hdr/2k/%s_2k.hdr" % name, p)
        except Exception: NOTES.append("PH hdri " + name); return None
    return p

def ph_tex(name, kind):
    p = os.path.join(ADIR, "ph_%s_%s_1k.jpg" % (name, kind))
    if not os.path.exists(p):
        try: fetch(PH + "Textures/jpg/1k/%s/%s_%s_1k.jpg" % (name, name, kind), p)
        except Exception: NOTES.append("PH " + name + kind); return None
    return p

def bbox_of(objs):
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != "MESH": continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector((min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)))
            mx = Vector((max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)))
    return mn, mx

def load_asset(key, size, loc, rot=(0, 0, 0), axis="max", ground=True):
    """append a BlenderKit model, scale its largest (or given axis) dimension to `size`, put its bottom-centre at loc.
    returns root empty or None"""
    p = bk_file(key)
    if not p: return None
    try:
        with bpy.data.libraries.load(p, link=False) as (df, dt):
            dt.objects = list(df.objects)
        objs = [o for o in dt.objects if o is not None]
    except Exception as e:
        NOTES.append("load %s %s" % (key, type(e).__name__)); return None
    coll = bpy.data.collections.new("as_" + key); ROOT.children.link(coll)
    for o in objs:
        try: coll.objects.link(o)
        except Exception: pass
    root = bpy.data.objects.new("root_" + key, None); coll.objects.link(root)
    for o in objs:
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    mn, mx = bbox_of(objs)
    if mn.x > 1e8: NOTES.append("empty asset " + key); return root
    dims = mx - mn
    ref = {"max": max(dims), "x": dims.x, "y": dims.y, "z": dims.z}[axis]
    s = size / max(ref, 1e-6)
    ctr = (mn + mx) / 2
    root.scale = (s, s, s)
    root.location = Vector(loc) - Vector((ctr.x * s, ctr.y * s, (mn.z if ground else ctr.z) * s))
    bpy.context.view_layer.update()
    # rotate around its new bottom centre
    if any(rot):
        piv = bpy.data.objects.new("piv_" + key, None); coll.objects.link(piv); piv.location = loc
        root.parent = piv; root.location = root.location - Vector(loc); piv.rotation_euler = rot
        bpy.context.view_layer.update()
        INFO_ASSETS[key] = {"dims": [round(x, 3) for x in dims], "scale": round(s, 4)}
        return piv
    INFO_ASSETS[key] = {"dims": [round(x, 3) for x in dims], "scale": round(s, 4)}
    return root
INFO_ASSETS = {}

def set_children_vis(root, ranges):
    if root is None: return
    stack = [root]
    while stack:
        o = stack.pop(); stack.extend(o.children)
        if o.type in ("MESH", "CURVE", "FONT", "LIGHT"): vis(o, ranges)

# ================================================================ fonts / text
FONT = None
for fp in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Futura.ttc",
           "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
    if os.path.exists(fp):
        try: FONT = bpy.data.fonts.load(fp); break
        except Exception: pass

def text3d(name, body, loc, size=0.5, rot=(D(90), 0, 0), col=(1, 1, 1), es=3.0, extrude=0.0, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = "CENTER"
    if FONT: cu.font = FONT
    o = link(bpy.data.objects.new(name, cu)); o.location = loc; o.rotation_euler = rot
    m, s = emat("tx_" + name, col, es, solid=True)
    cu.materials.append(m)
    return o, s

def pop_in(o, t, dur=0.25, s1=1.0):
    o.scale = (0.001,) * 3; K(o, "scale", F(t) - 1, "LINEAR")
    o.scale = (s1 * 1.08,) * 3; K(o, "scale", F(t + dur * 0.7), "BEZIER")
    o.scale = (s1,) * 3; K(o, "scale", F(t + dur), "BEZIER")

# ================================================================ scene / render
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, C.NF
sc.render.engine = "BLENDER_EEVEE"
ee = sc.eevee
setattr_safe(ee, "taa_render_samples", 20)
setattr_safe(ee, "use_raytracing", True)
try:
    ee.ray_tracing_options.resolution_scale = "2"; ee.ray_tracing_options.use_denoise = True
except Exception: pass
setattr_safe(ee, "use_shadows", True)
setattr_safe(ee, "shadow_ray_count", 1); setattr_safe(ee, "shadow_step_count", 4)
setattr_safe(ee, "use_fast_gi", True)
setattr_safe(ee, "volumetric_end", 80.0); setattr_safe(ee, "volumetric_tile_size", "8"); setattr_safe(ee, "volumetric_samples", 48)
setattr_safe(sc.render, "use_motion_blur", True); setattr_safe(sc.render, "motion_blur_shutter", 0.5)
setattr_safe(sc.view_settings, "view_transform", "AgX")
for lk in ["AgX - Medium High Contrast", "Medium High Contrast"]:
    if setattr_safe(sc.view_settings, "look", lk): break
sc.view_settings.exposure = 0.0
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = C.W, C.H, 100
setattr_safe(sc.render, "use_persistent_data", True)

# world: HDRI lights everything (reflections), camera rays see a dark backdrop
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
nt = w.node_tree; N = nt.nodes; Lk = nt.links
for n in list(N): N.remove(n)
wout = N.new("ShaderNodeOutputWorld")
env = N.new("ShaderNodeTexEnvironment")
hp = ph_hdri("kloofendal_48d_partly_cloudy_puresky") or ph_hdri("moonless_golf")
WL = N.new("ShaderNodeBackground"); SV(WL, "Strength", 0.55)
WC = N.new("ShaderNodeBackground"); SV(WC, "Color", (0.004, 0.005, 0.008, 1)); SV(WC, "Strength", 1.0)
if hp:
    env.image = bpy.data.images.load(hp); Lk.new(env.outputs["Color"], WL.inputs["Color"])
else:
    SV(WL, "Color", (0.35, 0.45, 0.6, 1))
lp_ = N.new("ShaderNodeLightPath"); mix = N.new("ShaderNodeMixShader")
Lk.new(lp_.outputs["Is Camera Ray"], mix.inputs[0]); Lk.new(WL.outputs[0], mix.inputs[1]); Lk.new(WC.outputs[0], mix.inputs[2])
Lk.new(mix.outputs[0], wout.inputs["Surface"])
WLS = sock(WL, "Strength"); WLS.default_value = 0.0   # no sky inside the chamber / lab / phone sets
def sky_dome(name, center, radius):
    """inward-facing sphere that shows the HDRI sky (only around the Germany sets)"""
    o = prim("sphere", name, loc=center, segments=64, ring_count=32, radius=radius)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.flip_normals(); bpy.ops.object.mode_set(mode="OBJECT")
    m = bpy.data.materials.new(name + "_m"); m.use_nodes = True
    nt_ = m.node_tree; N_ = nt_.nodes
    for n in list(N_): N_.remove(n)
    out_ = N_.new("ShaderNodeOutputMaterial"); em_ = N_.new("ShaderNodeEmission"); SV(em_, "Strength", 1.0)
    tc_ = N_.new("ShaderNodeTexCoord"); en_ = N_.new("ShaderNodeTexEnvironment")
    if hp:
        en_.image = bpy.data.images.load(hp) if not bpy.data.images.get(os.path.basename(hp)) else bpy.data.images.get(os.path.basename(hp))
        nt_.links.new(tc_.outputs["Object"], en_.inputs["Vector"]); nt_.links.new(en_.outputs["Color"], em_.inputs["Color"])
    else:
        SV(em_, "Color", (0.35, 0.5, 0.75, 1))
    nt_.links.new(em_.outputs[0], out_.inputs["Surface"])
    setmat(o, m)
    return o

def area(name, loc, rot, energy, size=2.0, col=(1, 1, 1), shape="RECTANGLE", sy=None):
    ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.color = col; ld.size = size
    setattr_safe(ld, "shape", shape)
    if sy: ld.size_y = sy
    o = link(bpy.data.objects.new(name, ld)); o.location = loc; o.rotation_euler = rot
    return o

def point(name, loc, energy, col=(1, 1, 1), radius=0.1):
    ld = bpy.data.lights.new(name, "POINT"); ld.energy = energy; ld.color = col; ld.shadow_soft_size = radius
    o = link(bpy.data.objects.new(name, ld)); o.location = loc
    return o

def spot(name, loc, rot, energy, size_deg=45, blend=0.5, col=(1, 1, 1), radius=0.2):
    ld = bpy.data.lights.new(name, "SPOT"); ld.energy = energy; ld.color = col
    ld.spot_size = D(size_deg); ld.spot_blend = blend; ld.shadow_soft_size = radius
    o = link(bpy.data.objects.new(name, ld)); o.location = loc; o.rotation_euler = rot
    return o

def aim(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# ======================================================================== constants
_vis_orig = vis
VISED = set()
def vis(o, ranges, pad=1):
    if o is None or o.name in VISED: return
    VISED.add(o.name); _vis_orig(o, ranges, pad)
steel = mat("steel", (0.32, 0.33, 0.35), 0.32, 1.0)
steel_dk = mat("steel_dk", (0.08, 0.085, 0.09), 0.45, 1.0)
LON_OFF = -50.0
CYAN = (0.35, 0.85, 1.0)
WATER = (0.02, 0.18, 0.28)
S = Vector(C.S); P = Vector(C.P); E = Vector(C.E); X = Vector(C.X); Fb = Vector(C.Fb); Wv = Vector(C.Wv)
def shots_of(*ids): return [(s[1], s[2]) for s in C.SHOTS if s[0] in ids]
def set_ranges(st): return [(s[1], s[2]) for s in C.SHOTS if s[3] == st]
INFO = {}

def vis_tree(root, ranges):
    if root is None: return
    st = [root]
    while st:
        o = st.pop(); st.extend(o.children)
        if o.type in ("MESH", "CURVE", "FONT", "LIGHT", "ARMATURE"):
            if o.name.startswith("WGT") or o.hide_render or o.hide_get(): o.hide_render = True; continue
            vis(o, ranges)

def curve_obj(name, pts, bevel, col_mat, cyclic=False, res=4):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = bevel; cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)
    sp.use_cyclic_u = cyclic
    o = link(bpy.data.objects.new(name, cu)); cu.materials.append(col_mat)
    return o

def grow(o, t0, t1, interp="LINEAR"):
    cu = o.data
    cu.bevel_factor_end = 0.0; K(cu, "bevel_factor_end", F(t0), interp)
    cu.bevel_factor_end = 1.0; K(cu, "bevel_factor_end", F(t1), interp)

def stamp_x(name, loc, size, rot, t, ranges):
    m, s_ = emat(name + "_m", (1.0, 0.12, 0.1), 6.0, solid=True)
    piv = link(bpy.data.objects.new(name + "_piv", None)); piv.location = loc; piv.rotation_euler = rot
    for i, ang in enumerate((45, -45)):
        b_ = prim("cube", name + "_bar%d" % i, loc=(0, 0, 0), scale=(size, size * 0.12, size * 0.03), smooth=False)
        setmat(b_, m); b_.parent = piv; b_.location = (0, 0, 0); b_.rotation_euler = (0, 0, D(ang))
        vis(b_, ranges)
    pop_in(piv, t, 0.2)
    return piv

# ======================================================================== world look per set: dark; sky only via domes
# ---------------------------------------------------------------- SET S: seabed
sand_m = mat("sand_m", (0.36, 0.33, 0.26), 0.9, 0.0)
try:
    nt_ = sand_m.node_tree; b_ = bsdf(sand_m)
    tc_ = nt_.nodes.new("ShaderNodeTexCoord")
    nz = nt_.nodes.new("ShaderNodeTexNoise"); SV(nz, "Scale", 0.35); SV(nz, "Detail", 8)
    nt_.links.new(tc_.outputs["Object"], nz.inputs["Vector"])
    cr = nt_.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.05, 0.06, 0.06, 1); cr.color_ramp.elements[1].color = (0.16, 0.16, 0.14, 1)
    nt_.links.new(nz.outputs["Fac"], cr.inputs[0]); nt_.links.new(cr.outputs[0], b_.inputs["Base Color"])
    rp = nt_.nodes.new("ShaderNodeTexWave"); SV(rp, "Scale", 0.25); SV(rp, "Distortion", 6.0)
    bmp = nt_.nodes.new("ShaderNodeBump"); SV(bmp, "Strength", 0.35)
    nt_.links.new(tc_.outputs["Object"], rp.inputs["Vector"]); nt_.links.new(rp.outputs["Fac"], bmp.inputs["Height"]); nt_.links.new(bmp.outputs["Normal"], b_.inputs["Normal"])
    # caustics: animated voronoi emission
    vo = nt_.nodes.new("ShaderNodeTexVoronoi"); vo.voronoi_dimensions = "4D"; vo.feature = "DISTANCE_TO_EDGE"; SV(vo, "Scale", 0.4)
    nt_.links.new(tc_.outputs["Object"], vo.inputs["Vector"])
    KV(sock(vo, "W"), 1, 0.0, "LINEAR"); KV(sock(vo, "W"), C.NF, C.DUR * 0.35, "LINEAR")
    mr = nt_.nodes.new("ShaderNodeMapRange"); SV(mr, 1, 0.0); SV(mr, 2, 0.02); SV(mr, 3, 0.12); SV(mr, 4, 0.0)
    nt_.links.new(vo.outputs["Distance"], mr.inputs[0]); nt_.links.new(mr.outputs[0], b_.inputs["Emission Strength"])
    SV(b_, "Emission Color", (0.45, 0.75, 0.85, 1))
except Exception as e: NOTES.append("sand " + str(e)[:60])
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=240, y_segments=120, size=1.0)
from mathutils import noise as mnoise
for v in bm.verts:
    x, y = v.co.x * 160, v.co.y * 80
    k = min(1.0, max(0.0, (abs(y) - 1.2) / 8.0)); k = k * k * (3 - 2 * k)
    h = mnoise.fractal(Vector((x / 22.0, y / 22.0, 0.3)), 0.5, 2.0, 4) * 1.6 * k - 0.05
    v.co = Vector((x, y, h))
sea = new_mesh_obj("seabed", bm); sea.location = S
tx = bpy.data.textures.new("dunes", "CLOUDS"); tx.noise_scale = 18.0
for p_ in sea.data.polygons: p_.use_smooth = True
setmat(sea, sand_m)
# flatten a corridor for the cable
fl = sea.modifiers.new("flat", "VERTEX_WEIGHT_PROXIMITY") if False else None
# rocks
rock_m = mat("rock_m", (0.14, 0.14, 0.13), 0.85, 0.0)
random.seed(3)
for i in range(70):
    x = random.uniform(-140, 140); y = random.choice([-1, 1]) * random.uniform(6, 70)
    r = random.uniform(0.4, 3.5)
    rk = prim("ico", "rock%d" % i, loc=S + Vector((x, y, -r * 0.3)), subdivisions=2, radius=r, smooth=True)
    rk.scale = (1, random.uniform(0.6, 1.3), random.uniform(0.4, 0.8)); rk.rotation_euler = (0, 0, random.uniform(0, 6))
    d2 = rk.modifiers.new("d", "DISPLACE"); d2.texture = tx; d2.strength = r * 0.4
    setmat(rk, rock_m)
# underwater fog
fog_m = bpy.data.materials.new("fog_m"); fog_m.use_nodes = True
ntf = fog_m.node_tree
for n in list(ntf.nodes): ntf.nodes.remove(n)
fo = ntf.nodes.new("ShaderNodeOutputMaterial"); fv = ntf.nodes.new("ShaderNodeVolumePrincipled")
SV(fv, "Color", (0.06, 0.32, 0.5, 1)); SV(fv, "Density", 0.022); SV(fv, "Absorption Color", (0.12, 0.42, 0.55, 1))
ntf.links.new(fv.outputs[0], fo.inputs["Volume"])
fog = prim("cube", "fog", loc=S + Vector((0, 0, 75)), scale=(160, 90, 76), smooth=False); setmat(fog, fog_m)
sun = spot("sea_sun", S + Vector((-20, -30, 150)), (0, 0, 0), 9.0e5, 70, 0.6, (0.75, 0.92, 1.0), 6.0); aim(sun, S + Vector((10, 10, 0)))
amb = area("sea_fill", S + Vector((0, -60, 60)), (0, 0, 0), 4.0e4, 120.0, (0.35, 0.6, 0.75)); aim(amb, S)
# water surface from below + bright sky behind it (for the ship shot)
surf_m = mat("surf_m", (0.6, 0.85, 0.95), 0.05, 0.0, trans=1.0, ior=1.33)
try:
    nts = surf_m.node_tree; bs = bsdf(surf_m); wn = nts.nodes.new("ShaderNodeTexNoise"); SV(wn, "Scale", 0.08); SV(wn, "Detail", 4)
    bb = nts.nodes.new("ShaderNodeBump"); SV(bb, "Strength", 0.6); nts.links.new(wn.outputs["Fac"], bb.inputs["Height"]); nts.links.new(bb.outputs["Normal"], bs.inputs["Normal"])
    KV(sock(wn, "W"), 1, 0.0); wn.noise_dimensions = "4D"; KV(sock(wn, "W"), C.NF, 8.0)
except Exception: pass
surf = prim("plane", "surface", loc=S + Vector((0, 0, 150)), size=400); setmat(surf, surf_m)
skyp_m, _ = emat("skyplane_m", (0.8, 0.93, 1.0), 1.6, solid=True)
skyp = prim("plane", "skyplane", loc=S + Vector((0, 0, 175)), size=600, rot=(D(180), 0, 0)); setmat(skyp, skyp_m)
for o_ in (surf, skyp): vis(o_, shots_of("s14", "s15"))

# ---- the cable on the seabed (with light pulses running along it)
def cable_mat(name, fade=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt_ = m.node_tree; b_ = nt_.nodes.get("Principled BSDF")
    SV(b_, "Base Color", (0.03, 0.03, 0.035, 1)); SV(b_, "Roughness", 0.42); SV(b_, "Coat Weight", 0.3)
    SV(b_, "Emission Color", (*CYAN, 1))
    gp = nt_.nodes.new("ShaderNodeNewGeometry"); sp = nt_.nodes.new("ShaderNodeSeparateXYZ"); nt_.links.new(gp.outputs["Position"], sp.inputs[0])
    off = nt_.nodes.new("ShaderNodeMath"); off.operation = "SUBTRACT"; nt_.links.new(sp.outputs["X"], off.inputs[0])
    KV(off.inputs[1], 1, 0.0, "LINEAR"); KV(off.inputs[1], C.NF, C.CAB_SPEED * C.DUR, "LINEAR")
    dv = nt_.nodes.new("ShaderNodeMath"); dv.operation = "DIVIDE"; nt_.links.new(off.outputs[0], dv.inputs[0]); SV(dv, 1, 3.0)
    fr_ = nt_.nodes.new("ShaderNodeMath"); fr_.operation = "FRACT"; nt_.links.new(dv.outputs[0], fr_.inputs[0])
    lt = nt_.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; nt_.links.new(fr_.outputs[0], lt.inputs[0]); SV(lt, 1, 0.22)
    # only a thin stripe on top of the cable (the "light inside")
    sz = nt_.nodes.new("ShaderNodeMath"); sz.operation = "GREATER_THAN"; nt_.links.new(sp.outputs["Z"], sz.inputs[0]); SV(sz, 1, S.z + 0.13)
    mul = nt_.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; nt_.links.new(lt.outputs[0], mul.inputs[0]); nt_.links.new(sz.outputs[0], mul.inputs[1])
    st = nt_.nodes.new("ShaderNodeMath"); st.operation = "MULTIPLY"; nt_.links.new(mul.outputs[0], st.inputs[0]); SV(st, 1, 9.0)
    out_ = st.outputs[0]
    if fade:
        # brightness falls from 1 to 0.12 between fade[0] and fade[1] (repeater at fade[1]), back to 1 after it
        mr = nt_.nodes.new("ShaderNodeMapRange"); nt_.links.new(sp.outputs["X"], mr.inputs[0]); SV(mr, 1, fade[0]); SV(mr, 2, fade[1]); SV(mr, 3, 1.0); SV(mr, 4, 0.1)
        gt = nt_.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; nt_.links.new(sp.outputs["X"], gt.inputs[0]); SV(gt, 1, fade[1])
        mx = nt_.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"; nt_.links.new(mr.outputs[0], mx.inputs[0]); nt_.links.new(gt.outputs[0], mx.inputs[1])
        st2 = nt_.nodes.new("ShaderNodeMath"); st2.operation = "MULTIPLY"; nt_.links.new(out_, st2.inputs[0]); nt_.links.new(mx.outputs[0], st2.inputs[1]); out_ = st2.outputs[0]
    gate = nt_.nodes.new("ShaderNodeMath"); gate.operation = "MULTIPLY"; nt_.links.new(out_, gate.inputs[0]); SV(gate, 1, 1.0)
    nt_.links.new(gate.outputs[0], b_.inputs["Emission Strength"])
    return m, gate.inputs[1]
CR = 0.1
def cable_path(x0, x1, step=0.5, seed=1):
    pts = []
    x = x0
    while x <= x1:
        y = 0.35 * math.sin(x * 0.07 + seed) + 0.15 * math.sin(x * 0.21)
        pts.append((S.x + x, S.y + y, S.z + CR)); x += step
    return pts
cab_m, CAB_GATE = cable_mat("cable_m", fade=(20.0, 29.4))
SNAP_X = -30.0
cabL = curve_obj("cable_L", cable_path(-150, SNAP_X), CR, cab_m)
cabR = curve_obj("cable_R", cable_path(SNAP_X, 150), CR, cab_m)
# break: two ends pull apart, light dies
for o_, d in ((cabL, -1), (cabR, 1)):
    o_.location = (0, 0, 0); K(o_, "location", F(C.EV["snap"]), "CONSTANT")
    o_.location = (d * 0.5, 0.15 * d, 0.05); K(o_, "location", F(C.EV["snap"] + 0.25), "BEZIER")
    o_.location = (d * 0.65, 0.2 * d, 0.0); K(o_, "location", F(C.EV["snap"] + 1.0), "BEZIER")
    o_.location = (0, 0, 0); K(o_, "location", F(41.3), "CONSTANT")
KV(CAB_GATE, 1, 1.0, "CONSTANT"); KV(CAB_GATE, F(C.EV["snap"]) + 2, 1.0, "CONSTANT"); KV(CAB_GATE, F(C.EV["snap"]) + 3, 0.0, "CONSTANT"); KV(CAB_GATE, F(41.3), 1.0, "CONSTANT")
spark_m, spark_s = emat("spark_m", (1.0, 0.75, 0.4), 0.0)
sparks = []
random.seed(11)
for i in range(26):
    sp_ = prim("ico", "spark%d" % i, loc=S + Vector((SNAP_X, 0, CR)), subdivisions=1, radius=0.025); setmat(sp_, spark_m)
    dvec = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0.2, 1.2))).normalized() * random.uniform(0.6, 1.6)
    sp_.location = S + Vector((SNAP_X, 0, CR)); K(sp_, "location", F(C.EV["snap"]), "CONSTANT")
    sp_.location = S + Vector((SNAP_X, 0, CR)) + dvec; K(sp_, "location", F(C.EV["snap"] + 0.6), "BEZIER")
    vis(sp_, shots_of("s11"))
KV(spark_s, 1, 0.0, "CONSTANT"); KV(spark_s, F(C.EV["snap"]), 40.0, "CONSTANT"); KV(spark_s, F(C.EV["snap"] + 0.6), 0.0, "LINEAR")
flash = point("snap_flash", S + Vector((SNAP_X, 0, 0.4)), 0.0, (1.0, 0.8, 0.6), 0.1)
flash.data.energy = 0; K(flash.data, "energy", F(C.EV["snap"]) - 1, "CONSTANT"); flash.data.energy = 300; K(flash.data, "energy", F(C.EV["snap"]), "CONSTANT")
flash.data.energy = 0; K(flash.data, "energy", F(C.EV["snap"] + 0.5), "LINEAR")
tyr, _ = text3d("t_year", "~200 breaks every year", S + Vector((SNAP_X, 0.8, 0.72)), size=0.15, es=3.0)
pop_in(tyr, C.EV["yr_text"]); vis(tyr, shots_of("s11"))
# garden hose next to the cable (s06)
hose_m = mat("hose_m", (0.08, 0.55, 0.12), 0.35, 0.0, coat=0.4)
hpts = []
for i in range(80):
    x = -16 + i * 0.25; hpts.append((S.x + x, S.y + 0.55 + 0.25 * math.sin(i * 0.12), S.z + 0.105))
hose = curve_obj("hose", hpts, 0.105, hose_m)
hose.location = (0, 0, 2.5); K(hose, "location", F(C.EV["hose"]) - 1, "CONSTANT")
hose.location = (0, 0, 0); K(hose, "location", F(C.EV["hose"] + 0.35), "BEZIER")
vis(hose, shots_of("s06"))
th1, _ = text3d("t_hose", "garden hose", S + Vector((-8.6, 0.75, 0.42)), size=0.1, es=2.5, rot=(D(70), 0, D(-20)))
th2, _ = text3d("t_cab", "internet cable", S + Vector((-8.6, -0.25, 0.42)), size=0.1, es=2.5, rot=(D(70), 0, D(-20)), col=CYAN)
for o_ in (th1, th2): pop_in(o_, C.EV["hose"] + 0.45); vis(o_, shots_of("s06"))
# repeater (s09)
rep_m = mat("rep_m", (0.55, 0.57, 0.6), 0.25, 1.0)
rep = prim("cyl", "repeater", loc=S + Vector((30.0, 0.0, 1.2)), rot=(0, D(90), 0), vertices=64, radius=1.1, depth=7.0); setmat(rep, rep_m)
for sgn in (-1, 1):
    cap = prim("cone", "rep_cap", loc=S + Vector((30.0 + sgn * 4.6, 0.0, 1.2)), rot=(0, D(90 * sgn), 0), vertices=64, radius1=1.1, radius2=0.12, depth=2.2); setmat(cap, rep_m)
for k in range(5):
    rg = prim("torus", "rep_ring%d" % k, loc=S + Vector((27.5 + k * 1.25, 0, 1.2)), rot=(0, D(90), 0), major_radius=1.12, minor_radius=0.05, major_segments=64, minor_segments=6); setmat(rg, steel_dk)
rep_glow_m, rep_glow_s = emat("rep_glow_m", CYAN, 0.0, soft=1.5)
repg = prim("sphere", "rep_glow", loc=S + Vector((30.0, 0, 1.2)), segments=32, ring_count=16, radius=1.6, scale=(2.6, 1, 1)); setmat(repg, rep_glow_m)
KV(rep_glow_s, 1, 0.0, "CONSTANT"); KV(rep_glow_s, F(C.EV["rep_boost"]), 0.0, "LINEAR"); KV(rep_glow_s, F(C.EV["rep_boost"] + 0.2), 3.0, "BEZIER"); KV(rep_glow_s, F(C.EV["rep_boost"] + 1.2), 0.6, "BEZIER")
vis(repg, shots_of("s09"))
trp, _ = text3d("t_rep", "repeater  ·  every 60-100 km", S + Vector((30.0, -0.4, 3.4)), size=0.55, es=3.0, rot=(D(80), 0, 0))
pop_in(trp, C.EV["rep_text"]); vis(trp, shots_of("s09"))
# shark (BlenderKit) for s12/s13
shark = load_asset("shark", 25.0, S + Vector((-50.0, 0, 0)), axis="max", ground=False)
if shark is not None:
    INFO["shark"] = INFO_ASSETS.get("shark")
    sh_piv = link(bpy.data.objects.new("shark_path", None)); shark.parent = sh_piv
    shark.location = shark.location - S - Vector((-50, 0, 0))
    # swims in from the left-back, dips to the cable, then turns away
    keys = [(41.3, (-82, 25, 9), 0), (42.6, (-58, 6, 4.5), -20), (43.0, (-51, 1.5, 2.2), -28), (44.0, (-50, 1.2, 2.6), -28), (44.95, (-50, 1.2, 2.6), -28), (46.4, (-44, 18, 8), 40)]
    for t, pos, yaw in keys:
        sh_piv.location = S + Vector(pos); K(sh_piv, "location", F(t), "BEZIER")
        sh_piv.rotation_euler = (0, 0, D(yaw)); K(sh_piv, "rotation_euler", F(t), "BEZIER")
    vis_tree(sh_piv, shots_of("s12", "s13"))
    try:
        arm = next(o for o in bpy.data.objects if o.type == "ARMATURE" and o.name not in ("",) and (o.parent is not None))
        swim = next((a for a in bpy.data.actions if a.name.startswith("Shark_Forward")), None)
        att = next((a for a in bpy.data.actions if a.name.startswith("Shark_Attack")), None)
        if arm.animation_data is None: arm.animation_data_create()
        arm.animation_data.action = None
        tr = arm.animation_data.nla_tracks.new(); tr.name = "swim"
        s1 = tr.strips.new("swim", F(41.3) - 10, swim); s1.repeat = 8.0
        if att:
            tr2 = arm.animation_data.nla_tracks.new(); tr2.name = "attack"
            s2 = tr2.strips.new("attack", F(42.7), att); s2.blend_in = 4; s2.blend_out = 6
        INFO["shark_anim"] = [arm.name, swim.name if swim else None, att.name if att else None]
    except Exception as e: NOTES.append("shark anim " + str(e)[:80])
tmy, _ = text3d("t_myth", "MYTH", S + Vector((-50.0, -6.0, 9.0)), size=4.0, es=8.0, col=(1.0, 0.18, 0.15), rot=(D(80), 0, D(-18)), extrude=0.15)
pop_in(tmy, C.EV["myth"], 0.18); vis(tmy, shots_of("s13"))
tmy2, _ = text3d("t_myth2", "0 shark-caused faults in 2007-2014", S + Vector((-50.0, -6.0, 6.2)), size=1.1, es=3.0, rot=(D(80), 0, D(-18)))
pop_in(tmy2, C.EV["myth"] + 0.45); vis(tmy2, shots_of("s13"))
# ship + anchor (s14/s15)
ship = None
hull_m = mat("hull_m", (0.03, 0.03, 0.035), 0.6, 0.3)
hull = prim("cube", "hull", loc=S + Vector((58.0, 40.0, 158.0)), scale=(90.0, 16.0, 9.0), smooth=False)
hb = hull.modifiers.new("bev", "BEVEL"); hb.width = 6.0; hb.segments = 6
setmat(hull, hull_m); vis(hull, shots_of("s14", "s15"))
if ship is not None:
    vis_tree(ship, shots_of("s14", "s15"))
anchor = load_asset("anchor2", 30.0, S + Vector((0, 0, 0)), axis="max", ground=True)
anc_piv = link(bpy.data.objects.new("anchor_path", None))
if anchor is not None:
    anchor.parent = anc_piv; anchor.location = anchor.location - S
else:
    a_ = prim("cyl", "anchor_shank", loc=(0, 0, 10), vertices=16, radius=0.8, depth=20); setmat(a_, steel); a_.parent = anc_piv
# anchor drags along +y across the cable and lifts it
akeys = [(46.4, (58, -60, 30)), (48.1, (58, -26, 1.0)), (49.0, (58, -2, 0.8)), (50.5, (59, 9, 4.0)), (52.85, (60, 18, 9.0))]
for t, pos in akeys:
    anc_piv.location = S + Vector(pos); K(anc_piv, "location", F(t), "BEZIER")
anc_piv.rotation_euler = (D(-18), 0, 0)
vis_tree(anc_piv, shots_of("s14", "s15"))
chain_m = mat("chain_m", (0.2, 0.17, 0.14), 0.6, 1.0)
chain = prim("cyl", "chain", loc=(0, 0, 0), vertices=12, radius=0.35, depth=1.0); setmat(chain, chain_m)
con = chain.constraints.new("STRETCH_TO") if False else None
# chain: from the anchor up toward the ship: parent a long thin cylinder to the anchor, pointing up/back
chain.parent = anc_piv; chain.location = (0, 30, 90); chain.rotation_euler = (D(-18), 0, 0); chain.scale = (1, 1, 190)
vis(chain, shots_of("s14", "s15"))
# the cable gets hooked and lifted: a third cable piece at x=58 that follows the anchor
hook_pts = []
for i in range(41):
    u = i / 40.0; x = 40 + 36 * u
    hook_pts.append((S.x + x, S.y, S.z + CR))
hk = curve_obj("cable_hook", hook_pts, CR * 1.01, cab_m)
hk_hook = hk.modifiers.new("hook", "HOOK") if False else None
# simple lift: a curve shape made with three versions keyed via object scale/location (bow upward)
lift = link(bpy.data.objects.new("lift", None)); lift.location = S + Vector((58, 0, 0))
cu_ = hk.data
sp_ = cu_.splines[0]
def bow(h):
    for i, p in enumerate(sp_.points):
        u = i / 40.0; w_ = math.exp(-((u - 0.5) / 0.16) ** 2)
        p.co = (S.x + 40 + 36 * u, S.y + w_ * h * 0.9, S.z + CR + w_ * h, 1)
        try: p.keyframe_insert("co", frame=FRAMEK)
        except Exception: pass
for t, h in ((48.9, 0.0), (49.6, 1.6), (50.5, 4.2), (52.85, 9.0)):
    FRAMEK = F(t); bow(h)
vis(hk, shots_of("s14", "s15"))
tth, _ = text3d("t_thirds", "⅔ of all breaks: anchors & fishing gear", S + Vector((57.0, -4.0, 8.5)), size=1.0, es=3.5, rot=(D(78), 0, D(-35)))
pop_in(tth, C.EV["thirds"]); vis(tth, shots_of("s15"))
# s04 hint: a pulse label
tlb, _ = text3d("t_floor", "sea floor  ·  up to 8 km deep", S + Vector((1.2, 1.0, 0.9)), size=0.22, es=2.2, rot=(D(75), 0, D(-15)))
pop_in(tlb, 5.6); vis(tlb, shots_of("s04"))
# hide seabed-only stuff outside seabed shots (performance)
SEA_R = set_ranges("S")
for o_ in [sea, fog, sun, amb, cabL, cabR, flash, hose, rep] + [o for o in bpy.data.objects if o.name.startswith(("rock", "rep_", "anchor", "chain"))]:
    if o_.type in ("MESH", "CURVE", "LIGHT") and o_.name not in ("rep_glow",): vis(o_, SEA_R)

# ---------------------------------------------------------------- SET E: Earth in space
ocean_m = mat("ocean_m", (0.005, 0.02, 0.06), 0.35, 0.0)
earth = prim("sphere", "earth", loc=E, segments=128, ring_count=64, radius=6.0); setmat(earth, ocean_m)
land_m = mat("land_m", (0.16, 0.2, 0.22), 0.7, 0.0)
SV(bsdf(land_m), "Emission Color", (0.25, 0.45, 0.55, 1)); SV(bsdf(land_m), "Emission Strength", 0.08)
def ll2v(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon + LON_OFF)
    return Vector((r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la)))
world = json.load(open(os.path.join(HERE, "world.json")))
bm = bmesh.new()
for poly in world:
    try:
        vs = [bm.verts.new((lo, la, 0)) for lo, la in poly]
        f_ = bm.faces.new(vs)
    except Exception: continue
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if e.calc_length() > 3.0], cuts=2, use_grid_fill=True)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
for v in bm.verts:
    lo, la = v.co.x, v.co.y
    v.co = ll2v(la, lo, 6.03)
land = new_mesh_obj("land", bm); land.location = E
sol = land.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.03; sol.offset = 1.0
setmat(land, land_m)
atm_m, _ = emat("atm_m", (0.3, 0.6, 1.0), 0.5, soft=5.0)
atm = prim("sphere", "atmo", loc=E, segments=96, ring_count=48, radius=6.25); setmat(atm, atm_m)
# stars
star_m, _ = emat("star_m", (1, 1, 1), 6.0, solid=True)
random.seed(5)
for i in range(260):
    d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized() * 160
    st_ = prim("ico", "star%d" % i, loc=E + d, subdivisions=1, radius=random.uniform(0.12, 0.35), smooth=False); setmat(st_, star_m)
esun = area("earth_sun", E + Vector((-40, -30, 18)), (0, 0, 0), 3.0e4, 20.0, (1.0, 0.96, 0.9)); aim(esun, E)
erim = area("earth_rim", E + Vector((30, 25, 8)), (0, 0, 0), 4.0e4, 20.0, (0.5, 0.7, 1.0)); aim(erim, E)
# cable routes (lat, lon waypoints)
ROUTES = [
    [(40.6, -73.9), (44, -45), (48, -20), (50.8, -4.5)],
    [(36.8, -76.0), (39, -45), (42, -15), (43.4, -2.9)],
    [(33.9, -118.4), (36, -140), (38, -165), (37, 170), (34.9, 139.9)],
    [(45.0, -124.0), (47, -150), (46, -175), (40, 160), (35.5, 140.5)],
    [(43.3, 5.4), (38, 12), (34, 25), (31.2, 29.9), (27.5, 34), (20, 39), (12.5, 44), (13, 55), (18.9, 72.8)],
    [(18.9, 72.8), (8, 77), (5, 90), (1.3, 103.8), (10, 110), (22.3, 114.2), (28, 125), (35, 140)],
    [(1.3, 103.8), (-10, 105), (-31.9, 115.8), (-38, 130), (-33.9, 151.2)],
    [(-33.9, 151.2), (-20, 175), (21.3, -158.0), (33.9, -118.4)],
    [(25.8, -80.2), (18, -65), (8, -48), (-3.7, -38.5)],
    [(-3.7, -38.5), (10, -30), (28, -20), (38.7, -9.1)],
    [(38.7, -9.1), (28, -16), (14, -19), (3, -8), (-8, 8), (-20, 10), (-33.9, 18.4)],
    [(-33.9, 18.4), (-34, 30), (-25, 42), (-5, 55), (10, 63), (18.9, 72.8)],
    [(50.8, -4.5), (55, -2), (58, 5), (59.3, 10.7)],
    [(25.8, -80.2), (30, -78), (36.8, -76.0)],
]
def slerp_pts(wps, r, n=24):
    pts = []
    for (la0, lo0), (la1, lo1) in zip(wps[:-1], wps[1:]):
        a = ll2v(la0, lo0, 1).normalized(); b = ll2v(la1, lo1, 1).normalized()
        om = math.acos(max(-1, min(1, a.dot(b))))
        for k in range(n):
            u = k / n
            if om < 1e-6: v = a
            else: v = (math.sin((1 - u) * om) * a + math.sin(u * om) * b) / math.sin(om)
            pts.append(E + v.normalized() * r)
    la, lo = wps[-1]; pts.append(E + ll2v(la, lo, 1).normalized() * r)
    return pts
route_m, route_s = emat("route_m", CYAN, 5.0, solid=True)
routes = []
for i, wps in enumerate(ROUTES):
    ro = curve_obj("route%d" % i, slerp_pts(wps, 6.045), 0.018, route_m)
    t0 = C.EV["routes0"] + 0.12 * i
    grow(ro, t0, t0 + 1.4); routes.append(ro)
tpc, _ = text3d("t_pct", "99%", E + Vector((0, -7.5, 4.6)), size=1.6, es=4.0, extrude=0.06)
tpc2, _ = text3d("t_pct2", "of data between continents", E + Vector((0, -7.5, 3.75)), size=0.42, es=2.5)
for o_ in (tpc, tpc2): pop_in(o_, C.EV["pct"]); vis(o_, shots_of("e05"))
for o_ in routes: vis(o_, shots_of("e05", "e10"))
# satellite (s03) + red X
SATP = Vector((6.5, -6.5, 3.0))
sat = load_asset("satellite", 1.4, E + SATP, axis="max", ground=False)
if sat is None:
    sb = prim("cube", "sat_body", loc=E + SATP, scale=(0.25, 0.25, 0.25)); setmat(sb, mat("gold", (0.9, 0.7, 0.3), 0.3, 1.0))
    for s_ in (-1, 1):
        pn = prim("cube", "sat_panel", loc=E + SATP + Vector((s_ * 0.8, 0, 0)), scale=(0.55, 0.02, 0.22)); setmat(pn, mat("panel", (0.05, 0.08, 0.2), 0.3, 0.5))
    sat = sb
vis_tree(sat, shots_of("e03"))
sx = stamp_x("x_sat", E + SATP + Vector((-0.35, -0.6, 0)), 0.9, (D(90), 0, D(-12)), C.EV["x_sat"], shots_of("e03"))
# wrap: a long spiral around the Earth (s10)
wpts = []
NW = 3600
for i in range(NW + 1):
    u = i / NW
    lat = -70 + 140 * u; lon = 360 * 37 * u
    wpts.append(E + ll2v(lat, lon, 6.16 + 0.04 * math.sin(u * 300)))
wrap_m, _ = emat("wrap_m", (1.0, 0.85, 0.45), 4.0, solid=True)
wrap = curve_obj("wrap", wpts, 0.02, wrap_m)
grow(wrap, C.EV["wrap0"], C.EV["wrap1"], "BEZIER")
vis(wrap, shots_of("e10"))
tkm, _ = text3d("t_km", "1.5 million km of cable", E + Vector((0, -9.0, -4.6)), size=0.62, es=3.5)
tx35, _ = text3d("t_x35", "= 35+ times around Earth", E + Vector((0, -9.0, -5.45)), size=0.45, es=3.0, col=(1.0, 0.85, 0.45))
pop_in(tkm, C.EV["km_text"]); pop_in(tx35, C.EV["x35"])
for o_ in (tkm, tx35): o_.rotation_euler = (D(80), 0, 0); vis(o_, shots_of("e10"))
E_R = set_ranges("E")
for o_ in [earth, land, atm, esun, erim] + [o for o in bpy.data.objects if o.name.startswith("star")]:
    vis(o_, E_R)

# ---------------------------------------------------------------- SET X: cable cross-section (studio, 1 unit = 1 cm)
stud_m = mat("studio_m", (0.02, 0.025, 0.03), 0.55, 0.0)
stud = prim("plane", "studio_floor", loc=X + Vector((0, 0, -1.25)), size=200); setmat(stud, stud_m)
xk = area("x_key", X + Vector((4, -6, 6)), (0, 0, 0), 900.0, 4.0, (1.0, 0.96, 0.92)); aim(xk, X + Vector((3, 0, 0)))
xr = area("x_rim", X + Vector((10, 5, 3)), (0, 0, 0), 700.0, 3.0, (0.45, 0.7, 1.0)); aim(xr, X + Vector((4, 0, 0)))
xf = area("x_fill", X + Vector((-6, -4, 1)), (0, 0, 0), 200.0, 4.0, (1.0, 0.75, 0.55)); aim(xf, X)
def tube(name, r_out, thick, x0, length, m):
    o = prim("cyl", name, loc=X + Vector((x0 + length / 2, 0, 0)), rot=(0, D(90), 0), vertices=96, radius=r_out, depth=length)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
    # remove caps -> open tube, then solidify inward
    me = o.data
    bm_ = bmesh.new(); bm_.from_mesh(me)
    caps = [f for f in bm_.faces if len(f.verts) > 4]
    bmesh.ops.delete(bm_, geom=caps, context="FACES"); bm_.to_mesh(me); bm_.free()
    s_ = o.modifiers.new("sol", "SOLIDIFY"); s_.thickness = thick; s_.offset = -1.0; s_.use_even_offset = True
    setmat(o, m); return o
pe_m = mat("pe_m", (0.02, 0.02, 0.022), 0.35, 0.0, coat=0.5)
cu_m = mat("copper_m", (0.95, 0.5, 0.3), 0.22, 1.0)
stl_m = mat("steelw_m", (0.62, 0.64, 0.68), 0.25, 1.0)
gel_m = mat("gel_m", (0.9, 0.85, 0.5), 0.1, 0.0, trans=0.9, ior=1.4)
LEN = 14.0
layers = {}
layers["pe"] = tube("x_pe", 1.0, 0.16, -8.0, LEN, pe_m)
layers["cu"] = tube("x_cu", 0.82, 0.07, -8.0, LEN, cu_m)
wires = []
for i in range(18):
    a = i / 18 * 2 * math.pi
    wv = prim("cyl", "x_wire%d" % i, loc=X + Vector((-8.0 + LEN / 2, 0.64 * math.cos(a), 0.64 * math.sin(a))), rot=(0, D(90), 0), vertices=24, radius=0.09, depth=LEN); setmat(wv, stl_m)
    wires.append(wv)
layers["tube"] = tube("x_tube", 0.5, 0.06, -8.0, LEN, stl_m)
fibers = []
FCOL = [(0.1, 0.3, 1.0), (1.0, 0.45, 0.05), (0.1, 0.8, 0.2), (0.55, 0.3, 0.1), (0.6, 0.6, 0.6), (1.0, 1.0, 1.0), (0.9, 0.05, 0.05), (0.02, 0.02, 0.02)]
for i in range(8):
    a = i / 8 * 2 * math.pi
    fm = mat("fiber_m%d" % i, FCOL[i], 0.25, 0.0, coat=0.5)
    SV(bsdf(fm), "Emission Color", (*CYAN, 1))
    fb = prim("cyl", "x_fiber%d" % i, loc=X + Vector((-8.0 + LEN / 2, 0.18 * math.cos(a), 0.18 * math.sin(a))), rot=(0, D(90), 0), vertices=16, radius=0.035, depth=LEN); setmat(fb, fm)
    fibers.append((fb, sock(bsdf(fm), "Emission Strength")))
# exploded view: outer layers step back so the inner ones stick out (x = cut end)
STEP = {"pe": 0.0, "cu": 1.6, "wires": 3.2, "tube": 4.8, "fibers": 6.6}
def slide(o, dx):
    base = o.location.copy()
    o.location = base; K(o, "location", F(C.EV["cut"]), "CONSTANT")
    o.location = base + Vector((dx, 0, 0)); K(o, "location", F(C.EV["cut"] + 0.7), "BEZIER")
slide(layers["cu"], STEP["cu"])
for wv in wires: slide(wv, STEP["wires"])
slide(layers["tube"], STEP["tube"])
for fb, _ in fibers: slide(fb, STEP["fibers"])
# highlight each layer when it is named (emission flash on its material)
def flash_mat(m, t, col, peak=1.2):
    b_ = bsdf(m); SV(b_, "Emission Color", (*col, 1)); s_ = sock(b_, "Emission Strength")
    KV(s_, 1, 0.0, "CONSTANT"); KV(s_, F(t), 0.0, "LINEAR"); KV(s_, F(t + 0.2), peak, "BEZIER"); KV(s_, F(t + 1.2), 0.0, "BEZIER")
flash_mat(stl_m, C.EV["steel"], (0.8, 0.9, 1.0), 0.8)
flash_mat(cu_m, C.EV["copper"], (1.0, 0.55, 0.3), 1.0)
for fb, s_ in fibers:
    KV(s_, 1, 0.0, "CONSTANT"); KV(s_, F(C.EV["fibers"]), 0.0, "LINEAR"); KV(s_, F(C.EV["fibers"] + 0.3), 6.0, "BEZIER")
hair_m = mat("hair_m", (0.14, 0.075, 0.04), 0.38, 0.0, coat=0.3)
hair = prim("cyl", "x_hair", loc=X + Vector((10.0, 0.0, -0.5)), rot=(D(90), 0, D(20)), vertices=24, radius=0.035, depth=6.0); setmat(hair, hair_m)
hair.location = X + Vector((10.0, 0.0, 2.5)); K(hair, "location", F(C.EV["hair"]) - 1, "CONSTANT")
hair.location = X + Vector((9.6, 0.0, -0.32)); K(hair, "location", F(C.EV["hair"] + 0.4), "BEZIER")
LBL = [("t_steel", "steel wires", C.EV["steel"], X + Vector((-8.0 + LEN + STEP["wires"] - 0.8, -0.9, 1.15))),
       ("t_copper", "copper  ·  carries power", C.EV["copper"], X + Vector((-8.0 + LEN + STEP["cu"] - 1.0, -1.0, 1.35))),
       ("t_glass", "glass fibers", C.EV["fibers"], X + Vector((-8.0 + LEN + STEP["fibers"] - 0.4, -0.3, 0.5))),
       ("t_hair", "human hair", C.EV["hair"] + 0.3, X + Vector((9.6, -0.3, 0.75)))]
for nm, body, t, loc in LBL:
    o_, _ = text3d(nm, body, loc, size=0.26 if nm in ("t_glass", "t_hair") else 0.38, es=3.0, rot=(D(80), 0, D(-35)))
    pop_in(o_, t)
X_R = set_ranges("X")
for o_ in [o for o in bpy.data.objects if not o.name.startswith("x_sat") and o.name.startswith(("x_", "studio", "t_steel", "t_copper", "t_glass", "t_hair"))]:
    if o_.type in ("MESH", "FONT", "LIGHT", "CURVE"): vis(o_, X_R)
for o_ in (xk, xr, xf): vis(o_, X_R)
vis(hair, shots_of("x07b"))

# ---------------------------------------------------------------- SET F: inside the glass fibre (pulses of light)
clad_m = mat("clad_m", (0.85, 0.95, 1.0), 0.03, 0.0, trans=1.0, ior=1.46)
clad = prim("cyl", "f_clad", loc=Fb + Vector((10, 0, 0)), rot=(0, D(90), 0), vertices=96, radius=1.0, depth=60.0); setmat(clad, clad_m)
core_m = mat("core_m", (0.75, 0.95, 1.0), 0.02, 0.0, trans=1.0, ior=1.47)
core = prim("cyl", "f_core", loc=Fb + Vector((10, 0, 0)), rot=(0, D(90), 0), vertices=64, radius=0.32, depth=60.0); setmat(core, core_m)
pul_m, pul_s = emat("pulse_m", CYAN, 1.8, soft=2.0)
pulses = []
random.seed(9)
for i in range(26):
    pl = prim("sphere", "f_pulse%d" % i, loc=Fb, segments=24, ring_count=12, radius=0.16, scale=(4.0, 1, 1)); setmat(pl, pul_m)
    x0 = -24 + i * 2.6
    pl.location = Fb + Vector((x0, 0, 0)); K(pl, "location", F(22.4), "LINEAR")
    pl.location = Fb + Vector((x0 + 3.45 * 9.0, 0, 0)); K(pl, "location", F(25.85), "LINEAR")
    pulses.append(pl)
fl1 = point("f_light", Fb + Vector((4, 0, 0)), 20.0, CYAN, 0.3)
fk = area("f_key", Fb + Vector((2, -5, 4)), (0, 0, 0), 300.0, 6.0, (0.7, 0.85, 1.0)); aim(fk, Fb)
tlt, _ = text3d("t_light", "your message = light", Fb + Vector((2.5, -1.3, 1.6)), size=0.32, es=3.0, rot=(D(80), 0, 0))
pop_in(tlt, 23.0)
F_R = set_ranges("F")
for o_ in [clad, core, fl1, fk, tlt] + pulses: vis(o_, F_R)
# keep the seabed fog out of other sets automatically (it is far away)

# ---------------------------------------------------------------- SET W: ocean surface dive (s02)
oc = prim("plane", "ocean", loc=Wv, size=10)
try:
    om = oc.modifiers.new("ocean", "OCEAN"); om.size = 1.0; om.spatial_size = 120; om.resolution = 12; om.wave_scale = 1.4; om.choppiness = 1.2
    om.time = 1.0
    om.keyframe_insert("time", frame=1); om.time = 1.0 + C.DUR; om.keyframe_insert("time", frame=C.NF)
except Exception as e: NOTES.append("ocean " + str(e)[:50])
water_m = mat("water_m", (0.05, 0.25, 0.35), 0.03, 0.0, trans=0.9, ior=1.33)
setmat(oc, water_m)
uw_m = bpy.data.materials.new("uw_m"); uw_m.use_nodes = True
ntu = uw_m.node_tree
for n in list(ntu.nodes): ntu.nodes.remove(n)
uo = ntu.nodes.new("ShaderNodeOutputMaterial"); uv_ = ntu.nodes.new("ShaderNodeVolumePrincipled")
SV(uv_, "Color", (0.06, 0.32, 0.5, 1)); SV(uv_, "Density", 0.04); SV(uv_, "Absorption Color", (0.12, 0.42, 0.55, 1))
ntu.links.new(uv_.outputs[0], uo.inputs["Volume"])
uw = prim("cube", "underwater", loc=Wv + Vector((0, 0, -26)), scale=(70, 70, 25), smooth=False); setmat(uw, uw_m)
sky_dome("sky_w", Wv, 140.0)
wsun = point("w_sun", Wv + Vector((-60, 80, 40)), 4.0e6, (1.0, 0.85, 0.65), 4.0)
# glowing data pulse diving with the camera
dp_m, dp_s = emat("dive_pulse_m", CYAN, 25.0, soft=1.0)
dpl = prim("sphere", "dive_pulse", loc=Wv, segments=24, ring_count=12, radius=0.6, scale=(1, 1, 3.5)); setmat(dpl, dp_m)
dpl.location = Wv + Vector((0, -12, 6)); K(dpl, "location", F(1.6), "LINEAR")
dpl.location = Wv + Vector((0, 6, -16)); K(dpl, "location", F(3.2), "LINEAR")
W_R = set_ranges("W")
for o_ in [oc, uw, wsun, dpl] + [o for o in bpy.data.objects if o.name.startswith("sky_w")]: vis(o_, W_R)

# ---------------------------------------------------------------- SET P: phone on a desk
desk_m = mat("desk_m", (0.09, 0.06, 0.045), 0.35, 0.0, coat=0.4)
desk = prim("plane", "desk", loc=P, size=40); setmat(desk, desk_m)
wd_ = ph_tex("wood_table_001", "diff")
if wd_:
    try:
        ntt = desk_m.node_tree; ti = ntt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(wd_)
        tcm = ntt.nodes.new("ShaderNodeTexCoord"); mpm = ntt.nodes.new("ShaderNodeMapping"); SV(mpm, "Scale", (0.35, 0.35, 0.35))
        ntt.links.new(tcm.outputs["Object"], mpm.inputs[0]); ntt.links.new(mpm.outputs[0], ti.inputs[0])
        ntt.links.new(ti.outputs["Color"], bsdf(desk_m).inputs["Base Color"])
    except Exception as e: NOTES.append("desk tex " + str(e)[:40])
phone = load_asset("phone", 1.47, P, axis="max", ground=True)
INFO["phone"] = INFO_ASSETS.get("phone")
PH_TOP = 0.08
pw, pl = 0.71, 1.47
if phone is not None:
    bpy.context.view_layer.update()
    objs = []
    st_ = [phone]
    while st_:
        o_ = st_.pop(); st_.extend(o_.children)
        if o_.type == "MESH": objs.append(o_)
    mn, mx = bbox_of(objs)
    INFO["phone_bbox"] = [list(mn), list(mx)]
    dims = mx - mn
    if dims.z > dims.y:   # standing upright -> lay it down, screen up (rotate -90 deg about X)
        piv = link(bpy.data.objects.new("phone_lay", None)); piv.location = P + Vector((0, 0, 0))
        phone.parent = piv; phone.location = phone.location - piv.location
        piv.rotation_euler = (D(-90), 0, 0)
        bpy.context.view_layer.update(); mn, mx = bbox_of(objs)
        piv.location = piv.location + Vector((0, -(mn.y + mx.y) / 2 + P.y, -mn.z + P.z))
        bpy.context.view_layer.update(); mn, mx = bbox_of(objs)
        INFO["phone_laid"] = [list(mn), list(mx)]
    PH_TOP = mx.z - P.z; pw, pl = mx.x - mn.x, mx.y - mn.y
else:
    body = prim("cube", "phone_body", loc=P + Vector((0, 0, 0.04)), scale=(0.355, 0.735, 0.04)); setmat(body, mat("pframe", (0.55, 0.53, 0.5), 0.22, 1.0))
# screen: image of the video (screen_a.jpg = ocean, screen_b.jpg = ship) + spinner
scr_m = bpy.data.materials.new("screen_m"); scr_m.use_nodes = True
nts = scr_m.node_tree; Ns = nts.nodes
for n in list(Ns): Ns.remove(n)
so = Ns.new("ShaderNodeOutputMaterial"); se_ = Ns.new("ShaderNodeEmission"); SV(se_, "Strength", 1.4)
mixc = Ns.new("ShaderNodeMix"); mixc.data_type = "RGBA"
def by_id(coll, ident): return next(x for x in coll if x.identifier == ident)
MFAC = by_id(mixc.inputs, "Factor_Float"); MFAC.default_value = 0.0
for slot, fn, fallback in (("A_Color", "screen_a.jpg", (0.05, 0.3, 0.45, 1)), ("B_Color", "screen_b.jpg", (0.1, 0.2, 0.3, 1))):
    p_ = os.path.join(HERE, fn)
    if os.path.exists(p_):
        ti = Ns.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(p_)
        tc = Ns.new("ShaderNodeTexCoord"); mp_ = Ns.new("ShaderNodeMapping"); SV(mp_, "Rotation", (0, 0, 0))
        nts.links.new(tc.outputs["UV"], mp_.inputs[0]); nts.links.new(mp_.outputs[0], ti.inputs[0])
        nts.links.new(ti.outputs["Color"], by_id(mixc.inputs, slot))
    else:
        by_id(mixc.inputs, slot).default_value = fallback
dim = Ns.new("ShaderNodeMix"); dim.data_type = "RGBA"; DFAC = by_id(dim.inputs, "Factor_Float"); DFAC.default_value = 0.0
by_id(dim.inputs, "B_Color").default_value = (0.02, 0.02, 0.03, 1)
nts.links.new(by_id(mixc.outputs, "Result_Color"), by_id(dim.inputs, "A_Color"))
nts.links.new(by_id(dim.outputs, "Result_Color"), se_.inputs["Color"]); nts.links.new(se_.outputs[0], so.inputs["Surface"])
SCR_S = sock(se_, "Strength")
screen = prim("plane", "screen", loc=P + Vector((0, 0, PH_TOP + 0.0015)), scale=(pw / 2 * 0.9, pl / 2 * 0.94, 1)); setmat(screen, scr_m)
# end: screen dims behind a spinner (slow internet), then shows the ship
KV(DFAC, 1, 0.0, "CONSTANT"); KV(DFAC, F(C.EV["spinner"]), 0.0, "LINEAR"); KV(DFAC, F(C.EV["spinner"] + 0.3), 0.75, "LINEAR")
KV(DFAC, F(C.EV["boat"]), 0.75, "LINEAR"); KV(DFAC, F(C.EV["boat"] + 0.3), 0.0, "LINEAR")
KV(MFAC, 1, 0.0, "CONSTANT"); KV(MFAC, F(C.EV["boat"]), 0.0, "CONSTANT"); KV(MFAC, F(C.EV["boat"]) + 1, 1.0, "CONSTANT")
spn_m, spn_s = emat("spinner_m", (1, 1, 1), 3.0, solid=True)
spc = bpy.data.curves.new("spinner", "CURVE"); spc.dimensions = "3D"; spc.bevel_depth = 0.012
spl = spc.splines.new("POLY"); spl.points.add(47)
for i in range(48):
    a = i / 48 * 2 * math.pi * 0.75; spl.points[i].co = (0.09 * math.cos(a), 0.09 * math.sin(a), 0, 1)
spn = link(bpy.data.objects.new("spinner", spc)); spn.location = P + Vector((0, 0, PH_TOP + 0.004)); spc.materials.append(spn_m)
spn.rotation_euler = (0, 0, 0); K(spn, "rotation_euler", F(C.EV["spinner"]), "LINEAR")
spn.rotation_euler = (0, 0, D(-360 * 3)); K(spn, "rotation_euler", F(C.EV["boat"]), "LINEAR")
vis(spn, [(C.EV["spinner"], C.EV["boat"])])
# dive into the screen (p01): screen brightens
KV(SCR_S, 1, 1.4, "CONSTANT"); KV(SCR_S, F(C.EV["screen_dive"]), 1.4, "LINEAR"); KV(SCR_S, F(1.6), 6.0, "BEZIER"); KV(SCR_S, F(1.6) + 1, 1.4, "CONSTANT")
pk = area("phone_key", P + Vector((-3.5, 0.5, 4.5)), (0, 0, 0), 140.0, 1.5, (1.0, 0.93, 0.85)); aim(pk, P)
pr = area("phone_rim", P + Vector((2.6, 2.4, 1.2)), (0, 0, 0), 160.0, 1.5, (0.55, 0.65, 1.0)); aim(pr, P)
P_R = set_ranges("P")
for o_ in [desk, screen, pk, pr]: vis(o_, P_R)
if phone is not None:
    st_ = [phone] + ([bpy.data.objects.get("phone_lay")] if bpy.data.objects.get("phone_lay") else [])
    for r_ in st_: vis_tree(r_, P_R)

# ======================================================================== cameras
cams = {}
for sid, t0, t1, st, keys, ex in C.SHOTS:
    org = Vector(C.SETS[st])
    cd = bpy.data.cameras.new("cam_" + sid); cd.sensor_width = 36.0; cd.clip_start = 0.02; cd.clip_end = 3000
    co = link(bpy.data.objects.new("cam_" + sid, cd))
    tg = link(bpy.data.objects.new("tgt_" + sid, None))
    con = co.constraints.new("TRACK_TO"); con.target = tg; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    for (t, pos, tgt, lens) in keys:
        f = F(t) if t < t1 else F(t1) + 1
        co.location = org + Vector(pos); K(co, "location", f, "LINEAR")
        tg.location = org + Vector(tgt); K(tg, "location", f, "LINEAR")
        cd.lens = lens; K(cd, "lens", f, "LINEAR")
    if ex.get("fstop"):
        cd.dof.use_dof = True; cd.dof.aperture_fstop = ex["fstop"]; cd.dof.focus_object = tg
    cams[sid] = co
sc.camera = cams["p01"]
setattr_safe(sc.eevee, "volumetric_end", 400.0)

def setup_glare():
    try:
        tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
        sc.compositing_node_group = tree
        rl = tree.nodes.new("CompositorNodeRLayers"); gl = tree.nodes.new("CompositorNodeGlare")
        try: gl.glare_type = "BLOOM"
        except Exception:
            s_ = sock(gl, "Type")
            if s_ is not None: s_.default_value = "Bloom"
        for nm, v in (("Threshold", 0.9), ("Strength", 0.5), ("Size", 0.7)):
            c_ = sock(gl, nm)
            if c_ is not None and getattr(c_, "type", "") == "VALUE": c_.default_value = v
        try: tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        except Exception: pass
        go = tree.nodes.new("NodeGroupOutput")
        tree.links.new(rl.outputs["Image"], gl.inputs["Image"]); tree.links.new(gl.outputs["Image"], go.inputs[0])
        sc.render.use_compositing = True
    except Exception as e: NOTES.append("glare " + str(e)[:60])
setup_glare()

PREFS.keyframe_new_interpolation_type = "BEZIER"
info = {"notes": NOTES, "assets": INFO_ASSETS, "info": INFO, "font": FONT.name if FONT else None, "build_s": round(time.time() - T0, 1)}
json.dump(info, open(os.path.join(HERE, "build_info.json"), "w"), indent=1, default=str)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "cable.blend"))
print("CABLE SAVED", json.dumps(info, default=str)[:3000])
