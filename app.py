from flask import Flask,render_template,request,jsonify,redirect,url_for
from flask_sqlalchemy import SQLAlchemy #for database used in models.py
from models import db,Register,uploads_of_users,logsOf_profile_settings_of_users
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.pool import StaticPool
import os
#static folder path and assigining all to app

#template and 
app=Flask(__name__,template_folder="C:/Users/prave/Desktop/Flask/RCP/venv/templates",static_folder="C:/Users/prave/Desktop/Flask/RCP/venv/static")

#creates sql databse in instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'# Using SQLite and handle concurrent access

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': StaticPool
}
#session confirgurations
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
app.config['SECRET_KEY'] = '1309edqe3dwi~!W'


Session(app)

db.init_app(app)#inidlaise the database for app

#migrations are done for app database if there is schema or structural changes in data base so it will reflect in db
migrate=Migrate(app,db)
  # This creates the tables based on the defined models
    # print("Database created successfully!")
    # new_user=Register(full_name="pkr",email="olp@mail",password="mypass")
    # db.session.add(new_user)
    # db.session.commit()


login_manager=LoginManager()
login_manager.login_view="login"
login_manager.init_app(app)

#it will take the reguster details from html page and store it in db and 
# checks if user already exists or not and checks nonempty input values
@app.route("/submit_Register_Details", methods=["POST"])
def get_register_details():
    full_name=request.form.get("name")
    email=request.form.get("email")
    password=request.form.get("password")
    confirm_password=request.form.get("confirm-password")

    user= Register.query.filter_by(email=email).first()
    
    hashed_password = generate_password_hash(password)
    if password!=confirm_password:
        return jsonify({'error':"Password Mismatch"}),400
    
    if not full_name or not email or not password:#checks all fields are there or not
        return jsonify({'error':"All fileds are required!!"}),400
    
    if "@" not in email:#validates email
        return jsonify({'error':"Invalid Email format!!"}),400
    
    if len(password)<6:
        return jsonify({'error':"Password must be greater than 6 characters"}),400
    
    if user:
        return jsonify({'message': 'Email is already registered'}), 200
    
    try:
        new_user=Register(full_name=full_name,email=email,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback transaction to avoid locking the database
        print("Database Error:", e)  # Print the actual error
        return jsonify({'error': f"Error occurred: {str(e)}"}), 500
    return  redirect("/login")
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))

#it will check the login details and validates 
#also checks user in db or not
#if all are passed a session is created for user with user full name and redirects to home page
@app.route("/submit_loginDetails", methods=["POST"])
def check_login_details():
    email=request.form.get("email")
    password=request.form.get("password")

    if not email or not password:#checks all fields are there or not
        return jsonify({'error':"All fileds are required!!"}),400
    
    if "@" not in email:#validates email
        return jsonify({'error':"Invalid Email format!!"}),400
    
    user = Register.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Email is not registered'}), 200
    #checking given password and db"s password
    if not check_password_hash(user.password,password):
        return jsonify({'message': 'wrong Email/Password check again!!'}), 200
    login_user(user)
    return redirect("/home")

#main Home page of  the websute
#it checks  if there is a session for user if not u=reditects to login page
@app.route("/home")
def home():

    return render_template("home.html")

#root page which directs to index page
@app.route("/")
def index():
    return render_template("index.html")

#reguster page
@app.route("/register")
def register():
    return render_template('register.html')

#login page
@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')



@app.route("/dashboard")
def dashboard():
    user = logsOf_profile_settings_of_users.query.filter_by(user_id=current_user.id).first()
    profile_name = user.profile_name if user else "Guest"
    profile_picture = user.profile_picture if user else "/static/img/profile.jpg"
    return render_template("dashboard.html",profile_name=profile_name,profile_picture=profile_picture)


@app.route("/feedback")
@login_required
def feedback():
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    return render_template("feedback.html")

@login_required
@app.route("/upload")
def upload():
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    return render_template("upload.html")
@app.route("/upload_details",methods=["POST"])
def upload_details():
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    recipe_name=request.form.get("recipeName")
    image_file = request.files.get('recipeImage')
    ALLOWED_EXTENSIONS={'jpg','png','gif', 'jpeg'}
    PROFILE_PICTURE_FOLDER = 'uploads'
    app.config['PROFILE_PICTURE_FOLDER'] = PROFILE_PICTURE_FOLDER
    if not os.path.exists(app.config['PROFILE_PICTURE_FOLDER']):
        os.makedirs(app.config['PROFILE_PICTURE_FOLDER'])    

    def allowed_file(filename):
    # Ensure the file has an extension and it's one of the allowed types
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    if image_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config['PROFILE_PICTURE_FOLDER'], filename)
        # Save the file
        image_file.save(image_path)
        description=request.form.get("description") 
        new_recipe=uploads_of_users(recipe_name=recipe_name,image_filename=image_path,description=description,user_id=current_user.id)
        db.session.add(new_recipe)
        db.session.commit()
        return jsonify({'message': 'File successfully uploaded', 'path': image_path}), 200
# Create the folder if it doesn't exist
    # if not os.path.exists("UPLOAD_FOLDER"):
    #     os.makedirs("UPLOAD_FOLDER")
    #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #     image_file.save(image_path)
    # else:
    #     return jsonify({'error': 'Image is required and must be valid'}), 400


    if not recipe_name  or not description:
        return jsonify({'error':"allFields  must be filled"}),400
    
with app.app_context():
    db.create_all()
 
@app.route("/profile_settings")
def profile_setting_page():
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    return render_template("profile_settings.html")
@app.route("/change_profile_settings",methods=["POST"])
def profile_settings():
    if not current_user.is_authenticated:
        return app.login_manager.unauthorized()
    profile_name=request.form.get("profileName")
    profile_picture = request.files.get('profilePicture')
    ALLOWED_EXTENSIONS={'jpg','png','gif', 'jpeg'}
    PROFILE_PICTURE_FOLDER = 'uploads'
    app.config['PROFILE_PICTURE_FOLDER'] = PROFILE_PICTURE_FOLDER
    if not os.path.exists(app.config['PROFILE_PICTURE_FOLDER']):
        os.makedirs(app.config['PROFILE_PICTURE_FOLDER'])    

    def allowed_file(filename):
    # Ensure the file has an extension and it's one of the allowed types
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    if profile_picture.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if profile_picture and allowed_file(profile_picture.filename):
        filename = secure_filename(profile_picture.filename)
        image_path = os.path.join(app.config['PROFILE_PICTURE_FOLDER'], filename)
        # Save the file
        profile_picture.save(image_path)
        new_recipe=logsOf_profile_settings_of_users(profile_name=profile_name,profile_picture=image_path,user_id=current_user.id)
        db.session.add(new_recipe)
        db.session.commit()
        return redirect("/dashboard")
# Close sessions after each request
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

#it will create all db tables which are used till now
with app.app_context():
    db.create_all()


#main
if __name__=="__main__":
    app.run(debug=True)

