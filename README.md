# Cynbit Inquiry-to-Discovery Copilot

A small, explainable NLP proof of concept for triaging prospective-customer inquiries. Version 0.3 ranks a fixed catalogue of Cynbit service categories using TF-IDF cosine similarity and boundary-aware keyword evidence, checks for missing discovery details, applies explicit urgency rules, and drafts a follow-up for human review.

**Important:** this is a prototype based on public-facing service categories and synthetic examples. It does not establish that Cynbit has a lead-management problem, use Cynbit's internal data, predict lead conversion, or send messages. The service catalogue and synthetic evaluation set should be validated with the company before any pilot.

## Assessment deliverables

- `docs/AI_OPPORTUNITY_REPORT.md` — opportunity analysis and selection rationale.
- `app/` — working prototype and evaluation code.
- `docs/TECHNICAL_APPROACH.md` — model choice, pipeline, architecture, risks, and execution plan.
- `docs/EVALUATION_PLAN.md` — current smoke-test results and a plan for a proper evaluation.

## What the prototype does

1. Accepts a business inquiry as text.
2. Ranks service descriptions using TF-IDF vectorization and cosine similarity.
3. Shows the top service matches and exact keyword evidence.
4. Checks for missing business goal, systems, timeline, budget, data/privacy, and decision-process details using phrase/word-boundary matching.
5. Produces a completeness indicator based on the six discovery dimensions and an urgency signal with the matched urgency evidence.
6. Drafts a follow-up message for a human to review.
7. Exports the inquiry analysis as JSON.

It uses scikit-learn's TF-IDF implementation, not a trained classifier, generative LLM, RAG pipeline, or vector database. The service ranking score is not a probability. Completeness and urgency checks are rules, not ML predictions. The company-name extractor only returns a guess when it detects an explicit label or a title-cased name pattern; it intentionally leaves generic descriptions unlabelled.

## Requirements

- Python 3.11 or newer
- `uv` package manager
- Internet access on first dependency resolution (packages must be downloaded if not cached)

## Setup with uv (recommended)

Open a terminal in the project root:

```bash
uv sync
uv run streamlit run app/streamlit_app.py
```

`uv sync` resolves the dependencies in `pyproject.toml` and creates `uv.lock` on the first run. Commit the generated `uv.lock` so subsequent installs can use a reproducible resolution. In a repository where `uv.lock` has already been committed, use `uv sync --locked` to verify it has not changed.

Run tests and the smoke evaluation:

```bash
uv run python -m pytest -v
uv run python -m app.evaluate
uv run python -m app.export_report
```

### Alternative pip setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Project structure

```text
app/
  analyzer.py          TF-IDF service ranking and rule-based field checks
  streamlit_app.py     Interactive demo
  sample_cases.py      Synthetic examples; not real customer records
  evaluate.py          Small labeled smoke evaluation
  export_report.py     Print one analysis as JSON
  __init__.py

docs/
  AI_OPPORTUNITY_REPORT.md
  TECHNICAL_APPROACH.md
  EVALUATION_PLAN.md

tests/
  test_analyzer.py

pyproject.toml         Project and dependency configuration for uv
requirements.txt       pip-compatible dependency list
```

## Current baseline revision (v0.3)

- Word/phrase matching now uses token boundaries to reduce substring false positives.
- Company-name extraction avoids treating generic phrases such as “a small e-commerce business” as a company name.
- Explicit e-commerce context takes precedence over technology terms mentioned as requested features.
- “Pilot” alone does not mark an inquiry as urgent; explicit urgency phrases and stated durations are recorded as evidence.
- The completeness indicator is the percentage of six discovery dimensions with keyword evidence, not a measure of lead quality or conversion likelihood.
- Tests cover these behaviors, but the evaluation set remains small and synthetic.

## Privacy and limitations

- Use synthetic inquiries only; do not paste personal, confidential, or production customer data into this demo.
- The service catalogue is a small manually written reference set based on public service descriptions and must be checked against current company offerings.
- TF-IDF is lexical and can miss paraphrases or confuse overlapping categories.
- Rule-based extraction can misread negation or context (for example, mentioning a budget without giving an amount).
- The lead-readiness indicator is an arbitrary completeness heuristic, not a sales-conversion score.
- The current evaluation set is tiny and synthetic. Its results are a smoke test only and are not a claim of real-world accuracy.
- No LLM, RAG, external API, CRM integration, or automatic message sending is implemented.
- A production pilot would require stakeholder validation, privacy/security review, access controls, retention policies, monitoring, a representative labeled dataset, and human approval.
