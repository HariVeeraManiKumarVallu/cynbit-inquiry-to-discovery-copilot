# AI Opportunity Report: Cynbit

## 1. Executive summary

This report proposes an **Inquiry-to-Discovery Copilot** as a practical candidate proof of concept. It takes an incoming prospective-customer inquiry, suggests relevant service categories, flags missing discovery information, and prepares a draft follow-up for a human to review.

The opportunity is a hypothesis, not a verified internal problem: Cynbit's public positioning includes AI automation, software development, CRM/lead workflows, and digital services. Those offerings make inquiry triage a relevant use case to investigate, but public information does not establish Cynbit's actual lead volume, process, conversion rate, or pain points. The first real-world step should be a short stakeholder interview to confirm the workflow and baseline.

## 2. Public-information basis and limits

The assessment asks applicants to review Cynbit's website, services, and publicly available information. The opportunity should be grounded in public-facing service categories rather than assumptions about internal systems or private customer records.

Before submission, re-open the following official pages and verify that the content is current; capture access dates and exact claims in the final evidence log:

- Cynbit website: https://cynbit.com/
- Services: https://cynbit.com/services
- Products: https://cynbit.com/products
- Careers: https://cynbit.com/careers
- Contact: https://cynbit.com/contact

These links are starting points for research, not proof that every page currently exists or that every service description is unchanged. This report does not claim access to Cynbit's internal CRM, operational metrics, or customer records.

## 3. Opportunity landscape

| Candidate | Potential value | PoC feasibility | Main limitation |
|---|---|---|---|
| Inquiry-to-discovery copilot | More consistent inquiry summaries and discovery preparation | High | Must validate that inquiry handling is a real bottleneck |
| Document intake and extraction | Reduce repetitive data capture from business documents | High | Requires representative documents and field-level accuracy evaluation |
| AI-assisted project scoping | Structure requirements, assumptions, and follow-up questions | High | Output needs engineering review and cannot replace estimation |
| Service knowledge assistant | Answer service questions from approved company material | High | Requires maintained source documents and citation/grounding evaluation |
| Adaptive coding mentor | Personalize learning guidance and code feedback | Medium | Depends on product scope, learner data, and safe evaluation design |

This comparison is qualitative. It is not a measured market ranking or a claim that Cynbit has confirmed demand for any one opportunity.

## 4. Selected opportunity

### Inquiry-to-Discovery Copilot

**Proposed users:** a sales, business-development, or solutions team member who reviews inbound inquiries.

**Proposed workflow:**
1. A team member pastes an inquiry into the tool.
2. The prototype ranks likely service categories using TF-IDF similarity to a small service catalogue.
3. Transparent rules identify possible urgency, budget/timeline mentions, and discovery gaps.
4. The tool proposes follow-up questions and a draft response.
5. A human reviews, edits, and decides whether to use the draft.

**Why this is a suitable first PoC:** it has a clear user interaction, can be tested with synthetic data, is small enough for an internship assessment, and allows observable evaluation without access to private company systems.

## 5. Expected value and validation hypotheses

Potential value includes more consistent inquiry summaries, fewer missed discovery questions, and less time spent preparing an initial response. These benefits are not measured yet.

Proposed pilot metrics:
- Top-1 service routing accuracy on a human-labeled, representative set.
- Macro-F1 across service categories, to avoid hiding poor performance in less common categories.
- Field-level precision/recall for budget, timeline, and other extracted details.
- Percentage of suggested discovery questions judged relevant by reviewers.
- Human-rated draft usefulness and edit distance/time saved.
- Median processing time per inquiry.
- Rate of unsupported or misleading statements.

A small, blinded evaluation with a human-reviewed reference set should precede any business-impact claim. Do not infer revenue uplift from classification accuracy alone.

## 6. Risks and mitigations

- **Misrouting:** show evidence and alternative matches; send low-match or ambiguous cases to a human.
- **False extraction:** label fields as mentioned/not mentioned rather than inventing values; require review.
- **Privacy:** use synthetic inputs for this demo; do not connect production systems without authorization and a privacy review.
- **Over-reliance:** make the draft editable and clearly state that no message is sent automatically.
- **Stale catalogue:** validate service descriptions with Cynbit and maintain a versioned catalogue.
- **Misleading metrics:** describe the score as a heuristic completeness indicator, not a conversion probability.

## 7. Recommendation

Use this prototype to demonstrate the workflow and gather feedback, not as a production-ready sales tool. First confirm the problem with Cynbit, then collect a consented, minimized, representative evaluation set, compare the current TF-IDF/rule baseline with an LLM-assisted design if appropriate, and measure reviewer effort and quality before recommending deployment.
