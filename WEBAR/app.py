from flask import Flask, send_from_directory, render_template
import os
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, static_folder='static', template_folder='templates')

# Критично важливо для роботи з ngrok
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.route('/')
def home():
    return render_template('scanner.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Важливо: використовуйте порт 5000 або 8000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False для ngrok