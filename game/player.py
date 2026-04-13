"""
game/player.py
───────────────
Player data model for Quantum Tic-Tac-Toe.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from game.move import QuantumMove


@dataclass
class Player:
    """
    Represents a human player.

    Attributes:
        name     : Display name of the player.
        mark     : 'X' or 'O' — the player's classical symbol.
        move_count: How many quantum moves this player has made so far.
        moves    : All QuantumMove objects placed by this player.
    """
    name: str
    mark: str           # 'X' or 'O'
    move_count: int = field(default=0, init=False)
    moves: list[QuantumMove] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.mark not in ("X", "O"):
            raise ValueError(f"Player mark must be 'X' or 'O', got '{self.mark}'.")

    def next_move_num(self) -> int:
        """Return the move number for the upcoming move."""
        return self.move_count + 1

    def register_move(self, move: QuantumMove) -> None:
        """Record a completed quantum move for this player."""
        self.moves.append(move)
        self.move_count += 1

    def __repr__(self) -> str:
        return f"<Player {self.name!r} ({self.mark}) moves={self.move_count}>"
