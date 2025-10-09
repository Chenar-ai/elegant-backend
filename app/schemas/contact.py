from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr
    subject: str | None = None
    message: str
