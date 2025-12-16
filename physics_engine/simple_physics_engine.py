import tkinter as tk
from Vector2 import Vector2
import random
from time import time

root = tk.Tk()
root.resizable(False, False)
canvas = tk.Canvas(root, width=1000, height=500, bg="white")
canvas.pack()
root.update()

############ VARS ############

AMOUNT = 10
SIZE = 20
RESTITUTION = .6
FRICTION = 1 #not used
GRAVITY = Vector2(0, 0)

CELL_SIZE = SIZE * 2
gridW = canvas.winfo_width() // CELL_SIZE
gridH = canvas.winfo_height() // CELL_SIZE
lastTime = time()

grid_rects = {}
objects_grid = [[[] for _ in range(gridW)] for _ in range(gridH)] ## ASSUMING THAT OBJECTS ARE ALL THE SAME SIZE
balls = []

############ MAIN ############

class Circle:
    def __init__(self, pos: Vector2, radius, vel: Vector2, mass, color="blue"):
        self.pos = pos
        self.vel = vel
        self.mass = mass
        self.radius = radius

        self.circle = canvas.create_oval(
            pos.x - radius, pos.y - radius,
            pos.x + radius, pos.y + radius,
            fill=color, outline="black"
        )

    def getCoords(self):
        return self.pos.x, self.pos.y

    def move(self, x, y):
        canvas.move(self.circle, x, y)
        self.pos.x += x
        self.pos.y += y

    def update(self, dt):
        self.vel += GRAVITY * dt

        self.move(self.vel.x * dt, self.vel.y * dt)
        x, y = self.getCoords()

        if x - self.radius < 0:
            self.vel.x = -self.vel.x * RESTITUTION
            self.move(-(x - self.radius), 0)
        elif x + self.radius > canvas.winfo_width():
            self.vel.x = -self.vel.x * RESTITUTION
            self.move(canvas.winfo_width() - (x + self.radius), 0)

        if y - self.radius < 0:
            self.vel.y = -self.vel.y * RESTITUTION
            self.move(0, -(y - self.radius))
        elif y + self.radius > canvas.winfo_height():
            self.vel.y = -self.vel.y * RESTITUTION
            self.move(0, canvas.winfo_height() - (y + self.radius))

            if abs(self.vel.y) < 10:
                self.vel.y = 0

def getCell(x, y):
    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)

    col = max(0, min(gridW-1, col))
    row = max(0, min(gridH-1, row))
    return row, col

def getCellObjects(x,y):
    return objects_grid[y][x]

def checkCellCollision(cell_1: list[Circle], cell_2: list[Circle]):
    for obj_1 in cell_1:
        for obj_2 in cell_2:
            if obj_1 is obj_2:
                continue

            delta = obj_2.pos - obj_1.pos
            dist = delta.magnitude
            min_dist = obj_1.radius + obj_2.radius

            if dist == 0 or dist > min_dist:
                continue

            normal = delta.normalized()

            overlap = min_dist - dist
            total_mass = obj_1.mass + obj_2.mass

            correction = normal * (overlap / total_mass)
            obj_1.move(-correction.x * obj_2.mass, -correction.y * obj_2.mass)
            obj_2.move( correction.x * obj_1.mass,  correction.y * obj_1.mass)

            rv = obj_2.vel - obj_1.vel
            vel_along_normal = rv.dot(normal)

            if vel_along_normal > 0:
                continue

            j = -(1 + RESTITUTION) * vel_along_normal
            j /= (1 / obj_1.mass + 1 / obj_2.mass)

            impulse = normal * j

            obj_1.vel -= impulse * (1 / obj_1.mass)
            obj_2.vel += impulse * (1 / obj_2.mass)

def checkCollision():
    for row in range(1, gridH-1):
        for col in range(1, gridW-1):
            cell_1 = getCellObjects(col, row)
            for y in (-1,0,1):
                for x in (-1,0,1):
                    cell_2 = getCellObjects(col + x, row + y)
                    checkCellCollision(cell_1, cell_2)

def updateGrid():
    for r in range(gridH):
        for c in range(gridW):
            objects_grid[r][c].clear()
    
    for b in balls:
        row, col = getCell(b.pos.x, b.pos.y)
        objects_grid[row][col].append(b)

############ MISC ############

def draw_grid():
    for c in range(gridW + 1):
        x = c * CELL_SIZE
        canvas.create_line(x, 0, x, canvas.winfo_height(),
                           fill="#dddddd")

    for r in range(gridH + 1):
        y = r * CELL_SIZE
        canvas.create_line(0, y, canvas.winfo_width(), y,
                           fill="#dddddd")

def draw_occupied_cells():
    for rect in grid_rects.values():
        canvas.delete(rect)
    grid_rects.clear()

    for r in range(gridH):
        for c in range(gridW):
            if objects_grid[r][c]:
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE

                rect = canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="red",
                    fill="",

                )
                grid_rects[(r, c)] = rect

############ SPAWN ############

def rand(minimum, maximum):
    return random.randrange(minimum, maximum)

def createCircle(pos, vel, radius, mass, color):
    balls.append(Circle(pos, radius, vel, mass, color))

for _ in range(AMOUNT):
    radius = SIZE
    pos = Vector2(
        rand(radius, canvas.winfo_width() - radius),
        rand(radius, canvas.winfo_height() - radius)
    )
    vel = Vector2(rand(-200, 200), rand(-200, 200))
    createCircle(pos, vel, radius, 10, "blue")

############ LOOP ############

def animate():
    global lastTime
    currentTime = time()
    dt = currentTime - lastTime

    checkCollision()

    for b in balls:
        b.update(dt)
    
    lastTime = currentTime
    updateGrid()
    # draw_occupied_cells()

    canvas.after(1, animate)

# draw_grid()
updateGrid()
animate()
root.mainloop()
