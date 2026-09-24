"""
FORTIVEXA - Synthetic Cybercrime Dataset Generator (TRL 3 Experimental Proof-of-Concept)
Complies with SIH problem statement schema:
- 120 synthetic cases + 8 clean demo cases (128 total)
- 24 accounts with role taxonomy (victim, mule_l1, mule_l2, cashout_withdrawal)
- 14 fictional ATM/Branch locations with coordinates and risk indices
- 384 transactions modeling multi-hop mule layering (Victim -> L1 -> L2 -> Cashout)
- 19 seeded cross-case fraud rings for empirical validation of the linkage algorithm
"""

import json
import random
import datetime
import os

random.seed(42)

# 14 Fictional Geographic Hotspots (Metro Cyber Sector coordinates)
LOCATIONS = [
    {"location_id": "LOC-DEMO-01", "name": "Sector 4 Central ATM Kiosk", "type": "ATM", "lat": 12.9716, "lng": 77.5946, "jurisdiction": "Metro Central PS", "risk_index": 0.88, "historical_cashouts": 34},
    {"location_id": "LOC-DEMO-02", "name": "Tech Hub Commercial Bank e-Lobby", "type": "e-Lobby", "lat": 12.9782, "lng": 77.6012, "jurisdiction": "Cyber North PS", "risk_index": 0.74, "historical_cashouts": 21},
    {"location_id": "LOC-DEMO-03", "name": "Outer Ring Road Metro Station ATM", "type": "ATM", "lat": 12.9352, "lng": 77.6245, "jurisdiction": "South Cyber Cell", "risk_index": 0.92, "historical_cashouts": 48},
    {"location_id": "LOC-DEMO-04", "name": "North Junction Retail Hub ATM 02", "type": "ATM", "lat": 13.0012, "lng": 77.5714, "jurisdiction": "North Suburban PS", "risk_index": 0.65, "historical_cashouts": 14},
    {"location_id": "LOC-DEMO-05", "name": "Industrial Area State Bank Kiosk", "type": "ATM", "lat": 12.9124, "lng": 77.6410, "jurisdiction": "Industrial Cyber Wing", "risk_index": 0.81, "historical_cashouts": 29},
    {"location_id": "LOC-DEMO-06", "name": "Grand Mall Basement ATM Enclosure", "type": "ATM", "lat": 12.9601, "lng": 77.6480, "jurisdiction": "East Zone PS", "risk_index": 0.58, "historical_cashouts": 12},
    {"location_id": "LOC-DEMO-07", "name": "Railway Terminal Plaza Cash Point", "type": "ATM", "lat": 12.9774, "lng": 77.5728, "jurisdiction": "Transit Cyber Cell", "risk_index": 0.85, "historical_cashouts": 41},
    {"location_id": "LOC-DEMO-08", "name": "Cyber Towers Gate 3 Express ATM", "type": "ATM", "lat": 12.9850, "lng": 77.6105, "jurisdiction": "Cyber North PS", "risk_index": 0.79, "historical_cashouts": 26},
    {"location_id": "LOC-DEMO-09", "name": "Highway Petrol Pump Mini ATM", "type": "ATM", "lat": 12.9189, "lng": 77.5855, "jurisdiction": "South Cyber Cell", "risk_index": 0.69, "historical_cashouts": 18},
    {"location_id": "LOC-DEMO-10", "name": "University Campus Main Branch Kiosk", "type": "ATM", "lat": 12.9930, "lng": 77.5320, "jurisdiction": "West Cyber PS", "risk_index": 0.42, "historical_cashouts": 7},
    {"location_id": "LOC-DEMO-11", "name": "Old Market Street Co-op Bank ATM", "type": "ATM", "lat": 12.9655, "lng": 77.5790, "jurisdiction": "Metro Central PS", "risk_index": 0.63, "historical_cashouts": 15},
    {"location_id": "LOC-DEMO-12", "name": "Suburban Metro Pillar 142 Kiosk", "type": "ATM", "lat": 13.0180, "lng": 77.5540, "jurisdiction": "North Suburban PS", "risk_index": 0.71, "historical_cashouts": 19},
    {"location_id": "LOC-DEMO-13", "name": "Airport Expressway Toll Plaza ATM", "type": "ATM", "lat": 13.0850, "lng": 77.6180, "jurisdiction": "Highway Cyber Wing", "risk_index": 0.52, "historical_cashouts": 9},
    {"location_id": "LOC-DEMO-14", "name": "Financial District Overseas Bank Kiosk", "type": "ATM", "lat": 12.9490, "lng": 77.6120, "jurisdiction": "Financial Crime Wing", "risk_index": 0.77, "historical_cashouts": 25},
]

