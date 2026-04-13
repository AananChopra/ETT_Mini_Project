"""
game/game_engine.py
────────────────────
Core game loop and rule orchestration for Quantum Tic-Tac-Toe.

Flow per turn:
    1. Show current board.
    2. Active player picks two cells → QuantumMove placed in superposition.
    3. Check for entanglement cycle.
       3a. If cycle found → resolve_collapse():
           - Non-creating player picks which cyclic cell to observe.
           - Qiskit measures which quantum move wins that cell.
           - Forced collapses propagate through the board.
    4. Check for winner or draw.
    5. Switch active player.
"""

from __future__ import annotations
from game.board import Board
from game.move import QuantumMove
from game.player import Player
from quantum.measurement import quantum_choice
from utils import display as ui
from utils.validators import (
    ValidationError,
    validate_two_cells,
    validate_move_cells,
    validate_collapse_cell,
)
from config.settings import TOTAL_CELLS


class GameEngine:
    """
    Orchestrates the full Quantum Tic-Tac-Toe game.

    Args:
        player_x: Player with mark 'X'.
        player_o: Player with mark 'O'.
    """

    def __init__(self, player_x: Player, player_o: Player) -> None:
        self.board = Board()
        self.players = [player_x, player_o]
        self.current_idx = 0      # index into self.players
        self.turn_count = 0
        self.finished = False
        self.winner: str | None = None

    # ── Public API ────────────────────────────────────────────────────────

    @property
    def current_player(self) -> Player:
        return self.players[self.current_idx]

    @property
    def other_player(self) -> Player:
        return self.players[1 - self.current_idx]

    def run(self) -> None:
        """Main game loop."""
        ui.print_rule("  Game Start  ")
        ui.render_board(self.board)

        while not self.finished:
            self._take_turn()

        self._end_game()

    # ── Private Helpers ───────────────────────────────────────────────────

    def _take_turn(self) -> None:
        """Execute one full turn for the current player."""
        player = self.current_player
        move_num = player.next_move_num()

        ui.print_turn_header(player.name, player.mark, move_num)
        ui.print_quantum_state_info(self.board)

        # ── Get valid two-cell input ──────────────────────────────────────
        move = self._get_player_move(player, move_num)

        # ── Place on board ────────────────────────────────────────────────
        self.board.place_quantum_move(move)
        player.register_move(move)
        self.turn_count += 1

        ui.print_success(
            f"{player.mark}{move_num} placed in superposition: "
            f"cells {move.cells[0]} & {move.cells[1]}"
        )
        ui.render_board(self.board)

        # ── Check for entanglement cycle ──────────────────────────────────
        cycle = self.board.find_cycle()
        if cycle:
            ui.print_collapse_announcement(cycle)
            self._resolve_collapse(cycle)

            # After collapse, render updated board
            ui.render_board(self.board, self.board.winning_line())

            # Check win / draw after collapse
            winner = self.board.check_winner()
            if winner:
                self.winner = winner
                self.finished = True
                return
            if self.board.is_draw():
                self.finished = True
                return

        # ── Advance turn ──────────────────────────────────────────────────
        self._switch_player()

    def _get_player_move(self, player: Player, move_num: int) -> QuantumMove:
        """Prompt the player to select two distinct, available cells."""
        while True:
            try:
                raw = ui.prompt(
                    f"Enter two cell numbers for [bold]{player.mark}{move_num}[/bold] "
                    "(e.g. '1 5'  or  '3 7'):"
                )
                parts = raw.split()
                if len(parts) != 2:
                    raise ValidationError("Please enter exactly TWO cell numbers separated by space.")

                cell_a, cell_b = validate_two_cells(parts[0], parts[1])
                validate_move_cells(cell_a, cell_b, self.board)

                return QuantumMove(
                    player=player.mark,
                    move_num=move_num,
                    cells=(cell_a, cell_b),
                )
            except ValidationError as exc:
                ui.print_error(str(exc))

    def _resolve_collapse(self, cycle: list[int]) -> None:
        """
        Handle entanglement collapse:
        1. The player who did NOT create the cycle picks a cell to observe.
        2. Qiskit measurement picks the winning quantum move in that cell.
        3. Collapse propagates through entangled moves.
        """
        observer = self.other_player   # non-creating player decides
        ui.print_info(
            f"[bold]{observer.name}[/bold] (the non-creating player) "
            f"chooses which cycle cell to observe first."
        )
        ui.print_info(f"Cycle cells: {cycle}")

        # ── Step 1: observer picks a cycle cell ───────────────────────────
        first_cell = self._get_collapse_cell(observer, cycle)

        # ── Step 2: quantum measurement picks the winner in that cell ─────
        candidates = [
            m for m in self.board.quantum_moves(first_cell)
            if not m.collapsed
        ]
        if not candidates:
            ui.print_warning(f"No quantum moves in cell {first_cell} to collapse.")
            return

        ui.print_info(
            f"Collapsing cell {first_cell} — candidates: "
            f"{[m.label for m in candidates]}"
        )

        # Quantum measurement selects the surviving move
        winner_move: QuantumMove = self._quantum_measure(candidates)

        ui.print_success(
            f"⚛ Quantum measurement → [{winner_move.player}] "
            f"{winner_move.label} survives in cell {first_cell}!"
        )
        ui.print_collapse_animation(first_cell, winner_move.player)

        # ── Step 3: collapse the chosen cell ─────────────────────────────
        self.board.collapse_cell(first_cell, winner_move)

        # ── Step 4: propagate forced collapses ────────────────────────────
        self._propagate_all_forced()

    def _get_collapse_cell(self, observer: Player, cycle: list[int]) -> int:
        """Prompt the observer to pick a cell from the cycle."""
        while True:
            try:
                raw = ui.prompt(
                    f"[bold]{observer.name}[/bold], choose a cell from cycle "
                    f"{cycle} to collapse:"
                )
                return validate_collapse_cell(raw, cycle, self.board)
            except ValidationError as exc:
                ui.print_error(str(exc))

    def _quantum_measure(self, candidates: list[QuantumMove]) -> QuantumMove:
        """
        Use Qiskit to select one surviving QuantumMove from candidates.

        Each candidate is equally probable (uniform superposition).
        """
        idx = quantum_choice(len(candidates))
        return candidates[idx]

    def _propagate_all_forced(self) -> None:
        """
        After an initial collapse, iteratively force-collapse any quantum move
        whose partner cell is now classical (so it must collapse to this cell).
        """
        changed = True
        while changed:
            changed = False
            for cell in range(1, TOTAL_CELLS + 1):
                if self.board.is_classical(cell):
                    continue
                for move in list(self.board.quantum_moves(cell)):
                    if move.collapsed:
                        continue
                    partner = next(c for c in move.cells if c != cell)
                    if self.board.is_classical(partner) or move.collapsed:
                        # This move is forced to land in `cell`
                        # But first check the other direction:
                        # if the move already collapsed elsewhere, skip
                        if move.collapsed:
                            continue
                        ui.print_info(
                            f"  Forced: {move.label} → cell {cell} "
                            f"(partner cell {partner} is classical)"
                        )
                        ui.print_collapse_animation(cell, move.player)
                        self.board.collapse_cell(cell, move)
                        changed = True
                        break   # restart inner loop after mutation

    def _switch_player(self) -> None:
        self.current_idx = 1 - self.current_idx

    def _end_game(self) -> None:
        """Handle end-of-game display."""
        ui.print_rule()
        if self.winner:
            winning_player = next(
                p for p in self.players if p.mark == self.winner
            )
            ui.render_board(self.board, self.board.winning_line())
            ui.print_winner(winning_player.name, self.winner)
        else:
            ui.render_board(self.board)
            ui.print_draw()
