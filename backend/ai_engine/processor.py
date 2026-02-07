import cv2
import base64
import mediapipe as mp
from typing import Dict, List, Tuple, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_video(self, video_path: str) -> Dict[str, any]:
        """
        Process the video and extract real biomechanical metrics using MediaPipe.
        Returns a dictionary containing metrics and detected action type.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        landmarks_history = []
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            
            # Convert to RGB for MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            
            if results.pose_landmarks:
                # Store key landmarks for this frame
                landmarks = results.pose_landmarks.landmark
                frame_data = {
                    'nose': landmarks[self.mp_pose.PoseLandmark.NOSE],
                    'right_wrist': landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST],
                    'left_wrist': landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST],
                    'right_shoulder': landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER],
                    'left_shoulder': landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER],
                    'right_hip': landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP],
                    'left_hip': landmarks[self.mp_pose.PoseLandmark.LEFT_HIP],
                    'right_ankle': landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE],
                    'left_ankle': landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE],
                    'right_elbow': landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW],
                    'left_elbow': landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW],
                }
                landmarks_history.append(frame_data)
                
        cap.release()
        
        if not landmarks_history:
            return {
                "detected_action": "unknown",
                "metrics": {}
            }

        # 1. Detect Action Type
        detected_action = self._detect_action_type(landmarks_history)

        # 2. Identify Key Phase (Hit Window)
        # Returns start_index, end_index, peak_velocity_index
        hit_window = self._detect_hit_phase(landmarks_history)
        
        # 3. Calculate Real Metrics
        metrics = self._calculate_real_metrics(landmarks_history, detected_action, hit_window, fps)
        
        # 4. Generate Keyframe Snapshot
        peak_idx = hit_window[2]
        keyframe_data = self._generate_keyframe(video_path, peak_idx, landmarks_history[peak_idx])

        return {
            "detected_action": detected_action,
            "metrics": metrics,
            "keyframe": keyframe_data
        }

    def _detect_action_type(self, history: List[Dict]) -> str:
        """
        Heuristic-based action detection.
        Returns: 'smash', 'lift', 'net_shot', 'drop', or 'clear'
        """
        if not history:
            return "smash" 

        # 1. Calculate Body Height (Reference)
        body_heights = []
        for frame in history:
            nose = frame['nose'].y
            ankle = (frame['right_ankle'].y + frame['left_ankle'].y) / 2
            h = abs(ankle - nose)
            if h > 0.05: body_heights.append(h)
        
        avg_body_height = float(np.mean(body_heights)) if body_heights else 0.5

        # 2. Extract Normalized Features
        heights_above_nose = [] # Relative to body height
        normalized_velocities = [] # Relative to body height
        downward_velocities = [] # Relative to body height (positive = down)
        wrist_ys = []

        for i, frame in enumerate(history):
            # Wrist Height check
            r_y = frame['right_wrist'].y
            l_y = frame['left_wrist'].y
            min_wrist_y = min(r_y, l_y)
            wrist_ys.append(min_wrist_y)
            
            nose_y = frame['nose'].y
            # Positive means above nose
            relative_h = (nose_y - min_wrist_y) / avg_body_height
            heights_above_nose.append(relative_h)
            
            # Velocity check
            if i > 0:
                curr = frame['right_wrist']
                prev = history[i-1]['right_wrist']
                dist = np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
                # Normalize velocity
                norm_vel = dist / avg_body_height
                normalized_velocities.append(norm_vel)
                
                # Downward velocity (Y diff)
                dy = curr.y - prev.y # Positive if moving down
                norm_dy = dy / avg_body_height
                downward_velocities.append(norm_dy)
        
        max_reach = max(heights_above_nose) if heights_above_nose else 0.0
        max_velocity = max(normalized_velocities) if normalized_velocities else 0.0
        max_downward_velocity = max(downward_velocities) if downward_velocities else 0.0
        
        # Variance of Wrist Y (normalized by body height)
        # We want variance of (wrist_y / body_height)
        normalized_wrist_ys = [y / avg_body_height for y in wrist_ys]
        y_variance = np.var(normalized_wrist_ys) if normalized_wrist_ys else 0.0
        
        logger.info(f"Action Detect: Reach={max_reach:.2f}, MaxVel={max_velocity:.2f}, MaxDownVel={max_downward_velocity:.2f}, Var={y_variance:.4f}")

        # Heuristic 1: Overhead Shots
        # Wrist goes significantly above nose (e.g., > 0.2 body heights)
        # Previous absolute threshold was 0.35 (screen top). 
        IS_OVERHEAD = max_reach > 0.15 
        
        if IS_OVERHEAD:
            # 3-Way Classification: Drop vs Smash vs Clear
            
            # 1. Check for Drop (Low absolute speed)
            if max_velocity <= 0.12:
                return "drop"
            else:
                # Fast Swing: Distinguish Smash vs Clear using Downward Velocity
                # Smash has high downward velocity (vertical strike)
                # Clear has forward/upward velocity (lower downward component relative to total speed)
                
                # Threshold heuristic: 0.05 normalized body heights per frame
                if max_downward_velocity > 0.05:
                    return "smash"
                else:
                    return "clear"
            
        # Heuristic 2: Underhand Shots
        # Distinguish Lift vs Net Shot based on movement variance
        # Net shot has very low variance. Lift has swing.
        if y_variance < 0.005: # Tighter threshold for normalized variance
            return "net_shot"
        else:
            return "lift"

    def _detect_hit_phase(self, history: List[Dict]) -> Tuple[int, int, int]:
        """
        Detect the swing phase based on wrist velocity.
        Returns (start_idx, end_idx, peak_idx)
        """
        velocities = []
        for i in range(1, len(history)):
            # Simple 2D distance for velocity
            curr = history[i]['right_wrist']
            prev = history[i-1]['right_wrist']
            dist = np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
            velocities.append(dist)
        
        if not velocities:
            return 0, len(history)-1, 0
            
        # Find peak velocity
        peak_idx = int(np.argmax(velocities) + 1) # +1 because velocities is 1 shorter
        
        # Define window (e.g., +/- 15 frames)
        window_size = 15
        start_idx = int(max(0, peak_idx - window_size))
        end_idx = int(min(len(history) - 1, peak_idx + window_size))
        
        return start_idx, end_idx, peak_idx

    def _calculate_real_metrics(self, history: List[Dict], action: str, hit_window: Tuple[int, int, int], fps: float) -> Dict[str, float]:
        start, end, peak = hit_window
        window_data = history[start:end+1]
        
        # Base body height for normalization (Nose to Ankle)
        # Calculate average body height in the clip to be robust
        body_heights = []
        for frame in window_data:
            nose = frame['nose'].y
            ankle = (frame['right_ankle'].y + frame['left_ankle'].y) / 2
            h = abs(ankle - nose)
            if h > 0.1: body_heights.append(h)
        
        avg_body_height = float(np.mean(body_heights)) if body_heights else 0.5
        
        metrics = {}
        
        # --- Common Metrics ---
        # 1. Contact Height (Normalized 0-1)
        metrics['contact_height'] = self._calc_contact_height(history, peak, avg_body_height)
        
        # --- Action Specific Metrics ---
        if action == 'smash' or action == 'clear':
            metrics['swing_amplitude'] = self._calc_swing_amplitude(window_data, avg_body_height)
            metrics['coordination'] = self._calc_coordination(window_data)
            metrics['downward_velocity'] = self._calc_downward_velocity(history, start, end, avg_body_height, fps)
            metrics['timing'] = self._calc_timing(history, peak, avg_body_height)
            
            # Fill others with reasonable defaults if missing
            metrics['direction_stability'] = 0.6 
            metrics['stability'] = 0.6

        elif action == 'drop':
            metrics['swing_amplitude'] = self._calc_swing_amplitude(window_data, avg_body_height)
            metrics['stability'] = self._calc_stability(window_data, avg_body_height)
            # For drop, downward velocity should be controlled (not too high, not too low)
            # But let's reuse the calculator and interpret it differently in rules
            metrics['downward_velocity'] = self._calc_downward_velocity(history, start, end, avg_body_height, fps)
            metrics['timing'] = self._calc_timing(history, peak, avg_body_height)
            
        elif action == 'lift':
            metrics['estimated_shuttle_height'] = self._calc_estimated_shuttle_height(history, peak, avg_body_height)
            metrics['simplicity'] = self._calc_simplicity(window_data, avg_body_height)
            metrics['stability'] = self._calc_stability(window_data, avg_body_height)
            metrics['contact_height_variance'] = 0.3 # Not applicable for single shot
            
        elif action == 'net_shot':
            metrics['net_tightness_proxy'] = self._calc_net_tightness(window_data, avg_body_height)
            metrics['swing_speed_low'] = self._calc_swing_speed_low(history, start, end, avg_body_height)
            metrics['simplicity'] = self._calc_simplicity(window_data, avg_body_height)
            
        # Fallback for any missing keys to avoid crashes
        defaults = {
            "swing_amplitude": 0.5, "coordination": 0.5, "timing": 0.5,
            "downward_velocity": 0.5, "direction_stability": 0.5, "stability": 0.5,
            "estimated_shuttle_height": 0.5, "simplicity": 0.5,
            "contact_height_variance": 0.5, "swing_speed_low": 0.5,
            "net_tightness_proxy": 0.5
        }
        for k, v in defaults.items():
            if k not in metrics:
                metrics[k] = v
                
        return metrics

    # --- Individual Metric Algorithms ---

    def _calc_contact_height(self, history: List[Dict], peak_idx: int, body_height: float) -> float:
        # Search for highest wrist point near peak velocity (contact point)
        # Search window: peak - 5 to peak + 5
        start = max(0, peak_idx - 5)
        end = min(len(history), peak_idx + 5)
        
        min_wrist_y = 1.0 # 1.0 is bottom
        
        for i in range(start, end):
            frame = history[i]
            # Use higher wrist
            wrist_y = min(frame['right_wrist'].y, frame['left_wrist'].y)
            if wrist_y < min_wrist_y:
                min_wrist_y = wrist_y
                
        nose_y = history[peak_idx]['nose'].y
        
        # Higher than nose?
        # delta negative means wrist is above nose (since y=0 at top)
        # We want score: higher is better
        # Distance above nose
        dist_above_nose = nose_y - min_wrist_y
        
        # Normalize by body height
        # 0.5 body height above nose is great (approx arm length)
        ratio = dist_above_nose / body_height
        
        # Map: -0.1 (below nose) -> 0.0, 0.4 (high) -> 1.0
        score = (ratio + 0.1) / 0.5
        return float(np.clip(score, 0.0, 1.0))

    def _calc_swing_amplitude(self, window_data: List[Dict], body_height: float) -> float:
        # Measure total travel distance of wrist relative to body height
        total_dist = 0
        for i in range(1, len(window_data)):
            curr = window_data[i]['right_wrist']
            prev = window_data[i-1]['right_wrist']
            total_dist += np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
            
        # Normalize
        # A full smash swing might travel 2-3 body heights?
        ratio = total_dist / body_height
        
        # Map 1.0 -> 0.2, 4.0 -> 1.0
        score = (ratio - 1.0) / 3.0
        return float(np.clip(score, 0.0, 1.0))

    def _calc_coordination(self, window_data: List[Dict]) -> float:
        # Measure Shoulder Rotation Range (Z-axis proxy)
        # Width of shoulders projected on 2D plane changes as they rotate
        # Max Width = Facing camera, Min Width = Side to camera
        
        widths = []
        for frame in window_data:
            rw = frame['right_shoulder']
            lw = frame['left_shoulder']
            width = np.sqrt((rw.x - lw.x)**2 + (rw.y - lw.y)**2)
            widths.append(width)
            
        if not widths: return 0.5
        
        max_w = max(widths)
        min_w = min(widths)
        
        # Rotation Ratio: 1 - (min/max)
        # If min approx max, no rotation -> 0
        # If min << max, high rotation -> 1
        rotation_score = 1.0 - (min_w / (max_w + 0.001))
        
        # Map 0.1 -> 0.0, 0.5 -> 1.0
        score = (rotation_score - 0.1) / 0.4
        return float(np.clip(score, 0.0, 1.0))

    def _calc_downward_velocity(self, history: List[Dict], start: int, end: int, body_height: float, fps: float) -> float:
        # Max positive Y velocity (downward)
        max_vel = 0
        for i in range(start, end):
            curr = history[i+1]['right_wrist'].y
            prev = history[i]['right_wrist'].y
            vel = (curr - prev) * fps # Units per second
            
            if vel > max_vel:
                max_vel = vel
                
        # Normalize relative to body height
        # E.g., 5 body heights per second is fast
        vel_norm = max_vel / body_height
        
        # Map 2.0 -> 0.0, 8.0 -> 1.0
        score = (vel_norm - 2.0) / 6.0
        return float(np.clip(score, 0.0, 1.0))

    def _calc_timing(self, history: List[Dict], peak_idx: int, body_height: float) -> float:
        # Compare index of max height vs index of peak velocity
        # Ideally they should be close (Hit at max extension and max speed)
        
        # Find index of max height in window
        window_size = 15 # Increased search window to catch earlier preparations
        s = int(max(0, peak_idx - window_size))
        e = int(min(len(history), peak_idx + window_size))
        
        min_wrist_y = 1.0
        max_height_idx = peak_idx
        
        for i in range(s, e):
            y = history[i]['right_wrist'].y
            if y < min_wrist_y:
                min_wrist_y = y
                max_height_idx = i
                
        diff = abs(max_height_idx - peak_idx)
        
        # Relaxed tolerance: 12 frames (approx 0.4s at 30fps)
        # Allows for natural follow-through lag
        score = 1.0 - (diff / 12.0)
        return float(np.clip(score, 0.0, 1.0))

    def _calc_estimated_shuttle_height(self, history: List[Dict], peak_idx: int, body_height: float) -> float:
        # For lift, "shuttle height" goal is high.
        # We assume follow-through height indicates lift height.
        # Look at end of window
        end_idx = min(len(history)-1, peak_idx + 10)
        wrist_y = history[end_idx]['right_wrist'].y
        nose_y = history[end_idx]['nose'].y
        
        # Higher is better (lower y)
        dist_above_nose = nose_y - wrist_y
        ratio = dist_above_nose / body_height
        
        # Map -0.2 -> 0.0, 0.3 -> 1.0
        score = (ratio + 0.2) / 0.5
        return float(np.clip(score, 0.0, 1.0))

    def _calc_simplicity(self, window_data: List[Dict], body_height: float) -> float:
        # Ratio of Displacement / Total Distance
        # 1.0 = Straight line (Simple)
        
        start_pt = window_data[0]['right_wrist']
        end_pt = window_data[-1]['right_wrist']
        
        displacement = np.sqrt((end_pt.x - start_pt.x)**2 + (end_pt.y - start_pt.y)**2)
        
        total_dist = 0
        for i in range(1, len(window_data)):
            curr = window_data[i]['right_wrist']
            prev = window_data[i-1]['right_wrist']
            total_dist += np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
            
        if total_dist == 0: return 1.0
        
        ratio = displacement / total_dist
        # Direct map 0-1
        return float(ratio)

    def _calc_stability(self, window_data: List[Dict], body_height: float) -> float:
        # Variance of nose position
        nose_xs = [f['nose'].x for f in window_data]
        nose_ys = [f['nose'].y for f in window_data]
        
        var = np.var(nose_xs) + np.var(nose_ys)
        std = np.sqrt(var)
        
        # Normalize by body height
        # std 0.0 -> 1.0 (stable), std 0.1 -> 0.0 (unstable)
        norm_std = std / body_height
        
        score = 1.0 - (norm_std / 0.1)
        return float(np.clip(score, 0.0, 1.0))

    def _calc_net_tightness(self, window_data: List[Dict], body_height: float) -> float:
        # Proxy: Elbow stability (movement of elbow relative to shoulder)
        # For net shot, elbow should be relatively stable
        dists = []
        for f in window_data:
            e = f['right_elbow']
            s = f['right_shoulder']
            d = np.sqrt((e.x - s.x)**2 + (e.y - s.y)**2)
            dists.append(d)
            
        var = np.var(dists)
        std = np.sqrt(var)
        
        norm_std = std / body_height
        # Lower is better
        score = 1.0 - (norm_std / 0.05)
        return float(np.clip(score, 0.0, 1.0))

    def _calc_swing_speed_low(self, history: List[Dict], start: int, end: int, body_height: float) -> float:
        # For net shot, we want LOW speed.
        # Calculate max speed in window
        max_dist = 0
        for i in range(start, end):
            curr = history[i+1]['right_wrist']
            prev = history[i]['right_wrist']
            dist = np.sqrt((curr.x - prev.x)**2 + (curr.y - prev.y)**2)
            if dist > max_dist: max_dist = dist
            
        speed = max_dist / body_height
        
        # If speed is high (> 0.1 per frame), score is low
        # If speed is low (< 0.02), score is high
        
        score = 1.0 - (speed - 0.02) / 0.08
        return float(np.clip(score, 0.0, 1.0))

    def _generate_keyframe(self, video_path: str, frame_idx: int, landmarks: Dict) -> Optional[str]:
        try:
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            success, image = cap.read()
            cap.release()
            
            if not success:
                return None
                
            h, w, _ = image.shape
            color = (0, 255, 255) # Yellow
            thickness = 2
            radius = 5
            
            pts = {}
            # Map landmarks to pixel coords
            for name, lm in landmarks.items():
                px = int(lm.x * w)
                py = int(lm.y * h)
                pts[name] = (px, py)
                cv2.circle(image, (px, py), radius, (0, 0, 255), -1) 
                
            # Draw Connections
            connections = [
                ('right_shoulder', 'left_shoulder'),
                ('right_shoulder', 'right_elbow'), ('right_elbow', 'right_wrist'),
                ('left_shoulder', 'left_elbow'), ('left_elbow', 'left_wrist'),
                ('right_shoulder', 'right_hip'), ('left_shoulder', 'left_hip'),
                ('right_hip', 'left_hip')
            ]
            
            for start, end in connections:
                if start in pts and end in pts:
                    cv2.line(image, pts[start], pts[end], color, thickness)
                
            # Encode
            _, buffer = cv2.imencode('.jpg', image)
            b64_str = base64.b64encode(buffer.tobytes()).decode('utf-8')
            return f"data:image/jpeg;base64,{b64_str}"
            
        except Exception as e:
            logger.error(f"Keyframe generation failed: {e}")
            return None
