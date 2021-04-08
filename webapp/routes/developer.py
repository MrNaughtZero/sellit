from flask import Flask, Blueprint, render_template

developer_bp = Blueprint("developer", __name__)

@developer_bp.route('/', methods=['GET'], subdomain='developer')
def index():
    return render_template('/developer/index.html')