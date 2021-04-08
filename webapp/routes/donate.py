from webapp.utils.tasks import new_donation_email
from webapp.utils.tools import convert_currency_symbol, generate_string
from webapp.forms import MakeDonationForm
from webapp.models import User, Donation
from flask import Blueprint, abort, render_template, flash, get_flashed_messages, jsonify, request, redirect, url_for, session

donate_bp = Blueprint("donate", __name__)

@donate_bp.route('/@<string:username>/donate', methods=['GET'])
def donate(username):
    user = User().fetch_user_supply_username(username)
    
    if not user:
        return abort(404)
    
    ## User can only access the pay donation page before they've paid. Then the session is removed
    if (session.get('donation_tracker')) and (session['donation_tracker'] > 2):
        session.pop('donation_session')

    return render_template('/shop/donate.html', user=user, form=MakeDonationForm(), flashed_message=get_flashed_messages())

@donate_bp.route('/donation/create/payment', methods=['POST'])
def create_donation() -> jsonify:
    form = MakeDonationForm()
    
    if not form.validate_on_submit():
        return jsonify({'Success':'Failure', 'error' : list(form.errors.values())[0]}), 400

    session['donation_session'] = generate_string(40)

    add_donation = Donation().add(request.form, request.referrer)
    
    if not all(add_donation):
        return jsonify({'Success':'Failure', 'error' : str(add_donation[1])}), 400

    session['donation_tracker'] = 1
    
    return jsonify({'success':'True', 'Payment':str(add_donation['payment']), 'address':str(add_donation['address']), 'donation_id' : add_donation['donation_id'], 'amount' : add_donation['amount']}), 200

@donate_bp.route('/donation/check/<string:donation_id>', methods=['GET'])
def donation_check(donation_id):
    
    if not session.get('donation_session'):
        return abort(404)

    donation = Donation().fetch_donation(donation_id)
    
    if not donation:
        return abort(404)
    
    user = User().query.filter_by(uuid=donation.user).first()

    if request.args.get('payment_timeout'):
        flash(['Payment timeout. Donation cancelled.'])
        return redirect(url_for('donate.donate', username=user.username)), 302

    if donation.status == 'Completed':
        flash([f'You successfully donated {convert_currency_symbol(user.settings.currency)}{float(donation.amount):.2f} to {user.username}'])
        return redirect(url_for('donate.donate', username=user.username))

    if donation.payment_method == 'paypal':
       validated_paypal_donation = Donation().validate_paypal_donation(donation_id)
       if not validated_paypal_donation:
           return redirect(url_for('donate.donate', username=user.username))
            
    if donation.payment_method == 'stripe':
        stripe_payment = Donation().validate_stripe_donation(donation_id, request.args.get('intent'))
        
        if not stripe_payment:
            return redirect(url_for('donate.donate', username=user.username))

    else:
        check_crypto_transactions = Donation().validate_crypto_donation(donation.donation_payment.transaction_id)
        
        if not check_crypto_transactions:
            return jsonify(check_crypto_transactions)

        else:
            session['donation_tracker'] =+1

    new_donation_email.apply_async(args=[user.email, f'{convert_currency_symbol(user.settings.currency)}{donation.amount}'])

    flash([f'You successfully donated {convert_currency_symbol(user.settings.currency)}{float(donation.amount):.2f} to {user.username}'])
    return redirect(url_for('donate.donate', username=user.username)), 302
        
@donate_bp.route('/donation/cancel/<string:donation_id>', methods=['GET'])
def cancel_donation(donation_id):
    cancel_donation = Donation().cancel_donation(donation_id)
    
    if not cancel_donation:
        return abort(404)
    
    flash(['Donation Cancelled'])
    return redirect(url_for('donate.donate', username=cancel_donation))