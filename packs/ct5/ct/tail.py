# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); link(cam); sc.camera = cam
tg = empty('camtgt', (0, 0, 1))
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.clip_start = 0.002
H_ = anchors['hero'].location.copy(); DP = anchors['disp'].location.copy()
DTc = anchors['dticket'].location.copy(); WN = anchors['win'].location.copy(); LT = anchors['latex'].location.copy(); PH = anchors['phone'].location.copy()
HT = tpos(hero, 0.5, 0.15); HB = tpos(hero, 0.5, 0.85)
SHOTS = [
 (0.0, 4.05, H_ + V((0.10, -0.30, 0.22)), H_ + V((0, 0.03, 0)), 38, H_ + V((0.06, -0.20, 0.15)), H_ + V((0, 0.03, 0)), 42),
 (4.05, 7.0, V((0.75, -1.15, 1.35)), V((0.15, 0.0, CT + 0.05)), 32, V((0.55, -0.95, 1.25)), V((0.25, 0.05, CT + 0.06)), 34),
 (7.0, 11.4, HT + V((0.0, -0.10, 0.13)), HT, 50, HB + V((0.0, -0.10, 0.13)), HB, 50),
 (11.4, 15.2, DTc + V((-0.25, -0.42, 0.42)), DTc + V((0, 0.02, 0)), 40, DTc + V((-0.12, -0.24, 0.26)), DTc, 45),
 (15.2, 18.1, WN + V((0.02, -0.07, 0.10)), WN, 55, WN + V((0.015, -0.05, 0.075)), WN, 60),
 (18.1, 20.2, LT + V((0.0, -0.08, 0.11)), LT, 50, LT + V((0.0, -0.06, 0.085)), LT, 52),
 (20.2, 22.55, V((-0.9, -1.6, 1.45)), V((0.1, 0.4, 1.0)), 24, V((-0.7, -1.4, 1.35)), V((0.1, 0.4, 1.0)), 26),
 (22.55, 24.5, PH + V((-0.3, -0.42, 0.16)), PH, 40, PH + V((-0.2, -0.3, 0.12)), PH, 45),
 (24.5, DUR, DP + V((0.0, -0.80, 0.22)), DP, 32, DP + V((0.0, -0.62, 0.18)), DP, 34),
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
cd.dof.use_dof = True; cd.dof.focus_object = tg; cd.dof.aperture_fstop = 5.6
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/ct/scene.blend')
from bpy_extras.object_utils import world_to_camera_view
proj = {}
for fr in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(fr)
    proj[fr] = {n: [round(c.x, 4), round(1 - c.y, 4), round(c.z, 3)] for n, e in anchors.items() for c in [world_to_camera_view(sc, cam, e.matrix_world.translation)]}
json.dump(proj, open(ROOT + '/ct/proj.json', 'w'))
print('SCENE OK', sc.frame_end)
