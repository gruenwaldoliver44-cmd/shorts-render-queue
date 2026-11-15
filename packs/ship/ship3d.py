# Machine Times longform "Inside the 2,000-Ton Engine" - 3D shots, one Blender run per shot.
#   Blender -b -P ship3d.py -- SHOT MODE [PCT]
#   MODE: still (one frame at 40% of the shot -> st_SHOT.jpg) | render (all frames -> r_SHOT/f####.jpg, skips existing)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ship_head import *          # helpers, clears scene, base Eevee settings

SHOT = argv[0] if argv else "sea_track"
MODE = argv[1] if len(argv) > 1 else "still"
PCT = int(argv[2]) if len(argv) > 2 else 100

# ------------------------------------------------------------------ shot table
# set, duration (s), camera keys [(t, pos, target, lens)], extras
SH = {
 "port":       ("PORT", 8.02,  [(0, (-95, -150, 9), (10, 25, 22), 28), (8.02, (-55, -140, 11), (25, 25, 22), 28)], {}),
 "holo_reveal":("HOLO", 6.36,  [(0, (19, -15.5, 5), (0, 0, 9), 22), (6.36, (13, -14.5, 4.5), (-2, 0, 9.5), 22)], {}),
 "crank_a":    ("CRANK", 8.11, [(0, (0.55, -1.25, 0.32), (0, 0, 0.0), 45), (8.11, (0.25, -1.0, 0.22), (0, 0, 0.02), 45)], {}),
 "sea_title":  ("SEA", 4.64,   [(0, (430, -270, 150), (0, 0, 15), 35), (4.64, (390, -240, 128), (0, 0, 15), 35)], {}),
 "sea_track":  ("SEA", 8.92,   [(0, (170, -175, 38), (170, 0, 22), 35), (8.92, (-40, -175, 38), (-40, 0, 22), 35)], {}),
 "sea_bow":    ("SEA", 7.3,    [(0, (330, -70, 4), (185, 0, 14), 28), (7.3, (300, -58, 5), (185, 0, 16), 28)], {}),
 "holo_dive":  ("HOLO", 10.72, [(0, (14, -11, 24.5), (0, 0, 12), 22), (5.0, (12, -12, 15), (0, 0, 10), 22), (10.72, (17, -14.5, 3.5), (0, 0, 9), 22)], {}),
 "holo_orbit": ("HOLO", 10.95, [], {"orbit": (17, 6, 8, -75, -25)}),
 "holo_close": ("HOLO", 7.11,  [(0, (14, -4.6, 17.2), (-6, 0, 14.5), 22), (7.11, (-9, -4.6, 17.0), (-24, 0, 14), 22)], {}),
 "holo_shaft": ("HOLO", 6.68,  [(0, (-16, -1.9, 3.4), (-40, 0, 2.2), 24), (6.68, (-50, -1.9, 3.1), (-72, 0, 2.2), 24)], {}),
 "stern_prop": ("STERN", 8.42, [(0, (-19, -11, -1.5), (0, 0, 0), 26), (8.42, (-15, -12.5, -0.6), (0, 0, 0.3), 26)], {}),
 "crank_b":    ("CRANK", 3.01, [(0, (-0.6, -1.1, 0.45), (0, 0, 0.05), 40), (3.01, (-0.5, -1.0, 0.4), (0, 0, 0.05), 40)], {"air": 1}),
 "holo_eff":   ("HOLO", 7.22,  [(0, (22, -17, 3), (0, 0, 8), 20), (7.22, (20, -15.5, 12), (0, 0, 7), 20)], {}),
 "sea_top":    ("SEA", 11.45,  [(0, (80, 10, 430), (80, 0, 0), 28), (11.45, (-30, -10, 400), (-30, 0, 0), 28)], {"roll": 1}),
 "sea_wake":   ("SEA", 3.58,   [(0, (-430, 50, 70), (-120, 0, 12), 38), (3.58, (-410, 42, 66), (-120, 0, 12), 38)], {}),
 "sea_sunset": ("SEA", 8.2,    [(0, (-650, -320, 55), (0, 0, 20), 55), (8.2, (-610, -300, 50), (0, 0, 20), 55)], {"sunset": 1}),
 "stern_slow": ("STERN", 4.33, [(0, (-9, -6, 0.6), (0, 0, 0.3), 30), (4.33, (-8, -5.4, 0.5), (0, 0, 0.3), 30)], {}),
 "holo_end":   ("HOLO", 7.59,  [(0, (16, -14, 10), (0, 0, 9), 22), (7.59, (9, -9.5, 7.5), (0, 0, 9), 26)], {}),
 "sea_end":    ("SEA", 8.55,   [(0, (-900, 260, 95), (0, 0, 20), 45), (8.55, (-860, 245, 85), (0, 0, 20), 45)], {"sunset": 1}),
}
SET, DUR, CAMK, EX = SH[SHOT]
NFR = int(round(DUR * FPS))
sc.frame_start, sc.frame_end = 1, NFR
sc.render.resolution_percentage = PCT

