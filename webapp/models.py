import webapp.utils.tasks as task
from webapp.database import db
from webapp.payments.crypto import check_coin_transaction, create_coin_transaction
from webapp.payments.paypal import create_paypal_donation, create_paypal_order, check_paypal_success
from webapp.payments.stripe import create_donation_checkout, check_stripe_intent
from webapp.utils.regex import check_if_upload_is_image
from webapp.utils.tools import (check_coupon_dates, date_rearrange,
                             generate_string, hash_string, timestamp)
from webapp.utils.uploads import copy_file, delete_upload, upload_file
from os import environ
from typing import Union
from flask import session, flash
from flask_login import UserMixin, current_user
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uuid = db.Column(db.String(25), primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.String(10), nullable=False)
    registration_timestamp = db.Column(db.String(30), default=timestamp(0))
    setting_id = db.Column(db.String(25), foreign_keys=('settings.uuid'))
    api_token = db.Column(db.String(50), nullable=False)
    # relationships
    verification = db.relationship('Verification', back_populates='user', lazy=True, uselist=False)
    avatar = db.relationship('UserImage', backref='user_avatar', uselist=False)
    settings = db.relationship('Setting', back_populates='user', uselist=False)
    payment_methods = db.relationship('PaymentMethod', backref='user_payment_methods', uselist=False)
    categories = db.relationship('Category', backref='user_link', lazy=True)
    products = db.relationship('Product', backref='user_product', lazy=True, uselist=True)
    product_category = db.relationship('ProductCategory', backref='product', lazy=True, uselist=True)
    attachments = db.relationship('Attachment', backref="user_attachments", lazy=True)
    coupons = db.relationship('Coupon', backref='user_coupons', lazy=True)
    order = db.relationship('Order', backref='user_order', lazy=True, uselist=True)
    blacklist = db.relationship('Blacklist', backref="user_blacklist", lazy=True)
    donation = db.relationship('Donation', backref="user_donation_settings", uselist=False)

    def get_id(self) -> str:
        return self.uuid

    def get_username(self) -> str:
        return self.username

    def get_email(self) -> str:
        return self.email

    def create_user(self, data) -> object:
        self.uuid = generate_string(25)
        self.username = data.get('username')
        self.email = data.get('email')
        self.password = hash_string(data.get('password'))
        self.date_of_birth = data.get('date_of_birth')
        self.api_token = generate_string(49)

        db.session.add(self)
        db.session.commit()
        
        task.registration_email.apply_async(args=[self.email, Verification(user_uuid=self.uuid).add()])
        
        Setting(uuid=self.uuid).add()
        UserImage().add(self.uuid)
        PaymentMethod(id=self.uuid).add()
        EmailNotification(uuid=self.uuid).add()
        
        return self

    def check_credentials(self, email, password) -> object:
        return self.query.filter_by(email=email, password=hash_string(password)).first()

    def activate_account(self, email_code) -> bool:
        ''' Email activation once user has signed up '''
        ''' return False if the user hasn't verified their email '''
        
        query = Verification().query.filter_by(email_code=email_code).first()
        
        if not query:
            return False
        
        query.email_code = None
        db.session.commit()
        
        return True

    def password_reset(self, email) -> bool:
        ''' generate password reset code and send an email with a link '''
        
        query = self.query.filter_by(email=email).first()
        
        if not query:
            return False
        
        query.verification.password_code = generate_string(100)
        db.session.commit()
        
        task.password_successfully_reset_email.apply_async(args=[email, query.verification.password_code])

    def set_new_password(self, code) -> bool:
        ''' generate a new password for the user, which will have to be changed the next time they login '''
        ''' Then send an email with their new password '''
        
        query = Verification().query.filter_by(password_code=code).first()
        
        if not query:
            return False
        
        query.password_code = None
        new_password = generate_string(25)
        query.user.password = User.hash_password(new_password)
        
        db.session.commit()
        task.new_password_email.apply_async(args=[query.user.email, new_password])
        
        return True

    def update_password(self, password, new_password) -> Union[bool, str]:
        query = self.query.filter_by(uuid=current_user.get_id()).first()
        
        if hash_string(password) != query.password:
            return False
        
        query.password = hash_string(new_password)
        db.session.commit()
        
        task.password_changed_email.apply_async(args=[query.email])
        
        return query.uuid
        
    def fetch_user_logged_in(self) -> object:
        return self.query.filter_by(uuid=current_user.get_id()).first()

    def fetch_user_supply_username(self, username) -> object:
        return self.query.filter_by(username=username).first()

    def fetch_user_supply_uuid(self, uuid) -> object:
        return self.query.filter_by(uuid=uuid).first()

class UserImage(db.Model):
    __tablename__ = 'user_images'
    id = db.Column(db.String(25), db.ForeignKey('users.uuid'), primary_key=True)
    avatar_filename = db.Column(db.String(100), nullable=True, default='default')

    def add(self, uuid):
        self.id = uuid
        db.session.add(self)
        db.session.commit()

    def update_avatar(self, avatar_file) -> bool:
        ''' check if the user has previously uploaded an avatar. If they have, then remove their avatar and either:'''
        ''' : replace with their new avatar and delete the old '''
        ''' : set their avatar to default and delete the old avatar '''

        query = self.query.filter_by(id=current_user.get_id()).first()

        if not query:
            return False
        
        if str(avatar_filename.filename) == '':
            if query.avatar_filename != 'default':
                delete_upload(query.avatar_filename, environ.get('AWS_PROFILE_AVATARS'))
            query.avatar_name = 'default'
        else:
            delete_upload(query.avatar_name, environ.get('AWS_PROFILE_AVATARS'))
            query.avatar_name = upload_file(avatar_file, environ.get('AWS_PROFILE_AVATARS'))
        
        db.session.commit()

        return True

