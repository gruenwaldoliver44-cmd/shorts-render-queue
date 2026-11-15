# Machine Times: "Your printer boils ink" (16:9, 25 fps, Blender 5.2 / Eevee). Build: Blender -b -P ink.py -- save
import bpy, bmesh, math, os, sys, json, uuid, random, time, urllib.request, urllib.parse
from mathutils import Vector, Matrix, Euler
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "save"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ink_common as C
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


# ======================================================================== ink body
_vis_orig = vis
VISED = set()
def vis(o, ranges, pad=1):
    if o is None or o.name in VISED: return
    VISED.add(o.name); _vis_orig(o, ranges, pad)
def shots_of(*ids): return [(s[1], s[2]) for s in C.SHOTS if s[0] in ids]
def set_ranges(st): return [(s[1], s[2]) for s in C.SHOTS if s[3] == st]
INFO = {}
WLS.default_value = 0.10
EV = C.EV

HUD = (0.45, 0.9, 1.0)
HEAT = (1.0, 0.30, 0.04)
INKC = (0.85, 0.02, 0.42)
STEAM = (0.85, 0.93, 1.0)
CMY = [(0.0, 0.62, 0.95), (0.92, 0.02, 0.55), (1.0, 0.85, 0.0)]

def snap(): return set(o.name for o in bpy.data.objects)
def set_vis(before, st, extra=None):
    rng = set_ranges(st) + (extra or [])
    for o in bpy.data.objects:
        if o.name in before: continue
        if o.type == "EMPTY" and o.instance_type != "COLLECTION": continue
        if o.type == "CAMERA": continue
        if o.name.startswith("WGT") or o.hide_render: o.hide_render = True; continue
        vis(o, rng)

def curve_obj(name, pts, bevel, col_mat, cyclic=False, res=4):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = bevel; cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)
    sp.use_cyclic_u = cyclic
    o = link(bpy.data.objects.new(name, cu)); cu.materials.append(col_mat)
    return o

