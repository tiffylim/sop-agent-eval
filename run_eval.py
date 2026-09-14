from eval_scenarios import SCENARIOS
from run_agent import run_agent


def run_eval():
    results = []

    for scenario in SCENARIOS:
        print(f"\n{'#'*70}")
        print(f"# Scenario {scenario['id']}: {scenario['description']}")
        print(f"{'#'*70}")

        decision, rationale = run_agent(scenario["transaction"], auto_approve_for_eval=True)

        is_match = (decision == scenario["correct_decision"])
        results.append({
            "id": scenario["id"],
            "description": scenario["description"],
            "correct": scenario["correct_decision"],
            "agent_decision": decision,
            "match": is_match,
            "rationale": rationale,
        })

    print(f"\n\n{'='*70}")
    print("EVAL REPORT")
    print(f"{'='*70}\n")

    for r in results:
        status = "PASS" if r["match"] else "FAIL"
        print(f"[{status}] {r['id']}: {r['description']}")
        print(f"       Correct: {r['correct']:<8} Agent: {r['agent_decision']}")
        if not r["match"]:
            print(f"       Agent's rationale: {r['rationale']}")
        print()

    num_correct = sum(1 for r in results if r["match"])
    total = len(results)
    accuracy = num_correct / total

    correct_labels = [s["correct_decision"] for s in SCENARIOS]
    majority_label = max(set(correct_labels), key=correct_labels.count)
    baseline_correct = sum(1 for label in correct_labels if label == majority_label)
    baseline_accuracy = baseline_correct / total

    print(f"{'='*70}")
    print(f"Agent accuracy:    {num_correct}/{total} = {accuracy:.1%}")
    print(f"Baseline (always guess '{majority_label}'): {baseline_correct}/{total} = {baseline_accuracy:.1%}")
    print(f"{'='*70}")


if __name__ == "__main__":
    run_eval()