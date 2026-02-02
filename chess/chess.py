from enum import Enum, auto
from typing import Literal
from chess_pieces import Piece
from chess_pieces import King
from chess_pieces import Rook
from chess_pieces import Pawn
from utils.Vec2 import Vec2
import exceptions

#FEN_notation = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

class GameStatus(Enum):
    ONGOING = auto()
    CHECK = auto()
    CHECKMATE = auto()
    STALEMATE = auto()

    PROMOTING = auto()

class Chess():
    def __init__(self, fen_notation: str):
        self.board: dict[Vec2, Piece] = self._create_board(fen_notation)
        self.current_team: Literal["WHITE", "BLACK"] = "WHITE"

        self.last_move: tuple[Vec2, Vec2] | None = None #en passant

        self.promoting_pawn_pos: Vec2 | None = None
        self.promoting_team: Literal["WHITE", "BLACK"] | None = None

        self.status = self._board_status()


        # self._print_board(self.board)

    #======================PUBLIC METHODS======================

    def move(self, pos_1: Vec2, pos_2: Vec2): 
        """pos_1 is the piece to move, pos_2 is where to move"""
        if self.status in (GameStatus.CHECKMATE, GameStatus.STALEMATE):
            raise exceptions.GameEnded("Game is already over")
        if self.status == GameStatus.PROMOTING:
            raise exceptions.InvalidMove("Must promote pawn first")
        
        piece = self.board.get(pos_1)
        if not piece or piece.team != self.current_team:
            raise exceptions.InvalidMove("Invalid piece selection")
        
        if pos_2 in self.board and self.board[pos_2].team == self.current_team:
            raise exceptions.InvalidMove("Cannot capture your own team pieces")
        
        #should never trigger, unless a special piece is used
        if pos_2 in self.board and piece == self.board[pos_2]:
            raise exceptions.InvalidMove("Cannot capture yourself")

        legal_moves = self.get_piece_moves(pos_1)
        if pos_2 not in legal_moves:
            raise exceptions.InvalidMove("Illegal move")
        
        #----------------------------------------------------

        #castling (move rooks)
        if isinstance(piece, King) and abs(pos_2.x - pos_1.x) == 2:
            rook_x = 8 if pos_2.x > pos_1.x else 1
            rook_dest_x = pos_2.x - 1 if pos_2.x > pos_1.x else pos_2.x + 1
            rook_pos = Vec2(rook_x, pos_1.y)
            self.board[Vec2(rook_dest_x, pos_1.y)] = self.board.pop(rook_pos)

        #en Passant capturing
        if isinstance(piece, Pawn) and pos_1.x != pos_2.x and pos_2 not in self.board:
            self.board.pop(Vec2(pos_2.x, pos_1.y), None)

        self.board[pos_2] = self.board.pop(pos_1)

        if isinstance(piece, (King, Rook)):
            piece.moved = True
            
        last_rank = 8 if piece.team == "WHITE" else 1
        if isinstance(piece, Pawn) and  pos_2.y == last_rank:
            self.status = GameStatus.PROMOTING
            self.promoting_pawn_pos = pos_2
            self.promoting_team = piece.team
            return

        self.last_move = (pos_1, pos_2)
        self.current_team = self._enemy(self.current_team)
        self.status = self._board_status()

    def get_piece_moves(self, pos: Vec2) -> list[Vec2]: 
        """Returns the legal moves for the piece"""
        piece = self.board.get(pos)
        if not piece or piece.team != self.current_team:
            return []
        
        moves = piece.get_moves(pos, self.board)
        legal_moves = []

        #castling pseudo-moves
        if isinstance(piece, King) and not piece.moved:
            if not self._is_in_check(self.board, self.current_team):
                moves.extend(self._get_castle_moves(piece, pos))

        if isinstance(piece, Pawn):
            moves.extend(self._get_en_passant_moves(pos, piece))
        
        #handles: can the piece checking the king be captured or blocked, avoids reveal checks
        for move in moves:
            if isinstance(piece, King) and abs(move.x - pos.x) == 2:
                #is king and castle
                step = 1 if move.x > pos.x else -1
                path = [Vec2(pos.x + step, pos.y), Vec2(pos.x + 2 * step, pos.y)]

                if any(self._is_square_attacked(self.board, sq, self.current_team) for sq in path):
                    continue

            board_copy = self._simulate_move(self.board, pos, move)
            if not self._is_in_check(board_copy, self.current_team):
                legal_moves.append(move)

        return legal_moves #returns the moves that doesnt get the king in check
    
    def promote(self, piece_type: Literal["Q", "R", "B", "N"]):
        if self.status != GameStatus.PROMOTING:
            raise exceptions.InvalidMove("No pawn to promote")
        
        if not self.promoting_pawn_pos or not self.promoting_team:
            self.status = GameStatus.ONGOING
            raise exceptions.InvalidMove("Position or team not found for pawn to promote")
        
        if piece_type not in ("Q", "R", "B", "N"):
            raise exceptions.InvalidInput("Invalid promotion piece")
        
        pos, team = self.promoting_pawn_pos, self.promoting_team

        piece = Piece.create_piece(piece_type, team)
        if piece is None:
            raise exceptions.InvalidInput("Invalid piece to promote") #should never trigger
            
        del self.board[pos]
        self.board[pos] = piece
    
        self.promoting_pawn_pos = self.promoting_team = None
    
        self.current_team = self._enemy(team)
        self.status = self._board_status()

    def undo(self):
        pass
    
    #======================PRIVATE METHODS======================

    def _get_en_passant_moves(self, pos: Vec2, piece: Pawn) -> list[Vec2]:
            ep_moves = []
            if not self.last_move: return []

            last_start, last_end = self.last_move
            last_piece = self.board.get(last_end)

            if isinstance(last_piece, Pawn) and abs(last_start.y - last_end.y) == 2:
                if last_end.y == pos.y and abs(last_end.x - pos.x) == 1:
                    direction = 1 if piece.team == "WHITE" else -1
                    ep_moves.append(Vec2(last_end.x, pos.y + direction))
            return ep_moves

    def _get_castle_moves(self, king: King, pos: Vec2) -> list[Vec2]:
        return king.castle(self.board)
    
    #returns all of the legal moves for the team
    def _get_all_legal_moves(self, board: dict[Vec2, Piece], team: Literal["WHITE", "BLACK"]) -> list[Vec2]:
        moves = []
        original_team = self.current_team
        self.current_team = team

        for pos, piece in board.items():
            if piece.team == team:
                moves.extend(self.get_piece_moves(pos))

        self.current_team = original_team
        return moves

    #returns pseudo moves
    @staticmethod
    def _get_team_moves(board: dict[Vec2, Piece], team: Literal["WHITE", "BLACK"]) -> list[Vec2]:
        all_moves = []
        for pos, piece in board.items():
            if piece.team == team:
                all_moves.extend(piece.get_moves(pos, board))

        return all_moves

    #check if the team is in check
    def _is_in_check(self, board: dict[Vec2, Piece], team: Literal["WHITE", "BLACK"]) -> bool:
        enemy = self._enemy(team)
        king_pos = self._get_king_pos(board, team)
        return king_pos in self._get_team_moves(board, enemy)
    
    def _is_king_in_checkmate(self, board: dict[Vec2, Piece], team: Literal["WHITE", "BLACK"]) -> bool:
        king = self._get_king_pos(board, team)
        king_moves = board[king].get_moves(king, board)
        for moves in king_moves:
            simulated_board = self._simulate_move(board, king, moves)
            if not self._is_in_check(simulated_board, team):
                return False
        return True

    #======================HELPERS======================
    
    def _board_status(self)-> GameStatus:
        in_check = self._is_in_check(self.board, self.current_team)
        total_legal_moves = len(self._get_all_legal_moves(self.board, self.current_team))

        if in_check and total_legal_moves == 0:
            return GameStatus.CHECKMATE
        elif not in_check and total_legal_moves == 0:
            return GameStatus.STALEMATE
        elif in_check and total_legal_moves != 0:
            #check if the king can capture the piece that is attacking, if not then is a checkmate
            if self._is_king_in_checkmate(self.board, self.current_team):
                return GameStatus.CHECKMATE
            return GameStatus.CHECK
        return GameStatus.ONGOING

    def _is_square_attacked(self, board: dict[Vec2, Piece], square: Vec2, team: Literal["WHITE", "BLACK"]) -> bool:
        enemy = self._enemy(team)
        return square in self._get_team_moves(board, enemy)

    @staticmethod
    def _get_king_pos(board: dict[Vec2, Piece], team: Literal["WHITE", "BLACK"]) -> Vec2:
        for pos, piece in board.items():
            if piece.team == team and isinstance(piece, King):
                return pos
        raise ValueError(f"No king found")

    @staticmethod
    def _simulate_move(board: dict[Vec2, Piece], pos_1: Vec2, pos_2: Vec2) -> dict[Vec2, Piece]:
        new_board = board.copy()
        new_board[pos_2] = new_board.pop(pos_1)
        return new_board
    
    @staticmethod
    def _enemy(team: Literal["WHITE", "BLACK"]) -> Literal["WHITE", "BLACK"]:
        return "BLACK" if team == "WHITE" else "WHITE"

    @staticmethod
    def _create_board(fen_notation: str) -> dict[Vec2, Piece]:
        board: dict[Vec2, Piece] = {}
        rows = fen_notation.split("/")
        
        if len(rows) != 8:
            raise exceptions.InvalidBoard("Invalid FEN")
    
        for y_index, row in enumerate(rows):
            x = 1
            y = 8 - y_index
    
            for char in row:
                if char.isdigit():
                    x += int(char)
                    continue
                
                team = "WHITE" if char.isupper() else "BLACK"
                pos = Vec2(x, y)
    
                piece = Piece.create_piece(char, team)

                if piece:
                    board[pos] = piece
    
                x += 1
    
        return board
       
    #for debugging
    @staticmethod
    def _print_board(board):
        p = [["." for _ in range(8)] for _ in range(8)]

        for pos, piece in board.items():
            row = 8 - pos.y
            col = pos.x - 1
            p[row][col] = str(piece)

        lol = 8
        for row in p:
            print(lol, " ".join(row))
            lol-=1
        print("  A B C D E F G H")
