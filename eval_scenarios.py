# Hand-labeled ground truth for the SOP triage agent.
# Every "correct_decision" was decided BEFORE running the agent, based on
# the SOP policy in SOP_SPEC.md — not by looking at what the agent produced.
#
# All fixtures referenced here (EVAL-REF-*, EVAL-CUST-A, EVAL-S6/7/8) live
# in agent.py's isolated eval mock dictionaries, kept separate from the
# Day 5 dev-testing fixtures so this golden set can't drift from unrelated
# debugging changes elsewhere.

SCENARIOS = [
    {
        "id": "S1",
        "description": "Confirmed duplicate reference number",
        "transaction": {
            "transaction_id": "EVAL-S1",
            "reference_number": "EVAL-REF-S1",
            "flag_reason": "duplicate reference number",
        },
        "correct_decision": "reject",
    },
    {
        "id": "S2",
        "description": "Reference number checked, not a duplicate",
        "transaction": {
            "transaction_id": "EVAL-S2",
            "reference_number": "EVAL-REF-S2",
            "flag_reason": "duplicate reference number",
        },
        "correct_decision": "release",
    },
    {
        "id": "S3",
        "description": "Comfortably under daily limit ($190K of $200K)",
        "transaction": {
            "transaction_id": "EVAL-S3",
            "customer_id": "EVAL-CUST-A",
            "amount": 10000,
            "flag_reason": "amount exceeds limit",
        },
        "correct_decision": "release",
    },
    {
        "id": "S4",
        "description": "Clearly over daily limit ($210K of $200K)",
        "transaction": {
            "transaction_id": "EVAL-S4",
            "customer_id": "EVAL-CUST-A",
            "amount": 30000,
            "flag_reason": "amount exceeds limit",
        },
        "correct_decision": "reject",
    },
    {
        "id": "S5",
        "description": "Exactly at daily limit boundary ($200K of $200K)",
        "transaction": {
            "transaction_id": "EVAL-S5",
            "customer_id": "EVAL-CUST-A",
            "amount": 20000,
            "flag_reason": "amount exceeds limit",
        },
        "correct_decision": "release",
    },
    {
        "id": "S6",
        "description": "Missing info received in time (day 2 of 3)",
        "transaction": {
            "transaction_id": "EVAL-S6",
            "flag_reason": "missing required information",
        },
        "correct_decision": "release",
    },
    {
        "id": "S7",
        "description": "Missing info never arrives by deadline (day 4)",
        "transaction": {
            "transaction_id": "EVAL-S7",
            "flag_reason": "missing required information",
        },
        "correct_decision": "reject",
    },
    {
        "id": "S8",
        "description": "Missing info received exactly on deadline (day 3)",
        "transaction": {
            "transaction_id": "EVAL-S8",
            "flag_reason": "missing required information",
        },
        "correct_decision": "release",
    },
]