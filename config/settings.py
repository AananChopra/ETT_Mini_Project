# ============================================================
# config/settings.py
# Game-wide configuration constants for Quantum Tic-Tac-Toe
# ============================================================

# ── Qiskit / Simulation ──────────────────────────────────────
SHOTS: int = 1024          # Number of Qiskit measurement shots
SIMULATOR_BACKEND: str = "aer_simulator"   # 'aer_simulator' | 'statevector_simulator'
COLLAPSE_MODE: str = "quantum"             # 'quantum' (Qiskit) | 'random' (no Qiskit)

# ── Board ────────────────────────────────────────────────────
BOARD_SIZE: int = 3        # 3×3 board (cells 1-9)
TOTAL_CELLS: int = BOARD_SIZE * BOARD_SIZE  # 9

# ── Players ──────────────────────────────────────────────────
PLAYER_MARKS: tuple[str, str] = ("X", "O")
MAX_MOVES_PER_PLAYER: int = TOTAL_CELLS // 2 + 1   # practical upper bound

# ── Display ──────────────────────────────────────────────────
BOARD_CELL_WIDTH: int = 12   # characters wide per cell in CLI rendering
COLLAPSE_ANIMATION_DELAY: float = 0.05   # seconds between animation frames

# ── Debug ────────────────────────────────────────────────────
DEBUG: bool = False          # Set True to print Qiskit circuit diagrams
