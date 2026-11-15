# Machine Times: "Crema" (16:9, 25 fps, Blender 5.2 / Eevee). Build: Blender -b -P esp.py -- save
import bpy, bmesh, math, os, sys, json, uuid, random, time, urllib.request, urllib.parse
from mathutils import Vector, Matrix, Euler
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "save"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import esp_common as C
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
hp = ph_hdri("studio_small_09") or ph_hdri("kloofendal_48d_partly_cloudy_puresky")
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


# ======================================================================== crema body
_vis_orig = vis
VISED = set()
def vis(o, ranges, pad=1):
    if o is None or o.name in VISED: return
    VISED.add(o.name); _vis_orig(o, ranges, pad)
def set_ranges(st): return [(s[1], s[2]) for s in C.SHOTS if s[3] == st]
EV = C.EV
INFO = {}
OVR = {}            # per-shot camera offset (computed from asset positions)
WLS.default_value = 0.35
sc.view_settings.exposure = -0.4
def snap(): return set(o.name for o in bpy.data.objects)
def set_vis(before, st):
    rng = set_ranges(st)
    for o in bpy.data.objects:
        if o.name in before: continue
        if o.type == "EMPTY" and o.instance_type != "COLLECTION": continue
        if o.type == "CAMERA": continue
        if o.name.startswith("WGT") or o.hide_render: o.hide_render = True; continue
        vis(o, rng)
def kids_of(root):
    out, st_ = [], [root]
    while st_:
        o = st_.pop(); out.append(o); st_.extend(o.children)
    return out
def find(root, prefix):
    return next((o for o in kids_of(root) if o.name.startswith(prefix)), None) if root else None
def kl(o, t, loc, interp="BEZIER"): o.location = loc; K(o, "location", F(t), interp)
def kr(o, t, rot, interp="BEZIER"): o.rotation_euler = rot; K(o, "rotation_euler", F(t), interp)
def ks(o, t, s, interp="BEZIER"):
    o.scale = s if hasattr(s, "__len__") else (s, s, s); K(o, "scale", F(t), interp)
def kv(sock_, t, v, interp="BEZIER"): KV(sock_, F(t), v, interp)

def curve_obj(name, pts, bevel, m, res=4):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = bevel; cu.bevel_resolution = res
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        bp = sp.bezier_points[i]; bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = link(bpy.data.objects.new(name, cu)); cu.materials.append(m)
    return o

def rim_mat(name, col, strength, power=2.5, base=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt_ = m.node_tree; N_ = nt_.nodes
    for n in list(N_): N_.remove(n)
    o_ = N_.new("ShaderNodeOutputMaterial"); em = N_.new("ShaderNodeEmission"); SV(em, "Color", (*col, 1))
    lw = N_.new("ShaderNodeLayerWeight"); SV(lw, "Blend", 0.5)
    pw = N_.new("ShaderNodeMath"); pw.operation = "POWER"; nt_.links.new(lw.outputs["Facing"], pw.inputs[0]); SV(pw, 1, power)
    mu = N_.new("ShaderNodeMath"); mu.operation = "MULTIPLY_ADD"; nt_.links.new(pw.outputs[0], mu.inputs[0]); mu.inputs[1].default_value = strength; mu.inputs[2].default_value = base
    nt_.links.new(mu.outputs[0], em.inputs["Strength"])
    tr = N_.new("ShaderNodeBsdfTransparent"); ad = N_.new("ShaderNodeAddShader")
    nt_.links.new(tr.outputs[0], ad.inputs[0]); nt_.links.new(em.outputs[0], ad.inputs[1]); nt_.links.new(ad.outputs[0], o_.inputs["Surface"])
    setattr_safe(m, "surface_render_method", "BLENDED")
    return m

def half_cyl(name, r, z0, z1, org, m, seg=64, r_in=None):
    """vertical cylinder (or tube when r_in) cut open at y<0 for a cut-away view"""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=not r_in, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    for v in bm.verts: v.co.z += (z0 + z1) / 2
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(0, -1, 0), clear_outer=True)
    if not r_in:
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd: bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
    o = new_mesh_obj(name, bm); o.location = org
    for p in o.data.polygons: p.use_smooth = True
    if r_in:
        sd = o.modifiers.new("wall", "SOLIDIFY"); sd.thickness = r - r_in; sd.offset = -1.0; sd.use_rim = True; sd.use_even_offset = True
    setmat(o, m)
    return o

