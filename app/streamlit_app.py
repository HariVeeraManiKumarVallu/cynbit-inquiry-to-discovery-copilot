"""Streamlit interface for the Cynbit Inquiry-to-Discovery Copilot."""
import json
import streamlit as st

from app.analyzer import analyze_inquiry
from app.sample_cases import SAMPLE_INQUIRIES

st.set_page_config(page_title="Cynbit Inquiry-to-Discovery Copilot", page_icon="🧭", layout="wide")
st.title("Inquiry-to-Discovery Copilot")
st.caption("Cynbit AI/ML Engineer Intern assessment · NLP proof of concept")
st.warning("Use synthetic text only. Do not enter confidential or real customer information. All recommendations and drafts require human review.")

with st.sidebar:
    st.header("Try a synthetic example")
    selected = st.selectbox("Example inquiry", ["Choose an example…", *SAMPLE_INQUIRIES.keys()])
    st.markdown("**What it does**")
    st.markdown("- Ranks relevant services using TF-IDF similarity\n- Shows keyword evidence\n- Flags discovery gaps\n- Drafts a response for human review\n- Exports structured JSON")
    st.caption("No LLM/API call is made. The service catalogue is a small, manually authored reference set.")

initial_text = SAMPLE_INQUIRIES.get(selected, "") if selected != "Choose an example…" else ""
inquiry = st.text_area("Business inquiry", value=initial_text, height=210, placeholder="Describe the prospective customer's business need…")
if st.button("Analyze inquiry", type="primary"):
    result = analyze_inquiry(inquiry)
    if "error" in result:
        st.error(result["error"])
    else:
        st.session_state["analysis_result"] = result
        st.session_state["analysis_input"] = inquiry

result = st.session_state.get("analysis_result")
if result:
    st.divider()
    st.subheader("Analysis results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Suggested service", result["primary_service_recommendation"])
    c2.metric("Completeness indicator", f"{result['lead_readiness_score']}/100")
    c3.metric("Urgency signal", result["urgency_signal"].title())
    if result.get("urgency_evidence"):
        st.caption("Urgency evidence: " + ", ".join(result["urgency_evidence"]))
    else:
        st.caption("No explicit urgency phrase or time window was detected.")
    st.caption(result["score_interpretation"])

    left, right = st.columns(2)
    with left:
        st.markdown("#### Inquiry summary")
        st.json({k: result[k] for k in ["company_guess", "industry_or_context", "budget_status", "timeline_status", "recommendation_status"]})
        st.markdown("#### Top service matches")
        if result["service_matches"]:
            for item in result["service_matches"]:
                st.write(f"**{item['service']}** — ranking score `{item['score']:.3f}`")
                st.caption(f"TF-IDF similarity: {item['tfidf_similarity']:.3f} · Keyword evidence: {', '.join(item['matched_terms']) or 'no exact keyword match'}")
        else:
            st.info("No service match. Route to human discovery.")
    with right:
        st.markdown("#### Missing discovery questions")
        if result["missing_discovery_questions"]:
            for question in result["missing_discovery_questions"]:
                st.write(f"- {question}")
        else:
            st.success("No discovery gaps were detected by the current rules.")
        st.markdown("#### Draft response — edit before use")
        edited_draft = st.text_area("Follow-up draft", value=result["draft_follow_up"], height=220, key="editable_draft")

    export_result = {**result, "draft_follow_up": edited_draft}
    export_payload = {"inquiry": st.session_state.get("analysis_input", ""), "analysis": export_result}
    st.download_button("Download analysis as JSON", data=json.dumps(export_payload, indent=2, ensure_ascii=False), file_name="cynbit_inquiry_analysis.json", mime="application/json")
    st.caption(f"Method: {result['method']}. The ranking score is not a probability. No message is sent automatically.")
