from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO,emit,send
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'secret'
db_path = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(db_path, 'database.db'))
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Employee Model (Example)
class employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    emp_name = db.Column(db.String(150), nullable=False)

# Late Model (Example)
class late(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    emp_name = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.String(150), nullable=False)
    from_time = db.Column(db.String(150), nullable=False)
    to_time = db.Column(db.String(150), nullable=False)
    hod_approval = db.Column(db.String(150))
    hr_approval = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
# Leave Model (Example)
class leave(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    emp_name = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    from_date = db.Column(db.String(150), nullable=False)
    to_date = db.Column(db.String(150), nullable=False)
    hod_approval = db.Column(db.String(150), default=None)
    hr_approval = db.Column(db.String(150), default=None)


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/late_form_page')
def late_form_page():
    return render_template('emp_late.html')


@app.route('/leave_form_page')
def leave_form_page():
    return render_template('emp_leave.html')


@socketio.on('connect')
def handle_connect():
    print('Client Connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')    

@socketio.on('my event')
def show_connect():
    a=10

# Late Form Submission

def serialize_late(late_object):
    return {
        'id': late_object.id,
        'emp_id': late_object.emp_id,
        'emp_name': late_object.emp_name,
        'reason': late_object.reason,
        'from_time': late_object.from_time,
        'to_time': late_object.to_time,
        'hod_approval': late_object.hod_approval,
        'hr_approval': late_object.hr_approval,
        'date': late_object.date.strftime('%Y-%m-%d %H:%M:%S'),  # Convert date to string
    }


@socketio.on('late')
def handle_form_callback(lateDet):
    try:
        new_request=late(emp_id=lateDet['emp_id'],emp_name=lateDet['emp_name'],reason=lateDet['reason'],from_time=lateDet['from_time'],to_time=lateDet['to_time'],hod_approval=None,hr_approval=None)
        db.session.add(new_request)
        db.session.commit()
        all_data = late.query.order_by(late.date).all()
        all_Data = [serialize_late(entry) for entry in all_data]
        print(all_Data)
        emit('late', all_Data, broadcast=True)


    except Exception as e:
        print(f"An error occurred: {str(e)}")


@app.route('/form')
def formfun():
    return render_template('form.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database Created")
    socketio.run(app, debug=True)


    # if request.method == 'POST':
    #     emp_id = request.form.get('emp_id')
    #     emp_name = request.form.get('emp_name')
    #     reason = request.form.get('reason')
    #     from_time_str = request.form.get('from_time')
    #     to_time_str = request.form.get('to_time')

    #     current_time = datetime.now()
    #     current_date = current_time.date()

    #     # Parse form inputs into datetime objects
    #     from_time = datetime.combine(current_date, datetime.strptime(from_time_str, '%H:%M').time())
    #     to_time = datetime.combine(current_date, datetime.strptime(to_time_str, '%H:%M').time())

        # Create a new Late record
        # new_late_record = Late(
        #     emp_id=emp_id,
        #     emp_name=emp_name,
        #     reason=reason,
        #     user_req_time=current_time,
        #     from_time=from_time,
        #     to_time=to_time,
        #     hod_approval=None,
        #     hr_approval=None
        # )

        # db.session.add(new_late_record)
        # db.session.commit()

        # flash('Late record submitted successfully', 'success')

        # return redirect(url_for('index'))


# # Leave Form Submission
# @socketio.on('leave_form')
# def leave_form():
#     if request.method == 'POST':
#         emp_id = request.form.get('emp_id')
#         emp_name = request.form.get('emp_name')
#         reason = request.form.get('reason')
#         from_date_str = request.form.get('from_date')
#         to_date_str = request.form.get('to_date')

#         # Get the current date and time
#         current_time = datetime.now()

#         # Parse form inputs into datetime objects
#         from_date = datetime.strptime(from_date_str, '%d-%m-%Y')
#         to_date = datetime.strptime(to_date_str, '%d-%m-%Y')

#         # Create a new Leave record
#         new_leave_record = Leave(
#             emp_id=emp_id,
#             emp_name=emp_name,
#             reason=reason,
#             user_req_time=current_time,
#             from_date=from_date,
#             to_date=to_date,
#             hod_approval=None,
#             hr_approval=None
#         )

#         db.session.add(new_leave_record)
#         db.session.commit()

#         flash('Leave request submitted successfully', 'success')

#         return redirect(url_for('index'))


# # User Login
# @socketio.on('login')
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         user = User.query.filter_by(email=email).first()

#         if user and bcrypt.check_password_hash(user.password, password):
#             login_user(user)
#             flash('Login successful!', 'success')
#             return redirect(url_for('form'))
#         else:
#             flash('Login failed. Please check your credentials.', 'danger')

#     return render_template('login.html')

# @socketio.on('form')
# def form():

#     return render_template("form.html")

# @socketio.on('Sign_up_page')
# def sign_up_page():
#     return render_template('Sign_up.html')

# @socketio.on('Login_page')
# def login_page():
#     return render_template('Login_Page.html')

# # User Logout
# @socketio.on('  logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out.', 'success')
#     return redirect(url_for('index'))


# Run the application