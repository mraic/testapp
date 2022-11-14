from flask import current_app, render_template
from flask_mail import Message

from src import mail


def created_bank_account(bank_account, recipients, accounts):
    msg = Message(
        subject="Hi {}, you have successfully account with {} no.".format(
            recipients,
            bank_account),
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[recipients])
    msg.html = render_template("email_template.html", accounts=accounts
                               )

    mail.send(msg)


def send_accounts_to_user(recipients, accounts, length):
    msg = Message(
        subject="Hi {}, list of your accounts".format(recipients),
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[recipients])
    msg.html = render_template("email_template_2.html", accounts=accounts,
                               length=length)

    mail.send(msg)
