from flask import Flask, g, jsonify, request
from http import HTTPStatus
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
mongo_database = os.getenv("MONGO_DATABASE")
mongo_collection = os.getenv("MONGO_COLLECTION")

client = MongoClient(mongo_uri)

def get_db():
    if 'db' not in g:
        g.db = client[mongo_database]
    return g.db

def get_collection():
    return get_db()[mongo_collection]

# @app.before_request
def open_connection():
    g.db = get_db()
    g.collection = get_collection()

# @app.teardown_appcontext
def close_connection(exception):
    g.pop('db', None)
    g.pop('collection', None)

@app.errorhandler(Exception)
def handle_error(ex):
    print("Exception type:", type(ex).__name__)
    return jsonify({"error": str(ex)})

@app.errorhandler(HTTPException)
def handle_error(ex):
    print("Exception type:", type(ex).__name__)
    return jsonify({"error": str(ex.description)}), ex.code

@app.route("/reportAssign/recvAlarm", methods=['POST'])
def recvAlarm():
    response = g.collection.insert_one(request.get_json())
    return jsonify(response), HTTPStatus.CREATED

@app.route("/reportAssign/recvTransferState", methods=['POST'])
def recvTransferState():
    response = g.collection.insert_one(request.get_json())
    return jsonify(response), HTTPStatus.CREATED

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=12345)
