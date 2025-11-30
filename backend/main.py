from __future__ import annotations

from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv
from supabase import Client, create_client
import resend

APP_ROOT = Path(__file__).resolve().parent
EMAIL_LOG = APP_ROOT / "sent_emails.log"
ADMIN_EMAIL = "fomondi@vassar.edu"

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_TABLE = os.environ.get("SUPABASE_TABLE", "shows")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "ComedyUO <onboarding@resend.dev>")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the backend .env"
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Initialize Resend if API key is provided
resend_configured = False
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    resend_configured = True
    # Warn if using a potentially unverified domain
    if RESEND_FROM_EMAIL and "@resend.dev" not in RESEND_FROM_EMAIL:
        print(
            f"⚠️  Warning: Using FROM email '{RESEND_FROM_EMAIL}'\n"
            "   Make sure this domain is verified in Resend, or use:\n"
            "   RESEND_FROM_EMAIL=ComedyUO <onboarding@resend.dev>\n"
        )

app = FastAPI(title="ComedyUO Shows", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ShowBase(BaseModel):
    title: str = Field(..., max_length=140)
    location: str = Field(..., max_length=140)
    start_time: datetime
    description: str
    status: str = Field(default="upcoming", pattern="^(upcoming|past)$")


class ShowCreate(ShowBase):
    pass


class ShowUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=140)
    location: Optional[str] = Field(None, max_length=140)
    start_time: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(upcoming|past)$")


class ShowOut(ShowBase):
    id: int


class EmailRequest(BaseModel):
    show_id: int
    guest_name: str
    guest_email: EmailStr
    message: str | None = None


class EmailResponse(BaseModel):
    subject: str
    to: EmailStr
    preview: str


# -----------------------------------------------------------------------------
# Supabase helpers and CRUD operations
# -----------------------------------------------------------------------------

def _parse_show(record: dict[str, Any]) -> ShowOut:
    raw = dict(record)
    # Supabase typically returns ISO strings with Z; normalize for fromisoformat
    start = raw.get("start_time")
    if isinstance(start, str):
        raw["start_time"] = datetime.fromisoformat(
            start.replace("Z", "+00:00")
        )
    return ShowOut.model_validate(raw)


@app.get("/shows", response_model=list[ShowOut])
def list_shows(status: str | None = None):
    if status and status not in {"upcoming", "past"}:
        raise HTTPException(status_code=400, detail="Invalid status filter")

    query = supabase.table(SUPABASE_TABLE).select("*").order("start_time")
    if status:
        query = query.eq("status", status)
    response = query.execute()
    # No response.error in this client; if something goes wrong, Supabase will raise.
    return [_parse_show(row) for row in (response.data or [])]