class Verification(db.Model):
    __tablename__ = 'verifications'
    id = db.Column(db.Integer, primary_key=True)
    email_code = db.Column(db.String(25), default=generate_string(25), nullable=True)
    password_code = db.Column(db.String(100), nullable=True)
    user_uuid = db.Column(db.String(25), db.ForeignKey('users.uuid'))
    user = db.relationship('User', back_populates='verification', uselist=False, lazy=True)

    def add(self) -> str:
        ''' Link user to verification and return generated email code '''
        
        db.session.add(self)
        db.session.commit()
        return self.email_code

    def update_verification(self, uuid) -> str:
        ''' Update email verification for existing user '''
        
        query = self.query.filter_by(user_uuid=uuid).first()
        query.email_code = generate_string(25)
        
        db.session.commit()
        
        task.registration_email.apply_async(args=[query.user.email, query.email_code])
        return query.email_code

class Setting(db.Model):
    __tablename__ = 'settings'
    uuid = db.Column(db.String(25), db.ForeignKey('users.uuid'), primary_key=True)
    currency = db.Column(db.String(5), nullable=False, default='GBP')
    tawk_key = db.Column(db.String(200), nullable=True)
    timezone = db.Column(db.String(50), nullable=False, default='Europe/London')
    donations = db.Column(db.Boolean, default=False, nullable=True)
    minimum_donation = db.Column(db.String(10), default=1, nullable=False)
    user = db.relationship('User', back_populates='settings', uselist=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        ''' update user settings: email, tawk, paypal, currency, timezone, user avatar '''
        query = self.query.filter_by(uuid=current_user.get_id()).first()
        
        if data.form.get('email') != query.user.email:
            task.email_change_email.apply_async(args=[query.user.email, data.form.get('email')])
            query.user.email = data.form.get('email')
        
        query.paypal = data.form.get('paypal_email')

        if data.form.get('tawk_key') == '':
            query.tawk_key = None
        else:
            query.tawk_key = data.form.get('tawk_key')
        
        query.currency = data.form.get('currency')
        query.timezone = data.form.get('timezone')

        if data.form.get('image-changed') == 'y':
            ''' user avatar has been changed '''
            UserImage(id=current_user.get_id()).update_avatar(data.files['avatar'])
        
        db.session.commit()

    def donation_toggle(self, value):
        ''' Set donation status to Boolean value: Enabled/Disabled '''
        
        query = self.query.filter_by(uuid=current_user.get_id()).first().donations = value
        db.session.commit()

    def update_minimum_amount(self, data):
        query = self.query.filter_by(uuid=current_user.get_id()).first()
        query.minimum_donation = data.get('amount')
        db.session.commit()

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.String(25), db.ForeignKey('users.uuid'), primary_key=True)
    paypal = db.Column(db.String(200), nullable=True)
    paypal_delivery = db.Column(db.Boolean, nullable=True) ## If set to True: Products will only be delivered the email used for paypal payment
    stripe = db.Column(db.String(50), nullable=True)
    BTC = db.Column(db.String(40), nullable=True) # Bitcoin
    ETH = db.Column(db.String(40), nullable=True) # Ethereum
    LTC = db.Column(db.String(40), nullable=True) # Litecoin

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update_stripe_acc(self, acc_id):
        self.query.filter_by(id=current_user.get_id()).first().stripe = acc_id
        db.session.commit()

    def remove_stripe_acc(self):
        user = self.query.filter_by(id=current_user.get_id()).first().stripe = None
        db.session.commit()

    def update_payment_methods(self, data):
        query = self.query.filter_by(id=current_user.get_id()).first()
        
        query.paypal = data.get('paypal')
        
        if data.get('paypal_delivery') == 'y':
            query.paypal_delivery = True
        else:
            query.paypal_delivery = False
       
        query.BTC = data.get('BTC')
        query.ETH = data.get('ETH')
        query.LTC = data.get('LTC')
        
        db.session.commit()

    def fetch_user_payment_method(self):
        return self.query.filter_by(id=current_user.get_id()).first()

