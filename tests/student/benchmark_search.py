"""Reproducible benchmark for naive, kmp, and rk on identical inputs in the common domain (n, m <= 3000)."""

import pathlib
import random
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Python" / "source"))

import algorithms

SEED = 20261104
SIZES = [(1000, 200), (2000, 400), (3000, 600)]
WARMUP_RUNS = 2
MEASURED_RUNS = 5


def build_cases():
    cases = []
    # 1. Random cases (4-letter alphabet "ABCD", uniform PRNG seed 20261104)
    for idx, (n, m) in enumerate(SIZES):
        rng = random.Random(SEED + idx)
        text = "".join(rng.choice("ABCD") for _ in range(n))
        pattern = "".join(rng.choice("ABCD") for _ in range(m))
        cases.append({
            "case": "Random (uniform 'ABCD')",
            "n": n,
            "m": m,
            "seed_info": f"random.Random({SEED + idx}) over 'ABCD'",
            "text": text,
            "pattern": pattern,
        })
    # 2. Repetitive cases (all-'a' text and pattern triggering worst-case overlaps & hash collisions)
    for n, m in SIZES:
        text = "a" * n
        pattern = "a" * m
        cases.append({
            "case": "Repetitive ('a'^n vs 'a'^m)",
            "n": n,
            "m": m,
            "seed_info": "deterministic 'a'*n, 'a'*m",
            "text": text,
            "pattern": pattern,
        })
    return cases


def main():
    # Also verify the known collision pair ("abdj", "ab") and ("bcek", "bc") first
    for text, pat, expected in [("abdj", "ab", [0]), ("bcek", "bc", [0])]:
        r_n = algorithms.naive({"task": "naive", "text": text, "pattern": pat})["positions"]
        r_k = algorithms.kmp({"task": "kmp", "text": text, "pattern": pat})["positions"]
        r_r = algorithms.rk({"task": "rk", "text": text, "pattern": pat})["positions"]
        assert r_n == r_k == r_r == expected, f"Collision check failed on {text}, {pat}"

    cases = build_cases()
    methods = [
        ("naive", algorithms.naive),
        ("kmp", algorithms.kmp),
        ("rk", algorithms.rk),
    ]

    print("|Case|n|m|Seed/generator|Algorithm|Run 1 (ms)|Run 2 (ms)|Run 3 (ms)|Run 4 (ms)|Run 5 (ms)|Median (ms)|Correct outputs checked|")
    print("|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|")

    for c in cases:
        req_base = {"text": c["text"], "pattern": c["pattern"]}
        # Verify identical outputs across all 3 algorithms before timing
        out_naive = algorithms.naive({"task": "naive", **req_base})["positions"]
        out_kmp = algorithms.kmp({"task": "kmp", **req_base})["positions"]
        out_rk = algorithms.rk({"task": "rk", **req_base})["positions"]
        assert out_naive == out_kmp == out_rk, "Mismatch between algorithms!"
        matches_count = len(out_naive)

        for name, fn in methods:
            req = {"task": name, "text": c["text"], "pattern": c["pattern"]}
            for _ in range(WARMUP_RUNS):
                res = fn(req)
                assert len(res["positions"]) == matches_count

            runs_ms = []
            for _ in range(MEASURED_RUNS):
                t0 = time.perf_counter_ns()
                res = fn(req)
                t1 = time.perf_counter_ns()
                assert len(res["positions"]) == matches_count
                runs_ms.append((t1 - t0) / 1e6)

            med = statistics.median(runs_ms)
            print(
                f"|{c['case']}|{c['n']}|{c['m']}|{c['seed_info']}|`{name}`|"
                f"{runs_ms[0]:.3f}|{runs_ms[1]:.3f}|{runs_ms[2]:.3f}|{runs_ms[3]:.3f}|{runs_ms[4]:.3f}|"
                f"{med:.3f}|Yes ({matches_count} matches; `naive==kmp==rk`)|"
            )


if __name__ == "__main__":
    main()