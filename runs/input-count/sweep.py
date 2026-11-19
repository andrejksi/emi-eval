"""Would more inputs catch what the laws missed? For every discrimination
candidate judged under the `laws` condition, run the task's law files on the
candidate twice: derandomized with 100 examples (as EMI pins them), and with
10,000 random examples under three seeds. Compares both with EMI's decision.

    python3 runs/input-count/sweep.py . PYTHON

PYTHON is an interpreter with pytest and hypothesis. Reads
runs/discrimination-0.1.1/, writes runs/input-count/rows.json."""
import json, os, subprocess, sys, tempfile, collections
from pathlib import Path
S = Path(sys.argv[1]).resolve(); PY = sys.argv[2]
sys.path.insert(0, str(S))
RUN = S / "runs" / "discrimination-0.1.1"
from suites import disc_a, disc_b
tasks = {t.id: t for t in disc_a.TASKS + disc_b.TASKS if t.laws}
truth = {(d["task"], d["candidate"]): d for d in map(json.loads, open(RUN / "truth.jsonl"))}
res = [d for d in map(json.loads, open(RUN / "results.jsonl")) if d["condition"] == "laws"]
def conf(n, derand):
    return ("from hypothesis import settings, HealthCheck\n"
            f"settings.register_profile('sweep', max_examples={n}, derandomize={derand}, database=None,"
            " deadline=None, suppress_health_check=list(HealthCheck))\n"
            "settings.load_profile('sweep')\n")
ARMS = [("pinned100", 100, True, [None]), ("random10k", 10000, False, [1, 2, 3])]
out = []
for d in res:
    t = tasks.get(d["task"])
    if not t: continue
    cand = next(c for c in t.candidates if c.id == d["candidate"])
    correct = truth[(d["task"], d["candidate"])]["oracle"]["correct"]
    with tempfile.TemporaryDirectory() as w:
        w = Path(w)
        files = dict(t.files); files.update({k: v for k, v in cand.edits.items()})
        for k, v in files.items():
            if v is None: continue
            p = w / k; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(v)
        for k in [k for k, v in cand.edits.items() if v is None]:
            (w / k).unlink(missing_ok=True)
        lawdir = w / "_laws"; lawdir.mkdir()
        for k, v in t.laws.items(): (lawdir / k).write_text(v)
        row = dict(task=d["task"], cand=d["candidate"], correct=correct, emi=d["emi"]["action"])
        import time
        for name, n, derand, seeds in ARMS:
            (lawdir / "conftest.py").write_text(conf(n, derand))
            got = []; t0 = time.time()
            for seed in seeds:
                cmd = [PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "_laws", "--rootdir", str(w)]
                if seed is not None: cmd.insert(-3, f"--hypothesis-seed={seed}")
                r = subprocess.run(cmd, cwd=w, capture_output=True, text=True, timeout=1800,
                                   env={**os.environ, "PYTHONPATH": str(w), "PYTHONHASHSEED": "0"})
                got.append({0: "pass", 1: "FAIL"}.get(r.returncode, f"err{r.returncode}"))
            row[name] = got; row[name + "_s"] = round((time.time() - t0) / len(seeds), 1)
    out.append(row)
    print(json.dumps(out[-1]), flush=True)
json.dump(out, open(S / "runs" / "input-count" / "rows.json", "w"), indent=1)
