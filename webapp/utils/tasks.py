from webapp import celery
from webapp import models as model
from webapp.utils.emails import Email
from webapp.utils.tools import timestamp

# Email tasks

@celery.task
def registration_email(email, verify):
    Email(email=email).welcome_email(activation_code=verify)

@celery.task
def password_reset_email(email, password_code):
    Email(email=email).reset_password_email(password_code)

@celery.task
def password_successfully_reset_email(email, password):
    Email(email=email).password_successfully_reset_email(password)

@celery.task
def password_changed_email(email):
    Email(email=email).password_changed()

@celery.task
def email_change_email(email, new_email):
    Email(email).email_change_email(new_email)

@celery.task
def order_complete_items(email, items, order_id):
    Email(email=email).order_confirmation_items(items, order_id)

@celery.task
def order_confirmation_attachment(email, order_id, file):
    Email(email=email).order_confirmation_attachment(order_id, file)

@celery.task
def out_of_stock_email(email):
    Email(email=email).out_of_stock()

@celery.task
def new_donation_email(email, amount):
    Email(email=email).donation_received(amount)

# Order tasks

@celery.task
def update_donation_status(donation_id):
    donation_timestamp = model.Donation().fetch_donation(donation_id)
    if donation_timestamp:
        if (int(timestamp(0)) > int(donation_timestamp.expiry)) and (donation_timestamp.status == 'Pending'):
            donation_timestamp.status = 'Cancelled'
            donation_timestamp.update()

@celery.task
def leave_feedback(email, username, order_id, order_hash):
    Email(email=email).leave_feedback(username, order_id, order_hash)

## ticket tasks

@celery.task
def ticket_created(email, message, username, ticket_id):
    Email(email=email).ticket_created(message, username, ticket_id)

@celery.task
def seller_new_ticket_notification(email):
    Email(email=email).seller_new_ticket_notification()