## 🎯 How to Win Quantum Tic-Tac-Toe

### The Board
Same 3×3 grid as classical Tic-Tac-Toe — cells numbered 1–9.

### What's different: **Quantum (Spooky) Moves**

Instead of placing X in ONE cell, you place it in **TWO cells at once** (superposition). The mark `X1` means "Player X's 1st move — it exists simultaneously in both cells until collapse."

```
 X1,O1 |  X1   |  O1
───────────────────────
       |  X2   |  X2,O2
───────────────────────
  O2   |       |       
```

---

### How X/O Actually Gets **Placed Classically** (Collapse)

You **cannot** directly put a classical X or O. They only appear through **quantum collapse**, triggered automatically when an **entanglement cycle** forms.

#### What's a cycle?
When quantum marks form a loop. Example:
- `X1` is in cells **1 & 2**
- `O1` is in cells **2 & 3**  
- `X2` is in cells **3 & 1**

→ Cells 1→2→3→1 form a **cycle**! Collapse triggers.

---

### Collapse Sequence (the key mechanic)

1. **The player who did NOT create the cycle picks** one of the cycle's cells to "observe first"
2. **Qiskit runs a real quantum circuit** (Hadamard gate → measure) to randomly pick which mark survives in that cell
3. The winning mark **classically fixes** to that cell (becomes permanent X or O)
4. **Forced collapses propagate** — any mark whose OTHER cell was just taken must collapse to its remaining cell

---

### Win Condition
Once cells start collapsing classically, **first player to get 3 of their marks in a row/column/diagonal wins** — exactly like classical Tic-Tac-Toe.

---

### Example Turn Sequence

| Turn | Player | Action |
|------|--------|--------|
| 1 | X | Types `1 5` → `X1` in superposition across cells 1 & 5 |
| 2 | O | Types `2 5` → `O1` in superposition across cells 2 & 5 |
| 3 | X | Types `2 1` → `X2` across cells 2 & 1 → **CYCLE detected** (1↔5↔2↔1)! |
| — | O | (non-creator) picks a cycle cell, e.g. `1` |
| — | Qiskit | Measures → `X1` wins cell 1 |
| — | Auto | `O1` forced to cell 2, `X2` forced to cell 5 |

Now cells 1, 2, 5 are all classically settled. Game continues.

---

### Key Rules Summary

| Rule | Detail |
|------|--------|
| Each turn | Place mark in **exactly 2 cells** |
| Same cell twice? | ❌ Not allowed |
| Classically occupied cell? | ❌ Can't place there |
| Collapse triggered | Automatically when a cycle forms |
| Who collapses? | The **other** player chooses the observation cell |
| Quantum randomness | Qiskit `|+⟩` measurement decides winner |
| Win | 3 classical marks in a line |

---

Essentially: **you're playing strategy on WHERE you create superpositions**, trying to force collapses that benefit you while the Qiskit quantum coin flip adds true randomness. The deeper strategy is creating cycles where either outcome gives you an advantage.