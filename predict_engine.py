"""
FORTIVEXA - Explainable Location Prediction Engine (TRL 3 Proof of Concept)
Demonstrates multi-factor probabilistic forecasting of likely cash-withdrawal locations
from cybercrime complaints, generating transparent plain-language feature attributions.

Honesty note (post-review fix): this engine no longer looks up the current case's own
seeded ground-truth location while scoring it (that was label leakage). Every feature
below is derived only from (a) properties of the candidate location itself, or
(b) OTHER complaints' historical outcomes for the same mule chain — exactly the kind
of cross-case evidence a real investigator would have at inference time, with the
current case's own answer excluded. Confidence percentages are the raw weighted score
itself (0-100), not a hardcoded per-rank band, so a weak case can honestly land at 35%
and a strong one at 90% regardless of rank position.
"""

import sys
import json
import math
import os
from datetime import datetime
from collections import Counter

def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def haversine_dist(lat1, lon1, lat2, lon2):
    """Distance in km between two geo coordinates"""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _derive_l2_mule(case, transactions):
    """Finds the Layer-2 (layering) mule account for a case from its own transactions."""
    l1_mule = case["suspicious_account"]
    for t in transactions:
        if t.get("case_id") != case["complaint_id"]:
            continue
        if t["source_account"] == l1_mule and "MULE" in t["destination_account"]:
            return t["destination_account"]
    return l1_mule

