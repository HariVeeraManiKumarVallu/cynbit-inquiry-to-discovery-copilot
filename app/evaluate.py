"""Small, reproducible smoke evaluation on synthetic examples."""
from __future__ import annotations

from app.analyzer import analyze_inquiry
from app.sample_cases import SAMPLE_INQUIRIES

EXPECTED = {
    "AI workflow automation": "AI automation & agents",
    "Document and invoice extraction": "Document processing",
    "Custom client portal": "Custom software & SaaS",
    "CRM lead routing": "CRM & lead automation",
    "SEO and campaign reporting": "Digital marketing & SEO",
}


def run_evaluation() -> dict[str, float | int]:
    evaluated = 0
    correct = 0
    rows = []
    for case_name, expected in EXPECTED.items():
        result = analyze_inquiry(SAMPLE_INQUIRIES[case_name])
        predicted = result["primary_service_recommendation"]
        match = predicted == expected
        evaluated += 1
        correct += int(match)
        rows.append((case_name, expected, predicted, match))
    print("Synthetic service-routing smoke test")
    print("=" * 76)
    for name, expected, predicted, match in rows:
        print(f"{name}: expected={expected!r}; predicted={predicted!r}; match={match}")
    accuracy = correct / evaluated if evaluated else 0.0
    print(f"\nExact top-1 matches: {correct}/{evaluated} ({accuracy:.1%})")
    print("Interpretation: tiny synthetic smoke test only; not a real-world performance estimate.")
    return {"evaluated": evaluated, "correct": correct, "accuracy": accuracy}


if __name__ == "__main__":
    run_evaluation()
