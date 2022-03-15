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


# Initializes database
@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	print('Intialized Database')



@app.before_request
def before_request():
	g.user = None
	if 'customerId' in session:
		g.user = Customer.query.filter_by(customerId=session['customerId']).first()
	

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
			return render_template('ownerLandingPage.html')

	return render_template('login.html', error=error)

# Creates a new staff member in the database
@app.route('/create_staff', methods = ['POST']) 
def createStaff():

	db.session.add(Staff(request.form['staffUsername'], request.form['staffPassword']))
	db.session.commit()
	return render_template('ownerLandingPage.html')

# Link to create a staff member
@app.route('/ownerLandingPage<functionality>', methods = ["GET"])
def createStaffOrLogout(functionality):

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
			return render_template('staffLandingPage.html')
	
	return render_template('staffLandingPage.html', error = error)


# Function to log staff member out, viewable from staff landing page
@app.route('/staffLandingPage')
def logoutStaff(): 

	flash('You were logged out')
	return render_template('login.html')



# ----------------------------------------------------------------------------------------------------------------------------------------------#
#Customer 
@app.route('/signupCustomer', methods = ['POST']) 
def signupCustomer():

	customer = Customer(request.form['cUsername'], request.form['cPassword'])
	db.session.add(customer)
	db.session.commit()
	session['customer_id'] = customer.id
	return render_template('customerLandingPage.html')


# Function to log the customer ut, viewable from customer landing page
@app.route('/customerLandingPage<functionality>')
def customerFunction(functionality): 
	
	if functionality == "logout":
		return render_template('login.html')

	else: 
		return render_template('create_event.html')

	
@app.route('/create_event', methods = ['POST'])
def createEvent():

	db.session.add(Event(request.form['eventName'], request.form['eventDate'], session['customer_id']))
	db.session.commit()
	return render_template('customerLandingPage.html')