class EmailNotification(db.Model):
    id = db.Column(db.String(10), nullable=False, primary_key=True)
    uuid = db.Column(db.String(25), db.ForeignKey('users.uuid'), nullable=False)
    new_order = db.Column(db.Boolean, default=True)
    new_donation = db.Column(db.Boolean, default=True)
    new_feedback = db.Column(db.Boolean, default=True)
    new_support_ticket = db.Column(db.Boolean, default=True)
    support_ticket_reply = db.Column(db.Boolean, default=True)

    def add(self):
        db.session.add(self)
        db.session.commit()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.String(8), primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)
    product_count = db.Column(db.Integer, nullable=True, default=0)
    user = db.Column(db.String(25), db.ForeignKey('users.uuid'))

    def add(self, data) -> Union[bool, str]:
        self.id = generate_string(8)
        self.user = current_user.get_id()
        self.category_name = data.get('category_name')
        
        if self.query.filter_by(category_name=self.category_name, user=self.user).first():
            return False
        
        self.product_count = len(data.getlist('linked_products'))

        ## Search each item inside linked_products -> linked_products is each item now linked to selected category
        ## if item (linked_product) does not have a row inside ProductCategory: i.e doesn't exist
        ## add product category

        for item in data.getlist('linked_products'):
            if not ProductCategory().query.filter_by(product_id=item, category_name=self.category_name, user=current_user.get_id()).first():
                ProductCategory(product_id=item, category_name=self.category_name, user=current_user.get_id()).add()
        
        db.session.add(self)
        db.session.commit()
        
        return self.id

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, category_id, data) -> bool:
        query = self.query.filter_by(id=category_id).first()
        
        if not query:
            return False
        
        query.category_name = data.get('category_name')

        query.product_count = len(data.getlist('linked_products'))

        product_categories = ProductCategory().query.filter_by(category=query.name, user=current_user.get_id()).all()
        linked_products_list = data.getlist('linked_products')
        
        if product_categories:
            for item in product_categories:
                if item.product_id not in linked_products_list:
                    item.delete()
            for product_cat in linked_products_list:
                if not ProductCategory().query.filter_by(product_id=product_cat).first():
                    ProductCategory(product_id=product_cat, category=query.name, user=current_user.get_id()).add()
        else:
            for item in linked_products_list:
                ProductCategory(product_id=item, category=query.name, user=current_user.get_id()).add()

        return True

    def update_product_count(self, category, equation):
        query = self.query.filter_by(user=current_user.get_id(), category_name=category).first()
        
        if not query:
            return None
        
        if '+' in equation:
            query.product_count = query.product_count + 1
        
        else:
            query.product_count = query.product_count - 1
        
        db.session.commit()

    def fetch_user_categories(self) -> Union[None, object]:
        return self.query.filter_by(user=current_user.get_id()).all()

    def fetch_user_categories_pagination(self) -> Union[None, object]:
        return self.query.filter_by(user=current_user.get_id()).paginate(per_page=12)

    def fetch_category_by_id(self, category_id) -> Union[None, object]:
        return self.query.filter_by(id=category_id).first()

    def remove_category(self, category_id) -> Union[None, str]:
        query = self.fetch_category_by_id(category_id)
        
        if not query:
            return None

        query.delete()

        product_categories = ProductCategory().delete_all_linked_categories(query.category_name)

        return query.category_name

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(10), nullable=False)
    description = db.Column(db.TEXT(1500), nullable=False)
    product_type = db.Column(db.String(10), nullable=False)
    stock = db.Column(db.String(20), nullable=True)
    timestamp = db.Column(db.String(35), default=timestamp(0))
    user = db.Column(db.String(25), db.ForeignKey('users.uuid'))
    ## relationships
    product_attachment = db.relationship('ProductAttachment', backref='product_attachment', uselist=False, lazy=True)
    product_image = db.relationship('ProductImage', backref='product_image', lazy=True, uselist=False)
    product_items = db.relationship('ProductItem', backref='product_items', lazy=True, uselist=True)
    product_category = db.relationship('ProductCategory', backref='product_category', lazy=True, uselist=True)
    order = db.relationship('Order', backref='ordered_product', lazy=True, uselist=True)

    def add(self, data):
        self.id = generate_string(8)
        
        while self.query.filter_by(id=self.id).first():
            self.id = generate_string(8)

        self.name = data.form.get('product_name')
        self.price = float(data.form.get('price'))
        self.description = data.form.get('description_value')
        self.product_type = data.form.get('product_type')
        self.user = current_user.get_id()

        if self.product_type == 'file':
            ProductAttachment().add(self.id, data.form.get('attachment_file'))
            self.stock = data.form.get('stock')
        
        db.session.add(self)
        db.session.commit()
        
        if self.product_type == 'item':
            product_item_list = ProductItem().add_product_items(self.id, data.form.get('items'))
        
        ProductImage(id=self.id).add(data.files['product_image'])

        for item in data.form.getlist('categories'):
            ProductCategory(product_id=self.id, category_name=item, user=self.user).add()
            
            Category().update_product_count(item, '+')

    def update(self, data, product_id) -> Union[bool, str]:
        product = self.query.filter_by(id=product_id).first()
        
        if not product:
            return False
        
        product.name = data.form.get('product_name')
        product.price = float(data.form.get('price'))
        product.description = data.form.get('description_value')

        if data.form.get('image-changed') == 'y':
            ProductImage().update_product_image(self.id, data.files)

        if product.product_type == 'item':
            if data.form.get('product_type') == 'item':
                new_product_items = ProductItem().update_product_items(product.id, data.form.get('items').split('\n'))
                product.stock = new_product_items

            else:
                ProductItem().remove_all_product_items(product.id)
                product.product_type = 'file'
                product.stock = data.form.get('stock')

                ProductAttachment().add(product.id, data.form.get('attachment_file'))

        else:
            if data.form.get('product_type') == 'item':
                product_items_list = ProductItem().add_product_items(product.id, data.form.get('items'))
                product.stock = product_items_list
                product.product_type = 'item'
                ProductAttachment().delete(product.id)
            
            else:
                product.attachment = data.form.get('attachment_file')
                product.stock = data.form.get('stock')
                
                ProductAttachment().update_attachment_filename(product_id, data.form.get('attachment_file'))

        db.session.commit()
        
        if data.form.get('image-changed'):
            ProductImage().update_product_image(product.id, data.files['product_image'])
                    
        ProductCategory().update_product_categories(product.id, data.form.getlist('categories'), current_user.get_id())
        
        return product.id

    def delete(self, product_id) -> bool:
        query = self.query.filter_by(id=product_id).first()
        
        if not query:
            return False

        if query.product_type == 'item':
            ProductItem().remove_all_product_items(query.id)

        else:
            ProductAttachment().delete(product_id)

        ProductImage().delete(product_id)
        
        ProductCategory().remove_all_product_categories(query.id)

        db.session.delete(query)
        db.session.commit()
        
        return True

    def deliver_product(self, product_id, order_id, quantity, email) -> Union[object, bool]:
        query = self.query.filter_by(id=product_id).first()
        order = Order().query.filter_by(id=order_id).first()
        
        if (not order) or (not query):
            return False
        
        if int(query.stock) < int(quantity):
            order.status = 'Out of stock'
            db.session.commit()
            
            return out_of_stock_email.apply_async(email)

        if query.product_type == 'item':
            product_items = ProductItem().fetch_sold_serials(product_id, order_id)
            print(int(query.stock))
            print(len(product_items))
            query.stock = int(query.stock) - len(product_items)
            order.status = 'Completed'
            print(query.stock)
            task.order_complete_items.apply_async(args=[email, product_items, query.id])

        else:
            attachment = Attachment().query.filter_by(attachment_name=query.attachment).first()
            
            copy_file(query.attachment, environ.get('AWS_ATTACHMENTS'), environ.get('AWS_SOLD_ATTACHMENTS'))
            Sold(order_id=order.id, item=attachment.id).add()
            
            task.order_confirmation_attachment.apply_async(args=[order.email, order_id, attachment.id])

        db.session.commit()

        return True

    def fetch_user_products(self) -> object:
        return self.query.filter_by(user=current_user.get_id()).all()

    def fetch_product(self, product_id, uuid) -> object:
        return self.query.filter_by(id=product_id, user=uuid).first()

