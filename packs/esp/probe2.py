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
sc.render.resolution_x = 560; sc.render.resolution_y = 420
os.makedirs("p2", exist_ok=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
if not sc.world: sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.025, 1)
def area(loc, tgt, e, s):
    ld = bpy.data.lights.new("a", "AREA"); ld.energy = e; ld.size = s
    o = bpy.data.objects.new("a", ld); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
info = {}
for key in ["linea", "hero", "cup", "retro", "portafilter"]:
    try:
        p = bk_file(key)
        for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
        with bpy.data.libraries.load(p, link=False) as (df, dt):
            dt.objects = list(df.objects)
        objs = [o for o in dt.objects if o]
        for o in objs: sc.collection.objects.link(o)
        bpy.context.view_layer.update()
        mats = {}
        for o in objs:
            if o.type != "MESH": continue
            for m in o.data.materials:
                if not m or m.name in mats: continue
                d = {"users": [], "method": getattr(m, "surface_render_method", None), "blend": getattr(m, "blend_method", None)}
                if m.use_nodes:
                    d["nodes"] = sorted({n.bl_idname for n in m.node_tree.nodes})
                    for n in m.node_tree.nodes:
                        if n.bl_idname == "ShaderNodeBsdfPrincipled":
                            g = lambda s: (n.inputs[s].default_value if not n.inputs[s].is_linked else "LINK")
                            def cv(v):
                                try: return [round(x, 2) for x in v]
                                except TypeError: return v if isinstance(v, str) else round(v, 2)
                            d["bsdf"] = {s: cv(g(s)) for s in ("Base Color", "Metallic", "Roughness", "Alpha", "Transmission Weight") if s in n.inputs}
                mats[m.name] = d
            for m in o.data.materials:
                if m and o.name not in mats[m.name]["users"]: mats[m.name]["users"].append(o.name)
        mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
        for o in objs:
            if o.type != "MESH": continue
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
        info[key] = {"mats": mats, "objs": [(o.name, o.type, o.parent.name if o.parent else None, [round(x, 3) for x in o.matrix_world.translation], [round(x, 3) for x in o.dimensions]) for o in objs]}
        ctr = (mn + mx) / 2; size = max(mx - mn)
        fl = bpy.data.meshes.new("f"); fl.from_pydata([(-5, -5, 0), (5, -5, 0), (5, 5, 0), (-5, 5, 0)], [], [(0, 1, 2, 3)])
        fo = bpy.data.objects.new("floor", fl); sc.collection.objects.link(fo); fo.location.z = mn.z
        fm = bpy.data.materials.new("fm"); fm.use_nodes = True; b = fm.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1); b.inputs["Roughness"].default_value = 0.15; fl.materials.append(fm)
        area(ctr + Vector((-size * 1.5, -size * 1.8, size * 2.0)), ctr, 300 * size * size * 10, size * 1.5)
        area(ctr + Vector((size * 2.0, size * 1.0, size * 1.2)), ctr, 200 * size * size * 10, size)
        area(ctr + Vector((0, size * 2.0, size * 1.5)), ctr, 200 * size * size * 10, size)
        cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
        for vi, dv in enumerate([(0, -1, 0.35), (1, 0, 0.35), (0, 1, 0.35), (-1, 0, 0.35)]):
            cam.location = ctr + Vector(dv).normalized() * size * 2.6
            cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.abspath("p2/%s_%d.jpg" % (key, vi)); bpy.ops.render.render(write_still=True)
    except Exception as e:
        info[key] = {"err": str(e)[:300]}
json.dump(info, open("probe2.json", "w"), indent=1)
print("PROBE2 DONE")
