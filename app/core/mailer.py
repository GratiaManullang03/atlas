from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings

# Konfigurasi berdasarkan settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates' / 'emails'
)

# Inisialisasi FastMail
fm = FastMail(conf)

async def send_email(
    subject: str,
    recipient: str,
    template_name: str,
    template_body: Dict[str, Any]
):
    """
    Mengirim email menggunakan template.
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],
            template_body=template_body,
            subtype="html"
        )
        await fm.send_message(message, template_name=template_name)
    except Exception as e:
        print(f"Error sending email: {e}")
        # Di lingkungan produksi, Anda mungkin ingin log error ini
        # atau menambahkannya ke sistem antrian jika pengiriman gagal.