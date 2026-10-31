import bpy, sys, os, math
argv = sys.argv[sys.argv.index('--') + 1:]
out = argv[0]; times = [float(x) for x in argv[1].split(',')]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
pr = bpy.context.preferences.addons['cycles'].preferences
try:
    if os.environ.get('CPU_ONLY'): raise Exception('cpu only')
    pr.compute_device_type = 'METAL'; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = 'GPU'
except Exception as e: print('gpu', e)
sc.cycles.samples = 32; sc.render.resolution_percentage = 45
sc.render.image_settings.file_format = 'JPEG'
for t in times:
    f = int(round(t * 24)) + 1; sc.frame_set(f)
    sc.render.filepath = '%s/t%05.1f.jpg' % (out, t); bpy.ops.render.render(write_still=True)
import time
if os.environ.get('EEVEE_TOO'):
    t0 = time.time()
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try: sc.render.engine = eng; break
        except Exception: pass
    sc.render.resolution_percentage = 100
    for t in times[:4]:
        f = int(round(t * 24)) + 1; sc.frame_set(f)
        sc.render.filepath = '%s/ev%05.1f.jpg' % (out, t); bpy.ops.render.render(write_still=True)
    print('EEVEE_SEC_PER_FRAME', round((time.time() - t0) / 4, 1))
print('STILLS OK')
