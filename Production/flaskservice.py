from flask import Flask, request
app = Flask(__name__)

# configure Flask routes

@app.route('/')
def index():
  return 'Flask service is up and running!'

@app.route('/add')
def add():
	weekday = request.args['weekday']
	festivalreligion = request.args['festivalreligion']
	workingday = request.args['workingday']
	holidaysequence = request.args['holidaysequence']
	totalamount = request.args['totalamount']
	xyzamount = request.args['xyzamount']
	return weekday + festivalreligion + workingday + holidaysequence + totalamount + xyzamount

	

# http://localhost:5000/add?weekday=1.0&festivalreligion=1.0&workingday=1.0&holidaysequence=1.0&totalamount=1.0&xyzamount=1.0