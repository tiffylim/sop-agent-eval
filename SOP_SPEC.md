# SOP: Transaction Review Triage (First-Line Analyst)

## Context
This SOP covers first-line analyst triage for transactions flagged for
review after passing initial KYC/sanctions screening. Tier limits and
review deadlines below are illustrative placeholder values, not real
policy figures.

## Steps

1. [ACTION] Transaction is flagged for review and enters the queue.

2. [DECISION] Analyst identifies which of three reasons applies:
   - Duplicate reference number
   - Transaction amount exceeds limit
   - Transaction missing required information

3. Branch A — Duplicate reference number
   - [ACTION] Email partner bank to confirm whether this is a duplicate.
   - [DECISION] Confirmed duplicate -> reject and return funds.
     Not a duplicate -> release.

4. Branch B — Amount exceeds limit
   - [ACTION] Look up the customer's business tier and its daily
     transaction limit.
   - [ACTION] Sum the customer's transactions already processed today.
   - [DECISION] Sum of today's transactions plus this new one fits
     within the tier's daily limit -> release.
     Exceeds the daily limit -> reject and return funds.

5. Branch C — Missing information
   - [ACTION] Email partner bank requesting the missing information.
   - [ACTION] Wait up to the review deadline (illustrative: 3 business
     days).
   - [DECISION] Information received and complete before deadline ->
     release.
     Not received, or still incomplete, after deadline -> reject and
     return funds.

6. [CONFIRM] Before executing any reject-and-return-funds action, a
   second analyst must sign off. Release actions do not require a
   second sign-off.

7. [ACTION] Log the decision and rationale for every case, regardless
   of outcome, for the audit trail.

## Config values (illustrative placeholders, not real policy)
- Tier 1: $200,000 daily cap
- Tier 2: $500,000 daily cap
- Missing-information deadline: 3 business days
