from webapp.forms import PurchaseProduct, StoreContact, TicketReply, FeedbackForm
from webapp.models import User, Product, Coupon, Ticket, TicketMessage, Order
import webapp.utils.tasks as task
from flask import Blueprint, abort, render_template, get_flashed_messages, jsonify, request, flash, get_flashed_messages, redirect, url_for, session

shop_bp = Blueprint("shop", __name__)

@shop_bp.route('/@<string:username>', methods=['GET'])
def shop(username):
    user = User().fetch_user_supply_username(username)
    
    if not user:
        return abort(404)
    
    return render_template('/shop/shop.html', user=user, flashed_message=get_flashed_messages())

@shop_bp.route('/@<string:username>/category/<string:category>', methods=['GET'])
def shop_category(username, category):
    user = User().fetch_user_supply_username(username)

    if not user:
        return abort(404)

    return render_template('/shop/shop-category.html', user=user, category=category.replace('-', ' '))

@shop_bp.route('/@<string:username>/contact', methods=['GET'])
def open_ticket(username):
    user = User().fetch_user_supply_username(username)

    if not user:
        return abort(404)

    return render_template('/shop/contact.html', user=user, form=StoreContact(), flashed_message=get_flashed_messages())

@shop_bp.route('/@<string:username>/contact/submit', methods=['POST'])
def submit_ticket(username):
    form = StoreContact()

    user = User().fetch_user_supply_username(username)

    if not user:
        return abort(404)

    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('shop.open_ticket', username=username))

    Ticket().add(request.form, username)

    flash(['Your message has been sent.'])
    return redirect(url_for('shop.shop', username=username))

@shop_bp.route('/@<string:username>/ticket/<string:email>/<string:ticket_id>', methods=['GET'])
def customer_ticket(username, email, ticket_id):
    ticket = Ticket().fetch_customer_ticket(username, email, ticket_id)
    user = User().fetch_user_supply_uuid(ticket.user_id)

    if not ticket:
        return abort(404)

    return render_template('/shop/view-ticket.html', ticket=ticket, user=user, form=TicketReply(), flashed_message=get_flashed_messages())

@shop_bp.route('/ticket/<string:ticket_id>/submit', methods=['POST'])
def customer_ticket_reply(ticket_id):
    if Ticket().fetch_ticket_by_id(ticket_id) == 'Closed':
        return abort(404)
    
    form = TicketReply()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(request.referrer)
    
    TicketMessage().add_customer_message(ticket_id, request.form.get('message'))
   
    return redirect(request.referrer)

@shop_bp.route('/@<string:username>/<string:product_id>', methods=['GET'])
def product_page(username, product_id):
    form = PurchaseProduct()
    
    user = User().fetch_user_supply_username(username)
    product = Product().fetch_product(product_id, user.uuid)
    
    if product.user != user.uuid:
        return abort(404)

    form.product_id.data = product.id
    
    return render_template('/shop/product-page.html', product=product, user=user, form=form, flashed_message=get_flashed_messages())

@shop_bp.route('/product/coupon/check', methods=['POST'])
def check_coupon():
    check = Coupon().check_coupon(request.form)
    if not check:
        return jsonify({'Success':'False'}), 400
    else:
        return jsonify({'Success':'True', 'Discount':f'0.{check}'}), 200

@shop_bp.route('/order/<string:order_id>/<string:email>/<string:order_hash>/feedback', methods=['GET'])
def feedback_hash(order_id, email, order_hash):
    order = Order().query.filter_by(id=order_id, email=email, order_hash=order_hash).first()
    
    if not order:
        return abort(404)

    session['order_hash'] = order.order_hash
    return redirect(url_for('shop.leave_feedback', order_id=order_id, username=User().fetch_user_supply_uuid(order.user).username))

@shop_bp.route('/@<string:username>/order/<string:order_id>/feedback', methods=['GET'])
def leave_feedback(username, order_id):
    order = Order().fetch_order(order_id)

    if not order:
        return abort(404)
    
    if (not session.get('order_hash')) or (session['order_hash'] != order.order_hash):
        Order().update_order_hash(order_id, username)
        
        flash(['Please check your email. You can leave feedback by clicking the link in your email'])
        return redirect(url_for('shop.shop', username=username))

    return render_template('/shop/feedback.html', user=User().fetch_user_supply_username(username), form=FeedbackForm())
