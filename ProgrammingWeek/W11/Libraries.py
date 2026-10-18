import turtle

t = turtle.Turtle()
t.forward(100)
t.left(90)

t.forward(100)
t.right(90)

t.forward(100)
t.left(90)

t.forward(100)
t.right(90)

t.forward(100)
turtle.done()


import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root, width=500, height=500)
canvas.pack()

canvas.create_oval(200, 50, 400, 250, fill="orange")
canvas.create_line(300, 250, 300, 450)

root.mainloop()


import matplotlib.pyplot as plt

temperatures = [
    [30, 31, 32, 30, 30, 31, 33],
    [29, 30, 31, 32, 31, 30, 29],
    [31, 32, 33, 34, 32, 31, 30],
    [30, 29, 30, 30, 29, 30, 32]
]

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

for week in temperatures:
    plt.plot(days, week)

plt.xlabel("Day")
plt.ylabel("Temperature (C)")
plt.title("Temperature for 4 Weeks")
plt.legend(["Week 1", "Week 2", "Week 3", "Week 4"])
plt.show()
