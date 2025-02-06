from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin   
# Initialize the database instance
db = SQLAlchemy()

# Define the User model
class Register(UserMixin,db.Model):
    __tablename__="register"
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Unique constraint
    password = db.Column(db.String(255), nullable=False)  # Store hashed password
    created_at=db.Column(db.DateTime,default=datetime.now)
    recipes = db.relationship('uploads_of_users', backref='user', lazy=True,primaryjoin="Register.id == uploads_of_users.user_id")
    profile_settings=db.relationship('logsOf_profile_settings_of_users', backref='user', lazy=True,primaryjoin="Register.id == logsOf_profile_settings_of_users.user_id")
    def __repr__(self):
        return f"<Register id={self.id}, full_name={self.full_name}, email={self.email}>"

class uploads_of_users(db.Model):
    __tablename__='recipes'
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    recipe_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=False,default="/static/img/profile.jpg")
    upload_date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'))  # Foreign key to associate with a user
    def __repr__(self):
        return f"<Recipe {self.recipe_name} by User {self.user_id}>"
class logsOf_profile_settings_of_users(db.Model):
    __tablename__='profile_settings'
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    profile_name= db.Column(db.String(100), nullable=False)
    profile_picture=db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('register.id'))  # Foreign key to associate with a user
   




