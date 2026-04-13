"""
game/move.py
─────────────
Quantum move representation.

A QuantumMove is a "spooky mark" that exists in superposition
across exactly two board cells simultaneously, until collapse.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class QuantumMove:
    """
    Represents a single quantum (spooky) move placed by a player.

    Attributes:
        player  : 'X' or 'O'
        move_num: Sequential move number for this player (1, 2, 3 …)
        cells   : Tuple of exactly two 1-indexed board cells (e.g. (1, 5))
        label   : Human-readable label, e.g. 'X1', 'O3'
        collapsed: True once the move has been resolved to one cell
        classical_cell: The cell this move collapsed into (None until collapse)
    """
    player: str
    move_num: int
    cells: tuple[int, int]
    collapsed: bool = field(default=False, init=False)
    classical_cell: int | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if len(self.cells) != 2:
            raise ValueError("A QuantumMove must span exactly two cells.")
        if self.cells[0] == self.cells[1]:
            raise ValueError("A QuantumMove cannot span the same cell twice.")
        self.cells = tuple(sorted(self.cells))

    @property
    def label(self) -> str:
        """Short label used on the board, e.g. 'X1'."""
        return f"{self.player}{self.move_num}"

    def collapse_to(self, cell: int) -> None:
        """Mark this move as collapsed to a specific cell."""
        if cell not in self.cells:
            raise ValueError(
                f"Cannot collapse {self.label} to cell {cell}; "
                f"it is only in cells {self.cells}."
            )
        self.collapsed = True
        self.classical_cell = cell

    def __repr__(self) -> str:
        status = (
            f"→cell{self.classical_cell}" if self.collapsed
            else f"∈{self.cells}"
        )
        return f"<QuantumMove {self.label} {status}>"

    def __hash__(self) -> int:
        return hash((self.player, self.move_num))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuantumMove):
            return NotImplemented
        return self.player == other.player and self.move_num == other.move_num
