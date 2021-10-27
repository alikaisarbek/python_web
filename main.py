from flask import Flask, jsonify, request, make_response
import jwt
import datetime
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisthesecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:asdfghjkl@localhost:5432/python'
db = SQLAlchemy(app)
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    token = db.Column(db.Text, nullable=False, default='')

    def __init__(self, username, email, password, token):
        self.username = username
        self.email = email
        self.password = password
        self.token = token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message' : 'Hello, Could not verify the token.'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Hello, Could not verify the token.'}), 403

        return f(*args, **kwargs)

    return decorated


@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : 'Hello, token which is provided is correct.'})

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = Users.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if auth and auth.password == user.password:
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=15)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

if __name__ == '__main__':
    app.run(debug=True)
