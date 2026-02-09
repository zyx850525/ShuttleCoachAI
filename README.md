# 🏸 ShuttleCoach AI

> **Your Personal AI Badminton Coach**  
> _Powered by Gemini 3 & MediaPipe_

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini API](https://img.shields.io/badge/AI-Gemini%203-blue)](https://deepmind.google/technologies/gemini/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)

[中文文档](./README_zh.md) | [Live Demo](https://youtu.be/RRDhoylC7d4)

---

## 📖 Introduction

**ShuttleCoach AI** is an intelligent application designed for badminton enthusiasts (beginners to intermediates). It uses advanced computer vision and LLM technologies to analyze your badminton training videos, providing objective scoring, technical diagnosis, and actionable improvement suggestions.

Unlike traditional tools that only provide data, ShuttleCoach AI acts like a real coach, offering detailed feedback and interactive guidance.

## 🚀 Why Gemini 3?

ShuttleCoach AI leverages the cutting-edge capabilities of **Gemini 3** to move beyond simple data plotting and provide a truly human-like coaching experience.

1.  **Deep Multimodal Understanding**: Unlike basic CV models, Gemini 3 analyzes the **temporal sequence** of the action. By processing frames from Preparation, Hit Point, and Follow-through simultaneously, it understands the biomechanical "flow" and can pinpoint exactly where energy is lost in the swing.
2.  **Complex Reasoning & Comparison**: Gemini 3 combines raw keypoint metrics with its vast knowledge of badminton techniques to provide **Standard vs. Actual** comparisons. It doesn't just say "hit higher"; it explains *why* your specific arm angle is limiting your power compared to a pro stance.
3.  **Context-Aware Interactive Coaching**: Through the **Interactive AI Coach**, Gemini 3 maintains a session context of your current performance. It can handle nuanced follow-up questions, providing drills that are specifically tailored to the flaws detected in your latest video.
4.  **Actionable Feedback Synthesis**: It transforms cold biomechanical data into objective, rational, yet encouraging "coach-speak," ensuring every piece of advice is immediately actionable for the student's next session.

## ✨ Key Features

*   **🎬 Automated Action Recognition**: Automatically detects and classifies actions like Smash, Clear, Lift, and Net Shot using MediaPipe Pose.
*   **📊 Sequence Analysis (Powered by Gemini 3)**: Analyzes the full action flow: **Preparation -> Hit Point -> Follow-through**, identifying issues in the entire motion chain using multimodal vision.
*   **🤖 Interactive AI Coach (Powered by Gemini 3)**: A personalized chat experience. Ask questions like "Why is my smash weak?" and get data-backed corrections in real-time.
*   **📈 Growth Profile**: Track your progress over time with historical score trends and detailed records.
*   **🖼️ Social Sharing**: Generate beautiful, shareable result cards with one click to showcase your training achievements.
*   **📱 Mobile First**: Fully responsive design for seamless use on mobile devices at the court.

## 🛠️ Technology Stack

### Frontend
*   **Framework**: React (Vite)
*   **Charts**: Chart.js (Radar & Line charts)
*   **Styling**: CSS Modules, Responsive Design
*   **Tools**: html2canvas (Sharing)

### Backend
*   **Framework**: FastAPI (Python)
*   **CV Engine**: MediaPipe Pose (Keypoint Extraction), OpenCV
*   **AI Engine**: Google Gemini 3 API (Multimodal Analysis)
*   **Database**: SQLite (Lightweight task storage)

## 🚀 Getting Started

### Prerequisites
*   Node.js (v16+)
*   Python (v3.9+)
*   A Google Gemini API Key

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/zyx850525/ShuttleCoachAI.git
    cd ShuttleCoachAI
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```env
    GEMINI_API_KEY=your_api_key_here
    # GEMINI_PROXY=http://127.0.0.1:7890 (Optional)
    ```

4.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    ```

### Running the App

1.  **Start Backend**
    ```bash
    cd ShuttleCoachAI
    uvicorn backend.main:app --reload
    ```

2.  **Start Frontend**
    ```bash
    cd frontend && npm run dev
    ```

3.  Open `http://localhost:5173` in your browser.

## 📸 Screenshots

### 1. Home & Video Upload
The clean and intuitive home screen where users can upload their badminton training videos.
![Home](./screenshots/home.png)

### 2. Ready to Analyze
After the video is uploaded, the system performs a quick quality check and prepares for deep biomechanical analysis.
![Ready to Analyze](./screenshots/ready_to_analysis.png)

### 3. Analysis in Progress
The AI engine (MediaPipe + Gemini 3) works in real-time to analyze the motion chain and calculate metrics.
![Analysis in Progress](./screenshots/analysis.png)

### 4. Detailed Analysis Result
The core value page showing scores, radar charts of metrics, and identified technical issues.
![Analysis Result](./screenshots/result.png)

### 5. Interactive AI Coach (Gemini 3)
Chat with your personal AI coach to get deeper insights and personalized training advice based on your video.
![AI Coach Chat](./screenshots/chat.png)

### 6. Growth Profile
Track your performance history and visualize your progress over time.
![Growth Profile](./screenshots/profile.png)

### 7. Social Share Card
Generate a high-resolution analysis summary card to share with friends or on social media.
![Share Card](./screenshots/share_card.png)

## 🗺️ Roadmap (Future Enhancements)
*   **3D Action Reconstruction**: Move beyond 2D keypoints to full 3D skeletal trajectory analysis for higher precision.
*   **Perspective-Aware Scoring**: Implement specific classifiers to adjust scoring weights based on camera angles (e.g., side view for swing amplitude vs. rear view for direction).
*   **Full-Match Tactical Analysis**: Evolve from single-action analysis to whole-match tracking of footwork and tactical execution.
*   **Social & Community**: Build a leaderboard and challenge system to foster engagement within the global badminton community.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
