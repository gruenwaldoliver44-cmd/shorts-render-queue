# Blender -b euv.blend -P euv_render.py -- render S E [pct]  |  stills pct f1,f2,...
import bpy, os, sys, time
argv = sys.argv[sys.argv.index("--") + 1:]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import esp_common as C
sc = bpy.context.scene
ims = sc.render.image_settings
try: ims.media_type = "IMAGE"
except Exception: pass
ims.file_format = "JPEG"; ims.quality = 93
def render_frame(f, path):
    s = C.shot_at((f - 1) / C.FPS)
    sc.camera = bpy.data.objects["cam_" + s[0]]
    sc.frame_set(f)
    sc.render.filepath = path
    t = time.time(); bpy.ops.render.render(write_still=True)
    print("FRAME %d %s %.1fs" % (f, s[0], time.time() - t), flush=True)
mode = argv[0]
if mode == "render":
    S, E = int(argv[1]), int(argv[2]); pct = int(argv[3]) if len(argv) > 3 else 100
    sc.render.resolution_percentage = pct
    os.makedirs(os.path.join(HERE, "r"), exist_ok=True)
    for f in range(S, E + 1):
        p = os.path.join(HERE, "r", "f%04d.jpg" % f)
        if os.path.exists(p) and os.path.getsize(p) > 1000: continue
        render_frame(f, p)
elif mode == "stills":
    pct = int(argv[1]); frames = [int(x) for x in argv[2].split(",")]
    sc.render.resolution_percentage = pct
    os.makedirs(os.path.join(HERE, "s"), exist_ok=True)
    for f in frames: render_frame(f, os.path.join(HERE, "s", "f%04d.jpg" % f))
