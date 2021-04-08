from os import environ
import smtplib

class Email():
    def __init__(self, email):
        self.email = email

    def send_email(self, content):
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.login(environ.get('SMTP_EMAIL'), environ.get('SMTP_PASSWORD'))
        server_ssl.sendmail(environ.get('SMTP_EMAIL'), self.email, content)
        server_ssl.close()

    def welcome_email(self, activation_code):
        to = self.email
        subject = 'Welcome to Sellit'
        body = f'Welcome to Sellit. You activate your account, please visit the link below. \n\n auth.{environ.get("SITE_URL")}/email/verify/{activation_code}'
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def reset_password_email(self, reset_code):
        to = self.email
        subject = 'Reset Your Password'
        body = f"You've recently requested a password reset. To reset your password visit the link below. \n\nauth.{environ.get('SITE_URL')}/reset/password/{reset_code}\n\nIf you did not request this password reset, consider changing your email address and password. Please contact support if you need any help"
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def password_successfully_reset_email(self, password):
        to = self.email
        subject = 'Your New Password'
        body = f"Your password has been successfully reset. You can now login with the password below \n\nPassword: {password}"
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def password_changed(self):
        to = self.email
        subject = 'Password change confirmation'
        body = f"Your password has been successfully changed."
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def email_change_email(self, email):
        to = self.email
        subject = 'Email Change Confirmation'
        body = f"Your email has been changed from {self.email} to {email}. If you did not make this change, please contact support as soon as possible."
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def out_of_stock(self, product_name, order_id):
        to = self.email
        subject = f'Sellit - Order #{order_id} - Out of stock'
        body = f"Unfortunately {product_name} is now out of stock. Please contact the seller regarding your refund. They have been notified."
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)


    def order_confirmation_items(self, items, order_id):
        to = self.email
        subject = f'Sellit - Order #{order_id}'
        body = "Your purchase is complete. Below is your purchase details: \n\n" +  '\n'.join(items)
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def order_confirmation_attachment(self, order_id, file):
        to = self.email
        subject = f'Sellit - Order #{order_id}'
        body = f"Your purchase is complete. \n\n Click to download your file: {environ.get('SITE_URL')}/order/{order_id}/download/{file}"
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def leave_feedback(self, username, order_id):
        to = self.email
        subject = f'Sellit - Leave Feedback #{order_id}'
        body = f"Please leave feedback for your order. {environ.get('SITE_URL')}/@{username}/order/{order_id}/feedback"
        content = f'Subject: {subject}\n\n{body}'

        self.send_email(content)

    def donation_received(self, amount):
        to = self.email
        subject = f'Sellit - New Donation Received'
        body = f"You've received a new donation of the amount {amount}"
        content = f'Subject: {subject}\n\n{body}'.encode('utf-8')

        self.send_email(content)


    def ticket_created(self, message, username, ticket_id):
        to = self.email
        subject = f'Sellit - New Ticket Opened'
        body = f"You've opened a new ticket with {username}. Please keep an eye on your email. The seller should reply next time they're online. You can view your ticket here: {environ.get('SITE_URL')}/ticket/{self.email}/{ticket_id}"
        content = f'Subject: {subject}\n\n{body}'.encode('utf-8')

        self.send_email(content)

    def seller_new_ticket_notification(self):
        to = self.email
        subject = f'Sellit - New Ticket Opened'
        body = f"A new ticket has been opened. Please check your Account to respond."
        content = f'Subject: {subject}\n\n{body}'.encode('utf-8')

        self.send_email(content)

    