def rim_mat(name, col, strength, power=2.5, base=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt_ = m.node_tree; N_ = nt_.nodes
    for n in list(N_): N_.remove(n)
    o_ = N_.new("ShaderNodeOutputMaterial"); em = N_.new("ShaderNodeEmission"); SV(em, "Color", (*col, 1))
    lw = N_.new("ShaderNodeLayerWeight"); SV(lw, "Blend", 0.5)
    pw = N_.new("ShaderNodeMath"); pw.operation = "POWER"; nt_.links.new(lw.outputs["Facing"], pw.inputs[0]); SV(pw, 1, power)
    mu = N_.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; nt_.links.new(pw.outputs[0], mu.inputs[0]); SV(mu, 1, strength)
    ad0 = N_.new("ShaderNodeMath"); ad0.operation = "ADD"; nt_.links.new(mu.outputs[0], ad0.inputs[0]); SV(ad0, 1, base)
    nt_.links.new(ad0.outputs[0], em.inputs["Strength"])
    tr = N_.new("ShaderNodeBsdfTransparent"); ad = N_.new("ShaderNodeAddShader")
    nt_.links.new(tr.outputs[0], ad.inputs[0]); nt_.links.new(em.outputs[0], ad.inputs[1]); nt_.links.new(ad.outputs[0], o_.inputs["Surface"])
    setattr_safe(m, "surface_render_method", "BLENDED")
    return m, mu.inputs[1]

# ---------------------------------------------------------------- node builder
class NB:
    def __init__(s, m):
        s.m = m; s.nt = m.node_tree; s.N = s.nt.nodes; s.L = s.nt.links
    def put(s, sock_, v):
        if isinstance(v, (int, float)): sock_.default_value = v
        elif isinstance(v, tuple): sock_.default_value = v
        else: s.L.new(v, sock_)
    def math(s, op, a, b=None, clamp=False):
        n = s.N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        s.put(n.inputs[0], a)
        if b is not None: s.put(n.inputs[1], b)
        return n.outputs[0]
    def mrange(s, v, a0, a1, b0, b1, smooth=True):
        n = s.N.new("ShaderNodeMapRange")
        if smooth: setattr_safe(n, "interpolation_type", "SMOOTHSTEP")
        n.clamp = True
        for i, x in enumerate((v, a0, a1, b0, b1)): s.put(n.inputs[i], x)
        return n.outputs[0]
    def sep(s, vec):
        n = s.N.new("ShaderNodeSeparateXYZ"); s.L.new(vec, n.inputs[0]); return n.outputs
    def comb(s, x, y, z):
        n = s.N.new("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)): s.put(n.inputs[i], v)
        return n.outputs[0]
    def obj(s):
        return s.N.new("ShaderNodeTexCoord").outputs["Object"]
    def attr(s, name):
        n = s.N.new("ShaderNodeAttribute"); n.attribute_name = name; return n.outputs["Fac"]
    def time(s):
        n = s.N.new("ShaderNodeValue"); o = n.outputs[0]
        o.default_value = 0.0; K(o, "default_value", 1, "LINEAR")
        o.default_value = C.NF / C.FPS; K(o, "default_value", C.NF + 1, "LINEAR")
        return o
    def ramp(s, v, cols, const=True):
        n = s.N.new("ShaderNodeValToRGB"); cr = n.color_ramp
        if const: cr.interpolation = "CONSTANT"
        k = len(cols)
        while len(cr.elements) < k: cr.elements.new(0.5)
        for i, c in enumerate(cols):
            cr.elements[i].position = i / k if const else i / max(1, k - 1)
            cr.elements[i].color = (*c, 1)
        s.L.new(v, n.inputs[0]); return n.outputs[0]
    def mixc(s, f, a, b, blend="MIX"):
        n = s.N.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = blend
        s.put(sock(n, "Factor_Float"), f); s.put(sock(n, "A_Color"), a); s.put(sock(n, "B_Color"), b)
        return next(o for o in n.outputs if o.identifier == "Result_Color")
    def out_add(s, col, strength):
        em = s.N.new("ShaderNodeEmission"); s.put(em.inputs["Color"], col); s.put(em.inputs["Strength"], strength)
        tr = s.N.new("ShaderNodeBsdfTransparent"); ad = s.N.new("ShaderNodeAddShader")
        s.L.new(tr.outputs[0], ad.inputs[0]); s.L.new(em.outputs[0], ad.inputs[1])
        out = s.N.new("ShaderNodeOutputMaterial"); s.L.new(ad.outputs[0], out.inputs["Surface"])
        setattr_safe(s.m, "surface_render_method", "BLENDED")
    def out_emit(s, col, strength):
        em = s.N.new("ShaderNodeEmission"); s.put(em.inputs["Color"], col); s.put(em.inputs["Strength"], strength)
        out = s.N.new("ShaderNodeOutputMaterial"); s.L.new(em.outputs[0], out.inputs["Surface"])

def newmat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    for n in list(m.node_tree.nodes): m.node_tree.nodes.remove(n)
    return m, NB(m)

def stream_mat(name, axis, length, seg, rate, strength, cols, seed=7.31):
    """moving bright segment along -axis (object space) per island; phase from 'rnd' attribute + time"""
    m, b = newmat(name)
    co = b.sep(b.obj()); pos = b.math("MULTIPLY", co[axis], -1.0)
    rnd = b.attr("rnd"); t = b.time()
    ph = b.math("FRACT", b.math("ADD", b.math("MULTIPLY", rnd, seed), b.math("MULTIPLY", t, rate)))
    d = b.math("ABSOLUTE", b.math("SUBTRACT", pos, b.math("MULTIPLY", ph, length)))
    mask = b.mrange(d, seg * 0.25, seg, 1.0, 0.0)
    col = b.ramp(b.math("FRACT", b.math("MULTIPLY", rnd, 3.71)), cols) if len(cols) > 1 else (*cols[0], 1)
    b.out_add(col, b.math("MULTIPLY", mask, strength))
    return m

def flash_mat(name, col, rate, strength, width=0.08, seed=7.31):
    m, b = newmat(name)
    rnd = b.attr("rnd"); t = b.time()
    ph = b.math("FRACT", b.math("ADD", b.math("MULTIPLY", rnd, seed), b.math("MULTIPLY", t, rate)))
    g = b.mrange(ph, 0.0, width, 1.0, 0.0)
    b.out_add((*col, 1), b.math("MULTIPLY", g, strength))
    return m

def set_rnd(me, vals):
    a = me.attributes.new("rnd", "FLOAT", "POINT")
    for i, v in enumerate(vals): a.data[i].value = v

def boxmesh(bm, x0, x1, y0, y1, z0, z1):
    vs = [bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    for f in idx: bm.faces.new([vs[i] for i in f])
    return vs

def box(name, x0, x1, y0, y1, z0, z1, m=None, org=(0, 0, 0), bevel=0.0):
    bm = bmesh.new(); boxmesh(bm, x0, x1, y0, y1, z0, z1)
    o = new_mesh_obj(name, bm); o.location = org
    if m: setmat(o, m)
    if bevel:
        md = o.modifiers.new("bv", "BEVEL"); md.width = bevel; md.segments = 3
    return o

def half_cyl(name, r, z0, z1, x=0.0, org=(0, 0, 0), m=None, seg=48, origin_top=False):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=(z1 - z0))
    zc = (z0 + z1) / 2 - (z1 if origin_top else 0.0)
    for v in bm.verts: v.co.x += x; v.co.z += zc
    g = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=g, plane_co=(0, 0, 0), plane_no=(0, -1, 0), clear_outer=True)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd: bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
    o = new_mesh_obj(name, bm); o.location = Vector(org) + Vector((0, 0, z1 if origin_top else 0.0))
    if m: setmat(o, m)
    return o

def ks(o, t, s, interp="BEZIER"):
    o.scale = s if hasattr(s, "__len__") else (s, s, s); K(o, "scale", F(t), interp)
def kl(o, t, loc, interp="BEZIER"):
    o.location = loc; K(o, "location", F(t), interp)
def kv(sock_, t, v, interp="BEZIER"): KV(sock_, F(t), v, interp)

def line(name, pts, m, bevel):
    return curve_obj(name, pts, bevel, m, res=2)

# ---------------------------------------------------------------- the "photo" (used by the printer swath and the halftone print)
PHOTO = os.path.join(HERE, "photo.png")
PIMG = bpy.data.images.load(PHOTO) if os.path.exists(PHOTO) else None
if PIMG is None: NOTES.append("no photo.png")

hud_m, _ = emat("hud_line", HUD, 6.0, solid=True)
hud_dim, _ = emat("hud_dim", HUD, 1.6, solid=True)

# ======================================================================== SET P: printhead printing
B = snap(); Po = Vector(C.P)
paper = box("p_paper", -70, 90, -45, 45, -0.2, 0.0, mat("paper", (0.82, 0.82, 0.8), 0.55), Po)
# printed swath: the photo, revealed behind the head (object-x < front)
sw_m, b = newmat("swath_m")
co = b.sep(b.obj())
front_n = b.N.new("ShaderNodeValue"); FRONT = front_n.outputs[0]
mask = b.mrange(b.math("SUBTRACT", FRONT, co[0]), -0.3, 0.6, 0.0, 1.0)
if PIMG:
    tx = b.N.new("ShaderNodeTexImage"); tx.image = PIMG
    uv = b.comb(b.math("ADD", b.math("DIVIDE", co[0], 90.0), 0.5), b.math("ADD", b.math("DIVIDE", co[1], 60.0), 0.5), 0.0)
    b.L.new(uv, tx.inputs["Vector"]); pc = tx.outputs["Color"]
else:
    pc = (0.6, 0.2, 0.5, 1)
bs = b.N.new("ShaderNodeBsdfPrincipled"); b.L.new(pc, bs.inputs["Base Color"]); SV(bs, "Roughness", 0.45)
tr = b.N.new("ShaderNodeBsdfTransparent"); mx_ = b.N.new("ShaderNodeMixShader")
b.L.new(mask, mx_.inputs[0]); b.L.new(tr.outputs[0], mx_.inputs[1]); b.L.new(bs.outputs[0], mx_.inputs[2])
out = b.N.new("ShaderNodeOutputMaterial"); b.L.new(mx_.outputs[0], out.inputs["Surface"])
setattr_safe(sw_m, "surface_render_method", "BLENDED")
swath = box("p_swath", -45, 45, -30, 30, 0.0, 0.03, sw_m, Po)
head = link(bpy.data.objects.new("p_head", None)); head.location = Po
plast = mat("plast_blk", (0.015, 0.016, 0.018), 0.28, 0.0, coat=0.6)
hb = box("p_carriage", -7, 7, -6, 6, 1.5, 13, plast, (0, 0, 0), bevel=0.8); hb.parent = head
for i, c_ in enumerate(CMY + [(0.05, 0.05, 0.05)]):
    cap = box("p_cap%d" % i, -6 + i * 3.1, -6 + i * 3.1 + 2.6, -5, 5, 13, 14.2, mat("cap%d" % i, c_, 0.3, coat=0.5), (0, 0, 0), bevel=0.3); cap.parent = hb
npl = box("p_noz", -5, 5, -1.2, 1.2, 1.35, 1.5, mat("gold", (0.9, 0.62, 0.28), 0.25, 1.0)); npl.parent = head
strip, _ = emat("p_strip_m", HUD, 5.0, solid=True)
led = box("p_led", -6.5, 6.5, -6.05, -5.95, 11.0, 11.25, strip); led.parent = head
rail = prim("cyl", "p_rail", loc=Po + Vector((10, 8.5, 9.5)), rot=(0, D(90), 0), vertices=32, radius=0.9, depth=180)
setmat(rail, mat("steel", (0.55, 0.56, 0.58), 0.22, 1.0))
# droplet rain under the head: thin vertical streaks, phase-shifted per streak
bm = bmesh.new(); vals = []
random.seed(11)
for i in range(140):
    x = random.uniform(-4.6, 4.6); y = random.uniform(-1.0, 1.0); r_ = random.random()
    vs = boxmesh(bm, x - 0.06, x + 0.06, y - 0.06, y + 0.06, -1.35, 0.0)
    vals += [r_] * len(vs)
dr = new_mesh_obj("p_drops", bm); set_rnd(dr.data, vals)
setmat(dr, stream_mat("p_drops_m", 2, 1.35, 0.35, 4.0, 30.0, CMY))
dr.parent = head; dr.location = (0, 0, 1.35)
# head motion + printed area follows
HX = [(0.0, -9.0), (2.45, 9.0)]
for (t, x) in HX:
    kl(head, t, Po + Vector((x, 0, 0)), "LINEAR")
    FRONT.default_value = x - 5.5; K(FRONT, "default_value", F(t), "LINEAR")
a_ = area("p_key", Po + Vector((-14, -26, 34)), (0, 0, 0), 22000, size=30); aim(a_, Po)
a_ = area("p_rim", Po + Vector((8, 30, 14)), (0, 0, 0), 20000, size=20, col=(0.5, 0.85, 1.0)); aim(a_, Po + Vector((0, 0, 6)))
a_ = area("p_fill", Po + Vector((30, -20, 6)), (0, 0, 0), 8000, size=20, col=(1.0, 0.6, 0.85)); aim(a_, Po + Vector((0, 0, 4)))
set_vis(B, "P")

# ======================================================================== SET N: the firing chamber, cut open
B = snap(); No = Vector(C.N)
def NV(x, y, z): return No + Vector((x, y, z))
si_m = mat("silicon", (0.045, 0.05, 0.065), 0.22, 0.7, coat=0.3)
pl_m = mat("gold_plate", (0.85, 0.58, 0.26), 0.28, 1.0)
wa_m = mat("barrier", (0.09, 0.08, 0.11), 0.35, 0.0, coat=0.4)
ink_m = mat("ink_sec", (0.22, 0.0, 0.09), 0.18, 0.0, emit=INKC, es=0.1, coat=0.6)
ink3_m = mat("ink_3d", (0.5, 0.0, 0.22), 0.04, 0.0, emit=INKC, es=0.35, coat=1.0)
box("n_sub", -7.5, 7.5, 0, 4, 5.0, 7.2, si_m, No)
heater = box("n_heater", -1.5, 1.5, 0, 3, 4.85, 5.0, mat("heater", (0.35, 0.33, 0.32), 0.3, 1.0), No)
HB = bsdf(heater.data.materials[0]); HES = sock(HB, "Emission Strength"); HEC = sock(HB, "Emission Color")
SV(HB, "Emission Color", (*HEAT, 1)); SV(HB, "Emission Strength", 0.0)
box("n_wall", 2.0, 7.5, 0, 4, 2.5, 5.0, wa_m, No)
plate = box("n_plate", -7.5, 7.5, 0, 4, 1.5, 2.5, pl_m, No)
cut = prim("cyl", "n_holecut", loc=NV(0, 0, 2.0), vertices=64, radius=0.8, depth=3.0)
md = plate.modifiers.new("hole", "BOOLEAN"); md.object = cut; md.operation = "DIFFERENCE"
cut.hide_render = True; cut.hide_viewport = True
box("n_ink", -7.5, 2.0, 0, 4, 2.5, 4.85, ink_m, No)
plug = half_cyl("n_plug", 0.8, 1.5, 2.5, 0.0, No, ink_m, origin_top=True)
# backdrop measurement grid (shows above / below the chip)
gm, b = newmat("grid_m")
co = b.sep(b.obj())
gx = b.mrange(b.math("ABSOLUTE", b.math("SUBTRACT", b.math("FRACT", co[0]), 0.5)), 0.46, 0.49, 0.0, 1.0)
gz = b.mrange(b.math("ABSOLUTE", b.math("SUBTRACT", b.math("FRACT", co[1]), 0.5)), 0.46, 0.49, 0.0, 1.0)
b.out_add((*HUD, 1), b.math("MULTIPLY", b.math("MAXIMUM", gx, gz), 0.35))
grid = prim("plane", "n_grid", loc=NV(0, 4.6, 0), rot=(D(90), 0, 0), size=60); setmat(grid, gm)
# section outlines (x-ray drawing)
ol = [[(-7.5, 5.0), (7.5, 5.0)], [(-7.5, 7.2), (7.5, 7.2)], [(-7.5, 2.5), (-0.8, 2.5)], [(0.8, 2.5), (7.5, 2.5)],
      [(-7.5, 1.5), (-0.8, 1.5)], [(0.8, 1.5), (7.5, 1.5)], [(-0.8, 1.5), (-0.8, 2.5)], [(0.8, 1.5), (0.8, 2.5)],
      [(2.0, 2.5), (2.0, 5.0)]]
for i, seg_ in enumerate(ol):
    line("n_ol%d" % i, [NV(p[0], -0.03, p[1]) for p in seg_], hud_dim, 0.022)
hol_m, HOL = emat("heater_ol_m", HUD, 0.0, solid=True)
hol = line("n_heater_ol", [NV(-1.5, -0.05, 4.85), NV(1.5, -0.05, 4.85), NV(1.5, -0.05, 5.0), NV(-1.5, -0.05, 5.0), NV(-1.5, -0.05, 4.85)], hol_m, 0.04)
# hot film, micro bubbles, steam bubble, jet, drop, satellite
film_m, FILM = emat("film_m", (1.0, 0.45, 0.08), 0.0)
film = box("n_film", -1.5, 1.5, -0.25, 3, 4.6, 4.85, film_m, No)
steam_m, _ = rim_mat("steam_m", STEAM, 3.2, 2.2, base=0.18)
micro = []
random.seed(5)
for i in range(26):
    o = prim("sphere", "n_mb%d" % i, loc=NV(random.uniform(-1.35, 1.35), random.uniform(-0.05, 0.4), 4.78), segments=16, ring_count=8, radius=random.uniform(0.07, 0.17))
    setmat(o, steam_m); o.scale = (0.001,) * 3; micro.append(o)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_outer=True)
