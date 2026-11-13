from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass


Position = tuple[int, int]


@dataclass(frozen=True)
class Move:

    start: Position
    end: Position


class IllegalMoveError(ValueError):
    """Raised when a requested peg jump is invalid."""


class SolitaireBoard(ABC):
    """Defines playable positions and jump directions for a board shape."""

    ORTHOGONAL = ((-1, 0), (1, 0), (0, -1), (0, 1))
    DIRECTIONS = ORTHOGONAL + ((-1, -1), (-1, 1), (1, -1), (1, 1))

    def __init__(self, size: int) -> None:
        self.size = size
        middle = size // 2
        self.holes = frozenset(
            (row, col)
            for row in range(size)
            for col in range(size)
            if self.contains(row - middle, col - middle)
        )

    @abstractmethod
    def contains(self, row_offset: int, col_offset: int) -> bool:
        """Return whether the position relative to the center is playable."""


class EnglishBoard(SolitaireBoard):
    def contains(self, row_offset: int, col_offset: int) -> bool:
        arm_width = max(1, self.size // 3)
        half_width = arm_width // 2
        return abs(row_offset) <= half_width or abs(col_offset) <= half_width


class HexagonBoard(SolitaireBoard):
    DIRECTIONS = SolitaireBoard.ORTHOGONAL + ((-1, 1), (1, -1))

    def contains(self, row_offset: int, col_offset: int) -> bool:
        return max(abs(row_offset), abs(col_offset),
                   abs(row_offset + col_offset)) <= self.size // 2


class DiamondBoard(SolitaireBoard):
    def contains(self, row_offset: int, col_offset: int) -> bool:
        return abs(row_offset) + abs(col_offset) <= self.size // 2


BOARD_CLASSES = {
    "English": EnglishBoard,
    "Hexagon": HexagonBoard,
    "Diamond": DiamondBoard,
}


class SolitaireGame:
    """Owns the state and rules shared by all board shapes."""

    BOARD_TYPES = tuple(BOARD_CLASSES)
    SIZES = (5, 7, 9)

    def __init__(
        self,
        board_type: str = "English",
        size: int = 7,
        pegs: set[Position] | None = None,
    ) -> None:
        if board_type not in self.BOARD_TYPES:
            raise ValueError(f"Unknown board type: {board_type}")
        if size not in self.SIZES:
            raise ValueError("Board size must be 5, 7, or 9")

        self.board_type = board_type
        self.size = size
        self.board = BOARD_CLASSES[board_type](size)
        self.holes = self.board.holes
        center = (size // 2, size // 2)
        initial = set(self.holes - {center}) if pegs is None else set(pegs)
        if not initial.issubset(self.holes):
            raise ValueError("A peg cannot be outside the board")
        self._pegs = initial
        self._history: list[frozenset[Position]] = []

    @property
    def pegs(self) -> frozenset[Position]:
        return frozenset(self._pegs)

    @property
    def remaining(self) -> int:
        return len(self._pegs)

    def legal_moves(self) -> list[Move]:
        moves = []
        empty_holes = self.holes - self._pegs
        for row, col in sorted(self._pegs):
            for dr, dc in self.board.DIRECTIONS:
                jumped = (row + dr, col + dc)
                end = (row + 2 * dr, col + 2 * dc)
                if jumped in self._pegs and end in empty_holes:
                    moves.append(Move((row, col), end))
        return moves

    def move(self, start: Position, end: Position) -> None:
        if Move(start, end) not in self.legal_moves():
            raise IllegalMoveError(f"Illegal jump: {start} to {end}")
        self._history.append(self.pegs)
        midpoint = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        self._pegs.remove(start)
        self._pegs.remove(midpoint)
        self._pegs.add(end)

    def undo(self) -> bool:
        if not self._history:
            return False
        self._pegs = set(self._history.pop())
        return True

    def random_move(self, rng: random.Random | None = None) -> Move | None:
        moves = self.legal_moves()
        if not moves:
            return None
        chosen = (rng or random).choice(moves)
        self.move(chosen.start, chosen.end)
        return chosen

    def rating(self) -> str | None:
        if self.legal_moves():
            return None
        if self.remaining == 1:
            return "Outstanding"
        if self.remaining == 2:
            return "Very Good"
        if self.remaining == 3:
            return "Good"
        return "Average"