class ProductAttachment(db.Model):
    __tablename__ = 'product_attachment'
    id = db.Column(db.String(8), db.ForeignKey('products.id'), primary_key=True)
    attachment_filename = db.Column(db.String(100), nullable=False)

    def add(self, product_id, attachment):
        self.id = product_id
        self.attachment_filename = attachment
        
        db.session.add(self)

    def fetch_product_attachment(self, product_id):
        return self.query.filter_by(id=product_id).first()

    def update_attachment_filename(self, product_id, attachment_filename):
        query =  self.query.filter_by(id=product_id).first()

        if query.attachment_filename != attachment_filename:
            query.attachment_filename = attachment_filename

        db.session.commit()

    def delete(self, product_id):
        query = self.fetch_product_attachment(product_id)
        db.session.delete(query)
        db.session.commit()

class ProductItem(db.Model):
    __tablename__ = 'product_items'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(8), db.ForeignKey('products.id'))
    item = db.Column(db.String(255), nullable=False)

    @staticmethod
    def remove_white_space_entries(data) -> list:
        ''' remove white space entries and return list '''
        
        output = []

        for item in data:
            if (not item.isspace()) and (item != ''):
                output.append(item.replace('\r', ''))
        return output

    def add_product_items(self, product_id, product_item_list) -> len:
        ''' loop through NEW items list and if item is not empty -> add to db with product_id '''
        ''' update stock amount '''

        product_item_list = self.remove_white_space_entries(product_item_list.split('\n'))
        
        for item in product_item_list:
            ProductItem().insert_new_product_items(product_id, item)

        query = Product().fetch_product(product_id, current_user.get_id()).stock = len(product_item_list)
        db.session.commit()

        return len(product_item_list)

    def insert_new_product_items(self, product_id, item):
        self.product_id = product_id
        self.item = item
        db.session.add(self)
        db.session.commit()

    def update_product_items(self, product_id, new_product_items) -> len:
        ''' compare two lot of product_items. If they don't match, remove the product_item from old list and update with new list '''

        query = self.query.filter_by(product_id=product_id).all()

        if not query:
            return None

        original_product_items = []
        new_product_items = self.remove_white_space_entries(new_product_items)

        for product_item in query:
            original_product_items.append(product_item.item)

        if original_product_items != new_product_items:
            for old_item in original_product_items:
                if original_product_items.count(old_item) != new_product_items.count(old_item):
                    self.delete_item_by_id(product_id, old_item)
                    
                    original_product_items = [i for i in original_product_items if i != old_item]

            for new_item in new_product_items:
                if new_item not in original_product_items:
                    ProductItem().insert_new_product_items(product_id, new_item)

        db.session.commit()

        return len(new_product_items)

    def remove_all_product_items(self, product_id) -> bool:
        ''' remove all product items; usually when a seller chanegs their product type from items -> attachment or deletes their product '''

        query = self.query.filter_by(product_id=product_id).all()

        if not query:
            return None

        for item in query:
            db.session.delete(item)
            db.session.commit()

        return True
    
    def fetch_sold_serials(self, product_id, order_id) -> list:
        ''' method is called when product is sold. return list of serials to be delivered via email'''

        query = self.query.filter_by(product_id=product_id).all()

        item_list = []

        for item in query:
            item_list.append(item.item)
            item.delete()
            Sold(order_id=order_id, item=item.item).add()

        return item_list

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def delete_item_by_id(self, product_id, item):
        query = self.query.filter_by(product_id=product_id, item=item).first()
            
        db.session.delete(query)
        db.session.commit()

    def fetch_active_product_items(self, product_items) -> list:
        ''' fetch all unsold items relating to a product '''
        unsold_product_items = []

        for item in product_items:
            if item == product_items[-1]:
                unsold_product_items.append(item.item)
            else:
                unsold_product_items.append(f'{item.item}\n')

        return unsold_product_items  

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.String(8), db.ForeignKey('products.id'), primary_key=True)
    original_image_filename = db.Column(db.String(100), nullable=True)
    image_filename = db.Column(db.String(45), nullable=False)

    def add(self, upload):
        ''' if no file is uploaded, set default image '''
        
        if "''" in str(upload):
            self.image_filename = 'default.png'
        else:
            self.original_image_filename = upload.filename
            self.image_filename = upload_file(upload, environ.get('AWS_PRODUCT_IMAGES'))
        
        db.session.add(self)
        db.session.commit()

    def update_product_image(self, product_id, upload):
        ''' replace product image. Check if product has previous image & remove '''
        
        query = self.query.filter_by(id=product_id).first()
        
        if not query:
            return None

        if "''" in str(upload):
            if query.image_filename:
                delete_upload(query.image_filename, environ.get('AWS_PRODUCT_IMAGES'))
                query.image_filename = 'default.png'
            
            query.original_image_filename = 'default.png'

        else:
            query.original_image_filename = upload.filename
            query.image_filename = upload_file(upload, environ.get('AWS_PRODUCT_IMAGES'))

        db.session.commit()

    def fetch_product_image(self, product_id) -> object:
        return self.query.filter_by(id=product_id).first()
    
    def delete(self, product_id):
        query = self.fetch_product_image(product_id)
        delete_upload(query.image_filename, environ.get('AWS_PRODUCT_IMAGES'))
        db.session.delete(query)
        db.session.commit()

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(8), db.ForeignKey('products.id'))
    category_name = db.Column(db.String(50), nullable=False)
    user = db.Column(db.String(25), db.ForeignKey('users.uuid'))

    def add(self):    
        db.session.add(self)
        db.session.commit()

    def update_product_categories(self, product_id, new_category_list, uuid) -> bool:
        ''' compare old product categories and new: '''
        ''' then remove the old and add the new '''
        query = self.query.filter_by(product_id=product_id).all()

        original_product_categories = []
        new_product_categories = []

        if query:
            for category in query:
                original_product_categories.append(category.category_name)

        for new_category in new_category_list:
            new_product_categories.append(new_category)

        if original_product_categories != new_product_categories:
            ## Delete replaced product categories
            for old_category in original_product_categories:
                if old_category not in new_category_list:
                    ProductCategory().delete_product_category(product_id, old_category)

            if new_category_list != []:
                ## add new product_categories
                for new_category in new_product_categories:
                    if new_category not in original_product_categories:
                        ProductCategory().add_new_product_category(product_id, new_category)
                        Category().update_product_count(new_category, '+')

        return True

    def add_new_product_category(self, product_id, category_name):
        ''' add new product category that is linked to a product '''

        self.product_id = product_id
        self.category_name = category_name
        self.user = current_user.get_id()

        ProductCategory().add(self)

    def delete_product_category(self, product_id, category):
        query = self.query.filter_by(product_id=product_id, category_name=category).first()
        ProductCategory().delete(self)

        Category().update_product_count(category, '-')

    def delete_all_linked_categories(self, category_name):
        ''' called when a user deletes a whole category '''
        ''' this method then deletes all categories linked to a product '''

        query = self.query.filter_by(category_name=category_name, user=current_user.get_id()).all()
        
        for item in query:
            db.session.delete(item)
            db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def remove_all_product_categories(self, product_id) -> bool:
        ''' remove all rows linked to a specific product '''

        query = self.query.filter_by(product_id=product_id).all()

        if not query:
            return False

        for item in query:
            item.delete()
            Category().update_product_count(item.category_name, '-')

        return True

    def fetch_linked_product_categories(self, product_id) -> object:
        return self.query.filter_by(product_id=product_id).all()

    def remove_all_categories(self, category_name) -> Union[None, bool]:
        ''' remove all product_categories after the primary Category has been deleted '''
        
        query = self.query.filter_by(category_name=category_name, user=current_user.get_id()).all()
        
        if not query:
            return None

        for item in query:
            query.delete()

        return True

