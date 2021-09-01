from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class BusinessForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	address = StringField('Address', validators=[DataRequired()])
	city = StringField('City', validators=[DataRequired()])
	stars = StringField('Rating', validators=[DataRequired()])
	review_count = StringField('Review Counts', validators=[DataRequired()])
	categories = StringField('Categories', validators=[DataRequired()])
	monday_hour = StringField('Monday Hour')
	tuesday_hour = StringField('Tuesday Hour')
	wednesday_hour = StringField('Wednesday Hour')
	thursday_hour = StringField('Thursday Hour')
	friday_hour = StringField('Friday Hour')
	saturday_hour = StringField('Saturday Hour')
	sunday_hour = StringField('Sunday Hour')
	# content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Submit')
