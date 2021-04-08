from flask import Flask, Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('/main/index.html')

@main_bp.route('/features', methods=['GET'])
def features():
    return render_template('/main/features.html')

@main_bp.route('/pricing', methods=['GET'])
def pricing():
    return render_template('/main/pricing.html')