class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.String(8), primary_key=True)
    uuid = db.Column(db.String(25), db.ForeignKey('users.uuid'))
    original_attachment_filename = db.Column(db.String(100), nullable=False)
    attachment_filename = db.Column(db.String(45), nullable=False)
    attachment_type = db.Column(db.String(10), nullable=False)

    def upload_attachment(self, upload) -> str:
        self.id = generate_string(8)
        self.uuid = current_user.get_id()
        self.original_attachment_filename = upload.filename
        self.attachment_filename = upload_file(upload, environ.get('AWS_ATTACHMENTS'))
        self.attachment_type = 'file'
        
        if(check_if_upload_is_image(self.original_attachment_filename)):
            self.attachment_type = 'image'
        
        db.session.add(self)
        db.session.commit()
        
        return self.attachment_filename

    def fetch_all_attachments(self, uuid) -> object:
        ''' fetch all attachments linked to user account '''
        
    def fetch_attachment(self, id) -> object:
        ''' fetch attachment by id and uuid '''
        return self.query.filter_by(id=id, uuid=current_user.get_id()).first()

    def check_if_already_exists(self, filename) -> object:
        ''' check if attachment exists. this is to prevent a user uploading the same attachment twice '''
        return self.query.filter_by(original_attachment_filename=filename, uuid=current_user.get_id()).first()

    def remove_attachment(self, id) -> True:
        ''' remove attachment when a user chooses to delete it '''
        
        attachment = self.fetch_attachment(id)
        delete_upload(attachment.attachment_filename, environ.get('AWS_ATTACHMENTS'))
        
        db.session.delete(attachment)
        db.session.commit()
        
        return True

    def fetch_user_attachments(self) -> object:
        return self.query.filter_by(uuid=current_user.get_id()).all()

    def fetch_user_attachments_pagination(self) -> object:
        print(type(self.query.filter_by(uuid=current_user.get_id()).paginate(per_page=12)))
        return self.query.filter_by(uuid=current_user.get_id()).paginate(per_page=12)

    def check_if_linked_to_product(self, attachment_id) -> bool:
        if Attachment().fetch_attachment(attachment_id):
            return False

        return True

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.String(12), primary_key=True)
    coupon_code = db.Column(db.String(50), nullable=False, unique=True)
    discount_amount = db.Column(db.String(5), nullable=False)
    max_uses = db.Column(db.String(10), nullable=True)
    start_date = db.Column(db.String(11), nullable=True)
    end_date = db.Column(db.String(11), nullable=True)
    restricted = db.Column(db.Boolean, nullable=True)
    uses = db.Column(db.Integer, default=0)
    user = db.Column(db.String(25), db.ForeignKey('users.uuid'))
    coupon_restriction = db.relationship('CouponRestrictedProduct', backref='linked_coupon', lazy=True)

    def add_coupon(self, data) -> Union[bool, str]:
        self.id = generate_string(12)
        self.coupon_code = data.get('coupon_code')

        if self.query.filter_by(coupon_code=self.coupon_code, user=current_user.get_id()).first():
            ''' user has already added the coupon '''
            return False

        self.discount_amount = data.get('discount_amount')
        self.max_uses = 0 if not data.get('max_uses') else int(data.get('max_uses'))
    
        if data.get('coupon_restricted') == 'y':
            self.restricted = True
            CouponRestrictedProduct().add_restricted_product(self.coupon_code, data.getlist('product_items'))
        
        self.start_date = date_rearrange(data.get('start_date'))
        self.end_date = date_rearrange(data.get('end_date'))
        
        self.user = current_user.get_id()
        
        db.session.add(self)
        db.session.commit()
        
        return self.id

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_all_coupons(self) -> object:
        ''' get all coupons linked to user account '''
        return self.query.filter_by(user=current_user.get_id()).paginate(per_page=12)

    def check_coupon(self, data) -> Union[bool, str]:
        ''' check if coupon is valid '''
        query = self.query.filter_by(coupon_code=data.get('coupon_code')).first()
        
        if (not query) or (query.coupon_code != data.get('coupon_code')):
            return False

        if (int(query.uses) >= int(query.max_uses)) and (int(query.max_uses) != 0):
            return False
        
        if (query.start_date != None) or (query.end_date != None):
           if not self.check_coupon_can_be_used(query.start_date, query.end_date, query.user):
               return False

        if query.restricted:
            if not CouponRestrictedProduct().check_product_matches_coupon(coupon_code=data.get('coupon_code'), product_id=data.get('coupon_code')):
                return False

        return query.discount_amount

    def check_coupon_can_be_used(self, start_date, end_date, uuid) -> bool:
        ''' check the coupon can be used by querying the start/end date '''
            
        timezone = User().fetch_user_supply_uuid(uuid).settings.timezone
            
        if start_date != None:
            if not check_coupon_dates(start_date, timezone, 'start'):
                return False
        
        if end_date != None:
            if not check_coupon_dates(start_date, timezone, 'end'):
                return False

        return True

    def update_coupon_use(self, coupon):
        ''' update the amount of times the coupon has been used '''
        
        query = self.query.filter_by(coupon_code=coupon).first()
        query.uses = query.uses + 1
        db.session.commit()

    def delete_coupon(self, coupon_id) -> Union[None, str]:
        query = self.query.filter_by(id=coupon_id, user=current_user.get_id()).first()

        if not query:
            return None

        if query.restricted:
            CouponRestrictedProduct().delete_all_restricted_coupons(query.coupon_code)
        
        query.delete()
        return query.id

    def fetch_coupon(self, coupon_id) -> object:
        return self.query.filter_by(id=coupon_id).first()

    def fetch_coupon_by_name_uuid(self, coupon_code) -> object:
        return self.query.filter_by(coupon_code=coupon_code, user=current_user.get_id())

    def prefill_coupon_values(self, form, data, coupon_id) -> Union[bool, object]:
        coupon = self.fetch_coupon(coupon_id)

        if not coupon:
            return False

        form.coupon_code.data = coupon.coupon_code
        form.discount_amount.data = coupon.discount_amount
        form.start_date.data = None if not coupon.start_date else datetime.strptime(coupon.start_date, '%d-%m-%Y')
        form.end_date.data = None if not coupon.end_date else datetime.strptime(coupon.end_date, '%d-%m-%Y')
        form.max_uses.data = coupon.max_uses
    
        if coupon.restricted:
            form.coupon_restricted.data = 'y'

        for item in Product().fetch_user_products():
            form.product_list.choices.append([item.id, item.name])

        return form

    def update_coupon(self, coupon_id, data) -> Union[None, bool]:
        coupon = self.query.filter_by(id=coupon_id).first()

        if not self.fetch_coupon_by_name_uuid(coupon.coupon_code):
            flash['Coupon code already exists. Please choose a different coupon code']
            return None

        coupon.coupon_name = data.get('coupon_code')
        coupon.discount_amount = data.get('coupon_amount')
        coupon.max_uses = data.get('max_uses')
        coupon.start_date = date_rearrange(data.get('start_date'))
        coupon.end_date = date_rearrange(data.get('end_date'))
        coupon.restricted = data.get('')

        if data.get('coupon_restricted') == 'y':
            coupon.restricted = True
            self.remove_products_linked_to_coupon(data.getlist('product_items'), )
            CouponRestrictedProduct().add_restricted_product(self.coupon_code, data.getlist('product_items'))

        return True

