# --- แบบที่ผิด: x เป็น local ---
x = 200                 # global

def draw():
    x = 200             # local 
    draw_balloon(x, 200, 50)
    x = x + 10          # เปลี่ยนแค่ local บอลลูนเลยไม่ขยับ


# --- แบบที่ถูก: ใช้ global ---
# x = 200               # อยู่นอกฟังก์ชัน
#
# def draw():
#     global x          # แก้ค่า x ตัวนอกฟังก์ชันได้
#     draw_balloon(x, 200, 50)
#     x = x + 10
