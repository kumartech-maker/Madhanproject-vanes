from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ Database Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))


@app.route('/project')
def project_management():
    return render_template('project.html')

# ✅ Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # ✅ Dummy credentials check
        if email == 'admin@example.com' and password == 'admin123':
            session['user'] = 'Admin'
            return redirect(url_for('dashboard'))

        # ✅ Check DB (optional for real users)
        user = Employee.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.name
            return redirect(url_for('dashboard'))
        else:
            return "Login Failed. Try again."

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ✅ Run App
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
