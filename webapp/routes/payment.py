from webapp.models import User, PaymentMethod
from webapp.payments.stripe import stripe_setup, disconnect_account, account_query
from webapp.utils.login_decorator import login_required
from flask import Blueprint, redirect, url_for, flash, session

payment_bp = Blueprint("payments", __name__)

@payment_bp.route('/stripe/connect', methods=['GET'], subdomain='dashboard')
@login_required
def stripe_connect():
    setup = stripe_setup(User().fetch_user_logged_in.email)
    session['acc_id'] = setup[0]
    
    return redirect(setup[1])

@payment_bp.route('/stripe/connect/validate', methods=['GET'], subdomain='dashboard')
@login_required
def validate_stripe_connect():
    if PaymentMethod().fetch_user_payment_method.stripe:
        return redirect(url_for('dashboard.payment_methods'))

    if account_query(session['acc_id'])['charges_enabled']:
        return redirect(url_for('payments.stripe_success'))
    else:
        flash('Semething went wrong. Please try again later')
        return redirect(url_for('dashboard.payment_methods'))

@payment_bp.route('/stripe/connect/success', methods=['GET'], subdomain='dashboard')
@login_required
def stripe_success():
    PaymentMethod().update_stripe_acc(session['acc_id'])
    session.pop('acc_id')

    flash(['Stripe successfully linked'])
    return redirect(url_for('dashboard.payment_methods'))

@payment_bp.route('/stripe/disconnect', methods=['GET'], subdomain='dashboard')
@login_required
def disconnect_stripe():
    disconnect_account(PaymentMethod().remove_stripe_acc())
    flash(['Stripe Successfully Disconnected'])

    return redirect(url_for('dashboard.payment_methods'))
    
