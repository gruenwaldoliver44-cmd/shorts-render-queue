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
import time
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc.render.resolution_x, sc.render.resolution_y = 960, 720
KEYS = os.environ.get("KEYS", "linea").split(",")
key0 = KEYS[0]
p = bk_file(key0)
with bpy.data.libraries.load(p, link=False) as (df, dt):
    dt.objects = list(df.objects)
objs = [o for o in dt.objects if o]
for o in objs: sc.collection.objects.link(o)
bpy.context.view_layer.update()
info = {"images": [], "mats": {}}
for im in bpy.data.images:
    info["images"].append([im.name, im.filepath, bool(im.packed_file), im.size[:], im.has_data])
for m in bpy.data.materials:
    if not m.use_nodes: continue
    disp = [n.bl_idname for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeDisplacement"]
    out = m.node_tree.nodes.get("Material Output")
    info["mats"][m.name] = {"disp": disp, "disp_linked": bool(out and out.inputs["Displacement"].is_linked), "method": getattr(m, "displacement_method", None)}
mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
for o in objs:
    if o.type != "MESH": continue
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
ctr = (mn + mx) / 2; size = max(mx - mn)
if not sc.world: sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.025, 1)
fl = bpy.data.meshes.new("f"); fl.from_pydata([(-5, -5, 0), (5, -5, 0), (5, 5, 0), (-5, 5, 0)], [], [(0, 1, 2, 3)])
fo = bpy.data.objects.new("floor", fl); sc.collection.objects.link(fo); fo.location.z = mn.z
fm = bpy.data.materials.new("fm"); fm.use_nodes = True; b = fm.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1); b.inputs["Roughness"].default_value = 0.2; fl.materials.append(fm)
def area(loc, e, s, col=(1, 1, 1)):
    ld = bpy.data.lights.new("a", "AREA"); ld.energy = e; ld.size = s; ld.color = col
    o = bpy.data.objects.new("a", ld); sc.collection.objects.link(o); o.location = ctr + Vector(loc)
    o.rotation_euler = (ctr - o.location).to_track_quat("-Z", "Y").to_euler()
k = size / 0.4
area((-0.6 * k, -0.8 * k, 0.7 * k), 60 * k * k, 0.6 * k, (1.0, 0.95, 0.9)); area((0.7 * k, 0.6 * k, 0.4 * k), 50 * k * k, 0.4 * k, (0.8, 0.9, 1.0)); area((0, 0.2 * k, 1.0 * k), 25 * k * k, 1.0 * k)
cd = bpy.data.cameras.new("c"); cd.lens = 50; cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = ctr + Vector((-0.45, -0.85, 0.35)) * (size / 0.4); cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
os.makedirs("ld", exist_ok=True)
sc.render.image_settings.file_format = "JPEG"
sc.render.engine = "BLENDER_EEVEE"; sc.render.filepath = os.path.abspath("ld/%s_eevee_orig.jpg" % key0); bpy.ops.render.render(write_still=True)
# variant: disconnect displacement
for m in bpy.data.materials:
    if m.use_nodes:
        out = m.node_tree.nodes.get("Material Output")
        if out and out.inputs["Displacement"].is_linked:
            for l in list(out.inputs["Displacement"].links): m.node_tree.links.remove(l)
sc.render.filepath = os.path.abspath("ld/%s_eevee_nodisp.jpg" % key0); bpy.ops.render.render(write_still=True)
sc.render.engine = "CYCLES"
try:
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "METAL"; cp.get_devices()
    for d in cp.devices: d.use = True
    sc.cycles.device = "GPU"
except Exception as e: print("GPU", e)
sc.cycles.samples = 128; sc.cycles.use_denoising = True
t = time.time(); sc.render.filepath = os.path.abspath("ld/%s_cycles.jpg" % key0); bpy.ops.render.render(write_still=True); info["cycles_s"] = round(time.time() - t, 1)
json.dump(info, open("ld_%s.json" % key0, "w"), indent=1, default=str)
print("LOOKDEV DONE")
