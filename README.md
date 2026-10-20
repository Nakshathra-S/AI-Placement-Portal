# AI Placement Portal — AI-Based Placement Preparation Portal

An end-to-end, full-stack campus placement preparation web application built with **Python Flask**, **HTML5/CSS3/Vanilla JavaScript**, **MySQL**, and **Google Gemini API**.

---

## 📸 Key Features & Visual Replication

Recreated with pixel-precise visual fidelity to the original design:

1. **Candidate Authentication & Registration**
   - Clean, modern login interface matching the original desktop layout.
   - Form validation, secure password hashing using Werkzeug, and server-side sessions.
   - Prevents duplicate accounts with dedicated error messages.

2. **Placement Preparation Dashboard**
   - Candidate welcome banner with dynamic user state.
   - Real-time diagnostic statistics: Total Attempts, Diagnostic Average Score, Best Score, and Placement Readiness Index.
   - Direct shortcuts to all 4 placement preparation modules.
   - Summary of recent diagnostic attempts.

3. **Technical Interview Practice**
   - Role selector supporting:
     - *Full Stack Developer*
     - *Python Developer*
     - *Java Developer*
     - *Data Analyst*
     - *AI/ML Engineer*
     - *Cyber Security Analyst*
   - Dynamic 5-question generation via Gemini AI.
   - Strict technical grading engine assessing conceptual accuracy, factual correctness, completeness, and clarity.
   - Word counter with penalty alerts for shallow answers (<20 words).
   - Detailed model answers, missing concepts breakdown, and specific improvement suggestions.

4. **HR Behavioral Interview Practice**
   - Module for common behavioral HR interview questions.
   - Real-time response length tracking.
   - Evaluated against the **STAR methodology** (Situation, Task, Action, Result) and professional tone.
   - Provides exemplary model responses and actionable communication tips.

5. **Group Discussion Practice**
   - Generates contemporary GD topics with background context across technology, society, and economy.
   - Multi-perspective evaluation analyzing relevance, argument quality, logical structure, supporting examples, and articulation.
   - Highlights missed counterarguments and offers a balanced model synthesis.

6. **English Communication & Grammar Checker**
   - Linguistic diagnostic analysis of written English paragraphs.
   - Calculates **Interview Score out of 10** with calibrated status badges (`POOR`, `FAIR`, `GOOD`, `EXCELLENT`).
   - Visual progress bar for **Placement Readiness Calibration**.
   - 5-category rubric card: *Clarity*, *Grammar*, *Sentence Structure*, *Tone*, and *Vocabulary*.
   - Line-by-line identified linguistic corrections with explanations and a polished professional model version.

7. **Previous Attempt History & Diagnostics**
   - Chronological list of past evaluations across all modules.
   - Color-coded diagnostic score badges (Green: 8–10, Yellow: 5–7, Red: 0–4).
   - Expandable accordion toggle: `▶ View AI Diagnostic Report & Score Breakdown`.
   - In-place secure record deletion with user confirmation.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System with Inter font), Vanilla JavaScript (ES6+ `fetch()` REST API communication).
- **Backend**: Python 3.10+ / Flask 3.0+.
- **Database**: MySQL 8.0+ (with automated SQLite fallback for immediate testing).
- **AI Integration**: Google Gemini API (`gemini-1.5-flash`).
- **Security**: Flask server-side session cookies, Werkzeug PBKDF2/SHA-256 password hashing, parameterized SQL queries against SQL injection.

---

## 📁 Project Directory Structure

