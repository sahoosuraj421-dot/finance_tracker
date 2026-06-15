# FinTrack — Personal Finance Tracker

A full-stack personal finance tracker with CSV/XLSX import, analytics dashboards, budget management, and an AI assistant powered by **Google Gemini** and **LangGraph**.

![FinTrack](https://img.shields.io/badge/React-18-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![LangGraph](https://img.shields.io/badge/LangGraph-AI-purple) ![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## Features

- **Dashboard** — Income, expenses, net balance, monthly trends, and category breakdown charts
- **Transactions** — View, filter, add, and delete transactions
- **File Upload** — Import bank statements from CSV or Excel (`.csv`, `.xlsx`, `.xls`)
- **Analytics** — Category spending, net balance trends, recurring expense detection
- **Budgets** — Set monthly limits per category with visual progress and alerts
- **AI Assistant** — LangGraph agent with Gemini that can query your data, set budgets, add transactions, and more

### AI Agent Tools

The chatbot has access to these automated tools:

| Tool | Description |
|------|-------------|
| `get_financial_summary` | Overall income, expenses, and top categories |
| `get_category_spending` | Spending breakdown by category |
| `find_recurring_expenses` | Detect subscriptions and recurring bills |
| `compare_two_months` | Month-over-month comparison |
| `check_budgets` | Budget status and overspending alerts |
| `set_budget` | Create or update category budgets |
| `get_recent_activity` | Latest transactions |
| `add_transaction` | Add a new transaction via chat |
| `search_transactions` | Search by description keyword |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Recharts, React Router |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI | LangGraph, LangChain, Google Gemini API |
| Data | Pandas, OpenPyXL |
| Deploy | Docker, Docker Compose, Nginx |

## Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [Python](https://www.python.org/) 3.11+
- [Gemini API Key](https://aistudio.google.com/apikey)

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/finance-tracker.git
cd finance-tracker
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Run with Docker (Recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Run Locally (Development)

**Backend:**

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Sample Data

A sample CSV is included at `sample-data/transactions.csv`. Upload it via the **Upload** page to populate the app with demo data.

### Supported File Formats

The parser auto-detects common column names:

| Field | Recognized Columns |
|-------|-------------------|
| Date | `date`, `transaction date`, `posted date` |
| Description | `description`, `memo`, `payee`, `merchant` |
| Amount | `amount`, `debit`/`credit` columns |
| Category | `category` (auto-detected from description if missing) |

## Project Structure

```
finance-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings & env vars
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # Database models
│   │   ├── routers/             # API endpoints
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── tools/               # LangGraph agent tools
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Route pages
│   │   └── services/            # API client
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── sample-data/                 # Demo CSV file
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/transactions` | List transactions |
| POST | `/api/transactions` | Create transaction |
| POST | `/api/transactions/upload` | Upload CSV/XLSX |
| GET | `/api/analytics/summary` | Financial summary |
| GET | `/api/analytics/categories` | Category breakdown |
| GET | `/api/analytics/recurring` | Recurring expenses |
| GET | `/api/analytics/budget-alerts` | Budget status |
| POST | `/api/analytics/budgets` | Set budget |
| POST | `/api/chat` | AI chat message |

Full interactive docs at `/docs` when the backend is running.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes (for chat) | — | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model name |
| `DATABASE_URL` | No | `sqlite:///./finance_tracker.db` | Database connection |
| `CORS_ORIGINS` | No | `http://localhost:5173,...` | Allowed CORS origins |

## Deploying to GitHub

1. Create a new repository on GitHub
2. Push this project:

```bash
git init
git add .
git commit -m "Initial commit: FinTrack finance tracker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/finance-tracker.git
git push -u origin main
```

3. **Never commit your `.env` file** — it is in `.gitignore`
4. For production, set `GEMINI_API_KEY` as a secret/environment variable on your hosting platform

## License

MIT License — feel free to use and modify for personal or commercial projects.
