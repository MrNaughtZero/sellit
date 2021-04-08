from webapp.forms import PurchaseProduct
from webapp.models import Order, Coupon, User, Product, Attachment
from webapp.payments.paypal import capture_paypal_order, get_paypal_order
from webapp.utils.uploads import download_file
from webapp.utils.tasks import leave_feedback
from flask import Blueprint, request, redirect, url_for, flash, render_template, get_flashed_messages, abort, Response
from os import environ

order_bp = Blueprint("order", __name__)

@order_bp.route('/create/order', methods=['POST'])
def create_order() -> redirect:
    form = PurchaseProduct()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(request.referrer)

    if request.form.get('coupon') != '':
        if not Coupon().check_coupon(request.form):
            flash(['Coupon is invalid. Please try again'])

    new_order = Order().add(request.form)

    if not new_order:
        flash(['Something went wrong. Please try again'])
        return redirect(request.referrer)

    if new_order['payment_method'] == 'paypal':
        ### redirect to the paypal page to pay
        return redirect(new_order['payment_address'])
    
    return redirect(url_for('order.track_order', order_id=new_order))

@order_bp.route('/order/<string:order_id>', methods=['GET'])
def track_order(order_id) -> render_template:
    fetch_order = Order().fetch_order(order_id)
    
    if not fetch_order:
        return abort(404)
    
    return render_template('/shop/order.html', order=fetch_order, flashed_message=get_flashed_messages(), user=User().fetch_user_supply_uuid(fetch_order.user), product=Product().fetch_product(fetch_order.product_id, fetch_order.user))

@order_bp.route('/order/payment/complete/<string:order_id>', methods=['GET'])
def payment_complete(order_id):
    ## this needs to be rewritten to take into account stripe and crypto payments
    token = request.args.get('token')
    payer_id = request.args.get('PayerID')
    
    order = Order().fetch_order(order_id)
    
    if not order:
        return abort(404)
    
    if order.payment.transaction_id != token:
        return abort(404)
    
    if order.status != 'Completed':
        capture_paypal_order(token)
        check_order = get_paypal_order(token)
    
        if check_order['payment_status'] == 'COMPLETED':
            order.status = 'Completed'

        if not order.email:
            order.email = check_order['buyer_email']
        
        order.update()

        deliver_goods = Product().deliver_product(order.product_id, order_id, order.quantity, order.email)
        leave_feedback.apply_async()
            
    return redirect(url_for('order.track_order', order_id=order_id))

@order_bp.route('/order/<string:order_id>/download/<string:attachment_id>', methods=['GET'])
def download_attachment(order_id, attachment_id):
    order = Order().fetch_order(order_id)
    
    if (not order) or (order.status != 'Completed'):
        return abort(404)

    attachment = Attachment().fetch_attachment(attachment_id)
    fetch_file = download_file(attachment.attachment_filename, environ.get('AWS_ATTACHMENTS'))
    
    return Response(
            fetch_file['file'],
            mimetype='text/plain',
            headers={"Content-Disposition": f"attachment;filename={attachment.original_attachment_filename}"}
    )

    
    
    
    
    
        
    
    