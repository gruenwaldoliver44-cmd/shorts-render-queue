# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); link(cam); sc.camera = cam
tg = empty('camtgt', (0, 0, 1))
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.clip_end = 6000; cd.clip_start = 0.01
A = V((0, 0, 0)); R = AR; CR = SCP; B = anchors['bars'].location.copy(); RG = RC.copy()
TOE = (EC - A).normalized()
def cp(tt):
    if tt < 4.4: return SCP + V((0, -60, 0))
    if tt < 7.6: return SCP + V((0, -60 + 18 * (tt - 4.4) / 3.2, 0))
    if tt < 22.9: return SCP + V((0, -42 + 22 * (tt - 7.6) / 15.3, 0))
    return SCP + V((0, -20 + 20 * min((tt - 22.9) / 2.6, 1), 0))
SHOTS = [
 (0.0, 4.6, A + V((-R * 1.6, -R * 2.2, R * 0.4)), A, 32, A + V((-R * 1.3, -R * 1.8, R * 0.35)), A, 34),
 (4.6, 7.5, cp(4.6) + V((17, 24, 8)), cp(4.6), 35, cp(7.5) + V((14, 20, 6.5)), cp(7.5), 35),
 (7.5, 11.9, A + V((R * 0.15, -R * 0.95, R * 0.35)), A + V((R * 0.3, 0, 0)), 32, A + V((-R * 0.2, -R * 0.85, R * 0.3)), A + V((-R * 0.2, 0, 0)), 32),
 (11.9, 16.9, A + V((R * 2.2, -R * 2.0, -R * 0.4)), A, 30, A + V((R * 2.5, -R * 1.2, -R * 0.2)), A, 30),
 (16.9, 19.95, A - TOE * R * 1.8 + V((R * 0.4, 0, R * 0.4)), A + TOE * 600, 30, A - TOE * R * 1.4 + V((R * 0.5, 0, R * 0.35)), A + TOE * 600, 32),
 (19.95, 23.0, B + V((0.6, -1.2, 0.55)), B, 38, B + V((0.45, -0.95, 0.45)), B, 40),
 (23.0, 25.35, cp(23.0) + V((-6, -16, 5)), A, 45, cp(25.3) + V((-5, -13, 4)), A, 45),
 (25.35, 29.3, RG + V((0.12, -0.25, 0.09)), RG, 70, RG + V((0.09, -0.2, 0.07)), RG, 75),
 (29.3, DUR, B + V((-0.5, -0.9, 0.35)), B + V((-0.1, 0, 0)), 42, B + V((-0.35, -0.7, 0.3)), B + V((-0.1, 0, 0)), 44),
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