bub = new_mesh_obj("n_bubble", bm); bub.location = NV(0, 0, 4.86); setmat(bub, steam_m)
for p_ in bub.data.polygons: p_.use_smooth = True
jet = prim("cyl", "n_jet", loc=(0, 0, 0), vertices=32, radius=0.42, depth=1.0)
for v in jet.data.vertices: v.co.z -= 0.5
jet.location = NV(0, 0, 1.55); setmat(jet, ink3_m)
drop = prim("sphere", "n_drop", loc=NV(0, 0, 1.2), segments=40, ring_count=20, radius=0.62); setmat(drop, ink3_m)
sat = prim("sphere", "n_sat", loc=NV(0, 0, 1.2), segments=20, ring_count=10, radius=0.22); setmat(sat, ink3_m)
ring_m, RING = emat("ring_m", STEAM, 0.0)
ring = prim("torus", "n_ring", loc=NV(0, -0.1, 3.9), rot=(D(90), 0, 0), major_radius=1.0, minor_radius=0.05, major_segments=64, minor_segments=8); setmat(ring, ring_m)
arr_m, ARR = emat("arrow_m", (1.0, 0.6, 0.85), 0.0, solid=False)
bm = bmesh.new()
for k in range(-4, 4):
    x = k * 2.0
    for sgn in (1, -1):
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((x, -0.08, 3.65 + sgn * 0.18)) @ Matrix.Rotation(D(35 * sgn), 4, "Y") @ Matrix.Diagonal((0.55, 0.05, 0.09, 1)))
arrows = new_mesh_obj("n_arrows", bm); setmat(arrows, arr_m); arrows.location = NV(-3.0, 0, 0)
# labels (lie in the section plane)
LBL = []
for (txt, tp, a, b_) in (("HEATER", (4.3, 6.15), (1.5, 4.92), (3.0, 5.95)), ("NOZZLE", (3.9, 0.95), (0.8, 1.9), (2.6, 1.05)),
                         ("INK", (-5.4, 3.65), None, None), ("SILICON", (-5.0, 6.15), None, None)):
    o, _ = text3d("n_lbl_" + txt, txt, NV(tp[0], -0.08, tp[1]), size=0.36, col=HUD, es=6.0)
    LBL.append(o)
    if a:
        LBL.append(line("n_lead_" + txt, [NV(a[0], -0.07, a[1]), NV(b_[0], -0.07, b_[1])], hud_m, 0.018))
for o in LBL:
    vis(o, [(25.3, 33.3)])
    pop_in(o, EV["heater_ol"] + (0.0 if "HEATER" in o.name else 0.2), 0.25)

REST = {"bub": (0.001,) * 3, "jet": (1.0, 1.0, 0.001), "drop": 0.001, "sat": 0.001}
def init_keys():
    kv(HES, 0, 0.0, "BEZIER"); kv(FILM, 0, 0.0); ks(bub, 0, REST["bub"]); ks(jet, 0, REST["jet"])
    ks(drop, 0, REST["drop"], "CONSTANT"); kl(drop, 0, NV(0, 0, 1.2), "CONSTANT")
    ks(sat, 0, REST["sat"], "CONSTANT"); kl(sat, 0, NV(0, 0, 1.2), "CONSTANT")
    ks(plug, 0, 1.0); kv(RING, 0, 0.0); kv(ARR, 0, 0.0); kv(HOL, 0, 0.0)
    for o in micro: ks(o, 0, 0.001)
init_keys()

