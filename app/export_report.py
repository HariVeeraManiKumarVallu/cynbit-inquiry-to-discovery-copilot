"""Print a sample analysis as JSON for quick local inspection."""
import json
from app.analyzer import analyze_inquiry
from app.sample_cases import SAMPLE_INQUIRIES

if __name__ == "__main__":
    inquiry = SAMPLE_INQUIRIES["AI workflow automation"]
    print(json.dumps({"inquiry": inquiry, "analysis": analyze_inquiry(inquiry)}, indent=2, ensure_ascii=False))
