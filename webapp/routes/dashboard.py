from webapp.utils.login_decorator import login_required
from webapp.utils.uploads import download_file
from webapp.utils.regex import email_regex, ip_regex
from webapp.forms import SettingsForm, ProductForm, CategoryForm, AttachmentForm, CouponForm, BlacklistForm, SecurityForm, PaymentForm, DonationSettingsForm, TicketReply, SettingsNotificationsForm
from webapp.models import User, Setting, Category, Product, Attachment, Coupon, Blacklist, ProductCategory, PaymentMethod, Donation, ProductItem, Ticket, TicketMessage, EmailNotification, Order
from flask import Blueprint, render_template, url_for, redirect, request, flash, get_flashed_messages, abort, Response
from flask_login import current_user
from os import environ
from typing import Union

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route('/', methods=['GET'], subdomain='dashboard')
@login_required
def home() -> render_template:
    return render_template('/dashboard/dashboard.html')

@dashboard_bp.route('/settings', methods=['GET'], subdomain='dashboard')
@login_required
def settings() -> render_template:
    user = User().fetch_user_logged_in()
    
    form = SettingsForm()
    form.username.data = user.username
    form.email.data = user.email

    if user.settings.tawk_key:
        form.tawk_key.data = user.settings.tawk_key

    form.currency.data = user.settings.currency
    form.timezone.data = user.settings.timezone
    
    return render_template('/dashboard/settings.html', form=form, flashed_message=get_flashed_messages(), avatar=user.avatar.avatar_filename)

@dashboard_bp.route('/settings/update', methods=['POST'], subdomain='dashboard')
@login_required
def update_settings() -> redirect:
    form = SettingsForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.settings'))

    Setting().update(request)
    
    flash(['Settings updated successfully'])
    return redirect(url_for('dashboard.settings'))

@dashboard_bp.route('/settings/security', methods=['GET'], subdomain='dashboard')
@login_required
def security_settings() -> render_template:
    return render_template('/dashboard/security.html', form=SecurityForm(), flashed_message=get_flashed_messages())

@dashboard_bp.route('/settings/security/update', methods=['POST'], subdomain='dashboard')
@login_required
def security_settings_update() -> render_template:
    form = SecurityForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.security_settings'))

    if not User().update_password(request.form.get('current_password'), request.form.get('password')):
        flash(['Incorrect Password. Please try again'])
        return redirect(url_for('dashboard.security_settings'))

    flash(['Password successfully updated'])
    return redirect(url_for('dashboard.security_settings'))

@dashboard_bp.route('/settings/payment/methods', methods=['GET'], subdomain='dashboard')
@login_required
def payment_methods() -> render_template:
    form = PaymentForm()
    user = User().fetch_user_logged_in()
    
    form.paypal.data = user.payment_methods.paypal or ''
    form.paypal_delivery.data = user.payment_methods.paypal_delivery or ''
    form.BTC.data = user.payment_methods.BTC or ''
    form.ETH.data = user.payment_methods.ETH or ''
    form.LTC.data = user.payment_methods.LTC or ''

    return render_template('/dashboard/payment-methods.html', form=form, user=user, flashed_message=get_flashed_messages())

@dashboard_bp.route('/settings/payment/methods/submit', methods=['POST'], subdomain='dashboard')
@login_required
def payment_methods_update() -> redirect:
    form = PaymentForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.payment_methods'))

    PaymentMethod().update_payment_methods(request.form)

    flash(['Payment Methods successfully updated'])
    return redirect(url_for('dashboard.payment_methods'))

@dashboard_bp.route('/settings/notifications', methods=['GET'], subdomain='dashboard')
@login_required
def notification_settings():
    form = SettingsNotificationsForm()
    notification = EmailNotification().fetch_notification_settings(current_user.get_id())
    
    form.new_order.checked = notification.new_order
    form.new_donation.checked = notification.new_donation
    form.new_feedback.checked = notification.new_feedback
    form.new_support_ticket.checked = notification.new_support_ticket
    form.support_ticket_reply.checked = notification.support_ticket_reply

    return render_template('/dashboard/settings-notification.html', form=form)