def helix(name, r, z0, z1, turns, wire, m, org):
    pts = []
    n = int(turns * 24)
    for i in range(n + 1):
        a = i / 24 * 2 * math.pi
        pts.append((r * math.cos(a), r * math.sin(a), z0 + (z1 - z0) * i / n))
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = wire; cu.bevel_resolution = 4
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (*p, 1)
    o = link(bpy.data.objects.new(name, cu)); cu.materials.append(m); o.location = org
    return o

# ---------------------------------------------------------------- shared materials
STEEL = mat("x_steel", (0.78, 0.78, 0.8), 0.18, 1.0)
CHROME = mat("x_chrome", (0.9, 0.9, 0.92), 0.06, 1.0)
BRUSHED = mat("x_brushed", (0.72, 0.72, 0.74), 0.28, 1.0)
BLACKP = mat("x_blackp", (0.02, 0.02, 0.022), 0.35, 0.0, coat=0.4)
FLOOR = mat("x_floor", (0.012, 0.012, 0.014), 0.22, 0.0, coat=1.0)
WALNUT = mat("x_walnut", (0.035, 0.016, 0.007), 0.3, 0.0, coat=0.7)
COFFEE = mat("x_coffee", (0.03, 0.012, 0.004), 0.06, 0.0, coat=1.0)
WATER = mat("x_water", (0.8, 0.9, 1.0), 0.02, 0.0, trans=1.0, ior=1.33, emit=(0.25, 0.6, 1.0), es=0.15)
COPPER = mat("x_copper", (0.95, 0.55, 0.35), 0.22, 1.0)

def crema_mat(name="x_crema"):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt_ = m.node_tree; N_ = nt_.nodes; L_ = nt_.links
    b = N_.get("Principled BSDF")
    tc = N_.new("ShaderNodeTexCoord")
    ns = N_.new("ShaderNodeTexNoise"); SV(ns, "Scale", 60.0); SV(ns, "Detail", 6.0); SV(ns, "Roughness", 0.6)
    L_.new(tc.outputs["Object"], ns.inputs["Vector"])
    cr = N_.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
    e[0].position = 0.3; e[0].color = (0.16, 0.06, 0.015, 1); e[1].position = 0.75; e[1].color = (0.52, 0.27, 0.08, 1)
    L_.new(ns.outputs["Fac"], cr.inputs[0]); L_.new(cr.outputs[0], b.inputs["Base Color"])
    vo = N_.new("ShaderNodeTexVoronoi"); SV(vo, "Scale", 900.0); setattr_safe(vo, "feature", "F1")
    L_.new(tc.outputs["Object"], vo.inputs["Vector"])
    bu = N_.new("ShaderNodeBump"); SV(bu, "Strength", 0.8); SV(bu, "Distance", 0.0008)
    L_.new(vo.outputs["Distance"], bu.inputs["Height"]); L_.new(bu.outputs["Normal"], b.inputs["Normal"])
    SV(b, "Roughness", 0.32); SV(b, "Coat Weight", 0.5); SV(b, "Subsurface Weight", 0.15)
    return m
CREMA = crema_mat()

def studio(name, org, size, key=1.0, warm=False, floor=True, rim_col=(0.75, 0.85, 1.0)):
    org = Vector(org)
    if floor:
        f = prim("plane", name + "_floor", loc=org, size=size * 30); setmat(f, FLOOR)
    kc = (1.0, 0.86, 0.7) if warm else (1.0, 0.97, 0.93)
    d = size * 3.0
    a = area(name + "_key", org + Vector((-d * 0.8, -d * 0.9, d * 0.9)), (0, 0, 0), 55 * d * d * key, size=d * 0.9, col=kc); aim(a, org + Vector((0, 0, size * 0.4)))
    a = area(name + "_rim", org + Vector((d * 0.9, d * 0.8, d * 0.7)), (0, 0, 0), 70 * d * d * key, size=d * 0.5, col=rim_col); aim(a, org + Vector((0, 0, size * 0.5)))
    a = area(name + "_top", org + Vector((0, 0.2 * d, d * 1.3)), (0, 0, 0), 25 * d * d * key, size=d * 1.2, col=(1, 1, 1)); aim(a, org)
    return f if floor else None

