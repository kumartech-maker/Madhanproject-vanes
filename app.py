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

@app.route('/create_project', methods=['POST'])
def create_project():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0] + 1
    enquiry_id = f"ve/TN/2526/e{str(count).zfill(3)}"
    print("Generated Enquiry ID:", enquiry_id)

    quotation = request.form.get('quotation')
    project_location = request.form.get('project_location')
    source_diagram = request.files.get('source_diagram')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    vendor_id = request.form.get('vendor_id')
    gst = request.form.get('gst')
    address = request.form.get('address')
    incharge = request.form.get('incharge')
    contact_number = request.form.get('contact_number')
    mail_id = request.form.get('mail_id')
    notes = request.form.get('notes')

    diagram_path = None
    if source_diagram and source_diagram.filename:
        diagram_path = os.path.join("static/uploads", source_diagram.filename)
        source_diagram.save(diagram_path)

    cur.execute("""
        INSERT INTO projects (enquiry_id, quotation, project_location, source_diagram, start_date, end_date, vendor_id, gst, address, incharge, contact_number, mail_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (enquiry_id, quotation, project_location, diagram_path, start_date, end_date, vendor_id, gst, address, incharge, contact_number, mail_id, notes))

    conn.commit()
    conn.close()
    flash('Project added successfully!', 'success')
    return redirect(url_for('project_management'))

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
