import bpy, sys, os, math
argv = sys.argv[sys.argv.index('--') + 1:]
out = argv[0]; times = [float(x) for x in argv[1].split(',')]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
pr = bpy.context.preferences.addons['cycles'].preferences
try:
    pr.compute_device_type = 'METAL'; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = 'GPU'
except Exception as e: print('gpu', e)
sc.cycles.samples = 32; sc.render.resolution_percentage = 45
sc.render.image_settings.file_format = 'JPEG'
for t in times:
    f = int(round(t * 24)) + 1; sc.frame_set(f)
    sc.render.filepath = '%s/t%05.1f.jpg' % (out, t); bpy.ops.render.render(write_still=True)
# calibration: straight-on ortho view of the hero machine front and side
cam = sc.camera; cam.constraints.clear(); cd = cam.data; cd.type = 'ORTHO'; cd.ortho_scale = 2.3; cd.dof.use_dof = False
sc.frame_set(1)
cam.location = (0, -6, 1.0); cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.filepath = '%s/calib_front.jpg' % out; bpy.ops.render.render(write_still=True)
cam.location = (6, -0.4, 1.0); cam.rotation_euler = (math.radians(90), 0, math.radians(90))
sc.render.filepath = '%s/calib_side.jpg' % out; bpy.ops.render.render(write_still=True)
print('STILLS OK')