@dashboard_bp.route('/settings/notifications/update', methods=['POST'], subdomain='dashboard')
@login_required
def update_notification_settings():
    if not EmailNotification().update(request.form):
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('dashboard.notification_settings'))

    flash(['Settings successfully updated'])
    return redirect(url_for('dashboard.notification_settings'))

@dashboard_bp.route('/donations', methods=['GET'], subdomain='dashboard')
@login_required
def donations() -> render_template:
    return render_template('/dashboard/donations.html', user=User().fetch_user_logged_in(), form=DonationSettingsForm(), flashed_message=get_flashed_messages(), donations=Donation().fetch_user_donations())

@dashboard_bp.route('/donations/enable', methods=['GET'], subdomain='dashboard')
@login_required
def enable_donations() -> redirect:
    Setting().donation_toggle(True)
    return redirect(url_for('dashboard.donations'))

@dashboard_bp.route('/donations/disable', methods=['GET'], subdomain='dashboard')
@login_required
def disable_donations() -> redirect:
    Setting().donation_toggle(None)
    return redirect(url_for('dashboard.donations'))

@dashboard_bp.route('/donations/update', methods=['POST'], subdomain='dashboard')
@login_required
def update_donation_settings() -> redirect:
    form = DonationSettingsForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.donations'))
    
    Setting().update_minimum_amount(request.form)
    
    flash(['Donation settings updated'])
    return redirect(url_for('dashboard.donations'))

@dashboard_bp.route('/products', methods=['GET'], subdomain='dashboard')
@login_required
def products() -> render_template:
    return render_template('/dashboard/products.html', flashed_message=get_flashed_messages(), prods=Product().fetch_user_products())

@dashboard_bp.route('/product/create', methods=['GET'], subdomain='dashboard')
@login_required
def create_product() -> render_template:
    form = ProductForm()
    attachments = Attachment().fetch_user_attachments()

    for item in Category().fetch_user_categories():
        form.categories.choices.append([item.category_name, item.category_name])

    for item in attachments:
        form.attachment_file.choices.append([item.attachment_filename, item.original_attachment_filename])
    
    return render_template('/dashboard/create-product.html', form=form, flashed_message=get_flashed_messages(), attachments=attachments)

@dashboard_bp.route('/product/create/submit', methods=['POST'], subdomain='dashboard')
@login_required
def submit_new_product() -> redirect:
    form = ProductForm()
    attachments = Attachment().fetch_user_attachments()
    
    for item in Category().fetch_user_categories():
        form.categories.choices.append([item.category_name, item.category_name])

    for item in attachments:
        form.attachment_file.choices.append([item.attachment_filename, item.original_attachment_filename])
        
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.create_product'))
   
    Product().add(request)
    
    flash(['Product Successfully Created'])
    return redirect(url_for('dashboard.products'))

@dashboard_bp.route('/product/edit/<string:product_id>', methods=['GET'], subdomain='dashboard')
@login_required
def edit_product(product_id):
    product = Product().fetch_product(product_id, current_user.get_id())
    form = ProductForm()
    
    for item in Category().fetch_user_categories():
        form.categories.choices.append([item.category_name, item.category_name])

    for item in Attachment().fetch_user_attachments():
        form.attachment_file.choices.append([item.attachment_filename, item.original_attachment_filename])
    
    if not product:
        flash(['Something went wrong. Please try again later'])
        return redirect(url_for('dashboard.products'))

    form.product_name.data = product.name
    
    if product.product_type == 'item':
        linked_product_items = ProductItem().fetch_active_product_items(product.product_items)
        form.items.data =  ''.join(linked_product_items)

    else:
        form.attachment_file.data = product.product_attachment.attachment_filename
        form.stock.data = product.stock

    form.price.data = float(product.price)

    return render_template('/dashboard/edit-product.html', product=product, form=form, flashed_message=get_flashed_messages(), attachments=Attachment().fetch_user_attachments())

