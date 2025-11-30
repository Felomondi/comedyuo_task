# ComedyUO Shows

A full-stack web application for managing and displaying comedy shows with email notifications.

## Live Deployment

- **Frontend:** [https://comedyuo.vercel.app/](https://comedyuo.vercel.app/)
- **Backend API:** [https://comedyuo-task-1.onrender.com/](https://comedyuo-task-1.onrender.com/)
- **API Documentation:** [https://comedyuo-task-1.onrender.com/docs](https://comedyuo-task-1.onrender.com/docs)

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

3. Create a `.env` file (optional for local development):
```
VITE_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Testing API Endpoints with Postman

### Base URL

- **Production:** `https://comedyuo-task-1.onrender.com`
- **Local Development:** `http://localhost:8000`

### CRUD Operations

I used postman to test my API endpoints

#### 1. List All Shows

**GET Request**

- **URL:** `https://comedyuo-task-1.onrender.com/shows`
- **Method:** GET
- **Headers:** None required


**Postman Steps:**
1. Create a new request
2. Set method to `GET`
3. Enter URL: `https://comedyuo-task-1.onrender.com/shows`
4. (Optional) Add query parameter `status` with value `upcoming` or `past`
5. Click Send

**Expected Response:** Array of show objects with `id`, `title`, `location`, `start_time`, `description`, and `status`.

#### 2. Get a Single Show

**GET Request**

- **URL:** `https://comedyuo-task-1.onrender.com/shows/{show_id}`
- **Method:** GET
- **Headers:** None required

**Postman Steps:**
1. Create a new request
2. Set method to `GET`
3. Enter URL: `https://comedyuo-task-1.onrender.com/shows/1` (replace `1` with actual show ID)
4. Click Send

**Expected Response:** Single show object with all details.

#### 3. Create a Show

**POST Request**

- **URL:** `https://comedyuo-task-1.onrender.com/shows`
- **Method:** POST
- **Headers:**
  - `Content-Type: application/json`
- **Body (JSON):**

```json
{
  "title": "Friday Night Comedy",
  "location": "The Comedy Club",
  "start_time": "2024-12-20T20:00:00",
  "description": "An amazing night of comedy with surprise lineups!",
  "status": "upcoming"
}
```

**Expected Response:** Created show object with assigned `id`.

**Note:** `status` must be either `"upcoming"` or `"past"`. `start_time` must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

#### 4. Update a Show

**PUT Request**

- **URL:** `https://comedyuo-task-1.onrender.com/shows/{show_id}`
- **Method:** PUT
- **Headers:**
  - `Content-Type: application/json`
- **Body (JSON):** Include only the fields you want to update

```json
{
  "title": "Updated Show Title",
  "description": "Updated description"
}
```

**Expected Response:** Updated show object.

**Note:** You can update any combination of fields: `title`, `location`, `start_time`, `description`, or `status`. Omit fields you don't want to change.

#### 5. Delete a Show

**DELETE Request**

- **URL:** `https://comedyuo-task-1.onrender.com/shows/{show_id}`
- **Method:** DELETE
- **Headers:** None required

**Expected Response:** 204 No Content (empty response body on success).

### Email Endpoint

#### Send Email

**POST Request**

- **URL:** `https://comedyuo-task-1.onrender.com/emails/send`
- **Method:** POST
- **Headers:**
  - `Content-Type: application/json`
- **Body (JSON):**

```json
{
  "show_id": 1,
  "guest_name": "John Doe",
  "guest_email": "fomondi@vassar.edu",
  "message": "Looking forward to the show!"
}
```

**Expected Response:**
```json
{
  "subject": "Your ComedyUO Show Details: [Show Title]",
  "to": "fomondi@vassar.edu",
  "preview": "Show details for [Show Title] sent to [Guest Name]"
}
```

**Important:** Due to Resend API account restrictions, emails can only be sent to `fomondi@vassar.edu`. The email address in the request will be used, but the Resend API account is configured to send to this specific address. I could have added the @comedy.uo domain but I needed access to your records in the hosting platform. 

**What happens:**
1. Fetches the show details from the database using `show_id`
2. Generates an HTML email template with the show information
3. Sends the email via Resend API to the specified email address
4. Sends a notification email to the admin
5. Logs the email details to `backend/sent_emails.log`

**Note:** The email includes show title, date, time, location, description, and links to purchase tickets. The email template matches the design provided in the original HTML template.

## Production Build

Frontend was deployed on vercel: https://comedyuo.vercel.app/
Backend was deployed as a web service on Render: https://comedyuo-task-1.onrender.com/
