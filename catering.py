from cmath import log
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from models import  db, Staff, Customer, Event


app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='owner',
	PASSWORD='pass',

	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')
))
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

db.init_app(app)




# ----------------------------------------------------------------------------------------------------------------------------------------------#
# App movement and base functionality


# @app.before_request
# def before_request():
# 	g.user = None
# 	if 'staff.id' in session:
# 		g.user = Staff.query.filter_by(id=session['staff_id']).first()
# 	else: 
# 		g.user = Customer.query.filter_by(id=session['customer_id']).first()


# Initializes database
@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	print('Intialized Database')


# Default, brings user to screen where they can choose authentication options
@app.route('/')
def loginPage():
	return render_template('login.html')



# Routes to signing up or logging in as different user types depending on who the user elects themselves to bet
@app.route('/login<whoYouAre>', methods = ["GET"])
def continueAs(whoYouAre):
	flash('you got here brudda')
	if whoYouAre == "staff":
		return render_template('loginStaff.html')
	elif whoYouAre == "owner":
		return render_template('loginOwner.html')
	elif whoYouAre == "customer":
		return render_template('loginCustomer.html')
	else: 
		return render_template('signupCustomer.html')	


def howManyWorkers(event):

	workers = []
	workers = event.workers

	return workers
	



# ----------------------------------------------------------------------------------------------------------------------------------------------#

# Owner

# Logs in owner using hardcoded credentials
@app.route('/loginOwner', methods=['GET', 'POST'])
def loginOwner():
	error = None

	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			events = Event.query.all()
			

			return render_template('ownerLandingPage.html', events=events)

	return render_template('login.html', error=error)

# Creates a new staff member in the database
@app.route('/createStaff<functionality>', methods = ['POST', 'GET']) 
def createStaff(functionality):

	if functionality == "create":
		events = Event.query.all()
		db.session.add(Staff(request.form['staffUsername'], request.form['staffPassword']))
		db.session.commit()
		return render_template('ownerLandingPage.html', events = events)
	else: 
		return render_template('login.html')

# Link to create a staff member
@app.route('/ownerLandingPage<functionality>', methods = ["GET"])
def ownerLandingPage(functionality):

	if functionality == "createStaff":
		return render_template("create_staff.html")
	else: 
		return render_template('login.html')
	
# ----------------------------------------------------------------------------------------------------------------------------------------------#
# Staff Member

@app.route('/loginStaff', methods=['GET', 'POST'])
def loginStaff():
	error = None

	if request.method == 'POST': 
		
		staff = Staff.query.filter_by(username=request.form['sUsername']).first()
		
		if staff is None: 
			error = "Invalid Username" 

		elif request.form['sPassword'] != staff.password:
				error = "Invalid Password"
		
		else:
			flash('A staff member was logged in')
			session['staff_id'] = staff.id

			events = Event.query.all()
			myEvents = Staff.query.filter_by(id = session['staff_id']).first().myEvents.all()

			availableEvents = [] 
			for event in events:
				if event not in myEvents: 
					availableEvents.append(event)
			
			return render_template('staffLandingPage.html', availableEvents = availableEvents, myEvents = myEvents)
	
	return render_template('loginStaff.html', error = error)


@app.route('/staffFunctions<what><eventID>', methods = ['POST', 'GET'])
def staffFunctions(what, eventID):
	staffWorker = Staff.query.filter_by(id = session['staff_id']).first()
	events = Event.query.all()
	availableEvents = [] 

	if what == "add":
		staffWorker.myEvents.append(Event.query.filter_by(id = eventID).first())
		theEvent = Event.query.filter_by(id = eventID).first()
		theEvent.counter = theEvent.counter + 1
		db.session.commit()
		myEvents = Staff.query.filter_by(id = session['staff_id']).first().myEvents.all()
		for event in events:
			if event not in myEvents: 
				if event.counter < 3:
					availableEvents.append(event)
		return render_template('staffLandingPage.html', availableEvents = availableEvents, myEvents = myEvents)

	elif what == 'remove':
		staffWorker.myEvents.remove(Event.query.filter_by(id = eventID).first())
		theEvent = Event.query.filter_by(id = eventID).first()
		theEvent.counter = theEvent.counter - 1 
		db.session.commit()
		myEvents = Staff.query.filter_by(id = session['staff_id']).first().myEvents.all()
		for event in events:
			if event not in myEvents: 
				if event.counter < 3:
					availableEvents.append(event)
		return render_template('staffLandingPage.html', availableEvents = availableEvents, myEvents = myEvents)

	else: 
		return render_template('login.html')


# ----------------------------------------------------------------------------------------------------------------------------------------------#
#Customer 
@app.route('/loginCustomer', methods = ['GET', 'POST']) 
def loginCustomer():

	error = None

	if request.method == 'POST': 
		
		customer = Customer.query.filter_by(username=request.form['customerUsername']).first()
		
		if customer is None: 
			error = "Invalid Username" 

		elif request.form['customerPassword'] != customer.password:
				error = "Invalid Password"
		
		else:
			flash('A staff member was logged in')
			session['customer_id'] = customer.id
			customerEvents = Event.query.filter_by(customer_id = session['customer_id']).all()
			return render_template('customerLandingPage.html', customerEvents = customerEvents)

	return render_template('loginCustomer.html', error = error)

@app.route('/signupCustomer', methods = ['POST']) 
def signupCustomer():

	customer = Customer(request.form['cUsername'], request.form['cPassword'])
	db.session.add(customer)
	db.session.commit()
	session['customer_id'] = customer.id
	customerEvents = Event.query.filter_by(customer_id = session['customer_id']).all()
	return render_template('customerLandingPage.html', customerEvents = customerEvents)


# Function to log the customer out or create event viewable from customer landing page
@app.route('/customerLandingPage<functionality><eventID>', methods = ['POST', 'GET'])
def customerFunctions(functionality, eventID):

	if functionality == "logout": 
		return render_template('login.html')

	elif functionality == "createEvent":
		return render_template('create_event.html')

	else:
		customerEvent = Event.query.filter_by(id = eventID).first()
		db.session.delete(customerEvent)
		db.session.commit()
		customerEvents = Event.query.filter_by(customer_id = session['customer_id']).all()
		return render_template('customerLandingPage.html', customerEvents = customerEvents)


	
@app.route('/create_event<what>', methods = ['POST'])
def createEvent(what):

	if what =="logout":
		return render_template('login.html')

	else:
		error = None

		eventDate = request.form['eventDate']

		events = Event.query.all()

		for event in events: 
			if event.date == eventDate:
				error = "There is already an event scheduled on that day, please enter new date"
			
		if error == None:
			db.session.add(Event(request.form['eventName'], request.form['eventDate'], session['customer_id'], 0,))
			db.session.commit()
			customerEvents = Event.query.filter_by(customer_id = session['customer_id']).all()
			return render_template('customerLandingPage.html', customerEvents = customerEvents)

		else: 
			return render_template("create_event.html", error = error)


