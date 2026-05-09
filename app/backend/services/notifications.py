import logging

# Set up a simple logger for our mock email service
logger = logging.getLogger("notifications")
logger.setLevel(logging.INFO)

# Create console handler with formatting
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('\n[EMAIL SERVICE] %(message)s\n')
ch.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(ch)

def send_collab_email(to_email: str, subject: str, message: str) -> None:
    """
    Mock function to simulate sending an email.
    In a production environment, this would integrate with SendGrid, SES, etc.
    """
    email_content = f"""
    ==================================================
    TO: {to_email}
    SUBJECT: {subject}
    --------------------------------------------------
    {message}
    ==================================================
    """
    logger.info(email_content)
