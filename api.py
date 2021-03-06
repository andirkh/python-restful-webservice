from flask import Flask, request, jsonify, make_response
# jsonify: return the information
from flask_sqlalchemy import SQLAlchemy
import uuid
# uuid: generate random public id
from werkzeug.security import generate_password_hash, check_password_hash
# hashing

import jwt
# jwt: web token generator
# did pip uninstall JWT and pip uninstall PyJWT then finally pip install PyJWT.
import datetime
from functools import wraps

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


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'message' : 'Token is Missing'}), 401

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
			current_user = User.query.filter_by(public_id=data['public_id']).first()
		except:
			return jsonify({'message': 'Token is invalid'}), 401

		return f(current_user, *args, **kwargs)

	return decorated

# create fucking API :
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
	if not current_user.admin:
		return jsonify({'message': 'Cannot perform that functions'})

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
@token_required
def get_one_user(current_user,public_id):
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
@token_required
def create_user(current_user):
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
@token_required
def promote_user(current_user, public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'message': 'No user found!'})

	# the update is very simple
	user.admin = True
	db.session.commit()

	return jsonify({'message': 'The user has been promoted'})

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
	user = User.query.filter_by(public_id=public_id).first()
	if not user:
		return jsonify({'message': 'No user found!'})
	# this is how you delete fucking user:
	db.session.delete(user)
	db.session.commit()

	return jsonify({'message': 'The user has been deleted'})

@app.route('/login')
def login():
	#NO AUTH
	auth = request.authorization
	if not auth or not auth.username or not auth.password:
		return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
	
	#NO USER IN DATABASE
	user = User.query.filter_by(name=auth.username).first()
	if not user:
		return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

	if check_password_hash(user.password, auth.password):
		#login success
		token = jwt.encode({'public_id': user.public_id, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
		return jsonify({'token': token.decode('UTF-8')})

	# PASSWORD isnt correct
	return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


if __name__ == '__main__':
	# set your port here:
	app.run(debug=True, port=3002)
