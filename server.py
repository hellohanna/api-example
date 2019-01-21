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

    print('created new record', id)
    return jsonify(id[0]), 201


@app.route('/data/<id>', methods = ['GET'])
def get_data(id):
    if not id or not id.isdigit():
        return 'integer ID expected', 400

    sql = "SELECT name FROM data WHERE id = :id"
    cursor = db.session.execute(sql, {"id": id})
    data = cursor.fetchone()
    if not data:
        return 'not found', 401

    print('return data:', data)
    return 'data', 200


@app.route('/delete/<id>', methods = ['DELETE'])
def delete_data(id):
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
    
    print('data deleted')
    return 'data deleted', 200


@app.route('/change/<id>', methods = ['PUT'])
def put_data(id):
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

    print('data changed:', data['name'])
    return 'data changed', 200


def connect_to_db(app, database_uri="postgresql:///sampledb"):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__=='__main__':
    connect_to_db(app)
    app.run(host="0.0.0.0")