def cycle(h0, h1, n, bf, j0, dt, aw, c0, c1, r0, r1, peak=9.0):
    # heater
    kv(HES, h0, 0.0); kv(HEC, h0, (*HEAT, 1))
    kv(HES, h1, peak); kv(HEC, h1, (1.0, 0.75, 0.35, 1))
    kv(HES, n, peak * 1.05); kv(HEC, n, (1.0, 0.8, 0.45, 1))
    kv(HES, bf, peak * 0.25); kv(HES, c1, 0.0); kv(HEC, c1, (*HEAT, 1))
    # superheated film
    kv(FILM, h0, 0.0); kv(FILM, h1, 3.0); kv(FILM, n, 5.0); kv(FILM, n + 0.12, 0.0)
    # micro bubbles
    for i, o in enumerate(micro):
        tt = n - 0.1 + (i % 7) * 0.015
        ks(o, tt - 0.01, 0.001); ks(o, tt + 0.06, 1.0); ks(o, n + 0.18, 0.001)
    # steam bubble
    ks(bub, n - 0.01, REST["bub"]); ks(bub, n + 0.02, (1.35, 1.2, 0.08)); ks(bub, bf, (1.95, 1.35, 1.92))
    ks(bub, c0, (1.95, 1.35, 1.92)); ks(bub, c1, REST["bub"], "CONSTANT")
    # jet + drop
    ks(jet, j0, REST["jet"]); ks(jet, dt, (1.0, 1.0, 2.4), "LINEAR"); ks(jet, dt + 0.28, REST["jet"])
    ks(drop, j0 - 0.02, REST["drop"], "BEZIER"); kl(drop, j0 - 0.02, NV(0, 0, 1.3), "BEZIER")
    ks(drop, j0 + 0.2, 0.55); ks(drop, dt, 1.0, "LINEAR")
    kl(drop, dt, NV(0, 0, 1.55 - 2.4 - 0.4), "LINEAR")
    ks(drop, aw, (0.92, 0.92, 1.12), "CONSTANT"); kl(drop, aw, NV(0, 0, -16.0), "CONSTANT")
    ks(drop, aw + 0.04, REST["drop"], "CONSTANT"); kl(drop, aw + 0.04, NV(0, 0, 1.2), "CONSTANT")
    ks(sat, dt - 0.01, REST["sat"], "CONSTANT"); kl(sat, dt - 0.01, NV(0, 0, -0.5), "LINEAR")
    ks(sat, dt + 0.02, 1.0, "LINEAR"); kl(sat, dt + 0.02, NV(0, 0, -0.55), "LINEAR")
    kl(sat, aw + 0.3, NV(0, 0, -14.0), "CONSTANT"); ks(sat, aw + 0.3, 1.0, "CONSTANT")
    ks(sat, aw + 0.34, REST["sat"], "CONSTANT"); kl(sat, aw + 0.34, NV(0, 0, 1.2), "CONSTANT")
    # collapse flash
    ks(ring, c1 - 0.12, 0.4); kv(RING, c1 - 0.12, 0.0); kv(RING, c1 - 0.02, 5.0); ks(ring, c1 + 0.4, 2.3); kv(RING, c1 + 0.4, 0.0)
    # meniscus retracts, refill
    ks(plug, c0 + 0.05, 1.0); ks(plug, c1 + 0.1, (1.0, 1.0, 0.22)); ks(plug, r0, (1.0, 1.0, 0.22)); ks(plug, r1, 1.0)
    kv(ARR, r0 - 0.1, 0.0); kv(ARR, r0 + 0.15, 3.0); kv(ARR, r1 - 0.15, 3.0); kv(ARR, r1, 0.0)
    kl(arrows, r0 - 0.1, NV(-3.0, 0, 0), "LINEAR"); kl(arrows, r1, NV(-3.0 + 2.0 * max(1, round((r1 - r0) / 0.45)), 0, 0), "LINEAR")

cycle(2.42, 2.55, 2.60, 3.00, 2.95, 3.40, 3.80, 3.95, 4.15, 4.25, 4.7, peak=10.0)
kv(HOL, EV["heater_ol"] - 0.05, 0.0); kv(HOL, EV["heater_ol"] + 0.1, 9.0); kv(HOL, EV["heater_ol"] + 0.6, 3.0); kv(HOL, 33.0, 3.0); kv(HOL, 33.3, 0.0)
cycle(EV["heat0"], EV["heat_max"], EV["nucleate"], EV["bubble_full"], EV["jet0"], EV["detach"], EV["away"],
      EV["collapse"], EV["collapse1"], EV["refill0"], EV["refill1"], peak=8.0)
cycle(42.86, 42.98, 43.02, 43.50, 43.55, 44.00, 44.35, 44.45, 44.70, 44.75, 45.35, peak=10.0)
d_ = 15.0
a_ = area("n_key", NV(-6, -12, 10), (0, 0, 0), 30 * d_ * d_, size=8); aim(a_, NV(0, 0, 3.5))
a_ = area("n_fill", NV(8, -10, -2), (0, 0, 0), 12 * d_ * d_, size=8, col=(1.0, 0.55, 0.85)); aim(a_, NV(0, 0, 2.0))
a_ = area("n_under", NV(0, -6, -10), (0, 0, 0), 20 * d_ * d_, size=6, col=(0.55, 0.85, 1.0)); aim(a_, NV(0, 0, 0.0))
heat_l = point("n_heatlight", NV(0, -1.2, 4.2), 0.0, col=(1.0, 0.5, 0.15), radius=0.5)
for (t, e) in ((0, 0), (2.42, 0), (2.55, 900), (3.0, 200), (4.1, 0), (27.3, 0), (31.0, 700), (33.6, 800), (35.2, 200), (40.3, 0), (42.86, 0), (42.98, 900), (43.5, 200), (44.7, 0)):
    heat_l.data.energy = e; K(heat_l.data, "energy", F(t), "BEZIER")
set_vis(B, "N")

# ======================================================================== SET Z: cartridge underside -> nozzle plate -> hair
B = snap(); Zo = Vector(C.Z)
box("z_body", -16, 16, 0, 30, -22, 12, plast, Zo, bevel=1.2)
flex = box("z_flex", -11, 11, -0.08, 0.0, -17, 2.2, mat("flex", (0.55, 0.32, 0.12), 0.3, 0.6, coat=0.8), Zo)
bm = bmesh.new()
for i in range(6):
    for j in range(4):
        x = -8 + i * 3.2; z = -14 + j * 3.6
        boxmesh(bm, x - 1.0, x + 1.0, -0.14, -0.08, z - 1.1, z + 1.1)
pads = new_mesh_obj("z_pads", bm); pads.location = Zo; setmat(pads, mat("gold", (0.9, 0.62, 0.28), 0.25, 1.0))
zpl = box("z_plate", -6.5, 6.5, -0.07, 0.0, 4.0, 6.0, mat("noz_plate", (0.8, 0.8, 0.82), 0.18, 1.0), Zo)
bm = bmesh.new()
for row, zz in enumerate((4.75, 5.25)):
    for i in range(140):
        x = -5.9 + i * 0.085 + row * 0.0425
        bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=0.011, matrix=Matrix.Translation((x, -0.072, zz)) @ Matrix.Rotation(D(90), 4, "X"))
holes = new_mesh_obj("z_holes", bm); holes.location = Zo
setmat(holes, mat("hole_m", (0.02, 0.0, 0.01), 0.1, 0.0, emit=INKC, es=0.8))
hair = prim("cyl", "z_hair", loc=Zo + Vector((-3.0, -0.14, 4.83)), rot=(0, D(90), D(4)), vertices=32, radius=0.035, depth=3.0)
setmat(hair, mat("hair", (0.16, 0.09, 0.05), 0.35, 0.0, coat=0.5))
kl(hair, EV["hair0"], Zo + Vector((-3.0, -0.14, 4.83))); kl(hair, EV["hair1"], Zo + Vector((-0.25, -0.14, 4.83))); kl(hair, 25.3, Zo + Vector((-0.12, -0.14, 4.83)))
a_ = area("z_key", Zo + Vector((-30, -55, 40)), (0, 0, 0), 120000, size=40); aim(a_, Zo)
a_ = area("z_rim", Zo + Vector((25, -20, 30)), (0, 0, 0), 50000, size=20, col=(0.5, 0.85, 1.0)); aim(a_, Zo + Vector((0, 0, 3)))
a_ = area("z_near", Zo + Vector((-1.5, -3.0, 7.0)), (0, 0, 0), 40, size=2.0); aim(a_, Zo + Vector((0, 0, 5)))
a_ = area("z_near2", Zo + Vector((2.0, -2.5, 3.0)), (0, 0, 0), 15, size=1.5, col=(1.0, 0.6, 0.85)); aim(a_, Zo + Vector((0, 0, 5)))
set_vis(B, "Z")

