"""
game/board.py
──────────────
Board state management for Quantum Tic-Tac-Toe.

The 3×3 board uses 1-indexed cells (1-9):
    1 | 2 | 3
    ---------
    4 | 5 | 6
    ---------
    7 | 8 | 9

Each cell can hold:
  - An empty list []           → unoccupied
  - A list of QuantumMove(s)   → superposed (quantum state)
  - A single string 'X'/'O'   → classically collapsed
"""

from __future__ import annotations
from typing import Optional
from game.move import QuantumMove
from config.settings import BOARD_SIZE, TOTAL_CELLS

# Winning lines (1-indexed cell numbers)
WIN_LINES: list[tuple[int, int, int]] = [
    (1, 2, 3), (4, 5, 6), (7, 8, 9),   # rows
    (1, 4, 7), (2, 5, 8), (3, 6, 9),   # cols
    (1, 5, 9), (3, 5, 7),              # diagonals
]


class Board:
    """
    Manages the quantum board state.

    Internal representation:
        _cells: dict[int, list[QuantumMove] | str]
            cell → []           (empty)
            cell → [move, ...]  (quantum superposition)
            cell → 'X' or 'O'  (collapsed classical)
    """

    def __init__(self) -> None:
        self._cells: dict[int, list[QuantumMove] | str] = {
            i: [] for i in range(1, TOTAL_CELLS + 1)
        }

    # ── Queries ───────────────────────────────────────────────────────────

    def is_empty(self, cell: int) -> bool:
        """True if cell has no marks at all."""
        v = self._cells[cell]
        return isinstance(v, list) and len(v) == 0

    def is_classical(self, cell: int) -> bool:
        """True if cell has collapsed to a classical X or O."""
        return isinstance(self._cells[cell], str)

    def is_quantum(self, cell: int) -> bool:
        """True if cell contains quantum (superposed) moves."""
        v = self._cells[cell]
        return isinstance(v, list) and len(v) > 0

    def classical_mark(self, cell: int) -> Optional[str]:
        """Return 'X', 'O', or None if not collapsed."""
        v = self._cells[cell]
        return v if isinstance(v, str) else None

    def quantum_moves(self, cell: int) -> list[QuantumMove]:
        """Return list of QuantumMoves in a cell (empty if none)."""
        v = self._cells[cell]
        return v if isinstance(v, list) else []

    def available_cells(self) -> list[int]:
        """Cells that are empty (can accept a new quantum move endpoint)."""
        return [c for c in range(1, TOTAL_CELLS + 1) if not self.is_classical(c)]

    def is_cell_available_for_move(self, cell: int) -> bool:
        """A cell is available if it is not yet classically collapsed."""
        return not self.is_classical(cell)

    # ── Mutations ─────────────────────────────────────────────────────────

    def place_quantum_move(self, move: QuantumMove) -> None:
        """Add a quantum move to both of its superposed cells."""
        for cell in move.cells:
            if self.is_classical(cell):
                raise ValueError(
                    f"Cannot place quantum move in already-collapsed cell {cell}."
                )
            self._cells[cell].append(move)

    def collapse_cell(self, cell: int, winner_move: QuantumMove) -> None:
        """
        Collapse a cell to the classical mark of `winner_move`.
        All other quantum moves that were in this cell are evicted
        from it (they still exist in their other superposed cell).
        """
        if self.is_classical(cell):
            return   # already collapsed, no-op

        # Record classical winner
        self._cells[cell] = winner_move.player
        winner_move.collapse_to(cell)

        # Evict other moves from this cell (they survive in their partner cell)
        # Nothing to do here storage-wise: the dict entry is now a string.

    def propagate_collapses(self, collapsed_cells: set[int]) -> None:
        """
        After collapsing some cells, any quantum move whose one cell
        was already collapsed must be forced to collapse into its other cell.
        Repeat until no more forced collapses remain.
        """
        changed = True
        while changed:
            changed = False
            for cell in range(1, TOTAL_CELLS + 1):
                if self.is_classical(cell):
                    continue
                moves_here = self.quantum_moves(cell)
                forced = [
                    m for m in moves_here
                    if not m.collapsed and self.is_classical(
                        next(c for c in m.cells if c != cell)
                    )
                ]
                for m in forced:
                    # The partner cell is already classical — force this cell
                    self.collapse_cell(cell, m)
                    changed = True
                    break   # restart scan after each collapse

    # ── Cycle Detection ───────────────────────────────────────────────────

    def build_quantum_graph(
        self,
    ) -> dict[int, list[QuantumMove]]:
        """
        Build an adjacency structure for entanglement cycle detection.

        Returns a dict: cell → list of QuantumMove objects that connect
        this cell to another via superposition.
        """
        graph: dict[int, list[QuantumMove]] = {
            i: [] for i in range(1, TOTAL_CELLS + 1)
        }
        for cell in range(1, TOTAL_CELLS + 1):
            for move in self.quantum_moves(cell):
                if not move.collapsed:
                    graph[cell].append(move)
        return graph

    def find_cycle(self) -> Optional[list[int]]:
        """
        Detect an entanglement cycle in the quantum graph using DFS.

        Returns a list of cell ids forming the cycle, or None.
        """
        graph = self.build_quantum_graph()
        visited: set[int] = set()
        path: list[int] = []

        def dfs(node: int, came_from_move: Optional[QuantumMove]) -> Optional[list[int]]:
            if node in visited:
                # Cycle found — extract the cycle portion
                idx = path.index(node)
                return path[idx:]

            visited.add(node)
            path.append(node)

            for move in graph[node]:
                if move.collapsed:
                    continue
                neighbor = next((c for c in move.cells if c != node), None)
                if neighbor is None:
                    continue
                # Don't traverse back the same edge we came from
                if move == came_from_move:
                    continue
                result = dfs(neighbor, move)
                if result is not None:
                    return result

            path.pop()
            visited.discard(node)
            return None

        for start in range(1, TOTAL_CELLS + 1):
            if graph[start] and start not in visited:
                result = dfs(start, None)
                if result:
                    return result

        return None

    # ── Win Detection ─────────────────────────────────────────────────────

    def check_winner(self) -> Optional[str]:
        """
        Check if any player has won on the classical (collapsed) board.

        Returns 'X', 'O', or None.
        """
        for a, b, c in WIN_LINES:
            marks = [self.classical_mark(a), self.classical_mark(b), self.classical_mark(c)]
            if marks[0] and marks[0] == marks[1] == marks[2]:
                return marks[0]
        return None

    def winning_line(self) -> Optional[tuple[int, int, int]]:
        """Return the winning triple of cells, or None."""
        for line in WIN_LINES:
            a, b, c = line
            marks = [self.classical_mark(a), self.classical_mark(b), self.classical_mark(c)]
            if marks[0] and marks[0] == marks[1] == marks[2]:
                return line
        return None

    def is_full(self) -> bool:
        """True when every cell is classically collapsed."""
        return all(self.is_classical(c) for c in range(1, TOTAL_CELLS + 1))

    def is_draw(self) -> bool:
        """True if board is full with no winner."""
        return self.is_full() and self.check_winner() is None

    # ── Raw Access ────────────────────────────────────────────────────────

    def raw(self, cell: int):
        return self._cells[cell]

    def __repr__(self) -> str:
        rows = []
        for row in range(BOARD_SIZE):
            cells = [str(self._cells[row * BOARD_SIZE + col + 1]) for col in range(BOARD_SIZE)]
            rows.append(" | ".join(cells))
        return "\n".join(rows)
