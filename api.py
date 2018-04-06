from flask import Flask, request, jsonify
# request: to get the request data
# jsonify: return the information
from flask_sqlalchemy import SQLAlchemy
import uuid
# uuid: generate random public id
from werkzeug.security import generate_password_hash, check_password_hash
# hashing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'
# create fucking sqlite database
# then open python3
# 	from api import db
# 	db.create_all()
# 	exit
# check in sqlite3 todo.db
# 	.tables
# 	.exit
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# create database model :
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String(50), unique=True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(80))
	admin = db.Column(db.Boolean)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(50))
	complete = db.Column(db.Boolean)
	user_id = db.Column(db.Integer)

# create fucking API :
@app.route('/users', methods=['GET'])
def get_all_users():
	return ''

@app.route('/user/<user_id>', methods=['GET'])
def get_one_user():
	return ''

@app.route('/user', methods=['POST'])
def create_user():
	data = request.get_json()
	#print(data)

	hashed_password = generate_password_hash(data['password'], method='sha256')
	#print(hashed_password)

	new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message': 'new user created'})

@app.route('/user/<user_id>', methods=['PUT'])
def promote_user():
	return ''

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user():
	return ''

if __name__ == '__main__':
	app.run(debug=True)
