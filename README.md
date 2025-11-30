# ComedyUO Shows (Lean Stack)

- `frontend/`: Small React SPA (Vite) that lists shows, filters upcoming vs past, and exposes a detail page with an email form.
- `backend/`: Minimal FastAPI + SQLite service with two responsibilities: CRUD for shows and an email-hydration endpoint that targets `felixomondi727@gmail.com`.

## Run locally
```
cd frontend
npm install       # already run once, repeat if needed
npm run dev
```
Open `http://localhost:5173` to view the page. The build has no backend dependency; all copy, links, and assets map directly to the provided HTML version.

## Production build
```
cd frontend
npm run build
```
Outputs static assets in `frontend/dist` that can be hosted on Netlify, Vercel, or any static host.

## Backend (FastAPI + SQLite)
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
FastAPI endpoints:
- `GET /shows?status=upcoming|past`
- `GET /shows/{id}`
- `POST /shows`
- `PUT /shows/{id}`
- `DELETE /shows/{id}`
- `POST /emails/send` (hydrates template + logs outgoing email to `backend/sent_emails.log`, aimed at `felixomondi727@gmail.com`)

The backend seeds three upcoming shows plus one past entry automatically, so the frontend filters have data immediately.