ACCOUNTS_METADATA = [
    {"account_id": "ACC-MULE-001", "bank": "Axis Neo Bank", "ifsc": "UTIB0002194", "phone_suffix": "8812", "role": "mule_l1", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-MULE-002", "bank": "Federal Digital", "ifsc": "FDRL0001042", "phone_suffix": "3341", "role": "mule_l1", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-003", "bank": "Kotak Smart", "ifsc": "KKBK0000841", "phone_suffix": "9021", "role": "mule_l1", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-004", "bank": "ICICI Apex", "ifsc": "ICIC0006240", "phone_suffix": "4419", "role": "mule_l2", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-MULE-005", "bank": "Yes Express", "ifsc": "YESB0000318", "phone_suffix": "7712", "role": "mule_l2", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-MULE-006", "bank": "IndusInd Rapid", "ifsc": "INDB0000512", "phone_suffix": "2291", "role": "mule_l2", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-007", "bank": "Canara Digital", "ifsc": "CNRB0001923", "phone_suffix": "5504", "role": "mule_l1", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-008", "bank": "HDFC Horizon", "ifsc": "HDFC0001844", "phone_suffix": "1198", "role": "mule_l1", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-009", "bank": "PNB Online", "ifsc": "PUNB0003912", "phone_suffix": "6640", "role": "mule_l2", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-MULE-010", "bank": "IDFC First Pay", "ifsc": "IDFB0004011", "phone_suffix": "8823", "role": "mule_l1", "risk_rating": "MEDIUM"},
    {"account_id": "ACC-MULE-011", "bank": "RBL FastBank", "ifsc": "RATN0000129", "phone_suffix": "9934", "role": "mule_l2", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-012", "bank": "Equitas Small Bank", "ifsc": "ESFB0001099", "phone_suffix": "1102", "role": "mule_l1", "risk_rating": "MEDIUM"},
    {"account_id": "ACC-MULE-013", "bank": "Paytm Payments Bank", "ifsc": "PYTM0123456", "phone_suffix": "7789", "role": "mule_l2", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-014", "bank": "Airtel Payments Bank", "ifsc": "AIRP0000001", "phone_suffix": "5531", "role": "mule_l1", "risk_rating": "MEDIUM"},
    {"account_id": "ACC-MULE-015", "bank": "Bandhan Quick", "ifsc": "BDBL0000210", "phone_suffix": "4490", "role": "mule_l2", "risk_rating": "HIGH"},
    {"account_id": "ACC-MULE-016", "bank": "UCO Modern", "ifsc": "UCBA0001402", "phone_suffix": "6618", "role": "mule_l1", "risk_rating": "LOW"},
    {"account_id": "ACC-CASHOUT-01", "bank": "Apex Debit Card Ops", "ifsc": "ICIC0006240", "phone_suffix": "0011", "role": "withdrawal", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-CASHOUT-02", "bank": "QuickCash ATM Proxy", "ifsc": "YESB0000318", "phone_suffix": "0022", "role": "withdrawal", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-CASHOUT-03", "bank": "RapidWithdraw Card Ops", "ifsc": "PUNB0003912", "phone_suffix": "0033", "role": "withdrawal", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-CASHOUT-04", "bank": "Terminal Point Cash Proxy", "ifsc": "KKBK0000841", "phone_suffix": "0044", "role": "withdrawal", "risk_rating": "CRITICAL"},
    {"account_id": "ACC-VICTIM-001", "bank": "State Bank of India", "ifsc": "SBIN0000843", "phone_suffix": "1234", "role": "victim", "risk_rating": "LOW"},
    {"account_id": "ACC-VICTIM-002", "bank": "HDFC Bank", "ifsc": "HDFC0000042", "phone_suffix": "5678", "role": "victim", "risk_rating": "LOW"},
    {"account_id": "ACC-VICTIM-003", "bank": "ICICI Bank", "ifsc": "ICIC0000011", "phone_suffix": "9012", "role": "victim", "risk_rating": "LOW"},
    {"account_id": "ACC-VICTIM-004", "bank": "Punjab National Bank", "ifsc": "PUNB0000192", "phone_suffix": "3456", "role": "victim", "risk_rating": "LOW"},
]

FRAUD_CATEGORIES = [
    "UPI Phishing / Impersonation",
    "Part-Time Job / Task Scam",
    "Fake Investment / Stock Advisory",
    "Electricity Bill / KYC Suspension",
    "Loan App Extortion / Quick Credit",
    "SIM Swap / OTP Interception",
    "Card Skimming & Unauthorized Debit",
    "Crypto Arbitrage Scam"
]

STATUS_CHOICES = ["Open", "Under Investigation", "Escalated", "Actioned - Location Flagged"]

# 19 Ground Truth Seeded Rings with dedicated mule structures
SEED_RINGS = [
    {"ring_id": "RING-01", "name": "Apex Syndicate Layer A", "l1_mule": "ACC-MULE-001", "shared_account_id": "ACC-MULE-004", "member_case_ids": ["CMP-1001", "CMP-1014", "CMP-1028", "CMP-1052"], "primary_loc": "LOC-DEMO-01"},
    {"ring_id": "RING-02", "name": "East Coast Job-Scam Hub", "l1_mule": "ACC-MULE-002", "shared_account_id": "ACC-MULE-005", "member_case_ids": ["CMP-1002", "CMP-1019", "CMP-1033", "CMP-1077"], "primary_loc": "LOC-DEMO-03"},
    {"ring_id": "RING-03", "name": "FastCash Multi-Hop Ring", "l1_mule": "ACC-MULE-003", "shared_account_id": "ACC-MULE-009", "member_case_ids": ["CMP-1003", "CMP-1022", "CMP-1045", "CMP-1066", "CMP-1090"], "primary_loc": "LOC-DEMO-07"},
    {"ring_id": "RING-04", "name": "Metro North Phishing Cluster", "l1_mule": "ACC-MULE-001", "shared_account_id": "ACC-MULE-006", "member_case_ids": ["CMP-1004", "CMP-1015", "CMP-1037", "CMP-1061"], "primary_loc": "LOC-DEMO-04"},
    {"ring_id": "RING-05", "name": "Industrial Sector Withdrawal Grid", "l1_mule": "ACC-MULE-007", "shared_account_id": "ACC-MULE-006", "member_case_ids": ["CMP-1005", "CMP-1031", "CMP-1059", "CMP-1084"], "primary_loc": "LOC-DEMO-05"},
    {"ring_id": "RING-06", "name": "Tech Corridor KYC Ring", "l1_mule": "ACC-MULE-002", "shared_account_id": "ACC-MULE-004", "member_case_ids": ["CMP-1006", "CMP-1025", "CMP-1048", "CMP-1073"], "primary_loc": "LOC-DEMO-02"},
    {"ring_id": "RING-07", "name": "Outer Ring Stock Scam Loop", "l1_mule": "ACC-MULE-008", "shared_account_id": "ACC-MULE-011", "member_case_ids": ["CMP-1007", "CMP-1039", "CMP-1068", "CMP-1099"], "primary_loc": "LOC-DEMO-03"},
    {"ring_id": "RING-08", "name": "Terminal Quick-Drain Network", "l1_mule": "ACC-MULE-003", "shared_account_id": "ACC-MULE-005", "member_case_ids": ["CMP-1008", "CMP-1029", "CMP-1055", "CMP-1081"], "primary_loc": "LOC-DEMO-08"},
    {"ring_id": "RING-09", "name": "West Cyber Micro-Mule Pool", "l1_mule": "ACC-MULE-007", "shared_account_id": "ACC-MULE-013", "member_case_ids": ["CMP-1010", "CMP-1034", "CMP-1063", "CMP-1088"], "primary_loc": "LOC-DEMO-09"},
    {"ring_id": "RING-10", "name": "Urban Crypto Drain Ring", "l1_mule": "ACC-MULE-008", "shared_account_id": "ACC-MULE-015", "member_case_ids": ["CMP-1012", "CMP-1041", "CMP-1070", "CMP-1095"], "primary_loc": "LOC-DEMO-01"},
    {"ring_id": "RING-11", "name": "Highway Corridor Extraction Chain", "l1_mule": "ACC-MULE-010", "shared_account_id": "ACC-MULE-013", "member_case_ids": ["CMP-1016", "CMP-1044", "CMP-1072", "CMP-1102"], "primary_loc": "LOC-DEMO-12"},
    {"ring_id": "RING-12", "name": "Suburban Night-Shift Ring", "l1_mule": "ACC-MULE-012", "shared_account_id": "ACC-MULE-015", "member_case_ids": ["CMP-1018", "CMP-1047", "CMP-1075", "CMP-1108"], "primary_loc": "LOC-DEMO-11"},
    {"ring_id": "RING-13", "name": "Apex Layer B Sub-Syndicate", "l1_mule": "ACC-MULE-014", "shared_account_id": "ACC-MULE-004", "member_case_ids": ["CMP-1020", "CMP-1050", "CMP-1080", "CMP-1112"], "primary_loc": "LOC-DEMO-01"},
    {"ring_id": "RING-14", "name": "Digital Task Scam Cell C", "l1_mule": "ACC-MULE-010", "shared_account_id": "ACC-MULE-011", "member_case_ids": ["CMP-1023", "CMP-1053", "CMP-1083", "CMP-1115"], "primary_loc": "LOC-DEMO-06"},
    {"ring_id": "RING-15", "name": "Pillar 142 Fast-Drain Syndicate", "l1_mule": "ACC-MULE-012", "shared_account_id": "ACC-MULE-009", "member_case_ids": ["CMP-1026", "CMP-1056", "CMP-1086", "CMP-1118"], "primary_loc": "LOC-DEMO-12"},
    {"ring_id": "RING-16", "name": "Central Retail Extortion Pod", "l1_mule": "ACC-MULE-014", "shared_account_id": "ACC-MULE-006", "member_case_ids": ["CMP-1027", "CMP-1058", "CMP-1089", "CMP-1121"], "primary_loc": "LOC-DEMO-05"},
    {"ring_id": "RING-17", "name": "Financial District Impersonation Loop", "l1_mule": "ACC-MULE-016", "shared_account_id": "ACC-MULE-005", "member_case_ids": ["CMP-1030", "CMP-1060", "CMP-1092", "CMP-1124"], "primary_loc": "LOC-DEMO-14"},
    {"ring_id": "RING-18", "name": "Airport Plaza Rapid Cashout", "l1_mule": "ACC-MULE-016", "shared_account_id": "ACC-MULE-009", "member_case_ids": ["CMP-1035", "CMP-1065", "CMP-1096", "CMP-1126"], "primary_loc": "LOC-DEMO-13"},
    {"ring_id": "RING-19", "name": "Commercial e-Lobby Syndicate", "l1_mule": "ACC-MULE-001", "shared_account_id": "ACC-MULE-006", "member_case_ids": ["CMP-1038", "CMP-1069", "CMP-1098", "CMP-1128"], "primary_loc": "LOC-DEMO-02"}
]

CASE_TO_RING = {}
for r in SEED_RINGS:
    for cid in r["member_case_ids"]:
        CASE_TO_RING[cid] = r

def generate_dataset():
    complaints = []
    transactions = []
    account_stats = {acc["account_id"]: {"incoming_count": 0, "outgoing_count": 0, "total_volume": 0, "connected": set()} for acc in ACCOUNTS_METADATA}
    start_date = datetime.datetime(2026, 8, 1, 10, 0, 0)

    # 8 Hand-Authored Clean Demo Cases
    CLEAN_DEMO_CASES = [
        {"complaint_id": "CMP-1001", "amount": 95000, "category": "UPI Phishing / Impersonation", "victim_account": "ACC-VICTIM-001", "suspicious_account": "ACC-MULE-001", "intermediate_mule": "ACC-MULE-004", "withdrawal_account": "ACC-CASHOUT-01", "days_offset": 2, "hour": 18, "minute": 15, "target_loc": "LOC-DEMO-01", "status": "Actioned - Location Flagged", "narrative": "Victim received counterfeit electricity disconnection warning with APK link. ₹95,000 debited via IMPS to Axis mule ACC-MULE-001, transferred within 18 minutes to L2 mule ACC-MULE-004."},
        {"complaint_id": "CMP-1002", "amount": 142000, "category": "Part-Time Job / Task Scam", "victim_account": "ACC-VICTIM-002", "suspicious_account": "ACC-MULE-002", "intermediate_mule": "ACC-MULE-005", "withdrawal_account": "ACC-CASHOUT-02", "days_offset": 4, "hour": 19, "minute": 30, "target_loc": "LOC-DEMO-03", "status": "Under Investigation", "narrative": "Telegram task completion scam. ₹1,42,000 deposited in 2 tranches into Federal mule ACC-MULE-002, layered to Yes Express L2 mule ACC-MULE-005."},
        {"complaint_id": "CMP-1003", "amount": 210000, "category": "Fake Investment / Stock Advisory", "victim_account": "ACC-VICTIM-003", "suspicious_account": "ACC-MULE-003", "intermediate_mule": "ACC-MULE-009", "withdrawal_account": "ACC-CASHOUT-03", "days_offset": 6, "hour": 20, "minute": 10, "target_loc": "LOC-DEMO-07", "status": "Escalated", "narrative": "Institutional trading group impersonation. Victim directed to transfer ₹2,10,000 to Kotak mule ACC-MULE-003, routed immediately to PNB L2 hub ACC-MULE-009."},
        {"complaint_id": "CMP-1004", "amount": 68000, "category": "Electricity Bill / KYC Suspension", "victim_account": "ACC-VICTIM-004", "suspicious_account": "ACC-MULE-001", "intermediate_mule": "ACC-MULE-006", "withdrawal_account": "ACC-CASHOUT-01", "days_offset": 8, "hour": 18, "minute": 45, "target_loc": "LOC-DEMO-04", "status": "Open", "narrative": "Counterfeit utility bill payment SMS. Victim entered credentials on phishing portal; funds moved via ACC-MULE-001 to IndusInd mule ACC-MULE-006."},
        {"complaint_id": "CMP-1005", "amount": 185000, "category": "Loan App Extortion / Quick Credit", "victim_account": "ACC-VICTIM-001", "suspicious_account": "ACC-MULE-007", "intermediate_mule": "ACC-MULE-006", "withdrawal_account": "ACC-CASHOUT-02", "days_offset": 10, "hour": 17, "minute": 50, "target_loc": "LOC-DEMO-05", "status": "Actioned - Location Flagged", "narrative": "Illegal instant credit application harassment. Coerced transfer of ₹1,85,000 into Canara mule ACC-MULE-007, layered to ACC-MULE-006 within 12 minutes."},
        {"complaint_id": "CMP-1006", "amount": 74000, "category": "SIM Swap / OTP Interception", "victim_account": "ACC-VICTIM-002", "suspicious_account": "ACC-MULE-002", "intermediate_mule": "ACC-MULE-004", "withdrawal_account": "ACC-CASHOUT-04", "days_offset": 12, "hour": 18, "minute": 20, "target_loc": "LOC-DEMO-02", "status": "Under Investigation", "narrative": "Fraudulent SIM replacement triggered unauthorized net-banking reset. ₹74,000 routed to ACC-MULE-002, subsequently consolidated at ACC-MULE-004."},
        {"complaint_id": "CMP-1007", "amount": 320000, "category": "Crypto Arbitrage Scam", "victim_account": "ACC-VICTIM-003", "suspicious_account": "ACC-MULE-008", "intermediate_mule": "ACC-MULE-011", "withdrawal_account": "ACC-CASHOUT-03", "days_offset": 14, "hour": 20, "minute": 40, "target_loc": "LOC-DEMO-03", "status": "Escalated", "narrative": "Off-market crypto arbitrage portal lure. High-value transfer of ₹3,20,000 split across HDFC mule ACC-MULE-008 and layered into RBL mule ACC-MULE-011."},
        {"complaint_id": "CMP-1008", "amount": 115000, "category": "Card Skimming & Unauthorized Debit", "victim_account": "ACC-VICTIM-004", "suspicious_account": "ACC-MULE-003", "intermediate_mule": "ACC-MULE-005", "withdrawal_account": "ACC-CASHOUT-01", "days_offset": 16, "hour": 19, "minute": 15, "target_loc": "LOC-DEMO-08", "status": "Actioned - Location Flagged", "narrative": "Cloned debit card transactions at commercial POS terminal. Instant routing into Kotak mule ACC-MULE-003 and onward to Yes Express hub ACC-MULE-005."}
    ]

    txn_counter = 1001

    # Add 8 clean demo cases
    for case_data in CLEAN_DEMO_CASES:
        cid = case_data["complaint_id"]
        c_time = start_date + datetime.timedelta(days=case_data["days_offset"], hours=case_data["hour"] - 1, minutes=case_data["minute"])
        amt = case_data["amount"]
        c_loc = next(l for l in LOCATIONS if l["location_id"] == case_data["target_loc"])
        
        complaint = {
            "complaint_id": cid,
            "date": c_time.strftime("%Y-%m-%d"),
            "amount": amt,
            "victim_account": case_data["victim_account"],
            "suspicious_account": case_data["suspicious_account"],
            "transaction_datetime": c_time.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_location": c_loc["name"],
            "category": case_data["category"],
            "status": case_data["status"],
            "narrative": case_data["narrative"],
            "ground_truth_ring": CASE_TO_RING.get(cid, {}).get("ring_id", "RING-01"),
            "predicted_atm_location_id": case_data["target_loc"]
        }
        complaints.append(complaint)

        # Hop 1
        t1_id = f"TXN-{txn_counter}"
        txn_counter += 1
        transactions.append({
            "transaction_id": t1_id,
            "case_id": cid,
            "source_account": case_data["victim_account"],
            "destination_account": case_data["suspicious_account"],
            "amount": amt,
            "timestamp": c_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": "Online / Net-Banking Portal",
            "type": "IMPS",
            "risk_score": 88
        })

        # Hop 2
        t2_id = f"TXN-{txn_counter}"
        txn_counter += 1
        t2_time = c_time + datetime.timedelta(minutes=18)
        layer_amt = round(amt * 0.96)
        transactions.append({
            "transaction_id": t2_id,
            "case_id": cid,
            "source_account": case_data["suspicious_account"],
            "destination_account": case_data["intermediate_mule"],
            "amount": layer_amt,
            "timestamp": t2_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": "Inter-Bank Instant Gateway",
            "type": "UPI",
            "risk_score": 94
        })

        # Hop 3
        t3_id = f"TXN-{txn_counter}"
        txn_counter += 1
        t3_time = t2_time + datetime.timedelta(minutes=32)
        withdraw_amt = round(layer_amt * 0.95)
        transactions.append({
            "transaction_id": t3_id,
            "case_id": cid,
            "source_account": case_data["intermediate_mule"],
            "destination_account": case_data["withdrawal_account"],
            "amount": withdraw_amt,
            "timestamp": t3_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": c_loc["name"],
            "type": "ATM_WITHDRAWAL",
            "risk_score": 97
        })

    # Generate cases CMP-1009 to CMP-1128
    for i in range(9, 129):
        cid = f"CMP-{1000 + i}"
        days_offset = (i * 3) % 45
        if random.random() < 0.65:
            hour = random.choice([17, 18, 19, 20, 21])
        else:
            hour = random.choice([10, 11, 14, 15, 16, 22])
        minute = random.randint(0, 59)
        c_time = start_date + datetime.timedelta(days=days_offset, hours=hour, minutes=minute)

        ring = CASE_TO_RING.get(cid)
        if ring:
            l1_acc = ring.get("l1_mule", "ACC-MULE-001")
            l2_acc = ring["shared_account_id"]
            target_loc_id = ring["primary_loc"]
        else:
            # Independent cases with sporadic mules
            l1_acc = random.choice(["ACC-MULE-010", "ACC-MULE-012", "ACC-MULE-014", "ACC-MULE-016"])
            l2_acc = random.choice(["ACC-MULE-013", "ACC-MULE-015", "ACC-MULE-011"])
            target_loc_id = random.choice([l["location_id"] for l in LOCATIONS])

        target_loc = next(l for l in LOCATIONS if l["location_id"] == target_loc_id)
        victim_acc = random.choice(["ACC-VICTIM-001", "ACC-VICTIM-002", "ACC-VICTIM-003", "ACC-VICTIM-004"])
        cashout_acc = random.choice(["ACC-CASHOUT-01", "ACC-CASHOUT-02", "ACC-CASHOUT-03", "ACC-CASHOUT-04"])

        amt = random.choice([45000, 52000, 68000, 85000, 95000, 110000, 135000, 160000, 195000, 240000, 310000])
        cat = random.choice(FRAUD_CATEGORIES)
        status = random.choice(STATUS_CHOICES)

        complaint = {
            "complaint_id": cid,
            "date": c_time.strftime("%Y-%m-%d"),
            "amount": amt,
            "victim_account": victim_acc,
            "suspicious_account": l1_acc,
            "transaction_datetime": c_time.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_location": target_loc["name"],
            "category": cat,
            "status": status,
            "narrative": f"Reported cyber fraudulent debit of ₹{amt:,} under {cat}. Originating victim account {victim_acc} transferred funds to initial entry mule {l1_acc}.",
            "ground_truth_ring": ring["ring_id"] if ring else "UNASSIGNED",
            "predicted_atm_location_id": target_loc_id
        }
        complaints.append(complaint)

        # Hop 1
        t1_id = f"TXN-{txn_counter}"
        txn_counter += 1
        transactions.append({
            "transaction_id": t1_id,
            "case_id": cid,
            "source_account": victim_acc,
            "destination_account": l1_acc,
            "amount": amt,
            "timestamp": c_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": "Online / Cyber Banking",
            "type": random.choice(["UPI", "IMPS", "NEFT"]),
            "risk_score": random.randint(75, 92)
        })

        # Hop 2
        t2_id = f"TXN-{txn_counter}"
        txn_counter += 1
        t2_time = c_time + datetime.timedelta(minutes=random.randint(10, 25))
        layer_amt = round(amt * 0.95)
        transactions.append({
            "transaction_id": t2_id,
            "case_id": cid,
            "source_account": l1_acc,
            "destination_account": l2_acc,
            "amount": layer_amt,
            "timestamp": t2_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": "Inter-Bank Clearing Switch",
            "type": "UPI",
            "risk_score": random.randint(82, 96)
        })

        # Hop 3
        t3_id = f"TXN-{txn_counter}"
        txn_counter += 1
        t3_time = t2_time + datetime.timedelta(minutes=random.randint(15, 50))
        withdraw_amt = round(layer_amt * 0.94)
        transactions.append({
            "transaction_id": t3_id,
            "case_id": cid,
            "source_account": l2_acc,
            "destination_account": cashout_acc,
            "amount": withdraw_amt,
            "timestamp": t3_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": target_loc["name"],
            "type": "ATM_WITHDRAWAL",
            "risk_score": random.randint(88, 99)
        })

    # Aggregate accounts
    for t in transactions:
        src = t["source_account"]
        dst = t["destination_account"]
        amt = t["amount"]
        if src in account_stats:
            account_stats[src]["outgoing_count"] += 1
            account_stats[src]["total_volume"] += amt
            account_stats[src]["connected"].add(dst)
        if dst in account_stats:
            account_stats[dst]["incoming_count"] += 1
            account_stats[dst]["total_volume"] += amt
            account_stats[dst]["connected"].add(src)

    accounts_payload = []
    for meta in ACCOUNTS_METADATA:
        acc_id = meta["account_id"]
        stats = account_stats.get(acc_id, {"incoming_count": 0, "outgoing_count": 0, "total_volume": 0, "connected": set()})
        accounts_payload.append({
            "account_id": acc_id,
            "bank": meta["bank"],
            "ifsc": meta["ifsc"],
            "phone_suffix": meta["phone_suffix"],
            "role": meta["role"],
            "risk_rating": meta["risk_rating"],
            "incoming_txn_count": stats["incoming_count"],
            "outgoing_txn_count": stats["outgoing_count"],
            "total_amount": stats["total_volume"],
            "connected_accounts": sorted(list(stats["connected"]))
        })

    rings_payload = []
    for r in SEED_RINGS:
        member_complaints = [c for c in complaints if c["complaint_id"] in r["member_case_ids"]]
        total_diverted = sum(c["amount"] for c in member_complaints)
        rings_payload.append({
            "ring_id": r["ring_id"],
            "name": r["name"],
            "shared_account_id": r["shared_account_id"],
            "primary_location_id": r["primary_loc"],
            "member_case_ids": r["member_case_ids"],
            "total_cases": len(r["member_case_ids"]),
            "total_diverted_inr": total_diverted,
            "status": "DETECTED_AND_CORRELATED",
            "confidence_score": 0.94
        })

    full_dataset = {
        "metadata": {
            "version": "2.0.0",
            "project_stage": "TRL 3 - Experimental Proof of Concept",
            "dataset_type": "Synthetic Cybercrime Complaints with Ground Truth Rings",
            "generated_at": datetime.datetime.now().isoformat(),
            "total_complaints": len(complaints),
            "clean_demo_cases": len(CLEAN_DEMO_CASES),
            "total_accounts": len(accounts_payload),
            "total_transactions": len(transactions),
            "total_seeded_rings": len(rings_payload),
            "locations_count": len(LOCATIONS)
        },
        "complaints": complaints,
        "accounts": accounts_payload,
        "transactions": transactions,
        "rings": rings_payload,
        "locations": LOCATIONS
    }

    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "dataset.json"), "w", encoding="utf-8") as f:
        json.dump(full_dataset, f, indent=2)

    with open(os.path.join(out_dir, "clean_walkthrough_cases.json"), "w", encoding="utf-8") as f:
        json.dump(CLEAN_DEMO_CASES, f, indent=2)

    print("Dataset refreshed successfully.")

if __name__ == "__main__":
    generate_dataset()