# ------------------------------------------------------------------ world
def world(hdri=None, strength=1.0, cam_sees=True, back=(0.004, 0.005, 0.008), rot=0.0, vol=None):
    w = bpy.data.worlds.new("W_" + SET); sc.world = w; w.use_nodes = True
    nt = w.node_tree; N = nt.nodes; Lk = nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputWorld"); bg = N.new("ShaderNodeBackground"); SV(bg, "Strength", strength)
    p = ph_hdri(hdri) if hdri else None
    if p:
        env = N.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(p)
        tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); SV(mp, "Rotation", (0, 0, rot))
        Lk.new(tc.outputs["Generated"], mp.inputs["Vector"]); Lk.new(mp.outputs[0], env.inputs["Vector"])
        Lk.new(env.outputs["Color"], bg.inputs["Color"])
    else:
        SV(bg, "Color", (*back, 1))
    if cam_sees or not p:
        Lk.new(bg.outputs[0], out.inputs["Surface"])
    else:
        bk = N.new("ShaderNodeBackground"); SV(bk, "Color", (*back, 1))
        lp = N.new("ShaderNodeLightPath"); mx = N.new("ShaderNodeMixShader")
        Lk.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); Lk.new(bg.outputs[0], mx.inputs[1]); Lk.new(bk.outputs[0], mx.inputs[2])
        Lk.new(mx.outputs[0], out.inputs["Surface"])
    if vol:
        v = N.new("ShaderNodeVolumePrincipled"); SV(v, "Color", (*vol[0], 1)); SV(v, "Density", vol[1])
        SV(v, "Anisotropy", vol[2] if len(vol) > 2 else 0.3)
        Lk.new(v.outputs[0], out.inputs["Volume"])

def sun(rot, energy, col=(1, 0.97, 0.92), angle=1.0):
    ld = bpy.data.lights.new("sun", "SUN"); ld.energy = energy; ld.color = col; ld.angle = D(angle)
    o = link(bpy.data.objects.new("sun", ld)); o.rotation_euler = rot; return o

# ------------------------------------------------------------------ container ship (real scale, metres; bow +X, waterline z=0)
LOA, BEAM, DECK, DRAFT = 400.0, 61.0, 18.0, 15.0
def hull_halfwidth(x):
    if x > 120: return BEAM / 2 * max(0.0, 1 - ((x - 120) / 80.0) ** 1.8) ** 0.55
    if x < -170: return BEAM / 2 * (0.9 + 0.1 * (x + 200) / 30.0)
    return BEAM / 2
def hull_bottom(x):
    if x > 150: return -DRAFT + (x - 150) / 50.0 * 7.0
    if x < -160: return -DRAFT + ((-160 - x) / 40.0) ** 1.5 * 11.0
    return -DRAFT
def build_hull(name="hull", sections=110):
    bm = bmesh.new(); rings = []
    xs = [-200 + i * 400.0 / sections for i in range(sections + 1)]
    for x in xs:
        w = max(0.25, hull_halfwidth(x)); zb = hull_bottom(x); flare = 1.0 + (0.12 if x > 150 else 0.0)
        prof = [(-w * flare, DECK), (-w, 4), (-w, zb + 4), (-w * 0.75, zb + 0.3), (0, zb), (w * 0.75, zb + 0.3), (w, zb + 4), (w, 4), (w * flare, DECK)]
        rings.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for a, b in zip(rings, rings[1:]):
        for i in range(len(a) - 1):
            bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
    for r in (rings[0], rings[-1]):
        try: bm.faces.new(r)
        except Exception: pass
    # deck
    top = [r[0] for r in rings] + [r[-1] for r in reversed(rings)]
    try: bm.faces.new(top)
    except Exception: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_mesh_obj(name, bm)
    for p in o.data.polygons: p.use_smooth = True
    # paint: antifouling red below z=2, dark navy above, white boot-top stripe
    m = bpy.data.materials.new("hullpaint"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.32, 0.035, 0.03, 1)
    cr.elements[1].position = 1.0; cr.elements[1].color = (0.018, 0.03, 0.06, 1)
    e = cr.elements.new(0.48); e.color = (0.32, 0.035, 0.03, 1)
    e = cr.elements.new(0.50); e.color = (0.8, 0.8, 0.78, 1)
    e = cr.elements.new(0.53); e.color = (0.018, 0.03, 0.06, 1)
    mr = nt.nodes.new("ShaderNodeMapRange"); SV(mr, 1, -20.0); SV(mr, 2, 20.0)
    nt.links.new(sp.outputs["Z"], mr.inputs[0]); nt.links.new(mr.outputs[0], ramp.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise"); SV(nz, "Scale", 0.4); SV(nz, "Detail", 6)
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; SV(mix, "Factor_Float", 0.25)
    nt.links.new(ramp.outputs[0], sock(mix, "A_Color")); nt.links.new(nz.outputs["Color"], sock(mix, "B_Color"))
    nt.links.new(next(x for x in mix.outputs if x.identifier == "Result_Color"), b.inputs["Base Color"])
    SV(b, "Roughness", 0.55); SV(b, "Metallic", 0.2)
    setmat(o, m)
    return o

def box(name, loc, size, m):
    o = prim("cube", name, loc=loc, scale=(size[0] / 2, size[1] / 2, size[2] / 2), smooth=False); apply_scale(o); setmat(o, m); return o

def build_superstructure():
    white = mat("white", (0.78, 0.79, 0.8), 0.5); glass = mat("glass", (0.02, 0.025, 0.03), 0.08, metal=0.3)
    navy = mat("navy", (0.03, 0.05, 0.09), 0.45)
    # bridge / accommodation block (forward third, like modern ULCVs)
    bx = 95
    box("acc", (bx, 0, DECK + 22), (16, 38, 44), mat("accgrey", (0.62, 0.64, 0.66), 0.55))
    for k in range(9):
        for side in (-1, 1):
            box("winS%d_%d" % (k, side), (bx, side * 19.05, DECK + 6 + k * 4.4), (13, 0.2, 1.2), glass)
        box("winA%d" % k, (bx - 8.05, 0, DECK + 6 + k * 4.4), (0.2, 30, 1.2), glass)
    lash = mat("lash", (0.55, 0.55, 0.5), 0.6, metal=0.3)
    x = -180.0
    while x < 180:
        if abs(x - 95) > 14 and abs(x + 150) > 12:
            box("lashb%.0f" % x, (x, 0, DECK + 6), (0.6, BEAM - 6, 10), lash)
        x += 12.4
    box("bridge", (bx, 0, DECK + 46.5), (12, BEAM + 2, 5), white)
    box("bridgeglass", (bx + 6.05, 0, DECK + 46.8), (0.2, BEAM + 1.6, 2.2), glass)
    for k in range(9):
        box("winrow%d" % k, (bx + 8.05, 0, DECK + 6 + k * 4.4), (0.2, 30, 1.3), glass)
    box("mast", (bx, 0, DECK + 54), (1.2, 1.2, 12), white)
    # funnel aft
    box("funnel", (-150, 0, DECK + 16), (16, 18, 32), navy)
    box("funnelcap", (-150, 0, DECK + 32.5), (16.4, 18.4, 1.5), mat("black", (0.01, 0.01, 0.01), 0.6))
    # hatch covers
    hc = mat("hatch", (0.05, 0.12, 0.18), 0.6)
    box("hatches", (0, 0, DECK + 0.6), (370, BEAM - 4, 1.2), hc)

CRATE = None
def crate_mesh():
    """one 20' container mesh (BlenderKit 'Container Rusty'; self-built corrugated box if the download fails)."""
    global CRATE
    if CRATE: return CRATE
    r = load_asset("crate", 6.06, (0, 0, 0), axis="max")
    meshes = []
    if r:
        st = [r]
        while st:
            o = st.pop(); st.extend(o.children)
            if o.type == "MESH": meshes.append(o)
    if meshes:
        for o in bpy.context.selected_objects: o.select_set(False)
        for o in meshes:
            o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        for o in meshes:
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if len(meshes) > 1: bpy.ops.object.join()
        c = bpy.context.view_layer.objects.active
        mn, mx = bbox_of([c])
        # orient long side to X
        if (mx.y - mn.y) > (mx.x - mn.x):
            c.rotation_euler = (0, 0, D(90)); bpy.ops.object.transform_apply(rotation=True)
            mn, mx = bbox_of([c])
        c.data.transform(Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))))
        c.location = (0, 0, 0)
        sx = 6.06 / max(1e-6, mx.x - mn.x); sy = 2.44 / max(1e-6, mx.y - mn.y); sz = 2.59 / max(1e-6, mx.z - mn.z)
        c.scale = (sx, sy, sz); apply_scale(c)
        NOTES.append("crate asset ok")
    else:
        NOTES.append("crate fallback")
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(6.06, 2.44, 2.59), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0, 1.295), verts=bm.verts)
        c = new_mesh_obj("crate", bm); setmat(c, mat("crate_fb", (0.5, 0.2, 0.1), 0.6, metal=0.4))
    CRATE = c
    return c

