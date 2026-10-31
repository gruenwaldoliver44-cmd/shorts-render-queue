# ---------- camera ----------
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); link(cam); sc.camera = cam
tg = empty('camtgt', (0, 0, 1))
tc = cam.constraints.new('TRACK_TO'); tc.target = tg; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.clip_end = 3000
S0 = SHIP0; Y = SD
SC = V((0, 0, DECK_Z + 8))
G = anchors['gavel'].location.copy(); HCt = HC.copy()
FLG = V((0, STERN_Y - SD * 1.85, DECK_Z + 5.6)); PILE = DT + V((0.75, 0.05, 0.12))
SHOTS = [
 (0.0, 1.36, V((-38, Y * 25, 1.2)), V((0, -Y * 30, DECK_Z + 10)), 30, V((-36, Y * 22, 1.4)), V((0, -Y * 12, DECK_Z + 10)), 32),
 (1.36, 3.84, V((-85, -Y * 40, 42)), V((0, -Y * 6, DECK_Z)), 30, V((-80, -Y * 25, 36)), V((0, 0, DECK_Z)), 32),
 (3.84, 5.36, V((-30, BOL[1].y - Y * 18, 2.5)), BOL[1] + V((-4, 0, 3.5)), 32, V((-27, BOL[1].y - Y * 15, 2.6)), BOL[1] + V((-4, 0, 3.5)), 34),
 (5.36, 7.68, FLG + V((-16, -Y * 4, -0.5)), FLG, 50, FLG + V((-13, -Y * 3, -0.3)), FLG, 55),
 (7.68, 10.6, HCt + V((0.8, -1.6, 0.7)), HCt + V((0, 0.2, -0.05)), 32, HCt + V((0.5, -1.3, 0.5)), HCt + V((0, 0.2, -0.05)), 34),
 (10.6, 13.6, HCt + V((-0.15, -1.6, 0.9)), HCt + V((-0.1, 0.25, -0.1)), 30, HCt + V((-0.1, -1.4, 0.8)), HCt + V((-0.05, 0.25, -0.1)), 31),
 (13.6, 14.7, HCt + V((0.5, -1.0, 0.25)), HCt, 45, HCt + V((0.4, -0.8, 0.2)), HCt, 50),
 (14.7, 17.0, G + V((0.75, -1.3, 0.5)), G + V((-0.3, 0.1, 0.12)), 35, G + V((0.65, -1.15, 0.45)), G + V((-0.3, 0.1, 0.12)), 36),
 (17.0, 19.2, V((-60, Y * 50, 14)), V((0, 0, DECK_Z + 6)), 32, V((-55, Y * 35, 10)), V((0, 0, DECK_Z + 6)), 34),
 (19.2, 20.25, G + V((-0.7, -1.1, 0.45)), G + V((-0.2, 0.1, 0.12)), 38, G + V((-0.65, -1.0, 0.42)), G + V((-0.2, 0.1, 0.12)), 39),
 (20.25, 21.5, V((-45, -Y * 15, 6)), V((0, Y * 10, DECK_Z + 6)), 30, V((-42, -Y * 10, 6)), V((0, Y * 20, DECK_Z + 6)), 30),
 (21.5, 24.4, PILE + V((-0.35, -0.95, 0.55)), PILE + V((-0.3, 0, 0.05)), 36, PILE + V((-0.3, -0.85, 0.6)), PILE + V((-0.3, 0, 0.12)), 37),
 (24.4, 27.25, HCt + V((0.9, -1.5, 0.3)), HCt + V((0, 0, -0.05)), 40, HCt + V((0.6, -1.15, 0.25)), HCt + V((0, 0, 0)), 42),
 (27.25, DUR, HCt + V((0.4, -1.6, 0.6)), HCt + V((0, 0.4, 0.05)), 35, HCt + V((0.6, -2.6, 1.3)), HCt + V((0, 0.5, 0.0)), 30),
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
print('SCENE OK', sc.frame_end, 'HULL_X', round(HULL_X, 2), 'DECK_Z', round(DECK_Z, 2))
