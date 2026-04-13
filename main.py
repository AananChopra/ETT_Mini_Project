"""
main.py
────────
Entry point for Quantum Tic-Tac-Toe.

Run with:
    python main.py
"""

from __future__ import annotations
import sys
import os

# ── Ensure project root is on sys.path so sub-packages resolve cleanly ─────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from game.player import Player
from game.game_engine import GameEngine
from utils import display as ui
from config.settings import DEBUG

console = Console()


# ── How-To ─────────────────────────────────────────────────────────────────────

HOW_TO_PLAY = """\
[bold bright_cyan]HOW TO PLAY[/bold bright_cyan]

  • Each turn you place a [bold]quantum (spooky) move[/bold] in [italic]two[/italic] cells at once.
  • Your mark (e.g. [cyan]X1[/cyan]) exists in [bold]superposition[/bold] between both cells.
  • When quantum marks form an [bold yellow]entanglement cycle[/bold yellow], a collapse is triggered:
      – The [italic]other[/italic] player picks which cycle cell to observe first.
      – [bold magenta]Qiskit[/bold magenta] measures a quantum circuit to pick the surviving mark.
      – Forced collapses propagate until the board stabilises.
  • Win by getting three of your collapsed marks in a row, column, or diagonal.

  [dim]Cell reference:[/dim]

      [dim] 1 │ 2 │ 3 [/dim]
      [dim]───┼───┼───[/dim]
      [dim] 4 │ 5 │ 6 [/dim]
      [dim]───┼───┼───[/dim]
      [dim] 7 │ 8 │ 9 [/dim]
"""


def show_how_to_play() -> None:
    console.print(Panel(HOW_TO_PLAY, border_style="bright_blue", padding=(1, 3)))


def get_player_names() -> tuple[str, str]:
    """Prompt for player names, falling back to defaults."""
    console.print()
    console.print("  [bold bright_white]Enter player names (press Enter for defaults)[/bold bright_white]")
    console.print()

    name_x = Prompt.ask(
        "  [cyan]Player X[/cyan] name",
        default="Alice",
        console=console,
    )
    name_o = Prompt.ask(
        "  [magenta]Player O[/magenta] name",
        default="Bob",
        console=console,
    )
    return name_x.strip() or "Alice", name_o.strip() or "Bob"


def ask_play_again() -> bool:
    """Ask if the players want a rematch."""
    console.print()
    answer = Prompt.ask(
        "  [bold]Play again?[/bold]",
        choices=["y", "n"],
        default="n",
        console=console,
    )
    return answer.lower() == "y"


def main() -> None:
    """Main entry point — handles repeated games."""
    ui.print_banner()
    show_how_to_play()

    name_x, name_o = get_player_names()

    if DEBUG:
        console.print("  [dim][DEBUG mode ON — Qiskit circuits will be printed][/dim]")

    while True:
        console.print()
        ui.print_rule("  New Game  ")

        player_x = Player(name=name_x, mark="X")
        player_o = Player(name=name_o, mark="O")

        engine = GameEngine(player_x, player_o)

        try:
            engine.run()
        except KeyboardInterrupt:
            console.print()
            ui.print_warning("Game interrupted by user.")
            sys.exit(0)

        if not ask_play_again():
            console.print()
            console.print(
                Align.center(
                    Text("Thanks for playing Quantum Tic-Tac-Toe! ⚛", style="bold bright_cyan")
                )
            )
            console.print()
            break


if __name__ == "__main__":
    main()