def bokeh(name, org, n, spread, z0, z1, col, strength, r, seed=1):
    random.seed(seed)
    m, _ = emat(name + "_m", col, strength, solid=True)
    bm = bmesh.new()
    for i in range(n):
        p = Vector((random.uniform(-spread, spread), random.uniform(spread * 0.6, spread * 1.4), random.uniform(z0, z1)))
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=r * random.uniform(0.6, 1.4), matrix=Matrix.Translation(p))
    o = new_mesh_obj(name, bm); o.location = org; setmat(o, m)
    return o

# ---------------------------------------------------------------- the cup (used three times)
def cup_at(key_suffix, loc, size=0.106, rot=(0, 0, 0)):
    r = load_asset("cup", size, loc, rot=rot)
    if r is None:
        o = prim("cyl", "cup_fallback" + key_suffix, loc=Vector(loc) + Vector((0, 0, 0.03)), vertices=48, radius=0.035, depth=0.06); setmat(o, mat("x_ceramic", (0.92, 0.92, 0.9), 0.15))
        s = prim("cyl", "crema_fallback" + key_suffix, loc=Vector(loc) + Vector((0, 0, 0.058)), vertices=48, radius=0.032, depth=0.002); setmat(s, CREMA)
        return None
    for o in kids_of(r):
        if o.type != "MESH": continue
        for i, ms in enumerate(o.material_slots):
            if ms.material and ms.material.name.startswith("LATTEART"): ms.material = CREMA
    return r

# ======================================================================== CUP set
B = snap(); Co = Vector(C.CUP)
studio("cup", Co, 0.12, key=0.45, warm=True, floor=False)
tbl = prim("plane", "cup_table", loc=Co, size=4); setmat(tbl, WALNUT)
cup1 = cup_at("_a", Co)
if cup1:
    cm = find(cup1, "cup_1")
    if cm:
        mn, mx = bbox_of([cm]); INFO["cup_top"] = [round(x, 4) for x in mx]; INFO["cup_ctr"] = [round(x, 4) for x in (mn + mx) / 2]
        top = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mx.z - 0.004))
        for sid, tgt in (("c02", (0.004, 0.0, 0.062)), ("c03", (0.0, 0.0, 0.06))):
            OVR[sid] = top - (Co + Vector(tgt))
bokeh("cup_bokeh", Co, 26, 0.9, 0.05, 0.6, (1.0, 0.62, 0.3), 6.0, 0.02, seed=3)
beans = load_asset("beans", 0.09, Co + Vector((0.11, 0.06, 0.0)))
set_vis(B, "CUP")

# ======================================================================== OLD set (before 1948 – graded sepia in post)
B = snap(); Oo = Vector(C.OLD)
studio("old", Oo, 0.45, key=0.7, warm=True, floor=False)
prim("plane", "old_table", loc=Oo, size=6)
setmat(bpy.data.objects["old_table"], WALNUT)
conti = load_asset("conti", 0.75, Oo + Vector((0.05, 0.22, 0.0)))
vg = load_asset("vgrinder", 0.24, Oo + Vector((-0.42, 0.12, 0.0)), rot=(0, 0, D(-25)))
gauges = load_asset("gauges", 0.62, Oo + Vector((0.30, -0.02, 0.24)), rot=(D(90), 0, 0), ground=False)
if gauges:
    hs = [o for o in kids_of(gauges) if o.type == "MESH" and o.name.startswith("Needle holder")]
    if hs:
        mn, mx = bbox_of(hs[:1]); c_ = (mn + mx) / 2; INFO["gauge"] = [round(x, 3) for x in (c_ - Oo)]
        OVR["o02"] = c_ - (Oo + Vector((0.30, 0.0, 0.40)))
cup_old = cup_at("_old", Oo + Vector((-0.30, 0.0, 0.0)))
if cup_old:
    for o in kids_of(cup_old):
        if o.type == "MESH":
            for ms in o.material_slots:
                if ms.material is CREMA: ms.material = COFFEE
