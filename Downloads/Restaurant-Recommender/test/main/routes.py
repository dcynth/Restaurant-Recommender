from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from test.models import Business, UserLikeBusiness, UserFollowUser, User
from test import db
import time, datetime
from datetime import datetime
import sqlite3
from sqlite3 import Error
from test.main.forms import BusinessForm
import string, random
import googlemaps
from math import radians, sin, cos, asin, sqrt

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

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
	database = r"test/data.db"
	conn = create_connection(database)
	cur = conn.cursor()
	# select_all_tasks(conn)

	business_id = request.args.get('business_id', default=99999999999)
	liked_business_id = []
	recommended_businesses = {}
	chosen_latitude = ""
	chosen_longitude = ""
	# selection the greeting
	t = time.localtime()
	current_time = time.strftime("%H:%M:%S", t)
	hour = int(current_time.split(':')[0])
	minute = int(current_time.split(':')[1])
	greeting = ''
	if hour>5 and hour < 12:
		greeting = 'Good morning!'
	elif hour>= 12 and hour <17:
		greeting = 'Good afternoon!'
	elif hour>= 17 and hour <23:
		greeting = 'Good evening!'
	else:
		greeting = "Hi, night owl."

	# day = datetime.today().strftime('%A')
	day = datetime.today().weekday()

	# the following part is about user
	if current_user.is_authenticated:
		if business_id != 99999999999:
			# current_relationship = UserLikeBusiness.query.filter_by(user_id=current_user.id, business_id=business_id).all()
			cur.execute("SELECT * FROM user_like_business where user_id=? and business_id=?", (current_user.id, business_id))
			current_relationship = cur.fetchall()
			if current_relationship == []:
				cur.execute("INSERT INTO user_like_business(user_id, business_id) VALUES(?,?)", (current_user.id, business_id))
			else:
				cur.execute("DELETE FROM user_like_business where user_id=? and business_id=?", (current_user.id, business_id))
			conn.commit()

		# liked_business = UserLikeBusiness.query.filter_by(user_id=current_user.id).all()
		# liked_business_id = [x.business_id for x in liked_business]
		cur.execute("SELECT * FROM user_like_business where user_id=?", (current_user.id,))
		liked_business = cur.fetchall()
		liked_business_id = [x[1] for x in liked_business]

		# get all the friends ID
		# friends = UserFollowUser.query.filter_by(id1=current_user.id).all()
		# friends_id = [x.id2 for x in friends]
		cur.execute("SELECT * FROM user_follow_user where id1=?", (current_user.id,))
		friends = cur.fetchall()
		friends_id = [x[1] for x in friends]

		# Count all the recommended businesses
		recommended_businesses_tmp = {}
		for friend_id in friends_id:
			# name = User.query.filter_by(id=friend_id).all()[0].username
			cur.execute("SELECT * FROM user where id=?", (friend_id,))
			name = cur.fetchall()[0][1]

			# fav_business = UserLikeBusiness.query.filter_by(user_id=friend_id).all()
			# fav_business = [x.business_id for x in fav_business]
			cur.execute("SELECT * FROM user_like_business where user_id=?", (friend_id,))
			fav_business = cur.fetchall()
			fav_business = [x[1] for x in fav_business]
			for b in fav_business:
				if b not in recommended_businesses_tmp:
					recommended_businesses_tmp[b] = []
				recommended_businesses_tmp[b].append(name)

		# print(recommended_businesses_tmp)
		tmp = {}
		for b in recommended_businesses_tmp:
			tmp[b] = len(recommended_businesses_tmp[b])

		key_order = sorted(tmp.items(), key=lambda x: x[1], reverse=True)

		counter = 0
		for bb in key_order:
			if counter == 5: break
			bb = bb[0]
			# recommended_businesses[Business.query.filter_by(id=bb).all()[0]] = recommended_businesses_tmp[bb]
			cur.execute("SELECT * FROM business where id=?", (bb,))
			tmp = cur.fetchall()
			if len(tmp)==0:continue
			tmp = tmp[0]
			counter+=1
			recommended_businesses[tmp] = recommended_businesses_tmp[bb]

	# if the user use the
	page = request.args.get('page', default=1, type=int)

	# the default ranking condition
	city = request.args.get('city', default='all')
	# ranking = request.args.get('ranking', default='highlow')
	ranking = request.args.get('ranking', default='default')
	greaterthan = request.args.get('greaterthan', default='zero')
	curr_latitude = request.args.get('curr_latitude', default='zero')
	curr_longitude = request.args.get('curr_longitude', default='zero')
	chosen_latitude = request.args.get('chosen_latitude', default=curr_latitude)
	chosen_longitude = request.args.get('chosen_longitude', default=curr_longitude)

	# if the user posts any change to the ranking condition
	if request.method == 'POST':
		city = request.form.get('city')
		ranking = request.form.get('ranking')
		greaterthan = request.form.get('greaterthan')
		chosen_latitude = request.form.get('chosen_latitude')
		chosen_longitude = request.form.get('chosen_longitude')

	sql_query = ''
	per_page=5
	if ranking == 'highlow' or ranking == 'default':
		order = ' order by stars desc'
	else:
		order = ' order by stars asc'

	if greaterthan == 'zero':
		where = 'WHERE stars > 0'
	elif greaterthan == 'one':
		where = 'WHERE stars > 1'
	elif greaterthan == 'two':
		where = 'WHERE stars > 2'
	elif greaterthan == 'three':
		where = 'WHERE stars > 3'
	elif greaterthan == 'four':
		where = 'WHERE stars > 4'
	else:
		where = 'WHERE stars > 0'

	def generatePages(page_nums, current_page, left_edge=1, right_edge=1, left_current=4, right_current=5):
		if current_page>left_edge+left_current+1:
			LS = list(range(1,1+left_edge))+[None]+list(range(current_page-1-left_current, current_page+1))
		else:
			LS = list(range(1, 1+current_page))

		if current_page<page_nums-right_current:
			RS = list(range(current_page+1, current_page+right_current+1))+[None]+list(range(page_nums-right_edge+1, page_nums+1))
		else:
			RS = list(range(current_page+1, page_nums+1))

		return LS+RS

	if city == 'all':
		cur.execute("SELECT * FROM business "+where+ " "+order)
		businesses = cur.fetchall()

	else:
		cur.execute("SELECT * FROM business " + where + " AND city=?"+order, (city,))
		businesses = cur.fetchall()

	#display Distance and time
	distances = []
	times = []

	def cal_distance(lat1, lat2, lon1, lon2):
		lon1 = radians(float(lon1))
		lon2 = radians(float(lon2))
		lat1 = radians(float(lat1))
		lat2 = radians(float(lat2))
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
		c = 2 * asin(sqrt(a))
		r = 6371
		return(c * r)

	def find_distance(client, latitude1, longitude1, latitude2, longitude2):
		# 40.112846 -88.240511 zero zero
		# params = {"origins": latitude1 + "," + longitude1,
		  # "destinations": latitude2 + "," + longitude2}
		# return str(client._request("/maps/api/distancematrix/json", params)["rows"][0]["elements"][0]['distance']['text'])
		if latitude1 == 'zero' or longitude1 == 'zero' or latitude2 == 'zero' or longitude2 == 'zero' or latitude1 == 'None' or longitude1 == 'None' or latitude2 == 'None' or longitude2 == 'None' or latitude1 == '' or longitude1 == '' or latitude2 == '' or longitude2 == '':
			return 'Unknown'
		else:
			distance = round(cal_distance(latitude1, latitude2, longitude1, longitude2),1)
		return str(distance)+' km'

	def find_time(client, latitude1, longitude1, latitude2, longitude2):
		# params = {"origins": latitude1 + "," + longitude1,
		#   "destinations": latitude2 + "," + longitude2}
		# return str(client._request("/maps/api/distancematrix/json", params)["rows"][0]["elements"][0]['duration']['text'])
		if latitude1 == 'zero' or longitude1 == 'zero' or latitude2 == 'zero' or longitude2 == 'zero' or latitude1 == 'None' or longitude1 == 'None' or latitude2 == 'None' or longitude2 == 'None' or latitude1 == '' or longitude1 == '' or latitude2 == '' or longitude2 == '':
			time = 'Unknown'
		else:
			distance = cal_distance(latitude1, latitude2, longitude1, longitude2)
			time = round(distance/3*60)
			if time > 1:
				time = str(time) + ' mins'
			else:
				time = str(time) + ' min'

		return time

	gmaps = googlemaps.Client(key='AIzaSyCUoJ69dE6EDWp8jSqZ6C5D6tKLP62x2co')
	for business in businesses:
		distances.append(find_distance(gmaps, str(business[4]), str(business[5]), chosen_latitude, chosen_longitude))
		times.append(find_time(gmaps, str(business[4]), str(business[5]), chosen_latitude, chosen_longitude))
	opening_status = []

	# "9:0-21:0"
	for business in businesses:
		# specific_openingtime = [business.Monday_hour, business.Tuesday_hour, business.Wednesday_hour, business.Thursday_hour, business.Friday_hour, business.Saturday_hour, business.Sunday_hour][int(day)]
		specific_openingtime = [business[9], business[10], business[11], business[12], business[13], business[14], business[15]][int(day)]
		if specific_openingtime=='closed'or specific_openingtime=='' or specific_openingtime==None or specific_openingtime=='Closed':
			opening_status.append('Closed')
			continue
		openH = int(specific_openingtime.split('-')[0].split(':')[0])
		openM = int(specific_openingtime.split('-')[0].split(':')[1])
		closeH = int(specific_openingtime.split('-')[1].split(':')[0])
		closeM = int(specific_openingtime.split('-')[1].split(':')[1])

		if hour < openH or hour > closeH:
			opening_status.append('Closed')
		elif hour == openH and minute<openM:
			opening_status.append('Closed')
		elif hour == closeH and minute>openM:
			opening_status.append('Closed')
		else:
			opening_status.append('Open')

	status = []
	for i, business in enumerate(businesses):
		# status.append((business.id, business.name, business.address, business.city, business.stars, opening_status[i]))
		status.append((business[0], business[1], business[2], business[3], business[6], opening_status[i], distances[i], times[i]))

	def SortStatusBasedOnDistances(status):
		floatDistances = []
		for i in status:
			if i[6] == 'Unknown':
				floatDistances.append(999999999999999999)
			else:
				floatDistances.append(float(i[6].replace(' km','').replace(',','')))
		_, orderedStatus = zip(*sorted(zip(floatDistances, status)))
		return orderedStatus

	if ranking == 'default':
		status = SortStatusBasedOnDistances(status)

	page_nums = len(status)//per_page+1
	status = status[(page-1)*per_page:page*per_page]
	page_indexes = generatePages(page_nums, page, left_current=2, right_current=3)

	'''DATA VISUALIZATION CODE'''
	if city == 'all':
		cur.execute("SELECT * FROM business")
	else:
		cur.execute("SELECT * FROM business where city=?", (city,))
	businesses = cur.fetchall()
	results = [int(b[6]) for b in businesses]
	values = [0, 0, 0, 0, 0]
	for r in results:
		if r >= 5:
			r = 5
		elif r <= 1:
			r = 1
		values[r-1] += 1
	labels = [1, 2, 3, 4, 5]
	############################################
	results = [b[8].split(", ") for b in businesses]
	my_dict = {'Mexican':0, 'Indian':0, 'Chinese':0, 'Greek':0, 'Vietnamese':0, 'Cajun/Creole':0, 'Thai':0, 'Italian':0, 'American (Traditional)':0}
	for result in results:
		for r in result:
			if r in my_dict.keys():
				my_dict[r] += 1
	labels_pi = []
	values_pi = []
	for key in my_dict.keys():
		labels_pi.append(key)
		values_pi.append(my_dict[key])

	return render_template('home.html', businesses=businesses, liked_business_id=liked_business_id, recommended_businesses=recommended_businesses,
	 						city=city, ranking=ranking, greeting=greeting, status=status, page_indexes=page_indexes, current_page=page, values=values, labels=labels,
							labels_pi=labels_pi, values_pi=values_pi, chosen_latitude = chosen_latitude, chosen_longitude = chosen_longitude)

