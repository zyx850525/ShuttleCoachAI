import json
import os
from typing import Dict, List, Any, Optional
from .models import AnalysisResult, Issue

class ActionAnalyzer:
    def __init__(self):
        self.rules = self._load_json("rules/issue_rules.json")
        self.thresholds = self._load_json("thresholds/level_thresholds.json")
        self.scoring_config = self._load_json("config/action_scoring_config.json")
        
        # Bilingual Templates
        self.suggestion_templates = {
            "contact_point_low": {
                "tip": {"zh": "击球点太低，无法发力。", "en": "Contact point is too low, limiting power."},
                "suggestion": {"zh": "架拍时手肘抬高，争取在最高点击球。", "en": "Raise elbow during setup, aim to hit at the highest point."}
            },
            "incomplete_swing": {
                "tip": {"zh": "挥拍动作未做完整。", "en": "Swing action is incomplete."},
                "suggestion": {"zh": "击球后球拍应顺势挥向身体对侧，不要急停。", "en": "Follow through to the opposite side of body, do not stop abruptly."}
            },
            "arm_only_smash": {
                "tip": {"zh": "只用了手臂力量，杀球不重。", "en": "Relying mainly on arm strength, smash lacks power."},
                "suggestion": {"zh": "侧身转体，利用腰腹力量带动挥拍。", "en": "Rotate torso sideways, use core power to drive the swing."}
            },
            "low_lift_height": {
                "tip": {"zh": "挑球弧度太平，容易被抓。", "en": "Lift trajectory is too flat, easily intercepted."},
                "suggestion": {"zh": "拍面朝上，多向前上方用力，把球挑到底线。", "en": "Face racket up, push forward and up, aim for the backcourt."}
            },
            "over_swing_lift": {
                "tip": {"zh": "挑球动作幅度太大。", "en": "Lift swing amplitude is too large."},
                "suggestion": {"zh": "依靠手腕手指发力，动作要小而快。", "en": "Rely on wrist and finger power, keep action compact and fast."}
            },
            "unstable_lift_contact": {
                "tip": {"zh": "击球点不稳定。", "en": "Contact point is unstable."},
                "suggestion": {"zh": "盯球要紧，脚步到位后再出手。", "en": "Watch the shuttle closely, ensure feet are in position before hitting."}
            },
            "late_net_contact": {
                "tip": {"zh": "抢网太慢，击球点低。", "en": "Slow to net, contact point is low."},
                "suggestion": {"zh": "上网步伐要快，拍头时刻举起，争取高点搓球。", "en": "Move faster to net, keep racket head up, aim for high contact point."}
            },
            "floating_net_shot": {
                "tip": {"zh": "回球质量不高，过网太高。", "en": "Net shot quality low, too high over net."},
                "suggestion": {"zh": "控制拍面角度，手感要柔和。", "en": "Control racket angle, use a soft touch."}
            },
            "low_contact_drop": {
                "tip": {"zh": "击球点太低，容易挂网或过高。", "en": "Contact point too low, risk of net or high arc."},
                "suggestion": {"zh": "架拍时手肘抬高，争取在最高点出手，保持动作一致性。", "en": "Raise elbow, hit at highest point to maintain consistency."}
            },
            "poor_deception": {
                "tip": {"zh": "动作太慢，意图太明显。", "en": "Action too slow, intent is obvious."},
                "suggestion": {"zh": "挥拍前段速度要快（模拟杀球），击球瞬间突然收力。", "en": "Fast preparation (mimic smash), sudden deceleration at impact."}
            },
            "unstable_drop": {
                "tip": {"zh": "击球时身体晃动，落点不准。", "en": "Body unstable during hit, poor accuracy."},
                "suggestion": {"zh": "保持核心稳定，脚步到位再出手，不要跑动中勉强击球。", "en": "Stabilize core, get in position, avoid hitting while off-balance."}
            },
            "low_contact_clear": {
                "tip": {"zh": "击球点太低，无法打到底线。", "en": "Contact point too low, cannot reach backcourt."},
                "suggestion": {"zh": "争取高点击球，充分利用重力势能。", "en": "Hit at high point, utilize gravity potential."}
            },
            "insufficient_swing": {
                "tip": {"zh": "挥拍幅度不足，发力不充分。", "en": "Insufficient swing amplitude, lack of power."},
                "suggestion": {"zh": "加大引拍幅度，动作要舒展，从后向前完整挥拍。", "en": "Increase backswing amplitude, extend fully from back to front."}
            },
            "unstable_clear": {
                "tip": {"zh": "击球时身体不稳，回球不到位。", "en": "Unstable body during hit, weak return."},
                "suggestion": {"zh": "核心收紧，脚步到位后再击球，避免后仰击球。", "en": "Tighten core, feet in position, avoid leaning back."}
            }
        }

    def _load_json(self, relative_path: str) -> Dict:
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, relative_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {file_path}")
            return {}

    def analyze(self, action_type: str, metrics: Dict[str, float], level_assumption: str = "beginner", keyframe_base64: Optional[str] = None) -> AnalysisResult:
        if action_type not in self.rules:
            return self._create_empty_result(action_type, level_assumption)

        # 1. Identify Issues
        issues = self._identify_issues(action_type, metrics, level_assumption)

        # 2. Calculate Score
        score = self._calculate_score(action_type, metrics)

        # 3. Generate Feedback (Try LLM first, fallback to rules)
        positive_feedback = None
        next_training_focus = None
        generation_source = "rules"
        
        try:
            from .llm_client import gemini_coach
            if gemini_coach.enabled:
                llm_result = gemini_coach.generate_feedback(action_type, int(score), metrics, issues, keyframe_base64)
                if llm_result:
                    positive_feedback = llm_result.get('positive_feedback')
                    next_training_focus = llm_result.get('next_training_focus')
                    generation_source = "gemini"
        except ImportError:
            pass # LLM client not available or dependency missing

        # Fallback Logic (if LLM disabled or failed)
        if not positive_feedback:
            generation_source = "rules"
            if not issues:
                 positive_feedback = {
                     "zh": "表现完美！动作非常标准。",
                     "en": "Perfect performance! Very standard action."
                 }
            elif score > 75:
                 positive_feedback = {
                     "zh": "整体动作流畅，核心发力感不错！",
                     "en": "Overall motion is smooth, good core power usage!"
                 }
            else:
                 positive_feedback = {
                     "zh": "基本动作框架已有，细节还需打磨。",
                     "en": "Basic framework is present, details need refinement."
                 }

        if not next_training_focus:
            next_training_focus = [issue.suggestion for issue in issues[:2]]
            if not next_training_focus:
                 next_training_focus = [
                     {"zh": "保持当前状态", "en": "Maintain current form"},
                     {"zh": "尝试提高动作一致性", "en": "Try to improve consistency"}
                 ]

        return AnalysisResult(
            action=action_type,
            level_assumption=level_assumption,
            score=int(score),
            metrics=metrics,
            issues=issues,
            positive_feedback=positive_feedback,
            next_training_focus=next_training_focus,
            generation_source=generation_source
        )

    def _identify_issues(self, action: str, metrics: Dict[str, float], level: str) -> List[Issue]:
        issues = []
        action_rules = self.rules.get(action, {})
        level_thresholds = self.thresholds.get(action, {})

        # Sort rules by priority if possible? They are in dict, so unordered strictly speaking but usually insertion order.
        # issue_rules.json has "priority" field.
        sorted_rules = sorted(action_rules.items(), key=lambda x: x[1].get("priority", 99))

        for rule_name, rule_data in sorted_rules:
            metric_name = rule_data["metric"]
            condition = rule_data["condition"] # e.g. "< beginner"
            
            if metric_name not in metrics:
                continue
            
            val = metrics[metric_name]
            
            parts = condition.split()
            if len(parts) != 2:
                continue
                
            operator, threshold_level = parts
            
            # Get threshold value
            threshold_dict = level_thresholds.get(metric_name)
            if not threshold_dict:
                continue
                
            threshold_val = threshold_dict.get(threshold_level)
            if threshold_val is None:
                continue

            is_issue = False
            if operator == "<":
                if val < threshold_val:
                    is_issue = True
            elif operator == ">":
                if val > threshold_val:
                    is_issue = True
            
            if is_issue:
                template = self.suggestion_templates.get(rule_name, {
                    "tip": {"zh": f"注意改善 {rule_name}", "en": f"Improve {rule_name}"},
                    "suggestion": {"zh": "请参考标准动作进行练习", "en": "Please practice with standard form"}
                })
                
                issues.append(Issue(
                    tag=rule_name,
                    level="warning", 
                    coach_tip=template["tip"], 
                    suggestion=template["suggestion"]
                ))
        
        return issues

    def _calculate_score(self, action: str, metrics: Dict[str, float]) -> float:
        config = self.scoring_config.get(action, {}).get("metrics", {})
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in config.items():
            val = metrics.get(metric, 0.5) 
            # Assume metric value 0.0-1.0 maps directly to score?
            # Or should we clamp it? 
            # For MVP let's map 0.0-1.0 directly to 0-100.
            total_score += val * 100 * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return round(total_score / total_weight)

    def _create_empty_result(self, action, level) -> AnalysisResult:
        return AnalysisResult(
            action=action,
            level_assumption=level,
            score=0,
            metrics={},
            issues=[],
            positive_feedback={"zh": "不支持的动作类型", "en": "Unsupported action type"},
            next_training_focus=[]
        )
