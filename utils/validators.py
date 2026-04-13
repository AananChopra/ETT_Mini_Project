"""
utils/validators.py
────────────────────
Input validation for Quantum Tic-Tac-Toe.
"""

from __future__ import annotations
from config.settings import TOTAL_CELLS


class ValidationError(Exception):
    """Raised when user input is invalid."""
    pass


def validate_cell_number(value: str) -> int:
    """
    Parse and validate a single cell number string.

    Args:
        value: Raw string input from user.

    Returns:
        Integer cell number in [1, 9].

    Raises:
        ValidationError on bad input.
    """
    try:
        cell = int(value.strip())
    except ValueError:
        raise ValidationError(f"'{value}' is not a valid integer.")

    if not (1 <= cell <= TOTAL_CELLS):
        raise ValidationError(
            f"Cell {cell} is out of range. Choose between 1 and {TOTAL_CELLS}."
        )
    return cell


def validate_two_cells(a_str: str, b_str: str) -> tuple[int, int]:
    """
    Validate two distinct cell inputs.

    Args:
        a_str, b_str: Raw string inputs.

    Returns:
        Tuple of two distinct cell integers.

    Raises:
        ValidationError if same cell or out of range.
    """
    a = validate_cell_number(a_str)
    b = validate_cell_number(b_str)
    if a == b:
        raise ValidationError(
            "You must choose two DIFFERENT cells for a quantum move."
        )
    return a, b


def validate_move_cells(cell_a: int, cell_b: int, board) -> None:
    """
    Ensure both target cells accept a new quantum move (not classically collapsed).

    Args:
        cell_a, cell_b: 1-indexed cell numbers.
        board: Board instance.

    Raises:
        ValidationError if either cell is already classically occupied.
    """
    for cell in (cell_a, cell_b):
        if board.is_classical(cell):
            mark = board.classical_mark(cell)
            raise ValidationError(
                f"Cell {cell} is already classically occupied by '{mark}'. "
                "Choose a different cell."
            )


def validate_collapse_cell(value: str, cycle_cells: list[int], board) -> int:
    """
    Validate the player's chosen collapse cell during a cyclic entanglement.

    The chosen cell must be part of the detected cycle and must be quantum
    (not already collapsed).

    Args:
        value      : Raw string from user.
        cycle_cells: List of cell ids forming the cycle.
        board      : Board instance.

    Returns:
        Valid cell integer.

    Raises:
        ValidationError on bad input.
    """
    cell = validate_cell_number(value)
    if cell not in cycle_cells:
        raise ValidationError(
            f"Cell {cell} is not part of the entanglement cycle {cycle_cells}. "
            "Please choose one of those cells."
        )
    if board.is_classical(cell):
        raise ValidationError(
            f"Cell {cell} has already been classically collapsed."
        )
    return cell
