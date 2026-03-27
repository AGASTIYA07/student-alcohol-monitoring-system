# 🛡️ Intelligent Student Alcohol Monitoring, Risk Prediction, and Recovery System

Traditional alcohol detection systems provide only one-time outputs and fail to track behavioral patterns or support long-term recovery. 

This project aims to build an intelligent, behavior-aware system that not only detects alcohol consumption but also tracks behavioral patterns over time, identifies habit-forming consumption, and provides personalized recovery support.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web_App-lightgrey?style=for-the-badge&logo=flask)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=for-the-badge&logo=javascript)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=for-the-badge&logo=sqlite)

---

## ✨ Core Features
- **🌡️ Automated Alcohol Input**: Integrates with physical MQ-3 hardware sensors via PySerial, with built-in intelligent simulated fallbacks for software-only deployments.
- **📊 Behavior Pattern Analysis**: Recursively analyzes a student's last 7 entries to categorize risk vs. safety reliably.
- **🔍 Early-Addiction Detection**: The innovative Consistency Engine flags habit-forming behavior even if the readings are low-level (e.g., 5 out of 7 days showing low alcohol levels will trigger warnings).
- **📉 Dynamic Risk Scoring**: Calculates a normalized 0-100 risk score factoring in high-usage, frequencies, and violations (e.g., consuming during strict class hours).
- **📈 Real-Time Charts & UI**: Features a beautiful dark-mode glassmorphic dashboard powered by `Chart.js` for instant visualization of student histories.
- **🗣️ Voice Feedback Alerts**: Natively utilizes the Web `SpeechSynthesis` API to verbally communicate AI-driven suggestions and warnings to students seamlessly.
- **⏳ Escalation Tracking System**: Intelligent backend tracks mandatory counseling flags and faculty warnings across severe repeat offenses.
- **🎓 Dedicated Faculty Dashboard**: An aggregated sortable view measuring all student risks, recovery streaks, and avoidance flags centrally.

## 🚀 Live Demo
You can view the live project deployed via Render here:
👉 **[Student Alcohol Monitoring System](https://student-alcohol-monitoring-system.onrender.com/)**

## 💻 Technical Stack
* **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), JavaScript (Fetch APIs), Chart.js
* **Backend**: Python 3, Flask, PySerial, Gunicorn (WSGI)
* **Database**: SQLite
* **Deployment**: Render Infrastructure-as-Code (`render.yaml`)

## 🛠️ Local Installation
If you want to run this application locally on your laptop:

1. Clone this repository:
```bash
git clone https://github.com/AGASTIYA07/student-alcohol-monitoring-system.git
cd student-alcohol-monitoring-system
```
2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```
4. Start the Application:
```bash
python3 app.py
```
Visit `http://127.0.0.1:5000` in your web browser.

---

## 👥 Contributors
- **[Your Name]** - *Lead Developer* - [@YourGitHubUser](https://github.com/YourGitHubUser)
- **[Contributor 2 Name]** - *Role/Contribution* - [@ContributorGitHub](https://github.com/ContributorGitHub)
- **[Contributor 3 Name]** - *Role/Contribution* - [@ContributorGitHub](https://github.com/ContributorGitHub)

---
*Developed as an academic prototype for behavior-aware student wellbeing and monitoring.*
