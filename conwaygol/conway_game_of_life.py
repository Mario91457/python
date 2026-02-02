import tkinter as tk
from collections import defaultdict
from grid import Vec2
from grid import Grid

root = tk.Tk()

WIDTH = 500
HEIGTH = 500
SIZE_X = 10
SIZE_Y = 10

root.geometry("500x500")
canvas = tk.Canvas(root, bg="white", width=WIDTH, height=HEIGTH)
canvas.pack(fill="both", expand=True) 
root.update()

amount = Vec2((WIDTH//SIZE_X), (HEIGTH//SIZE_Y))
size = Vec2(SIZE_X, SIZE_Y)
grid = Grid(canvas, amount, size, True)

def setNewCellStates(grid: Grid, newStates: set[Vec2]):
    currentGridCells = set(grid.active_ids.keys())
    # duplicates = currentGridCells & newStates 
    new = newStates.difference(currentGridCells)
    old = currentGridCells.difference(newStates)

    for i in new:
        grid.toggle_cell(i, True)

    for i in old:
        grid.toggle_cell(i, False)

def step(live: set[Vec2]) -> set[Vec2]:
    neighbor_count = defaultdict(int)

    for cell in live:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor = Vec2(cell.x + dx, cell.y + dy)
                neighbor_count[neighbor] += 1

    next_gen = set()

    for cell, neighbors in neighbor_count.items():
        if cell in live:
            if neighbors == 2 or neighbors == 3:    #rule 2
                next_gen.add(cell)
        else:
            if neighbors == 3:                      #rule 4
                next_gen.add(cell)

    return next_gen

offset = 10

grid.toggle_cell(Vec2(offset+2, offset), True)
grid.toggle_cell(Vec2(offset+3, offset), True)
grid.toggle_cell(Vec2(offset+1, offset+1), True)
grid.toggle_cell(Vec2(offset+2, offset+1), True)
grid.toggle_cell(Vec2(offset+2, offset+2), True)

def animate():
    newCells = step(set(grid.active_ids.keys()))
    setNewCellStates(grid, newCells)
    canvas.after(100, animate)

animate()
root.mainloop()
