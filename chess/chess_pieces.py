from typing import Literal, Type
from abc import ABC, abstractmethod
from utils.Vec2 import Vec2

PIECES_MAP = {
    "P": {"NAME": "PAWN",   "WHITE": "♙", "BLACK": "♟"},
    "R": {"NAME": "ROOK",   "WHITE": "♖", "BLACK": "♜"},
    "N": {"NAME": "KNIGHT", "WHITE": "♘", "BLACK": "♞"},
    "B": {"NAME": "BISHOP", "WHITE": "♗", "BLACK": "♝"},
    "Q": {"NAME": "QUEEN",  "WHITE": "♕", "BLACK": "♛"},
    "K": {"NAME": "KING",   "WHITE": "♔", "BLACK": "♚"},
    "M": {"NAME": "TEST", "WHITE": "m", "BLACK": "M"},
}

class Piece(ABC):
    Pieces: dict[str, Type["Piece"]] = {}
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        self.team: Literal["WHITE", "BLACK"] = team

    def __init_subclass__(cls, *, abbreviation: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.abbreviation = abbreviation
        Piece.Pieces[abbreviation] = cls

    def __str__(self) -> str:
        data = PIECES_MAP[self.abbreviation]
        return data[self.team]

    def __repr__(self) -> str:
        return f"{self.team} {self.__class__.__name__}"

    @abstractmethod
    def get_moves(self, pos: Vec2, board: dict[Vec2, "Piece"]) -> list[Vec2]: ...

    @staticmethod
    def create_piece(abbreviation: str, team: Literal["WHITE", "BLACK"]) -> "Piece | None":
        cls = Piece.Pieces.get(abbreviation.upper())
        if cls is None:
            return None
        return cls(team)
    
    @staticmethod
    def in_board(pos: Vec2) -> bool:
        return 1 <= pos.x <= 8 and 1 <= pos.y <= 8
    
    def orthogonal_diagonal(self, pos: Vec2, board: dict[Vec2, "Piece"], mode: tuple[bool, bool], reach: int) -> list[Vec2]:
        moves: list[Vec2] = []
        ortogonal = ((-1,0),(0,-1),(0,1),(1,0))
        diagonal = ((-1,-1),(-1,1),(1,-1),(1,1))

        directions = ((ortogonal if mode[0] else ()) + (diagonal if mode[1] else ()))

        for x, y in directions:
            for i in range(1, reach + 1):
                dest = Vec2(pos.x + x*i, pos.y + y*i)

                if not self.in_board(dest):
                    break

                if dest in board:
                    if board[dest].team != self.team:
                        moves.append(dest)
                    break

                moves.append(dest)

        return moves
    
#all position that piece can move
#check for blocking friendly, or attack enemy
#filter outside of board
#uses index starting from 1 to 8

class Pawn(Piece, abbreviation="P"):
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        super().__init__(team=team)
         
    def get_moves(self, pos: Vec2, board: dict[Vec2, Piece]) -> list[Vec2]:
        moves: list[Vec2] = []

        direction = 1 if self.team == "WHITE" else -1
        
        front = pos.y + direction
        if not self.in_board(Vec2(pos.x, front)):
            return []
        
        if Vec2(pos.x, front) not in board:
            moves.append(Vec2(pos.x, front))

            start_rank = 2 if self.team == "WHITE" else 7
            double_front = pos.y + 2 * direction
            if pos.y == start_rank:
                if Vec2(pos.x, double_front) not in board:
                    moves.append(Vec2(pos.x, double_front))

        for i in (-1,1):
            diag = pos.x + i
            target = Vec2(diag, front)
            if target in board and board[target].team != self.team:
                    moves.append(Vec2(diag,front))

        filtered = [m for m in moves if self.in_board(m)]
        return filtered
    
class Knight(Piece, abbreviation="N"):
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        super().__init__(team=team)

    def get_moves(self, pos: Vec2, board: dict[Vec2, Piece]) -> list[Vec2]:
        moves: list[Vec2] = []

        possible_moves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))

        for x,y in possible_moves:
            dest = Vec2(pos.x+x, pos.y+y)
            if not self.in_board(dest):
                continue
            if dest in board and board[dest].team == self.team:
                continue
            moves.append(dest)

        filtered = [mv for mv in moves if self.in_board(mv)]
        return filtered
    
class Bishop(Piece, abbreviation="B"):
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        super().__init__(team=team)

    def get_moves(self, pos: Vec2, board: dict[Vec2, Piece]) -> list[Vec2]:
        moves: list[Vec2] = self.orthogonal_diagonal(pos, board, (False, True), 8)
        return moves
    
class Rook(Piece, abbreviation="R"):
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        super().__init__(team=team)
        self.moved = False

    def get_moves(self, pos: Vec2, board: dict[Vec2, Piece]) -> list[Vec2]:
        moves: list[Vec2] = self.orthogonal_diagonal(pos, board, (True, False), 8)
        return moves
    
class Queen(Piece, abbreviation="Q"):
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        super().__init__(team=team)

    def get_moves(self, pos: Vec2, board: dict[Vec2, Piece]) -> list[Vec2]:
        moves: list[Vec2] = self.orthogonal_diagonal(pos, board, (True, True), 8)
        return moves
    
class King(Piece, abbreviation="K"):
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        super().__init__(team=team)
        self.moved = False
 
    def get_moves(self, pos: Vec2, board: dict[Vec2, Piece]) -> list[Vec2]:
        moves: list[Vec2] = self.orthogonal_diagonal(pos, board, (True, True), 1)
        return moves
    
    def castle(self, board: dict[Vec2, Piece]) -> list[Vec2]:
        if self.moved:
            return []

        moves: list[Vec2] = []
        rank = 1 if self.team == "WHITE" else 8

        # (rook_position, spaces_between, king_destination)
        castles = [
            (Vec2(1, rank), [Vec2(2, rank), Vec2(3, rank), Vec2(4, rank)], Vec2(3, rank)), #queenside
            (Vec2(8, rank), [Vec2(6, rank), Vec2(7, rank)], Vec2(7, rank)), #kingside
        ]

        for rook_pos, between, king_dest in castles:
            if rook_pos not in board:
                continue

            rook = board[rook_pos]
            if not isinstance(rook, Rook):
                continue
            if rook.team != self.team or rook.moved:
                continue
            if any(square in board for square in between):
                continue

            moves.append(king_dest)

        return moves
    
class yourmom(Piece, abbreviation="M"):
    def __init__(self, team: Literal["WHITE", "BLACK"]):
        super().__init__(team=team)

    def get_moves(self, pos: Vec2, board: dict[Vec2, Piece]) -> list[Vec2]:
        moves: list[Vec2] = []
        for i in range(1,9):
            for j in range(3,7):
                moves.append(Vec2(i,j))
        return moves
