import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_dl import *
OUTD = sys.argv[sys.argv.index("--") + 1]; os.makedirs(OUTD, exist_ok=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 8
sc.cycles.device = "CPU"
lines = []
def W(*a): lines.append(" ".join(str(x) for x in a))
keys = list(BK.keys()); x0 = 0.0
for i, k in enumerate(keys):
    r = load_objs(k)
    if not r: W("FAIL", k); continue
    coll, objs, tops = r
    mn, mx = bbox(objs); d = mx - mn
    W("ASSET", k, "dims", tuple(round(v, 3) for v in d), "min", tuple(round(v, 3) for v in mn), "n_obj", len(objs), "tops", [t.name for t in tops][:12])
    for o in objs:
        if o.type == "MESH":
            W("  obj", o.name, "parent", o.parent.name if o.parent else "-", "mats", [m.name for m in o.data.materials if m][:4], "loc", tuple(round(v, 3) for v in o.matrix_world.translation), "dims", tuple(round(v, 3) for v in o.dimensions))
        elif o.type in ("EMPTY", "ARMATURE", "CURVE"):
            W("  ", o.type, o.name)
    s = 1.6 / max(d.x, d.y, d.z, 0.01)
    gx = i % 4; gy = i // 4
    root = bpy.data.objects.new("ROOT_" + k, None); coll.objects.link(root)
    for t in tops: t.parent = root; t.matrix_parent_inverse = root.matrix_world.inverted()
    c = (mn + mx) / 2
    root.scale = (s, s, s)
    root.location = Vector((gx * 2.2 - 3.3, 0, -gy * 2.2 + 2.2)) - Vector((c.x, c.y, c.z)) * s
W("NOTES", NOTES)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 9.5
cam.location = (0, -20, 0); cam.rotation_euler = (math.radians(90), 0, 0)
w = sc.world or bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
hd = ph_hdri("studio_small_09")
if hd:
    n = w.node_tree.nodes.new("ShaderNodeTexEnvironment"); n.image = bpy.data.images.load(hd)
    w.node_tree.links.new(n.outputs[0], w.node_tree.nodes["Background"].inputs[0])
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
open(os.path.join(OUTD, "info.txt"), "w").write("\n".join(lines))
sc.render.filepath = os.path.join(OUTD, "lineup.png")
try: bpy.ops.render.render(write_still=True)
except Exception as e: print("RENDER FAIL", e)
open(os.path.join(OUTD, "info.txt"), "w").write("\n".join(lines))
print("PROBE OK")