# ======================================================================== SET L: 1977 lab bench (cm)
B = snap(); Lo = Vector(C.L)
def LV(x, y, z): return Lo + Vector((x, y, z))
box("l_bench", -70, 70, -35, 35, -5, 0, mat("bench", (0.06, 0.035, 0.02), 0.45, 0.0, coat=0.3), Lo)
box("l_wall", -120, 120, 45, 50, -5, 120, mat("wall", (0.03, 0.035, 0.04), 0.8), Lo)
box("l_floor", -200, 200, -200, 200, -80, -79, mat("floor", (0.02, 0.02, 0.02), 0.6), Lo)
TIP = LV(12.0, 0.0, 10.5)
syr = load_asset("syringe", 20.0, LV(0, 0, 10.5), rot=(0, 0, D(-90)), ground=False)
if syr:
    bpy.context.view_layer.update()
    kids = []
    st_ = [syr]
    while st_:
        o = st_.pop(); st_.extend(o.children); kids.append(o)
    for o in kids:
        if o.name.startswith("needle_cover"): o.hide_render = True
    ndl = next((o for o in kids if o.name.startswith("needle") and not o.name.startswith("needle_cover")), None)
    mn, mx = bbox_of([o for o in kids if o.type == "MESH" and not o.hide_render])
    ctr = (mn + mx) / 2
    if ndl:
        nmn, nmx = bbox_of([ndl])
        if (nmn.x + nmx.x) / 2 < ctr.x:
            syr.rotation_euler.z += D(180); bpy.context.view_layer.update()
            mn, mx = bbox_of([o for o in kids if o.type == "MESH" and not o.hide_render])
        nmn, nmx = bbox_of([ndl])
        tip_now = Vector((nmx.x, (nmn.y + nmx.y) / 2, (nmn.z + nmx.z) / 2))
    else:
        tip_now = Vector((mx.x, (mn.y + mx.y) / 2, (mn.z + mx.z) / 2))
    syr.location += TIP - tip_now
    bpy.context.view_layer.update()
    body = next((o for o in kids if o.name.startswith("Body")), None)
    if body:
        bmn, bmx = bbox_of([body])
        rr = min(bmx.y - bmn.y, bmx.z - bmn.z) * 0.36
        ln = (bmx.x - bmn.x) * 0.62
        ink = prim("cyl", "l_syr_ink", loc=Vector((bmx.x - ln / 2 - (bmx.x - bmn.x) * 0.08, (bmn.y + bmx.y) / 2, (bmn.z + bmx.z) / 2)), rot=(0, D(90), 0), vertices=32, radius=rr, depth=ln)
        setmat(ink, mat("ink_dark", (0.12, 0.0, 0.06), 0.15, 0.0, emit=INKC, es=0.25))
    INFO["syringe_tip"] = [round(x, 2) for x in (TIP - Lo)]
else:
    b_ = prim("cyl", "l_syr_body", loc=LV(-1, 0, 10.5), rot=(0, D(90), 0), vertices=32, radius=0.9, depth=12); setmat(b_, mat("syr_glass", (0.8, 0.85, 0.9), 0.05, alpha=0.4))
    n_ = prim("cyl", "l_needle", loc=LV(8.5, 0, 10.5), rot=(0, D(90), 0), vertices=16, radius=0.05, depth=7); setmat(n_, mat("steel", (0.55, 0.56, 0.58), 0.22, 1.0))
# clamp stand holding the syringe
st_m = mat("stand", (0.15, 0.16, 0.17), 0.35, 1.0)
s1 = prim("cyl", "l_rod", loc=LV(-4, 9, 12), vertices=24, radius=0.6, depth=24); setmat(s1, st_m)
s2 = box("l_base", -12, 4, 2, 16, 0, 1.2, st_m, Lo, bevel=0.3)
s3 = prim("cyl", "l_arm", loc=LV(-4, 4.5, 10.5), rot=(D(90), 0, 0), vertices=16, radius=0.35, depth=9); setmat(s3, st_m)
s4 = prim("torus", "l_clamp", loc=LV(-4, 0, 10.5), rot=(0, D(90), 0), major_radius=1.25, minor_radius=0.3); setmat(s4, st_m)
# soldering iron: local +X runs from the tip up to the handle
iron = link(bpy.data.objects.new("l_iron", None))
IR_DIR = Vector((0.55, -0.25, 0.8)).normalized()
iron.rotation_euler = IR_DIR.to_track_quat("X", "Z").to_euler()
tipglow_m, TIPG = emat("tipglow_m", (1.0, 0.35, 0.06), 2.0, solid=True)
parts = [("l_ir_tip", "cone", 0.0, 1.4, dict(radius1=0.06, radius2=0.28), tipglow_m),
         ("l_ir_shaft", "cyl", 1.4, 9.0, dict(radius=0.28), mat("chrome", (0.75, 0.75, 0.78), 0.12, 1.0)),
         ("l_ir_collar", "cyl", 9.0, 10.2, dict(radius=0.55), mat("brass", (0.8, 0.55, 0.25), 0.3, 1.0)),
         ("l_ir_grip", "cyl", 10.2, 22.0, dict(radius=0.95), mat("bakelite", (0.09, 0.03, 0.015), 0.35, 0.0, coat=0.6))]
for (nm, kind, a0, a1, kw, m_) in parts:
    if kind == "cone":
        o = prim("cone", nm, loc=(0, 0, 0), vertices=32, depth=a1 - a0, **kw)
    else:
        o = prim("cyl", nm, loc=(0, 0, 0), vertices=32, depth=a1 - a0, **kw)
    o.rotation_euler = (0, D(90), 0); o.location = ((a0 + a1) / 2, 0, 0); setmat(o, m_); o.parent = iron
cab = curve_obj("l_ir_cable", [(22, 0, 0), (27, 0, -2), (31, 3, -12), (34, 10, -30)], 0.35, mat("cable", (0.02, 0.02, 0.02), 0.5), res=3)
cab.parent = iron
CONTACT = TIP + Vector((-1.0, 0.0, 0.07))
def iron_at(t, back, interp="BEZIER"):
    kl(iron, t, CONTACT + IR_DIR * back, interp)
iron_at(0, 16.0); iron_at(EV["approach0"], 16.0); iron_at(11.8, 3.0); iron_at(EV["touch"], 0.0, "CONSTANT")
iron_at(14.7, 0.0); iron_at(16.9, 2.5); iron_at(61.3, 9.0); iron_at(EV["end_touch"], 0.0); iron_at(66.5, 0.0)
kv(TIPG, 0, 2.0); kv(TIPG, 61.3, 2.0); kv(TIPG, 64.5, 6.0); kv(TIPG, 66.5, 6.0)
# contact flash + steam puff
fl_m, FL = emat("touch_flash_m", (1.0, 0.75, 0.45), 0.0, soft=1.5)
flash = prim("sphere", "l_flash", loc=CONTACT, segments=24, ring_count=12, radius=0.6); setmat(flash, fl_m)
for (t, v) in ((0, 0), (EV["touch"] - 0.02, 0), (EV["touch"] + 0.06, 8), (EV["touch"] + 0.6, 0), (EV["end_touch"] - 0.02, 0), (EV["end_touch"] + 0.06, 10), (66.5, 4)):
    kv(FL, t, v)
