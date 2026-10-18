# Evaluation Plan

## Current evaluation

`python -m app.evaluate` runs five synthetic examples with expected service labels. The test suite checks empty input, selected service routes, JSON serialization, human-review signaling, explicit and generic company-name cases, industry-context priority, urgency classification, duration/currency parsing, token boundaries, and the same five expected labels.

These tests are intended to catch basic regressions. They are not a representative dataset, do not measure generalization, and should not be presented as proof of real-world accuracy.

## Metrics for a meaningful evaluation

- **Service routing:** top-1 accuracy, macro-F1, per-class precision/recall, and confusion matrix.
- **Field checks:** precision and recall for budget/timeline/goal mentions, with a clear annotation guide.
- **Discovery questions:** reviewer-rated relevance, completeness, and redundancy.
- **Draft response:** human-rated usefulness, factuality, tone, and time/edit effort.
- **Safety:** unsupported-claim rate, false extraction rate, and percentage correctly routed to human review when ambiguous.
- **Operational:** median and p95 latency; per-inquiry cost if an external model is introduced.

## Evaluation protocol

1. Obtain approval for the data source and minimize personal or confidential content.
2. Create a labeled dataset spanning all service categories, mixed-intent inquiries, short/ambiguous text, spelling errors, negation, and missing details.
3. Have two reviewers label a subset and resolve disagreements.
4. Freeze the service catalogue and test set before model comparisons.
5. Compare the TF-IDF/rule baseline against any candidate model on the same held-out examples.
6. Inspect false positives and false negatives by category; do not rely on aggregate accuracy alone.
7. Keep synthetic and real/authorized evaluation results separate in reports.

## Proposed pilot gates (not achieved results)

- Macro-F1 >= 0.80 on an agreed held-out routing set.
- Zero fabricated budget/timeline values in a manual audit of structured fields.
- At least 80% reviewer-rated relevance for discovery questions.
- Every outbound message reviewed and approved by a person.
- Written privacy/security approval before production customer data is used.

The targets are initial discussion points and must be agreed with Cynbit. Passing them would not by itself prove business impact.
