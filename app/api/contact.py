from fastapi import APIRouter, HTTPException
from app.schemas.contact import ContactForm
from app.mailer import send_contact_email
import asyncio

router = APIRouter()

@router.post("/contact")
async def submit_contact(form: ContactForm):
    # Run the email sending in a thread (since Brevo SDK is sync)
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, send_contact_email, form.email, form.subject, form.message)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"message": "Your message has been sent successfully."}
