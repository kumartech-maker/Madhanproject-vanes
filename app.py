from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------- DB --------------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS project (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_id TEXT,
            quotation TEXT,
            location TEXT,
            source_diagram TEXT,
            start_date TEXT,
            end_date TEXT,
            vendor TEXT,
            gst TEXT,
            address TEXT,
            incharge TEXT,
            contact TEXT,
            email TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------- Dummy Vendors --------------------

dummy_vendors = [
    {'name': 'Vanes Engineering', 'gst': '29AABCU9603R1ZK', 'address': 'Chennai, Tamil Nadu'},
    {'name': 'Kumar Duct Systems', 'gst': '07AAACG1234F1ZV', 'address': 'Delhi, India'},
    {'name': 'Sree Air Tech', 'gst': '33AAGCS4445K1Z2', 'address': 'Coimbatore, TN'}
]

# -------------------- Routes --------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == 'admin@example.com' and password == 'admin123':
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/project')
def project_management():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM project ORDER BY id DESC")
    projects = cur.fetchall()
    conn.close()
    return render_template('project.html', projects=projects, vendors=dummy_vendors)

@app.route('/add_project', methods=['POST'])
def add_project():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = request.form
    file = request.files['source_diagram']
    file_name = ""

    if file and file.filename != "":
        file_name = datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
        file.save(os.path.join(UPLOAD_FOLDER, file_name))

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO project (enquiry_id, quotation, location, source_diagram,
        start_date, end_date, vendor, gst, address,
        incharge, contact, email, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('enquiry_id'), data.get('quotation'), data.get('location'), file_name,
        data.get('start_date'), data.get('end_date'), data.get('vendor'),
        data.get('gst'), data.get('address'), data.get('incharge'),
        data.get('contact'), data.get('email'), data.get('notes')
    ))
    conn.commit()
    conn.close()
    flash("Project added successfully!", "success")
    return redirect(url_for('project_management'))

# -------------------- Run --------------------

if __name__ == '__main__':
    app.run(debug=True)
