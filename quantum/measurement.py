"""
quantum/measurement.py
───────────────────────
Interpret raw Qiskit measurement counts into game-level decisions.
"""

from __future__ import annotations
from quantum.simulator import run_circuit, collapse_quantum_state
from quantum.circuit import build_superposition_circuit


def interpret_measurement(counts: dict[str, int]) -> int:
    """
    Given a Qiskit counts dict (bitstring → frequency), return
    the most-frequently measured integer value.

    Args:
        counts: e.g. {'0': 600, '1': 424}

    Returns:
        int: most dominant measurement outcome (0 or 1 for 1-qubit)
    """
    if not counts:
        raise ValueError("interpret_measurement: empty counts dict.")
    dominant_bitstring = max(counts, key=counts.get)
    return int(dominant_bitstring, 2)


def quantum_coin_flip() -> int:
    """
    Perform a true quantum coin flip using a single-qubit
    Hadamard circuit measured on AerSimulator.

    Returns:
        0 or 1  (each with ~50% probability over many calls)
    """
    circuit = build_superposition_circuit()
    counts = run_circuit(circuit)
    return interpret_measurement(counts)


def quantum_choice(n: int) -> int:
    """
    Choose a random integer in [0, n) using quantum measurement.

    Args:
        n: Number of options (must be >= 1)

    Returns:
        An integer index in [0, n) chosen via quantum randomness.
    """
    options = list(range(n))
    chosen = collapse_quantum_state(options)
    return chosen
