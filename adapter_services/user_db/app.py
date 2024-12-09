import os
from flask import Flask
from routes.user_routes import user_bp

app = Flask(__name__)

app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))