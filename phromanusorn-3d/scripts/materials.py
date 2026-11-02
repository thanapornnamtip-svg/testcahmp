"""รายการวัสดุทั้งหมด (สีประจำโรงเรียน น้ำเงิน-ชมพู)"""
from mb import mat


def define_all():
    # ผนัง / โครงสร้าง
    mat("wall_cream", "#EFE6D2", 0.85)
    mat("wall_white", "#F3F1EA", 0.85)
    mat("wall_pinkish", "#F3DDE4", 0.85)
    mat("wall_bluish", "#DDE6F1", 0.85)
    mat("wall_in", "#D8D2C5", 0.9)
    mat("trim_pink", "#E07FA8", 0.7)
    mat("trim_blue", "#2D4E9A", 0.6)
    mat("trim_white", "#F7F7F2", 0.7)
    mat("column", "#F4F1E8", 0.8)
    mat("plinth", tex="concrete.jpg", scale=3.0, rough=0.9)
    mat("floor_tile", tex="concrete_light.jpg", scale=2.0, rough=0.6)
    mat("ceiling", "#E9E6DE", 0.9)
    mat("soffit", "#E6E1D6", 0.9)
    mat("glass", "#2B3F4E", 0.05, metal=0.3, spec=0.7)
    mat("glass_light", "#5C7D92", 0.05, metal=0.2, spec=0.7)
    mat("frame", "#CDD1D4", 0.35, metal=0.6)
    mat("frame_wood", "#6E4528", 0.6)
    mat("door", "#7A4A2A", 0.6)
    mat("door_blue", "#355A9C", 0.5)
    mat("dark", "#2A2A2C", 0.9)
    mat("breeze", tex="breeze.png", scale=0.8, clip=True, rough=0.9)
    mat("breeze_solid", tex="breeze_solid.jpg", scale=0.8, rough=0.9)
    mat("railing", tex="railing.png", scale=1.0, clip=True, rough=0.5, metal=0.3)
    mat("louvre", tex="louvre.png", scale=1.0, clip=True, rough=0.5, metal=0.3)
    mat("concrete", tex="concrete.jpg", scale=3.0, rough=0.9)
    mat("concrete_paint", "#E4E0D6", 0.85)
    mat("chalkboard", "#2F4A3A", 0.7)
    mat("shutter", tex="shutter.jpg", scale=1.0, rough=0.4, metal=0.5)
    # หลังคา
    for c in ("blue", "orange", "green", "red", "grey"):
        mat("roof_" + c, tex=f"roof_{c}.jpg", scale=1.6, rough=0.55)
    mat("ridge", "#ECE8E0", 0.6)
    for c in ("blue", "zinc", "pink"):
        mat("metal_" + c, tex=f"metal_{c}.jpg", scale=1.0, rough=0.4, metal=0.5)
    mat("steel_blue", "#2F5DA8", 0.4, metal=0.5)
    mat("steel_pink", "#D9789F", 0.4, metal=0.4)
    mat("steel_white", "#EDEDED", 0.4, metal=0.4)
    mat("steel", "#9AA1A8", 0.35, metal=0.8)
    mat("gold", "#D9A93A", 0.25, metal=1.0)
    mat("red_lacquer", "#8E1B20", 0.5)
    # ป้าย / สัญลักษณ์
    mat("flag", tex="thai_flag.jpg", rough=0.8)
    mat("emblem", tex="emblem.png", clip=True, rough=0.5)
    for n in ("sign_gate", "sign_stone", "label_gym", "label_hall", "label_canteen", "label_shrine",
              "label_guard", "label_welcome", "label_admin", "sign_road", "label_stand", "banner_motto",
              "stalls"):
        mat(n, tex=n + ".jpg", rough=0.5)
    mat("sign_schoolzone", tex="sign_schoolzone.png", clip=True, rough=0.5)
    for i in range(1, 10):
        mat(f"label_b{i}", tex=f"label_b{i}.jpg", rough=0.5)
    for i in range(12):
        mat(f"shop_{i}", tex=f"shop_{i}.jpg", rough=0.5)
    # พื้น
    mat("grass", tex="grass.jpg", scale=6.0, rough=0.95)
    mat("grass_dry", tex="grass_dry.jpg", scale=8.0, rough=0.95)
    mat("field", tex="field.jpg", rough=0.95)
    mat("track", tex="track.jpg", rough=0.9)
    mat("asphalt", tex="asphalt.jpg", scale=4.0, rough=0.9)
    mat("paving", tex="paving.jpg", scale=2.0, rough=0.85)
    mat("soil", tex="soil.jpg", scale=3.0, rough=0.95)
    mat("sand", tex="sand.jpg", scale=2.0, rough=0.95)
    mat("hill", tex="hill.jpg", scale=60.0, rough=0.95)
    mat("vegbed", tex="vegbed.jpg", scale=2.0, rough=0.95)
    mat("court_basket", tex="court_basket.jpg", rough=0.7)
    mat("court_takraw", tex="court_takraw.jpg", rough=0.7)
    mat("woodfloor", tex="woodfloor.jpg", scale=2.0, rough=0.4)
    mat("curb_bw", tex="curb_bw.jpg", scale=1.0, rough=0.8)
    mat("curb_rw", tex="curb_rw.jpg", scale=1.0, rough=0.8)
    mat("road_white", "#EDEDED", 0.7)
    mat("road_yellow", "#E8C23A", 0.7)
    mat("kerb", "#BDB8AE", 0.85)
    # ต้นไม้
    mat("leaves", tex="leaves.jpg", scale=2.5, rough=0.8)
    mat("leaves_light", tex="leaves_light.jpg", scale=2.5, rough=0.8)
    mat("leaves_plumeria", tex="leaves_plumeria.jpg", scale=1.0, rough=0.7)
    mat("bark", tex="bark.jpg", scale=1.0, rough=0.95)
    mat("bark_plumeria", "#8E8576", 0.9)
    mat("flower_white", "#FBF6E6", 0.6)
    mat("flower_yellow", "#F6CF5E", 0.6)
    mat("flower_pink", "#EE8FB5", 0.6)
    mat("palm_trunk", "#A29A8C", 0.9)
    mat("palm_leaf", "#4F7F35", 0.7)
    mat("crownshaft", "#6F9A45", 0.6)
    mat("hedge", tex="leaves_light.jpg", scale=1.5, rough=0.85)
    # คน
    mat("skin", "#C99A74", 0.6)
    mat("skin2", "#B9855F", 0.6)
    mat("hair", "#1E1A18", 0.7)
    mat("shirt_white", "#F5F5F2", 0.8)
    mat("navy", "#1F2A48", 0.8)
    mat("khaki", "#A78E60", 0.8)
    mat("black", "#18181A", 0.6)
    mat("teacher_1", "#6C8EBF", 0.8)
    mat("teacher_2", "#C46A85", 0.8)
    mat("teacher_3", "#7A9A6A", 0.8)
    # ยานพาหนะ
    for n, c in (("car_white", "#EDEDEA"), ("car_silver", "#A9ADB1"), ("car_red", "#A52A2A"),
                 ("car_blue", "#2E4E86"), ("car_black", "#1E1F22"), ("car_grey", "#6E7276")):
        mat(n, c, 0.3, metal=0.4, coat=0.6)
    for n, c in (("mb_red", "#B32025"), ("mb_black", "#202022"), ("mb_blue", "#2050A0"),
                 ("mb_white", "#EAEAEA"), ("mb_pink", "#E58FB0")):
        mat(n, c, 0.35, metal=0.2)
    mat("tire", "#1A1A1A", 0.9)
    mat("chrome", "#D0D4D8", 0.15, metal=1.0)
    # เขาวัง / ตึกแถว
    mat("chedi_white", "#F2F0EA", 0.8)
    mat("prang_red", "#A4442F", 0.85)
    mat("palace_wall", "#EFE9DD", 0.85)
    mat("rock", "#8F877B", 0.95)
    mat("mountain_far", "#7F9396", 1.0)
    mat("far_ground", "#8E9468", 1.0)
    for i, c in enumerate(("#E8D7B0", "#CFE0E8", "#F0C9B0", "#DDE8C8", "#E9E9E9", "#F2E2A0", "#E8C4C4", "#D5D0E8")):
        mat(f"sh_{i}", c, 0.85)
    mat("cable", "#151515", 0.7)
    mat("pole_concrete", "#B9B5AC", 0.9)
    mat("bench_stone", "#BDB6A8", 0.6)
    mat("lamp", "#FFF6DA", 0.3, emit="#FFF2CC", emit_str=0.0)
    mat("water", "#3C6E8A", 0.05, spec=0.8)
    mat("net", "#F0F0F0", 0.7)
    mat("cloth_yellow", "#E9B83A", 0.8)