@dashboard_bp.route('/product/edit/<string:product_id>/submit', methods=['POST'], subdomain='dashboard')
@login_required
def update_product(product_id):
    form = ProductForm()
    attachments = Attachment().fetch_user_attachments()
    
    for item in Category().fetch_user_categories():
        form.categories.choices.append([item.category_name, item.category_name])

    for item in attachments:
        form.attachment_file.choices.append([item.attachment_filename, item.original_attachment_filename])
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.edit_product', product_id=product_id))
    
    if not Product().update(request, product_id):
        flash(['Something went wrong. Please try again later'])
        return redirect(url_for('dashboard.products'))

    flash(['Product Successfully Updated'])
    return redirect(url_for('dashboard.edit_product', product_id=product_id))

@dashboard_bp.route('/product/delete/<string:product_id>', methods=['GET'], subdomain='dashboard')
@login_required
def delete_product(product_id) -> redirect:
    query = Product().fetch_product(product_id, current_user.get_id())
    
    if not query:
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('dashboard.products'))
    
    Product().delete(product_id)

    flash(['Product Successfully deleted'])
    return redirect(url_for('dashboard.products'))

@dashboard_bp.route('/coupons', methods=['GET'], subdomain='dashboard')
@login_required
def coupons() -> render_template:
    form = CouponForm()
    
    for item in Product().fetch_user_products():
        form.product_list.choices.append([item.id, item.name])

    return render_template('/dashboard/coupons.html', flashed_message=get_flashed_messages(), form=form, all_coupons=Coupon().get_all_coupons())

@dashboard_bp.route('/coupons/create', methods=['GET'], subdomain='dashboard')
@login_required
def create_coupon() -> render_template:
    form = CouponForm()
    
    for item in Product().fetch_user_products():
        form.product_list.choices.append([item.id, item.name])
    
    return render_template('/dashboard/create-coupon.html', form=form)

@dashboard_bp.route('/coupons/create/submit', methods=['POST'], subdomain='dashboard')
@login_required
def submit_coupon() -> redirect:
    form = CouponForm()
    
    for item in Product().fetch_user_products():
        form.product_list.choices.append([item.id, item.name])
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.coupons'))

    if not Coupon().add_coupon(request.form):
        flash(['Coupon already exists. Please choose a different coupon code.'])
        return redirect(url_for('dashboard.coupons'))

    flash(['Coupon successfully added'])
    return redirect(url_for('dashboard.coupons'))

@dashboard_bp.route('/coupon/delete/<string:coupon_id>', methods=['GET'], subdomain='dashboard')
@login_required
def delete_coupon(coupon_id) -> redirect:
    if not Coupon().delete_coupon(coupon_id):
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('dashboard.coupons'))
    
    flash(['Coupon Successfully Deleted'])
    return redirect(url_for('dashboard.coupons'))

@dashboard_bp.route('/coupon/<string:coupon_id>/edit', methods=['GET'], subdomain='dashboard')
@login_required
def edit_coupon(coupon_id) -> Union[redirect, render_template]:
    coupon = Coupon().fetch_coupon(coupon_id)

    coupon_form = Coupon().prefill_coupon_values(CouponForm(), request.form, coupon_id)
    
    if not coupon:
        flash['Something went wrong. Please try again']
        return redirect(url_for('dashboard.coupons'))

    return render_template('/dashboard/edit-coupon.html', coupon=coupon, form=coupon_form)

@dashboard_bp.route('/coupon/<string:coupon_id>/update', methods=['POST'], subdomain='dashboard')
def update_coupon(coupon_id) -> redirect:
    for item in Product().fetch_user_products():
        form.product_list.choices.append([item.id, item.name])

@dashboard_bp.route('/orders', methods=['GET'], subdomain='dashboard')
@login_required
def orders() -> render_template:
    return render_template('/dashboard/orders.html', orders=Order().fetch_orders(), user=User().fetch_user_logged_in())

@dashboard_bp.route('/categories', methods=['GET'], subdomain='dashboard')
@login_required
def categories() -> render_template:
    return render_template('/dashboard/categories.html', flashed_message=get_flashed_messages(), cats=Category().fetch_user_categories_pagination())

