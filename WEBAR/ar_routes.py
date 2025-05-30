from flask import Blueprint, render_template, send_from_directory
import os

webar_bp = Blueprint('webar', __name__,
                    template_folder='templates',
                    static_folder='static')

@webar_bp.route('/')
def home():
    return render_template('scanner.html')

@webar_bp.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)