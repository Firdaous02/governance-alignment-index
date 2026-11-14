from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

DIMENSIONS = (
    "security_access_control",   # d1
    "quality_integrity",         # d2
    "metadata_lineage",          # d3
    "interoperability",          # d4
    "retention_compliance",      # d5
)
SCALE_MIN, SCALE_MAX = 0.0, 5.0


@dataclass(frozen=True)
class Pair:
    name: str
    c: tuple[float, ...]   # IT capability vector
    r: tuple[float, ...]   # DG requirement vector
    w: float               # weight



# Core formulas

def _validate(c: Sequence[float], r: Sequence[float]) -> None:
    if len(c) != len(r):
        raise ValueError("c and r must have the same length")
    for v in (*c, *r):
        if not SCALE_MIN <= v <= SCALE_MAX:
            raise ValueError(f"score {v} outside [{SCALE_MIN}, {SCALE_MAX}]")
    if not any(c) or not any(r):
        raise ValueError("c and r must be nonzero vectors")


def cosine(c: Sequence[float], r: Sequence[float]) -> float:
    """Eq. (1): profile coherence."""
    _validate(c, r)
    dot = sum(a * b for a, b in zip(c, r))
    return dot / (math.sqrt(sum(a * a for a in c)) * math.sqrt(sum(b * b for b in r)))


def coverage(c: Sequence[float], r: Sequence[float]) -> float:
    """Eq. (2): requirement coverage kappa_i."""
    _validate(c, r)
    return sum(min(a, b) for a, b in zip(c, r)) / sum(r)


def pair_alignment(c: Sequence[float], r: Sequence[float]) -> float:
    """a_i = cos(theta_i) * kappa_i."""
    return cosine(c, r) * coverage(c, r)


def global_index(pairs: Sequence[Pair], use_cosine_only: bool = False,
                 weights: Sequence[float] | None = None) -> float:
    """Eq. (3): weighted global index A. Weights must sum to 1."""
    w = list(weights) if weights is not None else [p.w for p in pairs]
    if not math.isclose(sum(w), 1.0, abs_tol=1e-9):
        raise ValueError(f"weights must sum to 1, got {sum(w)}")
    f = cosine if use_cosine_only else pair_alignment
    return sum(wi * f(p.c, p.r) for wi, p in zip(w, pairs))


def classify(a: float) -> str:
    if a < 0.40:
        return "Low"
    if a <= 0.70:
        return "Medium"
    return "High"



# Scenario from the paper (Table 4)

PAPER_PAIRS = [
    Pair("IoT acquisition",    (4, 2, 1, 4, 1), (3, 5, 3, 3, 2), 0.40),
    Pair("Cloud + AI analytics", (4, 2, 1, 3, 1), (3, 4, 5, 4, 4), 0.35),
    Pair("Alert generation",   (3, 1, 1, 2, 0), (2, 3, 4, 3, 4), 0.25),
]


def load_csv(path: Path) -> list[Pair]:
    """CSV columns: name, weight, c1..c5, r1..r5"""
    pairs = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = tuple(float(row[f"c{k}"]) for k in range(1, 6))
            r = tuple(float(row[f"r{k}"]) for k in range(1, 6))
            pairs.append(Pair(row["name"], c, r, float(row["weight"])))
    return pairs



# Reporting

def report(pairs: Sequence[Pair]) -> dict:
    rows = []
    for p in pairs:
        cs, kp = cosine(p.c, p.r), coverage(p.c, p.r)
        rows.append({"pair": p.name, "c": p.c, "r": p.r, "weight": p.w,
                     "cos": cs, "kappa": kp, "a": cs * kp})
    n = len(pairs)
    equal = [1.0 / n] * n
    out = {
        "pairs": rows,
        "A": global_index(pairs),
        "level": classify(global_index(pairs)),
        "A_equal_weights": global_index(pairs, weights=equal),
        "level_equal_weights": classify(global_index(pairs, weights=equal)),
        "A_cosine_only": global_index(pairs, use_cosine_only=True),
    }
    return out


def print_report(res: dict) -> None:
    print(f"{'Pair':<22}{'cos':>8}{'kappa':>8}{'a_i':>8}{'w_i':>7}")
    for r in res["pairs"]:
        print(f"{r['pair']:<22}{r['cos']:>8.4f}{r['kappa']:>8.4f}"
              f"{r['a']:>8.4f}{r['weight']:>7.2f}")
    print()
    print(f"Global index A (paper weights) : {res['A']:.4f}  -> {res['level']}")
    print(f"A with equal weights           : {res['A_equal_weights']:.4f}  "
          f"-> {res['level_equal_weights']}")
    print(f"A with cosine similarity only  : {res['A_cosine_only']:.4f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, help="CSV file (default: paper scenario)")
    ap.add_argument("--json", type=Path, help="also write results to this JSON file")
    args = ap.parse_args()

    pairs = load_csv(args.input) if args.input else PAPER_PAIRS
    res = report(pairs)
    print_report(res)
    if args.json:
        args.json.write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
