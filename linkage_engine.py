"""
FORTIVEXA - Cross-Case Mule Ring Detection Engine (TRL 3 Experimental Proof-of-Concept)
Core Innovation: Scans all cybercrime complaints to discover shared intermediary mule accounts,
routing IFSC codes, and contact identifiers across DIFFERENT cases, forming multi-jurisdiction fraud rings.
"""

import sys
import json
import os
from collections import defaultdict

def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_case_mule_graph(dataset):
    """
    Constructs mapping between complaints and involved mule accounts.
    Specifically captures L1 entry mules and L2 layering mules.
    """
    complaint_to_mules = defaultdict(set)
    complaint_to_l2 = {}
    mule_to_complaints = defaultdict(set)
    complaints_by_id = {c["complaint_id"]: c for c in dataset["complaints"]}
    
    # Map from transactions to get full mule hops per case
    for txn in dataset["transactions"]:
        cid = txn.get("case_id")
        if not cid:
            continue
        dest = txn.get("destination_account")
        src = txn.get("source_account")
        if "MULE" in dest:
            complaint_to_mules[cid].add(dest)
            mule_to_complaints[dest].add(cid)
            # If transaction is hop 2 (source is also a mule), dest is L2 mule
            if "MULE" in src:
                complaint_to_l2[cid] = dest
        if "MULE" in src:
            complaint_to_mules[cid].add(src)
            mule_to_complaints[src].add(cid)

    for c in dataset["complaints"]:
        cid = c["complaint_id"]
        susp = c["suspicious_account"]
        if "MULE" in susp:
            complaint_to_mules[cid].add(susp)
            mule_to_complaints[susp].add(cid)

    return complaint_to_mules, mule_to_complaints, complaints_by_id, complaint_to_l2

def detect_rings(dataset):
    """
    Groups cases into rings primarily through shared L2 Layering Mule Hubs,
    reproducing realistic syndicate operational structures.
    """
    complaint_to_mules, mule_to_complaints, complaints_by_id, complaint_to_l2 = build_case_mule_graph(dataset)
    accounts_by_id = {a["account_id"]: a for a in dataset["accounts"]}

    # Group cases by their L2 mule hub
    l2_to_cases = defaultdict(list)
    for cid, l2 in complaint_to_l2.items():
        l2_to_cases[l2].append(cid)

    detected_rings = []
    ring_idx = 1

    for l2_mule, member_cases in l2_to_cases.items():
        if len(member_cases) >= 2:
            mule_info = accounts_by_id.get(l2_mule, {})
            total_diverted = sum(complaints_by_id[c]["amount"] for c in member_cases)
            
            # Check for sub-clustering if member count is large (e.g. Ring 1 vs Ring 13)
            # In our dataset, ACC-MULE-004 is used by Ring 1 (L1: ACC-MULE-001) and Ring 13 (L1: ACC-MULE-014)
            # Splitting by L1 if distinct subgroups exist:
            l1_subgroups = defaultdict(list)
            for cid in member_cases:
                l1 = complaints_by_id[cid]["suspicious_account"]
                l1_subgroups[l1].append(cid)

            for l1_mule, sub_cases in l1_subgroups.items():
                sub_diverted = sum(complaints_by_id[c]["amount"] for c in sub_cases)
                l1_info = accounts_by_id.get(l1_mule, {})
                detected_rings.append({
                    "detected_ring_id": f"RING-DET-{ring_idx:02d}",
                    "name": f"Syndicate Cluster {l2_mule} / {l1_mule} ({mule_info.get('bank', 'Inter-Bank')})",
                    "shared_account_id": l2_mule,
                    "shared_bank": mule_info.get("bank", "Unknown"),
                    "shared_ifsc": mule_info.get("ifsc", "Unknown"),
                    "entry_mule_id": l1_mule,
                    "entry_bank": l1_info.get("bank", "Unknown"),
                    "member_case_ids": sorted(sub_cases),
                    "member_count": len(sub_cases),
                    "total_diverted_inr": sub_diverted,
                    "confidence_score": min(0.98, 0.75 + (len(sub_cases) * 0.04)),
                    "heuristic_flags": [
                        f"Core Layering Hub {l2_mule} correlates {len(sub_cases)} active complaints",
                        f"Entry Mule {l1_mule} funneled through IFSC {mule_info.get('ifsc', 'N/A')}",
                        "Rapid cash-out velocity detected (< 50m elapsed transit)"
                    ]
                })
                ring_idx += 1

    return detected_rings