class CouponRestrictedProduct(db.Model):
    __tablename__ = 'coupon_restricted_products'
    id = db.Column(db.Integer, primary_key=True)
    coupon_code = db.Column(db.String(50), db.ForeignKey('coupons.coupon_code'), nullable=False)
    product_id = db.Column(db.String(8), nullable=False)
    uuid = db.Column(db.String(25), nullable=False)

    def add_restricted_product(self, coupon_code, product_list):
        for item in product_list:
            self.coupon_code = coupon_code
            self.product_id = item
            self.uuid = current_user.get_id()
            db.session.add(self)
        
        db.session.commit()

    def check_product_matches_coupon(self, coupon_code, product_id) -> Union[bool, object]:
        ''' check that coupon code is valid for a certain product '''
        return self.query.filter_by(coupon_code=coupon_code, product_id=product_id).first()

    def fetch_all_restricted_products(self,coupon_code):
        ''' fetch all products that can be used with coupon code '''
        return self.query.filter_by(coupon_code-coupon_code, uuid=current_user.get_id()).all()

    def compare_updated_restricted_list(self, coupon_code, new_restricted_products):
        ''' compare old restricted products and new restricted product. update if they don't match. >>> used when a seller updates their coupon code '''
        query = self.fetch_all_restricted_products(coupon_code)

        original_restricted_products = []
        
        for restricted_product in query:
            original_restricted_products.append(query.product_id)

        for new_restricted_product in new_restricted_products:
            if new_restricted_product not in original_restricted_products:
                self.add_restricted_product(coupon_code, new_restricted_product)

    def delete_all_restricted_coupons(self, coupon_code):
        ''' when a user deletes a coupon -> remove all linked restrictions '''

        query = self.query.filter_by(coupon_code=coupon_code, uuid=current_user.get_id()).all()

        for restriction in query:
            db.session.delete(restriction)

        db.session.commit()

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.String(40), nullable=False, primary_key=True)
    product_id = db.Column(db.String(8), db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer(), nullable=False)
    currency = db.Column(db.String(5), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    coupon = db.Column(db.String(50), nullable=True)
    payment_method = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), default='Pending Payment', nullable=False)
    expiry = db.Column(db.String(15), nullable=True)
    user = db.Column(db.String(25), db.ForeignKey('users.uuid'))
    # relationships
    payment = db.relationship('Payment', backref='order_payment', uselist=False, lazy=True)
    sold = db.relationship('Sold', backref='order_sold', lazy=True)

    def add(self, data) -> Union[bool, dict]:
        product = Product().query.filter_by(id=data.get('product_id')).first()
        
        if not product:
            return False

        user = User().fetch_user_supply_uuid(product.user)
        self.currency = user.settings.currency
        
        self.id = generate_string(8)
        self.product_id = product.id
        self.quantity = int(data.get('quantity'))
        
        if data.get('coupon_code') != '':
            coupon_check = Coupon().check_coupon(data)
            self.coupon = data.get('coupon_code')
            self.price = '%.2f' % ((float(product.price)) - (float(coupon_check) / 100 * float(product.price)) * int(self.quantity))
            Coupon().update_coupon_use(data.get('coupon_code'))
            
        else:
            self.price = product.price

        self.payment_method = data.get('payment_method')
        
        if data.get('email') != '':
            self.email = data.get('email')
        
        self.user = product.user
        self.expiry = timestamp(1800)
        
        db.session.add(self)
        db.session.commit()

        if self.payment_method == 'paypal':
            ## replace receiver in production env
            payment_create = create_paypal_order(self.currency, self.price, self.quantity, self.id, 'sb-zricq5204691@personal.example.com', product.name, product.id)
            Payment(id=self.id, payment_address=payment_create['address'], transaction_id=payment_create['transaction_id']).add()
        else:
            crypto_payment = create_coin_transaction(self.price, self.currency, self.payment_method)
            Payment(id=self.id, payment_address=crypto_payment['address'], transaction_id=crypto_payment['txn'], amount=crypto_payment['amount']).add()
        
        return {
            'id' : self.id,
            'payment_method' : self.payment_method,
            'payment_address' : payment_create['address']
        }

    def update(self):
        db.session.commit()

    def fetch_order(self, order_id) -> object:
        return self.query.filter_by(id=order_id).first()

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.String(40), db.ForeignKey('orders.id'), primary_key=True)
    transaction_id = db.Column(db.String(50), nullable=False)
    payment_address = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.String(20), nullable=True) ## this is only for Crypto payments

    def add(self):
        db.session.add(self)
        db.session.commit()

