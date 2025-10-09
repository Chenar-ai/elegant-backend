from fastapi import APIRouter, HTTPException
from app.schemas.contact import ContactForm
from app.mailer import send_contact_email

router = APIRouter()

@router.post("/contact")
async def submit_contact(form: ContactForm):
    success = send_contact_email(form.email, form.subject, form.message)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    return {"message": "Your message has been sent successfully."}