pf_m, _ = rim_mat("puff_m", (0.9, 0.9, 0.95), 0.9, 2.0, base=0.05)
random.seed(3)
for i in range(7):
    o = prim("sphere", "l_puff%d" % i, loc=CONTACT, segments=16, ring_count=8, radius=0.35); setmat(o, pf_m)
    t0 = EV["touch"] + 0.1 + i * 0.12
    ks(o, 0, 0.001); ks(o, t0, 0.001); kl(o, t0, CONTACT)
    ks(o, t0 + 1.6, 1.0 + random.random()); kl(o, t0 + 1.6, CONTACT + Vector((random.uniform(-1, 1), random.uniform(-0.5, 0.5), 2.5 + random.random() * 2)))
    ks(o, t0 + 2.2, 0.001)
# bead swelling at the needle tip, then the spurt (slow motion)
bead = prim("sphere", "l_bead", loc=TIP + Vector((0.05, 0, 0)), segments=24, ring_count=12, radius=0.14); setmat(bead, ink3_m)
ks(bead, 0, 0.001); ks(bead, 13.4, 0.001); ks(bead, EV["spurt"] - 0.05, 1.0); ks(bead, EV["spurt"] + 0.15, 0.001)
VEL = Vector((2.8, 0.0, 0.55)); GRAV = 0.9
random.seed(9)
for k in range(44):
    tk = EV["spurt"] + k * 0.045
    r_ = 0.035 + 0.05 * random.random() * (1.0 if k % 3 else 1.5)
    o = prim("sphere", "l_spurt%d" % k, loc=TIP, segments=16, ring_count=8, radius=r_); setmat(o, ink3_m)
    jit = Vector((0, random.uniform(-0.15, 0.15), random.uniform(-0.12, 0.12)))
    ks(o, 0, 0.001, "CONSTANT"); kl(o, 0, TIP, "CONSTANT")
    ks(o, tk - 0.02, 0.001, "CONSTANT"); kl(o, tk - 0.02, TIP, "CONSTANT")
    ks(o, tk, (1.6, 1.0, 1.0), "LINEAR"); kl(o, tk, TIP, "LINEAR")
    tt = tk
    while tt < 17.0:
        tt += 0.12; dtt = tt - tk
        p = TIP + (VEL + jit) * dtt + Vector((0, 0, -0.5 * GRAV * dtt * dtt))
        kl(o, tt, p, "LINEAR")
    ks(o, 16.95, 1.0, "CONSTANT"); ks(o, 17.0, 0.001, "CONSTANT")
# a few props: microscope, beaker, ink bottle
load_asset("microscope", 38.0, LV(-32, 20, 0), rot=(0, 0, D(25)), axis="z")
bk_ = prim("cyl", "l_beaker", loc=LV(-18, 18, 6), vertices=48, radius=4.0, depth=12); setmat(bk_, mat("glass", (0.9, 0.95, 1.0), 0.02, trans=1.0, ior=1.45))
bt = prim("cyl", "l_bottle", loc=LV(-24, 24, 5), vertices=32, radius=3.0, depth=10); setmat(bt, mat("bottle", (0.08, 0.0, 0.04), 0.08, coat=1.0))
bl = prim("cyl", "l_bottle_lbl", loc=LV(-24, 24, 5), vertices=32, radius=3.05, depth=4.5); setmat(bl, mat("label", (0.85, 0.8, 0.65), 0.6))
bc = prim("cyl", "l_bottle_cap", loc=LV(-24, 24, 11), vertices=32, radius=1.6, depth=2.0); setmat(bc, mat("plast_blk2", (0.02, 0.02, 0.02), 0.3))
# desk lamp
lm = mat("lamp_green", (0.03, 0.18, 0.1), 0.3, 0.6, coat=0.8)
box("l_lamp_base", -40, -28, 2, 14, 0, 2, lm, Lo, bevel=0.5)
la = curve_obj("l_lamp_arm", [LV(-34, 8, 2), LV(-30, 6, 26), LV(-18, 3, 34)], 0.6, st_m)
shade = prim("cone", "l_shade", loc=LV(-16, 2, 32), vertices=48, radius1=6.0, radius2=2.0, depth=7.0); setmat(shade, lm)
aim(shade, TIP)
bulb_m, BULB = emat("bulb_m", (1.0, 0.8, 0.55), 0.0, solid=True)
bulb = prim("sphere", "l_bulb", loc=LV(-15.2, 1.6, 31.0), segments=16, ring_count=8, radius=1.6); setmat(bulb, bulb_m)
lamp = spot("l_lamp", LV(-15.0, 1.5, 30.5), (0, 0, 0), 0.0, size_deg=70, blend=0.6, col=(1.0, 0.72, 0.42), radius=2.0); aim(lamp, LV(6, 0, 8))
for (t, e, bb) in ((0, 0, 0), (EV["lamp"], 0, 0), (EV["lamp"] + 0.05, 100000, 25), (EV["lamp"] + 0.12, 25000, 6), (EV["lamp"] + 0.2, 120000, 30), (EV["lamp"] + 0.5, 120000, 30)):
    lamp.data.energy = e; K(lamp.data, "energy", F(t), "LINEAR"); kv(BULB, t, bb, "LINEAR")
a_ = area("l_moon", LV(-90, -40, 90), (0, 0, 0), 250000, size=80, col=(0.35, 0.55, 1.0)); aim(a_, LV(0, 0, 0))
a_ = area("l_rim", LV(40, 60, 40), (0, 0, 0), 150000, size=40, col=(0.5, 0.8, 1.0)); aim(a_, TIP)
a_ = area("l_tipkey", LV(20, -25, 30), (0, 0, 0), 0.0, size=15, col=(1.0, 0.85, 0.7)); aim(a_, TIP)
for (t, e) in ((0, 0), (EV["lamp"], 0), (EV["lamp"] + 0.2, 25000)):
    a_.data.energy = e; K(a_.data, "energy", F(t), "LINEAR")
ir_l = point("l_tiplight", CONTACT + Vector((0, -0.6, 0.6)), 0.0, col=(1.0, 0.45, 0.12), radius=0.4)
for (t, e) in ((0, 0), (EV["touch"] - 0.02, 0), (EV["touch"] + 0.06, 400), (EV["touch"] + 0.6, 0), (EV["end_touch"] - 0.02, 0), (EV["end_touch"] + 0.06, 500), (66.5, 200)):
    ir_l.data.energy = e; K(ir_l.data, "energy", F(t), "LINEAR")
hz = box("l_haze", -100, 100, -100, 60, -5, 90, None, Lo)
hm = bpy.data.materials.new("haze_m"); hm.use_nodes = True
for n in list(hm.node_tree.nodes): hm.node_tree.nodes.remove(n)
vs_ = hm.node_tree.nodes.new("ShaderNodeVolumeScatter"); SV(vs_, "Density", 0.0012)
vo_ = hm.node_tree.nodes.new("ShaderNodeOutputMaterial"); hm.node_tree.links.new(vs_.outputs[0], vo_.inputs["Volume"])
setmat(hz, hm)
set_vis(B, "L")

# ======================================================================== SET G: endless rows of printers (m)
B = snap(); Go = Vector(C.G)
pr = load_asset("printer", 0.45, (0, 0, 0), axis="max")
PH_ = 0.16
if pr:
    coll = bpy.data.collections.get("as_printer")
    ROOT.children.unlink(coll)
    mn, mx = bbox_of([o for o in coll.all_objects if o.type == "MESH"]); PH_ = mx.z - mn.z
    for iy in range(0, 12):
        for ix in range(-5, 6):
            e = link(bpy.data.objects.new("g_inst_%d_%d" % (ix, iy), None))
            e.instance_type = "COLLECTION"; e.instance_collection = coll
            e.location = Go + Vector((ix * 0.75, iy * 0.9, 0))
