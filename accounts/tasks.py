import logging

from project.celery import app

logger = logging.getLogger(__name__)


@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="accounts.tasks.send_sms_task",
)
def send_sms_task(self, phone_number, message):
    payload = {
        "message": message,
        "phone_number": str(phone_number),
    }
    logger.info(f"Send sms, payload: {payload}")


@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="accounts.tasks.send_email_task",
)
def send_email_task(self, email_to, subject, message, email_from=None):
    payload = {
        "message": message,
        "subject": subject,
        "email_from": email_from,
        "email_to": email_to,
    }
    logger.info(f"Send email, payload: {payload}")
