import os
import json
import logging
import base64
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiCoach:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.enabled = False
        self.model = None
        
        self.proxy = os.getenv("GEMINI_PROXY")

        if self.api_key:
            try:
                # Configure proxy if available
                if self.proxy:
                    os.environ["http_proxy"] = self.proxy
                    os.environ["https_proxy"] = self.proxy
                    logger.info(f"Using Gemini Proxy: {self.proxy}")

                # Configure GenAI - prefer REST for better proxy compatibility
                genai.configure(api_key=self.api_key, transport="rest")
                
                # Use gemini-3-flash-preview as requested
                self.model = genai.GenerativeModel('gemini-3-flash-preview') 
                self.enabled = True
                logger.info("Gemini AI Coach enabled.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

    def generate_feedback(self, action_type: str, score: int, metrics: Dict, issues: List, keyframe_base64: Optional[str]) -> Optional[Dict]:
        if not self.enabled:
            return None

        try:
            # 1. Prepare Text Prompt
            # Convert Issue objects to dicts for prompt
            issues_data = []
            for i in issues:
                if hasattr(i, 'model_dump'):
                    issues_data.append(i.model_dump())
                elif hasattr(i, 'dict'):
                    issues_data.append(i.dict())
                else:
                    issues_data.append(str(i))

            prompt = f"""
            You are a professional Badminton Coach using high-tech analysis.
            Analyze this student's performance based on the data and the attached keyframe image (hit point).
            
            Action: {action_type}
            Score: {score}/100
            Biomechanical Metrics (0-1 scale): {json.dumps(metrics)}
            Identified Issues: {json.dumps(issues_data, ensure_ascii=False)}
            
            Task:
            1. Provide "positive_feedback": A brief overall summary (1-2 sentences). Be encouraging but point out the main characteristic.
            2. Provide "next_training_focus": 2 to 3 specific, actionable training drills or focus points.
            
            Output strictly in this JSON structure (do not include markdown code blocks):
            {{
                "positive_feedback": {{ "zh": "Chinese text", "en": "English text" }},
                "next_training_focus": [
                    {{ "zh": "Chinese text", "en": "English text" }},
                    ...
                ]
            }}
            """
            
            content = [prompt]
            
            # 2. Prepare Image
            if keyframe_base64:
                try:
                    # Remove header if present
                    if "," in keyframe_base64:
                        b64_data = keyframe_base64.split(",")[1]
                    else:
                        b64_data = keyframe_base64
                    
                    image_data = base64.b64decode(b64_data)
                    
                    # Pass as blob
                    image_blob = {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                    content.append(image_blob)
                except Exception as img_err:
                    logger.warning(f"Failed to process keyframe for Gemini: {img_err}")

            # 3. Call API
            # generation_config={"response_mime_type": "application/json"} is supported in newer SDKs
            response = self.model.generate_content(content)
            
            # 4. Parse Response
            text = response.text.strip()
            
            # Clean markdown code blocks
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            return json.loads(text.strip())

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None

# Singleton instance
gemini_coach = GeminiCoach()
