import json
import unittest

from app.analyzer import analyze_inquiry
from app.evaluate import EXPECTED
from app.sample_cases import SAMPLE_INQUIRIES


class AnalyzerTests(unittest.TestCase):
    def test_empty_input_returns_error(self):
        self.assertIn("error", analyze_inquiry("  "))

    def test_document_inquiry_routes_to_document_processing(self):
        result = analyze_inquiry("We need to extract invoice fields from PDF documents.")
        self.assertEqual(result["primary_service_recommendation"], "Document processing")
        self.assertTrue(result["human_review_required"])

    def test_custom_portal_routes_to_software(self):
        result = analyze_inquiry("We need a client portal and dashboard integrated with our API.")
        self.assertEqual(result["primary_service_recommendation"], "Custom software & SaaS")

    def test_crm_inquiry_routes_to_crm(self):
        result = analyze_inquiry("We need CRM lead routing for new sales enquiries.")
        self.assertEqual(result["primary_service_recommendation"], "CRM & lead automation")

    def test_ambiguous_inquiry_routes_to_human(self):
        result = analyze_inquiry("We need help with our business and want to discuss options.")
        self.assertTrue(result["human_review_required"])
        self.assertEqual(result["primary_service_recommendation"], "Needs human discovery")
        self.assertEqual(result["recommendation_status"], "low_match_route_to_human")

    def test_generic_ecommerce_description_is_not_company_name(self):
        result = analyze_inquiry("We are a small e-commerce business looking for CRM integration.")
        self.assertIsNone(result["company_guess"])
        self.assertEqual(result["industry_or_context"], "Retail / e-commerce")

    def test_explicit_company_name_is_extracted(self):
        result = analyze_inquiry("Company name: Northstar Retail. We need CRM lead routing.")
        self.assertEqual(result["company_guess"], "Northstar Retail")

    def test_pilot_alone_does_not_signal_urgency(self):
        result = analyze_inquiry("We want to discuss a pilot for CRM lead routing.")
        self.assertEqual(result["urgency_signal"], "unspecified")
        self.assertEqual(result["urgency_evidence"], [])

    def test_explicit_urgent_language_is_high_urgency(self):
        result = analyze_inquiry("We urgently need CRM lead routing as soon as possible.")
        self.assertEqual(result["urgency_signal"], "high")
        self.assertTrue(result["urgency_evidence"])

    def test_urgent_requests_as_a_feature_do_not_mark_the_project_urgent(self):
        result = analyze_inquiry("We want a system that identifies urgent customer requests and routes them to our CRM within 6–8 weeks.")
        self.assertEqual(result["urgency_signal"], "medium")
        self.assertNotIn("urgent", result["urgency_evidence"])

    def test_duration_range_is_recognized_as_timeline(self):
        result = analyze_inquiry("We need a CRM solution within 6–8 weeks and have an approved budget.")
        self.assertEqual(result["timeline_status"], "mentioned")
        self.assertEqual(result["urgency_signal"], "medium")

    def test_keyword_boundary_prevents_app_substring_match(self):
        result = analyze_inquiry("We need support with happy customers and business growth.")
        self.assertNotIn("app", result["evidence_terms"])

    def test_rupee_symbol_is_preserved(self):
        result = analyze_inquiry("We have a budget of ₹2–4 lakh for a custom dashboard.")
        self.assertEqual(result["budget_status"], "mentioned")

    def test_result_is_json_serializable(self):
        json.dumps(analyze_inquiry(SAMPLE_INQUIRIES["AI workflow automation"]), ensure_ascii=False)

    def test_completeness_score_is_based_on_discovery_dimensions(self):
        result = analyze_inquiry("We need CRM integration, a budget, and launch within 8 weeks.")
        self.assertGreaterEqual(result["lead_readiness_score"], 0)
        self.assertLessEqual(result["lead_readiness_score"], 100)
        self.assertIn("six discovery dimensions", result["score_interpretation"])

    def test_all_labeled_smoke_cases_have_expected_top_match(self):
        for case_name, expected in EXPECTED.items():
            with self.subTest(case=case_name):
                result = analyze_inquiry(SAMPLE_INQUIRIES[case_name])
                self.assertEqual(result["primary_service_recommendation"], expected)


if __name__ == "__main__":
    unittest.main()
