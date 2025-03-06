from flask import Flask, g, jsonify, request
from http import HTTPStatus
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__)

mongo_url = ${{MongoDB.MONGO_URL}}
# mongo_url = "mongodb://mongo:CoujcuIauUPtOwJjPZybLvVCbQFGbtVA@crossover.proxy.rlwy.net:31947"
mongo_database = ${{MongoDB.MONGO_DATABASE}}
# mongo_database = "test"
mongo_collection = ${{MongoDB.MONGO_COLLECTION}}
# mongo_collection = "alarm"
mongo_full_url = str(mongo_url) + "/" + str(mongo_database) + "?authSource=admin"
print("mongo_full_url:", mongo_full_url)

client = MongoClient(mongo_full_url)
# client = MongoClient(f"mongodb://mongo:CoujcuIauUPtOwJjPZybLvVCbQFGbtVA@crossover.proxy.rlwy.net:31947/test?authSource=admin")

def get_db():
    if 'db' not in g:
        g.db = client[str(mongo_database)]
    return g.db

def get_collection():
    return get_db()[str(mongo_collection)]

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
    response = g.collection.insert_one(request.get_json())
    return jsonify(response), HTTPStatus.CREATED

@app.route("/reportAssign/recvTransferState", methods=['POST'])
def recvTransferState():
    response = g.collection.insert_one(request.get_json())
    return jsonify(response), HTTPStatus.CREATED

if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
