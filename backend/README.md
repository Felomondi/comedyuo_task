# ComedyUO Backend (Lean, Supabase)

Single-file FastAPI service backed by your Supabase `shows` table so the React app can list shows, filter upcoming vs past, open detail pages, manage CRUD, and trigger the email template.

## 1. Supabase Setup
1. Create a `shows` table in Supabase with at least:
   - `id` (bigint, identity, primary key)
   - `title` (text)
   - `location` (text)
   - `start_time` (timestamptz)
   - `description` (text)
   - `status` (text, constrained to `'upcoming'` or `'past'`)
2. Seed three upcoming shows (and optionally one past) using the SQL or Table Editor.

## 2. Backend Setup
Create `backend/.env` (or copy from `.env.example`):
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_TABLE=shows

# Optional: Resend API for sending emails
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=ComedyUO <onboarding@resend.dev>
```

**Note:** If `RESEND_API_KEY` is not set, emails will only be logged to `sent_emails.log` and not actually sent. Get your Resend API key from https://resend.com/api-keys

Then:
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 3. Endpoints
- `GET /shows?status=upcoming|past` – list shows (filter optional)
- `GET /shows/{id}` – detail
- `POST /shows` – create
- `PUT /shows/{id}` – update
- `DELETE /shows/{id}` – remove
- `POST /emails/send` – hydrates an HTML email template (matching takehome.html design) and sends it via Resend API to `felixomondi727@gmail.com`. Also logs to `sent_emails.log` for auditing.

All routes respond with JSON so the React app can drive both the list view and details screen.
