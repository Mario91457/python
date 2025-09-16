import random
import msvcrt
import sys
from time import sleep
from typing import List, Optional
from colors import APPEARANCE

MOVEMENTS = {  # y, x
    b'H': (-1, 0),  # up
    b'P': (1, 0),   # down
    b'K': (0, -1),  # left
    b'M': (0, 1),   # right
}

OPPOSITES = {
    b'H': b'P',
    b'P': b'H',
    b'K': b'M',
    b'M': b'K',
}

def enable_vt_mode():
    """Enable ANSI escape processing on Windows consoles (no-op on other OS)."""
    if __import__("os").name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            ENABLE_VT = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT)
    except Exception:
        # best-effort: if it fails, ANSI may still work in some terminals
        pass

def clear_screen():
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


class SnakeGame:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.running = True
        self.current_input: Optional[bytes] = None
        self.last_direction: bytes = b'M'  # default moving right
        self.score = 0

        self.game_map = [[APPEARANCE["empty"] for _ in range(width)] for _ in range(height)]

        center_y, center_x = height // 2, width // 2
        self.snake_pos: List[List[int]] = [[center_y, center_x]]
        self.head = [center_y, center_x]
        self.size = 1

        self.game_map[center_y][center_x] = APPEARANCE["snake"]
        self._spawn_apple()

    def _spawn_apple(self):
        """Place a new apple"""
        while True:
            y, x = random.randrange(self.height), random.randrange(self.width)
            if self.game_map[y][x] == APPEARANCE["empty"]:
                self.game_map[y][x] = APPEARANCE["apple"]
                break

    def _collision(self, direction: tuple[int, int]) -> str:
        """Check collision"""
        next_y, next_x = self.head[0] + direction[0], self.head[1] + direction[1]

        if not (0 <= next_y < self.height and 0 <= next_x < self.width):
            return "Wall"
        return self.game_map[next_y][next_x]

    def update(self, direction: tuple[int, int]) -> bool:
        """Move snake one step"""
        collide = self._collision(direction)
        growing = False

        if collide == APPEARANCE["apple"]:
            self.size += 1
            self.score += 1
            self._spawn_apple()
            growing = True
        elif collide in (APPEARANCE["snake"], "Wall"):
            return False

        # Move head
        self.game_map[self.head[0]][self.head[1]] = APPEARANCE["snake"]
        self.head[0] += direction[0]
        self.head[1] += direction[1]
        self.game_map[self.head[0]][self.head[1]] = APPEARANCE["snake_head"]
        self.snake_pos.append(self.head[:])

        if not growing:
            # Remove tail
            tail_y, tail_x = self.snake_pos.pop(0)
            self.game_map[tail_y][tail_x] = APPEARANCE["empty"]

        return True

    def draw(self):
        clear_screen()
        rows = [APPEARANCE["walls"] + "".join(row) + APPEARANCE["walls"] for row in self.game_map]
        output = f"Score: {self.score}\n" + "\n".join(rows)
        print(output, end="")

    def handle_input(self):
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in {b'\x00', b'\xe0'}:
                key = msvcrt.getch()
                if key in MOVEMENTS:
                    if OPPOSITES.get(self.last_direction) != key:
                        self.current_input = key


def main():
    enable_vt_mode()
    try:
        size_x = int(input("size in X: "))
        size_y = int(input("size in Y: "))
        Delay = int(input("Delay (ms): "))/1000
    except ValueError:
        print("Invalid input. Must be integers.")
        return

    if size_x <= 0 or size_y <= 0:
        print("Error: Both size in X and Y must be greater than 0")
        return

    game = SnakeGame(size_x, size_y)

    try:
        while game.running:
            game.handle_input()

            if game.current_input:
                game.last_direction = game.current_input
                game.current_input = None

            direction = MOVEMENTS[game.last_direction]
            if not game.update(direction):
                game.draw()
                print("\nGame Over!")
                break

            game.draw()
            sleep(Delay)
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
