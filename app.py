from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------- DB --------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Create projects table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_id TEXT,
            quotation TEXT,
            project_location TEXT,
            source_diagram TEXT,
            start_date TEXT,
            end_date TEXT,
            vendor_id TEXT,
            gst TEXT,
            address TEXT,
            incharge TEXT,
            contact_number TEXT,
            mail_id TEXT,
            notes TEXT
        )
    ''')

    # Create vendors table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gst TEXT,
            address TEXT
        )
    ''')

    # Optional: Add dummy vendors if table is empty
    cur.execute("SELECT COUNT(*) FROM vendors")
    if cur.fetchone()[0] == 0:
        dummy_vendors = [
            ('Vanes Engineering', '29AABCU9603R1ZK', 'Chennai, Tamil Nadu'),
            ('Kumar Duct Systems', '07AAACG1234F1ZV', 'Delhi, India'),
            ('Sree Air Tech', '33AAGCS4445K1Z2', 'Coimbatore, TN')
        ]
        cur.executemany("INSERT INTO vendors (name, gst, address) VALUES (?, ?, ?)", dummy_vendors)

    conn.commit()
    conn.close()

init_db()

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

@app.route('/get_next_enquiry_id')
def get_next_enquiry_id():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0] + 1
    enquiry_id = f"VE/TN/2526/E{str(count).zfill(3)}"
    return jsonify({"enquiry_id": enquiry_id})

@app.route('/project')
def project_management():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = cur.fetchall()
    cur.execute("SELECT * FROM vendors")
    vendors = cur.fetchall()
    conn.close()
    return render_template('project.html', projects=projects, vendors=vendors)

@app.route('/create_project', methods=['POST'])
def create_project():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0] + 1
    enquiry_id = f"VE/TN/2526/E{str(count).zfill(3)}"

    data = request.form
    diagram_file = request.files.get('source_diagram')
    diagram_path = None

    if diagram_file and diagram_file.filename:
        diagram_path = os.path.join("static/uploads", diagram_file.filename)
        diagram_file.save(diagram_path)

    cur.execute("""
        INSERT INTO projects (
            enquiry_id, quotation, project_location, source_diagram, start_date, end_date,
            vendor_id, gst, address, incharge, contact_number, mail_id, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        enquiry_id,
        data.get('quotation'),
        data.get('project_location'),
        diagram_path,
        data.get('start_date'),
        data.get('end_date'),
        data.get('vendor_id'),
        data.get('gst'),
        data.get('address'),
        data.get('incharge'),
        data.get('contact_number'),
        data.get('mail_id'),
        data.get('notes')
    ))
    conn.commit()
    conn.close()
    flash("Project created successfully!", "success")
    return redirect(url_for('project_management'))

@app.route('/edit_project', methods=['POST'])
def edit_project():
    project_id = request.form.get('project_id')
    quotation = request.form.get('quotation')
    project_location = request.form.get('project_location')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    vendor_id = request.form.get('vendor_id')
    gst = request.form.get('gst')
    address = request.form.get('address')
    incharge = request.form.get('incharge')
    contact_number = request.form.get('contact_number')
    mail_id = request.form.get('mail_id')
    notes = request.form.get('notes')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE projects SET quotation=?, project_location=?, start_date=?, end_date=?, 
        vendor_id=?, gst=?, address=?, incharge=?, contact_number=?, mail_id=?, notes=?
        WHERE id=?
    """, (quotation, project_location, start_date, end_date, vendor_id, gst, address, incharge, contact_number, mail_id, notes, project_id))

    conn.commit()
    conn.close()
    flash("Project updated successfully!", "success")
    return redirect(url_for('project_management'))

@app.route('/delete_project', methods=['POST'])
def delete_project():
    project_id = request.form.get('project_id')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    flash("Project deleted successfully!", "success")
    return redirect(url_for('project_management'))

@app.route('/init_db')
def trigger_db_init():
    init_db()
    return "Database initialized!"

# -------------------- Run --------------------

if __name__ == '__main__':
    app.run(debug=True)