class Sold(db.Model):
    __tablename__ = 'sold_products'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(40), db.ForeignKey('orders.id'), nullable=False)
    item = db.Column(db.String(100), nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.String(40), primary_key=True)
    amount = db.Column(db.String(10), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), default="Anonymous")
    message = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=True)
    expiry = db.Column(db.String(15), nullable=True)
    timestamp = db.Column(db.String(15), nullable=True)
    user = db.Column(db.String(25), db.ForeignKey('users.uuid'))
    donation_payment = db.relationship('DonationPayment', backref='user_donations', uselist=False)

    def add(self, data, referrer) -> Union[bool, dict]:
        ''' insert donation record '''
        validate_donation_attempt = self.validate_donation_attempt(data)

        if False in validate_donation_attempt:
            return validate_donation_attempt
        
        self.id = generate_string(40)
        self.amount = "{:.2f}".format(float(data.get('amount')))
        self.payment_method = data.get('payment_method')
        
        if data.get('name') == '':
            self.name = data.get('Anonymous')
        else:
            self.name = data.get('name')
        
        if data.get('message') != '':
            self.message = data.get('message')
        
        self.expiry = timestamp(900)
        self.user = data.get('uuid')
        
        db.session.add(self)
        db.session.commit()

        task.update_donation_status.apply_async(args=[self.id], countdown=901)

        if self.payment_method == 'paypal':
            return DonationPayment().add_paypal_donation(user.settings.currency, self.id, self.amount, referrer)
        
        elif self.payment_method == 'stripe':
            return DonationPayment().add_stripe_donation(self.id, user.payment_methods.stripe, self.amount, user.settings.currency)
        
        else:
            return DonationPayment().add_crypto_donation(self.id, self.amount, user.settings.currency, self.payment_method)

    def validate_donation_attempt(self, data) -> list:
        ''' check that the donation can be made and the attempt is valid '''
        user = User().query.filter_by(uuid=data.get('uuid')).first()
        
        if not user:
            return [False, 'Something went wrong. Please try again']

        if not user.settings.donations:
            return [False, f'{user.username} is not currently accepting donations']

        if float(data.get('amount')) < float(user.settings.minimum_donation):
            return [False, f'The minimum donation amount you can make is {user.settings.currency}{user.settings.minimum_donation}']

        if not getattr(user.payment_methods, data.get('payment_method')):
            return [False, f'{request.form.get("payment_method").capitalize()} is no longer available. Please choose a different payment method']

    def cancel_donation(self, id) -> Union[None, str]:
        query = self.query.filter_by(id=id).first()
        
        if not query:
            return None
        
        query.status = 'Cancelled'
        db.session.commit()

        return User().query.filter_by(uuid=query.user).first().username
    
    def fetch_donation(self, donation_id) -> object:
        return self.query.filter_by(id=donation_id).first()

    def update(self):
        db.session.commit()

    def fetch_user_donations(self):
        return self.query.filter_by(user=current_user.get_id(), status='completed').paginate(per_page=12)

    def check_donation(donation_id):
        query = self.query.filter_by(id=donation_id).first()

    def validate_paypal_donation(self, donation_id, token) -> bool:
        query = self.check_donation(donation_id)

        if not query:
            flash['Something went wrong. Please try again']
            return False
        
        if query.donation_payment.transaction_id != token:
            flash['Something went wrong. Please try again']
            return False
        
        if not check_paypal_success(query.donation_payment.transaction_id):
            flash['Something went wrong. Please try again']
            return False

        query.status = 'completed'
        query.timestamp = timestamp(0)
        query.update()

        return True

    def validate_stripe_donation(self, donation_id, intent) -> bool:
        donation = self.fetch_donation(donation_id)
        intent = check_stripe_intent(intent)

        if (not intent) or (str(intent)['amount_received'] != str(donation.amount).replace('.', '')):
            flash['Something went wrong. Please try again']
            return False

        donation.status = 'completed'
        donation.timestamp = timestamp(0)
        donation.update()

        return True

    def validate_crypto_donation(self, donation_id, transaction_id) -> bool:
        check_transaction = check_coin_transaction(transaction_id)

        if check_transaction['result']['status_text'] != 'completed':
            return {
                'success':'True',
                'amount' : check_coin['result']['amountf'], 
                'amount_received' : check_coin['result']['receivedf'], 
                'confirmation' : check_coin['result']['recv_confirms']
            }

        return True

