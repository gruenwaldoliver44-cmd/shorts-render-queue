# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); link(cam); sc.camera = cam
tg = empty('camtgt', (0, 0, 1))
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24
FY = FRONT_Y; DZ = P['deck_z']; SZ = P['scr_z']; SX = P['scr_x']
PHC = Vector(anchors['phone'].location); BTN = Vector(btn.location); MON = Vector(anchors['money'].location)
GS = Vector(scr_g.location); CI = Vector(((cimn.x + cimx.x) / 2, (cimn.y + cimx.y) / 2, cimx.z))
V = Vector
SHOTS = [
 (0.0, 1.4, PHC + V((-0.22, -0.30, 0.16)), PHC, 70, PHC + V((-0.17, -0.24, 0.12)), PHC, 85),
 (1.4, 2.7, BTN + V((0.14, -0.26, 0.12)), BTN, 85, BTN + V((0.10, -0.20, 0.09)), BTN, 95),
 (2.7, 4.1, V((SX, FY - 1.25, SZ + 0.02)), V((SX, FY, SZ)), 50, V((SX, FY - 0.95, SZ)), V((SX, FY, SZ)), 50),
 (4.1, 5.6, PHC + V((-0.55, -0.6, 0.35)), PHC, 45, PHC + V((-0.45, -0.5, 0.3)), PHC, 50),
 (5.6, 9.7, CI + V((0.35, -0.45, 0.30)), CI, 40, CI + V((0.12, -0.22, 0.14)), CI, 45),
 (9.7, 14.2, V((SX + 0.05, FY - 1.15, SZ + 0.12)), V((SX, FY, SZ)), 32, V((SX + 0.03, FY - 0.85, SZ + 0.08)), V((SX, FY, SZ)), 38),
 (14.2, 19.8, GS + V((-0.5, -1.5, 0.05)), GS, 35, GS + V((-0.1, -0.85, 0.0)), GS, 45),
 (19.8, 22.6, (PHC + BTN) / 2 + V((0.02, -0.55, 0.33)), (PHC + BTN) / 2, 50, (PHC + BTN) / 2 + V((0.0, -0.45, 0.27)), (PHC + BTN) / 2, 55),
 (22.6, 26.2, V((0.35, -2.0, 3.2)), V((0, FY - 0.2, 1.0)), 24, V((0.2, -1.95, 3.2)), V((0, FY - 0.1, 1.1)), 28),
 (26.2, 29.4, MON + V((0.40, -0.55, 0.12)), MON, 55, MON + V((0.30, -0.42, 0.1)), MON, 60),
 (29.4, DUR, V((SX, FY - 1.9, SZ + 0.1)), V((SX, FY, SZ)), 32, V((SX, FY - 0.75, SZ)), V((SX, FY, SZ)), 50),
]
for (t0, t1, p0, g0, l0, p1, g1, l1) in SHOTS:
    f0, f1 = F(t0), F(t1) - 1
    for idb, prop, a, b in ((cam, 'location', p0, p1), (tg, 'location', g0, g1), (cd, 'lens', l0, l1)):
        setattr(idb, prop, a); idb.keyframe_insert(prop, frame=f0)
        setattr(idb, prop, b); idb.keyframe_insert(prop, frame=f1)
for idb in (cam, tg, cd):
    for fc in fcurves(idb):
        kps = sorted(fc.keyframe_points, key=lambda k: k.co.x)
        for i, kp in enumerate(kps):
            kp.interpolation = 'BEZIER' if i % 2 == 0 else 'CONSTANT'
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
cd.dof.use_dof = True; cd.dof.focus_object = tg; cd.dof.aperture_fstop = 2.2
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/ct/scene.blend')
from bpy_extras.object_utils import world_to_camera_view
proj = {}
for fr in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(fr)
    proj[fr] = {n: [round(c.x, 4), round(1 - c.y, 4), round(c.z, 3)] for n, e in anchors.items() for c in [world_to_camera_view(sc, cam, e.matrix_world.translation)]}
json.dump(proj, open(ROOT + '/ct/proj.json', 'w'))
print('SCENE OK', sc.frame_end, 'FRONT_Y', round(FRONT_Y, 3), 'hero', [round(v, 3) for v in hmn], [round(v, 3) for v in hmx])
