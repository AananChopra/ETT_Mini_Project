"""
quantum/simulator.py
─────────────────────
Run Qiskit circuits on AerSimulator and return measurement results.
"""

from __future__ import annotations
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from qiskit_aer import AerSimulator
from qiskit import transpile
from config.settings import SHOTS, SIMULATOR_BACKEND, DEBUG


def _get_backend() -> AerSimulator:
    """Instantiate the configured Qiskit Aer backend."""
    # AerSimulator() with no args uses automatic method selection.
    # Only pass an explicit method when it is a known valid Aer method string.
    _VALID_METHODS = {
        "automatic", "statevector", "density_matrix", "stabilizer",
        "matrix_product_state", "extended_stabilizer", "unitary",
        "superop",
    }
    method = SIMULATOR_BACKEND.replace("aer_", "")
    if method in _VALID_METHODS:
        return AerSimulator(method=method)
    return AerSimulator()   # automatic


def run_circuit(circuit, shots: int = SHOTS) -> dict[str, int]:
    """
    Transpile and run a QuantumCircuit on AerSimulator.

    Args:
        circuit: A QuantumCircuit with measurement operations.
        shots:   Number of measurement repetitions.

    Returns:
        counts: dict mapping bitstring → count, e.g. {'0': 512, '1': 512}
    """
    backend = _get_backend()
    compiled = transpile(circuit, backend)
    job = backend.run(compiled, shots=shots)
    result = job.result()
    counts = result.get_counts(compiled)

    if DEBUG:
        print(f"  [Simulator] counts={counts}")

    return counts


def collapse_quantum_state(options: list, shots: int = SHOTS) -> object:
    """
    Use quantum measurement to select one item from `options`.

    If len(options) == 1  → trivially returns options[0]
    If len(options) == 2  → uses single-qubit Hadamard (true superposition)
    Otherwise             → uses n-qubit uniform superposition

    Args:
        options: A list of possible outcomes to choose from.
        shots:   Qiskit shots for measurement.

    Returns:
        One element from `options`, chosen via quantum randomness.
    """
    if not options:
        raise ValueError("collapse_quantum_state: options list is empty.")

    if len(options) == 1:
        return options[0]

    from quantum.circuit import build_superposition_circuit, build_collapse_circuit

    if len(options) == 2:
        circuit = build_superposition_circuit()
        counts = run_circuit(circuit, shots=shots)
        # Pick the most-measured outcome for determinism under many shots
        dominant = max(counts, key=counts.get)
        index = int(dominant, 2) % len(options)
    else:
        circuit, n_qubits = build_collapse_circuit(len(options))
        counts = run_circuit(circuit, shots=shots)
        # Filter out-of-range bitstrings, then pick most frequent valid one
        valid_counts = {
            bs: cnt for bs, cnt in counts.items()
            if int(bs, 2) < len(options)
        }
        if not valid_counts:
            import random
            return random.choice(options)
        dominant = max(valid_counts, key=valid_counts.get)
        index = int(dominant, 2)

    return options[index]
