"""ท้องฟ้า แสงแดด กล้อง และการตั้งค่าเรนเดอร์ (Cycles)"""
import math

import bpy
from mathutils import Vector

# แดดยามเช้า (เวลาเข้าแถวหน้าเสาธง ~ 8:30 น.) ส่องมาจากทิศตะวันออกเฉียงใต้
SUN_ELEV = math.radians(38.0)
SUN_AZIM = math.radians(112.0)   # วัดจากทิศเหนือ ตามเข็มนาฬิกา


def sun_dir():
    """เวกเตอร์ชี้ไปยังดวงอาทิตย์ (แกน +y = เหนือ, +x = ตะวันออก)"""
    ce = math.cos(SUN_ELEV)
    return Vector((ce * math.sin(SUN_AZIM), ce * math.cos(SUN_AZIM), math.sin(SUN_ELEV)))


def setup_world(strength=0.32):
    sc = bpy.context.scene
    w = bpy.data.worlds.get("Sky") or bpy.data.worlds.new("Sky")
    sc.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    try:
        sky.sky_type = "MULTIPLE_SCATTERING"
    except Exception:
        sky.sky_type = "HOSEK_WILKIE"
    for k, v in (("sun_disc", False), ("sun_elevation", SUN_ELEV), ("altitude", 30.0), ("air_density", 1.0),
                 ("aerosol_density", 1.6), ("ozone_density", 1.0)):
        try:
            setattr(sky, k, v)
        except Exception:
            pass
    try:
        # sun_rotation: มุมรอบแกน z (0 = +x) ทวนเข็ม
        sky.sun_rotation = math.atan2(sun_dir().y, sun_dir().x)
    except Exception:
        pass
    bg.inputs["Strength"].default_value = strength
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return w


def setup_sun(energy=4.2):
    sd = sun_dir()
    ld = bpy.data.lights.new("Sun", "SUN")
    ld.energy = energy
    ld.angle = math.radians(0.6)
    ld.color = (1.0, 0.96, 0.9)
    ob = bpy.data.objects.new("Sun", ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (-sd).to_track_quat("-Z", "Y").to_euler()
    return ob


def add_camera(name, loc, target, lens=32.0, ortho=None, coll=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.5
    cd.clip_end = 6000
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    ob = bpy.data.objects.new(name, cd)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob


def setup_render(res=(1600, 1000), samples=96):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.03
    cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    cy.max_bounces = 6
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 3
    cy.transparent_max_bounces = 12
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    sc.view_settings.exposure = 0.0
    sc.render.threads_mode = "AUTO"
