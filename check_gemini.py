import sys
import os
import logging

# Add current directory to path
sys.path.append(os.getcwd())

from backend.ai_engine.llm_client import gemini_coach

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("Checking Gemini Configuration...")
    print(f"API Key Present: {bool(gemini_coach.api_key)}")
    print(f"Proxy Setting: {gemini_coach.proxy}")
    print(f"Enabled: {gemini_coach.enabled}")
    
    if gemini_coach.enabled:
        print("\nAttempting to connect to Gemini API...")
        try:
            # Try a simple generation
            response = gemini_coach.model.generate_content("Hello, say 'Connection Successful!'")
            print(f"\nResponse: {response.text}")
            print("\nSUCCESS: Gemini API is reachable!")
        except Exception as e:
            print(f"\nFAILURE: Could not connect to Gemini API.\nError: {e}")
            print("\nPlease check your GEMINI_PROXY in .env file.")
    else:
        print("\nGemini is disabled. Check if GEMINI_API_KEY is set in .env")
