from flask import Flask, g, jsonify, request
from http import HTTPStatus
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__)

# deploy
mongo_url = os.getenv("MONGO_URL")
mongo_database = os.getenv("MONGO_DATABASE")
mongo_collection = os.getenv("MONGO_COLLECTION")

# test
# mongo_url = "mongodb://mongo:CoujcuIauUPtOwJjPZybLvVCbQFGbtVA@crossover.proxy.rlwy.net:31947"
# mongo_database = "test"
# mongo_collection = "alarm"

mongo_full_url = str(mongo_url) + "/" + str(mongo_database) + "?authSource=admin"
print("connection uri:", mongo_full_url)

client = MongoClient(mongo_full_url)

def get_db():
    if 'db' not in g:
        g.db = client[mongo_database]
    return g.db

def get_collection():
    return get_db()[mongo_collection]

@app.before_request
def open_connection():
    g.db = get_db()
    g.collection = get_collection()
    
@app.teardown_appcontext
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

@app.route("/test", methods=['GET'])
def get():
    response = list(g.collection.find({}, {"_id": 0}))
    return jsonify(response)
    
@app.route("/reportAssign/recvAlarm", methods=['POST'])
def recvAlarm():
    result = g.collection.insert_one(request.get_json())
    response = {"inserted_id": str(result.inserted_id)}
    return jsonify(response), HTTPStatus.CREATED

@app.route("/reportAssign/recvTransferState", methods=['POST'])
def recvTransferState():
    result = g.collection.insert_one(request.get_json())
    response = {"inserted_id": str(result.inserted_id)}
    return jsonify(response), HTTPStatus.CREATED

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
