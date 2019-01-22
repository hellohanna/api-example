from flask import Flask, request, jsonify, Response
from random import randint
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from functools import wraps


app = Flask(__name__)
db = SQLAlchemy()


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """

    sql = "SELECT password_hash FROM users WHERE login = :username"
    rows = db.session.execute(sql, {'username': username}).fetchall()
    if not rows:
        return False
    password_hash = bytes(rows[0][0])
    if password_hash != bcrypt.hashpw(password.encode(), password_hash):
        return False
    return True


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return 'unauthorized', 401
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/data', methods = ['POST'])
@requires_auth
def post_data():
    """Creates new record in db"""

    if not request.json:
        return 'json body is expected', 400

    data = request.json
    
    sql = """
    INSERT INTO data (name)
    VALUES (:name)
    RETURNING id
    """
    cursor = db.session.execute(sql, {"name": data['name']})
    id = cursor.fetchone()
    db.session.commit()

    return jsonify(id[0]), 201


@app.route('/data/<id>', methods = ['GET'])
@requires_auth
def get_data(id):
    """Returns name from db by id"""

    if not id or not id.isdigit():
        return 'integer ID expected', 400

    sql = "SELECT name FROM data WHERE id = :id"
    cursor = db.session.execute(sql, {"id": id})
    data = cursor.fetchone()
    if not data:
        return 'not found', 404

    return jsonify(data[0]), 200


@app.route('/data/<id>', methods = ['DELETE'])
@requires_auth
def delete_data(id):
    """Delete name from db by id"""

    if not id or not id.isdigit():
        return 'integer ID expected', 400

    sql = "SELECT name FROM data WHERE id = :id"
    cursor = db.session.execute(sql, {"id": id})
    data = cursor.fetchall()
    if not data:
        return 'not found', 404

    sql = "DELETE FROM data WHERE id = :id"
    db.session.execute(sql, {"id": id})
    db.session.commit()
    
    return 'data deleted', 200


@app.route('/data/<id>', methods = ['PUT'])
@requires_auth
def put_data(id):
    """Changes name in db by id"""

    if not request.json:
        return 'json body is expected', 400

    if not id or not id.isdigit():
        return 'integer ID expected', 400

    sql = "SELECT name FROM data WHERE id = :id"
    cursor = db.session.execute(sql, {"id": id})
    data = cursor.fetchall()
    if not data:
        return 'not found', 404

    data = request.json
    sql = "UPDATE data SET name = :name WHERE id = :id"
    cursor = db.session.execute(sql, {"name": data['name'], "id": id})
    db.session.commit()

    return 'data changed', 200


def create_test_user():
    """Create test login and password"""

    login = 'test'
    password = 'password'

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt)

    sql = "DELETE FROM users WHERE login = :login"
    db.session.execute(sql, {'login': login})

    sql = """
    INSERT INTO users (login, password_hash)
    VALUES (:login, :password_hash)
    """
    db.session.execute(sql, {'login': login, 'password_hash': password_hash})
    db.session.commit()


def connect_to_db(app, database_uri="postgresql:///sampledb"):
    """Connect the database to Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    create_test_user()


if __name__=='__main__':
    connect_to_db(app)
    app.run(host="0.0.0.0")


