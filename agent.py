import json
from datetime import datetime

# ---------------------------------------------------------------------------
# Day 5 development/smoke-test fixtures — informal manual testing only.
# NOT used by the formal eval suite (eval_scenarios.py), so these can be
# freely changed while debugging without affecting eval results.
# ---------------------------------------------------------------------------
MOCK_DUPLICATE_RESPONSES = {
    "REF1001": True,
    "REF1002": False,
}

MOCK_CUSTOMER_DATA = {
    "CUST-A": {"tier": "Tier 1", "daily_limit": 200_000, "already_processed_today": 180_000},
    "CUST-B": {"tier": "Tier 2", "daily_limit": 500_000, "already_processed_today": 100_000},
}

MOCK_MISSING_INFO_RESPONSES = {
    "TXN-201": {"received": True, "days_taken": 2},
    "TXN-202": {"received": False, "days_taken": 4},
}

# ---------------------------------------------------------------------------
# Formal eval suite fixtures — used only by eval_scenarios.py's hand-labeled
# ground truth. Kept isolated from the dev-testing fixtures above so the
# eval's golden set can't silently drift from unrelated debugging changes.
# ---------------------------------------------------------------------------
MOCK_EVAL_DUPLICATE_RESPONSES = {
    "EVAL-REF-S1": True,   # confirmed duplicate -> reject
    "EVAL-REF-S2": False,  # not a duplicate -> release
}

MOCK_EVAL_CUSTOMER_DATA = {
    "EVAL-CUST-A": {"tier": "Tier 1", "daily_limit": 200_000, "already_processed_today": 180_000},
}

MOCK_EVAL_MISSING_INFO_RESPONSES = {
    "EVAL-S6": {"received": True, "days_taken": 2},   # in time -> release
    "EVAL-S7": {"received": False, "days_taken": 4},  # never arrives -> reject
    "EVAL-S8": {"received": True, "days_taken": 3},   # exactly on deadline -> release
}


def check_duplicate_with_bank(reference_number: str) -> dict:
    """Simulates emailing the partner bank to confirm whether a reference
    number is a duplicate. Checks both dev-testing and eval fixtures."""
    combined = {**MOCK_DUPLICATE_RESPONSES, **MOCK_EVAL_DUPLICATE_RESPONSES}
    is_duplicate = combined.get(reference_number, False)
    return {"reference_number": reference_number, "confirmed_duplicate": is_duplicate}


def lookup_tier_and_daily_sum(customer_id: str, new_transaction_amount: float) -> dict:
    """Simulates looking up a customer's tier, daily limit, and how much
    they've already processed today. Checks both dev-testing and eval
    fixtures."""
    combined = {**MOCK_CUSTOMER_DATA, **MOCK_EVAL_CUSTOMER_DATA}
    customer = combined.get(customer_id)
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
    checking whether it arrived within the 3-business-day deadline. Checks
    both dev-testing and eval fixtures."""
    combined = {**MOCK_MISSING_INFO_RESPONSES, **MOCK_EVAL_MISSING_INFO_RESPONSES}
    result = combined.get(transaction_id, {"received": False, "days_taken": None})
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