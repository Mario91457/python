import re
import chess
import exceptions
from typing import cast, Literal
from utils.Vec2 import Vec2

FILES = "ABCDEFGH"
POSITION_REGEX = re.compile(r"^[A-H][1-8]$")

FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

game = chess.Chess(FEN)

def decode_position(text: str) -> Vec2 | None:
    text = text.strip().upper()
    if POSITION_REGEX.match(text):
        return Vec2(FILES.index(text[0]) + 1, int(text[1]))
    return None

def encode_position(pos: Vec2) -> str:
    return f"{FILES[pos.x - 1]}{pos.y}"

def print_board(board: dict, highlight: list[Vec2] | None = None):
    highlight = highlight or []
    grid = [["." for _ in range(8)] for _ in range(8)]

    for pos, piece in board.items():
        row = 8 - pos.y
        col = pos.x - 1
        grid[row][col] = str(piece)

    for pos in highlight:
        row = 8 - pos.y
        col = pos.x - 1
        if 0 <= row < 8 and 0 <= col < 8:
            grid[row][col] = f"\033[31m{grid[row][col]}\033[0m"

    for i, row in enumerate(grid):
        print(f"{8 - i} " + " ".join(row))
    print("  A B C D E F G H\n")

def prompt_position(prompt: str) -> Vec2:
    while True:
        try:
            pos = decode_position(input(prompt))
            if not pos:
                raise exceptions.InvalidInput("Use A-H and 1-8 (example: E2)")
            return pos
        except exceptions.InvalidInput as e:
            print(f"[ERROR] {e}")

def choose_move(piece_pos: Vec2) -> Vec2 | None:
    moves = game.get_piece_moves(piece_pos)

    if not moves:
        print("No legal moves for this piece.\n")
        return None

    print_board(game.board, moves)
    print("Valid moves:", ", ".join(encode_position(m) for m in moves))

    while True:
        try:
            dst = decode_position(input("Move to: "))
            if not dst or dst not in moves:
                raise exceptions.InvalidInput("Select one of the highlighted squares")
            return dst
        except exceptions.InvalidInput as e:
            print(f"[ERROR] {e}")

def handle_promotion():
    print("🎓 PAWN PROMOTION!")
    choices = {"Q": "Queen", "R": "Rook", "B": "Bishop", "N": "Knight"}
    
    while True:
        choice = input("Promote to (Q, R, B, N): ").strip().upper()
        if choice in choices:
            try:
                game.promote(cast(Literal["Q", "R", "B", "N"], choice)) #bc type checker     
                print(f"Pawn promoted to {choices[choice]}.")
                break
            except exceptions.InvalidMove as e:
                print(f"[ERROR] {e}")
        else:
            print("[ERROR] Invalid choice. Please enter Q, R, B, or N.")

def main():
    while game.status not in (chess.GameStatus.CHECKMATE, chess.GameStatus.STALEMATE):
        print_board(game.board)

        if game.status == chess.GameStatus.CHECK:
            print("⚠️  Check!\n")

        print(f"Turn: {game.current_team}")

        src = prompt_position("Select piece: ")
        dst = choose_move(src)

        if dst is None:
            continue

        try:
            game.move(src, dst)
            if game.status == chess.GameStatus.PROMOTING:
                print_board(game.board)
                handle_promotion()
        except exceptions.InvalidMove as e:
            print(f"[ERROR] {e}")

        print("-" * 40)

    print_board(game.board)

    if game.status == chess.GameStatus.CHECKMATE:
        print("♚ Checkmate!")
    else:
        print("½ Stalemate!")

if __name__ == "__main__":
    main()
