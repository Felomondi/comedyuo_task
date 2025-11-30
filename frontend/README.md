# ComedyUO Frontend (Lean)

React + Vite SPA that hits the FastAPI backend to list comedy shows, filter by status, render details, and ping the admin via the email endpoint.

## Run locally
```
cd frontend
cp .env.example .env   # optional – defaults to http://localhost:8000
npm install
npm run dev
```
Open `http://localhost:5173` and ensure the backend is running on the API URL in `.env`.

## Build
```
npm run build
```
Outputs static files in `dist/` for any static host.