# steam: volume puffs drifting up
stm = bpy.data.materials.new("steam_vol"); stm.use_nodes = True
for n in list(stm.node_tree.nodes): stm.node_tree.nodes.remove(n)
pv = stm.node_tree.nodes.new("ShaderNodeVolumePrincipled"); SV(pv, "Density", 6.0); SV(pv, "Color", (0.95, 0.92, 0.88, 1))
nz = stm.node_tree.nodes.new("ShaderNodeTexNoise"); SV(nz, "Scale", 6.0); SV(nz, "Detail", 4.0)
mr = stm.node_tree.nodes.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.5; mr.inputs[2].default_value = 0.75
stm.node_tree.links.new(nz.outputs["Fac"], mr.inputs[0])
mu = stm.node_tree.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = 6.0
stm.node_tree.links.new(mr.outputs[0], mu.inputs[0]); stm.node_tree.links.new(mu.outputs[0], pv.inputs["Density"])
so = stm.node_tree.nodes.new("ShaderNodeOutputMaterial"); stm.node_tree.links.new(pv.outputs[0], so.inputs["Volume"])
random.seed(4)
for i, (sx, sz) in enumerate([(0.0, 0.30), (0.12, 0.34), (-0.1, 0.32), (-0.30, 0.08), (-0.27, 0.10)]):
    o = prim("sphere", "old_steam%d" % i, loc=Oo + Vector((sx, -0.05, sz)), segments=16, ring_count=8, radius=0.06 if i < 3 else 0.03)
    setmat(o, stm)
    t0 = 6.05 + i * 0.5
    for t in (6.05, 15.4):
        kl(o, t, Oo + Vector((sx + (t - 6) * 0.004, -0.05, sz + (t - 6.05) * (0.035 if i < 3 else 0.02))), "LINEAR")
        ks(o, t, 1.0 + (t - 6.05) * 0.18, "LINEAR")
set_vis(B, "OLD")

# ======================================================================== LEV set – Gaggia lever group, cut open
B = snap(); Lo = Vector(C.LEV)
studio("lev", Lo, 0.35, key=0.9, floor=True)
pf = load_asset("portafilter", 0.233, Lo + Vector((0.078, 0.0, 0.215)), axis="x", ground=False)
wood = None; basket_top = 0.255
if pf:
    for o in kids_of(pf):
        if o.type == "MESH":
            for ms in o.material_slots:
                if ms.material and ms.material.name.startswith("wood"): wood = ms.material
    bk_ = find(pf, "basket")
    if bk_:
        mn, mx = bbox_of([bk_]); basket_top = mx.z - Lo.z; INFO["lev_basket"] = [round(x, 3) for x in (mn - Lo)] + [round(x, 3) for x in (mx - Lo)]
wood = wood or WALNUT
HZ0, HZ1 = basket_top + 0.004, basket_top + 0.20
half_cyl("lev_housing", 0.048, HZ0, HZ1, Lo, CHROME, r_in=0.040)
half_cyl("lev_cap", 0.052, HZ1, HZ1 + 0.012, Lo, CHROME)
half_cyl("lev_collar", 0.052, HZ0 - 0.006, HZ0 + 0.01, Lo, CHROME, r_in=0.031)
puck = half_cyl("lev_puck", 0.029, basket_top - 0.016, basket_top - 0.002, Lo, mat("x_grounds", (0.06, 0.03, 0.012), 0.9))
piston = half_cyl("lev_piston", 0.039, 0.0, 0.012, Lo, STEEL)
water = half_cyl("lev_water", 0.0385, 0.0, 1.0, Lo, WATER)
spring = helix("lev_spring", 0.030, 0.0, 1.0, 9, 0.0032, CHROME, Lo)
PZ_LOW, PZ_HIGH = HZ0 + 0.02, HZ1 - 0.07
def piston_at(t, z, interp="BEZIER"):
    kl(piston, t, Lo + Vector((0, 0, z)), interp)
    kl(spring, t, Lo + Vector((0, 0, z + 0.012)), interp); ks(spring, t, (1, 1, max(0.02, HZ1 - z - 0.012)), interp)
    kl(water, t, Lo + Vector((0, 0, basket_top)), interp); ks(water, t, (1, 1, max(0.0005, z - basket_top)), interp)
