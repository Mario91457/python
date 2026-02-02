class GameEnded(Exception): pass

class InvalidBoard(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidMove(Exception): 
    def __init__(self, message):
        super().__init__(message)

class InvalidInput(Exception): 
    def __init__(self, message):
        super().__init__(message)