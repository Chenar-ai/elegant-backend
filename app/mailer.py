import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.config import BREVO_CONFIG

def send_contact_email(from_email: str, subject: str, message: str):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_CONFIG["api_key"]

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": BREVO_CONFIG["to_email"]}],
        sender={"email": from_email},
        subject=subject or "New Contact Form Message",
        text_content=message
    )

    try:
        response = api_instance.send_transac_email(email)
        print("✅ Email sent! Message ID:", response.message_id)
        return True
    except ApiException as e:
        print("❌ Brevo email failed:", e)
        return False