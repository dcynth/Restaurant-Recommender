from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from test import db, bcrypt
from test.models import User, Post, UserFollowUser
from test.users.forms import RegisterationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from test.users.utils import save_picture, send_reset_email
import sqlite3
from sqlite3 import Error

users = Blueprint('users', __name__)

def create_connection(db_file):
	""" create a database connection to a SQLite database """
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	finally:
		if conn:
			return conn

@users.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegisterationForm()
	if form.validate_on_submit():
		hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
		db.session.add(user)
		db.session.commit()
		flash('Account created! Now you can login!','success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=form)

@users.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			if next_page:
				return redirect(next_page)
			else:
				return redirect(url_for('main.home'))
		else:
			flash(f'Wrong email and password combination!','danger')
	return render_template('login.html', title='Login', form=form)

@users.route('/logout', methods=['GET','POST'])
def logout():
	logout_user()
	return redirect(url_for('main.home'))

@users.route('/account', methods=['GET','POST'])
@login_required
def account():
	database = r"test/data.db"
	conn = create_connection(database)
	cur = conn.cursor()

	friend_id = request.args.get('friend_id', default=99999999999, type=int)

	if friend_id != 99999999999:
		current_relationship = UserFollowUser.query.filter_by(id1=current_user.id, id2=friend_id).all()
		if current_relationship == []:
			relationship = UserFollowUser(id1=current_user.id, id2=friend_id)
			db.session.add(relationship)
			db.session.commit()
		else:
			relationship = UserFollowUser.query.get_or_404((current_user.id, friend_id))
			db.session.delete(relationship)
			db.session.commit()

	friends = UserFollowUser.query.filter_by(id1=current_user.id).all()
	friends_id = [x.id2 for x in friends]

	form = UpdateAccountForm()
	# users = User.query.filter_by().all()
	cur.execute("SELECT * FROM user where id=?",(current_user.id,))
	current_users = cur.fetchall()
	cur.execute("SELECT * FROM user where id!=?",(current_user.id,))
	all_users_without_current = cur.fetchall()

	users = current_users+all_users_without_current

	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!','success')
		return redirect(url_for('users.account'))
	elif request.method=='GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form, users=users, current_user=current_user, friends_id=friends_id)

# @users.route('/account/<string:friend_id>', methods=['GET','POST'])
# @login_required
# def account_friend(friend_id):
# 	form = UpdateAccountForm()
# 	users = User.query.filter_by().all()
#
# 	if form.validate_on_submit():
# 		if form.picture.data:
# 			picture_file = save_picture(form.picture.data)
# 			current_user.image_file = picture_file
# 		current_user.username = form.username.data
# 		current_user.email = form.email.data
# 		db.session.commit()
# 		flash('Your account has been updated!','success')
# 		return redirect(url_for('users.account'))
#
# 	elif request.method=='GET':
# 		form.username.data = current_user.username
# 		form.email.data = current_user.email
#
# 	print(friend_id)
#
# 	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
# 	return render_template('account.html', title='Account', image_file=image_file, form=form, users=users, current_user=current_user)

@users.route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', default=1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)

@users.route('/reset_password', methods=['GET','POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		print(form.email.data)
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent to reset ur password', 'info')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@users.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if not user:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('users.reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_pw
		db.session.commit()
		flash('Your password has been updated!','success')
		return redirect(url_for('users.login'))

	return render_template('reset_token.html', title='Reset Password', form=form)
