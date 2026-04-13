"""
quantum/circuit.py
──────────────────
Qiskit circuit builders for quantum superposition and collapse.
"""

from __future__ import annotations
from qiskit import QuantumCircuit
from config.settings import DEBUG


def build_superposition_circuit() -> QuantumCircuit:
    """
    Create a single-qubit circuit in superposition.

    |0⟩ ──[H]──[M]──

    Measuring gives 0 or 1 with equal probability (50/50),
    used as a quantum coin flip for binary collapse decisions.
    """
    qc = QuantumCircuit(1, 1)
    qc.h(0)          # Hadamard: |0⟩ → |+⟩ = (|0⟩ + |1⟩) / √2
    qc.measure(0, 0)

    if DEBUG:
        print("\n[Qiskit] Superposition Circuit:")
        print(qc.draw(output="text"))

    return qc


def build_collapse_circuit(num_options: int) -> QuantumCircuit:
    """
    Create an n-qubit uniform superposition circuit to randomly
    select one of `num_options` classical outcomes.

    For num_options == 2  →  1 qubit (|+⟩)
    For num_options == 3  →  2 qubits (4 outcomes, filtered to 3)
    For num_options == 4  →  2 qubits
    ...up to 8 options → 3 qubits.

    Returns a QuantumCircuit with enough qubits to encode all options.
    """
    import math
    n_qubits = max(1, math.ceil(math.log2(num_options))) if num_options > 1 else 1
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Apply Hadamard to all qubits → uniform superposition
    for i in range(n_qubits):
        qc.h(i)

    qc.measure(range(n_qubits), range(n_qubits))

    if DEBUG:
        print(f"\n[Qiskit] Collapse Circuit ({n_qubits} qubits, {num_options} options):")
        print(qc.draw(output="text"))

    return qc, n_qubits


def build_entanglement_circuit(n: int) -> QuantumCircuit:
    """
    Build a GHZ-like entangled circuit for n qubits.
    Used to illustrate quantum entanglement between cells
    (visualisation/educational purposes).

    |0⟩^n ──[H on q0]──[CNOT q0→q1]──...──[CNOT q0→qn-1]──[M all]
    """
    if n < 2:
        raise ValueError("Entanglement circuit requires at least 2 qubits.")

    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(1, n):
        qc.cx(0, i)
    qc.measure(range(n), range(n))

    if DEBUG:
        print(f"\n[Qiskit] Entanglement Circuit ({n} qubits):")
        print(qc.draw(output="text"))

    return qc
