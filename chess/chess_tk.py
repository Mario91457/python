import tkinter as tk
from typing import Any
from PIL import Image, ImageTk
from os import path
from utils.Vec2 import Vec2
import chess
import exceptions

root = tk.Tk()

WIDTH = 500
HEIGTH = 500
SOUND = True

FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

root.geometry("500x500")
canvas = tk.Canvas(root, bg="white", width=WIDTH, height=HEIGTH)
canvas.pack(fill="both", expand=True) 
root.update()
 
size = Vec2(WIDTH//8, HEIGTH//8)

try:
    has_pygame = False
    if SOUND:
        import pygame
        has_pygame = True
        pygame.mixer.init()
        
except ImportError:
    has_pygame = False
    print("has_pygame is not installed. No sound will be played.")

def play_sound(sound_name):
    if not has_pygame and not SOUND:
        return
    
    sound_path = path.join(f"sounds/{sound_name}")
    if not path.exists(sound_path):
        print("No file found")
        return
    
    try:
        s = pygame.mixer.Sound(sound_path)
        s.play()
    except pygame.error as e:
        print(f"[ERROR sound]: {e}")

class ChessTk():
    def __init__(self, canvas: tk.Canvas, FEN: str, cell_size: Vec2 = Vec2(100,100), rotate_on_each_move: bool = False):
        self.canvas = canvas
        self.game = chess.Chess(FEN)
        self.cell_size = cell_size
        self.grid_size = Vec2(8 * cell_size.x, 8 * cell_size.y)

        self.images = []

        self._drag_start = Vec2(0, 0)
        self._drag_threshold = 5
        self._is_dragging = False

        #never work with canvas coord unless is drawinging, chess coords: 1-8
        self.piece_selected_id: int | None = None  #id of piece selected
        self.piece_selected_start_pos: Vec2 | None = None  #chess coords
        self.pieces_ids: dict[Vec2, int] = {}   #chess coords
        self.hint_ids: dict[Vec2, int] = {}  #id of the hints

        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

        canvas.tag_bind("piece", "<Enter>", self._on_enter)
        canvas.tag_bind("piece", "<Leave>", self._on_leave)
        self._create_board()

    def _move(self, pos_1: Vec2, pos_2: Vec2) -> Vec2:
        if pos_1 == pos_2: return pos_1
        cw, ch = self.cell_size.x, self.cell_size.y
        capture = False
        try:
            self.game.move(pos_1, pos_2)
            
            if self.game.status == chess.GameStatus.PROMOTING:
                self._handle_promotion()

            if self.piece_selected_start_pos is None:
                return pos_1
            
            piece_id = self.pieces_ids.pop(self.piece_selected_start_pos)
            
            if pos_2 in self.pieces_ids:
                capture = True
                captured_id = self.pieces_ids.pop(pos_2)
                self.canvas.delete(captured_id)
            else:
                ep_pos = Vec2(pos_2.x, pos_1.y)
                if pos_1.x != pos_2.x and ep_pos in self.pieces_ids and ep_pos not in self.game.board:
                    capture = True
                    captured_id = self.pieces_ids.pop(ep_pos)
                    self.canvas.delete(captured_id)
            # ------------------------------------------

            self.pieces_ids[pos_2] = piece_id

            vis_pos = self._reverse(pos_2)
            highlight_colors = ("#F5F682", "#B9CA43") 
            highlight_color = highlight_colors[(vis_pos.y + vis_pos.x) % 2]

            self.canvas.create_rectangle(
                (vis_pos.x-1)*cw, (vis_pos.y-1)*ch, 
                (vis_pos.x)*cw, (vis_pos.y)*ch, 
                fill=highlight_color, outline="", tags="highlight"
            )
            self.canvas.tag_raise("highlight", "square")

            if self.game.status == chess.GameStatus.CHECK:
                play_sound("check.mp3")
            elif self.game.status == chess.GameStatus.CHECKMATE:
                play_sound("game-end.mp3")
            elif capture:
                play_sound("capture.mp3")
            else:
                play_sound("move.mp3")
            return pos_2

        except exceptions.InvalidMove as e:
            print(f"[ERROR] {e}")
            play_sound("illegal.mp3")

        return pos_1

    def _handle_promotion(self):
        play_sound("promote.mp3")
        self.game.promote("Q")

    def _on_mouse_down(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        if not (0 <= canvas_x < self.grid_size.x and 0 <= canvas_y < self.grid_size.y):
            return

        cw, ch = self.cell_size.x, self.cell_size.y
        cell_x = int(self.canvas.canvasx(event.x) // cw) + 1
        cell_y = int(self.canvas.canvasy(event.y) // ch) + 1
        click_pos = self._reverse(Vec2(cell_x, cell_y)) #chess coords

        if self.piece_selected_id and self.piece_selected_start_pos and click_pos in self.hint_ids and click_pos != self.piece_selected_start_pos: 
            target = self._move(self.piece_selected_start_pos, click_pos)
            vis_pos = self._reverse(target)
            target_x, target_y = (vis_pos.x * cw) - cw//2, (vis_pos.y * ch) - ch//2

            self.canvas.coords(self.piece_selected_id, target_x, target_y)

            if self.piece_selected_start_pos != target:
                self._check_board()

            for vec, hint in self.hint_ids.items(): self.canvas.delete(hint)

            self.hint_ids.clear()
            self.piece_selected_id = self.piece_selected_start_pos = self._is_dragging= None
            return
        
        if click_pos in self.pieces_ids:
            for vec, hint in self.hint_ids.items(): self.canvas.delete(hint)

            self.hint_ids.clear()
            self.canvas.delete("highlight") 

            selected_pos = self._reverse(Vec2(cell_x, cell_y)) #in chess coords
            self.piece_selected_id = self.pieces_ids[selected_pos] #id of the piece
            self.piece_selected_start_pos = selected_pos    # vec2 of where it started

            #HIGHLIGH SELECTED PIECE
            highlight_colors = ("#F5F682", "#B9CA43",)
            highlight_color = highlight_colors[(cell_y + cell_x) % 2]

            self.canvas.create_rectangle(
                (cell_x-1)*cw, (cell_y-1)*ch, 
                (cell_x)*cw, (cell_y)*ch, 
                fill=highlight_color, outline="", tags="highlight"
            )
            self.canvas.tag_raise("highlight", "square")

            #CREATE HINT FOR THE PIECE
            hint_colors = ( "#CACBB3","#638046")
            moves = self.game.get_piece_moves(selected_pos)
            for move in moves:
                vis_move = self._reverse(move)
                color = hint_colors[(vis_move.y + vis_move.x) % 2]
                cx, cy = (vis_move.x * cw) - (cw // 2), (vis_move.y * ch) - (ch // 2)

                is_capture = move in self.pieces_ids
                radius_mult = 0.45 if is_capture else 1/6
                style: dict[str, Any] = ({"outline": color, "width": 4} if is_capture else {"fill": color, "outline": ""})

                r_w, r_h = radius_mult * cw, radius_mult * ch

                hid = self.canvas.create_oval(
                    cx - r_w, cy - r_h, 
                    cx + r_w, cy + r_h, 
                    **style, 
                    tags="hint"
                )
                self.hint_ids[move] = hid

    def _on_mouse_drag(self, event):
        if not self.piece_selected_id:
            return

        dx = abs(event.x - self._drag_start.x)
        dy = abs(event.y - self._drag_start.y)
        if dx > self._drag_threshold or dy > self._drag_threshold:
            self._is_dragging = True
            self.canvas.coords(self.piece_selected_id, event.x, event.y)
        self.canvas.tag_raise(self.piece_selected_id)

    def _on_mouse_up(self, event):
        if not self.piece_selected_id or not self.piece_selected_start_pos:
            return
        
        if self._is_dragging:
            cw, ch = self.cell_size.x, self.cell_size.y
            drop_x = int(self.canvas.canvasx(event.x) // cw) + 1
            drop_y = int(self.canvas.canvasy(event.y) // ch) + 1
            dest_pos = self._reverse(Vec2(drop_x, drop_y))

            target = self._move(self.piece_selected_start_pos, dest_pos)
            vis_pos = self._reverse(target)
            target_x, target_y = (vis_pos.x * cw) - cw//2, (vis_pos.y * ch) - ch//2

            self.canvas.coords(self.piece_selected_id, target_x, target_y)
            if self.piece_selected_start_pos != target:
                self._check_board()            
                
            for vec, hint in self.hint_ids.items(): self.canvas.delete(hint)

            self.hint_ids.clear()
            self.piece_selected_id = self.piece_selected_start_pos = self._is_dragging= None
      
    def _create_board(self, rebuild=False):
        cw, ch = self.cell_size.x, self.cell_size.y
        colors = ("#EEEED2", "#769656")

        if not rebuild:
            for y in range(8):
                for x in range(8):
                    color = colors[(y + x) % 2]
                    self.canvas.create_rectangle(
                        x*cw, y*ch, (x+1)*cw, (y+1)*ch, 
                        fill=color, outline="", tags="square"
                    )
        else:
            for piece_id in self.pieces_ids.values():
                self.canvas.delete(piece_id)

            self.pieces_ids.clear()
            self.images.clear()

            self.canvas.delete("hint")
            self.canvas.delete("highlight")
            self.hint_ids.clear()

        for pos, piece in self.game.board.items():
            team =  "w" if piece.team=="WHITE" else 'b'
            filename = path.join("img", f"{team}{piece.abbreviation.lower()}.png")
            piece_img = Image.open(filename).resize((cw, ch), Image.LANCZOS) # type: ignore
            photo_image = ImageTk.PhotoImage(piece_img)

            vis_pos = self._reverse(pos)
            self.images.append(photo_image)

            x = (vis_pos.x * cw) - cw // 2
            y = (vis_pos.y * ch) - ch // 2
            img_id = self.canvas.create_image(x, y, image=photo_image, tags=("piece", f"{team}{piece.abbreviation.lower()}"))
            self.pieces_ids[pos] = img_id

    def _on_enter(self, event):
        self.canvas.config(cursor="hand2") 

    def _on_leave(self, event):
        self.canvas.config(cursor="")

    def _check_board(self):
        for pos in list(self.pieces_ids.keys()):
            if pos not in self.game.board:
                self._create_board(rebuild=True)

        for pos, engine_piece in self.game.board.items():
            if pos not in self.pieces_ids:
                self._create_board(rebuild=True); 

            gui_id = self.pieces_ids[pos]
            all_tags = self.canvas.gettags(gui_id)

            team = "w" if engine_piece.team == "WHITE" else "b"
            expected_tag = f"{team}{engine_piece.abbreviation.lower()}"

            if expected_tag not in all_tags:
                self._create_board(rebuild=True)
               

    @staticmethod
    def _reverse(pos: Vec2) -> Vec2:
        return Vec2(pos.x, 9 - pos.y)

AAAA = ChessTk(canvas=canvas, FEN=FEN, cell_size=size)

root.mainloop()
