import numpy as np
import json
import sklearn.gaussian_process
from sklearn.gaussian_process.kernels import RBF
from flask import Flask, jsonify, request
from bson.objectid import ObjectId
from bson import json_util
from pymongo import MongoClient
from flask_cors import CORS


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "this is a music app"
CORS(app)
database_link = "mongodb://XXXX:XXXXX15@ds127841.mlab.com:27841/music_exp"


def predict_music(used_music, available_music, alp):
    """
    Predict the music based on user feedback data

    Parameters
    ----------
    used_music: list of lists
        each list contains data associated with music listened by the user

    available_music: list of list
        each list contains data associated with music in the pool that is not sampled.

    alp: string
        Alpha value

    Returns
    -------
    selected_music_index: int
        the index of the selected music in the list of available music
    """
    user_data = np.array(used_music)
    alpha = int(alp)
    train_x = user_data[:, 2:-3].astype(np.float)
    train_y = user_data[:, -1].astype(np.int).flatten()
    kernel = 1.0 * RBF(1.0)
    model = sklearn.gaussian_process.GaussianProcessClassifier(kernel=kernel)
    model.fit(train_x, train_y)
    class_prob = model.predict_proba(np.array(available_music)[:, 2:].astype(np.float))
    selected_music_prob = np.percentile(class_prob[:, 1], alpha)
    selected_music_index = np.argmin(np.absolute(class_prob[:, 1] - selected_music_prob))
    return selected_music_index


@app.route('/getAlgoMusic', methods=["Post"])
def update_newmusic():
    """
    Return dictionary containing url and id of recommended music in format

    Returns
    -------
    client_data: dictionary
        format is {"m_url": Recommended music url string, "m_id": Music id}
    """
    connection = MongoClient(database_link)
    db = connection.music_exp
    user_id = request.get_json()
    user = db.user_data.find_one({"_id": ObjectId(user_id["u_id"])})
    music_index = predict_music(user[user_id["current_session"]], user["available_songs"], user_id["alp"])
    selected_music = user["available_songs"][music_index]
    selected_music_data = db.music_data.find_one({"_id": ObjectId(selected_music[0])})
    db.user_data.update({"_id": ObjectId(user_id["u_id"])}, {'$pull': {"available_songs": selected_music}})
    client_data = {}
    client_data["m_url"] = selected_music_data["url"]
    client_data["m_id"] = selected_music
    connection.close()
    return jsonify(client_data)


@app.route('/getRandomMusic', methods=["Post"])
def update_music():
    """
    Returns dictionary containing url and id of randomly sampled music in format

    Returns
    -------
    client_data: dictionary
         format is {"m_url": Random music url string, "m_id": Music id}
    """
    connection = MongoClient(database_link)
    db = connection.music_exp
    user_id = request.get_json()
    user = db.user_data.find_one({"_id": ObjectId(user_id["u_id"])})
    music_index = np.random.choice(len(user["available_songs"]))
    selected_music = user["available_songs"][music_index]
    selected_music_data = db.music_data.find_one({"_id": ObjectId(selected_music[0])})
    db.user_data.update({"_id": ObjectId(user_id["u_id"])}, {'$pull': {"available_songs": selected_music}})
    client_data = {}
    client_data["m_url"] = selected_music_data["url"]
    client_data["m_id"] = selected_music
    connection.close()
    return jsonify(client_data)


@app.route('/', methods=['GET'])
def create_store():
    """
    Create data collection for the user in database and return user id

    Returns
    -------
    user: dictionary
        format is {"u_id": "User id}
    """
    connection = MongoClient(database_link)
    db = connection.music_exp
    music = db.music_data.find({})
    user = {}
    user["available_songs"] = [[str(m["_id"])]+[str(m["genres"])]+m["stFeatures"][:] for m in music]
    user_id = db.user_data.insert_one(user)
    user["u_id"] = str(user_id.inserted_id)
    del user["_id"]
    connection.close()
    return jsonify(user)


@app.route("/sendChoice", methods=["Post"])
def update_user():
    """
    Store the feedback for each music in the database
    """
    connection = MongoClient(database_link)
    db = connection.music_exp
    user_choice = request.get_json()
    db.user_data.update({"_id": ObjectId(user_choice["u_id"])}, {'$push': {user_choice["current_session"]: user_choice["m_id"]}})
    connection.close()
    return json.dumps(user_choice["m_id"], indent=4, default=json_util.default)


@app.route("/feedback", methods=["Post"])
def update_feedback():
    """
    Store the feedback/suggestions on user experience received at the end of the experiment in the database
    """
    connection = MongoClient(database_link)
    db = connection.music_exp
    user_choice = request.get_json()
    db.user_data.update({"_id": ObjectId(user_choice["u_id"])}, {'$set': {'feedback': user_choice["comment"]}})
    connection.close()
    return json.dumps(user_choice["comment"], indent=4, default=json_util.default)


if __name__ == '__main__':
    app.secret_key = "this is a music app"
    app.run()
