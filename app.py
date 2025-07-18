from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ------------------ DB Setup ------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_id TEXT,
            quotation TEXT,
            location TEXT,
            diagram_file TEXT,
            start_date TEXT,
            end_date TEXT,
            vendor_name TEXT,
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

# Run once at startup
init_db()

# ------------------ Routes ------------------

@app.route('/')
def home():
    return redirect(url_for('project_management'))

@app.route('/project')
def project_management():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    return render_template('project.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project():
    conn = get_db()
    cur = conn.cursor()

    # Auto-generate enquiry ID like VE/TN/2526/E001
    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0] + 1
    enquiry_id = f"VE/TN/2526/E{str(count).zfill(3)}"

    quotation = request.form['quotation']
    location = request.form['location']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    vendor_name = request.form['vendor_name']
    gst = request.form['gst']
    address = request.form['address']
    incharge = request.form.get('incharge')
    contact = request.form.get('contact')
    email = request.form.get('email')
    notes = request.form.get('notes')

    # Handle file upload
    file = request.files['diagram_file']
    filename = ''
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    cur.execute('''
        INSERT INTO projects (
            enquiry_id, quotation, location, diagram_file,
            start_date, end_date, vendor_name, gst, address,
            incharge, contact, email, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        enquiry_id, quotation, location, filename,
        start_date, end_date, vendor_name, gst, address,
        incharge, contact, email, notes
    ))

    conn.commit()
    conn.close()
    return redirect(url_for('project_management'))

# ------------------ Run Server ------------------
if __name__ == '__main__':
    app.run(debug=True)
