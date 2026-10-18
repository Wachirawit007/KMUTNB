# ===== Loop : Fixed number (slide 11) - แบบ text-mode =====
# วาดบันไดด้วยตัวอักษร  ขั้นละ  _|
#       _
#     _|
#   _|
# _|

def draw_stairs(x, y, s):
    """x = จำนวนช่องว่างเริ่มต้นฝั่งซ้าย, y = ไม่ใช้ใน text-mode, s = จำนวนขั้น"""
    i = s - 1
    # ขั้นบนสุดมีแค่ "_"
    print(" " * (x + 2 * s) + "_")
    while i >= 0:
        print(" " * (x + 2 * i) + "_|")
        i = i - 1


draw_stairs(0, 0, 3)