PALETTE = [(0.0, 1.0), (0.58, 0.8), (0.62, 0.6), (0.33, 0.6), (0.1, 1.2), (0.0, 0.35), (0.5, 0.7), (0.0, 2.2), (0.15, 1.1), (0.7, 0.5)]
def tinted_crate(k):
    """copy of the crate with a hue/value-shifted material, for colour variety"""
    base = crate_mesh()
    c = base.copy(); c.data = base.data.copy(); link(c); c.name = "crate_v%d" % k
    c.hide_render = False; c.hide_viewport = False
    hue, val = PALETTE[k % len(PALETTE)]
    for i, ms in enumerate(c.data.materials):
        if ms is None or not ms.use_nodes: continue
        m2 = ms.copy(); c.data.materials[i] = m2
        b = next((n for n in m2.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
        if b is None: NOTES.append("tint: no principled in %s" % ms.name); continue
        src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].is_linked else None
        hs = m2.node_tree.nodes.new("ShaderNodeHueSaturation"); SV(hs, "Hue", (0.5 + hue) % 1.0); SV(hs, "Value", val); SV(hs, "Saturation", 0.75)
        if src: m2.node_tree.links.new(src, hs.inputs["Color"])
        else: SV(hs, "Color", (*b.inputs["Base Color"].default_value[:3], 1))
        m2.node_tree.links.new(hs.outputs[0], b.inputs["Base Color"])
    return c

def stacks(name, positions_by_variant, parent_loc=(0, 0, 0)):
    """dupliverts: one vertex-cloud parent per colour variant"""
    roots = []
    for k, pts in positions_by_variant.items():
        if not pts: continue
        me = bpy.data.meshes.new("%s_pts%d" % (name, k)); me.from_pydata(pts, [], []); me.update()
        par = link(bpy.data.objects.new("%s_par%d" % (name, k), me)); par.location = parent_loc
        par.instance_type = "VERTS"
        ch = tinted_crate(k); ch.parent = par; ch.location = (0, 0, 0)
        roots.append(par)
    base = crate_mesh(); base.hide_render = True; base.hide_viewport = True
    return roots

def ship_containers(rnd):
    pos = {k: [] for k in range(len(PALETTE))}
    z0 = DECK + 1.2
    x = -185.0
    while x < 188:
        if abs(x - 95) < 12 or abs(x + 150) < 11:
            x += 6.2; continue
        w = hull_halfwidth(x + 3) - 1.0
        rows = int((2 * w) // 2.48)
        tiers = rnd.choice([7, 8, 9, 9, 10, 10]) if x < 150 else rnd.choice([4, 5, 6])
        for r in range(rows):
            y = -rows * 2.48 / 2 + 1.24 + r * 2.48
            h = tiers - (1 if rnd.random() < 0.12 else 0) - (1 if abs(r - rows / 2) > rows / 2 - 1.5 and rnd.random() < 0.5 else 0)
            edge = r < 2 or r >= rows - 2 or x < -180 or x > 180 or abs(x - 95) < 19 or abs(x + 150) < 18 or rnd.random() < 0.08
            for t in range(h):
                if edge or t >= h - 2:
                    pos[rnd.randrange(len(PALETTE))].append((x + 3.03, y, z0 + t * 2.6))
        x += 6.2
    return stacks("ship", pos)

def build_ship():
    rnd = random.Random(11)
    hull = build_hull(); build_superstructure(); ship_containers(rnd)
    return hull

def foam_plane(name, loc, size, rot=(0, 0, 0), dens=0.5, speed=(0, 0), scale=0.08):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = (size[0], size[1], 1)
    m = bpy.data.materials.new(name + "_m"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); df = N.new("ShaderNodeBsdfDiffuse"); SV(df, "Color", (0.85, 0.88, 0.9, 1))
    tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader")
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping")
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    vor = N.new("ShaderNodeTexNoise"); SV(vor, "Scale", 1.0 / scale); SV(vor, "Detail", 8); SV(vor, "Roughness", 0.7)
    nt.links.new(mp.outputs[0], vor.inputs["Vector"])
    gr = N.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"; nt.links.new(tc.outputs["Object"], gr.inputs["Vector"])
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    mr = N.new("ShaderNodeMapRange"); SV(mr, 1, dens); SV(mr, 2, dens + 0.15)
    nt.links.new(vor.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], mul.inputs[0]); nt.links.new(gr.outputs["Fac"], mul.inputs[1])
    nt.links.new(mul.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(df.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    setattr_safe(m, "surface_render_method", "BLENDED"); setmat(o, m)
    loc0 = sock(mp, "Location")
    KV(loc0, 1, (0, 0, 0)); KV(loc0, NFR + 1, (-speed[0] * DUR / size[0], -speed[1] * DUR / size[1], 0))
    return o

def set_sea():
    sunset = EX.get("sunset")
    if sunset:
        hd = next((h for h in ("belfast_sunset_puresky", "qwantani_dusk_2_puresky", "kiara_1_dawn") if ph_hdri(h)), None)
        world(hd, 1.0, rot=D(120)); sun((D(84), 0, D(-60)), 2.5, (1.0, 0.62, 0.35), 0.8)
    else:
        world("kloofendal_48d_partly_cloudy_puresky", 1.0, rot=D(30)); sun((D(48), 0, D(-35)), 4.0)
    build_ship()
    V = 7.5   # m/s the water streams past the ship (ship appears to move +X)
    oc = ocean("ocean", (-1000, -1000, 0), size=1000, res=14, wave_scale=1.6, choppy=1.1, wind=14, time_keys=[(0, 0.0), (DUR, DUR)])
    oc.modifiers["Ocean"].repeat_x = 3; oc.modifiers["Ocean"].repeat_y = 3
    K(oc, "location", 1); oc.location = (-1000 - V * DUR, -1000, 0); K(oc, "location", NFR + 1)
    far = prim("plane", "farsea", loc=(0, 0, -0.6), scale=(15000, 15000, 1), smooth=False); setmat(far, oc.data.materials[0])
    # bow wave, hull-side foam and wake
    foam_plane("bowfoam", (200, 0, 0.3), (40, 70), dens=0.45, speed=(-V * 0.2, 0), scale=0.03)
    foam_plane("sidefoamL", (0, -BEAM / 2 - 3, 0.25), (420, 10), dens=0.55, speed=(-V, 0), scale=0.04)
    foam_plane("sidefoamR", (0, BEAM / 2 + 3, 0.25), (420, 10), dens=0.55, speed=(-V, 0), scale=0.04)
    foam_plane("wake", (-380, 0, 0.2), (380, 80), dens=0.5, speed=(-V, 0), scale=0.05)
    setattr_safe(sc.eevee, "volumetric_end", 2000.0)

# ------------------------------------------------------------------ port at night
def set_port():
    world("dikhololo_night", 0.25, rot=D(0), vol=((0.6, 0.65, 0.75), 0.0012, 0.4))
    gnd = prim("plane", "ground", loc=(0, -150, 0), scale=(400, 220, 1), smooth=False)
    nt_m = mat("asphalt", (0.025, 0.025, 0.028), 0.22); setmat(gnd, nt_m)
    quay = box("quay", (0, 40, -1), (900, 12, 4), mat("concrete", (0.25, 0.25, 0.24), 0.8))
    oc = ocean("water", (0, 300, -3), size=300, res=12, wave_scale=0.3, choppy=0.6, wind=6, time_keys=[(0, 0.0), (DUR, DUR)])
    # ship alongside, bow +X, side at y=+52
    hull = build_hull(); build_superstructure(); roots = ship_containers(random.Random(5))
    for o in [hull] + [x for x in bpy.data.objects if x.name.startswith(("acc", "bridge", "winrow", "mast", "funnel", "hatches"))] + roots:
        if o.parent is None: o.location.y += BEAM / 2 + 47; o.location.z -= 3
    # container yard: blocks of stacks
    rnd = random.Random(3); pos = {k: [] for k in range(len(PALETTE))}
    for bxk in range(-6, 6):
        for byk in range(5):
            x0 = bxk * 52; y0 = -40 - byk * 34
            for i in range(6):
                for j in range(7):
                    h = rnd.choice([2, 3, 4, 4, 5])
                    for t in range(h):
                        if not (i in (0, 5) or j in (0, 6) or t == h - 1): continue
                        pos[rnd.randrange(len(PALETTE))].append((x0 + i * 6.3, y0 + j * 2.6, t * 2.6))
    stacks("yard", pos)
    # gantry cranes over the yard
    for k, (cx, cy) in enumerate([(-30, -58), (75, -92), (-140, -126)]):
        r = load_asset("crane", 34.0, (cx, cy, 0), rot=(0, 0, D(90)), axis="z")
        if r is None: NOTES.append("crane missing")
    # floodlight masts
    for k in range(9):
        x = -200 + k * 50; y = -20 - (k % 3) * 70
        box("mast%d" % k, (x, y, 17), (0.8, 0.8, 34), mat("pole", (0.2, 0.2, 0.2), 0.5))
        head = box("lamp%d" % k, (x, y, 34.5), (4, 2, 1), emat("lamp", (1.0, 0.82, 0.55), 40, solid=True)[0])
        s = spot("spot%d" % k, (x, y, 33.5), (0, 0, 0), 900000, size_deg=110, blend=0.6, col=(1.0, 0.8, 0.55), radius=1.0)
    for k in range(5):
        point("glow%d" % k, (-150 + k * 80, 30, 25), 200000, (1.0, 0.75, 0.5), radius=2)

# ------------------------------------------------------------------ engine room (self-built: no marine engine exists on BlenderKit)
def cylu(name, loc, r, h, verts=32, rot=(0, 0, 0)):
    return prim("cyl", name, loc=loc, rot=rot, vertices=verts, radius=r, depth=h)
def cub(name, loc, size, rot=(0, 0, 0)):
    o = prim("cube", name, loc=loc, rot=rot, scale=(size[0] / 2, size[1] / 2, size[2] / 2), smooth=False); apply_scale(o); return o
def bevel(o, w=0.04, seg=2):
    md = o.modifiers.new("bv", "BEVEL"); md.width = w; md.segments = seg; md.limit_method = "ANGLE"
    try: o.data.shade_smooth_by_angle(angle=D(35))
    except Exception:
        for p in o.data.polygons: p.use_smooth = False
    return o

def paint(name, col, rough=0.5, metal=0.0, grime=0.35, scale=1.5):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    nz = nt.nodes.new("ShaderNodeTexNoise"); SV(nz, "Scale", scale); SV(nz, "Detail", 10); SV(nz, "Roughness", 0.65)
    mr = nt.nodes.new("ShaderNodeMapRange"); SV(mr, 1, 0.42); SV(mr, 2, 0.68); SV(mr, 3, 1.0); SV(mr, 4, 1.0 - grime)
    nt.links.new(nz.outputs["Fac"], mr.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; SV(mx, "Factor_Float", 1.0)
    sock(mx, "A_Color").default_value = (*col, 1)
    cmb = nt.nodes.new("ShaderNodeCombineColor"); nt.links.new(mr.outputs[0], cmb.inputs[0]); nt.links.new(mr.outputs[0], cmb.inputs[1]); nt.links.new(mr.outputs[0], cmb.inputs[2])
    nt.links.new(cmb.outputs[0], sock(mx, "B_Color"))
    nt.links.new(next(x for x in mx.outputs if x.identifier == "Result_Color"), b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); SV(rr, 3, rough * 0.7); SV(rr, 4, min(1.0, rough * 1.3))
    nt.links.new(nz.outputs["Fac"], rr.inputs[0]); nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    SV(b, "Metallic", metal)
    bm_ = nt.nodes.new("ShaderNodeBump"); SV(bm_, "Strength", 0.015); nt.links.new(nz.outputs["Fac"], bm_.inputs["Height"])
    nt.links.new(bm_.outputs[0], b.inputs["Normal"])
    MATS[name] = m
    return m

NCYL, PITCH = 12, 2.05
def build_engine():
    P = dict(eng=paint("engpaint", (0.30, 0.36, 0.36), 0.45), dark=paint("darksteel", (0.07, 0.075, 0.08), 0.35, metal=0.6),
             silver=paint("insul", (0.62, 0.63, 0.64), 0.3, metal=0.9, grime=0.2, scale=6), yellow=paint("railyel", (0.85, 0.6, 0.05), 0.45),
             blue=paint("pipeblue", (0.08, 0.22, 0.45), 0.4), green=paint("pipegrn", (0.12, 0.35, 0.18), 0.4), red=paint("pipered", (0.5, 0.06, 0.04), 0.4),
             floor=paint("floorpl", (0.12, 0.12, 0.13), 0.35, metal=0.7, grime=0.5, scale=3), wall=paint("wallp", (0.2, 0.24, 0.26), 0.6, grime=0.45))
    xs = [(i - (NCYL - 1) / 2) * PITCH for i in range(NCYL)]
    L = NCYL * PITCH + 2.4
    bevel(setmat(cub("bedplate", (0, 0, 1.3), (L + 1, 6.6, 2.6)), P["eng"]), 0.06)
    bevel(setmat(cub("frame", (0, 0, 5.4), (L, 5.4, 5.6)), P["eng"]), 0.06)
    bevel(setmat(cub("cylframe", (0, 0, 10.4), (L, 4.4, 4.4)), P["eng"]), 0.06)
    bevel(setmat(cub("scav", (0, 3.0, 10.0), (L, 1.6, 2.6)), P["eng"]), 0.08)
    ex = setmat(cylu("exhrec", (0, -3.0, 15.2), 1.15, L, rot=(0, D(90), 0)), P["silver"])
    for k, x in enumerate((-8.5, 0.5, 9.5)):
        setmat(cylu("turbo%d" % k, (x, -5.6, 13.0), 1.45, 2.8, rot=(D(90), 0, 0)), P["silver"])
        setmat(cylu("turbocone%d" % k, (x, -7.3, 13.0), 0.9, 0.8, rot=(D(90), 0, 0)), P["dark"])
        bevel(setmat(cub("cooler%d" % k, (x, -5.6, 9.6), (2.6, 2.2, 3.6)), P["dark"]), 0.05)
        for fz in range(8): setmat(cub("fin%d_%d" % (k, fz), (x, -6.72, 8.1 + fz * 0.42), (2.4, 0.06, 0.12)), P["silver"])
        setmat(cylu("tdown%d" % k, (x, -4.4, 14.2), 0.45, 1.6), P["silver"])
    for i, x in enumerate(xs):
        # crankcase doors with bolts
        d = bevel(setmat(cub("door%d" % i, (x, -2.74, 4.6), (1.25, 0.1, 1.6)), P["eng"]), 0.03)
        for bx in (-0.5, 0.5):
            for bz in (-0.65, 0.65):
                setmat(cylu("bolt%d_%.1f_%.1f" % (i, bx, bz), (x + bx, -2.8, 4.6 + bz), 0.04, 0.05, verts=8, rot=(D(90), 0, 0)), P["dark"])
        setmat(cub("lbl%d" % i, (x, -2.77, 6.1), (0.5, 0.02, 0.25)), mat("lblplate", (0.75, 0.75, 0.7), 0.4))
        # cylinder cover, studs, exhaust valve, pipes
        cv = setmat(cylu("cover%d" % i, (x, 0, 13.0), 0.85, 0.7), P["dark"])
        for a in range(8):
            th = a * math.pi / 4
            setmat(cylu("stud%d_%d" % (i, a), (x + 0.7 * math.cos(th), 0.7 * math.sin(th), 13.45), 0.06, 0.25, verts=8), P["silver"])
        setmat(cylu("valve%d" % i, (x, 0, 14.1), 0.38, 1.5), P["eng"])
        setmat(cylu("vtop%d" % i, (x, 0, 14.95), 0.42, 0.2), P["dark"])
        # exhaust branch to the receiver
        setmat(cylu("exb%d" % i, (x, -1.6, 14.4), 0.32, 2.4, rot=(D(70), 0, 0)), P["silver"])
        # fuel / cooling pipes
        setmat(cylu("hp%d" % i, (x + 0.55, -0.9, 13.2), 0.05, 1.4, verts=10, rot=(D(30), 0, 0)), P["dark"])
        setmat(cylu("cw%d" % i, (x - 0.55, 1.2, 12.6), 0.1, 2.2, verts=12, rot=(D(-20), 0, 0)), P["blue"])
        # indicator cock + lube box
        bevel(setmat(cub("lube%d" % i, (x, 2.3, 7.5), (0.6, 0.35, 0.5)), P["dark"]), 0.02)
    # long pipe runs
    for (y, z, r, col) in ((-2.95, 8.9, 0.12, "blue"), (-2.95, 8.55, 0.09, "green"), (2.4, 12.6, 0.16, "blue"), (2.4, 12.2, 0.08, "red"), (-2.95, 3.0, 0.1, "yellow")):
        setmat(cylu("run_%.1f_%.1f" % (y, z), (0, y, z), r, L + 6, verts=16, rot=(0, D(90), 0)), P[col])
    # catwalks with gratings and yellow railings
    def catwalk(y0, z, w, side):
        g = prim("grid", "grate_%.1f" % z, loc=(0, y0, z), x_subdivisions=int(L * 4), y_subdivisions=int(w * 4), size=1, smooth=False)
        g.scale = (L + 4, w, 1); apply_scale(g)
        md = g.modifiers.new("wf", "WIREFRAME"); md.thickness = 0.03; md.use_replace = True; setmat(g, P["dark"])
        ry = y0 + side * w / 2
        setmat(cylu("rail_%.1f" % z, (0, ry, z + 1.1), 0.03, L + 4, verts=10, rot=(0, D(90), 0)), P["yellow"])
        setmat(cylu("rail2_%.1f" % z, (0, ry, z + 0.55), 0.025, L + 4, verts=10, rot=(0, D(90), 0)), P["yellow"])
        for k in range(int((L + 4) / 1.5) + 1):
            setmat(cylu("post_%.1f_%d" % (z, k), (-(L + 4) / 2 + k * 1.5, ry, z + 0.55), 0.03, 1.1, verts=8), P["yellow"])
    catwalk(-3.9, 7.2, 1.5, -1); catwalk(-3.9, 12.0, 1.4, -1); catwalk(3.9, 12.0, 1.4, 1); catwalk(0, 16.3, 1.6, -1)
    # room: floor plates, hull frames, ceiling with lamps, shaft tunnel aft
    fl = setmat(prim("plane", "floor", loc=(0, 0, 0), scale=(45, 20, 1), smooth=False), P["floor"])
    for side in (-1, 1):
        setmat(prim("plane", "wall%d" % side, loc=(0, side * 19, 13), rot=(D(90), 0, 0), scale=(45, 13, 1), smooth=False), P["wall"])
        for k in range(46):
            bevel(setmat(cub("frm%d_%d" % (side, k), (-45 + k * 2, side * 18.6, 13), (0.25, 0.8, 26)), P["wall"]), 0.02)
    setmat(prim("plane", "ceil", loc=(0, 0, 26), scale=(45, 20, 1), smooth=False), P["wall"])
    setmat(prim("plane", "wallF", loc=(45, 0, 13), rot=(0, D(90), 0), scale=(13, 20, 1), smooth=False), P["wall"])
    lamp_m = emat("lampstrip", (1.0, 0.88, 0.7), 8, solid=True)[0]
    for k in range(10):
        for y in (-9, 0, 9):
            setmat(cub("lamp_%d_%d" % (k, y), (-36 + k * 8, y, 25.6), (2.4, 0.3, 0.12)), lamp_m)
            area("al_%d_%d" % (k, y), (-36 + k * 8, y, 25.3), (0, 0, 0), 420, size=2.4, sy=0.4, col=(1.0, 0.86, 0.68), shape="RECTANGLE")
    for k, (x, y, z) in enumerate(((10, -8, 9), (-10, -8, 9), (0, 8, 6), (14, -2, 18), (-14, -2, 18))):
        point("pr%d" % k, (x, y, z), 500, (1.0, 0.78, 0.55), radius=0.4)
    # aft bulkhead with the shaft tunnel opening, intermediate shaft on bearings to the stern seal
    ZC = 2.2
    setmat(prim("plane", "bulk", loc=(-45, 0, 13), rot=(0, D(90), 0), scale=(13, 20, 1), smooth=False), P["wall"])
    setmat(cylu("shaft", (-38, 0, ZC), 0.42, 56, rot=(0, D(90), 0)), paint("shaftsteel", (0.55, 0.56, 0.58), 0.25, metal=1.0, grime=0.15, scale=8))
    for k in range(5):
        bevel(setmat(cub("bearing%d" % k, (-18 - k * 8, 0, ZC - 0.5), (1.2, 1.6, 1.4)), P["eng"]), 0.04)
    for k in range(3):
        setmat(cylu("flange%d" % k, (-14 - k * 16, 0, ZC), 0.75, 0.25, rot=(0, D(90), 0)), P["dark"])
    # tunnel walls past the bulkhead (x<-45)
    tm = P["wall"]
    for side in (-1, 1):
        setmat(prim("plane", "tw%d" % side, loc=(-58, side * 3.2, 3), rot=(D(90), 0, 0), scale=(14, 3, 1), smooth=False), tm)
    setmat(prim("plane", "tceil", loc=(-58, 0, 5.6), scale=(14, 3.2, 1), smooth=False), tm)
    setmat(prim("plane", "tfloor", loc=(-58, 0, 0.0), scale=(14, 3.2, 1), smooth=False), P["floor"])
    setmat(prim("plane", "tend", loc=(-71.5, 0, 3), rot=(0, D(90), 0), scale=(3, 3.2, 1), smooth=False), P["dark"])
    for k in range(6):
        setmat(cub("tl%d" % k, (-48 - k * 4, 0, 5.5), (1.5, 0.15, 0.08)), lamp_m)
        point("tp%d" % k, (-48 - k * 4, 0, 5.0), 120, (1.0, 0.86, 0.68), radius=0.2)
    # rotating shaft (76 rpm): rotation key so flanges/bearing highlights move
    sh = bpy.data.objects["shaft"]
    sh.rotation_euler = (0, D(90), 0); K(sh, "rotation_euler", 1)
    sh.rotation_euler = (2 * math.pi * 76 / 60 * DUR, D(90), 0); K(sh, "rotation_euler", NFR + 1)

def build_propeller(name, loc, R, holo=False, blades=6):
    root = link(bpy.data.objects.new(name, None)); root.location = loc
    hub = cylu(name + "_hub", (0, 0, 0), R * 0.16, R * 0.35, rot=(0, D(90), 0)); hub.parent = root; hub.location = (0, 0, 0)
    objs = [hub]
    for b in range(blades):
        bm = bmesh.new(); prof = []
        n = 14
        # blade surface: radial from hub to tip, chord twisting, skewed
        rows = []
        for i in range(n + 1):
            r = R * (0.15 + 0.85 * i / n)
            chord = R * (0.28 + 0.32 * math.sin(math.pi * min(1, i / n * 0.9 + 0.05))) * (1 - (i / n) ** 4 * 0.85)
            pitch = math.atan2(R * 0.9, 2 * math.pi * r) * 1.0
            skew = (i / n) ** 2 * R * 0.25
            row = []
            for j in range(7):
                u = (j / 6.0 - 0.5) * chord
                th = 0.06 * R * (1 - (2 * j / 6.0 - 1) ** 2) * (1 - 0.8 * i / n)
                xl = u * math.sin(pitch); yt = u * math.cos(pitch) + skew
                row.append(bm.verts.new((xl + th, yt, r)))
            for j in range(6, -1, -1):
                u = (j / 6.0 - 0.5) * chord
                th = 0.06 * R * (1 - (2 * j / 6.0 - 1) ** 2) * (1 - 0.8 * i / n)
                xl = u * math.sin(pitch); yt = u * math.cos(pitch) + skew
                row.append(bm.verts.new((xl - th, yt, r)))
            rows.append(row)
        for a, c in zip(rows, rows[1:]):
            for j in range(len(a)):
                bm.faces.new((a[j], a[(j + 1) % len(a)], c[(j + 1) % len(a)], c[j]))
        try: bm.faces.new(rows[-1])
        except Exception: pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = new_mesh_obj("%s_b%d" % (name, b), bm)
        for p in o.data.polygons: p.use_smooth = True
        o.parent = root; o.rotation_euler = (b * 2 * math.pi / blades, 0, 0)
        objs.append(o)
    if True:
        bronze = mat("bronze", (0.62, 0.42, 0.22), 0.28, metal=1.0)
        for o in objs: setmat(o, bronze)
        sub = None
    return root

def set_engine():
    world("studio_small_09", 0.15, cam_sees=False, back=(0.01, 0.01, 0.012), vol=((0.9, 0.85, 0.8), 0.0018, 0.5))
    build_engine()
    setattr_safe(sc.eevee, "volumetric_end", 90.0)

# ------------------------------------------------------------------ underwater stern
def set_stern():
    world(None, 1.0, back=(0.02, 0.13, 0.15), vol=((0.3, 0.75, 0.75), 0.02, 0.55))
    sun((D(25), D(10), D(30)), 8.0, (0.85, 1.0, 0.95), 2.0)
    area("uwfill", (-14, -10, -6), (D(110), 0, D(-55)), 30000, size=12, col=(0.55, 0.9, 0.9))
    area("uwkey", (-6, -14, 4), (D(70), 0, D(-25)), 18000, size=6, col=(0.9, 1.0, 0.95))
    # hull bottom above the propeller (stern section of the same hull, local)
    h = build_hull("sternhull", sections=80); h.location = (190, 0, 13.5)
    shaftm = mat("steelshaft", (0.4, 0.4, 0.42), 0.3, metal=1.0)
    s = cylu("shaft", (6, 0, 0), 0.5, 12, rot=(0, D(90), 0)); setmat(s, shaftm)
    boss = cylu("boss", (13, 0, 0), 1.3, 3, rot=(0, D(90), 0)); setmat(boss, mat("hullred", (0.32, 0.035, 0.03), 0.6))
    rud = cub("rudder", (-7, 0, 1), (5, 0.9, 12)); setmat(rud, mat("hullred", (0.32, 0.035, 0.03), 0.6))
    prop = build_propeller("prop", (0, 0, 0), 4.8, holo=False)
    rps = 76.0 / 60.0
    prop.rotation_euler = (0, 0, 0); K(prop, "rotation_euler", 1)
    prop.rotation_euler = (2 * math.pi * rps * DUR, 0, 0); K(prop, "rotation_euler", NFR + 1)
    # bubbles: particles from a ring at the blade tips
    em = cylu("bubsrc", (0.3, 0, 0), 4.6, 0.4, rot=(0, D(90), 0)); em.hide_render = True
    bub = prim("ico", "bubble", loc=(0, 0, -50), radius=0.05, subdivisions=1); setmat(bub, mat("bubm", (0.9, 1, 1), 0.05, trans=1.0, ior=1.0))
    em.modifiers.new("ps", "PARTICLE_SYSTEM"); ps = em.particle_systems[0].settings
    ps.count = 6000; ps.frame_start = -200; ps.frame_end = NFR; ps.lifetime = 120; ps.normal_factor = 0.3
    ps.object_align_factor = (-1.5, 0, 0); ps.factor_random = 0.6
    ps.render_type = "OBJECT"; ps.instance_object = bub; ps.particle_size = 1.0; ps.size_random = 0.8
    ps.effector_weights.gravity = -0.03
    # light shafts from above
    for k in range(4):
        spot("ray%d" % k, (-10 + k * 8, -4 + k * 2, 40), (0, 0, 0), 60000, size_deg=12, blend=0.9, col=(0.8, 1, 0.95), radius=0.5)
    setattr_safe(sc.eevee, "volumetric_end", 120.0)

# ------------------------------------------------------------------ crank (BlenderKit 'Car Engine ANIMATED' x-ray asset)
def set_crank():
    world("studio_small_09", 0.6, cam_sees=False, back=(0.006, 0.008, 0.012))
    r = load_asset("carengine", 1.0, (0, 0, -0.35), axis="max")
    if r is None: NOTES.append("carengine missing")
    # loop every action so the pistons keep moving for the whole shot
    nfc = 0
    for a in bpy.data.actions:
        for fc in all_fcurves(a):
            try:
                if not any(m.type == "CYCLES" for m in fc.modifiers): fc.modifiers.new("CYCLES"); nfc += 1
            except Exception: pass
    NOTES.append("cycled fcurves %d" % nfc)
    area("key", (1.2, -1.4, 1.4), (D(50), 0, D(40)), 400, size=1.5, col=(0.75, 0.9, 1.0))
    area("rim", (-1.4, 1.0, 1.0), (D(60), 0, D(-130)), 500, size=1.2, col=(1.0, 0.6, 0.3))
    area("fill", (0, -2, -0.2), (D(95), 0, 0), 80, size=3)
    if EX.get("air"):
        point("airglow", (0, 0, 0.25), 30, (0.5, 0.85, 1.0), radius=0.2)

# ------------------------------------------------------------------ build + camera
{"SEA": set_sea, "PORT": set_port, "HOLO": set_engine, "STERN": set_stern, "CRANK": set_crank}[SET]()
strip_displacement()

cam_d = bpy.data.cameras.new("cam"); cam = link(bpy.data.objects.new("cam", cam_d)); sc.camera = cam
cam_d.clip_start = 0.05 if SET == "CRANK" else 0.5; cam_d.clip_end = 6000
tgt = link(bpy.data.objects.new("tgt", None))
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
if EX.get("orbit"):
    R_, Z_, TZ, a0, a1 = EX["orbit"]
    for f in range(1, NFR + 2, 2):
        a = D(a0 + (a1 - a0) * (f - 1) / NFR)
        cam.location = (R_ * math.cos(a), R_ * math.sin(a), Z_); K(cam, "location", f, "LINEAR")
    tgt.location = (0, 0, TZ); cam_d.lens = 22
else:
    for (t, p, g, lens) in CAMK:
        f = F(t)
        cam.location = p; K(cam, "location", f, "BEZIER")
        tgt.location = g; K(tgt, "location", f, "BEZIER")
        cam_d.lens = lens; K(cam_d, "lens", f, "BEZIER")
if SET == "CRANK":
    cam_d.dof.use_dof = True; cam_d.dof.focus_object = tgt; cam_d.dof.aperture_fstop = 2.8

for k in ("taa_render_samples",):
    setattr_safe(sc.eevee, k, 24 if SET in ("SEA", "PORT", "STERN") else 16)

print("SHIP3D BUILT", SHOT, SET, NFR, "notes:", NOTES[:30], "assets:", INFO_ASSETS, "t=%.1f" % (time.time() - T0))

if MODE == "build":
    print("BUILD ONLY"); sys.exit(0)
ims = sc.render.image_settings
try: ims.media_type = "IMAGE"
except Exception: pass
ims.file_format = "JPEG"; ims.quality = 92
if MODE == "still":
    for frac in (0.15, 0.6):
        f = max(1, int(NFR * frac)); sc.frame_set(f)
        sc.render.filepath = os.path.join(os.getcwd(), "st_%s_%d.jpg" % (SHOT, int(frac * 100)))
        bpy.ops.render.render(write_still=True)
    print("SHIP3D STILLS", SHOT, "t=%.1f" % (time.time() - T0))
else:
    od = os.path.join(os.getcwd(), "r_" + SHOT); os.makedirs(od, exist_ok=True)
    for f in range(1, NFR + 1):
        p = os.path.join(od, "f%04d.jpg" % f)
        if os.path.exists(p) and os.path.getsize(p) > 1000: continue
        sc.frame_set(f); sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
    print("SHIP3D RENDERED", SHOT, NFR, "t=%.1f" % (time.time() - T0))
