# 🚦 ASTRA: AI-Powered Traffic Intelligence Platform

ASTRA is an advanced, AI-driven traffic management and incident response platform designed to predict, manage, and mitigate urban gridlock. 

Built with a fast, modern tech stack, ASTRA leverages Machine Learning to predict the severity, duration, and cascading effects of traffic incidents, and utilizes a robust Rule Engine to instantly generate optimal deployment strategies for ground units.

## ✨ Key Features
- **🔮 Predictive Intelligence**: Input event details (like an accident or VIP movement) and our ML models instantly calculate a Risk Score (0-100), predicting the incident's impact on city-wide corridor stress.
- **🧠 SHAP Explainability**: The platform doesn't just give you a number. It uses live SHAP (SHapley Additive exPlanations) values to tell you exactly *why* an event is high risk (e.g. Peak Hour + Road Closure).
- **🤖 Automated Deployment Rule Engine**: A bespoke backend rule engine automatically processes the AI risk score and calculates exactly how many officers, barricades, and diversions are needed (Strategy A vs B vs C).
- **📊 Real-time Dashboard**: Monitor active KPIs, average resolution times, and the current stress levels of major city corridors.

## 🛠️ Tech Stack
- **Frontend**: React, TypeScript, TailwindCSS, Recharts
- **Backend**: FastAPI (Python), SQLAlchemy, PostgreSQL
- **AI/ML Engine**: Scikit-Learn, SHAP, Pandas
- **Infrastructure**: Docker & Docker Compose

---

## 🚀 How to Run Locally

### Prerequisites
- Make sure **Docker Desktop** is installed and running on your machine.
- Ensure ports `5173` (Frontend), `8000` (Backend API), and `5432` (PostgreSQL Database) are available.

### Quick Start (Windows)
1. Extract or clone the project folder.
2. Double-click the **`Start ASTRA`** shortcut (or the `Start_ASTRA.bat` script) located in the main folder.
3. This script will automatically build the Docker containers, initialize the ML models, and open the ASTRA Dashboard in your default web browser (`http://localhost:5173`).
4. *Note: To stop the environment later, simply double-click the `Stop_ASTRA.bat` file.*

### Quick Start (Mac / Linux / Manual Method)
1. Open a terminal in the project root directory.
2. Run the following command to build and launch the platform:
   ```bash
   docker-compose up --build -d
   ```
3. Wait about 10-15 seconds for the database and backend AI models to fully initialize.
4. Open your web browser and navigate to: `http://localhost:5173`
5. *Note: To stop the environment later, run `docker-compose down` in the terminal.*

## 🧪 Testing the Platform
1. **Dashboard**: View the real-time active metrics and high-risk events overview.
2. **Event Prediction**: Navigate to the "Event Prediction" tab, fill out a mock incident (e.g., an Accident requiring Road Closure on Bellary Road), and click **Generate Intelligence**. 
3. **Recommendations**: Watch the ML models generate a live Risk Score and the backend Rule Engine automatically construct dynamic deployment strategies (A/B/C) based on the severity and time of the incident!
