from test.models import Business, User, UserFollowUser, UserLikeBusiness, Post
import json
from faker import Faker
from test import bcrypt
import sqlite3
from sqlite3 import Error
# id = db.Column(db.String(100), primary_key=True)
# name = db.Column(db.String(100), nullable=False)
# address = db.Column(db.String(100))
# city = db.Column(db.String(100))
# latitude = db.Column(db.Float)
# longitude = db.Column(db.Float)
# stars = db.Column(db.Float)
# review_count = db.Column(db.Integer)
# categories = db.Column(db.String(100))

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

def ImportData():
	# faker = Faker()
	# for _ in range(10):
	# 	hashed_pw = bcrypt.generate_password_hash("123").decode('utf-8')
	# 	first_name = faker.first_name()
	# 	last_name = faker.last_name()
	# 	user = User(username=first_name+' '+last_name, email=first_name.lower()+"@illinois.edu", password=hashed_pw)
	# 	db.session.add(user)
	# 	db.session.commit()

	# update business data
	database = r"test/data.db"
	conn = create_connection(database)
	cur = conn.cursor()
	cur.execute("DELETE from business")
	conn.commit()

	with open('yelpUrbana/data/UCbusiness.json', 'r', encoding='utf-8') as fin:
		for i in fin:
			j = i.strip()

			text = json.loads(j)
			if 'business_id' not in text:continue
			if 'name' not in text:continue
			if 'address' not in text:continue
			if 'city' not in text:continue
			if 'latitude' not in text:continue
			if 'longitude' not in text:continue
			if 'stars' not in text:continue
			if 'review_count' not in text:continue
			if 'hours' not in text:continue

			business_id = text['business_id']
			name = text['name']
			address = text['address']
			city = text['city']
			latitude = text['latitude']
			longitude = text['longitude']
			stars = text['stars']
			review_count = text['review_count']
			if 'categories' not in text:
				categories = 'None'
			else:
				categories = text['categories']

			if 'Food' not in categories and 'Restaurants' not in categories and 'Restaurant' not in categories:
				continue

			hours = text['hours']
			if hours == None: continue

			if 'Monday' not in hours:
				Monday_hour = "closed"
			else:
				Monday_hour = hours['Monday']

			if 'Tuesday' not in hours:
				Tuesday_hour = "closed"
			else:
				Tuesday_hour = hours['Tuesday']

			if 'Wednesday' not in hours:
				Wednesday_hour = "closed"
			else:
				Wednesday_hour = hours['Wednesday']

			if 'Thursday' not in hours:
				Thursday_hour = "closed"
			else:
				Thursday_hour = hours['Thursday']

			if 'Friday' not in hours:
				Friday_hour = "closed"
			else:
				Friday_hour = hours['Friday']

			if 'Saturday' not in hours:
				Saturday_hour = "closed"
			else:
				Saturday_hour = hours['Saturday']

			if 'Sunday' not in hours:
				Sunday_hour = "closed"
			else:
				Sunday_hour = hours['Sunday']


			# business = Business(id=business_id, name=name, address=address, city=city,
			#  				latitude=latitude, longitude=longitude, stars=stars,
			# 				Monday_hour=Monday_hour, Tuesday_hour=Tuesday_hour, Wednesday_hour=Wednesday_hour,
			# 				Thursday_hour=Thursday_hour, Friday_hour=Friday_hour, Saturday_hour=Saturday_hour,
			# 				Sunday_hour=Sunday_hour, review_count=review_count, categories=categories)
			# db.session.add(business)
			# db.session.commit()
			cur.execute("INSERT INTO business(id, name, address, city, latitude, longitude, stars, review_count, categories, Monday_hour, Tuesday_hour, Wednesday_hour, Thursday_hour, Friday_hour, Saturday_hour, Sunday_hour) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
			 		(business_id, name, address, city, latitude, longitude,
					stars, review_count, categories, Monday_hour, Tuesday_hour, Wednesday_hour,
					 Thursday_hour, Friday_hour, Saturday_hour, Sunday_hour,))
			conn.commit()
