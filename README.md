# ComedyUO Shows


## Technology Stack

**Frontend:**
- React 18
- Vite (build tool)
- React Router (routing)

**Backend:**
- Python 3
- FastAPI (web framework)
- Supabase (PostgreSQL database)
- Resend API (email delivery)
- Pydantic (data validation)

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory with the following variables:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_TABLE=shows
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=ComedyUO <onboarding@resend.dev>
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Testing API Endpoints

### CRUD Operations

All endpoints are available at `http://localhost:8000` when the backend is running.

#### 1. List All Shows

Get all shows or filter by status (upcoming/past):

```bash
# Get all shows
curl http://localhost:8000/shows

# Get only upcoming shows
curl http://localhost:8000/shows?status=upcoming

# Get only past shows
curl http://localhost:8000/shows?status=past
```

#### 2. Get a Single Show

Retrieve a specific show by ID:

```bash
curl http://localhost:8000/shows/1
```

#### 3. Create a Show

Create a new show:

```bash
curl -X POST http://localhost:8000/shows \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Friday Night Comedy",
    "location": "The Comedy Club",
    "start_time": "2024-12-20T20:00:00",
    "description": "An amazing night of comedy with surprise lineups!",
    "status": "upcoming"
  }'
```

The response will include the created show with an assigned ID.

#### 4. Update a Show

Update an existing show (you can update any combination of fields):

```bash
curl -X PUT http://localhost:8000/shows/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Show Title",
    "description": "Updated description"
  }'
```

#### 5. Delete a Show

Delete a show by ID:

```bash
curl -X DELETE http://localhost:8000/shows/1
```

This returns a 204 No Content status on success.

### Email Endpoint

#### Send Email

Send a formatted email with show details. **Important:** Due to Resend API account restrictions, emails can only be sent to `fomondi@vassar.edu`. Any email address entered in the form will be replaced with this address.

```bash
curl -X POST http://localhost:8000/emails/send \
  -H "Content-Type: application/json" \
  -d '{
    "show_id": 1,
    "guest_name": "John Doe",
    "guest_email": "fomondi@vassar.edu",
    "message": "Looking forward to the show!"
  }'
```

The endpoint will:
1. Fetch the show details from the database
2. Generate an HTML email template with the show information
3. Send the email via Resend API to `fomondi@vassar.edu`
4. Send a notification email to the admin
5. Log the email details to `backend/sent_emails.log`

**Note:** The email includes show title, date, time, location, description, and links to purchase tickets. The email template matches the design provided in the original HTML template.

## Production Build

### Frontend

Build the frontend for production:

```bash
cd frontend
npm run build
```

This outputs static files in `frontend/dist` that can be deployed to any static hosting service (Vercel, Netlify, etc.).

### Backend

The backend can be deployed to any platform that supports Python applications (Render, Railway, Fly.io, etc.). Make sure to set the environment variables in your deployment platform's configuration.

