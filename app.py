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
    conn = get_db()
    cur = conn.cursor()

    data = request.form
    project_id = data.get('project_id')
    diagram_file = request.files.get('source_diagram')
    diagram_path = data.get('existing_diagram')

    if diagram_file and diagram_file.filename:
        diagram_path = os.path.join("static/uploads", diagram_file.filename)
        diagram_file.save(diagram_path)

    cur.execute("""
        UPDATE projects SET
            quotation=?, project_location=?, source_diagram=?, start_date=?, end_date=?,
            vendor_id=?, gst=?, address=?, incharge=?, contact_number=?, mail_id=?, notes=?
        WHERE id=?
    """, (
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
        data.get('notes'),
        project_id
    ))
    conn.commit()
    conn.close()
    flash("Project updated!", "success")
    return redirect(url_for('project_management'))

@app.route('/delete_project', methods=['POST'])
def delete_project():
    project_id = request.form.get('project_id')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    flash("Project deleted!", "danger")
    return redirect(url_for('project_management'))
# -------------------- Run --------------------

if __name__ == '__main__':
    app.run(debug=True)
