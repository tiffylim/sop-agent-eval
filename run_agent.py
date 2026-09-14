import json
from anthropic import Anthropic
from agent import (
    check_duplicate_with_bank,
    lookup_tier_and_daily_sum,
    request_missing_info,
    log_decision,
)

client = Anthropic()

TOOLS = [
    {
        "name": "check_duplicate_with_bank",
        "description": "Simulates emailing the partner bank to confirm whether a transaction's reference number is a duplicate. Use when the transaction was flagged for a duplicate reference number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reference_number": {"type": "string", "description": "The transaction's reference number."}
            },
            "required": ["reference_number"],
        },
    },
    {
        "name": "lookup_tier_and_daily_sum",
        "description": "Simulates looking up a customer's tier, daily limit, and today's processed total, to check whether a new transaction fits the remaining daily limit. Use when the transaction was flagged for exceeding the amount limit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "The customer's ID."},
                "new_transaction_amount": {"type": "number", "description": "Dollar amount of the flagged transaction."},
            },
            "required": ["customer_id", "new_transaction_amount"],
        },
    },
    {
        "name": "request_missing_info",
        "description": "Simulates requesting missing information from the partner bank and checking whether it arrived within the 3-business-day deadline. Use when the transaction was flagged for missing required information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "The transaction's ID."}
            },
            "required": ["transaction_id"],
        },
    },
    {
        "name": "log_decision",
        "description": "Writes the final decision and rationale to the audit log. Call this once, only after you have reasoned through the case and reached a final release or reject decision.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string"},
                "decision": {"type": "string", "enum": ["release", "reject"]},
                "rationale": {"type": "string", "description": "Plain-English explanation of why this decision was reached."},
            },
            "required": ["transaction_id", "decision", "rationale"],
        },
    },
]

TOOL_FUNCTIONS = {
    "check_duplicate_with_bank": check_duplicate_with_bank,
    "lookup_tier_and_daily_sum": lookup_tier_and_daily_sum,
    "request_missing_info": request_missing_info,
    "log_decision": log_decision,
}

SYSTEM_PROMPT = """You are a first-line transaction review analyst following this SOP:

A transaction is flagged for one of three reasons:
1. Duplicate reference number
2. Transaction amount exceeds the customer's daily limit
3. Transaction missing required information

Duplicate reference number: check with the partner bank. Confirmed duplicate -> reject. Not a duplicate -> release.
Amount exceeds limit: look up the customer's tier and daily sum. Fits within the daily limit -> release. Exceeds it -> reject.
Missing information: request it. Received and complete within the 3-business-day deadline -> release. Otherwise -> reject.

Use the appropriate tool to gather the information you need. Then explain your reasoning in
plain English, citing the specific numbers or facts that led to your decision. After
explaining your reasoning, call log_decision with your final decision and a rationale.
"""


def run_agent(transaction: dict):
    messages = [
        {
            "role": "user",
            "content": f"A transaction has been flagged for review. Details: {json.dumps(transaction)}. Please review it per the SOP.",
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        for block in response.content:
            if block.type == "text":
                print(f"\nClaude's reasoning:\n{block.text}\n")

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":

                # --- Human confirmation gate ---
                # Only reject-and-return-funds decisions need a second
                # analyst's sign-off, per SOP step 6. Release does not.
                if block.name == "log_decision" and block.input.get("decision") == "reject":
                    print(f"\n{'='*60}")
                    print("SECOND ANALYST SIGN-OFF REQUIRED")
                    print(f"Transaction: {block.input.get('transaction_id')}")
                    print("Proposed decision: REJECT (return funds)")
                    print(f"Rationale: {block.input.get('rationale')}")
                    print(f"{'='*60}")
                    approval = input("Approve this reject? (y/n): ").strip().lower()

                    if approval != "y":
                        # Option A: human override is final. No round-trip
                        # back to Claude — log it directly and end review.
                        override_reason = input(
                            "Reject declined. Enter the reason for overriding to release "
                            "(this is the final decision — it will be logged as-is): "
                        ).strip()
                        log_decision(
                            transaction_id=block.input.get("transaction_id"),
                            decision="release (override)",
                            rationale=f"Second analyst declined the reject and overrode to release. Reason: {override_reason}",
                        )
                        print("\nOverride logged. This is the final decision for this case — ending review.\n")
                        return
                    print("Approved. Proceeding.\n")
                # --- end confirmation gate ---

                func = TOOL_FUNCTIONS[block.name]
                result = func(**block.input)
                print(f"[Tool called: {block.name}({block.input}) -> {result}]")
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
                )

        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    print("\n### Case 1: Amount exceeds limit (expect: release, no confirmation needed) ###")
    test_transaction_release = {
        "transaction_id": "TXN-501",
        "customer_id": "CUST-A",
        "amount": 10000,
        "flag_reason": "amount exceeds limit",
    }
    run_agent(test_transaction_release)

    print("\n\n### Case 2: Duplicate reference number (expect: reject, confirmation required) ###")
    test_transaction_reject = {
        "transaction_id": "TXN-502",
        "reference_number": "REF1001",
        "flag_reason": "duplicate reference number",
    }
    run_agent(test_transaction_reject)

    print("\n\n### Case 3: Missing information, received in time (expect: release) ###")
    test_transaction_missing_ok = {
        "transaction_id": "TXN-201",
        "flag_reason": "missing required information",
    }
    run_agent(test_transaction_missing_ok)

    print("\n\n### Case 4: Missing information, received too late (expect: reject, confirmation required) ###")
    test_transaction_missing_late = {
        "transaction_id": "TXN-202",
        "flag_reason": "missing required information",
    }
    run_agent(test_transaction_missing_late)    