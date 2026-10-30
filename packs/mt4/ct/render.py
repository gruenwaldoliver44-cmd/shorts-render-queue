import bpy, sys, os
argv = sys.argv[sys.argv.index('--') + 1:]
sc = bpy.context.scene
if argv[0] == 'frames':
    pr = bpy.context.preferences.addons['cycles'].preferences
    try:
        pr.compute_device_type = 'METAL'; pr.get_devices()
        for d in pr.devices: d.use = True
        sc.cycles.device = 'GPU'
    except Exception: pass
    out = argv[1]; frames = [int(x) for x in argv[2].split(',')]
    if len(argv) > 3: sc.cycles.samples = int(argv[3])
    if len(argv) > 4: sc.render.resolution_percentage = int(argv[4])
    os.makedirs(out, exist_ok=True)
    for f in frames:
        sc.frame_set(f); sc.render.filepath = '%s/f%04d.jpg' % (out, f)
        bpy.ops.render.render(write_still=True)
if argv[0] == 'mac':
    out, spp, a, b = argv[1], int(argv[2]), int(argv[3]), int(argv[4])
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = 'METAL'; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = 'GPU'; sc.cycles.samples = spp
    sc.render.resolution_x = 1080; sc.render.resolution_y = 1920; sc.render.resolution_percentage = 100
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45
    sc.frame_start = max(a, sc.frame_start); sc.frame_end = min(b, sc.frame_end)
    ims = sc.render.image_settings
    if hasattr(ims, 'media_type'): ims.media_type = 'VIDEO'
    ims.file_format = 'FFMPEG'
    ff = sc.render.ffmpeg; ff.format = 'MPEG4'; ff.codec = 'H264'
    try: ff.constant_rate_factor = 'PERC_LOSSLESS'
    except Exception: pass
    sc.render.filepath = out
    bpy.ops.render.render(animation=True)