piston_at(0, PZ_LOW); piston_at(EV["lever_dn"], PZ_LOW); piston_at(EV["lever_dn1"], PZ_HIGH); piston_at(EV["push0"], PZ_HIGH); piston_at(EV["push1"], PZ_LOW)
# lever arm with wooden knob, pivot on the side of the cap
lever = link(bpy.data.objects.new("lev_lever", None)); lever.location = Lo + Vector((0.05, 0.0, HZ1 - 0.01))
arm = prim("cyl", "lev_arm", loc=(0, 0, 0.17), vertices=24, radius=0.009, depth=0.34); setmat(arm, CHROME); arm.parent = lever
knob = prim("sphere", "lev_knob", loc=(0, 0, 0.36), segments=32, ring_count=16, radius=0.024); setmat(knob, wood); knob.parent = lever
knob.scale = (1, 1, 1.35)
hub = prim("cyl", "lev_hub", loc=(0, 0, 0), rot=(D(90), 0, 0), vertices=32, radius=0.016, depth=0.03); setmat(hub, CHROME); hub.parent = lever
kr(lever, 0, (0, D(-20), 0)); kr(lever, 19.0, (0, D(-20), 0)); kr(lever, EV["lever_dn1"], (0, D(-105), 0)); kr(lever, EV["push0"], (0, D(-105), 0)); kr(lever, EV["push1"], (0, D(-20), 0))
# espresso dripping out under the portafilter
drp = prim("cyl", "lev_stream", loc=Lo + Vector((0.0, 0.0, 0.10)), vertices=16, radius=0.0025, depth=0.20); setmat(drp, COFFEE)
for v in drp.data.vertices: v.co.z -= 0.10
drp.location = Lo + Vector((0.0, 0.0, basket_top - 0.045))
ks(drp, 0, (1, 1, 0.001), "CONSTANT"); ks(drp, EV["drip"], (1, 1, 0.001)); ks(drp, EV["drip"] + 0.5, (1, 1, 1.0)); ks(drp, 26.7, (1, 1, 1.0))
cup_lev = cup_at("_lev", Lo + Vector((0.0, 0.0, 0.0)), size=0.09)
set_vis(B, "LEV")

# ======================================================================== SEA set – 90 m down
B = snap(); So = Vector(C.SEA)
sea = prim("cube", "sea_vol", loc=So + Vector((0, 0, 0.5)), size=12)
sv = bpy.data.materials.new("sea_vol_m"); sv.use_nodes = True
for n in list(sv.node_tree.nodes): sv.node_tree.nodes.remove(n)
vp = sv.node_tree.nodes.new("ShaderNodeVolumePrincipled"); SV(vp, "Density", 0.07); SV(vp, "Color", (0.1, 0.35, 0.6, 1)); SV(vp, "Absorption Color", (0.01, 0.12, 0.3, 1))
vo_ = sv.node_tree.nodes.new("ShaderNodeOutputMaterial"); sv.node_tree.links.new(vp.outputs[0], vo_.inputs["Volume"]); setmat(sea, sv)
diver = load_asset("diver", 0.7, So + Vector((0, 0, 0.05)), rot=(D(8), 0, D(20)))
if diver:
    kr(diver, 26.7, (D(8), 0, D(20)), "LINEAR"); kr(diver, 30.6, (D(10), 0, D(45)), "LINEAR")
    kl(diver, 26.7, So + Vector((0, 0, 0.25)), "LINEAR"); kl(diver, 30.6, So + Vector((0, 0, -0.05)), "LINEAR")
sun = spot("sea_sun", So + Vector((0.4, 0.6, 5.0)), (0, 0, 0), 2500, size_deg=40, blend=0.8, col=(0.6, 0.85, 1.0), radius=0.5); aim(sun, So)
a_ = area("sea_fill", So + Vector((-1.5, -2.0, 1.0)), (0, 0, 0), 120, size=2, col=(0.4, 0.7, 1.0)); aim(a_, So)
random.seed(8)
bm = bmesh.new()
for i in range(260):
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(0.002, 0.006), matrix=Matrix.Translation((random.uniform(-1.5, 1.5), random.uniform(-1.0, 2.0), random.uniform(-0.6, 1.8))))
snow = new_mesh_obj("sea_snow", bm); snow.location = So; setmat(snow, emat("sea_snow_m", (0.7, 0.9, 1.0), 2.0, solid=True)[0])
kl(snow, 26.7, So, "LINEAR"); kl(snow, 30.6, So + Vector((0, 0, 0.35)), "LINEAR")
set_vis(B, "SEA")

