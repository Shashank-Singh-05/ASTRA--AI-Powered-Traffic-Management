<div align="center">
  <img src="traffic_light.ico" alt="ASTRA Logo" width="120" />
  <h1>🚦 ASTRA</h1>
  <p><strong>AI-Powered Traffic Intelligence & Incident Management Platform</strong></p>
</div>

<br />

ASTRA is an advanced, enterprise-grade traffic management and incident response platform designed to predict, manage, and mitigate urban gridlock before it cascades. 

Built with a modern, high-performance tech stack, ASTRA leverages custom Machine Learning models to instantly predict the severity and duration of traffic incidents, while a bespoke backend Rule Engine dynamically generates precise, resource-optimized deployment strategies for ground units.

---

## Comprehensive Feature List

### 1. Predictive Intelligence Engine
Gone are the days of guessing the impact of a crash. When a new incident occurs, operators input the details (Event Cause, Priority, Location, Road Closure Needs), and ASTRA's Machine Learning models instantly calculate:
- **Risk Score (0-100):** A quantifiable metric predicting the incident's impact on city-wide corridor stress.
- **Estimated Resolution Time:** Model-driven predictions on how long it will take to clear the incident based on historical data and current conditions.

### 2. Explainable AI (XAI) & SHAP
The platform doesn't just give you a black-box number. ASTRA features an integrated **Feature Contribution Chart** powered by **SHAP** (SHapley Additive exPlanations). 
- It visually breaks down *exactly why* an event is deemed high risk (e.g., showing that "Peak Hour" and "Road Closure" contributed 60% of the risk score). 
- Generates dynamic, plain-English rationales explaining the AI's logic so human commanders can trust the intelligence.

### 3. Automated Deployment Rule Engine
Once the ML model predicts the severity, ASTRA's Python-based Rule Engine takes over to recommend actionable ground strategies. It calculates exactly what the response should be, generating distinct strategies (e.g., Aggressive Intervention vs. Balanced Approach) and recommending:
- Exact number of Traffic Officers to deploy.
- Exact number of physical Barricades required.
- Whether a full traffic diversion is necessary.

### 4. Real-Time Operations Dashboard
A beautifully designed, centralized command center for traffic authorities.
- **Live KPIs:** Track Total Active Events, Critical Risk Events, Total Officers Deployed, and Average Resolution Times.
- **Active Incident Tracker:** A real-time grid of all ongoing incidents, their severity, and their assigned response strategies.

### 5. AI Copilot
ASTRA includes a built-in AI Copilot tailored for traffic commanders. Operators can chat directly with the Copilot to get advice on handling specific anomalies, managing VIP movements, or interpreting complex traffic data.

### 6. Historical Event Tracking
A dedicated history log that permanently records all resolved events. Authorities can review past incidents, the strategies used to resolve them, and their final resolution times, providing invaluable data for future urban planning and ML model retraining.

---

## Technical Architecture

ASTRA is built on a scalable, containerized microservices architecture:

- **Frontend:** React, TypeScript, TailwindCSS, Recharts, Lucide Icons, Vite
- **Backend API:** FastAPI (Python), Pydantic
- **Database:** PostgreSQL, SQLAlchemy (ORM)
- **AI/ML Pipeline:** Scikit-Learn (Joblib models), Pandas, Numpy, SHAP
- **Infrastructure:** Fully containerized using Docker & Docker Compose

---

## How to Run Locally

### Prerequisites
- Make sure **Docker Desktop** is installed and running on your machine.
- Ensure ports 5173 (Frontend), 8000 (Backend API), and 5432 (PostgreSQL Database) are available.

### Quick Start (Windows)
1. Extract or clone the project folder.
2. Double-click the **Start ASTRA** shortcut (or the `Start_ASTRA.bat` script) located in the main folder.
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

---

## Testing the Platform
1. **Explore the Dashboard:** View the real-time active metrics and high-risk events overview.
2. **Generate Intelligence:** Navigate to the "Event Prediction" tab, fill out a mock incident (e.g., an Accident requiring Road Closure on Bellary Road), and click **Generate Intelligence**. 
3. **Review Recommendations:** Watch the ML models generate a live Risk Score, view the SHAP logic, and let the backend Rule Engine automatically construct dynamic deployment strategies!
4. **Resolve Events:** Mark events as resolved and watch them seamlessly move into your History log.
