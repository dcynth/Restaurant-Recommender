import pyodbc
import json
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = r'localhost\cs-htong-08\zhexu3,49172'
database = 'CS411'
username = 'team40'
password = 'CS411team40'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# Make table
# CREATE TABLE business (
#     business_id varchar(255),
#     name varchar(255),
#     address varchar(255),
#     city varchar(255),
# 	latitude float,
# 	longitude float,
# 	stars float,
# 	review_count float
# );

# Input all the Restaurant info
with open('data/UCbusiness.json', 'r', encoding='utf-8') as fin:
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
		business_id = text['business_id']
		name = text['name']
		address = text['address']
		city = text['city']
		latitude = text['latitude']
		longitude = text['longitude']
		stars = text['stars']
		review_count = text['review_count']
		cursor.execute("""
		INSERT INTO business (business_id, name, address, city, latitude, longitude, stars, review_count)
		VALUES (?,?,?,?,?,?,?,?)""",
		business_id, name, address, city, latitude, longitude, stars, review_count)
		cnxn.commit()
		# row = cursor.fetchone()
		# while row:
		# 	print('Inserted Product key is ' + str(row[0]))
		# 	row = cursor.fetchone()

#Sample insert query
# cursor.execute("""
# INSERT INTO SalesLT.Product (Name, ProductNumber, StandardCost, ListPrice, SellStartDate)
# VALUES (?,?,?,?,?)""",
# 'SQL Server Express New 20', 'SQLEXPRESS New 20', 0, 0, CURRENT_TIMESTAMP)
# cnxn.commit()
# row = cursor.fetchone()
#
# while row:
#     print('Inserted Product key is ' + str(row[0]))
#     row = cursor.fetchone()