bm = bmesh.new(); bm2 = bmesh.new()
for iy in range(0, 90):
    for ix in range(-34, 35):
        x = ix * 0.75; y = iy * 0.9
        if not (abs(ix) <= 5 and iy < 12) or not pr:
            boxmesh(bm, x - 0.21, x + 0.21, y - 0.17, y + 0.17, 0, PH_)
        boxmesh(bm2, x - 0.05, x + 0.05, y - 0.16, y - 0.12, PH_ + 0.001, PH_ + 0.006)
prox = new_mesh_obj("g_proxy", bm); prox.location = Go; setmat(prox, mat("proxy_m", (0.75, 0.76, 0.78), 0.4))
leds = new_mesh_obj("g_leds", bm2); leds.location = Go
setmat(leds, emat("g_led_m", HUD, 14.0, solid=True)[0])
fl = box("g_floor", -60, 60, -10, 120, -0.02, 0.0, mat("g_floor_m", (0.01, 0.01, 0.012), 0.12, 0.0, coat=1.0), Go)
for i in range(6):
    a_ = area("g_strip%d" % i, Go + Vector((0, i * 14 + 2, 7)), (0, 0, 0), 1500, size=30, col=(0.85, 0.92, 1.0), shape="RECTANGLE", sy=0.6)
a_ = area("g_key", Go + Vector((-1.5, -2.0, 2.0)), (0, 0, 0), 150, size=1.5); aim(a_, Go + Vector((0, 0, 0.1)))
a_ = area("g_rim", Go + Vector((1.5, 2.5, 1.5)), (0, 0, 0), 150, size=1.5, col=(0.5, 0.85, 1.0)); aim(a_, Go + Vector((0, 0, 0.1)))
gh = box("g_haze", -60, 60, -10, 120, -1, 15, None, Go)
gm_ = bpy.data.materials.new("g_haze_m"); gm_.use_nodes = True
for n in list(gm_.node_tree.nodes): gm_.node_tree.nodes.remove(n)
vs_ = gm_.node_tree.nodes.new("ShaderNodeVolumeScatter"); SV(vs_, "Density", 0.02); SV(vs_, "Color", (0.6, 0.8, 1.0, 1))
vo_ = gm_.node_tree.nodes.new("ShaderNodeOutputMaterial"); gm_.node_tree.links.new(vs_.outputs[0], vo_.inputs["Volume"])
setmat(gh, gm_)
set_vis(B, "G")

# ======================================================================== SET A: hundreds of nozzles firing (10 um)
B = snap(); Ao = Vector(C.A)
box("a_plate", -260, 260, 0, 6, -14, 14, mat("gold_plate2", (0.85, 0.58, 0.26), 0.26, 1.0), Ao)
bmh = bmesh.new(); bmr = bmesh.new(); bms = bmesh.new(); vh = []; vr = []; vsx = []
random.seed(21)
for row, zz in enumerate((-6, -2, 2, 6)):
    for i in range(121):
        x = -240 + i * 4 + (row % 2) * 2
        r_ = random.random()
        before = len(bmh.verts)
        bmesh.ops.create_circle(bmh, cap_ends=True, segments=20, radius=1.0, matrix=Matrix.Translation((x, -0.03, zz)) @ Matrix.Rotation(D(90), 4, "X"))
        vh += [r_] * (len(bmh.verts) - before)
        before = len(bmr.verts)
        bmesh.ops.create_cone(bmr, cap_ends=False, segments=20, radius1=1.45, radius2=1.05, depth=0.05, matrix=Matrix.Translation((x, -0.06, zz)) @ Matrix.Rotation(D(90), 4, "X"))
        vr += [r_] * (len(bmr.verts) - before)
        before = len(bms.verts)
        boxmesh(bms, x - 0.45, x + 0.45, -60.0, -0.2, zz - 0.45, zz + 0.45)
        vsx += [r_] * (len(bms.verts) - before)
ah = new_mesh_obj("a_holes", bmh); ah.location = Ao; setmat(ah, mat("a_hole_m", (0.02, 0.0, 0.01), 0.1, emit=INKC, es=0.6))
ar = new_mesh_obj("a_rings", bmr); ar.location = Ao; set_rnd(ar.data, vr); setmat(ar, flash_mat("a_ring_m", (1.0, 0.45, 0.1), 2.2, 8.0, 0.07))
as_ = new_mesh_obj("a_streams", bms); as_.location = Ao; set_rnd(as_.data, vsx)
setmat(as_, stream_mat("a_stream_m", 1, 60.0, 2.2, 2.2, 4.0, [INKC]))
a_ = area("a_key", Ao + Vector((-40, -60, 50)), (0, 0, 0), 8 * 80 * 80, size=60); aim(a_, Ao)
a_ = area("a_rim", Ao + Vector((60, -30, -40)), (0, 0, 0), 10 * 80 * 80, size=60, col=(0.5, 0.85, 1.0)); aim(a_, Ao)
set_vis(B, "A")

# ======================================================================== SET T: holographic tower, grape, bucket (m)
B = snap(); To = Vector(C.T)
fg, b = newmat("t_floor_m")
co = b.sep(b.obj())
def gl_(c, sz):
    return b.mrange(b.math("ABSOLUTE", b.math("SUBTRACT", b.math("FRACT", b.math("DIVIDE", c, sz)), 0.5)), 0.47, 0.495, 0.0, 1.0)
gr_ = b.math("MAXIMUM", gl_(co[0], 5.0), gl_(co[1], 5.0))
fade = b.mrange(b.math("LENGTH", b.obj()) if False else b.math("ADD", b.math("ABSOLUTE", co[0]), b.math("ABSOLUTE", co[1])), 40.0, 160.0, 1.0, 0.0)
b.out_add((*HUD, 1), b.math("MULTIPLY", b.math("MULTIPLY", gr_, fade), 1.6))
tfl = prim("plane", "t_floor", loc=To, size=400); setmat(tfl, fg)
tw = load_asset("tower", 90.0, To + Vector((-36, 6, 0)), axis="z")
holo_fill, _ = rim_mat("holo_fill", HUD, 0.6, 3.0, base=0.015)
holo_line = emat("holo_line", HUD, 4.0, solid=True)[0]
holo_slab, _ = rim_mat("holo_slab", HUD, 0.8, 1.5, base=0.04)
if tw:
    st_ = [tw]
    while st_:
        o = st_.pop(); st_.extend(o.children)
        if o.type != "MESH": continue
        nm = o.name.lower()
        if nm.startswith("light"): o.hide_render = True; continue
        m_ = holo_line if ("profile" in nm or "column" in nm) else (holo_slab if ("floor" in nm or "ceil" in nm) else holo_fill)
        o.data.materials.clear(); o.data.materials.append(m_)
        try:
            for p in o.data.polygons: p.material_index = 0
        except Exception: pass
else:
    for k in range(30):
        box("t_fl%d" % k, -60, -6, -24, 36, k * 3.0, k * 3.0 + 0.25, holo_slab, To)
bkt = load_asset("bucket", 3.0, To, axis="z")
if bkt is None:
    o = prim("cyl", "t_bucket", loc=To + Vector((0, 0, 1.5)), vertices=48, radius=1.2, depth=3.0); setmat(o, mat("bucket_m", (0.6, 0.6, 0.62), 0.3, 1.0))
a_ = spot("t_bspot", To + Vector((6, -9, 14)), (0, 0, 0), 30000, size_deg=35, blend=0.6, col=(1.0, 0.85, 0.7)); aim(a_, To + Vector((0, 0, 1)))
a_ = area("t_bfill", To + Vector((-6, -6, 4)), (0, 0, 0), 2500, size=4, col=(0.5, 0.85, 1.0)); aim(a_, To + Vector((0, 0, 1.5)))
gm2 = mat("grape_m", (0.35, 0.75, 0.12), 0.15, 0.0, emit=(0.5, 1.0, 0.25), es=1.2, coat=1.0)
grape = prim("sphere", "t_grape", loc=To + Vector((0, 0, C.GR_Z0)), segments=32, ring_count=16, radius=0.45); setmat(grape, gm2)
gring_m, GRS = emat("t_gring_m", (0.6, 1.0, 0.35), 5.0, solid=True)
gring = prim("torus", "t_gring", loc=grape.location, major_radius=1.4, minor_radius=0.05, major_segments=64, minor_segments=6); setmat(gring, gring_m)
gring.parent = grape; gring.location = (0, 0, 0)
t = 49.8
while t <= 56.45:
    kl(grape, t, To + Vector((0, 0, C.grape_z(t))), "LINEAR"); t += 0.08
