from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, TextAreaField, SelectField, DecimalField, FileField, IntegerField, SelectMultipleField, HiddenField, BooleanField, DateField
from wtforms.validators import InputRequired, Email, Length, EqualTo, Optional
from wtforms.widgets import html5 as h5widgets
from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, message='Username must be a minimum of 3 characters.')])
    email = StringField(validators=[InputRequired(), Email('Invalid Email'), Length(max=200, message="Email should be a maximum of 200 characters.")])
    password = PasswordField(validators=[InputRequired(), Length(min=8, message='Password must have a minimum 8 characters')])
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password', message='Passwords do not match')])
    date_of_birth = DateField('Date of Birth', validators=[InputRequired()], widget=h5widgets.DateInput())
    terms = BooleanField('Terms', validators=[InputRequired(message='You must agree to the Terms & Conditions')])

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email('Invalid Email')])
    password = PasswordField(validators=[InputRequired()])

class PasswordResetForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email('Invalid Email')])

class SettingsForm(FlaskForm):
    username = StringField('Username')
    avatar = FileField('Avatar')
    email = StringField('Email', validators=[InputRequired(), Email('Invalid Email'), Length(max=200, message="Email should be a maximum of 200 characters.")])
    paypal_email = StringField('PayPal Email', validators=[Length(max=200, message="Email should be a maximum of 200 characters.")])
    tawk_key = StringField('Tawk Key', validators=[Optional()])
    currency = SelectField('Currency', validators=[InputRequired()], choices=[('GBP', '£ GBP'), ('EUR', '€ EURO'), ('USD', '$ USD')])
    timezone = SelectField('Timezone', validators=[InputRequired()], choices=[('Europe/London', '''London, United Kingdom'''), ('US/Pacific', '''Pacific Time, United States'''), ('US/Mountain', '''Mountain Time, United States'''), ('US/Central', '''Central Time, United States'''), ('US/Eastern', '''Eastern Time, United States'''), ('Brazil/DeNoronha', '''Rio De Janeiro, Brazil'''), ('Europe/Berlin', '''Berlin, Germany'''), ('Europe/Moscow', '''Moscow, Russia'''), ('Asia/Dubai', '''Dubai, United Arab Emirates'''), ('Indian/Christmas', '''Mumbai, India'''), ('Asia/Singapore', '''Singapore, Singapore'''), ('Asia/Shanghai', '''Beijing, China'''), ('Asia/Tokyo', '''Tokyo, Japan'''), ('Australia/Sydney', '''Sydney, Australia'''), ('Pacific/Auckland', '''Auckland, New Zealand''')])

class SecurityForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, message='Password must have a minimum 8 characters')])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords do not match')])

class ProductForm(FlaskForm):
    product_type = HiddenField('Product Type')
    product_name = StringField('Product Name', validators=[InputRequired(), Length(min=3, max=100, message='Product title should be between 3 and 100 characters')])
    product_image = FileField('Product Image', validators=[Optional()])
    description = TextAreaField('Product Description')
    description_value = HiddenField('Product Description Value', validators=[InputRequired(), Length(min=3, max=9999, message='Description should be between 3 and 9999 characters')])
    items = TextAreaField('Product Items')
    attachment_file = SelectField('Attachment File', validators=[Optional()], choices=[])
    price = DecimalField('Product Price', validators=[InputRequired()])
    stock = IntegerField('Quantity', validators=[Optional()], widget=h5widgets.NumberInput())
    categories = SelectMultipleField('Categories', validators=[Optional()], choices=[])

class PaymentForm(FlaskForm):
    ''' payment form for settings page '''
    paypal = StringField('PayPal Email', validators=[Optional(), Email('Invalid Email')])
    paypal_delivery = BooleanField('Deliver to PayPal Emails only', validators=[Optional()])
    BTC = StringField('Bitcoin Address', validators=[Optional()])
    ETH = StringField('Ethereum Address', validators=[Optional()])
    LTC = StringField('Litecoin Address', validators=[Optional()])

class SettingsNotificationsForm(FlaskForm):
   new_order = BooleanField('New Order')
   new_donation = BooleanField('New Donation')
   new_feedback = BooleanField('New Feedback')
   new_support_ticket = BooleanField('New Ticket')
   support_ticket_reply = BooleanField('New Ticket')

class CouponForm(FlaskForm):
    coupon_code = StringField('Coupon', validators=[InputRequired(), Length(max=50, message='Maximum Length for a coupon is 50 characters.')])
    discount_amount = IntegerField('Coupon Discount', validators=[InputRequired()], widget=h5widgets.NumberInput(max=100, step=1))
    start_date = DateField('Start Date', validators=[Optional()], widget=h5widgets.DateInput(), default=datetime.today())
    end_date = DateField('Start Date', validators=[Optional()], widget=h5widgets.DateInput())
    max_uses = IntegerField('Max Uses', validators=[Optional()])
    coupon_restricted = BooleanField('Product Restriction')
    product_list = SelectMultipleField('Products', validators=[Optional()], choices=[])

class AttachmentForm(FlaskForm):
    attachment_upload = FileField('Attachment Upload', validators=[InputRequired()])

class CategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[InputRequired(), Length(max=50)])
    linked_products = SelectMultipleField('Linked Products', validators=[Optional()], choices=[])

class BlacklistForm(FlaskForm):
    blacklist_type = SelectField('Blacklist Type', validators=[InputRequired()], choices=[('Email', 'Email'), ('IP', 'IP')])
    blocked_data = StringField('Blacklist Data', validators=[InputRequired()])

class PurchaseProduct(FlaskForm):
    quantity = IntegerField('Quantity Amount', validators=[InputRequired()], widget=h5widgets.NumberInput(min=1, step=1))
    email = StringField('Delivery Email', validators=[Optional(), Email('Please enter a valid email')])
    coupon_code = StringField('Coupon Code', validators=[Optional()])
    coupon_set = HiddenField('Coupon Set', validators=[Optional()])
    payment_method = HiddenField('PM', validators=[InputRequired()])
    product_id = HiddenField('pid', validators=[InputRequired()])

class DonationSettingsForm(FlaskForm):
    amount = DecimalField('Donation Amount', validators=[InputRequired()], widget=h5widgets.NumberInput(max=100000, step=0.01))

class MakeDonationForm(FlaskForm):
    amount = DecimalField('Donation Amount', validators=[InputRequired()], widget=h5widgets.NumberInput(max=100000, step=0.01))
    leave_message = BooleanField(validators=[Optional()])
    name = StringField('Name', validators=[Optional()])
    message = TextAreaField('Message', validators=[Optional()])
    payment_method = HiddenField('Payment Method')
    uuid = HiddenField('uuid')

class StoreContact(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email('Please enter a valid email')])
    subject = StringField('Subject', validators=[InputRequired(), Length(min=3, max=100, message='Subject should be between 3-100 characters')])
    order_id = StringField('Order ID', validators=[Optional(), Length(max=40, message='Invalid Order ID')])
    message = TextAreaField('Message', validators=[InputRequired(), Length(min=3, max=1000, message='Message should be between 3-1000 characters')])

class TicketReply(FlaskForm):
    message = TextAreaField('Message', validators=[InputRequired(), Length(min=3, max=1000, message='Message should be between 3-1000 characters')])