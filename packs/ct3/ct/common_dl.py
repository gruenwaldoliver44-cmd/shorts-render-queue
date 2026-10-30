# shared asset download/load helpers (Blender side)
import bpy, os, json, uuid, urllib.request, urllib.parse
from mathutils import Vector
HOME = os.environ.get("AGENT_HOME", os.path.expanduser("~/ShortsRenderAgent"))
ADIR = os.path.join(HOME, "assets"); os.makedirs(ADIR, exist_ok=True)
NOTES = []
UA = {"User-Agent": "blenderkit/3.21.3 (Blender 5.2.3)", "accept": "application/json"}
def get_key():
    for name, ad in bpy.context.preferences.addons.items():
        if "blenderkit" in name.lower():
            return getattr(ad.preferences, "api_key", "") or ""
    return ""
KEY = get_key()
BK = {
 "ps5": "db02d8c0-a830-420b-88e4-66691c4dbe22",
 "driver": "b5b42e02-55ec-4c10-83c2-949b6ddc9276",
 "letter": "94a3c5d4-ac58-40ca-96f5-1e34a068e133",
 "lift": "a4bc27c8-e733-4991-9c81-0db209e04532",
 "bmw": "b274e63e-5584-44a3-a3d2-d5dfbdb7f176",
 "chest": "c285f038-c887-41fb-b398-738e4a7b71eb",
 "pos": "0d4c9ec9-6ce7-4eb5-8df9-d5d380e80083",
 "counter": "e0bc979f-4c04-41de-b5b5-2fe8ae00334e",
 "oil": "62d3b0f3-b043-4f3a-a094-5bf282241d20",
 "table": "0d4010d7-daef-4b9a-b613-16a17e85b794",
 "stamp": "6e2e540f-5fb5-4975-83a4-57a79ee30095",
}
def bk_resolve(base):
    q = "https://www.blenderkit.com/api/v1/search/?" + urllib.parse.urlencode({"query": "asset_base_id:" + base})
    h = dict(UA)
    if KEY: h["Authorization"] = "Bearer " + KEY
    r = json.loads(urllib.request.urlopen(urllib.request.Request(q, headers=h), timeout=60).read().decode())["results"][0]
    return [f for f in r["files"] if f["fileType"] == "blend"][0]["downloadUrl"]
def fetch(url, path, headers=None, timeout=300):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA["User-Agent"]})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(path + ".part", "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)
    os.replace(path + ".part", path)

def bk_file(key):
    aid = BK[key]
    p = os.path.join(ADIR, "bk_" + aid + ".blend")
    if os.path.exists(p) and os.path.getsize(p) > 1000: return p
    errs = []
    try: durl = bk_resolve(aid)
    except Exception as e:
        NOTES.append("BK resolve " + key + " " + type(e).__name__); return None
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
def ph_tex(name, kind, res="1k"):
    ext = "jpg"
    p = os.path.join(ADIR, "ph_%s_%s_%s.jpg" % (name, kind, res))
    if not os.path.exists(p):
        try: fetch(PH + "Textures/jpg/%s/%s/%s_%s_%s.jpg" % (res, name, name, kind, res), p)
        except Exception as e:
            NOTES.append("PH " + name + kind); return None
    return p

def ph_hdri(name, res="2k"):
    p = os.path.join(ADIR, "ph_%s_%s.hdr" % (name, res))
    if not os.path.exists(p):
        try: fetch(PH + "HDRIs/hdr/%s/%s_%s.hdr" % (res, name, res), p)
        except Exception: NOTES.append("PH hdri " + name); return None
    return p

def load_objs(key, coll_name=None):
    """append all renderable objects of a Blendkit file into a new scene collection; returns (collection, objects, top-level objects)"""
    p = bk_file(key)
    if not p: return None
    with bpy.data.libraries.load(p, link=False) as (df, dt):
        dt.objects = list(df.objects)
    coll = bpy.data.collections.new(coll_name or ("BK_" + key))
    bpy.context.scene.collection.children.link(coll)
    objs = []
    for o in dt.objects:
        if o is None: continue
        if o.type in ("CAMERA", "LIGHT"): continue
        if o.hide_render and o.type != "ARMATURE": continue
        coll.objects.link(o); objs.append(o)
    names = set(o.name for o in objs)
    tops = [o for o in objs if o.parent is None or o.parent.name not in names]
    return coll, objs, tops

def bbox(objs):
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        if o.type != "MESH": continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector((min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)))
            mx = Vector((max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)))
    return mn, mx
