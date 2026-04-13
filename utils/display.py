"""
utils/display.py
─────────────────
Rich CLI board rendering for Quantum Tic-Tac-Toe.

Uses the `rich` library for coloured, styled terminal output.
"""

from __future__ import annotations
import time
from game.move import QuantumMove  # noqa: F401 – used in type hints
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from rich.rule import Rule
from config.settings import BOARD_SIZE, TOTAL_CELLS, COLLAPSE_ANIMATION_DELAY

console = Console()

# ── Colour palette ─────────────────────────────────────────────────────────────
CLR_X         = "bold cyan"
CLR_O         = "bold magenta"
CLR_QUANTUM   = "dim yellow"
CLR_EMPTY     = "dim white"
CLR_COLLAPSE  = "bold green"
CLR_TITLE     = "bold white on dark_blue"
CLR_WARN      = "bold red"
CLR_INFO      = "bold blue"
CLR_HIGHLIGHT = "bold yellow on dark_red"


def _cell_text(cell: int, board) -> Text:
    """
    Build a Rich Text object for a single board cell.

    - Classical X → cyan bold
    - Classical O → magenta bold
    - Quantum moves → dim yellow, listed compactly
    - Empty → dim cell number hint
    """
    if board.is_classical(cell):
        mark = board.classical_mark(cell)
        style = CLR_X if mark == "X" else CLR_O
        return Text(f"  {mark}  ", style=style, justify="center")

    moves = board.quantum_moves(cell)
    if moves:
        labels = " ".join(m.label for m in moves if not m.collapsed)
        t = Text(labels or "?", style=CLR_QUANTUM, justify="center")
        return t

    # Empty: show cell number as hint
    return Text(f" [{cell}] ", style=CLR_EMPTY, justify="center")


def render_board(board, winning_line: tuple | None = None) -> None:
    """
    Print the full 3×3 quantum board to the terminal.

    Highlights the winning cells if `winning_line` is provided.
    """
    table = Table(
        show_header=False,
        box=box.HEAVY_HEAD,
        padding=(1, 2),
        expand=False,
        border_style="bright_blue",
    )

    for _ in range(BOARD_SIZE):
        table.add_column(justify="center", min_width=10)

    for row in range(BOARD_SIZE):
        row_cells: list[Text] = []
        for col in range(BOARD_SIZE):
            cell = row * BOARD_SIZE + col + 1
            txt = _cell_text(cell, board)
            if winning_line and cell in winning_line:
                txt.stylize(CLR_HIGHLIGHT)
            row_cells.append(txt)
        table.add_row(*row_cells)

    console.print(Align.center(table))


def print_banner() -> None:
    """Print the game title banner."""
    banner = Text()
    banner.append("⚛  QUANTUM  ", style="bold bright_cyan")
    banner.append("TIC-TAC-TOE", style="bold bright_white")
    banner.append("  ⚛", style="bold bright_cyan")
    console.print(Panel(Align.center(banner), style="bright_blue", padding=(1, 4)))
    console.print()


def print_rule(title: str = "") -> None:
    """Print a styled horizontal rule."""
    console.print(Rule(title, style="bright_blue"))


def print_quantum_state_info(board) -> None:
    """Print a compact summary of all quantum moves currently on the board."""
    all_moves: dict[str, "QuantumMove"] = {}
    for cell in range(1, TOTAL_CELLS + 1):
        for m in board.quantum_moves(cell):
            if not m.collapsed:
                all_moves[m.label] = m

    if not all_moves:
        return

    console.print()
    console.print("  [dim]Superposed moves:[/dim]")
    for label, move in sorted(all_moves.items()):
        style = CLR_X if move.player == "X" else CLR_O
        console.print(
            f"    [{style}]{label}[/{style}]"
            f" [dim]∈ cells {move.cells}[/dim]"
        )
    console.print()


def print_turn_header(player_name: str, mark: str, move_num: int) -> None:
    """Print a styled header showing whose turn it is."""
    style = CLR_X if mark == "X" else CLR_O
    console.print()
    console.print(
        f"  [{style}]▶  {player_name}'s turn  ({mark}{move_num})[/{style}]"
    )
    print_rule()


def print_collapse_announcement(cycle_cells: list[int]) -> None:
    """Announce that a quantum cycle has been detected."""
    console.print()
    console.print(Panel(
        f"[bold yellow]⚠  Entanglement Cycle Detected![/bold yellow]\n"
        f"[dim]Cells involved: {cycle_cells}[/dim]",
        border_style="yellow",
        padding=(0, 2),
    ))


def print_collapse_animation(cell: int, mark: str) -> None:
    """Animate a cell collapsing to a classical state."""
    style = CLR_X if mark == "X" else CLR_O
    frames = ["◌", "◎", "●", "✦", mark]
    console.print(f"  Collapsing cell {cell}:", end=" ")
    for frame in frames:
        console.print(f"[{style}]{frame}[/{style}]", end="  ", highlight=False)
        time.sleep(COLLAPSE_ANIMATION_DELAY * 5)
    console.print()


def print_winner(player_name: str, mark: str) -> None:
    """Print a victory announcement."""
    style = CLR_X if mark == "X" else CLR_O
    console.print()
    console.print(Panel(
        f"[{style}]🏆  {player_name} ({mark}) wins!  🏆[/{style}]",
        border_style=style.split()[0] if " " in style else style,
        padding=(1, 4),
    ))


def print_draw() -> None:
    """Print a draw announcement."""
    console.print()
    console.print(Panel(
        "[bold white]🤝  It's a draw!  Well played![/bold white]",
        border_style="white",
        padding=(1, 4),
    ))


def print_info(msg: str) -> None:
    console.print(f"  [bold blue]ℹ[/bold blue]  {msg}")


def print_warning(msg: str) -> None:
    console.print(f"  [{CLR_WARN}]⚠  {msg}[/{CLR_WARN}]")


def print_error(msg: str) -> None:
    console.print(f"  [bold red]✗  {msg}[/bold red]")


def print_success(msg: str) -> None:
    console.print(f"  [bold green]✓  {msg}[/bold green]")


def prompt(msg: str) -> str:
    """Show a styled input prompt and return stripped user input."""
    return console.input(f"  [bold bright_white]›[/bold bright_white] {msg} ").strip()
