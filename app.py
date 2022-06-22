from atexit import register
from fileinput import filename
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

import jwt
import os
import datetime

from sklearn import tree

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'UAS.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SECRET_KEY'] = "VoL"

class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))

db.create_all()

def cari_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('datatoken')
        if not token:
            return make_response(jsonify({"msg":"Token belum di isi, Isi token untuk melanjutkan"}), 401)
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return make_response(jsonify({"msg":"Token Invalid"}), 401)
        return f(*args, **kwargs)
    return decorator
class RegistertUser(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')
        if dataUsername and dataPassword:
            dataModel = AuthModel(username=dataUsername, password=dataPassword)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg":"Berhasil"}), 200)
        return jsonify({"msg":"Username/Password tidak boleh kosong"})
class LoginUser(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        queryUsername = [data.username for data in AuthModel.query.all()]
        queryPassword = [data.password for data in AuthModel.query.all()]
        if dataUsername in queryUsername and dataPassword in queryPassword:

            token =jwt.encode(
                {
                    "username":queryUsername,
                    "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
                }, app.config['SECRET_KEY'], algorithm="HS256"
            )
            return make_response(jsonify({"msg":"Login Sukses", "token":token}), 200)
        return jsonify({"msg":"Login Gagal"})
class Dashboard(Resource):
    @cari_token
    def get(self):
        return jsonify({"msg":"halaman yang masuk melalui login token "})
class Home(Resource):
    def get(self):
        return jsonify({"msg":"Public"})

api.add_resource(RegistertUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])
api.add_resource(Dashboard, "/api/dashboard", methods=["GET"])
api.add_resource(Home, "/api", methods=["GET"])

if __name__ == "__main__":
    app.run(debug=True)