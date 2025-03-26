from flask import Flask, g, jsonify, request
from http import HTTPStatus
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException
import os

app = Flask(__name__)

## deploy - MongoDB in Railway
# mongo_url = os.getenv("MONGO_URL")
# mongo_database = os.getenv("MONGO_DATABASE")
# mongo_collection = os.getenv("MONGO_COLLECTION")

## test - MongoDB in Railway
# mongo_url = "mongodb://mongo:CoujcuIauUPtOwJjPZybLvVCbQFGbtVA@crossover.proxy.rlwy.net:31947"
# mongo_database = "test"
# mongo_collection = "alarm"
# mongo_full_url = str(mongo_url) + "/" + str(mongo_database) + "?authSource=admin"

## test - MongoDB Atlas
# mongo_url = "mongodb+srv://admin:admin@cluster0.vkzwtsi.mongodb.net/?appName=Cluster0" #not work
mongo_url = "mongodb://admin:admin@ac-zmixluu-shard-00-00.vkzwtsi.mongodb.net:27017,ac-zmixluu-shard-00-01.vkzwtsi.mongodb.net:27017,ac-zmixluu-shard-00-02.vkzwtsi.mongodb.net:27017/?replicaSet=atlas-ky5u3w-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0"
mongo_database = "test"
mongo_collection = "alarm"
mongo_full_url = str(mongo_url) + "/" + str(mongo_database)

print("connection uri:", mongo_full_url)

try:
    client = MongoClient(mongo_full_url)
    client.admin.command('ping')

    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

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
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 12345)))
