# Keypoint Metrics Definition

本文件定义所有可计算的原子指标，用于动作评分与问题判断。

## 通用前提
- 关键点来源：MediaPipe Pose
- 默认击球手：右手
- 所有指标归一化到 [0, 1]

---

## 1. contact_height
击球点相对身体高度

公式：
(shoulder_y - wrist_y) / body_height

意义：
数值越大，击球点越高

---

## 2. timing
击球时机相对最高点的帧差

公式：
contact_frame - wrist_peak_frame

越接近 0 表示越接近最佳击球时机

---

## 3. swing_amplitude
挥拍幅度

计算：
击球前 N 帧内 wrist 与 shoulder 的最大距离

---

## 4. swing_speed
挥拍最大速度

计算：
wrist 关键点的最大位移速度

---

## 5. coordination
身体协调性（复合指标）

组成：
- 肩部旋转角度变化
- 髋部旋转角度变化
- 膝关节伸展幅度

---

## 6. stability
身体稳定性

计算：
击球前后 hip_center 的位置方差

---

## 7. simplicity
动作简洁性

计算：
wrist / elbow / shoulder 的轨迹路径总长度

越小表示越简洁（结果取反归一化）

---

## 8. net_tightness_proxy
放网贴网程度（近似）

定义：
contact_height 高 + swing_speed 低
