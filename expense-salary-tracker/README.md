# AD Tech Solution — Expense &amp; Salary Tracker

Simple admin-only dashboard to manage employees, salary, employee expenses (with receipt photos), and company wages — with month-wise totals and downloadable PDF reports/slips.

## What's inside

```
expense-salary-tracker/
├── app/                  ← FastAPI backend
│   ├── main.py
│   ├── models.py         ← database tables
│   ├── schemas.py        ← request/response validation
│   ├── database.py       ← SQLite connection
│   ├── core/auth.py      ← admin password check
│   └── routers/          ← employees, salary, employee-expenses, company-wages, summary, auth
├── frontend/
│   ├── index.html        ← the whole dashboard (single file, no build step)
│   └── assets/logo.png
├── requirements.txt
├── runtime.txt           ← pins Python version for Render
├── render.yaml           ← Render deploy blueprint
├── netlify.toml          ← Netlify deploy config
└── .gitignore
```

## Features

- **Login** — single admin password (`ADMIN_PASSWORD` env var), no employee accounts
- **Employees** — add/edit/delete
- **Salary** — month-wise, mark pending → paid with one click, download a PDF salary slip once paid
- **Employee Expenses** — month-wise reimbursements with an optional photo of the bill/receipt
- **Company Wages** — rent, bills, vendor payments, month-wise
- **Employee Profile** — pick an employee, see their complete salary + expense history in one place
- **Monthly Summary** — salary + employee expense + company wages combined, with a downloadable PDF report

---

## One-time setup: continuous deployment

Once this is set up, **every `git push` automatically redeploys both the backend (Render) and frontend (Netlify)** — no manual re-upload needed.

### 1. Push this code to GitHub
If you're working from this Codespace, it's likely already connected to a repo:
```bash
git add .
git commit -m "Initial deployment setup"
git push
```

### 2. Backend → Render (auto-deploys on every push)

1. Go to [render.com](https://render.com), sign up with GitHub
2. **New +** → **Blueprint** → select this repo
3. Render will detect `render.yaml` automatically and pre-fill everything (Python runtime, build/start commands, root directory)
4. It will ask you to set the `ADMIN_PASSWORD` env var (marked `sync: false` in the blueprint, so it's not stored in git) — set your own strong password here
5. Click **Apply** — first deploy takes 2-3 minutes

From now on, **any push to `main` auto-redeploys** the backend. No manual steps.

> If you'd rather not use the Blueprint flow, a plain **New Web Service** also works — just set Root Directory to `expense-salary-tracker`, Build Command to `pip install -r requirements.txt`, Start Command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and add the `ADMIN_PASSWORD` env var manually. Auto-deploy on push is on by default either way.

### 3. Frontend → Netlify (auto-deploys on every push)

1. Go to [netlify.com](https://netlify.com), sign up with GitHub
2. **Add new site** → **Import an existing project** → connect GitHub → select this repo
3. Netlify reads `netlify.toml` automatically (base directory `expense-salary-tracker/frontend`, no build step needed since it's static)
4. Click **Deploy** — live in under a minute

From now on, **any push to `main` auto-redeploys** the frontend too.

> Note: this replaces the earlier "drag and drop" method. Drag-and-drop deploys don't auto-update on push — connecting via GitHub is what enables continuous deployment.

### 4. Connect frontend to backend

Open your live Netlify URL → login screen → after logging in, if you see the red "Can't reach backend API" banner, paste your Render URL (`https://your-service.onrender.com`) and hit **Connect**. This is saved in the page's URL, so bookmark it.

---

## Local development (Codespaces)

**Backend:**
```bash
cd expense-salary-tracker
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd expense-salary-tracker/frontend
python3 -m http.server 5500
```
Open the forwarded port 5500 URL, set the API URL to your forwarded port 8000 URL via the API settings link.

Default local login password: `admin123` (change via `ADMIN_PASSWORD` env var before deploying).

## Known limitation

The database (`tracker.db`) is SQLite, stored as a file. Render's **free tier** file storage is not permanent — data can be lost on restart/redeploy. Fine for testing; for production use, consider migrating to Render's free PostgreSQL add-on.
