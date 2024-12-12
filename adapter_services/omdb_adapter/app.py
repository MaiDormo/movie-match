import os
from flask import Flask, jsonify
from routes.omdb_routes import omdb_bp

app = Flask(__name__)

app.register_blueprint(omdb_bp)

@app.errorhandler(405)
def method_not_allowed(e):
    response = {
        "status": "error",
        "code": 405,
        "message": "Method not allowed"
    }
    return jsonify(response), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))