trail_m, _ = emat("t_trail_m", (0.6, 1.0, 0.35), 2.5, solid=True)
trail = curve_obj("t_trail", [To + Vector((0, 0, C.GR_Z0)), To + Vector((0, 0, C.GR_Z1))], 0.06, trail_m)
t = C.EV["grape0"]
while t <= C.EV["grape_land"] + 0.05:
    trail.data.bevel_factor_end = max(0.0, min(1.0, (C.GR_Z0 - C.grape_z(t)) / (C.GR_Z0 - C.GR_Z1)))
    K(trail.data, "bevel_factor_end", F(t), "LINEAR"); t += 0.1
trail.data.bevel_factor_end = 0.0; K(trail.data, "bevel_factor_end", 1, "CONSTANT"); K(trail.data, "bevel_factor_end", F(C.EV["grape0"]) - 1, "LINEAR")
spl_m, SPL = emat("t_splash_m", (0.6, 1.0, 0.35), 0.0)
spl = prim("torus", "t_splash", loc=To + Vector((0, 0, 3.0)), major_radius=1.0, minor_radius=0.08, major_segments=64, minor_segments=6); setmat(spl, spl_m)
gl0 = C.EV["grape_land"]
ks(spl, 0, 0.5); ks(spl, gl0 - 0.02, 0.5); kv(SPL, 0, 0); kv(SPL, gl0 - 0.02, 0); kv(SPL, gl0 + 0.04, 9.0); ks(spl, gl0 + 0.9, 3.5); kv(SPL, gl0 + 0.9, 0.0)
mark = prim("torus", "t_target", loc=To + Vector((0, 0, 0.05)), major_radius=2.6, minor_radius=0.05, major_segments=96, minor_segments=6); setmat(mark, hud_m)
set_vis(B, "T")

# ======================================================================== SET H: the halftone photo (mm)
B = snap(); Ho = Vector(C.Hh)
hm_, b = newmat("halftone_m")
co = b.sep(b.obj())
PW, PHh, PITCH = 152.0, 102.0, 0.30
amt_n = b.N.new("ShaderNodeValue"); AMT = amt_n.outputs[0]
def photo_at(x, y):
    if not PIMG: return (0.5, 0.4, 0.6, 1)
    tx = b.N.new("ShaderNodeTexImage"); tx.image = PIMG; tx.extension = "EXTEND"
    uv = b.comb(b.math("ADD", b.math("DIVIDE", x, PW), 0.5), b.math("ADD", b.math("DIVIDE", y, PHh), 0.5), 0.0)
    b.L.new(uv, tx.inputs["Vector"]); return tx.outputs["Color"]
def sepc(c_):
    n = b.N.new("ShaderNodeSeparateColor"); b.put(n.inputs[0], c_); return n.outputs
col = (1.0, 1.0, 0.98, 1)
for ci, (ang, ink_) in enumerate(((15, CMY[0]), (75, CMY[1]), (0, CMY[2]))):
    ca, sa = math.cos(D(ang)), math.sin(D(ang))
    rx = b.math("SUBTRACT", b.math("MULTIPLY", co[0], ca), b.math("MULTIPLY", co[1], sa))
    ry = b.math("ADD", b.math("MULTIPLY", co[0], sa), b.math("MULTIPLY", co[1], ca))
    qx = b.math("DIVIDE", rx, PITCH); qy = b.math("DIVIDE", ry, PITCH)
    cx = b.math("ADD", b.math("FLOOR", qx), 0.5); cy = b.math("ADD", b.math("FLOOR", qy), 0.5)
    fx = b.math("SUBTRACT", qx, cx); fy = b.math("SUBTRACT", qy, cy)
    d = b.math("SQRT", b.math("ADD", b.math("MULTIPLY", fx, fx), b.math("MULTIPLY", fy, fy)))
    crx = b.math("MULTIPLY", cx, PITCH); cry = b.math("MULTIPLY", cy, PITCH)
    px = b.math("ADD", b.math("MULTIPLY", crx, ca), b.math("MULTIPLY", cry, sa))
    py = b.math("SUBTRACT", b.math("MULTIPLY", cry, ca), b.math("MULTIPLY", crx, sa))
    cc = sepc(photo_at(px, py))
    cov = b.math("SUBTRACT", 1.0, b.math("POWER", cc[ci], 0.4545), clamp=True)
    r = b.math("MULTIPLY", b.math("SQRT", cov), 0.62)
    msk = b.mrange(d, b.math("SUBTRACT", r, 0.05), b.math("ADD", r, 0.05), 1.0, 0.0)
    col = b.mixc(msk, col, (*ink_, 1), "MULTIPLY")
plain = photo_at(co[0], co[1])
final = b.mixc(AMT, plain, col)
b.out_emit(final, 1.0)
AMT.default_value = 1.0; K(AMT, "default_value", 1, "CONSTANT"); K(AMT, "default_value", F(59.4), "BEZIER")
AMT.default_value = 0.0; K(AMT, "default_value", F(61.0), "BEZIER")
ph_ = box("h_photo", -PW / 2, PW / 2, -PHh / 2, PHh / 2, -0.3, 0.0, hm_, Ho)
box("h_table", -400, 400, -400, 400, -1.3, -0.3, mat("h_table_m", (0.012, 0.012, 0.014), 0.3, 0.0, coat=0.6), Ho)
a_ = area("h_key", Ho + Vector((-120, -160, 260)), (0, 0, 0), 4.0e6, size=120); aim(a_, Ho)
set_vis(B, "H")

# ======================================================================== cameras
cams = {}
for sid, t0, t1, st, keys, ex in C.SHOTS:
    org = Vector(C.SETS[st])
    cd = bpy.data.cameras.new("cam_" + sid); cd.sensor_width = 36.0; cd.clip_start = 0.01; cd.clip_end = 3000
    co_ = link(bpy.data.objects.new("cam_" + sid, cd))
    tg = link(bpy.data.objects.new("tgt_" + sid, None))
    con = co_.constraints.new("TRACK_TO"); con.target = tg; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    for (t, pos, tgt, lens) in keys:
        f = F(t) if t < t1 else F(t1) + 1
        co_.location = org + Vector(pos); K(co_, "location", f, "BEZIER")
        tg.location = org + Vector(tgt); K(tg, "location", f, "BEZIER")
        cd.lens = lens; K(cd, "lens", f, "BEZIER")
    if ex.get("fstop"):
        cd.dof.use_dof = True; cd.dof.aperture_fstop = ex["fstop"]; cd.dof.focus_object = tg
    cams[sid] = co_
sc.camera = cams["i01"]
# grape ring faces the tower camera
c_ = gring.constraints.new("TRACK_TO"); c_.target = cams["i13"]; c_.track_axis = "TRACK_Z"; c_.up_axis = "UP_Y"
setattr_safe(sc.eevee, "volumetric_end", 300.0)

def setup_glare():
    try:
        tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
        sc.compositing_node_group = tree
        rl = tree.nodes.new("CompositorNodeRLayers"); gl = tree.nodes.new("CompositorNodeGlare")
        try: gl.glare_type = "BLOOM"
        except Exception:
            s_ = sock(gl, "Type")
            if s_ is not None: s_.default_value = "Bloom"
        for nm, v in (("Threshold", 0.85), ("Strength", 0.6), ("Size", 0.75)):
            c2 = sock(gl, nm)
            if c2 is not None and getattr(c2, "type", "") == "VALUE": c2.default_value = v
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
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "ink.blend"))
print("INK SAVED", json.dumps(info, default=str)[:3000])
