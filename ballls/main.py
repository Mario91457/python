import tkinter as tk
import random

root = tk.Tk()
canvas = tk.Canvas(root, width=1000, height=500, bg="white")
canvas.pack()

class Objects:
    def __init__(self, x_pos, y_pos, x_speed=0, y_speed=0):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_speed = x_speed
        self.y_speed = y_speed

class Circle(Objects):
    def __init__(self, x_pos, y_pos, radius, x_speed, y_speed, color="blue"):
        super().__init__(x_pos, y_pos, x_speed, y_speed)
        self.radius = radius
        self.circle = canvas.create_oval(
            x_pos - radius, y_pos - radius,
            x_pos + radius, y_pos + radius,
            fill=color, outline="black"
        )

    def getCoords(self):
        return self.x_pos, self.y_pos

    def move(self, x, y):
        canvas.move(self.circle, x, y)
        self.x_pos += x
        self.y_pos += y

    def update(self):
        self.move(self.x_speed, self.y_speed)
        x, y = self.getCoords()

        if x - self.radius < 0:
            self.x_speed = -self.x_speed
            self.move(-(x - self.radius), 0)
        elif x + self.radius > canvas.winfo_width():
            self.x_speed = -self.x_speed
            self.move(canvas.winfo_width() - (x + self.radius), 0)

        if y - self.radius < 0:
            self.y_speed = -self.y_speed
            self.move(0, -(y - self.radius))
        elif y + self.radius > canvas.winfo_height():
            self.y_speed = -self.y_speed
            self.move(0, canvas.winfo_height() - (y + self.radius))

balls = []
def rand(minimum, maximum):
    return random.randrange(minimum, maximum)

root.update()

for i in range(10):
    radius = rand(5, 40)
    x = rand(radius, canvas.winfo_width() - radius)
    y = rand(radius, canvas.winfo_height() - radius)
    balls.append(
        Circle(x, y, radius, rand(1, 20), rand(1, 20))
    )

def animate():
    for b in balls:
        b.update()
    canvas.after(16, animate)

animate()
root.mainloop()
