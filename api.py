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
# then build that db, open python3 in terminal
# 	from api import db
# 	db.create_all()
# 	exit

# check in sqlite3 todo.db
# 	.tables
# 	.exit
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# create database model :
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String(50), unique=True)
	name = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))
	admin = db.Column(db.Boolean)

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(50))
	complete = db.Column(db.Boolean)
	user_id = db.Column(db.Integer)

# create fucking API :
@app.route('/user', methods=['GET'])
def get_all_users():
	# process:
	users = User.query.all()
	output = []
	for user in users:
		user_data = {}
		user_data['public_id'] = user.public_id
		user_data['name'] = user.name
		user_data['password'] = user.password
		user_data['admin'] = user.admin
		output.append(user_data)
	# output
	return jsonify({ 'users' : output})

@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):
	# process :
	user = User.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message': 'No user found!'})

	user_data = {}
	user_data['public_id'] = user.public_id
	user_data['name'] = user.name
	user_data['password'] = user.password
	user_data['admin'] = user.admin
	return jsonify({'user': user_data})

@app.route('/user', methods=['POST'])
def create_user():
	# Get the Input :
	data = request.get_json()
	# check same name :
	user = User.query.filter_by(name=data['name']).first()
	if user:
		return jsonify({'message': 'please, use another username'})

	hashed_password = generate_password_hash(data['password'], method='sha256')
	# process :
	new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
	# Output :
	# save to database
	db.session.add(new_user)
	db.session.commit()
	# Response Output 
	return jsonify({'message': 'new user created'})

@app.route('/user/<public_id>', methods=['PUT'])
def promote_user(public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'message': 'No user found!'})

	# the update is very simple
	user.admin = True
	db.session.commit()

	return jsonify({'message': 'The user has been promoted'})

@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'message': 'No user found!'})
	# this is how you delete fucking user:
	db.session.delete(user)
	db.session.commit()

	return jsonify({'message': 'The user has been deleted'})

if __name__ == '__main__':
	app.run(debug=True, port=3002)
