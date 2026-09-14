# sop-agent-eval

Claude agent that walks a fintech ops SOP step-by-step, with a hand-labeled evaluation of its decisions.

## Evaluation results

| Metric | Result |
|---|---|
| Agent accuracy | 8/8 (100%) |
| Naive baseline ("always guess release") | 5/8 (62.5%) |

The baseline matters more than the headline number: 5 of the 8 hand-labeled
scenarios are correctly "release," so a system doing zero real reasoning
would already score 62.5% by guessing the same answer every time. The
baseline fails on exactly the 3 "reject" scenarios — a confirmed duplicate,
a transaction over the daily limit, and information that never arrived —
which are the financially consequential mistakes in a real review process.
The agent scored correctly on all three.

All 8 scenarios, including the exact "correct" answer for each, were
written down **before** the agent was run against them — see
`eval_scenarios.py`.

## What this is

A first-line transaction review analyst, modeled on a real fintech
operations triage process: a flagged transaction comes in, gets sorted
into one of three review branches, and either gets released or rejected
based on the specifics of the case.

1. **Duplicate reference number** — confirm with the partner bank;
   confirmed duplicate → reject, otherwise → release
2. **Amount exceeds daily limit** — look up the customer's tier and
   today's processed total; fits within the daily cap → release, exceeds
   it → reject
3. **Missing required information** — request it from the partner bank;
   received and complete within the 3-business-day deadline → release,
   otherwise → reject

Full step-by-step SOP: [`SOP_SPEC.md`](./SOP_SPEC.md).

**Reject decisions require a second analyst's sign-off before execution.**
Release does not. This mirrors the real SOP: a decision that returns funds
carries more risk than one that lets a transaction proceed, so it gets a
second pair of eyes. If the second analyst declines, their reasoning
becomes the final decision directly — it is not sent back to Claude for
reconsideration (see *Design decisions*, below).

## Example run (Scenario S1 — confirmed duplicate)

```
[Tool called: check_duplicate_with_bank({'reference_number': 'EVAL-REF-S1'})
 -> {'reference_number': 'EVAL-REF-S1', 'confirmed_duplicate': True}]

Claude's reasoning:
The partner bank confirmed that reference number EVAL-REF-S1 is indeed a
duplicate. Per the SOP, a confirmed duplicate reference number requires
rejection of the transaction.

============================================================
SECOND ANALYST SIGN-OFF REQUIRED
Transaction: EVAL-S1
Proposed decision: REJECT (return funds)
Rationale: Transaction was flagged for a duplicate reference number
(EVAL-REF-S1). Contacted the partner bank via check_duplicate_with_bank,
which confirmed_duplicate: true. Per SOP, a confirmed duplicate reference
number results in rejection.
============================================================
Approve this reject? (y/n): y
Approved. Proceeding.

Logged: EVAL-S1 -> reject
```

## Design decisions worth calling out

- **Boundary policy is inclusive, by deliberate choice, not default
  behavior.** A transaction landing exactly on the daily cap, or
  information arriving exactly on the deadline day, both count as passing.
  This was a real policy call made explicitly (see `eval_scenarios.py`
  scenarios S5 and S8) rather than left to whatever a `<` vs. `<=`
  happened to default to.
- **A human override on reject is final — it is not fed back to Claude.**
  When a second analyst declines a proposed reject, the code logs their
  reasoning directly and ends the review. The alternative (looping the
  human's explanation back to Claude for a fresh decision) was considered
  and rejected: a human overriding on business judgment is a human
  decision, not something that should be re-litigated by the model.
- **Evaluation fixtures are isolated from development fixtures.** The mock
  data used by `eval_scenarios.py` (`EVAL-*` IDs) is kept separate from
  the informal fixtures used while building the agent (`TXN-*`, `REF-*`
  IDs), so debugging changes elsewhere can't silently shift what the eval
  is actually measuring.
- **Only `log_decision` writes real output.** Every other tool
  (`check_duplicate_with_bank`, `lookup_tier_and_daily_sum`,
  `request_missing_info`) is mocked, since there's no real partner bank or
  customer database to call — but the audit log they feed into is a real,
  append-only file (`decision_log.jsonl`), because that part is genuinely
  useful to test truthfully.

## Project structure

| File | Purpose |
|---|---|
| `SOP_SPEC.md` | The full SOP, written from real ops experience, before any code |
| `agent.py` | Tool functions Claude can call, plus the real audit-log writer |
| `run_agent.py` | The agent loop: Claude reasons, calls tools, hits the confirmation gate |
| `eval_scenarios.py` | Hand-labeled ground truth, written before evaluation |
| `run_eval.py` | Runs all scenarios, grades the agent against ground truth, reports accuracy vs. baseline |

## Running it

Requires Python 3.10+ and an Anthropic API key set as `ANTHROPIC_API_KEY`.

```
pip install anthropic
python3 run_agent.py   # run the agent on a handful of sample cases
python3 run_eval.py    # run the full evaluation suite and print the accuracy report
```