# ======================================================================== PUK set – the puck seen from above
B = snap(); Po = Vector(C.PUK)
studio("puk", Po, 0.1, key=0.8, floor=True)
pf2 = load_asset("portafilter", 0.233, Po + Vector((0.078, 0.0, 0.04)), axis="x", ground=False)
pc = Po + Vector((0, 0, 0.06))
if pf2:
    bk2 = find(pf2, "basket")
    if bk2:
        mn, mx = bbox_of([bk2]); pc = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mx.z - 0.006))
        OVR["p01"] = pc - Po
gm = mat("x_grounds2", (0.07, 0.035, 0.014), 0.95)
puck2 = prim("cyl", "puk_puck", loc=pc, vertices=64, radius=0.029, depth=0.004); setmat(puck2, gm)
puck2.modifiers.new("d", "DISPLACE").strength = 0.0
ar_m, AR = emat("puk_arrow_m", (1.0, 0.75, 0.4), 0.0, solid=True)
for i in range(7):
    a = (i / 7) * 2 * math.pi; rr = 0.0 if i == 0 else 0.017
    p = pc + Vector((rr * math.cos(a), rr * math.sin(a), 0.03))
    c_ = prim("cone", "puk_arrow%d" % i, loc=p, rot=(D(180), 0, 0), vertices=24, radius1=0.0025, radius2=0.0, depth=0.012); setmat(c_, ar_m)
    kl(c_, 30.6, p + Vector((0, 0, 0.02))); kl(c_, 31.4, p, "BEZIER"); kl(c_, 33.5, p - Vector((0, 0, 0.012)))
kv(AR, 30.6, 0.0); kv(AR, 31.2, 2.5); kv(AR, 33.5, 2.5)
set_vis(B, "PUK")

