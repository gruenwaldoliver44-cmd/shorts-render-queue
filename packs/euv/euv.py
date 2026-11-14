# Machine Times sample: "50,000 drops of tin per second" (EUV lithography), 16:9, 25 fps, Blender 5.2 / Eevee.
# Run:  Blender -b -P euv.py -- save                 build the scene, save euv.blend next to this file
#       Blender -b euv.blend -P euv.py -- render S E [pct]   render frames S..E to r/f####.jpg (skip existing)
#       Blender -b euv.blend -P euv.py -- stills pct f1,f2,...  render single frames to s/f####.jpg
import bpy, bmesh, math, os, sys, json, uuid, random, time, urllib.request, urllib.parse
from mathutils import Vector, Matrix, Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "save"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import euv_common as C
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

VIOLET = (0.55, 0.25, 1.0)
EUVCOL = (0.62, 0.38, 1.0)
LASER = (1.0, 0.12, 0.05)
A = Vector(C.A); B = Vector(C.B); Cc = Vector(C.C); Lb = Vector(C.L); G = Vector(C.G); G2 = Vector(C.G2)
A_SHOTS = [(s[1], s[2]) for s in C.SHOTS if s[3] == "A"]
def shots_of(*ids): return [(s[1], s[2]) for s in C.SHOTS if s[0] in ids]

# ================================================================ SET A: vacuum chamber
steel = mat("steel", (0.32, 0.33, 0.35), 0.32, 1.0)
steel_dk = mat("steel_dk", (0.08, 0.085, 0.09), 0.45, 1.0)
shell = prim("cyl", "chamber", loc=A, vertices=96, radius=10, depth=22)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.flip_normals(); bpy.ops.object.mode_set(mode="OBJECT")
# brushed panels: noise bump on the shell
shm = mat("shell_m", (0.07, 0.075, 0.08), 0.34, 1.0)
try:
    nt2 = shm.node_tree; nz = nt2.nodes.new("ShaderNodeTexNoise"); SV(nz, "Scale", 40.0); SV(nz, "Detail", 6)
    bm_ = nt2.nodes.new("ShaderNodeBump"); SV(bm_, "Strength", 0.08)
    nt2.links.new(nz.outputs["Fac"], bm_.inputs["Height"]); nt2.links.new(bm_.outputs["Normal"], bsdf(shm).inputs["Normal"])
    vor = nt2.nodes.new("ShaderNodeTexVoronoi"); SV(vor, "Scale", 1.2)
    mr = nt2.nodes.new("ShaderNodeMapRange"); SV(mr, 1, 0.0); SV(mr, 2, 1.0); SV(mr, 3, 0.25); SV(mr, 4, 0.5)
    nt2.links.new(vor.outputs["Distance"], mr.inputs[0]); nt2.links.new(mr.outputs[0], bsdf(shm).inputs["Roughness"])
except Exception as e: NOTES.append("shell tex " + str(e)[:40])
setmat(shell, shm)
for i, z in enumerate([-8, -4.5, 4.5, 8]):
    r_ = prim("torus", "ring%d" % i, loc=A + Vector((0, 0, z)), major_radius=9.9, minor_radius=0.12, major_segments=96, minor_segments=8)
    setmat(r_, steel)
# vertical ribs + glowing service slits (detail for reflections)
rib_m = mat("rib_m", (0.10, 0.105, 0.11), 0.4, 1.0)
for i in range(28):
    ang = i / 28 * 2 * math.pi
    rb = prim("cube", "rib%d" % i, loc=A + Vector((9.82 * math.cos(ang), 9.82 * math.sin(ang), 0)), rot=(0, 0, ang), scale=(0.18, 0.09, 10.8), smooth=False)
    setmat(rb, rib_m)
slit_m, _ = emat("slit_m", (0.35, 0.6, 1.0), 5.0, solid=True)
for i in range(7):
    ang = (i + 0.5) / 7 * 2 * math.pi + 0.2
    sl = prim("cube", "slit%d" % i, loc=A + Vector((9.7 * math.cos(ang), 9.7 * math.sin(ang), -2.8 + (i % 3) * 2.6)), rot=(0, 0, ang), scale=(0.02, 1.2, 0.05), smooth=False)
    setmat(sl, slit_m)
# nozzle + catcher
noz = prim("cyl", "nozzle", loc=A + Vector((0, 0, 8.2)), vertices=48, radius=0.32, depth=5.4); setmat(noz, steel)
tip = prim("cone", "nozzle_tip", loc=A + Vector((0, 0, 5.25)), rot=(D(180), 0, 0), vertices=48, radius1=0.32, radius2=0.08, depth=0.5); setmat(tip, steel)
collar = prim("cyl", "nozzle_collar", loc=A + Vector((0, 0, 7.0)), vertices=48, radius=0.55, depth=0.6); setmat(collar, steel_dk)
cat = prim("cyl", "catcher", loc=A + Vector((0, 0, -8.5)), vertices=48, radius=0.6, depth=5.0); setmat(cat, steel)
catm = prim("cone", "catcher_mouth", loc=A + Vector((0, 0, -5.8)), vertices=48, radius1=0.6, radius2=1.1, depth=0.6); setmat(catm, steel_dk)
# collector mirror: spherical cap around the focus, facing -Y, with a central hole for the laser
bm = bmesh.new()
R = 5.0; NU, NV = 96, 28
th_max = math.acos(3.3 / R)
verts = []
for j in range(NV + 1):
    th = 0.11 + (th_max - 0.11) * j / NV
    row = []
    for i in range(NU):
        ph = i / NU * 2 * math.pi
        x = R * math.sin(th) * math.cos(ph); z = R * math.sin(th) * math.sin(ph); y = R * math.cos(th)
        row.append(bm.verts.new((x, y, z)))
    verts.append(row)
