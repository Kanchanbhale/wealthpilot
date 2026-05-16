import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_CLOUD_PROJECT  = os.getenv("GOOGLE_CLOUD_PROJECT","ieor-agentic-1")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION","us-central1")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI","TRUE")
GEMINI_MODEL          = os.getenv("GEMINI_MODEL","gemini-2.0-flash")
DRIFT_THRESHOLD       = 5.0
TLH_MIN_LOSS          = 1000.0
WASH_SALE_DAYS        = 30
RISK_TOLERANCE_MAP    = {
    "conservative": {"max_equities":40,"min_fixed_income":50},
    "moderate":     {"max_equities":70,"min_fixed_income":20},
    "aggressive":   {"max_equities":95,"min_fixed_income":0},
}
