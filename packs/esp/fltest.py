import bpy, json, os, sys, uuid, urllib.request, urllib.parse, math
from mathutils import Vector
HOME = os.environ.get("AGENT_HOME", os.path.expanduser("~/ShortsRenderAgent"))
ADIR = os.path.join(HOME, "assets"); os.makedirs(ADIR, exist_ok=True)
BK = json.load(open("bk.json"))
UA = {"User-Agent": "blenderkit/3.21.3 (Blender 5.2.3)", "accept": "application/json"}
KEY = ""
for n, ad in bpy.context.preferences.addons.items():
    if "blenderkit" in n.lower(): KEY = getattr(ad.preferences, "api_key", "") or ""
out = []
def fetch(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)
    os.replace(path + ".part", path)
def bk_file(key):
    aid, durl = BK[key]
    p = os.path.join(ADIR, "bk_" + aid + ".blend")
    if os.path.exists(p) and os.path.getsize(p) > 1000: return p
    h = dict(UA); h["Authorization"] = "Bearer " + KEY
    q = durl + "?" + urllib.parse.urlencode({"scene_uuid": str(uuid.uuid4())})
    fp = json.loads(urllib.request.urlopen(urllib.request.Request(q, headers=h), timeout=60).read().decode())["filePath"]
    fetch(fp, p); return p
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x = 640; sc.render.resolution_y = 480
sc.render.image_settings.file_format = "JPEG"
import bmesh, time
# ---- espresso pour: Mantaflow liquid test
D = math.radians
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.render.fps = 25
ee = sc.eevee
for a, v in (("taa_render_samples", 32), ("use_raytracing", True)):
    try: setattr(ee, a, v)
    except Exception: pass
try: ee.ray_tracing_options.resolution_scale = "1"
except Exception: pass
sc.view_settings.view_transform = "AgX"
def load(key, loc):
    try:
        p = bk_file(key)
        with bpy.data.libraries.load(p, link=False) as (df, dt):
            dt.objects = list(df.objects)
        objs = [o for o in dt.objects if o]
    except Exception as e:
        print("LOAD FALLBACK", key, e)
        if key == "portafilter":
            bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.025, location=(0, 0, 0.05)); a = bpy.context.object; a.name = "basket"
            bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.02, location=(0, 0, 0.03)); b = bpy.context.object; b.name = "spout"
            objs = [a, b]
        else:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.08, location=(0, 0, 0.04)); objs = [bpy.context.object]
        for o in objs:
            for c in list(o.users_collection): c.objects.unlink(o)
    root = bpy.data.objects.new("root_" + key, None); sc.collection.objects.link(root)
    for o in objs:
        sc.collection.objects.link(o)
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    return root, objs
def bbox(objs):
    mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
    for o in objs:
        if o.type != "MESH": continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    return mn, mx
log = {}
pr, pobjs = load("portafilter", (0, 0, 0))
pmn, pmx = bbox(pobjs)
bas = [o for o in pobjs if o.name.startswith("basket")]
bmn, bmx = bbox(bas)
bc = (bmn + bmx) / 2
# put basket centre over origin, spout bottom at z = 0.12
pr.location = Vector((-bc.x, -bc.y, 0.12 - pmn.z))
bpy.context.view_layer.update()
pmn, pmx = bbox(pobjs); bmn, bmx = bbox(bas)
spout_z = pmn.z
log["spout_z"] = spout_z; log["basket"] = [list(bmn), list(bmx)]
gl, gobjs = load("eglass", (0, 0, 0))
gmn, gmx = bbox(gobjs)
gl.location = Vector((-(gmn.x + gmx.x) / 2, -(gmn.y + gmx.y) / 2, -gmn.z))
bpy.context.view_layer.update()
gmn, gmx = bbox(gobjs); log["glass"] = [list(gmn), list(gmx)]
R = min(gmx.x - gmn.x, gmx.y - gmn.y) / 2
H = gmx.z - gmn.z
# hide the asset's own liquid layers (we simulate our own)
for o in gobjs:
    if o.type == "MESH":
        mats = [m.name.lower() for m in o.data.materials if m]
        log.setdefault("gmats", {})[o.name] = mats
        if any(k in " ".join(mats) for k in ("coffee", "crema", "liquid", "espresso", "foam")) or any(k in o.name.lower() for k in ("coffee", "liquid", "crema", "espresso")):
            o.hide_render = True; o.hide_viewport = True
