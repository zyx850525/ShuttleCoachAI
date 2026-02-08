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

    def generate_feedback(self, action_type: str, score: int, metrics: Dict, issues: List, keyframe_base64: Optional[str], action_sequence: List[str] = []) -> Optional[Dict]:
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
            Analyze this student's performance based on the data and the attached action sequence images.
            The images represent the Preparation, Hit Point, and Follow-through phases.
            
            Action: {action_type}
            Score: {score}/100
            Biomechanical Metrics (0-1 scale): {json.dumps(metrics)}
            Identified Issues: {json.dumps(issues_data, ensure_ascii=False)}
            
            Task:
            1. Provide "positive_feedback": A brief overall summary (1-2 sentences). Analyze the flow of the action (preparation -> hit -> follow-through).
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
            
            # 2. Prepare Images (Sequence preferred, fallback to keyframe)
            images_to_process = action_sequence if action_sequence else ([keyframe_base64] if keyframe_base64 else [])
            
            for b64_img in images_to_process:
                if not b64_img: continue
                try:
                    # Remove header if present
                    if "," in b64_img:
                        b64_data = b64_img.split(",")[1]
                    else:
                        b64_data = b64_img
                    
                    image_data = base64.b64decode(b64_data)
                    
                    # Pass as blob
                    image_blob = {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                    content.append(image_blob)
                except Exception as img_err:
                    logger.warning(f"Failed to process image for Gemini: {img_err}")

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

    def chat_with_coach(self, context: Dict[str, Any], user_msg: str, history: List[Dict[str, str]]) -> str:
        if not self.enabled:
            return "AI Coach is currently unavailable."
            
        try:
            # 1. Build System Context
            action = context.get('action', 'Unknown')
            score = context.get('score', 0)
            issues = context.get('issues', [])
            
            # Convert issues to text summary
            issues_text = ""
            for idx, issue in enumerate(issues):
                tag = issue.get('tag', 'Issue') if isinstance(issue, dict) else issue.tag
                tip = issue.get('coach_tip', {}).get('zh', '') if isinstance(issue, dict) else issue.coach_tip.get('zh', '')
                issues_text += f"{idx+1}. {tag}: {tip}\n"

            system_prompt = f"""
你是一位专业的羽毛球教练。你刚刚分析了这位学员的动作视频。
分析结果如下：
- 动作类型：{action}
- 得分：{score}/100
- 发现的主要问题：
{issues_text}

请基于以上分析结果回答学员的问题。
保持专业、鼓励的语气。如果学员问的问题与羽毛球无关，请礼貌地将话题引回羽毛球。
回答请简练，不要长篇大论。
"""
            
            # 2. Build Chat History for API
            gemini_history = []
            
            # Prepend context
            gemini_history.append({"role": "user", "parts": [system_prompt + "\n\n(Context provided. Please acknowledge.)"]})
            gemini_history.append({"role": "model", "parts": ["收到，我是您的羽毛球 AI 教练。请问有什么可以帮您？"]})
            
            for msg in history:
                role = "user" if msg['role'] == 'user' else "model"
                content = msg['content']
                gemini_history.append({"role": role, "parts": [content]})
            
            # 3. Start Chat
            chat = self.model.start_chat(history=gemini_history)
            
            # 4. Send Message
            response = chat.send_message(user_msg)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Chat generation failed: {e}")
            return "抱歉，教练现在有点忙，请稍后再试。"

# Singleton instance
gemini_coach = GeminiCoach()
