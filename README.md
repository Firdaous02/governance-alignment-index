# Governance Alignment Index (ITG–DG)

Reproducibility package for the paper **"Towards Unified IT and Data Governance:
A Design Science Approach for Responsible AI Decision-Making"** (INTIS).

It implements the Alignment Index of Section 5.2 and reproduces Table 4,
Eq. (4) and the sensitivity figures reported in the paper.

## Method (Section 5.2)

For each pair *i* (IT capability context, DG requirement context), scored on five
dimensions (security/access, quality/integrity, metadata/lineage,
interoperability, retention/compliance):

- `cos(θ_i) = c_i·r_i / (‖c_i‖‖r_i‖)`  (profile coherence, Eq. 1)
- `κ_i = Σ_k min(c_ik, r_ik) / Σ_k r_ik`  (requirement coverage, Eq. 2)
- `a_i = cos(θ_i) · κ_i`
- `A = Σ_i ω_i a_i`, with `Σ ω_i = 1`  (Eq. 3)

Levels: Low (A < 0.40), Medium (0.40 ≤ A ≤ 0.70), High (A > 0.70).

> The vectors and weights are **illustrative assumptions** (expert judgement),
> not empirical measurements. See the Limitations section of the paper.

## Requirements

Python ≥ 3.9. **No third-party dependencies** (standard library only).

## Run

```bash
python alignment_index.py                                        # paper scenario
python alignment_index.py --input data/scenario_predictive_maintenance.csv
python alignment_index.py --json results.json                    # also save results
python -m unittest -v                                            # check against the paper
```

Expected output:

```
Pair                       cos   kappa     a_i    w_i
IoT acquisition         0.8454  0.6250  0.5284   0.40
Cloud + AI analytics    0.8132  0.5000  0.4066   0.35
Alert generation        0.6676  0.3750  0.2503   0.25

Global index A (paper weights) : 0.4163  -> Medium
A with equal weights           : 0.3951  -> Low
A with cosine similarity only  : 0.7897
```

## Use your own data

Copy `data/scenario_predictive_maintenance.csv` and edit it.
Columns: `name, weight, c1..c5, r1..r5` (scores in [0, 5]; weights sum to 1).

## Files

| File | Purpose |
|---|---|
| `alignment_index.py` | Implementation + CLI |
| `test_alignment_index.py` | Tests reproducing the paper's numbers |
| `data/scenario_predictive_maintenance.csv` | Input data of Table 4 |


