from flask import Flask, request, jsonify
from random import randint
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy()


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/data', methods = ['POST'])
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


def connect_to_db(app, database_uri="postgresql:///sampledb"):
    """Connect the database to Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__=='__main__':
    connect_to_db(app)
    app.run(host="0.0.0.0")


