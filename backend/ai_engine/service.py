from typing import Dict, Any, Optional
from .processor import VideoProcessor
from .analyzer import ActionAnalyzer
from .models import AnalysisResult

class AIAnalysisService:
    def __init__(self):
        self.processor = VideoProcessor()
        self.analyzer = ActionAnalyzer()

    def analyze_video(self, video_path: str, action_type: Optional[str] = None, level_assumption: str = "beginner") -> Dict[str, Any]:
        """
        Orchestrates the analysis process:
        1. Process video to get raw metrics AND detect action type.
        2. Analyze metrics against rules using the detected action.
        3. Return structured JSON result.
        """
        # 1. Extract Metrics & Detect Action
        try:
            processing_result = self.processor.process_video(video_path)
            raw_metrics = processing_result["metrics"]
            detected_action = processing_result["detected_action"]
            keyframe = processing_result.get("keyframe")
        except Exception as e:
            # Fallback for error handling
            return {"error": f"Video processing failed: {str(e)}"}

        # 2. Analyze
        # Use detected action if no specific action_type is forced
        final_action = action_type if action_type else detected_action
        
        # Pass keyframe to analyzer for LLM context
        result = self.analyzer.analyze(final_action, raw_metrics, level_assumption, keyframe)
        
        # Inject Keyframe
        if keyframe:
            result.keyframe_base64 = keyframe
        
        # 3. Serialize
        # AnalysisResult is a Pydantic model, use model_dump to return dict
        return result.model_dump()

# Singleton instance for easy import
analysis_service = AIAnalysisService()
