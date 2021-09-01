from test import create_app
from test import db
from test.models import Business
from ImportData import ImportData

app = create_app()
LoadMode = False
TestMode = False

if __name__ == '__main__':
	if LoadMode:
		with app.app_context():
			# db.drop_all()
			# db.create_all()
			ImportData()
	elif TestMode:
		with app.app_context():
			print(Business.query.filter_by(city='Urbana').first())
	else:
		app.run(debug=True)
	# app.run(debug=False, host='0.0.0.0', port=12345)
