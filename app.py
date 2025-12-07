from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from werkzeug.utils import secure_filename
from db_config import db_config
import resume_parser # <--- IMPORT IT HERE
from collections import Counter # Helps us count things easily

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'align_project_secret_key_2024'

# Check if 'uploads' folder exists; if not, create it.
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Database Connection (UPDATED)
def get_db_connection():
    # We unpack the dictionary using ** to pass arguments cleanly
    return mysql.connector.connect(**db_config)

# ... rest of your code remains the same ...


# --- ROUTE 1: The New Landing Page (Public) ---
@app.route('/')
def index():
    # This loads the NEW split-screen file you just made
    return render_template('index.html')

# --- ROUTE 2: The Analyzer Tool (Protected) ---
# --- ROUTE: Analyzer (Handles both Viewing the Page AND Uploading) ---
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    # 1. Security Check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 2. If the user is just VIEWING the page (GET)
    if request.method == 'GET':
        return render_template('analyze.html')

    # 3. If the user clicked "Run Analysis" (POST)
    if request.method == 'POST':
        user_id = session['user_id']
        
        if 'resume' not in request.files:
            return 'No file part'
        
        file = request.files['resume']
        job_description = request.form['job_description']
        
        if file.filename == '':
            return 'No selected file'

        if file:
            # Save File
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # NLP Logic
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT skill_name FROM Skill_Master")
            db_skills = [row[0] for row in cursor.fetchall()]
            
            resume_data = resume_parser.parse_resume(filepath, db_skills)
            jd_skills = resume_parser.extract_skills(job_description, db_skills)
            
            # Scoring
            if len(jd_skills) > 0:
                matched_skills = set(resume_data['skills']).intersection(set(jd_skills))
                score = (len(matched_skills) / len(jd_skills)) * 100
                suggestions = f"Missing skills: {', '.join(list(set(jd_skills) - matched_skills))}"
            else:
                score = 0
                suggestions = "Job description contained no known keywords."

            # Database Saving
            cursor.execute("INSERT INTO Job_Postings (user_id, job_description) VALUES (%s, %s)",
                           (user_id, job_description))
            job_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO Resumes (user_id, filename, raw_text) VALUES (%s, %s, %s)",
                           (user_id, file.filename, resume_data['raw_text']))
            resume_id = cursor.lastrowid
            
            skills_str = ", ".join(resume_data['skills'])
            cursor.execute("INSERT INTO Extracted_Data (resume_id, skills_found) VALUES (%s, %s)",
                           (resume_id, skills_str))
            
            cursor.execute("""
                INSERT INTO Analysis_Results (resume_id, job_id, skill_score, formatting_score, overall_score, suggestions)
                VALUES (%s, %s, %s, 90, %s, %s)
            """, (resume_id, job_id, score, score, suggestions))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return redirect(url_for('dashboard'))

# --- ROUTE 3: Dashboard (View Results) ---
@app.route('/dashboard')
def dashboard():
    # 1. Security Check
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 2. SQL Query (Same as before)
    query = """
        SELECT 
            u.name, 
            r.filename, 
            ar.overall_score, 
            ar.suggestions, 
            COALESCE(ed.skills_found, '') as skills_found
        FROM Users u
        JOIN Resumes r ON u.user_id = r.user_id
        JOIN Analysis_Results ar ON r.resume_id = ar.resume_id
        LEFT JOIN Extracted_Data ed ON r.resume_id = ed.resume_id
        WHERE u.user_id = %s
        ORDER BY r.upload_date DESC
    """
    
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    conn.close()

    # 3. PYTHON LOGIC: Find the Top Skill
    all_skills = []
    for row in results:
        # If skills exist, split them by comma (e.g., "Python, SQL" -> ["Python", "SQL"])
        if row['skills_found']:
            skills_list = row['skills_found'].split(',')
            # Strip whitespace and add to our massive list
            all_skills.extend([s.strip() for s in skills_list])
    
    # Count them and find the most common one
    if all_skills:
        # .most_common(1) returns [('Python', 5)] so we grab [0][0]
        top_skill = Counter(all_skills).most_common(1)[0][0]
    else:
        top_skill = "None"

    # 4. Render Template (Pass 'top_skill' to HTML)
    return render_template('dashboard.html', results=results, top_skill=top_skill)

# --- ROUTE: Registration Page ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash("Email already registered! Please login.", "danger")
        else:
            # Insert new user
            cursor.execute("INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)", 
                           (name, email, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        
        conn.close()
    return render_template('register.html')

# --- ROUTE: Login Page ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Create Session Data
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            return redirect(url_for('analyze'))
        else:
            flash("Invalid email or password", "danger")
            
    return render_template('login.html')

# --- ROUTE: Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)