@main.route('/new', methods=['GET','POST'])
@login_required
def new_business():
	form = BusinessForm()
	if form.validate_on_submit():
		flash('New restaurant information has been created!','success')
		# post = Post(title=form.title.data, content=form.content.data, author=current_user)
		# db.session.add(post)
		# db.session.commit()
		database = r"test/data.db"
		conn = create_connection(database)
		cur = conn.cursor()
		# 22 digits id
		generatedId = ''.join(random.choice(string.ascii_uppercase + string.digits+string.ascii_lowercase) for _ in range(22))
		cur.execute("INSERT INTO business(id, name, address, city, stars, review_count, categories, Monday_hour, Tuesday_hour, Wednesday_hour, Thursday_hour, Friday_hour, Saturday_hour, Sunday_hour) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
		 		(generatedId, form.name.data, form.address.data, form.city.data, form.stars.data, form.review_count.data,
				form.categories.data, form.monday_hour.data, form.tuesday_hour.data, form.wednesday_hour.data,
				 form.thursday_hour.data, form.friday_hour.data, form.saturday_hour.data, form.sunday_hour.data,))
		conn.commit()
		return redirect(url_for('main.home'))
	# return render_template('create_post.html', title='New Post', form=form, legend='New Post')
	return render_template('create_business.html', title='New Restaurant', form=form, legend='New Restaurant')

