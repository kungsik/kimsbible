from flask import Flask
from flask_mail import Mail, Message
from kimsbible.lib import config
from kimsbible import app


app.config.update(
    MAIL_SERVER = config.mail_server,
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USE_TLS=False,
    MAIL_USERNAME = config.mail_username,
    MAIL_PASSWORD = config.mail_password
)

mail = Mail(app)
mail.init_app(app)


def sendmail(recipients, subject, html):
    with app.app_context():
        try:
            msg = Message(
                sender=config.mail_sender,
                recipients=recipients,
                subject=subject,
                html=html
            )

            mail.send(msg)

            return True
        
        except:
            return False