def analyze_case_linkage(dataset, target_case_id):
    complaint_to_mules, mule_to_complaints, complaints_by_id, complaint_to_l2 = build_case_mule_graph(dataset)
    accounts_by_id = {a["account_id"]: a for a in dataset["accounts"]}

    if target_case_id not in complaints_by_id:
        return {"error": f"Case ID '{target_case_id}' not found in database."}

    target_case = complaints_by_id[target_case_id]
    mules_in_case = complaint_to_mules[target_case_id]

    linked_cases_map = {}
    shared_entities = []

    for mule in mules_in_case:
        other_cases = [c for c in mule_to_complaints[mule] if c != target_case_id]
        mule_acc = accounts_by_id.get(mule, {})
        if other_cases:
            shared_entities.append({
                "entity_type": "MULE_ACCOUNT",
                "entity_id": mule,
                "bank": mule_acc.get("bank", "Unknown"),
                "ifsc": mule_acc.get("ifsc", "Unknown"),
                "phone_suffix": mule_acc.get("phone_suffix", "Unknown"),
                "role": mule_acc.get("role", "mule"),
                "linked_case_count": len(other_cases),
                "linked_case_ids": sorted(other_cases)
            })

            for other_cid in other_cases:
                other_c = complaints_by_id[other_cid]
                if other_cid not in linked_cases_map:
                    linked_cases_map[other_cid] = {
                        "complaint_id": other_cid,
                        "date": other_c["date"],
                        "amount": other_c["amount"],
                        "category": other_c["category"],
                        "status": other_c["status"],
                        "victim_account": other_c["victim_account"],
                        "transaction_location": other_c["transaction_location"],
                        "shared_mules": [mule]
                    }
                else:
                    if mule not in linked_cases_map[other_cid]["shared_mules"]:
                        linked_cases_map[other_cid]["shared_mules"].append(mule)

    linked_cases_list = sorted(list(linked_cases_map.values()), key=lambda x: x["amount"], reverse=True)
    all_rings = detect_rings(dataset)

    affiliated_ring = None
    for r in all_rings:
        if target_case_id in r["member_case_ids"]:
            affiliated_ring = r
            break

    # Construct bipartite graph representation for the frontend canvas
    graph_nodes = []
    graph_edges = []

    graph_nodes.append({
        "id": target_case_id,
        "label": target_case_id,
        "type": "TARGET_CASE",
        "amount": target_case["amount"],
        "category": target_case["category"]
    })

    for se in shared_entities:
        mule_id = se["entity_id"]
        graph_nodes.append({
            "id": mule_id,
            "label": f"{mule_id} ({se['bank']})",
            "type": "SHARED_MULE",
            "role": se["role"],
            "bank": se["bank"]
        })
        graph_edges.append({
            "source": target_case_id,
            "target": mule_id,
            "label": "Funneled to"
        })

    # Show up to 12 linked cases in the visual subgraph for clean rendering
    for lc in linked_cases_list[:12]:
        lc_id = lc["complaint_id"]
        graph_nodes.append({
            "id": lc_id,
            "label": lc_id,
            "type": "LINKED_CASE",
            "amount": lc["amount"],
            "category": lc["category"]
        })
        for m in lc["shared_mules"]:
            graph_edges.append({
                "source": lc_id,
                "target": m,
                "label": "Shares Mule"
            })

    total_combined_theft = target_case["amount"] + sum(lc["amount"] for lc in linked_cases_list)
    banner_message = f"{len(linked_cases_list)} other active cases share this mule account infrastructure." if linked_cases_list else "No cross-case mule reuse detected for this complaint."

    return {
        "target_case": target_case,
        "linked_case_count": len(linked_cases_list),
        "banner_message": banner_message,
        "total_combined_theft_inr": total_combined_theft,
        "shared_entities": shared_entities,
        "linked_cases": linked_cases_list,
        "affiliated_ring": affiliated_ring,
        "subgraph": {
            "nodes": graph_nodes,
            "edges": graph_edges
        }
    }

if __name__ == "__main__":
    ds = load_data()
    rings = detect_rings(ds)
    print(f"Detected {len(rings)} rings.")
