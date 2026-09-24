# FORTIVEXA — Cybercrime Predictive Analytics Framework (TRL 3)
> **SIH Problem Statement**: Forecasting likely cash-withdrawal locations from multi-hop cybercrime complaints to enable proactive law enforcement intervention.

[![TRL Stage](https://img.shields.io/badge/Project%20Stage-TRL%203%20Experimental%20POC-blue.svg)](#project-stage--trl-3-status)
[![Cross-Case Precision](https://img.shields.io/badge/Linkage%20Precision-42.8%25-orange.svg)](#empirical-validation-results)
[![Top-3 Accuracy](https://img.shields.io/badge/Top--3%20Location%20Accuracy-55.5%25-orange.svg)](#empirical-validation-results)
[![Status](https://img.shields.io/badge/Data-Synthetic%20Demonstration-orange.svg)](#ethical-disclosure--neutral-framing)

---

## Executive Summary

Most cybercrime analytics dashboards analyze one complaint in isolation. **FORTIVEXA** upgrades this paradigm through two foundational breakthroughs:
1. **Cross-Case Mule Ring Detection**: A bipartite graph correlation engine that scans all incoming complaints across distinct police stations for shared intermediary mule accounts (`mule_l1`, `mule_l2`), IFSC routing switches, and contact numbers. This transforms the platform from a "single-case visualizer" into an **"organized fraud syndicate detector"**.
2. **Explainable Location Predictions**: Rather than outputting an opaque black-box percentage, FORTIVEXA delivers **calibrated candidate rankings with plain-language feature factor attributions** (e.g., *"Same mule chain used 3x in 30 days, historical cashout window 6–8pm matches complaint delay, situated 1.2km from Mule L2 branch jurisdiction"*).

---

## Project Stage & TRL 3 Status

**Technology Readiness Level**: **TRL 3 (Experimental Proof of Concept)**.

> [!IMPORTANT]
> **Scientific & Academic Honesty Guarantee**:
> - **Persistent Ethical Badges**: All views and dossiers display `FORTIVEXA | TRL 3 PROOF OF CONCEPT (DEMO DATA)`.
> - **Fictional & Anonymized Data**: Evaluated on 128 standardized synthetic cases (8 hand-authored clean walkthrough cases + 120 synthetic cases) with 19 seeded ground-truth fraud rings. No real citizen PII is used.
> - **Neutral Investigative Framing**: System outputs serve as investigative leads requiring officer verification prior to field action; the system **never auto-accuses** nor establishes judicial guilt.
> - **Roadmap Transparency**: Advanced technologies not implemented at this stage (e.g., dynamic GNNs, Neo4j distributed cluster, LSTM spatio-temporal modeling, live NCRP webhooks) are explicitly demarcated as future roadmap (TRL 6+), not current state.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 6, TypeScript, Tailwind CSS, Recharts, Leaflet + OpenStreetMap, Lucide React |
| **Backend** | Node.js (v24), Express 4, In-Memory Caching, Child Process Python Runner |
| **ML & Graph Layer** | Pure Python 3.11 Standard Library (`math`, `collections`, `datetime`, `json`, `hashlib`) |
| **Audit Layer** | Cryptographic SHA-256 Tamper-Evident Merkle / Blockchain Ledger POC |

---

## Demo Credentials & Persona Logins

The application includes 1-click authentication for quick evaluation:

| Persona | Identifier | Station / Badge | Role Scope |
|---|---|---|---|
| **Cybercrime Investigator** | `investigator.le@fortivexa.local` | `LE-CYBER-884` | Case Management, Ring Correlation, Field Dispatch |
| **SIH Academic Evaluator** | `sih-audit@fortivexa.local` | `SIH-AUDIT-2026` | TRL 3 Validation Metrics, Benchmarks, Audit Ledger |

---

## Quick Start & Setup Instructions

### Prerequisites
- Node.js (v18+) and npm
- Python 3.10+

### Installation & Launch
```bash
# 1. Install Node.js dependencies (already installed in workspace)
npm install

# 2. Generate and validate the synthetic dataset (if needed)
python server/ml/dataset_generator.py
python server/ml/evaluate_trl3.py

# 3. Launch both Express Backend and Vite Frontend concurrently
npm run dev
```

The application will be accessible at:
- **Client Frontend**: `http://localhost:5173`
- **Backend REST API**: `http://localhost:5001/api`

---

## 12 Pages & Functional Modules

1. **Login (`/login`)**: Academic proof-of-concept authentication with 1-click persona quick-access.
2. **Dashboard (`/dashboard`)**: Tactical KPI summary, complaints timeline, hourly withdrawal peak distribution (17:30–21:30), threat risk donut, hotspot previews, and live syndicate alerts.
3. **Complaints Repository (`/complaints`)**: CRUD operations, multi-field search, category & status filters, and incident detail drawer with direct dispatch actions.
4. **Transactions Ledger (`/transactions`)**: Risk-classified transaction stream (LOW, MEDIUM, HIGH, CRITICAL), sorting, channel filters (UPI, IMPS, NEFT, ATM_WITHDRAWAL), and transaction trail inspector.
5. **Account Network (`/accounts`)**: Mule hierarchy table (`victim`, `mule_l1`, `mule_l2`, `withdrawal`) paired with an interactive SVG node/edge graph with zoom, pan, and node inspection.
6. **Cross-Case Linkage (`/linkage`) [CORE INNOVATION]**: Select any case to discover other FIRs sharing intermediary mule accounts across jurisdictions, featuring an alert banner (*"3 other active cases share this mule account"*), bipartite ring subgraph, and linked case registry.
7. **Prediction Engine (`/prediction`)**: Ranked candidate ATM kiosks with confidence percentages and 3 transparent plain-language factors per candidate (mule reuse count, time-of-day peak match, branch hub proximity).
8. **Prediction Pipeline (`/pipeline`)**: 9-stage interactive visual flow (Data Input $\to$ Preprocessing $\to$ Feature Extraction $\to$ Transaction Graph $\to$ ML Model $\to$ Geospatial Analysis $\to$ Location Prediction $\to$ Risk Score $\to$ Actionable Intelligence) with step simulation and schema telemetry.
9. **Risk Map (`/map`)**: Dark Leaflet map with Low, Medium, High, and Predicted-Hotspot markers, jurisdiction boundaries, and popup surveillance metrics.
10. **Actionable Intelligence (`/intelligence`)**: Per-case field dossiers, priority badges (P1/P2), neutral legal framing, patrol checklists, and print/export dispatch briefs.
11. **Blockchain Ledger (`/blockchain`)**: Cryptographic audit ledger anchoring records with SHA-256 block hashes, previous block hash pointers, and interactive "Verify Record Integrity" recalculation.
12. **TRL 3 Validation Page (`/trl3`)**: TRL 3 badge, validation stages checklist, TRL 1–7+ roadmap, empirical precision/recall metrics, and honest scientific limitations notes.

---

## Empirical Validation Results

Benchmarks computed from `server/ml/evaluate_trl3.py` on the 128-case dataset:

> **These numbers are computed, not hardcoded.** `npm run evaluate` re-runs `server/ml/evaluate_trl3.py`,
> which actually executes `detect_rings()` and a leave-one-out `predict_withdrawal_location()` against the
> seeded ground truth and counts real matches. An earlier version of this script assigned these figures as
> literal constants without running anything — that has been fixed, and the numbers below are honestly lower
> as a direct result. See `server/data/trl3_evaluation.json` for the full computed report.

| Benchmark Dimension | Measured Result | Evaluation Methodology |
|---|---|---|
| **Linkage Precision** | **42.8%** | Pairwise case co-occurrence precision on seeded rings (computed) |
| **Linkage Recall** | **100.0%** | Fraction of ground-truth syndicate members correlated (computed) |
| **Linkage F1-Score** | **59.9%** | Harmonic mean of cross-case precision and recall (computed) |
| **Model Top-1 Accuracy** | **16.4%** | True withdrawal location ranked as candidate #1, leave-one-out, no label leakage (computed) |
| **Model Top-3 Accuracy** | **55.5%** | True withdrawal location present in top 3 ranked candidates (computed) |
| **Mean Geodesic Error** | **5.37 km** | Average search radius discrepancy from true cashout ATM (computed) |

**What the real numbers say, honestly:** recall is a perfect 100% but precision is only 42.8% — the ring-detection
engine currently over-merges (it groups more cases together than the seeded ground truth intends) rather than
missing links. Prediction accuracy dropped sharply once the case's own ground-truth answer was removed from its
own historical lookup (previously a leakage bug) — Top-1 accuracy on a rule-based, non-learned engine with no
prior history for brand-new rings is genuinely hard, which is exactly the kind of honest limitation a TRL 3
prototype should surface rather than hide.
| **Dataset Volume** | **128 Cases** | 120 synthetic cases + 8 clean demo cases; 384 transactions |
| **Evaluation Split** | **80% / 20%** | Stratified holdout evaluation (26 test cases) |

---

## Honest Limitations Disclosure

1. **Ring Discrepancy Note (20 Detected vs. 19 Seeded)**:
   *The linkage engine detected 20 rings compared to 19 seeded rings. This split occurred because two distinct syndicates (`RING-01` and `RING-13`) both routed funds through a secondary mule account (`ACC-MULE-004`). In a live deployment, temporal decay weighting is required to distinguish concurrent syndicates sharing KYC pools.*
2. **Synthetic Data Boundary**:
   *Validation was executed against synthetic multi-hop topologies conforming to SIH standards. Real-world FIR reports often suffer from incomplete bank transaction statements, delayed reporting (>48h), and unindexed payment aggregator wallets.*
3. **Probabilistic Caution**:
   *Predictions represent likelihood indices based on historical cashout hubs and mule branch jurisdictions; they do NOT constitute judicial evidence or proof of guilt. On-ground verification by an investigating officer is strictly mandatory.*
4. **Cold-Start Limitation**:
   *Location prediction relies on cross-case history for the same mule hub. A brand-new mule ring with no prior complaints in the dataset has no such history to draw on, so it falls back to a weak, generic hotspot-density prior — accuracy on first-seen rings is meaningfully lower than on previously-observed ones. This is measured and disclosed rather than masked by a fixed confidence band.*
5. **Evaluation Correction Disclosure**:
   *An earlier version of `evaluate_trl3.py` assigned its headline metrics (94.7% precision, 78.3% Top-1 accuracy, etc.) as hardcoded constants rather than computing them, and the prediction engine briefly used each case's own seeded answer as a scoring feature. Both were identified and fixed: the evaluation script now genuinely runs the detection/prediction engines against ground truth, and the engine no longer sees a case's own label while scoring it. The current, lower, honestly-computed numbers are the direct result.*

---

## Implemented Prototype (TRL 3) vs Production Roadmap (TRL 6+)

| Architecture Layer | Current Implemented (TRL 3) | Future Roadmap (TRL 6+ Target) |
|---|---|---|
| **Mule Ring Detection** | Pure-Python Bipartite Graph Projection & Connected Components | Distributed Neo4j Graph DB + Dynamic Graph Neural Networks (GNN) |
| **Location Forecasting** | Rule-Informed Multi-Factor Spatial Ensemble (Branch Proximity + Hub Density) | LSTM Temporal Path Forecasting + Spatio-Temporal Graph ConvNets |
| **Data Ingestion** | Standardized JSON Schema (Batch Upload & CRUD UI) | Live NCRP / 1930 Portal Webhook Listener + RBI 2-Factor Bank Feeds |
| **Audit Ledger** | Cryptographic SHA-256 Tamper-Evident Chained Blocks (Local Memory/File) | Hyperledger Besu / Permissioned Inter-Agency Police Consortium |

---

## Ethical Disclosure & Neutral Framing

FORTIVEXA adheres to the following principles:
- **No Automated Accusations**: The platform identifies telemetric correlations and probable physical extraction points; it never labels individuals as guilty of criminal offenses.
- **Evidence Admissibility**: Audit blocks compute cryptographic fingerprints to maintain chain of custody in accordance with Section 65B of the Indian Evidence Act (now Bharatiya Sakshya Adhiniyam).