@main.route('/<business_id>', methods=['GET','POST'])
def business(business_id):
	database = r"test/data.db"
	conn = create_connection(database)
	cur = conn.cursor()
	cur.execute("SELECT * FROM business where id=? ", (business_id,))
	business = cur.fetchall()[0]
	# post = Post.query.get_or_404(post_id)
	return render_template('business.html', title=business[1], business=business)

@main.route('/<business_id>/delete', methods=['POST'])
@login_required
def delete_business(business_id):
	database = r"test/data.db"
	conn = create_connection(database)
	cur = conn.cursor()
	cur.execute("DELETE FROM business where id=? ", (business_id,))

	conn.commit()
	flash('Deleted!','success')
	return redirect(url_for('main.home'))

@main.route('/<business_id>/update', methods=['GET','POST'])
@login_required
def update_business(business_id):
	database = r"test/data.db"
	conn = create_connection(database)
	cur = conn.cursor()

	# post = Post.query.get_or_404(business_id)
	cur.execute("SELECT * FROM business where id=? ", (business_id,))
	business = cur.fetchall()[0]
	business_id = business[0]

	form = BusinessForm()
	if form.validate_on_submit():
		sql = ''' UPDATE business
			  SET name = ? ,
				  address = ? ,
				  city = ? ,
				  stars = ? ,
				  review_count = ? ,
				  categories = ? ,
				  Monday_hour = ? ,
				  Tuesday_hour = ? ,
				  Wednesday_hour = ? ,
				  Thursday_hour = ? ,
				  Friday_hour = ? ,
				  Saturday_hour = ? ,
				  Sunday_hour = ?
			  WHERE id = ?'''
		cur.execute(sql, (form.name.data, form.address.data, form.city.data, form.stars.data, form.review_count.data,
					form.categories.data, form.monday_hour.data, form.tuesday_hour.data, form.wednesday_hour.data, form.thursday_hour.data, form.friday_hour.data, form.saturday_hour.data, form.sunday_hour.data, business_id,))
		conn.commit()
		flash('Updated!','success')
		return redirect(url_for('main.business', business_id=business_id))
	elif request.method=="GET":
		form.name.data = business[1]
		form.address.data = business[2]
		form.city.data = business[3]
		form.stars.data = business[6]
		form.review_count.data = business[7]
		form.categories.data = business[8]
		form.monday_hour.data = business[9]
		form.monday_hour.data = business[10]
		form.wednesday_hour.data = business[11]
		form.thursday_hour.data = business[12]
		form.friday_hour.data = business[13]
		form.saturday_hour.data = business[14]
		form.sunday_hour.data = business[15]
	return render_template('create_business.html', title='Update Business', form=form, legend='Update Business')

@main.route('/about')
def about():
	return render_template('about.html', title='About')
