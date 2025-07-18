from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

UPLOAD_FOLDER = 'static/uploads'
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


@app.route('/get_next_enquiry_id')
def get_next_enquiry_id():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM project")
    count = cur.fetchone()[0] + 1
    enquiry_id = f"ve/TN/2526/e{str(count).zfill(3)}"
    return jsonify({"enquiry_id": enquiry_id})

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
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()

    # Auto-generate Enquiry ID
    cur.execute("SELECT COUNT(*) FROM project")
    count = cur.fetchone()[0] + 1
    enquiry_id = f"ve/TN/2526/e{str(count).zfill(3)}"

    # Get form data
    quotation = request.form.get('quotation')
    location = request.form.get('project_location')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    vendor = request.form.get('vendor_id')
    gst = request.form.get('gst')
    address = request.form.get('address')
    incharge = request.form.get('incharge')
    contact = request.form.get('contact_number')
    email = request.form.get('mail_id')
    notes = request.form.get('notes')

    # Handle file upload
    source_diagram = request.files.get('source_diagram')
    file_name = ""
    if source_diagram and source_diagram.filename:
        file_name = datetime.now().strftime("%Y%m%d%H%M%S_") + source_diagram.filename
        source_diagram.save(os.path.join(UPLOAD_FOLDER, file_name))

    # Insert into DB
    cur.execute('''
        INSERT INTO project (enquiry_id, quotation, location, source_diagram,
        start_date, end_date, vendor, gst, address,
        incharge, contact, email, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        enquiry_id, quotation, location, file_name,
        start_date, end_date, vendor, gst, address,
        incharge, contact, email, notes
    ))

    conn.commit()
    conn.close()
    flash("Project added successfully!", "success")
    return redirect(url_for('project_management'))


@app.route('/edit_project', methods=['POST'])
def edit_project():
    # Temporary placeholder
    flash("Edit project logic not implemented yet.", "warning")
    return redirect(url_for('project_management'))

# -------------------- Run --------------------

if __name__ == '__main__':
    app.run(debug=True)