@dashboard_bp.route('/categories/create', methods=['GET'], subdomain='dashboard')
@login_required
def create_category():
    form = CategoryForm()
    
    for item in Product().fetch_user_products():
        form.linked_products.choices.append([item.id, item.name])
    
    return render_template('/dashboard/create-category.html', form=form)

@dashboard_bp.route('/categories/create/submit', methods=['POST'], subdomain='dashboard')
@login_required
def add_category() -> redirect:
    form = CategoryForm()

    for item in Product().fetch_user_products():
        form.linked_products.choices.append([item.id, item.name])
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.categories'))

    new_category = Category().add(request.form)

    if not new_category:
        flash(['Category already exists'])
        return redirect(url_for('dashboard.categories'))

    flash(['Category Successfully Added'])
    return redirect(url_for('dashboard.categories'))

@dashboard_bp.route('/category/edit/<string:category_id>', methods=['GET'], subdomain='dashboard')
@login_required
def edit_category(category_id) -> render_template:
    form = CategoryForm()
    category = Category().fetch_category_by_id(category_id)
    
    if not cat:
        return abort(404)

    form.linked_products.data = []
    
    for item in Product().fetch_user_products:
        form.linked_products.choices.append([item.id, item.name])
        for product_cat in ProductCategory().fetch_linked_product_categories(item.id):
            if product_cat.category_name == category.category_name:
                form.linked_products.data.append(item.id)

    form.name.data = cat.category_name
    
    return render_template('/dashboard/edit-category.html', form=form, category=category)

@dashboard_bp.route('/categories/<string:category_id>/update', methods=['POST'], subdomain='dashboard')
@login_required
def update_category(category_id) -> redirect:
    category = Category().fetch_category_by_id(category_id)
    
    if not category:
        return abort(404)
    
    if not Category().update(category_id, request.form):
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('dashboard.edit_category', category_id=category_id))

    flash(['Category Successfully updated'])
    return redirect(url_for('dashboard.categories'))

@dashboard_bp.route('/categories/delete/<string:category_id>', methods=['GET'], subdomain='dashboard')
@login_required
def remove_category(category_id) -> redirect:
    remove = Category().remove_category(category_id)

    if not remove:
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('dashboard.categories'))

    ProductCategory().remove_all_categories(remove)

    flash(['Category Successfully Deleted'])
    return redirect(url_for('dashboard.categories'))

@dashboard_bp.route('/analytics', methods=['GET'], subdomain='dashboard')
@login_required
def analytics() -> render_template:
    return render_template('/dashboard/analytics.html')

@dashboard_bp.route('/attachments', methods=['GET'], subdomain='dashboard')
@login_required
def attachments() -> render_template:
    return render_template('/dashboard/attachments.html', form=AttachmentForm(), attachments=Attachment().fetch_user_attachments_pagination(), flashed_message=get_flashed_messages(), user=User().fetch_user_logged_in())

@dashboard_bp.route('/attachments/upload', methods=['POST'], subdomain='dashboard')
@login_required
def upload_attachment() -> redirect:
    form = AttachmentForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.attachments'))

    if Attachment().check_if_already_exists(request.files['attachment_upload'].filename):
        flash(['This attachment has already been uploaded. Please rename the attachment, or upload a different attachment'])
        return redirect(url_for('dashboard.attachments'))

    if not Attachment().check_attachment_size(request.files['attachment_upload']):
        flash(['Attachment too large. Maximum file size is 5MB'])
        return redirect(url_for('dashboard.attachments'))
    
    upload = Attachment().upload_attachment(request.files['attachment_upload'])
    
    flash(['Attachment Successfully Uploaded'])
    return redirect(url_for('dashboard.attachments'))

@dashboard_bp.route('/attachments/delete/<string:attachment_id>', methods=['GET'], subdomain='dashboard')
@login_required
def remove_attachment(attachment_id) -> redirect:
    attachment_file = Attachment().fetch_attachment(attachment_id)

    if not attachment_file:
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('dashboard.attachments'))

    if Attachment().check_if_linked_to_product(attachment_file.id):
        flash(["You can't delete an attachment whilst it belongs to an active product"])
        return redirect(url_for('dashboard.attachments'))

    Attachment().remove_attachment(attachment_id)
    
    flash(['Attachment Successfully Deleted'])
    return redirect(url_for('dashboard.attachments'))

