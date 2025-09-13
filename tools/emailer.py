import os
import smtplib
from email.message import EmailMessage


def send_file(filepath: str, to: str, cfg: dict) -> None:
    """Send a file via email using config settings."""
    if not cfg.get('enabled'):
        return
    msg = EmailMessage()
    msg['Subject'] = 'Research Database'
    msg['From'] = cfg.get('from')
    msg['To'] = to
    with open(filepath, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='octet-stream',
                           filename=os.path.basename(filepath))
    with smtplib.SMTP(cfg.get('smtp_host'), cfg.get('smtp_port', 587)) as s:
        if cfg.get('smtp_user'):
            s.starttls()
            s.login(cfg.get('smtp_user'), cfg.get('smtp_pass'))
        s.send_message(msg)
