import json
from datetime import datetime

# Mocked partner bank duplicate-check responses, keyed by reference number
MOCK_DUPLICATE_RESPONSES = {
    "REF1001": True,   # partner bank confirms this is a duplicate
    "REF1002": False,  # partner bank confirms this is NOT a duplicate
}

# Mocked customer tier + daily-sum data, keyed by customer_id
MOCK_CUSTOMER_DATA = {
    "CUST-A": {"tier": "Tier 1", "daily_limit": 200_000, "already_processed_today": 180_000},
    "CUST-B": {"tier": "Tier 2", "daily_limit": 500_000, "already_processed_today": 100_000},
}

# Mocked missing-information responses, keyed by transaction_id
MOCK_MISSING_INFO_RESPONSES = {
    "TXN-201": {"received": True, "days_taken": 2},
    "TXN-202": {"received": False, "days_taken": 4},
}


def check_duplicate_with_bank(reference_number: str) -> dict:
    """Simulates emailing the partner bank to confirm whether a reference
    number is a duplicate. Returns whether it was confirmed as a duplicate."""
    is_duplicate = MOCK_DUPLICATE_RESPONSES.get(reference_number, False)
    return {"reference_number": reference_number, "confirmed_duplicate": is_duplicate}


def lookup_tier_and_daily_sum(customer_id: str, new_transaction_amount: float) -> dict:
    """Simulates looking up a customer's tier, daily limit, and how much
    they've already processed today. Returns whether the new transaction
    would fit within today's remaining daily limit."""
    customer = MOCK_CUSTOMER_DATA.get(customer_id)
    if not customer:
        return {"error": f"No customer record found for {customer_id}"}

    total_if_processed = customer["already_processed_today"] + new_transaction_amount
    fits_within_limit = total_if_processed <= customer["daily_limit"]

    return {
        "customer_id": customer_id,
        "tier": customer["tier"],
        "daily_limit": customer["daily_limit"],
        "already_processed_today": customer["already_processed_today"],
        "total_if_processed": total_if_processed,
        "fits_within_limit": fits_within_limit,
    }


def request_missing_info(transaction_id: str) -> dict:
    """Simulates requesting missing information from the partner bank and
    checking whether it arrived within the 3-business-day deadline."""
    result = MOCK_MISSING_INFO_RESPONSES.get(
        transaction_id, {"received": False, "days_taken": None}
    )
    within_deadline = bool(result["received"]) and result["days_taken"] is not None and result["days_taken"] <= 3
    return {
        "transaction_id": transaction_id,
        "received": result["received"],
        "days_taken": result["days_taken"],
        "within_deadline": within_deadline,
    }


def log_decision(transaction_id: str, decision: str, rationale: str) -> None:
    """Really writes the decision and rationale to a local log file —
    this one is NOT mocked, it's a genuine audit trail."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "transaction_id": transaction_id,
        "decision": decision,
        "rationale": rationale,
    }
    with open("decision_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Logged: {transaction_id} -> {decision}")