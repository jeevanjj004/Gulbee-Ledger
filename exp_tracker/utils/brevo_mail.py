import requests
from django.conf import settings


def send_brevo_email(
    subject,
    html_content,
    text_content,
    to_email,
    to_name=""
):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": "GulbeeLedger",
            "email": settings.DEFAULT_FROM_EMAIL,
        },
        "to": [
            {
                "email": to_email,
                "name": to_name,
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": text_content,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()