# collision cup (inner wall of the glass)
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=R * 0.70, radius2=R * 0.80, depth=H * 0.92)
top = [f for f in bm.faces if f.normal.z > 0.9]
bmesh.ops.delete(bm, geom=top, context="FACES")
for v in bm.verts: v.co.z += H * 0.46 + H * 0.06
me = bpy.data.meshes.new("cupcol"); bm.to_mesh(me); col = bpy.data.objects.new("cupcol", me); sc.collection.objects.link(col)
sd = col.modifiers.new("s", "SOLIDIFY"); sd.thickness = 0.004; sd.offset = 1.0
col.hide_render = True
# domain
dz0, dz1 = -0.002, spout_z + 0.012
dom_me = bpy.data.meshes.new("dom")
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(dom_me)
dom = bpy.data.objects.new("domain", dom_me); sc.collection.objects.link(dom)
dom.location = (0, 0, (dz0 + dz1) / 2); dom.scale = (0.11, 0.11, dz1 - dz0)
bpy.context.view_layer.update()
md = dom.modifiers.new("Fluid", "FLUID"); md.fluid_type = "DOMAIN"
ds = md.domain_settings; ds.domain_type = "LIQUID"; ds.resolution_max = int(os.environ.get("RES", "160"))
ds.use_mesh = True; ds.mesh_scale = 2; ds.use_diffusion = True; ds.viscosity_base = 2.0; ds.viscosity_exponent = 6
ds.cache_type = "ALL"; ds.cache_frame_start = 1; ds.cache_frame_end = 90
ds.cache_directory = os.path.abspath("flcache")
try: ds.use_spray_particles = False
except Exception: pass
ds.time_scale = 0.6
# two inflows under the spouts
for i, dy in enumerate((-0.0085, 0.0085)):
    inm = bpy.data.meshes.new("in%d" % i); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.0018, radius2=0.0018, depth=0.004); bm.to_mesh(inm)
    io = bpy.data.objects.new("inflow%d" % i, inm); sc.collection.objects.link(io); io.location = (0, dy, spout_z - 0.004)
    m2 = io.modifiers.new("Fluid", "FLUID"); m2.fluid_type = "FLOW"
    fs = m2.flow_settings; fs.flow_type = "LIQUID"; fs.flow_behavior = "INFLOW"; fs.flow_source = "MESH"
    fs.use_initial_velocity = True; fs.velocity_coord = (0, 0, -0.25)
    fs.use_plane_init = False
    io.hide_render = True
    fs.use_inflow = True
    fs.keyframe_insert("use_inflow", frame=1); fs.use_inflow = True; fs.keyframe_insert("use_inflow", frame=70)
    fs.use_inflow = False; fs.keyframe_insert("use_inflow", frame=72)
m3 = col.modifiers.new("Fluid", "FLUID"); m3.fluid_type = "EFFECTOR"; m3.effector_settings.effector_type = "COLLISION"
t0 = time.time() if "time" in dir() else 0
import time as _t; t0 = _t.time()
bpy.context.view_layer.objects.active = dom
with bpy.context.temp_override(object=dom, active_object=dom):
    r = bpy.ops.fluid.bake_all()
log["bake"] = str(r); log["bake_s"] = round(_t.time() - t0, 1)
# espresso material on the domain mesh
m = bpy.data.materials.new("espresso"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.09, 0.035, 0.01, 1); b.inputs["Roughness"].default_value = 0.04
b.inputs["Transmission Weight"].default_value = 0.35; b.inputs["IOR"].default_value = 1.34
b.inputs["Subsurface Weight"].default_value = 0.3; b.inputs["Subsurface Radius"].default_value = (0.004, 0.0015, 0.0005)
b.inputs["Coat Weight"].default_value = 0.6
dom.data.materials.append(m)
# studio
if not sc.world: sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.012, 1); sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.4
fl = bpy.data.meshes.new("f"); fl.from_pydata([(-3, -3, 0), (3, -3, 0), (3, 3, 0), (-3, 3, 0)], [], [(0, 1, 2, 3)])
fo = bpy.data.objects.new("floor", fl); sc.collection.objects.link(fo)
fm = bpy.data.materials.new("fm"); fm.use_nodes = True; bb = fm.node_tree.nodes["Principled BSDF"]; bb.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1); bb.inputs["Roughness"].default_value = 0.2; fl.materials.append(fm)
def area(loc, tgt, e, s, col=(1, 1, 1)):
    ld = bpy.data.lights.new("a", "AREA"); ld.energy = e; ld.size = s; ld.color = col
    o = bpy.data.objects.new("a", ld); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
area((-0.35, -0.4, 0.4), (0, 0, 0.06), 18, 0.35, (1.0, 0.9, 0.8))
area((0.35, 0.35, 0.25), (0, 0, 0.08), 22, 0.25, (0.7, 0.85, 1.0))
area((0.0, 0.5, 0.1), (0, 0, 0.06), 10, 0.4)
cd = bpy.data.cameras.new("c"); cd.lens = 55; cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0
tg = bpy.data.objects.new("t", None); sc.collection.objects.link(tg); tg.location = (0, 0, spout_z * 0.55)
cd.dof.focus_object = tg
cam.location = (0.05, -0.30, spout_z * 0.75)
cam.rotation_euler = (tg.location - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.image_settings.file_format = "JPEG"
os.makedirs("fl", exist_ok=True)
for f in (12, 25, 40, 55, 70, 88):
    sc.frame_set(f); sc.render.filepath = os.path.abspath("fl/f%03d.jpg" % f); bpy.ops.render.render(write_still=True)
json.dump(log, open("fl.json", "w"), indent=1, default=str)
print("FLTEST DONE", json.dumps(log, default=str)[:800])
