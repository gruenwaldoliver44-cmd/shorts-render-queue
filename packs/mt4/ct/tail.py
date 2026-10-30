# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); link(cam); sc.camera = cam
tg = empty('camtgt', (0, 0, 1))
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.clip_start = 0.005
D = DC; C = CX; TRC = anchors['trace'].location.copy()
SHOTS = [
 (0.0, 2.2, D + V((0.10, -0.20, -0.30)), D, 30, D + V((0.18, -0.42, -0.62)), D + V((0, 0, -0.08)), 30),
 (2.2, 5.25, V((-1.7, KY - 3.3, 1.05)), V((0.15, KY - 0.8, 1.75)), 22, V((-1.45, KY - 3.0, 1.0)), V((0.2, KY - 0.85, 1.8)), 23),
 (5.25, 7.9, D + V((0.02, -0.13, -0.17)), D, 45, D + V((0.01, -0.05, -0.065)), D, 50),
 (7.9, 11.8, C + V((0.25, -2.4, 1.35)), C + V((0, 0, 0.25)), 32, C + V((0.08, -1.35, 0.62)), C + V((0, 0, 0.2)), 38),
 (11.8, 15.2, C + V((-0.7, -1.15, 0.38)), C + V((0, 0, 0.3)), 38, C + V((-0.5, -0.95, 0.32)), C + V((0, 0, 0.3)), 40),
 (15.2, 20.1, C + V((0.75, -2.3, 1.0)), C + V((0.2, 0, 0.25)), 30, C + V((0.55, -1.9, 0.75)), C + V((0.15, 0, 0.25)), 32),
 (20.1, 23.2, C + V((-1.3, -1.7, 0.62)), C + V((-0.2, 0, 0.32)), 32, C + V((-0.85, -1.35, 0.5)), C + V((-0.1, 0, 0.32)), 34),
 (23.2, 24.35, TRC + V((0.35, -1.0, 0.45)), TRC, 45, TRC + V((0.3, -0.85, 0.38)), TRC, 48),
 (24.35, 26.0, D + V((-0.55, -1.0, -0.75)), D + V((0, 0, -0.1)), 32, D + V((-0.42, -0.8, -0.6)), D + V((0, 0, -0.08)), 34),
 (26.0, DUR, C + V((0.05, -0.75, 0.55)), AMC, 45, C + V((0.02, -0.42, 0.34)), AMC, 55),
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
cd.dof.use_dof = True; cd.dof.focus_object = tg; cd.dof.aperture_fstop = 4.0
bpy.ops.wm.save_as_mainfile(filepath=ROOT + '/ct/scene.blend')
from bpy_extras.object_utils import world_to_camera_view
proj = {}
for fr in range(sc.frame_start, sc.frame_end + 1):
    sc.frame_set(fr)
    proj[fr] = {n: [round(c.x, 4), round(1 - c.y, 4), round(c.z, 3)] for n, e in anchors.items() for c in [world_to_camera_view(sc, cam, e.matrix_world.translation)]}
json.dump(proj, open(ROOT + '/ct/proj.json', 'w'))
print('SCENE OK', sc.frame_end, 'H', round(H, 3), 'KY', round(KY, 3))
