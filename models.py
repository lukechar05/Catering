from re import S
from flask_sqlalchemy import SQLAlchemy

# note this should only be created once per project
# to define models in multiple files, put this in one file, and import db into each model, as we import it in flaskr.py
db = SQLAlchemy()


staff_event = db.Table('staff_event', 
    db.Column('staff_id', db.Integer, db.ForeignKey('staff.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)
 
class Staff(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.Text, nullable = False)
    password = db.Column(db.Text, nullable = False)


    events = db.relationship('Event', secondary=staff_event, backref='workers')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return '<Staff{}>'.format(self.id)



class Customer(db.Model): 
    id = db.Column(db.Integer, primary_key = True) 
    username = db.Column(db.Text, nullable = False)
    password = db.Column(db.Text, nullable = False)

    events = db.relationship('Event', backref = 'customer')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return '<Customer{}>'.format(self.id)



class Event(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text, nullable = False)
    date = db.Column(db.Text, nullable = False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable = False)

 
    def __init__(self, name, date, customer_id):
        self.name = name
        self.date = date
        self.customer_id = customer_id
        
    
    def __repr__(self):
        return '<Event{}>'.format(self.id)
    