for j in range(NV):
    for i in range(NU):
        bm.faces.new((verts[j][i], verts[j][(i + 1) % NU], verts[j + 1][(i + 1) % NU], verts[j + 1][i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
coll_ = new_mesh_obj("collector", bm); coll_.location = A
for p_ in coll_.data.polygons: p_.use_smooth = True
sol = coll_.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.18
cm = mat("collector_m", (0.85, 0.85, 0.9), 0.04, 1.0, film=520.0, film_ior=1.9)
setmat(coll_, cm)
crim = prim("torus", "collector_rim", loc=A + Vector((0, 3.32, 0)), rot=(D(90), 0, 0), major_radius=3.78, minor_radius=0.14, major_segments=96, minor_segments=10); setmat(crim, steel)
# laser port behind the collector
lport = prim("cyl", "laser_port", loc=A + Vector((0, 7.5, 0)), rot=(D(90), 0, 0), vertices=48, radius=0.6, depth=4.0); setmat(lport, steel_dk)

# droplet stream (array of drops), masked away below the laser focus once the laser is on
drop_m = bpy.data.materials.new("tin_stream"); drop_m.use_nodes = True
ntd = drop_m.node_tree; Nd = ntd.nodes
bd = Nd.get("Principled BSDF"); SV(bd, "Base Color", (0.86, 0.86, 0.9, 1)); SV(bd, "Metallic", 1.0); SV(bd, "Roughness", 0.06)
SV(bd, "Emission Strength", 0.0)
outd = Nd.get("Material Output")
tcd = Nd.new("ShaderNodeNewGeometry"); spd = Nd.new("ShaderNodeSeparateXYZ"); ntd.links.new(tcd.outputs["Position"], spd.inputs[0])
cmpd = Nd.new("ShaderNodeMath"); cmpd.operation = "GREATER_THAN"; ntd.links.new(spd.outputs["Z"], cmpd.inputs[0]); SV(cmpd, 1, -1000.0)
trd = Nd.new("ShaderNodeBsdfTransparent"); mxd = Nd.new("ShaderNodeMixShader")
ntd.links.new(cmpd.outputs[0], mxd.inputs[0]); ntd.links.new(trd.outputs[0], mxd.inputs[1]); ntd.links.new(bd.outputs[0], mxd.inputs[2])
ntd.links.new(mxd.outputs[0], outd.inputs["Surface"])
setattr_safe(drop_m, "surface_render_method", "DITHERED")
CUT = cmpd.inputs[1]
KV(CUT, 1, -1000.0, "CONSTANT"); KV(CUT, F(C.LASER_ON), A.z - 0.02, "CONSTANT")
stream = prim("sphere", "stream", loc=A + Vector((0, 0, C.BASE0)), segments=24, ring_count=12, radius=0.12)
setmat(stream, drop_m)
arr = stream.modifiers.new("arr", "ARRAY"); arr.count = C.NDROP; arr.use_relative_offset = False
arr.use_constant_offset = True; arr.constant_offset_displace = (0, 0, -C.SP)
stream.location = A + Vector((0, 0, C.base_z(0))); K(stream, "location", 1, "LINEAR")
stream.location = A + Vector((0, 0, C.base_z(C.DUR + 0.2))); K(stream, "location", F(C.DUR + 0.2), "LINEAR")
macro_ranges = C.MACRO
nonmacro_A = [(a, b) for (s, a, b, st, k, e) in C.SHOTS if st == "A" and not e.get("macro")]
vis(stream, nonmacro_A)

# strobe plasma at the focus: sphere + light + laser beam pulses
plas_m, plas_s = emat("plasma_m", (0.85, 0.6, 1.0), 0.0, soft=1.5)
plasma = prim("ico", "plasma", loc=A, subdivisions=3, radius=0.22); setmat(plasma, plas_m)
halo_m, halo_s = emat("halo_m", (0.6, 0.35, 1.0), 0.0, alpha=0.35, soft=3.0)
halo = prim("sphere", "halo", loc=A, segments=32, ring_count=16, radius=0.6); setmat(halo, halo_m)
plight = point("plasma_light", A, 0.0, (0.7, 0.45, 1.0), 0.15)
beam_m, beam_s = emat("laser_beam_m", LASER, 0.0)
lbeam = prim("cyl", "laser_beam", loc=A + Vector((0, 4.0, 0)), rot=(D(90), 0, 0), vertices=16, radius=0.035, depth=8.0); setmat(lbeam, beam_m)
# continuous faint glow of the chamber's hydrogen/flash ambience
amb = point("chamber_fill", A + Vector((-6, -4, 5)), 250.0, (0.55, 0.65, 1.0), 2.0)
amb2 = area("chamber_key", A + Vector((-7, -6, 7)), (0, 0, 0), 500.0, 4.0, (0.85, 0.9, 1.0)); aim(amb2, A)
amb3 = area("chamber_rim", A + Vector((6, 5, 4)), (0, 0, 0), 700.0, 4.0, (1.0, 0.7, 0.45)); aim(amb3, A)

def strobe_keys():
    """per-frame keys for the strobe windows; zero elsewhere"""
    frames = {}
    for (a, b) in C.STROBE:
        cr = C.crossings(a - 0.2, b)
        for f in range(F(a), F(b) + 1):
            t = (f - 1) / FPS
            last = max([c for c in cr if c <= t + 0.5 / FPS] or [-9])
            dt = t - last
            frames[f] = math.exp(-max(0, dt) / 0.035) if dt < 0.25 else 0.0
    return frames
SK = strobe_keys()
f_prev = None
for f in range(1, C.NF + 1):
    v = SK.get(f, 0.0)
    if f_prev is not None and v == f_prev and f not in (1, C.NF): continue
    KV(plas_s, f, 30.0 * v, "CONSTANT"); KV(halo_s, f, 4.0 * v, "CONSTANT"); KV(beam_s, f, 40.0 * min(1, v * 1.4), "CONSTANT")
    plight.data.energy = 2500.0 * v; K(plight.data, "energy", f, "CONSTANT")
    s_ = 0.4 + 1.2 * v if v > 0.01 else 0.001; plasma.scale = (s_,) * 3; K(plasma, "scale", f, "CONSTANT")
    halo.scale = ((0.35 + 0.9 * v) if v > 0.01 else 0.001,) * 3; K(halo, "scale", f, "CONSTANT")
    f_prev = v
vis(plasma, nonmacro_A + macro_ranges); vis(halo, nonmacro_A + macro_ranges); vis(lbeam, nonmacro_A)

# 3D number in s03
t50, t50s = text3d("t50k", "50,000 drops\nevery second", A + Vector((0.24, -0.50, 1.95)), size=0.12, rot=(D(90), 0, D(-65)), es=4.0, align="CENTER")
pop_in(t50, C.EV["text50k"])
vis(t50, shots_of("s03"))

# --- macro rig: one drop frozen in time (s05, s12, s13, s14, s14b)
mdrop_m = mat("tin_macro", (0.88, 0.88, 0.92), 0.05, 1.0)
mdrop = prim("sphere", "mdrop", loc=A, segments=64, ring_count=32, radius=0.12); setmat(mdrop, mdrop_m)
vis(mdrop, shots_of("s05", "s12", "s13", "s14"))
# drop drifts down slowly in each macro shot (slow motion feel)
for (a, b) in shots_of("s05", "s12", "s13", "s14"):
    mdrop.location = A + Vector((0, 0, 0.05)); K(mdrop, "location", F(a), "LINEAR")
    mdrop.location = A + Vector((0, 0, -0.03)); K(mdrop, "location", F(b), "LINEAR")
# pancake (s13): flatten across the laser axis (thin along Y)
mdrop.scale = (1, 1, 1); K(mdrop, "scale", 1, "CONSTANT")
tp = C.EV["prepulse"]
K(mdrop, "scale", F(tp), "BEZIER")
mdrop.scale = (2.3, 0.22, 2.3); K(mdrop, "scale", F(tp + 0.55), "BEZIER")
K(mdrop, "scale", F(31.25) + 2, "CONSTANT")
mdrop.scale = (1, 1, 1); K(mdrop, "scale", F(31.26) + 3, "CONSTANT")  # not visible after s14 anyway
# macro pulses: thin red pre-pulse, thick main pulse
pp_m, pp_front, pp_s = beam_mat("prepulse_m", LASER, 0.0, axis="Z")
pp = prim("cyl", "prepulse", loc=A + Vector((0, 1.5, 0)), rot=(D(-90), 0, 0), vertices=24, radius=0.012, depth=3.0); setmat(pp, pp_m)
mp_m, mp_front, mp_s = beam_mat("mainpulse_m", (1.0, 0.45, 0.15), 0.0, axis="Z")
mp = prim("cyl", "mainpulse", loc=A + Vector((0, 1.5, 0)), rot=(D(-90), 0, 0), vertices=24, radius=0.035, depth=3.0); setmat(mp, mp_m)
vis(pp, shots_of("s05", "s13")); vis(mp, shots_of("s05", "s14"))
def pulse(strength_sock, t, peak, dur=0.10):
    KV(strength_sock, F(t) - 1, 0.0, "CONSTANT"); KV(strength_sock, F(t), peak, "CONSTANT")
    KV(strength_sock, F(t + dur), peak * 0.35, "CONSTANT"); KV(strength_sock, F(t + dur) + 1, 0.0, "CONSTANT")
KV(pp_s, 1, 0.0, "CONSTANT"); KV(mp_s, 1, 0.0, "CONSTANT")
pulse(pp_s, C.EV["twice1"], 5.0, 0.08); pulse(mp_s, C.EV["twice2"], 3.5, 0.12)
pulse(pp_s, tp, 6.0, 0.16)
pulse(mp_s, C.EV["mainpulse"], 8.0, 0.20)
# macro plasma bursts (reuse plasma objects: extra keys on a second, bigger sphere)
mb_m, mb_s = emat("burst_m", (0.9, 0.7, 1.0), 0.0, soft=1.5)
burst = prim("ico", "burst", loc=A, subdivisions=4, radius=0.12); setmat(burst, mb_m)
bh_m, bh_s = emat("bhalo_m", (0.55, 0.3, 1.0), 0.0, alpha=0.3, soft=3.0)
bhalo = prim("sphere", "bhalo", loc=A, segments=48, ring_count=24, radius=0.12); setmat(bhalo, bh_m)
ring_m, ring_s = emat("shock_m", (0.75, 0.6, 1.0), 0.0, alpha=0.6)
shock = prim("torus", "shock", loc=A, rot=(D(90), 0, 0), major_radius=0.2, minor_radius=0.012, major_segments=96, minor_segments=8); setmat(shock, ring_m)
mlight = point("macro_light", A, 0.0, (0.75, 0.5, 1.0), 0.05)
for o_ in (burst, bhalo): vis(o_, shots_of("s05", "s14", "s14b"))
vis(shock, shots_of("s14", "s14b"))
burst.scale = (0.01,) * 3; K(burst, "scale", 1, "CONSTANT"); bhalo.scale = (0.01,) * 3; K(bhalo, "scale", 1, "CONSTANT")
shock.scale = (0.01,) * 3; K(shock, "scale", 1, "CONSTANT")
KV(mb_s, 1, 0.0, "CONSTANT"); KV(bh_s, 1, 0.0, "CONSTANT"); KV(ring_s, 1, 0.0, "CONSTANT")
mlight.data.energy = 0; K(mlight.data, "energy", 1, "CONSTANT")
def burst_keys(t, big, hold=0.0):
    f0 = F(t)
    for o_ in (burst, bhalo, shock): o_.scale = (0.01,) * 3; K(o_, "scale", f0 - 1, "CONSTANT")
    seq = [(0, 1.0, 1.6, 0.6, 1.0), (2, 1.8, 3.0, 2.5, 0.8), (5, 2.2, 4.0, 6.0, 0.55), (10, 2.4, 4.6, 10.0, 0.4), (18, 2.3, 4.8, 14.0, 0.3)]
    if hold:
        seq += [(int(hold * FPS), 2.2, 4.6, 15.0, 0.25)]
    for df, sb, sh, sr, inten in seq:
        f = f0 + df
        burst.scale = (sb * big,) * 3; K(burst, "scale", f, "BEZIER")
        bhalo.scale = (sh * big,) * 3; K(bhalo, "scale", f, "BEZIER")
        shock.scale = (sr * big * (0.35 if big < 0.5 else 1.0),) * 3; K(shock, "scale", f, "BEZIER")
        KV(mb_s, f, 14.0 * inten, "BEZIER"); KV(bh_s, f, 1.6 * inten, "BEZIER"); KV(ring_s, f, 8.0 * inten * (1 if df < 12 else 0.2), "BEZIER")
        mlight.data.energy = 500.0 * inten * big; K(mlight.data, "energy", f, "BEZIER")
    fe = f0 + (seq[-1][0]) + 6
    for o_ in (burst, bhalo, shock): o_.scale = (0.01,) * 3; K(o_, "scale", fe, "CONSTANT")
    KV(mb_s, fe, 0.0, "CONSTANT"); KV(bh_s, fe, 0.0, "CONSTANT"); KV(ring_s, fe, 0.0, "CONSTANT")
    mlight.data.energy = 0; K(mlight.data, "energy", fe, "CONSTANT")
burst_keys(C.EV["twice2"], 0.3)
burst_keys(C.EV["mainpulse"], 1.0, hold=4.4)
# the tin drop disappears inside the burst
# (mdrop hidden from s14 main pulse on)
mdrop.hide_render = True; K(mdrop, "hide_render", F(C.EV["mainpulse"]) + 1, "CONSTANT")
mdrop.hide_render = True; K(mdrop, "hide_render", F(C.EV["twice2"]) + 1, "CONSTANT")
mdrop.hide_render = True; K(mdrop, "hide_render", F(9.6) + 1, "CONSTANT")
mdrop.hide_render = False; K(mdrop, "hide_render", F(26.2) - 1, "CONSTANT")
mdrop.hide_render = True; K(mdrop, "hide_render", F(31.25) + 40, "CONSTANT")
mk1 = area("macro_key", A + Vector((-1.2, -1.6, 1.4)), (0, 0, 0), 60.0, 0.8, (1.0, 0.95, 0.9)); aim(mk1, A)
mk2 = area("macro_rim", A + Vector((0.9, 1.2, 0.6)), (0, 0, 0), 18.0, 0.6, (0.6, 0.7, 1.0)); aim(mk2, A)
mk3 = area("macro_under", A + Vector((-0.6, 0.4, -1.4)), (0, 0, 0), 6.0, 1.2, (1.0, 0.75, 0.5)); aim(mk3, A)
for o_ in (mk1, mk2, mk3): vis(o_, C.MACRO)
# human hair for scale (s12)
hair_m = mat("hair_m", (0.16, 0.085, 0.045), 0.38, 0.0, coat=0.3)
try:
    nth = hair_m.node_tree; wv = nth.nodes.new("ShaderNodeTexWave"); SV(wv, "Scale", 18.0); SV(wv, "Distortion", 3.0)
    bh = nth.nodes.new("ShaderNodeBump"); SV(bh, "Strength", 0.25)
    nth.links.new(wv.outputs["Fac"], bh.inputs["Height"]); nth.links.new(bh.outputs["Normal"], bsdf(hair_m).inputs["Normal"])
except Exception: pass
hair = prim("cyl", "hair", loc=A + Vector((0.05, -0.62, 0.0)), rot=(D(8), D(14), 0), vertices=48, radius=0.33, depth=6.0); setmat(hair, hair_m)
vis(hair, shots_of("s12"))
hair.location = A + Vector((0.05, -0.62, 1.6)); K(hair, "location", F(26.2), "LINEAR")
hair.location = A + Vector((0.05, -0.62, 0.0)); K(hair, "location", F(C.EV["hair_in"] + 0.7), "BEZIER")
lab1, _ = text3d("lab_drop", "tin drop", A + Vector((0.0, 0.0, -0.32)), size=0.06, rot=(D(90), 0, D(-90)), es=2.5)
lab2, _ = text3d("lab_hair", "human hair", A + Vector((0.0, -0.62, -0.5)), size=0.06, rot=(D(90), 0, D(-90)), es=2.5)
for o_ in (lab1, lab2): vis(o_, shots_of("s12")); pop_in(o_, C.EV["hair_in"] + 0.9)
# temperature text (s14b)
th1, _ = text3d("t_hot", "~220,000 °C", A + Vector((0.0, 0.05, 0.95)), size=0.3, rot=(D(90), 0, D(-48)), es=5.0, col=(1.0, 0.85, 1.0))
th2, _ = text3d("t_sun", "40× hotter than the Sun's surface", A + Vector((0.0, 0.05, 0.64)), size=0.13, rot=(D(90), 0, D(-48)), es=3.0)
for o_ in (th1, th2): vis(o_, shots_of("s14b"))
pop_in(th1, C.EV["hot_text"]); pop_in(th2, C.EV["hot_text"] + 0.35)
# s15: EUV light leaves the plasma, hits the collector, and converges to the intermediate focus
cone_m, cone_s = emat("euv_cone_m", EUVCOL, 0.0, alpha=0.22, soft=1.2)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=64, radius1=3.7, radius2=0.02, depth=6.6)
cone = new_mesh_obj("euv_cone", bm); cone.location = A + Vector((0, 3.3 - 3.3, 0)); cone.rotation_euler = (D(90), 0, 0)
cone.location = A + Vector((0, 0.0, 0)); setmat(cone, cone_m)
# cone apex toward -Y (intermediate focus), base at the collector (y=+3.3)
cone.location = A + Vector((0, 3.3 - 3.3, 0))
bm2 = bmesh.new()
bmesh.ops.create_cone(bm2, cap_ends=False, cap_tris=False, segments=64, radius1=0.02, radius2=3.7, depth=3.3)
cone2 = new_mesh_obj("euv_fan", bm2); cone2.location = A + Vector((0, 1.65, 0)); cone2.rotation_euler = (D(-90), 0, 0); setmat(cone2, cone_m)
for o_ in (cone, cone2): vis(o_, shots_of("s15"))
KV(cone_s, 1, 0.0, "CONSTANT"); KV(cone_s, F(C.EV["flash_light"]) - 1, 0.0, "CONSTANT")
KV(cone_s, F(C.EV["flash_light"] + 0.25), 0.9, "BEZIER"); KV(cone_s, F(38.5), 0.7, "LINEAR")

# ================================================================ SET B: phone on a table
table_m = mat("table_m", (0.09, 0.06, 0.045), 0.35, 0.0, coat=0.4)
try:
    ntt = table_m.node_tree; wv = ntt.nodes.new("ShaderNodeTexWave"); SV(wv, "Scale", 1.6); SV(wv, "Distortion", 8.0); SV(wv, "Detail", 6)
    wv.wave_type = "BANDS"
    cr = ntt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.05, 0.03, 0.02, 1); cr.color_ramp.elements[1].color = (0.16, 0.10, 0.06, 1)
    ntt.links.new(wv.outputs["Fac"], cr.inputs[0]); ntt.links.new(cr.outputs[0], bsdf(table_m).inputs["Base Color"])
except Exception: pass
table = prim("plane", "table", loc=B, size=30); setmat(table, table_m)
wd_ = ph_tex("wood_table_001", "diff")
if wd_:
    try:
        ntt = table_m.node_tree; ti = ntt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(wd_)
        tcm = ntt.nodes.new("ShaderNodeTexCoord"); mpm = ntt.nodes.new("ShaderNodeMapping"); SV(mpm, "Scale", (0.35, 0.35, 0.35))
        ntt.links.new(tcm.outputs["Object"], mpm.inputs[0]); ntt.links.new(mpm.outputs[0], ti.inputs[0])
        ntt.links.new(ti.outputs["Color"], bsdf(table_m).inputs["Base Color"])
        rf_ = ph_tex("wood_table_001", "rough")
        if rf_:
            tr_ = ntt.nodes.new("ShaderNodeTexImage"); tr_.image = bpy.data.images.load(rf_); tr_.image.colorspace_settings.name = "Non-Color"
            ntt.links.new(mpm.outputs[0], tr_.inputs[0]); ntt.links.new(tr_.outputs["Color"], bsdf(table_m).inputs["Roughness"])
    except Exception as e: NOTES.append("table tex " + str(e)[:40])
phone = None  # BlenderKit token expired on the Mac -> modelled phone
PW, PL, PT = 0.72, 1.48, 0.082     # width, length, thickness (scaled 10x)
def rrect(name, w, l, t, r, z0, seg=10):
    bm_ = bmesh.new()
    pts = []
    for cx, cy, a0 in ((w / 2 - r, l / 2 - r, 0), (-w / 2 + r, l / 2 - r, 90), (-w / 2 + r, -l / 2 + r, 180), (w / 2 - r, -l / 2 + r, 270)):
        for k in range(seg + 1):
            a = D(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    vb = [bm_.verts.new((x, y, z0)) for x, y in pts]
    f_ = bm_.faces.new(vb)
    ex_ = bmesh.ops.extrude_face_region(bm_, geom=[f_])
    bmesh.ops.translate(bm_, verts=[e for e in ex_["geom"] if isinstance(e, bmesh.types.BMVert)], vec=(0, 0, t))
    bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces)
    o = new_mesh_obj(name, bm_); o.location = B
    bv_ = o.modifiers.new("bev", "BEVEL"); bv_.width = min(0.02, t * 0.3); bv_.segments = 4; bv_.limit_method = "ANGLE"
    return o
frame_m = mat("phone_frame", (0.55, 0.53, 0.5), 0.22, 1.0)
body = rrect("phone_body", PW, PL, PT, 0.1, 0.0); setmat(body, frame_m)
back_m = mat("phone_back", (0.06, 0.065, 0.075), 0.35, 0.0, coat=0.6)
glass_top = rrect("phone_glass", PW - 0.025, PL - 0.025, 0.004, 0.09, PT); setmat(glass_top, mat("phone_glass_m", (0.005, 0.005, 0.007), 0.12, 0.0, coat=0.3))
# side buttons
for i, (yy, ll) in enumerate(((0.32, 0.16), (0.12, 0.1))):
    bt = prim("cube", "pbtn%d" % i, loc=B + Vector((-PW / 2 - 0.006, yy, PT * 0.55)), scale=(0.008, ll / 2, 0.012), smooth=False); setmat(bt, frame_m)
bt = prim("cube", "pbtn_r", loc=B + Vector((PW / 2 + 0.006, 0.2, PT * 0.55)), scale=(0.008, 0.12, 0.012), smooth=False); setmat(bt, frame_m)
PH_TOP = PT + 0.004
scr_m = bpy.data.materials.new("screen_m"); scr_m.use_nodes = True
nts = scr_m.node_tree; Ns = nts.nodes
for n in list(Ns): Ns.remove(n)
so = Ns.new("ShaderNodeOutputMaterial"); se_ = Ns.new("ShaderNodeEmission"); sg = Ns.new("ShaderNodeBsdfGlossy")
SV(sg, "Roughness", 0.12); SV(sg, "Color", (0.025, 0.025, 0.03, 1))
gr = Ns.new("ShaderNodeTexGradient"); gr.gradient_type = "LINEAR"; tcs = Ns.new("ShaderNodeTexCoord")
mpg = Ns.new("ShaderNodeMapping"); SV(mpg, "Rotation", (0, 0, D(70)))
nts.links.new(tcs.outputs["Generated"], mpg.inputs[0]); nts.links.new(mpg.outputs[0], gr.inputs[0])
crs = Ns.new("ShaderNodeValToRGB"); crs.color_ramp.elements[0].color = (0.08, 0.05, 0.35, 1); crs.color_ramp.elements[1].color = (0.75, 0.3, 1.0, 1)
nts.links.new(gr.outputs["Fac"], crs.inputs[0])
SIMG = os.path.join(HERE, "screen.jpg")
SCR_SRC = crs.outputs[0]
if os.path.exists(SIMG):
    sti = Ns.new("ShaderNodeTexImage"); sti.image = bpy.data.images.load(SIMG)
    tcu = Ns.new("ShaderNodeTexCoord"); mpu = Ns.new("ShaderNodeMapping")
    SV(mpu, "Location", (0.5, 0.5, 0)); SV(mpu, "Rotation", (0, 0, D(90))); SV(mpu, "Scale", (1.0, 1.0, 1))
    # screen plane UV 0..1 portrait; rotate 90 deg so the 16:9 frame runs along the long side
    off = Ns.new("ShaderNodeVectorMath"); off.operation = "SUBTRACT"; SV(off, 1, (0.5, 0.5, 0))
    nts.links.new(tcu.outputs["UV"], off.inputs[0]); nts.links.new(off.outputs[0], mpu.inputs[0])
    nts.links.new(mpu.outputs[0], sti.inputs[0])
    SCR_SRC = sti.outputs["Color"]
    NOTES.append("screen image")
SCR_COL = Ns.new("ShaderNodeMix"); SCR_COL.data_type = "RGBA"
def by_id(coll, ident): return next(x for x in coll if x.identifier == ident)
SCR_FAC = by_id(SCR_COL.inputs, "Factor_Float"); SCR_FAC.default_value = 0.0
by_id(SCR_COL.inputs, "B_Color").default_value = (1.0, 0.92, 1.0, 1)
nts.links.new(SCR_SRC, by_id(SCR_COL.inputs, "A_Color"))
nts.links.new(by_id(SCR_COL.outputs, "Result_Color"), se_.inputs["Color"])
addsh = Ns.new("ShaderNodeAddShader"); nts.links.new(se_.outputs[0], addsh.inputs[0]); nts.links.new(sg.outputs[0], addsh.inputs[1])
nts.links.new(addsh.outputs[0], so.inputs["Surface"])
SCR_S = sock(se_, "Strength")
screen = prim("plane", "screen", loc=B + Vector((0, 0, 0.0)), scale=(0.33, 0.70, 1)); setmat(screen, scr_m)
isl = None
bv2 = None
INFO_PHONE = {}
def descendants(root):
    out, st = [], [root]
    while st:
        o = st.pop(); out.append(o); st.extend(o.children)
    return out
def place_screen():
    bpy.context.view_layer.update()
    screen.location = B + Vector((0, 0, PH_TOP + 0.0015))
    screen.scale = (PW / 2 - 0.035, PL / 2 - 0.035, 1)
    INFO_PHONE.update({"procedural": True})
place_screen()
isl = rrect("dyn_island", 0.17, 0.05, 0.002, 0.024, PH_TOP + 0.0016); isl.location = B + Vector((0, PL / 2 - 0.1, 0)); setmat(isl, mat("island_m", (0, 0, 0), 0.2, 0.0))
KV(SCR_S, 1, 0.0, "CONSTANT"); KV(SCR_S, F(C.EV["screen_on"]), 0.0, "LINEAR"); KV(SCR_S, F(C.EV["screen_on"] + 0.25), 1.6, "BEZIER")
# s24/s25: the screen plays "this video": violet flashes from the strobe pattern
cr2 = C.crossings(59.1, 63.5)
for f in range(F(59.1), F(63.5) + 1):
    t = (f - 1) / FPS
    last = max([c for c in cr2 if c <= t] or [-9]); v = math.exp(-max(0, t - last) / 0.05) if t - last < 0.3 else 0
    if f % 1 == 0:
        KV(SCR_S, f, 1.4 + 1.6 * v, "CONSTANT"); KV(SCR_FAC, f, 0.35 * v, "CONSTANT")
pk = area("phone_key", B + Vector((-3.5, 0.5, 4.5)), (0, 0, 0), 140.0, 1.5, (1.0, 0.93, 0.85)); aim(pk, B)
pr = area("phone_rim", B + Vector((2.6, 2.4, 1.2)), (0, 0, 0), 160.0, 1.5, (0.55, 0.65, 1.0)); aim(pr, B)
glow = point("screen_glow", B + Vector((0, 0, 0.45)), 0.0, (0.7, 0.45, 1.0), 0.4)
glow.data.energy = 0; K(glow.data, "energy", 1, "CONSTANT")
for f in range(F(59.1), F(63.5) + 1, 1):
    t = (f - 1) / FPS
    last = max([c for c in cr2 if c <= t] or [-9]); v = math.exp(-max(0, t - last) / 0.05) if t - last < 0.3 else 0
    glow.data.energy = 8 + 40 * v; K(glow.data, "energy", f, "CONSTANT")

# ================================================================ SET C: chip surface
die_m = mat("die_m", (0.03, 0.035, 0.05), 0.3, 0.6)
die = prim("plane", "die", loc=Cc, size=60); setmat(die, die_m)
fin_m = mat("fin_m", (0.95, 0.62, 0.38), 0.22, 1.0)
fin = prim("cube", "fins", loc=Cc + Vector((-12.0, -13.0, 0.12)), scale=(0.05, 0.2, 0.12), smooth=False); setmat(fin, fin_m); apply_scale(fin)
a1 = fin.modifiers.new("ax", "ARRAY"); a1.count = 100; a1.use_relative_offset = False; a1.use_constant_offset = True; a1.constant_offset_displace = (0.25, 0, 0)
a2 = fin.modifiers.new("ay", "ARRAY"); a2.count = 44; a2.use_relative_offset = False; a2.use_constant_offset = True; a2.constant_offset_displace = (0, 0.6, 0)
gate_m = mat("gate_m", (0.75, 0.78, 0.82), 0.3, 1.0)
gate = prim("cube", "gates", loc=Cc + Vector((-12.0, 0.0, 0.06)), scale=(0.025, 13.4, 0.06), smooth=False); setmat(gate, gate_m); apply_scale(gate)
g1 = gate.modifiers.new("ax", "ARRAY"); g1.count = 100; g1.use_relative_offset = False; g1.use_constant_offset = True; g1.constant_offset_displace = (0.25, 0, 0)
gate.location = Cc + Vector((-12.0 + 0.125, 0.0, 0.06))
# highlighted row (s08): same fins in one row, emissive where x < sweep
ROW_Y = -13.0 + 0.6 * 22
row_m = bpy.data.materials.new("row_m"); row_m.use_nodes = True
ntr = row_m.node_tree; Nr = ntr.nodes
br = Nr.get("Principled BSDF"); SV(br, "Base Color", (0.95, 0.62, 0.38, 1)); SV(br, "Metallic", 1.0); SV(br, "Roughness", 0.22)
SV(br, "Emission Color", (*EUVCOL, 1))
gpos = Nr.new("ShaderNodeNewGeometry"); sps = Nr.new("ShaderNodeSeparateXYZ"); ntr.links.new(gpos.outputs["Position"], sps.inputs[0])
lt = Nr.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; ntr.links.new(sps.outputs["X"], lt.inputs[0]); SV(lt, 1, -100.0)
ml = Nr.new("ShaderNodeMath"); ml.operation = "MULTIPLY"; ntr.links.new(lt.outputs[0], ml.inputs[0]); SV(ml, 1, 6.0)
ntr.links.new(ml.outputs[0], br.inputs["Emission Strength"])
SWEEP = lt.inputs[1]
row = prim("cube", "row", loc=Cc + Vector((-12.0, ROW_Y, 0.121)), scale=(0.051, 0.201, 0.121), smooth=False); setmat(row, row_m); apply_scale(row)
r1 = row.modifiers.new("ax", "ARRAY"); r1.count = 100; r1.use_relative_offset = False; r1.use_constant_offset = True; r1.constant_offset_displace = (0.25, 0, 0)
ub_m, ub_front, ub_s = beam_mat("uvbeam_m", EUVCOL, 8.0, axis="Z")
uvb = prim("cyl", "uv_beam", loc=Cc + Vector((0, ROW_Y, 3.1)), vertices=16, radius=0.025, depth=6.0); setmat(uvb, ub_m)
vis(uvb, shots_of("s08"))
x0, x1 = Cc.x - 3.0, Cc.x + 3.6
KV(SWEEP, 1, -1000.0, "CONSTANT")
KV(SWEEP, F(C.EV["sweep0"]), x0, "LINEAR"); KV(SWEEP, F(C.EV["sweep1"]), x1, "LINEAR")
uvb.location = Vector((x0, Cc.y + ROW_Y, Cc.z + 3.1)); K(uvb, "location", F(C.EV["sweep0"]), "LINEAR")
uvb.location = Vector((x1, Cc.y + ROW_Y, Cc.z + 3.1)); K(uvb, "location", F(C.EV["sweep1"]), "LINEAR")
uvdot = point("uv_dot", Vector((x0, Cc.y + ROW_Y, Cc.z + 0.2)), 0.0, EUVCOL, 0.02)
uvdot.data.energy = 0; K(uvdot.data, "energy", F(C.EV["sweep0"]) - 1, "CONSTANT")
uvdot.data.energy = 40; K(uvdot.data, "energy", F(C.EV["sweep0"]), "CONSTANT")
uvdot.location = Vector((x0, Cc.y + ROW_Y, Cc.z + 0.2)); K(uvdot, "location", F(C.EV["sweep0"]), "LINEAR")
uvdot.location = Vector((x1, Cc.y + ROW_Y, Cc.z + 0.2)); K(uvdot, "location", F(C.EV["sweep1"]), "LINEAR")
# blurry "normal light" (s07): big soft warm spot that covers dozens of switches
blur = spot("blur_light", Cc + Vector((2.2, 0.6, 5.0)), (0, 0, 0), 0.0, 38, 1.0, (1.0, 0.78, 0.45), 1.8)
aim(blur, Cc + Vector((2.2, 0.6, 0)))
blur.data.energy = 0; K(blur.data, "energy", 1, "CONSTANT")
K(blur.data, "energy", F(C.EV["blur_on"]), "LINEAR")
blur.data.energy = 2500; K(blur.data, "energy", F(C.EV["blur_on"] + 0.5), "BEZIER")
blur.location = Cc + Vector((2.2, 0.6, 5.0)); K(blur, "location", F(C.EV["blur_on"] + 0.5), "LINEAR")
blur.location = Cc + Vector((3.2, 0.9, 5.0)); K(blur, "location", F(16.9), "LINEAR")
blob_m, blob_s = emat("blob_m", (1.0, 0.8, 0.5), 0.0, alpha=0.18, soft=3.0)
blob = prim("sphere", "blob", loc=Cc + Vector((2.2, 0.6, 0.6)), segments=48, ring_count=24, radius=1.7, scale=(1, 1, 0.35)); setmat(blob, blob_m)
vis(blob, [])
KV(blob_s, F(C.EV["blur_on"]), 0.0, "LINEAR"); KV(blob_s, F(C.EV["blur_on"] + 0.5), 2.2, "BEZIER")
blob.location = Cc + Vector((2.2, 0.6, 0.6)); K(blob, "location", F(C.EV["blur_on"] + 0.5), "LINEAR")
blob.location = Cc + Vector((3.2, 0.9, 0.6)); K(blob, "location", F(16.9), "LINEAR")
ck = area("chip_key", Cc + Vector((-10, -4, 2.5)), (0, 0, 0), 900.0, 4.0, (0.75, 0.85, 1.0)); aim(ck, Cc)
cr_ = area("chip_rim", Cc + Vector((9, 6, 1.6)), (0, 0, 0), 700.0, 4.0, (1.0, 0.65, 0.4)); aim(cr_, Cc)
# chip key dims while the blurry light / UV beam carry the shot
ck.data.energy = 900; K(ck.data, "energy", F(13.3), "CONSTANT")
ck.data.energy = 250; K(ck.data, "energy", F(13.3) + 1, "CONSTANT")

# ================================================================ SET D: optics lab
floor_m = mat("lab_floor", (0.035, 0.037, 0.042), 0.16, 0.0, coat=0.5)
try:
    ntf = floor_m.node_tree; nzf = ntf.nodes.new("ShaderNodeTexNoise"); SV(nzf, "Scale", 3.0); SV(nzf, "Detail", 8)
    mrf = ntf.nodes.new("ShaderNodeMapRange"); SV(mrf, 3, 0.08); SV(mrf, 4, 0.3)
    ntf.links.new(nzf.outputs["Fac"], mrf.inputs[0]); ntf.links.new(mrf.outputs[0], bsdf(floor_m).inputs["Roughness"])
except Exception: pass
lfloor = prim("plane", "lab_floor", loc=Lb + Vector((70, 0, 0)), size=260); setmat(lfloor, floor_m)
# backdrop wall with soft panel lights (not a void)
wall_m = mat("lab_wall", (0.06, 0.065, 0.075), 0.5, 0.0)
wall = prim("plane", "lab_wall", loc=Lb + Vector((70, 9.0, 6)), rot=(D(90), 0, 0), size=260, scale=(1, 0.05, 1)); setmat(wall, wall_m)
strip_m, _ = emat("strip_m", (0.6, 0.75, 1.0), 2.5, solid=True)

table_lab_m = mat("bench_m", (0.12, 0.125, 0.13), 0.3, 1.0)
for xi in [0, 20, 40, 60, 80, 103, 130]:
    bench = prim("cube", "bench%d" % xi, loc=Lb + Vector((xi, 0, 0.35)), scale=(5.5 if xi != 103 else 9.0, 3.0, 0.35), smooth=False)
    bvb = bench.modifiers.new("bev", "BEVEL"); bvb.width = 0.03; bvb.segments = 3
    setmat(bench, table_lab_m)
    # optical breadboard holes
    hole_m = mat("hole_m", (0.01, 0.01, 0.012), 0.6, 0.0)
lk = area("lab_key", Lb + Vector((60, -12, 12)), (0, 0, 0), 9000.0, 25.0, (0.9, 0.95, 1.0), sy=8.0); aim(lk, Lb + Vector((60, 0, 0)))
lr = area("lab_back", Lb + Vector((60, 7.5, 6)), (0, 0, 0), 4000.0, 30.0, (0.5, 0.6, 1.0), sy=2.0); aim(lr, Lb + Vector((60, 0, 0.8)))
BT = 0.70  # bench top
# D1 waves
def wave_obj(name, x0_, x1_, z0, amp, lam, rad, col, es, step):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = rad; cu.bevel_resolution = 4
    sp_ = cu.splines.new("POLY"); n = int((x1_ - x0_) / step)
    sp_.points.add(n)
    for i in range(n + 1):
        x = x0_ + i * step
        sp_.points[i].co = (x, 0, z0 + amp * math.sin(2 * math.pi * x / lam), 1)
    o = link(bpy.data.objects.new(name, cu)); m_, s_ = emat(name + "_m", col, es, solid=True); cu.materials.append(m_)
    return o
wred = wave_obj("wave_red", -9, 9, 0.0, 0.45, 3.6, 0.045, (1.0, 0.25, 0.08), 6.0, 0.04)
wuv = wave_obj("wave_uv", -9, 9, 0.0, 0.05, 0.10, 0.010, EUVCOL, 12.0, 0.004)
wred.location = Lb + Vector((0, 0, BT + 1.15)); wuv.location = Lb + Vector((0, 0, BT + 0.3))
for o_, sp_ in ((wred, 1.6), (wuv, 0.5)):
    o_.location.x = Lb.x; K(o_, "location", F(19.3), "LINEAR")
    o_.location.x = Lb.x - sp_; K(o_, "location", F(21.25), "LINEAR")
tn1, _ = text3d("t_normal", "normal light", Lb + Vector((-2.6, -0.3, BT + 1.78)), size=0.2, es=2.5, align="LEFT")
tn2, _ = text3d("t_euv", "extreme ultraviolet  ·  13.5 nm", Lb + Vector((-2.6, -0.3, BT + 0.72)), size=0.22, es=4.0, col=(0.85, 0.7, 1.0), align="LEFT")
pop_in(tn2, C.EV["nm_text"])
for o_ in (wred, wuv, tn1, tn2): vis(o_, shots_of("s09"))
# D2 light bulb
bulb = None
fil_m, fil_s = emat("filament_m", (1.0, 0.62, 0.3), 0.0, solid=True)
if bulb is None:
    glass = prim("sphere", "bulb_glass", loc=Lb + Vector((20, 0, BT + 0.95)), segments=64, ring_count=32, radius=0.42)
    setmat(glass, mat("bulb_glass_m", (1, 1, 1), 0.02, 0.0, trans=1.0, ior=1.5))
    neck = prim("cone", "bulb_neck", loc=Lb + Vector((20, 0, BT + 0.52)), vertices=48, radius1=0.17, radius2=0.3, depth=0.25)
    setmat(neck, MATS["bulb_glass_m"])
    base = prim("cyl", "bulb_base", loc=Lb + Vector((20, 0, BT + 0.25)), vertices=48, radius=0.17, depth=0.32)
    setmat(base, mat("brass", (0.8, 0.62, 0.35), 0.28, 1.0))
    for k in range(4):
        th_ = prim("torus", "thread%d" % k, loc=Lb + Vector((20, 0, BT + 0.14 + k * 0.07)), major_radius=0.17, minor_radius=0.018, major_segments=48, minor_segments=6)
        setmat(th_, MATS["brass"])
    tipb = prim("sphere", "bulb_tip", loc=Lb + Vector((20, 0, BT + 0.08)), radius=0.06); setmat(tipb, mat("solder", (0.2, 0.2, 0.22), 0.4, 1.0))
    sock_ = prim("cyl", "bulb_socket", loc=Lb + Vector((20, 0, BT + 0.05)), vertices=48, radius=0.26, depth=0.1); setmat(sock_, steel_dk)
FIL_Z = BT + 0.95
cu = bpy.data.curves.new("filament", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.006
spf = cu.splines.new("POLY"); nn = 240; spf.points.add(nn - 1)
for i in range(nn):
    u = i / (nn - 1); x = -0.14 + 0.28 * u
    spf.points[i].co = (x, 0.02 * math.cos(u * 60), 0.02 * math.sin(u * 60) + 0.03 * math.sin(math.pi * u), 1)
filo = link(bpy.data.objects.new("filament", cu)); filo.location = Lb + Vector((20, 0, FIL_Z)); cu.materials.append(fil_m)
for side in (-1, 1):
    wq = prim("cyl", "lead", loc=Lb + Vector((20 + side * 0.14, 0, FIL_Z - 0.2)), vertices=8, radius=0.006, depth=0.42); setmat(wq, steel)
bl = point("bulb_light", Lb + Vector((20, 0, FIL_Z)), 0.0, (1.0, 0.7, 0.4), 0.08)
# glows, flickers, dies
seqb = [(21.25, 1.0), (21.9, 1.0), (22.0, 0.25), (22.06, 0.9), (22.15, 0.1), (22.2, 0.7), (C.EV["bulb_die"], 0.0)]
for t, v in seqb:
    KV(fil_s, F(t), 7.0 * v, "CONSTANT"); bl.data.energy = 18.0 * v; K(bl.data, "energy", F(t), "CONSTANT")
tlamp, _ = text3d("t_lamp", "13.5 nm?", Lb + Vector((20.55, -0.2, BT + 1.15)), size=0.13, es=3.0, col=(0.85, 0.7, 1.0), align="LEFT")
pop_in(tlamp, 22.45); vis(tlamp, shots_of("s10"))
# D3 air: beam fades in haze
air_m = bpy.data.materials.new("air_m"); air_m.use_nodes = True
nta = air_m.node_tree
for n in list(nta.nodes): nta.nodes.remove(n)
ao = nta.nodes.new("ShaderNodeOutputMaterial"); av = nta.nodes.new("ShaderNodeVolumePrincipled")
SV(av, "Density", 0.08); SV(av, "Color", (0.7, 0.75, 0.85, 1))
nta.links.new(av.outputs[0], ao.inputs["Volume"])
air = prim("cube", "air", loc=Lb + Vector((42.5, 0, BT + 1.0)), scale=(2.6, 1.6, 1.0), smooth=False); setmat(air, air_m)
airb_m, airb_front, airb_s = beam_mat("airbeam_m", EUVCOL, 26.0, axis="Z", fade=(-0.8, 1.3))
airb = prim("cyl", "air_beam", loc=Lb + Vector((41.0, 0, BT + 1.0)), rot=(0, D(90), 0), vertices=16, radius=0.03, depth=10.0); setmat(airb, airb_m)
# object-space Z of the beam = world x - 41 (rotated cylinder, world 36..46); air starts at world x 39.9
src1 = prim("cyl", "euv_source1", loc=Lb + Vector((35.7, 0, BT + 1.0)), rot=(0, D(90), 0), vertices=32, radius=0.25, depth=0.8); setmat(src1, steel)
KV(airb_front, 1, -100.0, "CONSTANT"); KV(airb_front, F(C.EV["air_beam"]), -5.0, "LINEAR"); KV(airb_front, F(C.EV["air_beam"] + 0.9), 5.0, "LINEAR")
tair, _ = text3d("t_air", "air", Lb + Vector((42.5, -1.7, BT + 1.55)), size=0.45, es=2.0, align="CENTER")
for o_ in (air, airb, tair): vis(o_, shots_of("s16"))
pop_in(tair, C.EV["air_beam"] + 0.5)
# D4 glass block stops the beam
glass_m = mat("block_glass", (0.85, 0.95, 1.0), 0.02, 0.0, trans=1.0, ior=1.5)
gblock = prim("cube", "glass_block", loc=Lb + Vector((60.0, 0, BT + 1.0)), scale=(0.6, 1.1, 0.95), smooth=False)
bvg = gblock.modifiers.new("bev", "BEVEL"); bvg.width = 0.04; bvg.segments = 4; setmat(gblock, glass_m)
gb_m, gb_front, gb_s = beam_mat("glassbeam_m", EUVCOL, 28.0, axis="Z")
gbeam = prim("cyl", "glass_beam", loc=Lb + Vector((57.5, 0, BT + 1.0)), rot=(0, D(90), 0), vertices=16, radius=0.03, depth=5.0); setmat(gbeam, gb_m)
src2 = prim("cyl", "euv_source2", loc=Lb + Vector((54.6, 0, BT + 1.0)), rot=(0, D(90), 0), vertices=32, radius=0.25, depth=0.8); setmat(src2, steel)
# beam z (object) = world x - 57.5 ; block face at world x = 59.4 -> z = 1.9
KV(gb_front, 1, -100.0, "CONSTANT"); KV(gb_front, F(C.EV["glass_beam"]), -2.5, "LINEAR"); KV(gb_front, F(C.EV["glass_beam"] + 0.3), 1.88, "LINEAR")
hit_m, hit_s = emat("hit_m", EUVCOL, 0.0, alpha=0.7, soft=2.0)
hit = prim("sphere", "glass_hit", loc=Lb + Vector((59.4, 0, BT + 1.0)), segments=24, ring_count=12, radius=0.2, scale=(0.3, 1, 1)); setmat(hit, hit_m)
KV(hit_s, 1, 0.0, "CONSTANT"); KV(hit_s, F(C.EV["glass_beam"] + 0.3), 0.0, "CONSTANT"); KV(hit_s, F(C.EV["glass_beam"] + 0.35), 30.0, "CONSTANT")
tgl, _ = text3d("t_glass", "glass", Lb + Vector((60.0, -1.2, BT + 2.15)), size=0.32, es=2.0)
for o_ in (gblock, gbeam, hit, tgl): vis(o_, shots_of("s17"))
pop_in(tgl, C.EV["glass_beam"] + 0.4)
# D5 a lens tips over
lens = prim("sphere", "lens", loc=Lb + Vector((80.0, 0, BT + 1.15)), segments=64, ring_count=32, radius=0.7, scale=(1, 0.16, 1))
setmat(lens, glass_m)
lring = prim("torus", "lens_ring", loc=Lb + Vector((80.0, 0, BT + 1.15)), rot=(D(90), 0, 0), major_radius=0.72, minor_radius=0.05, major_segments=64, minor_segments=8)
setmat(lring, MATS["brass"] if "brass" in MATS else mat("brass", (0.8, 0.62, 0.35), 0.28, 1.0))
post = prim("cyl", "lens_post", loc=Lb + Vector((80.0, 0, BT + 0.22)), vertices=24, radius=0.05, depth=0.44); setmat(post, steel)
lpiv = bpy.data.objects.new("lens_piv", None); link(lpiv); lpiv.location = Lb + Vector((80.0, 0, BT + 0.44))
for o_ in (lens, lring):
    o_.parent = lpiv; o_.location = o_.location - lpiv.location
tf = C.EV["lens_fall"]
lpiv.rotation_euler = (0, 0, 0); K(lpiv, "rotation_euler", F(tf), "LINEAR")
lpiv.rotation_euler = (D(12), 0, 0); K(lpiv, "rotation_euler", F(tf + 0.2), "BEZIER")
lpiv.rotation_euler = (D(88), 0, 0); K(lpiv, "rotation_euler", F(tf + 0.55), "BEZIER")
lpiv.rotation_euler = (D(80), 0, 0); K(lpiv, "rotation_euler", F(tf + 0.7), "BEZIER")
lpiv.rotation_euler = (D(86), 0, 0); K(lpiv, "rotation_euler", F(tf + 0.85), "BEZIER")
lpiv.location = Lb + Vector((80.0, 0, BT + 0.44)); K(lpiv, "location", F(tf + 0.2), "LINEAR")
lpiv.location = Lb + Vector((80.0, 0.1, BT + 0.12)); K(lpiv, "location", F(tf + 0.55), "BEZIER")
tno, _ = text3d("t_nolens", "no lenses", Lb + Vector((80.0, -1.2, BT + 1.95)), size=0.3, es=2.6)
pop_in(tno, tf + 0.55); vis(tno, shots_of("s18"))
# D6 mirror chain in vacuum to the wafer
mir_m = mat("mirror_m", (0.9, 0.9, 0.92), 0.02, 1.0, film=480.0, film_ior=1.9)
PTS = [Vector((97.0, 2.2, 1.6)), Vector((100.0, -2.4, 1.6)), Vector((103.0, 2.4, 1.6)), Vector((106.0, -2.4, 1.6)), Vector((109.0, 2.2, 1.6)), Vector((111.5, -1.6, 1.3))]
PTS = [Lb + Vector((p.x, p.y, BT + p.z)) for p in PTS]
srcp = Lb + Vector((94.0, -2.2, BT + 1.6))
src3 = prim("cyl", "euv_source3", loc=srcp, vertices=32, radius=0.28, depth=0.9); setmat(src3, steel)
d0 = (PTS[0] - srcp).normalized(); src3.rotation_euler = d0.to_track_quat("Z", "Y").to_euler()
chain_pts = [srcp] + PTS
seg_objs = []
for i in range(len(chain_pts) - 1):
    a_, b_ = chain_pts[i], chain_pts[i + 1]
    L_ = (b_ - a_).length
    m_, front, st_ = beam_mat("seg%d_m" % i, EUVCOL, 24.0, axis="Z")
    sg_ = prim("cyl", "seg%d" % i, loc=(a_ + b_) / 2, vertices=16, radius=0.03, depth=L_); setmat(sg_, m_)
    sg_.rotation_euler = (b_ - a_).normalized().to_track_quat("Z", "Y").to_euler()
    t_s = C.EV["chain0"] + i * C.EV["chain_seg"]
    KV(front, 1, -100.0, "CONSTANT"); KV(front, F(t_s), -L_ / 2, "LINEAR"); KV(front, F(t_s + C.EV["chain_seg"]), L_ / 2 + 0.05, "LINEAR")
    seg_objs.append(sg_)
for i in range(len(PTS) - 1):
    p_ = PTS[i]; din = (p_ - chain_pts[i]).normalized(); dout = (chain_pts[i + 2] - p_).normalized()
    nrm = (dout - din).normalized()
    mo = prim("cyl", "mirror%d" % i, loc=p_, vertices=64, radius=0.62, depth=0.12); setmat(mo, mir_m)
    mo.rotation_euler = nrm.to_track_quat("Z", "Y").to_euler()
    back = prim("cyl", "mback%d" % i, loc=p_ - nrm * 0.1, vertices=64, radius=0.66, depth=0.1); back.rotation_euler = mo.rotation_euler; setmat(back, steel_dk)
    rim_ = prim("torus", "mrim%d" % i, loc=p_ - nrm * 0.02, major_radius=0.66, minor_radius=0.045, major_segments=64, minor_segments=8); rim_.rotation_euler = mo.rotation_euler; setmat(rim_, steel)
    pst = prim("cyl", "mpost%d" % i, loc=Vector((p_.x, p_.y, (BT + p_.z) / 2 - 0.3)), vertices=16, radius=0.05, depth=max(0.2, p_.z - BT - 0.6)); setmat(pst, steel)
waf_m = bpy.data.materials.new("wafer_m"); waf_m.use_nodes = True
ntw = waf_m.node_tree; bw = ntw.nodes.get("Principled BSDF")
SV(bw, "Metallic", 1.0); SV(bw, "Roughness", 0.12); SV(bw, "Thin Film Thickness", 600.0); SV(bw, "Thin Film IOR", 2.2)
brick = ntw.nodes.new("ShaderNodeTexBrick"); SV(brick, "Scale", 14.0); SV(brick, "Mortar Size", 0.03); SV(brick, "Brick Width", 1.0); SV(brick, "Row Height", 1.0)
SV(brick, "Color1", (0.55, 0.58, 0.7, 1)); SV(brick, "Color2", (0.45, 0.5, 0.65, 1)); SV(brick, "Mortar", (0.1, 0.1, 0.12, 1))
ntw.links.new(brick.outputs["Color"], bw.inputs["Base Color"])
SV(bw, "Emission Color", (*EUVCOL, 1)); WAF_E = sock(bw, "Emission Strength")
if True:
    wd = prim("cyl", "wafer_disc", loc=PTS[-1], vertices=128, radius=1.0, depth=0.03); setmat(wd, waf_m)
    dwi = (PTS[-1] - PTS[-2]).normalized(); wd.rotation_euler = dwi.to_track_quat("Z", "Y").to_euler()
    wst = prim("cube", "wafer_stand", loc=Vector((PTS[-1].x, PTS[-1].y, (PTS[-1].z + Lb.z + BT) / 2 - 0.5)), scale=(0.08, 0.08, max(0.1, (PTS[-1].z - Lb.z - BT) / 2 - 0.5)), smooth=False); setmat(wst, steel)
KV(WAF_E, 1, 0.0, "CONSTANT"); KV(WAF_E, F(C.EV["wafer"]), 0.0, "LINEAR"); KV(WAF_E, F(C.EV["wafer"] + 0.3), 3.5, "BEZIER")
tvac, _ = text3d("t_vac", "vacuum", Lb + Vector((103.0, 2.8, BT + 3.4)), size=0.45, es=2.0, rot=(D(70), 0, 0))
pop_in(tvac, 45.7); vis(tvac, shots_of("s19"))
twf, _ = text3d("t_wafer", "chip wafer", PTS[-1] + Vector((0.3, -0.9, 1.4)), size=0.25, es=2.5, rot=(D(80), 0, D(25)))
pop_in(twf, C.EV["wafer"] + 0.2); vis(twf, shots_of("s19"))
# D7 hero mirror on a precision mount
hm = prim("cyl", "hero_mirror", loc=Lb + Vector((130.0, 0, BT + 1.6)), rot=(D(90), 0, 0), vertices=128, radius=1.25, depth=0.22); setmat(hm, mir_m)
bvh = hm.modifiers.new("bev", "BEVEL"); bvh.width = 0.03; bvh.segments = 4
hmb = prim("cyl", "hero_back", loc=Lb + Vector((130.0, 0.25, BT + 1.6)), rot=(D(90), 0, 0), vertices=128, radius=1.32, depth=0.3); setmat(hmb, mat("ule_glass", (0.25, 0.2, 0.18), 0.35, 0.0))
for k in range(6):
    a2 = k / 6 * 2 * math.pi
    act = prim("cyl", "actuator%d" % k, loc=Lb + Vector((130.0 + 1.45 * math.cos(a2), 0.3, BT + 1.6 + 1.45 * math.sin(a2))), rot=(D(90), 0, 0), vertices=24, radius=0.08, depth=0.6); setmat(act, steel)
hring = prim("torus", "hero_ring", loc=Lb + Vector((130.0, 0.25, BT + 1.6)), rot=(D(90), 0, 0), major_radius=1.48, minor_radius=0.07, major_segments=96, minor_segments=10); setmat(hring, steel_dk)
hpost = prim("cube", "hero_post", loc=Lb + Vector((130.0, 0.3, BT + 0.1)), scale=(0.25, 0.25, 0.3), smooth=False); setmat(hpost, steel_dk)
hk = area("hero_key", Lb + Vector((126.0, -5.0, 5.0)), (0, 0, 0), 900.0, 2.0, (1.0, 0.95, 0.9)); aim(hk, Lb + Vector((130.0, 0, 1.6)))

# ================================================================ SET E: Germany mirror
gpts = json.load(open(os.path.join(HERE, "germany_km.json")))
bm = bmesh.new()
vs = [bm.verts.new((x / 10.0, y / 10.0, 0.0)) for x, y in gpts[:-1] if True]
try:
    f_ = bm.faces.new(vs)
    ex = bmesh.ops.extrude_face_region(bm, geom=[f_])
    top = [e for e in ex["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, 1.2))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
except Exception as e:
    NOTES.append("germany mesh " + str(e)[:50])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
ger = new_mesh_obj("germany", bm); ger.location = G
gbv = ger.modifiers.new("bev", "BEVEL"); gbv.width = 0.25; gbv.segments = 3; gbv.limit_method = "ANGLE"
ger_m = mat("germany_m", (0.92, 0.93, 0.95), 0.015, 1.0, film=300.0, film_ior=1.5)
setmat(ger, ger_m)
sky_dome("sky_ger", G, 160.0)
gk = area("ger_key", G + Vector((-40, -60, 80)), (0, 0, 0), 60000.0, 60.0, (1.0, 0.95, 0.9)); aim(gk, G)
# faint neighbours grid on a dark plane below
sea_m = mat("sea_m", (0.01, 0.012, 0.018), 0.4, 0.0)
sea = prim("plane", "ger_ground", loc=G + Vector((0, 0, -0.4)), size=600); setmat(sea, sea_m)
tger, _ = text3d("t_ger", "GERMANY  ·  ~850 km", G + Vector((0, -50.0, 3.0)), size=4.5, es=2.5, rot=(D(60), 0, 0))
pop_in(tger, 52.0); vis(tger, shots_of("s21"))
# surface macro (s22): mirror patch with one tiny bump and a sheet of paper for scale
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=220, y_segments=220, size=6.0)
for v in bm.verts:
    r2 = (v.co.x - 0.2) ** 2 + (v.co.y - 0.0) ** 2
    v.co.z = 0.22 * math.exp(-r2 / 0.18)
patch = new_mesh_obj("mirror_patch", bm); patch.location = G2
for p_ in patch.data.polygons: p_.use_smooth = True
setmat(patch, ger_m)
paper = prim("cube", "paper", loc=G2 + Vector((1.9, -0.6, 0.11)), rot=(0, 0, D(14)), scale=(1.2, 1.6, 0.11), smooth=False)
setmat(paper, mat("paper_m", (0.92, 0.92, 0.9), 0.85, 0.0))
tmm, _ = text3d("t_mm", "0.1 mm", G2 + Vector((0.2, 0.0, 0.85)), size=0.28, es=4.0, rot=(D(80), 0, D(-35)))
tpp, _ = text3d("t_pp", "≈ one sheet of paper", G2 + Vector((1.9, -0.6, 0.55)), size=0.14, es=2.5, rot=(D(80), 0, D(-35)))
pop_in(tmm, C.EV["mm_text"]); pop_in(tpp, C.EV["mm_text"] + 0.5)
for o_ in (tmm, tpp): vis(o_, shots_of("s22"))
arrow_m, _ = emat("arrow_m", (1, 1, 1), 3.0, solid=True)
ar = prim("cyl", "bump_marker", loc=G2 + Vector((0.2, 0, 0.5)), vertices=12, radius=0.008, depth=0.5); setmat(ar, arrow_m)
vis(ar, shots_of("s22")); pop_in(ar, C.EV["mm_text"] - 0.1)
sky_dome("sky_g2", G2, 25.0)
g2k = area("g2_key", G2 + Vector((-3, -4, 4)), (0, 0, 0), 600.0, 3.0, (1.0, 0.95, 0.9)); aim(g2k, G2)

# ================================================================ cameras
cams = {}
for sid, t0, t1, st, keys, ex in C.SHOTS:
    org = Vector(C.SETS[st])
    cd = bpy.data.cameras.new("cam_" + sid); cd.sensor_width = 36.0; cd.clip_start = 0.01 if ex.get("macro") else 0.05; cd.clip_end = 2000
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
    m_ = sc.timeline_markers.new(sid, frame=F(t0)); m_.camera = co
sc.camera = cams["s01"]

# compositor bloom
def setup_glare():
    try:
        tree = bpy.data.node_groups.new("EUVComp", "CompositorNodeTree")
        sc.compositing_node_group = tree
        rl = tree.nodes.new("CompositorNodeRLayers")
        gl = tree.nodes.new("CompositorNodeGlare")
        try: gl.glare_type = "BLOOM"
        except Exception:
            s_ = sock(gl, "Type")
            if s_ is not None: s_.default_value = "Bloom"
        for nm, v in (("Threshold", 0.9), ("Strength", 0.55), ("Size", 0.7)):
            c_ = sock(gl, nm)
            if c_ is not None and getattr(c_, "type", "") == "VALUE": c_.default_value = v
        try: tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        except Exception: pass
        go = tree.nodes.new("NodeGroupOutput")
        tree.links.new(rl.outputs["Image"], gl.inputs["Image"]); tree.links.new(gl.outputs["Image"], go.inputs[0])
        sc.render.use_compositing = True
        NOTES.append("glare ok")
    except Exception as e:
        NOTES.append("glare fail " + type(e).__name__ + str(e)[:60])
setup_glare()

# ================================================================ save
PREFS.keyframe_new_interpolation_type = "BEZIER"
info = {"notes": NOTES, "assets": INFO_ASSETS, "phone": INFO_PHONE, "font": FONT.name if FONT else None, "build_s": round(time.time() - T0, 1)}
json.dump(info, open(os.path.join(HERE, "build_info.json"), "w"), indent=1, default=str)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "euv.blend"))
print("EUV SAVED", json.dumps(info, default=str)[:3000])
