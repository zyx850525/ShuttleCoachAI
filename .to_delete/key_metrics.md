太好了，这一步是**从“懂羽毛球”走向“真的能算”**的关键一步 👍
下面我会**严格站在工程可实现角度**，把你刚才认可的教学维度：

> 👉 **全部转化为「可计算的关键点指标」**
> 👉 **统一成一份可直接用于 AI Engine 的配置文件**

我会分 3 层来做，保证你一看就能写代码：

---

# 一、统一建模前提（所有动作通用）

## 1️⃣ 关键点来源（假设）

基于 **MediaPipe Pose**（或等价）：

常用关键点（示例）：

* 肩：`left_shoulder / right_shoulder`
* 肘：`left_elbow / right_elbow`
* 手腕：`left_wrist / right_wrist`
* 髋：`left_hip / right_hip`
* 膝：`left_knee / right_knee`
* 脚踝：`left_ankle / right_ankle`

击球手侧 = dominant side（MVP 可假设右手）

---

## 2️⃣ 通用可计算指标（原子能力）

> 下面这些是 **所有动作维度的“积木”**

### A. 击球点高度（Contact Height）

```text
contact_height =
    wrist_y_at_contact
    relative to body_height
```

计算方式：

* `body_height = shoulder_y - ankle_y`
* `normalized_height = (shoulder_y - wrist_y) / body_height`

---

### B. 击球时机（Contact Timing）

```text
timing =
    wrist_y_peak_time
    vs
    actual_contact_time
```

* 在上升期 / 顶点 / 下降期
* 用 `Δt = contact_frame - peak_frame`

---

### C. 挥拍幅度（Swing Amplitude）

```text
swing_amplitude =
    max(wrist_distance_from_shoulder)
```

* 计算击球前 N 帧内
* 欧氏距离

---

### D. 挥拍速度（Swing Speed）

```text
swing_speed =
    max(Δ wrist_position / Δ time)
```

---

### E. 身体协调（Body Coordination）

```text
coordination =
    hip_rotation + shoulder_rotation + knee_extension
```

简化实现：

* 肩线角度变化
* 髋线角度变化
* 下肢是否有明显伸展

---

### F. 身体稳定性（Body Stability）

```text
stability =
    center_of_mass_variance
```

* 髋部关键点的横向 / 纵向抖动
* 击球前后 N 帧

---

### G. 动作简洁性（Motion Simplicity）

```text
simplicity =
    total_joint_path_length
```

* 手腕 / 肘 / 肩轨迹越短越好（特定动作）

---

### H. 网前贴网程度（Net Tightness｜简化）

```text
net_tightness ≈
    contact_height_high
    + wrist_speed_low
```

> MVP 不算真实球网，只算「高点 + 轻触」

---

# 二、动作 → 维度 → 可计算指标映射

下面是**最关键部分**。

---

## 🟦 1️⃣ 杀球（Smash）

### 教学目标

高点 + 完整发力 + 向下压制

### 维度 → 指标

| 维度    | 可计算指标                     |
| ----- | ------------------------- |
| 击球点高度 | `contact_height`          |
| 挥拍完整度 | `swing_amplitude`         |
| 身体协调  | `coordination`            |
| 击球节奏  | `timing`                  |
| 下压趋势  | `wrist_velocity_vector.y` |

---

## 🟩 2️⃣ 高远球（Clear）

### 教学目标

稳定送到后场，动作舒展

| 维度    | 可计算指标                              |
| ----- | ---------------------------------- |
| 击球点高度 | `contact_height`                   |
| 动作舒展度 | `swing_amplitude`                  |
| 方向稳定  | `wrist_velocity_vector.x variance` |
| 身体平衡  | `stability`                        |
| 节奏    | `timing`                           |

---

## 🟨 3️⃣ 挑球（Lift）

### 教学目标

中前场被动下稳定送高

| 维度     | 可计算指标                        |
| ------ | ---------------------------- |
| 击球点稳定性 | `contact_height variance`    |
| 出球高度   | `estimated_shuttle_apex`（近似） |
| 动作简洁性  | `simplicity`                 |
| 身体稳定   | `stability`                  |

> ❗ 不使用：挥拍幅度 / 爆发速度

---

## 🟪 4️⃣ 放网（Net Shot）

### 教学目标

抢高点 + 轻控制

| 维度    | 可计算指标                        |
| ----- | ---------------------------- |
| 击球点高度 | `contact_height`             |
| 手腕控制  | `swing_speed (low)`          |
| 动作克制  | `simplicity`                 |
| 贴网程度  | `contact_height + low_speed` |

---

# 三、✅【最终统一动作配置文件（完整版）】

> **你可以直接保存为：`action_scoring_config.json`**

```json
{
  "global_metrics": {
    "contact_height": {
      "type": "normalized",
      "formula": "(shoulder_y - wrist_y) / body_height"
    },
    "timing": {
      "type": "delta_frames",
      "description": "contact_frame - wrist_peak_frame"
    },
    "swing_amplitude": {
      "type": "distance",
      "points": ["wrist", "shoulder"]
    },
    "swing_speed": {
      "type": "max_velocity",
      "point": "wrist"
    },
    "coordination": {
      "type": "composite",
      "components": ["hip_rotation", "shoulder_rotation", "knee_extension"]
    },
    "stability": {
      "type": "variance",
      "point": "hip_center"
    },
    "simplicity": {
      "type": "path_length",
      "points": ["wrist", "elbow", "shoulder"]
    }
  },
  "actions": {
    "smash": {
      "metrics": {
        "contact_height": 0.30,
        "swing_amplitude": 0.25,
        "coordination": 0.20,
        "timing": 0.15,
        "downward_velocity": 0.10
      }
    },
    "clear": {
      "metrics": {
        "contact_height": 0.25,
        "swing_amplitude": 0.25,
        "direction_stability": 0.20,
        "stability": 0.20,
        "timing": 0.10
      }
    },
    "lift": {
      "metrics": {
        "contact_height_variance": 0.30,
        "estimated_shuttle_height": 0.30,
        "simplicity": 0.20,
        "stability": 0.20
      }
    },
    "net_shot": {
      "metrics": {
        "contact_height": 0.35,
        "swing_speed_low": 0.25,
        "simplicity": 0.20,
        "net_tightness_proxy": 0.20
      }
    }
  }
}
```

---

## 🧠 你现在已经做到哪一步了（非常关键）

你已经完成了：

✅ 教学动作拆解
✅ 维度合理性校正
✅ 可计算指标建模
✅ 统一配置抽象

**下一步就是纯工程问题了**。

---

## 下一步我可以直接继续的方向（任选）

1. 🔢 帮你写 **Python 评分函数（读这个 JSON）**
2. 🎯 定义「新手 / 中级」的 **指标阈值区间**
3. 🤖 生成「问题标签判定逻辑」
4. 🧩 把这套配置接入你现有 PRD 的 AI Engine 章节

你选一个，我继续陪你把 ShuttleCoach AI 真正跑起来。