@dashboard_bp.route('/attachment/download/<string:attachment_id>', methods=['GET'], subdomain='dashboard')
@login_required
def download_attachment(attachment_id) -> Response:
    attachment = Attachment().fetch_attachment(attachment_id)
    
    if not attachment:
        return abort(404)

    download_response = download_file(attachment.attachment_name, environ.get('AWS_ATTACHMENTS'))
    
    return Response(
            download_response['file'],
            mimetype='text/plain',
            headers={"Content-Disposition": f"attachment;filename={download_response['original_filename']}"}
    )

@dashboard_bp.route('/reviews', methods=['GET'], subdomain='dashboard')
@login_required
def reviews() -> render_template:
    return render_template('/dashboard/reviews.html', orders=Order().fetch_orders())

@dashboard_bp.route('/blacklist', methods=['GET'], subdomain='dashboard')
@login_required
def blacklist() -> render_template:
    return render_template('/dashboard/blacklist.html', form=BlacklistForm(), flashed_message=get_flashed_messages(), blacklist=Blacklist().fetch_blacklist())

@dashboard_bp.route('/blacklist/create', methods=['GET'], subdomain='dashboard')
@login_required
def create_blacklist() -> render_template:
    return render_template('/dashboard/add-blacklist.html', form=BlacklistForm())

@dashboard_bp.route('/blacklist/create/submit', methods=['POST'], subdomain='dashboard')
@login_required
def add_to_blacklist() -> redirect:
    form = BlacklistForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.blacklist'))

    if request.form.get('blacklist_type') == 'email':
        if not email_regex(request.form.get('blocked_data')):
            flash(['Please enter a valid email'])
            return redirect(url_for('dashboard.blacklist'))
    else:
        if not ip_regex(request.form.get('blocked_data')):
            flash(['Please enter a valid IP Address'])
            return redirect(url_for('dashboard.blacklist'))

    Blacklist().add(request.form)
    
    flash(['Blocked Data Successfully Added'])
    return redirect(url_for('dashboard.blacklist'))

@dashboard_bp.route('/blacklist/remove/<string:blocked_id>', methods=['GET'], subdomain='dashboard')
@login_required
def remove_blacklist(blocked_id) -> redirect:    
    if not Blacklist().remove_from_blacklist(blocked_id):
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('dashboard.blacklist'))

    flash(['Data successfully removed from the Blacklist'])
    return redirect(url_for('dashboard.blacklist'))

@dashboard_bp.route('/tickets', methods=['GET'], subdomain='dashboard')
@login_required
def tickets():
    return render_template('/dashboard/tickets.html', tickets=Ticket().fetch_sellers_tickets_paginate())

@dashboard_bp.route('/ticket/<string:ticket_id>', methods=['GET'], subdomain='dashboard')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket().fetch_ticket_for_seller(ticket_id)
    if not ticket_id:
        return abort(404)
    return render_template('/dashboard/view-ticket.html', ticket=ticket, form=TicketReply())

@dashboard_bp.route('/ticket/<string:ticket_id>/submit', methods=['POST'], subdomain='dashboard')
def reply_to_ticket(ticket_id):
    form = TicketReply()

    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('dashboard.view_ticket', ticket_id=ticket_id))

    TicketMessage().add_reply(ticket_id, request.form.get('message'))

    flash(['Message Sent'])
    return redirect(url_for('dashboard.view_ticket', ticket_id=ticket_id))

@dashboard_bp.route('/ticket/<string:ticket_id>/close', methods=['GET'], subdomain='dashboard')
def close_open_ticket(ticket_id):
    Ticket().close_ticket(ticket_id)
    return redirect(url_for('dashboard.tickets'))

@dashboard_bp.route('/ticket/<string:ticket_id>/open', methods=['GET'], subdomain='dashboard')
def open_closed_ticket(ticket_id):
    Ticket().open_ticket(ticket_id)
    return redirect(url_for('dashboard.view_ticket', ticket_id=ticket_id))