```text
ai-placement-portal/
├── app.py                      # Flask Application entry point & factory
├── config.py                   # Environment configuration loader
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
├── .env                        # Local active environment configuration
├── README.md                   # Complete documentation & setup instructions
├── database/
│   ├── schema.sql              # MySQL DDL table schema script
│   └── db.py                   # Database connection pool & CRUD repository
├── services/
│   ├── gemini_service.py       # Google Gemini REST client & prompts
│   └── evaluation_service.py   # Rubric scoring engine & heuristics
├── routes/
│   ├── auth_routes.py          # /login, /register, /logout, /me
│   ├── dashboard_routes.py     # /dashboard, /dashboard/stats
│   ├── technical_routes.py     # /technical, /technical/generate, /technical/evaluate
│   ├── hr_routes.py            # /hr, /hr/questions, /hr/evaluate
│   ├── gd_routes.py            # /gd, /gd/generate-topic, /gd/evaluate
│   ├── english_routes.py       # /english, /english/analyze
│   └── history_routes.py       # /history, /history/data, DELETE /history/<id>
├── templates/
│   ├── base.html               # Shared layout & responsive navigation
│   ├── login.html              # Candidate Login (Screenshot 1)
│   ├── register.html           # Candidate Registration
│   ├── dashboard.html          # Candidate Dashboard & metrics
│   ├── technical.html          # Technical Practice (Screenshot 2)
│   ├── hr.html                 # HR Behavioral Practice (Screenshot 3)
│   ├── gd.html                 # Group Discussion Practice
│   ├── english.html            # English Grammar Checker (Screenshot 4)
│   └── history.html            # Attempt History (Screenshot 5)
├── static/
│   ├── css/
│   │   └── style.css           # Global design system & typography
│   └── js/
│       ├── auth.js             # Authentication async submission
│       ├── dashboard.js        # Live dashboard sync
│       ├── technical.js        # Technical module logic & word count
│       ├── hr.js               # HR question loading & evaluation
│       ├── gd.js               # Group discussion generation & scoring
│       ├── english.js          # Grammar checker & breakdown rendering
│       └── history.js          # Expandable history cards & deletion
└── tests/
    └── test_app.py             # Automated unit & integration tests
```

---

## 🚀 Setup & Installation Instructions

### 1. Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.13 installed.
- **MySQL Server** (Optional for testing, required for production MySQL mode).
- **Google Gemini API Key**: Free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Install Dependencies
In your terminal, navigate to the project directory and run:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables (`.env`)
Create or edit your `.env` file in the project root:

```ini
# Flask Configuration
SECRET_KEY=ai-placement-portal-super-secret-key-2026
FLASK_ENV=development
PORT=5000

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=ai_placement_portal

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

> **Note on Database Connection**:
> If MySQL credentials are not yet configured or the MySQL service is unreachable, the application automatically initializes a local SQLite database (`instance/ai_placement_portal.db`) so that you can run and test all features immediately without setup errors! Once you configure your MySQL password in `.env`, it will automatically use MySQL.

### 4. (Optional) Initialize MySQL Manually
If you want to manually run the SQL script in MySQL Workbench or the MySQL CLI:

```bash
mysql -u root -p < database/schema.sql
```

### 5. Run the Application
Start the Flask server:

```bash
python app.py
```

The application will be live at:
**http://127.0.0.1:5000**

---

## 🧪 Running the Automated Test Suite

A complete test suite is included in `tests/test_app.py`, verifying user registration, login, question generation, AI evaluation parsing, English rubric scoring, and history management:

```bash
python -m unittest tests/test_app.py -v
```

---

## 📡 REST API Documentation

### Authentication
- `POST /register`: Registers a new user. Body: `{ name, email, password, confirm_password }`
- `POST /login`: Authenticates a candidate. Body: `{ email, password }`
- `GET /logout`: Clears session and redirects to login.
- `GET /me`: Returns profile of the logged-in candidate.

### Dashboard
- `GET /dashboard/stats`: Returns JSON containing total attempts, average score, best score, and recent records.

### Technical Interview
- `POST /technical/generate`: Generates 5 role-specific questions. Body: `{ job_role }`
- `POST /technical/evaluate`: Strictly evaluates answer. Body: `{ job_role, question_number, question_text, submitted_answer }`
- `GET /technical/history`: Returns user's technical attempts.

### HR Behavioral Interview
- `GET /hr/questions`: Loads standard behavioral questions.
- `POST /hr/evaluate`: Evaluates candidate response using the STAR rubric. Body: `{ question_text, submitted_answer }`
- `GET /hr/history`: Returns user's HR attempts.

### Group Discussion
- `POST /gd/generate-topic`: Generates a contemporary GD topic with context.
- `POST /gd/evaluate`: Evaluates discussion arguments and counterarguments. Body: `{ topic, submitted_opinion }`
- `GET /gd/history`: Returns user's GD attempts.

### English Communication & Grammar
- `POST /english/analyze`: Analyzes text for clarity, grammar, structure, tone, and vocabulary. Body: `{ text }`
- `GET /english/history`: Returns user's English check records.

### History & Diagnostics
- `GET /history/data`: Returns unified chronological history of all user attempts.
- `DELETE /history/<module_type>/<attempt_id>`: Permanently deletes an attempt record belonging to the authenticated user.
