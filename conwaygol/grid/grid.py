import tkinter as tk
from .vec2 import Vec2

class Grid:
    def __init__(self, 
                 canvas: tk.Canvas, 
                 amount: Vec2 = Vec2(5,5), 
                 size: Vec2 = Vec2(5,5), 
                 draggable: bool = True, #draggable
                 infinite: bool = True, #grid restictions
                 clickable: bool = True, #only for the grid
        ) -> None:
        
        self.canvas = canvas
        self.amount = amount
        self.cell_size = size
        self.infinite = infinite

        self.draw_mode = False

        self.grid_pixel_size = Vec2(amount.x * size.x, amount.y * size.y)
        
        self.active_ids: dict[Vec2, list] = {} 
        
        self._drag_start = Vec2(0, 0)
        self._is_panning = False
        self._drag_threshold = 10

        # self.canvas.scan_dragto(int(self.canvas.winfo_width()/2), int(self.canvas.winfo_height()/2), gain=1)

        if not infinite:
            self._draw_grid_lines()
        
        if clickable:
            self.canvas.bind("<Button-1>", self._on_mouse_down)
            self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

        if draggable:
            # self.canvas.config(scrollregion=(0, 0, self.grid_pixel_size.x, self.grid_pixel_size.y))
            self.canvas.bind("<B1-Motion>", self._on_mouse_drag)

    def toggle_cell(self, cell: Vec2, state: bool | None = None, color: str = "red", text: str = ""):
        if not (0 <= cell.x < self.grid_pixel_size.x and 0 <= cell.y < self.grid_pixel_size.y) and not self.infinite:
            return
        
        is_currently_on = cell in self.active_ids

        target_state = not is_currently_on if state is None else state

        if target_state == is_currently_on:
            return

        if target_state:
            x1 = cell.x * self.cell_size.x
            y1 = cell.y * self.cell_size.y
            x2 = x1 + self.cell_size.x
            y2 = y1 + self.cell_size.y

            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            text_id = self.canvas.create_text(x1+((x2-x1)/2), y1+((y2-y1)/2), text=text, font=("Helvetica", 24))

            self.active_ids[cell] = [rect_id, text_id]
        else:
            active_ids = self.active_ids.pop(cell)
            for i in active_ids:
                self.canvas.delete(i)

    def _create_button(self):
        pass
    
    def _draw_grid_lines(self):
        w, h = self.grid_pixel_size.x, self.grid_pixel_size.y
        cw, ch = self.cell_size.x, self.cell_size.y
        
        for i in range(self.amount.x + 1):
            x = i * cw
            self.canvas.create_line(x, 0, x, h, fill="#e0e0e0", tags="grid_line")
        
        for i in range(self.amount.y + 1):
            y = i * ch
            self.canvas.create_line(0, y, w, y, fill="#e0e0e0", tags="grid_line")
            
        self.canvas.tag_lower("grid_line")

    def _on_mouse_down(self, event):
        self._drag_start = Vec2(event.x, event.y)
        self._is_panning = False
        self.canvas.scan_mark(event.x, event.y)

    def _on_mouse_drag(self, event):
        dx = abs(event.x - self._drag_start.x)
        dy = abs(event.y - self._drag_start.y)

        if dx > self._drag_threshold or dy > self._drag_threshold:
            self._is_panning = True
            self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_mouse_up(self, event):
        if self._is_panning:
            self._is_panning = False
            return

        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if not (0 <= canvas_x < self.grid_pixel_size.x and 0 <= canvas_y < self.grid_pixel_size.y) and not self.infinite:
            return

        cell_x = int(canvas_x // self.cell_size.x)
        cell_y = int(canvas_y // self.cell_size.y)
        
        self.toggle_cell(Vec2(cell_x, cell_y), color="#ff5555")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Grid")

    width = 200
    height = 200
    cell_w, cell_h = 10, 10

    canvas = tk.Canvas(root, bg="white", width=width, height=height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    root.update()

    amount = Vec2((width // cell_w), (height // cell_h))
    size = Vec2(cell_w, cell_h)

    large_amount = Vec2(50, 50) 
    
    app = Grid(canvas, large_amount, size, draggable=True, infinite=False)
    
    root.mainloop()