# ======================================================================== STU set – Linea Mini, x-ray, pour
B = snap(); Mo = Vector(C.STU)
studio("stu", Mo, 0.36, key=1.0, floor=True)
bokeh("stu_bokeh", Mo, 30, 2.0, 0.1, 1.2, (1.0, 0.7, 0.4), 4.0, 0.03, seed=5)
lin = load_asset("linea", 0.357, Mo, axis="z")
XR = []   # x-ray factor sockets
def xray_mat(base_m, name):
    """mix of the original look and a glowing glass shell, factor keyed"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt_ = m.node_tree; N_ = nt_.nodes; L_ = nt_.links
    for n in list(N_): N_.remove(n)
    out = N_.new("ShaderNodeOutputMaterial")
    pb = N_.new("ShaderNodeBsdfPrincipled"); SV(pb, "Base Color", (0.75, 0.75, 0.77, 1)); SV(pb, "Metallic", 1.0); SV(pb, "Roughness", 0.24)
    lw = N_.new("ShaderNodeLayerWeight"); SV(lw, "Blend", 0.35)
    em = N_.new("ShaderNodeEmission"); SV(em, "Color", (0.55, 0.85, 1.0, 1))
    mu = N_.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; L_.new(lw.outputs["Facing"], mu.inputs[0]); mu.inputs[1].default_value = 2.5
    L_.new(mu.outputs[0], em.inputs["Strength"])
    tr = N_.new("ShaderNodeBsdfTransparent"); ad = N_.new("ShaderNodeAddShader"); L_.new(tr.outputs[0], ad.inputs[0]); L_.new(em.outputs[0], ad.inputs[1])
    mx_ = N_.new("ShaderNodeMixShader"); L_.new(pb.outputs[0], mx_.inputs[1]); L_.new(ad.outputs[0], mx_.inputs[2]); L_.new(mx_.outputs[0], out.inputs["Surface"])
    setattr_safe(m, "surface_render_method", "BLENDED")
    XR.append(mx_.inputs[0])
    return m
spouts_pos = Mo + Vector((0, -0.12, 0.10))
if lin:
    for o in kids_of(lin):
        if o.type != "MESH": continue
        nm = o.name
        for ms in o.material_slots:
            mm = ms.material
            if not mm: continue
            n_ = mm.name.lower()
            if "logo" in n_ or "pressure display" in n_: continue
            if nm.startswith("Body"): ms.material = xray_mat(mm, "xr_" + nm)
            elif "steel" in n_ or "grid" in n_: ms.material = BRUSHED
            elif "white" in n_: ms.material = mat("x_whitep", (0.85, 0.85, 0.84), 0.3)
            elif "plastic" in n_: ms.material = BLACKP
        if nm.startswith("Sprouts"):
            mn, mx = bbox_of([o]); spouts_pos = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z)); INFO["spouts"] = [round(x, 3) for x in (spouts_pos - Mo)]
    mn, mx = bbox_of([o for o in kids_of(lin) if o.type == "MESH" and o.name.startswith("Body")])
    INFO["linea_body"] = [round(x, 3) for x in (mn - Mo)] + [round(x, 3) for x in (mx - Mo)]
else:
    mn, mx = Mo + Vector((-0.15, -0.15, 0.03)), Mo + Vector((0.15, 0.15, 0.35))
for s_ in XR:
    kv(s_, 0, 0.0); kv(s_, EV["xray0"], 0.0); kv(s_, EV["xray1"], 1.0); kv(s_, 40.6, 1.0); kv(s_, 40.85, 0.0, "CONSTANT")
# internals (visible through the x-ray): boiler, pump, water path
bc = (mn + mx) / 2
boiler = prim("cyl", "stu_boiler", loc=bc + Vector((0.0, 0.05, 0.02)), rot=(D(90), 0, 0), vertices=48, radius=0.055, depth=0.16); setmat(boiler, COPPER)
pump = prim("cyl", "stu_pump", loc=bc + Vector((-0.09, 0.08, -0.07)), rot=(0, D(90), 0), vertices=32, radius=0.025, depth=0.07); setmat(pump, BLACKP)
heat_m, HEAT = emat("stu_heat_m", (1.0, 0.35, 0.08), 0.0)
heat = prim("cyl", "stu_heat", loc=boiler.location, rot=(D(90), 0, 0), vertices=48, radius=0.058, depth=0.162); setmat(heat, heat_m)
kv(HEAT, 0, 0.0); kv(HEAT, 37.4, 0.0); kv(HEAT, 38.4, 2.5); kv(HEAT, 40.8, 2.5)
flow_m, FLOW = emat("stu_flow_m", (0.35, 0.75, 1.0), 0.0, solid=True)
path = [pump.location + Vector((0.035, 0, 0)), bc + Vector((-0.02, 0.10, -0.06)), boiler.location + Vector((0, 0.08, -0.04)),
        boiler.location + Vector((0, -0.06, 0.05)), Vector((spouts_pos.x, spouts_pos.y + 0.01, spouts_pos.z + 0.06))]
flow = curve_obj("stu_flow", path, 0.004, flow_m)
flow.data.bevel_factor_end = 0.0; K(flow.data, "bevel_factor_end", F(37.0), "BEZIER")
flow.data.bevel_factor_end = 1.0; K(flow.data, "bevel_factor_end", F(39.0), "BEZIER")
kv(FLOW, 0, 0.0); kv(FLOW, 36.9, 0.0); kv(FLOW, 37.1, 5.0); kv(FLOW, 40.8, 5.0)
# pour: two streams from the spouts into a cup on the drip tray
tray_z = Mo.z
if lin:
    trays = [o for o in kids_of(lin) if o.name.startswith("BodyFrontDripTray")]
    if trays: tray_z = bbox_of(trays)[1].z
cup_stu = cup_at("_stu", Vector((spouts_pos.x, spouts_pos.y, tray_z)), size=0.09)
st_m = COFFEE
for i, dx in enumerate((-0.008, 0.008)):
    s_ = prim("cyl", "stu_stream%d" % i, loc=(0, 0, 0), vertices=16, radius=0.0018, depth=1.0); setmat(s_, st_m)
    for v in s_.data.vertices: v.co.z -= 0.5
    s_.location = spouts_pos + Vector((dx, 0, -0.004))
    ks(s_, 0, (1, 1, 0.0005), "CONSTANT"); ks(s_, EV["pour0"], (1, 1, 0.0005)); ks(s_, EV["pour0"] + 0.4, (1, 1, 0.075)); ks(s_, EV["pour1"], (1, 1, 0.075))
OVR["m03"] = spouts_pos + Vector((0, 0, -0.01)) - (Mo + Vector((0.0, -0.05, 0.10)))
set_vis(B, "STU")

# ======================================================================== SGN set – backlit plexiglass sign
B = snap(); Go = Vector(C.SGN)
studio("sgn", Go, 0.3, key=0.35, warm=True, floor=True)
bokeh("sgn_bokeh", Go, 34, 1.6, 0.1, 1.2, (1.0, 0.62, 0.3), 5.0, 0.03, seed=9)
panel = prim("cube", "sgn_panel", loc=Go + Vector((0, 0, 0.30)), size=1.0); panel.scale = (0.30, 0.008, 0.10); apply_scale(panel)
setmat(panel, mat("x_acrylic", (0.95, 0.9, 0.82), 0.35, 0.0, trans=0.85, ior=1.49, emit=(1.0, 0.72, 0.45), es=0.12))
frame_ = prim("cube", "sgn_frame", loc=Go + Vector((0, 0.01, 0.30)), size=1.0); frame_.scale = (0.31, 0.006, 0.106); apply_scale(frame_); setmat(frame_, mat("x_brass", (0.95, 0.72, 0.38), 0.25, 1.0))
lt = area("sgn_back", Go + Vector((0, 0.08, 0.30)), (D(-90), 0, 0), 6, size=0.5, col=(1.0, 0.8, 0.55)); aim(lt, Go + Vector((0, -1, 0.30)))
for f_ in ("/System/Library/Fonts/Supplemental/SnellRoundhand.ttc", "/System/Library/Fonts/Supplemental/Zapfino.ttf"):
    if os.path.exists(f_):
        try: SCRIPT = bpy.data.fonts.load(f_); break
        except Exception: SCRIPT = None
else:
    SCRIPT = None
t1, _ = text3d("sgn_t1", "Crema caffè naturale", Go + Vector((0, -0.013, 0.312)), size=0.05, col=(1.0, 0.5, 0.15), es=4.0, extrude=0.0008)
t2, _ = text3d("sgn_t2", "FUNZIONA SENZA VAPORE", Go + Vector((0, -0.013, 0.258)), size=0.014, col=(0.9, 0.55, 0.25), es=1.5)
if SCRIPT: t1.data.font = SCRIPT
pop_in(t1, 52.0, 0.4)
set_vis(B, "SGN")

# ======================================================================== cameras
cams = {}
for sid, t0, t1_, st, keys, ex in C.SHOTS:
    org = Vector(C.SETS[st]); off = OVR.get(sid, Vector((0, 0, 0)))
    cd = bpy.data.cameras.new("cam_" + sid); cd.sensor_width = 36.0; cd.clip_start = 0.005; cd.clip_end = 200
    co_ = link(bpy.data.objects.new("cam_" + sid, cd))
    tg = link(bpy.data.objects.new("tgt_" + sid, None))
    con = co_.constraints.new("TRACK_TO"); con.target = tg; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    for (t, pos, tgt, lens) in keys:
        f = F(t) if t < t1_ else F(t1_) + 1
        co_.location = org + Vector(pos) + off; K(co_, "location", f, "BEZIER")
        tg.location = org + Vector(tgt) + off; K(tg, "location", f, "BEZIER")
        cd.lens = lens; K(cd, "lens", f, "BEZIER")
    if ex.get("fstop"):
        cd.dof.use_dof = True; cd.dof.aperture_fstop = ex["fstop"]; cd.dof.focus_object = tg
    cams[sid] = co_
sc.camera = cams[C.SHOTS[0][0]]

def setup_glare():
    try:
        tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
        sc.compositing_node_group = tree
        rl = tree.nodes.new("CompositorNodeRLayers"); gl = tree.nodes.new("CompositorNodeGlare")
        try: gl.glare_type = "BLOOM"
        except Exception:
            s_ = sock(gl, "Type")
            if s_ is not None: s_.default_value = "Bloom"
        for nm, v in (("Threshold", 1.0), ("Strength", 0.35), ("Size", 0.7)):
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
info = {"notes": NOTES, "assets": INFO_ASSETS, "info": INFO, "ovr": {k: [round(x, 3) for x in v] for k, v in OVR.items()}, "build_s": round(time.time() - T0, 1)}
json.dump(info, open(os.path.join(HERE, "build_info.json"), "w"), indent=1, default=str)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "esp.blend"))
print("ESP SAVED", json.dumps(info, default=str)[:3000])