@app.get("/shows/{show_id}", response_model=ShowOut)
def get_show(show_id: int):
    response = (
        supabase.table(SUPABASE_TABLE)
        .select("*")
        .eq("id", show_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    if not data:
        raise HTTPException(status_code=404, detail="Show not found")
    return _parse_show(data[0])


@app.post("/shows", response_model=ShowOut, status_code=status.HTTP_201_CREATED)
def create_show(show_in: ShowCreate):
    data = show_in.model_dump()
    data["start_time"] = show_in.start_time.isoformat()

    # ⬇️ no .select("*") here
    response = (
        supabase.table(SUPABASE_TABLE)
        .insert(data)
        .execute()
    )

    if not response.data:
        # Something went wrong / no row returned
        raise HTTPException(status_code=500, detail="Failed to create show")

    return _parse_show(response.data[0])


@app.put("/shows/{show_id}", response_model=ShowOut)
def update_show(show_id: int, show_in: ShowUpdate):
    updates = show_in.model_dump(exclude_unset=True)
    if "start_time" in updates and isinstance(updates["start_time"], datetime):
        updates["start_time"] = updates["start_time"].isoformat()
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    response = (
        supabase.table(SUPABASE_TABLE)
        .update(updates)
        .eq("id", show_id)
        .execute()
    )

    data = response.data or []
    if not data:
        raise HTTPException(status_code=404, detail="Show not found")
    return _parse_show(data[0])


@app.delete("/shows/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_show(show_id: int):
    response = (
        supabase.table(SUPABASE_TABLE)
        .delete()
        .eq("id", show_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Show not found")
    return None


# -----------------------------------------------------------------------------
# Email endpoint
# -----------------------------------------------------------------------------

def hydrate_email(show: ShowOut, payload: EmailRequest) -> str:
    show_date = show.start_time.strftime("%A, %B %d")
    show_time = show.start_time.strftime("%I:%M %p")
    doors_time = (show.start_time - timedelta(minutes=30)).strftime("%I:%M %p")
    message = payload.message or "No custom message provided."
    
    # HTML email template matching takehome.html design
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Inter, Arial; background-color: #feffff !important; padding: 0; margin: 0;">
  <div>
    <div dir="ltr" style="margin: 0px; width: 100%; padding: 0px; font-family: arial, sans-serif; color: #444a5b !important;">
      <table style="margin-left: auto; margin-right: auto; margin-top: 0px; margin-bottom: 0px; width: 100%; border-collapse: collapse; padding: 0px;">
        <tr>
          <th>
            <span style="justify-content: center">
              <div style="text-align: center">
                <img style="height: 175px; margin-top: 40px" src="https://cuo-email-photos.s3.us-east-1.amazonaws.com/cuo-white-logo.png" alt="ComedyUO" />
              </div>
            </span>
          </th>
        </tr>
      </table>
      <table role="presentation" valign="top" border="0" cellspacing="0" cellpadding="20" align="center" style="border-collapse: collapse; margin-left: auto; margin-right: auto; margin-top: 0px; margin-bottom: 0px; width: 600px; max-width: 600px; padding: 0px; font-size: 14px; color: #444a5b !important;">
        <tr>
          <td style="padding: 8px" align="center">
            <p style="font-size: 25px; margin: 0px; line-height: 35px; padding-top: 30px; color: #1a307a;">
              <strong>{show.title}</strong>
            </p>
            <p style="font-size: 22px; margin: 0px; margin-top: 20px; margin-bottom: 10px; color: #1a307a;">
              {show_date}
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding: 8px">
            <div style="line-height: 28px">
              <div style="text-align: center">
                <p style="font-size: 18px; color: #1a307a">
                  <strong>Hi {payload.guest_name}!</strong>
                </p>
                <p style="font-size: 18px; margin: 0px">
                  Here is the exclusive link to our comedy show at<br />@<br />
                  <b>{show.location}</b>
                </p>
              </div>
              <div>
                <p style="text-align: center; font-size: 18px">
                  {show_date}<br />
                  Timing<br />
                  Doors open: {doors_time}<br />
                  Show start: {show_time}<br />
                  <br />
                  {show.description}
                  <br /><br />
                </p>
              </div>
              <div style="text-align: center; padding: 30px">
                <a href="https://shop.comedyuo.com" target="_blank" style="font-size: 16px; padding: 15px; border: none; cursor: pointer; color: white; background-color: #1a307a; border-radius: 5px; text-decoration: none;">
                  GET YOUR TICKETS HERE
                </a>
              </div>
            </div>
          </td>
        </tr>
        <tr>
          <td>
            <div style="line-height: 22px">
              <div style="text-align: center">
                <p style="font-size: 16px">All lineups are a surprise!</p>
              </div>
            </div>
            <div style="text-align: center">
              <p style="font-size: 16px">
                If you have questions, feel free to DM us @comedy.uo on Instagram. Hope to see you there!
              </p>
              <p style="font-size: 16px">
                If you can't make it join the <a href="https://app.comedyuo.com/waitlist">waitlist</a> to get the latest on our upcoming shows ❤️
              </p>
              <div style="padding: 10px">
                <a href="https://app.comedyuo.com/waitlist" target="_blank" style="font-size: 16px; cursor: pointer; padding: 5px 10px; border: 1px solid #1a307a; color: #1a307a; background-color: white; border-radius: 3px; text-decoration: none;">
                  JOIN THE WAITLIST
                </a>
              </div>
            </div>
            <div style="line-height: 22px">
              <div style="text-align: center; font-style: italic">
                <p>—</p>
              </div>
              <div style="text-align: center; font-style: italic">
                <p>An important note on timing: doors open time for the show is 30 minutes prior to showtime. Come early to enjoy food & drinks.</p>
              </div>
              <div style="text-align: center; font-style: italic">
                <p>While we encourage you to take pictures and videos of the space, filming the comics is strictly prohibited.</p>
              </div>
              <div style="text-align: center; font-style: italic">
                <p>This is a 21+ event - security will be checking tickets and ID's.</p>
              </div>
              <div style="text-align: center; font-style: italic">
                <p>If you have any questions, please reach out to us via Instagram @comedy.uo or email us at admin@comedyuo.com</p>
              </div>
              <div style="text-align: center; font-style: italic; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                <p style="font-size: 14px; color: #666;">
                  <strong>Guest Inquiry Details:</strong><br />
                  Guest: {payload.guest_name} ({payload.guest_email})<br />
                  Message: {message}
                </p>
              </div>
            </div>
          </td>
        </tr>
      </table>
    </div>
  </div>
</body>
</html>"""
    return html


@app.post("/emails/send", response_model=EmailResponse)
def send_email(payload: EmailRequest):
    show = get_show(payload.show_id)
    hydrated = hydrate_email(show, payload)
    subject = f"Your ComedyUO Show Details: {show.title}"

    # Send email via Resend if configured
    email_sent = False
    email_error = None
    
    if resend_configured:
        try:
            params = {
                "from": RESEND_FROM_EMAIL,
                "to": [payload.guest_email],  # Send to the guest who filled out the form
                "subject": subject,
                "html": hydrated,
                "reply_to": ADMIN_EMAIL,  # So guest can reply to admin
            }
            result = resend.Emails.send(params)
            email_sent = True
            
            # Also notify admin about the guest inquiry
            try:
                admin_notification = {
                    "from": RESEND_FROM_EMAIL,
                    "to": [ADMIN_EMAIL],
                    "subject": f"New guest inquiry: {payload.guest_name} - {show.title}",
                    "html": (
                        f"<p>A new guest has requested show information:</p>"
                        f"<p><strong>Guest:</strong> {payload.guest_name} ({payload.guest_email})</p>"
                        f"<p><strong>Show:</strong> {show.title}</p>"
                        f"<p><strong>Message:</strong> {payload.message or 'No message provided'}</p>"
                    ),
                }
                resend.Emails.send(admin_notification)
            except Exception:
                # Don't fail if admin notification fails
                pass
            
            # Log successful send
            EMAIL_LOG.parent.mkdir(exist_ok=True, parents=True)
            with EMAIL_LOG.open("a", encoding="utf-8") as log_file:
                log_file.write(
                    f"[{datetime.utcnow().isoformat()}] "
                    f"✅ EMAIL SENT via Resend\n"
                    f"To: {payload.guest_email} ({payload.guest_name})\n"
                    f"Subject: {subject}\n"
                    f"Show: {show.title}\n"
                    f"Admin notified: {ADMIN_EMAIL}\n"
                    f"Resend ID: {result.get('id', 'unknown')}\n"
                    f"---\n"
                )
        except Exception as e:
            email_error = str(e)
            # Provide helpful error message for domain verification issues
            if "domain is not verified" in email_error.lower():
                email_error = (
                    f"{email_error}\n\n"
                    "💡 Solution: Use Resend's test domain in your .env file:\n"
                    "RESEND_FROM_EMAIL=ComedyUO <onboarding@resend.dev>\n\n"
                    "Or verify your own domain at https://resend.com/domains"
                )
            # Log error
            EMAIL_LOG.parent.mkdir(exist_ok=True, parents=True)
            with EMAIL_LOG.open("a", encoding="utf-8") as log_file:
                log_file.write(
                    f"[{datetime.utcnow().isoformat()}] "
                    f"❌ EMAIL SEND FAILED via Resend\n"
                    f"Error: {email_error}\n"
                    f"To: {payload.guest_email} ({payload.guest_name})\n"
                    f"From Address: {RESEND_FROM_EMAIL}\n"
                    f"Subject: {subject}\n"
                    f"Show: {show.title}\n"
                    f"---\n"
                )
    else:
        # Log that Resend is not configured
        EMAIL_LOG.parent.mkdir(exist_ok=True, parents=True)
        with EMAIL_LOG.open("a", encoding="utf-8") as log_file:
            log_file.write(
                f"[{datetime.utcnow().isoformat()}] "
                f"⚠️  EMAIL NOT SENT (Resend not configured)\n"
                f"To: {payload.guest_email} ({payload.guest_name})\n"
                f"Subject: {subject}\n"
                f"Show: {show.title}\n"
                f"---\n{hydrated}\n---\n"
            )

    # Return response (even if email send failed, we still log it)
    if email_error:
        raise HTTPException(
            status_code=500,
            detail=f"Email could not be sent: {email_error}"
        )
    
    return EmailResponse(
        subject=subject,
        to=payload.guest_email,
        preview=f"Show details for {show.title} sent to {payload.guest_name}",
    )

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
