# Machine Times: "Ship engine" (16:9, 25 fps, Blender 5.2 / Eevee). Build: Blender -b -P ship.py -- save
import bpy, bmesh, math, os, sys, json, uuid, random, time, urllib.request, urllib.parse
from mathutils import Vector, Matrix, Euler
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0] if argv else "save"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ship_common as C
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


# ---- ship additions
def strip_displacement():
    for m in bpy.data.materials:
        if not m.use_nodes or not m.node_tree: continue
        out = next((n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeOutputMaterial"), None)
        if out and out.inputs["Displacement"].is_linked:
            for l in list(out.inputs["Displacement"].links): m.node_tree.links.remove(l)

def ocean(name, loc, size=400.0, res=14, wave_scale=1.2, choppy=1.0, wind=18.0, time_keys=None):
    bpy.ops.mesh.primitive_plane_add(size=2, location=loc)
    o = bpy.context.object; o.name = name
    for c_ in list(o.users_collection): c_.objects.unlink(o)
    ROOT.objects.link(o)
    md = o.modifiers.new("Ocean", "OCEAN")
    md.geometry_mode = "GENERATE"; md.size = 1.0; md.spatial_size = int(size); md.repeat_x = 1; md.repeat_y = 1
    md.resolution = res; md.wave_scale = wave_scale; md.choppiness = choppy; md.wind_velocity = wind
    md.use_normals = True; md.use_foam = True; md.foam_layer_name = "foam"; md.foam_coverage = 0.0
    if time_keys:
        try: PREFS.keyframe_new_interpolation_type = "LINEAR"
        except Exception: pass
        for t, v in time_keys:
            md.time = v; md.keyframe_insert("time", frame=F(t))
    m = bpy.data.materials.new(name + "_m"); m.use_nodes = True
    nt_ = m.node_tree; b = nt_.nodes.get("Principled BSDF")
    SV(b, "Base Color", (0.004, 0.02, 0.03, 1)); SV(b, "Roughness", 0.03); SV(b, "IOR", 1.33)
    SV(b, "Transmission Weight", 0.0); SV(b, "Coat Weight", 0.0); SV(b, "Specular IOR Level", 0.6)
    at = nt_.nodes.new("ShaderNodeAttribute"); at.attribute_name = "foam"
    cr = nt_.nodes.new("ShaderNodeMapRange"); cr.inputs[1].default_value = 0.7; cr.inputs[2].default_value = 1.6
    nt_.links.new(at.outputs["Fac"], cr.inputs[0])
    mx = nt_.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    nt_.links.new(cr.outputs[0], sock(mx, "Factor_Float"))
    sock(mx, "A_Color").default_value = (0.004, 0.02, 0.03, 1); sock(mx, "B_Color").default_value = (0.75, 0.8, 0.82, 1)
    nt_.links.new(next(o_ for o_ in mx.outputs if o_.identifier == "Result_Color"), b.inputs["Base Color"])
    o.data.materials.append(m)
    return o


def all_fcurves(action):
    out = []
    try:
        for ly in action.layers:
            for st in ly.strips:
                for cb in st.channelbags: out.extend(cb.fcurves)
    except Exception: pass
    try: out.extend(action.fcurves)
    except Exception: pass
    return out