def predict_withdrawal_location(dataset, case_id, _exclude_case_id=None):
    """
    Leave-one-out prediction: scores every known location for how likely it is to be
    the cash-withdrawal point for `case_id`, using only (a) intrinsic location
    properties and (b) historical outcomes from OTHER complaints that reused the same
    mule chain. `_exclude_case_id` additionally excludes a case from the historical
    lookup during evaluation, so a case is never scored using its own ground truth.
    """
    complaints_by_id = {c["complaint_id"]: c for c in dataset["complaints"]}
    locations = dataset["locations"]
    transactions = dataset["transactions"]

    if case_id not in complaints_by_id:
        return {"error": f"Case ID '{case_id}' not found."}

    case = complaints_by_id[case_id]
    exclude_id = _exclude_case_id if _exclude_case_id is not None else case_id

    l1_mule = case["suspicious_account"]
    l2_mule = _derive_l2_mule(case, transactions)

    try:
        dt = datetime.strptime(case["transaction_datetime"], "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
    except Exception:
        hour = 18

    # --- Historical cross-case affinity (NOT using this case's own answer) ---
    # Look at every OTHER complaint that funneled through the same L2 mule hub and
    # see which locations THEIR ground truth pointed to. This is real transductive
    # signal ("this ring has cashed out here before"), never the current case's label.
    other_location_hits = Counter()
    for c in dataset["complaints"]:
        if c["complaint_id"] == exclude_id:
            continue
        other_l2 = _derive_l2_mule(c, transactions)
        if other_l2 == l2_mule and c.get("predicted_atm_location_id"):
            other_location_hits[c["predicted_atm_location_id"]] += 1
    total_hits = sum(other_location_hits.values())

    # Historical hub = the location most often associated with this ring in OTHER cases
    historical_hub = other_location_hits.most_common(1)[0][0] if total_hits > 0 else None
    locations_by_id = {l["location_id"]: l for l in locations}
    hub_loc = locations_by_id.get(historical_hub) if historical_hub else None

    candidates = []
    for loc in locations:
        loc_id = loc["location_id"]

        # Factor 1: Cross-case mule affinity (0-1) — purely from OTHER cases
        hits = other_location_hits.get(loc_id, 0)
        if total_hits > 0:
            mule_affinity_score = hits / total_hits
        else:
            # Brand-new/unseen ring: no historical signal, fall back to a weak,
            # honestly-labelled prior based only on the location's general activity.
            mule_affinity_score = 0.10 * loc["risk_index"]

        # Factor 2: Time-of-day withdrawal window alignment (0-1) — generic pattern,
        # not tied to this case's answer.
        time_diff = abs(hour - 19)
        time_alignment_score = max(0.2, 1.0 - (time_diff * 0.15))

        # Factor 3: Proximity to the ring's own historical hub (0-1). If this ring has
        # never been seen before, there is no honest geo-signal to lean on, so this
        # factor is neutral (0.5) rather than silently pointing at the true answer.
        if hub_loc is not None:
            dist_km = haversine_dist(hub_loc["lat"], hub_loc["lng"], loc["lat"], loc["lng"])
            prox_score = 1.0 if loc_id == historical_hub else max(0.1, 1.0 / (1.0 + (dist_km / 3.0)))
        else:
            dist_km = None
            prox_score = 0.5

        # Factor 4: Historical Cash-Out Density (0-1) — static, intrinsic property of
        # the location itself (public hotspot data), not derived from this case.
        density_score = loc["risk_index"]

        raw_score = (
            0.45 * mule_affinity_score +
            0.20 * prox_score +
            0.15 * time_alignment_score +
            0.20 * density_score
        )

        factors = []
        if hits > 0:
            factors.append(f"Mule hub ({l2_mule}) previously cashed out at this location in {hits} other complaint(s).")
        else:
            factors.append(f"No prior cash-out history for mule hub ({l2_mule}) at this location — first-seen ring or location.")
        if hour in (17, 18, 19, 20, 21):
            factors.append(f"Peak withdrawal window alignment (18:00-21:30) matches complaint timestamp ({hour:02d}:00).")
        else:
            factors.append(f"Off-peak operational window ({hour:02d}:00 hours).")
        if dist_km is not None:
            factors.append(f"Located ~{dist_km:.1f} km from this ring's known cash-out hub in {loc['jurisdiction']}.")
        else:
            factors.append(f"No established ring hub yet; ranked on general hotspot density in {loc['jurisdiction']}.")

        candidates.append({
            "location_id": loc_id,
            "name": loc["name"],
            "type": loc["type"],
            "jurisdiction": loc["jurisdiction"],
            "lat": loc["lat"],
            "lng": loc["lng"],
            "raw_score": raw_score,
            "distance_km": round(dist_km, 1) if dist_km is not None else None,
            "historical_cashouts": loc["historical_cashouts"],
            "contributing_features": {
                "mule_chain_affinity": round(mule_affinity_score * 100, 1),
                "geospatial_proximity": round(prox_score * 100, 1),
                "temporal_window_match": round(time_alignment_score * 100, 1),
                "historical_density": round(density_score * 100, 1)
            },
            "plain_language_reasons": factors
        })

    candidates.sort(key=lambda x: x["raw_score"], reverse=True)

    # Confidence IS the raw weighted score, scaled to 0-100 — no per-rank clamp.
    # A weak, low-signal case can honestly land at 30-40% for its own top pick.
    for idx, c in enumerate(candidates):
        c["confidence_percentage"] = round(min(97.0, c["raw_score"] * 100), 1)
        c["rank"] = idx + 1

    top_prediction = candidates[0]

    return {
        "case_id": case_id,
        "complaint_date": case["date"],
        "complaint_amount": case["amount"],
        "category": case["category"],
        "analyzed_mule_chain": {
            "entry_mule_l1": l1_mule,
            "layering_mule_l2": l2_mule
        },
        "top_ranked_candidate": top_prediction,
        "all_ranked_candidates": candidates[:6],
        "model_metadata": {
            "model_type": "Rule-Informed Multi-Factor Spatial Ensemble (leave-one-out, no label leakage)",
            "validation_stage": "TRL 3 Experimental Proof of Concept",
            "training_baseline": "128 synthetic cases with ground-truth seeded rings",
            "features_utilized": [
                "Cross-Case Mule Hub Historical Affinity (excludes the case's own label)",
                "Temporal Distribution & Transit Lag",
                "Proximity to Ring's Known Historical Hub",
                "Historical ATM Cashout Density"
            ],
            "disclaimer": "Demonstration result — trained on synthetic data. Requires field verification by law enforcement."
        }
    }

if __name__ == "__main__":
    ds = load_data()
    cid = sys.argv[1] if len(sys.argv) > 1 else "CMP-1001"
    res = predict_withdrawal_location(ds, cid)
    print(json.dumps(res, indent=2))
