# emi-eval

Synthetic suites that measure what EMI decides, against hidden oracles. Each
task is a small project, a set of candidate changes labelled correct or
incorrect, and a plain-Python oracle EMI never sees. A label that disagrees
with its oracle is a bug in the suite, and `validate` fails on it.

```
emi_evals/   the runner, gates, oracle runner and report
suites/      the tasks: shapes, determinism, discrimination (disc_a, disc_b), adversarial
tracks/      real-patch replay (rebench.py) and the live closed loop (closed_loop.py)
runs/        recorded results, one directory per run
```

```
pip install "emicode==0.1.1" "pytest>=8,<9" "hypothesis>=6,<7" "coverage>=7.9,<8"
python -m emi_evals validate          # oracles only; CI runs this
python -m emi_evals run               # EMI on every task, condition and candidate
python -m emi_evals report results/   # score a run into report.md and summary.json
```

Output goes to `results/` (ignored by git). A run worth keeping is copied
into `runs/`.

## Recorded runs

| Directory | What | EMI |
|---|---|---|
| `runs/upload/` | the files as first uploaded: shapes 30 of 30 and determinism 169 of 170 | as recorded |
| `runs/discrimination-0.1.1/` | the discrimination suite, 278 checks over 71 candidates on 10 tasks, run 16 Nov 2026 without the sandbox (bubblewrap was unavailable) | 0.1.1 |
| `runs/input-count/` | each law on each candidate with 100 fixed inputs and with 10,000 random inputs under three seeds, 17 Nov 2026: 10,000 inputs caught none of the 12 wrong changes EMI let through and blocked no correct one | Hypothesis only |

One author wrote both the wrong candidates and the laws here, so catch rates
from these suites are a ceiling, not an estimate.
