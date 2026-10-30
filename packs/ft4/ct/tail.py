# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); link(cam); sc.camera = cam
tg = empty('camtgt', (0, 0, 1))
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.clip_end = 6000; cd.clip_start = 0.01
A = V((0, 0, 0)); R = AR; CR = SCP; B = anchors['bars'].location.copy(); RG = RC.copy()
TOE = (EC - A).normalized()
def cp(tt): return SCP + V((0, -40 + 40 * min(max((tt - 13.0) / 5.7, 0), 1), 0))
SHOTS = [
 (0.0, 1.44, A + V((-R * 1.6, -R * 2.2, R * 0.4)), A, 32, A + V((-R * 1.4, -R * 1.9, R * 0.35)), A, 33),
 (1.44, 5.18, A - TOE * R * 3.2 + V((R * 0.5, 0, R * 0.6)), A + TOE * R * 4, 28, A - TOE * R * 2.6 + V((R * 0.7, 0, R * 0.5)), A + TOE * R * 4, 30),
 (5.18, 8.14, A + V((R * 0.15, -R * 0.95, R * 0.35)), A + V((R * 0.3, 0, 0)), 32, A + V((-R * 0.2, -R * 0.85, R * 0.3)), A + V((-R * 0.2, 0, 0)), 32),
 (8.14, 13.42, A + V((R * 2.2, -R * 2.0, -R * 0.4)), A, 30, A + V((R * 2.5, -R * 1.2, -R * 0.2)), A, 30),
 (13.42, 16.86, cp(13.42) + V((7, -6, 2.5)), cp(13.42), 30, cp(16.86) + V((5.5, -4.5, 2.0)), cp(16.86), 32),
 (16.86, 18.72, cp(16.86) + V((-4, -10, 2.8)), A, 30, cp(18.72) + V((-3.5, -8.5, 2.4)), A, 30),
 (18.72, 21.82, A + V((-R * 0.9, -R * 1.3, -R * 0.5)), A, 34, A + V((-R * 0.7, -R * 1.05, -R * 0.4)), A, 36),
 (21.82, 24.46, A - TOE * R * 1.8 + V((R * 0.4, 0, R * 0.4)), A + TOE * 600, 30, A - TOE * R * 1.4 + V((R * 0.5, 0, R * 0.35)), A + TOE * 600, 32),
 (24.46, 26.36, B + V((0.6, -1.2, 0.55)), B + V((0, 0, 0.0)), 38, B + V((0.45, -0.95, 0.45)), B, 40),
 (26.36, 28.7, RG + V((0.12, -0.25, 0.09)), RG, 70, RG + V((0.09, -0.2, 0.07)), RG, 75),
 (28.7, DUR, B + V((-0.5, -0.9, 0.35)), B + V((-0.1, 0, 0)), 42, B + V((-0.35, -0.7, 0.3)), B + V((-0.1, 0, 0)), 44),
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
print('SCENE OK', sc.frame_end, 'AR', round(AR, 2))