class DonationPayment(db.Model):
    __tablename__ = 'donation_payments'
    id = db.Column(db.String(40), db.ForeignKey('donations.id'), primary_key=True)
    transaction_id = db.Column(db.String(50), nullable=True)
    payment_address = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.String(20), nullable=True)

    def add_paypal_donation(self, currency, id, amount, referrer) -> Union[list, dict]:
        ''' method to handle paypal donations '''
        donation_payment_create = create_paypal_donation(currency, amount, id, '', referrer)
        
        if not donation_payment_create:
            return [False, 'Something went wrong. Please try again']
        
        self.id = id,
        self.transaction_id = donation_payment_create['transaction_id'],
        self.payment_address = donation_payment_create['payment_address'],
        self.amount = amount

        db.session.add(self)
        db.session.commit()

        return {
            'payment' : 'paypal', 
            'address' : donation_payment_create['payment_address'],
            'donation_id' : id,
            'amount' : amount
        }

    def add_stripe_donation(self, id, acc_id, price, currency) -> Union[list, dict]:
        ''' method to handle stripe donations '''
        donation_payment_create = create_donation_checkout(id, acc_id, price, currency)
        
        if not donation_payment_create:
            return [False, 'Something went wrong. Please try again'] ## Log into file
        
        self.id = id
        self.amount = price

        db.session.add(self)
        db.session.commit()

        return donation_payment_create
            
    def add_crypto_donation(self, id, amount, currency, payment_method) -> Union[list, dict]:
        self.id = id
        
        donation_payment_create = create_coin_transaction(amount, currency, payment_method)
        
        if not donation_payment_create:
            return [False, 'Something went wrong. Please try again']

        self.transaction_id = donation_payment_create['txn']
        self.payment_address = donation_payment_create['address']
        self.amount = donation_payment_create['amount']

        db.session.add(self)
        db.session.commit()

        return {
            'payment' : payment_method,
            'address' : donation_payment_create['address'],
            'donation_id' : id,
            'amount' : donation_payment_create['amount']
        }
    
    def add(self):
        db.session.add(self)

class Blacklist(db.Model):
    __tablename__ = 'blacklist'
    id = db.Column(db.Integer, primary_key=True)
    blacklist_type = db.Column(db.String(10), nullable=False)
    blocked_data = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(25), db.ForeignKey('users.uuid'))

    def add(self, data):
        self.user = current_user.get_id()
        self.blacklist_type = data.get('blacklist_type')
        self.blocked_data = data.get('blocked_data')
        
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def fetch_blacklist(self) -> object:
        return self.query.filter_by(user=current_user.get_id()).paginate(per_page=12)

    def remove_from_blacklist(self, blacklist_id):
        query = self.query.filter_by(id=blacklist_id, user=current_user.get_id()).first()

        if not query:
            return None

        query.delete()

        return query.id

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.String(10), nullable=False, primary_key=True)
    user_id = db.Column(db.String(25), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    order_id = db.Column(db.String(40), nullable=True)
    email = db.Column(db.String(255), nullable=False)
    ticket_created_timestamp = db.Column(db.String(10), default=timestamp(0), nullable=False)
    status = db.Column(db.String(20), default='Customer Message', nullable=False)
    ticket_message = db.relationship('TicketMessage', backref='ticket')

    def add(self, data, username):
        user = User().fetch_user_supply_username(username)
        self.id = generate_string(10)
        self.user_id = user.uuid
        self.subject = data.get('subject')
        self.email = data.get('email')

        if data.get('order_id') != '':
            self.order_id = data.get('order_id')

        db.session.add(self)
        db.session.commit()

        TicketMessage().add_customer_message(self.id, data.get('message'))
        
        task.ticket_created.apply_async(args=[self.email, data.get('message'), username, self.id])

        task.seller_new_ticket_notification.apply_async(args=[user.email])

    def fetch_ticket_by_id(self, ticket_id):
        return self.query.filter_by(id=ticket_id).first()

    def fetch_customer_ticket(self, username, email, ticket_id) -> Union[object, bool]:
        user = User().fetch_user_supply_username(username)
        return self.query.filter_by(email=email, user_id=user.uuid, id=ticket_id).first()

    def fetch_sellers_tickets_paginate(self):
        return self.query.filter_by(user_id=current_user.get_id()).paginate(per_page=12)

    def fetch_ticket_for_seller(self, ticket_id) -> Union[object, bool]:
        return self.query.filter_by(id=ticket_id, user_id=current_user.get_id()).first()

    def update_ticket_stats(self, ticket_id, status):
        ticket = self.query.filter_by(id=ticket_id).first()
        ticket.status = status
        db.session.commit()

    def close_ticket(self, ticket_id) -> bool:
        ticket = self.query.filter_by(id=ticket_id).first()
        if ticket.user_id != current_user.get_id():
            return False
        ticket.status = 'Closed'
        db.session.commit()
        return True

    def open_ticket(self, ticket_id) -> bool:
        ticket = self.query.filter_by(id=ticket_id).first()
        if ticket.user_id != current_user.get_id():
            return False
        ticket.status = 'Open'
        db.session.commit()
        return True

class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(10), db.ForeignKey('tickets.id'), nullable=False)
    message = db.Column(db.String(1000), nullable=True)
    message_timestamp = db.Column(db.String(10), nullable=True)
    reply = db.Column(db.String(1000), nullable=True)
    reply_timestamp = db.Column(db.String(10), nullable=True)
    last_update = db.Column(db.String(10), default=timestamp(0), nullable=False)

    def add_customer_message(self, ticket_id, message):
        self.ticket_id = ticket_id
        self.message = message
        self.message_timestamp = timestamp(0)
        Ticket().update_ticket_stats(ticket_id, 'Customer Message')
        
        db.session.add(self)
        db.session.commit()

    def add_reply(self, ticket_id, reply) -> Union[object, bool]:
        ticket = Ticket().fetch_ticket_for_seller(ticket_id)
        
        if not ticket_id:
            return False

        ticket_message = self.query.filter_by(ticket_id=ticket_id).first()
        
        if not ticket_message.reply:
            ticket_message.reply = reply
            ticket_message.reply_timestamp = timestamp(0)
            Ticket().update_ticket_stats(ticket_id, 'Replied')
            db.session.commit()

        else:
            self.ticket_id = ticket_id
            self.reply = reply
            self.reply_timestamp = timestamp(0)
            Ticket().update_ticket_stats(ticket_id, 'Replied')
            db.session.add(self)
            db.session.commit()
