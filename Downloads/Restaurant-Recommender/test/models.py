from test import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from flask import current_app

class Business(db.Model):
	id = db.Column(db.String(100), primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	address = db.Column(db.String(100))
	city = db.Column(db.String(100))
	latitude = db.Column(db.Float)
	longitude = db.Column(db.Float)
	stars = db.Column(db.Float)
	review_count = db.Column(db.Integer)
	categories = db.Column(db.String(100))
	Monday_hour= db.Column(db.String(100))
	Tuesday_hour= db.Column(db.String(100))
	Wednesday_hour= db.Column(db.String(100))
	Thursday_hour= db.Column(db.String(100))
	Friday_hour= db.Column(db.String(100))
	Saturday_hour= db.Column(db.String(100))
	Sunday_hour= db.Column(db.String(100))

	def __repr__(self):
		return f"Business('{self.name}','{self.city}')"

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	posts = db.relationship('Post', backref='author', lazy=True)

	def get_reset_token(self, expire_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expire_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}','{self.email}')"

class UserFollowUser(db.Model):
	id1 = db.Column(db.Integer, primary_key=True)
	id2 = db.Column(db.Integer, primary_key=True)

	def __repr__(self):
		return f"UserFollowUser('{self.id1}','{self.id2}')"



class UserLikeBusiness(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	business_id = db.Column(db.String(100), primary_key=True)

	def __repr__(self):
		return f"UserLikeBusiness('{self.user_id}'), Business('{self.business_id}')"

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Post('{self.title}','{self.date_posted}')"
