from flask import Flask, render_template, request, redirect, url_for, session, flash,send_from_directory
import mysql.connector
import os
from werkzeug.utils import secure_filename
from db_config import db_config
import resume_parser # <--- IMPORT IT HERE
from collections import Counter # Helps us count things easily
import MySQLdb.cursors


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'align_project_secret_key_2024'

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Check if 'uploads' folder exists; if not, create it.
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



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
    # 1. Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        job_title = request.form['job_title']
        
        # 2. Get Both Files
        resume_file = request.files['resume']
        jd_file = request.files['jd_file']

        if resume_file and jd_file:
            # 3. Setup Separate Folders
            base_upload_path = app.config['UPLOAD_FOLDER'] # 'uploads'
            resume_folder = os.path.join(base_upload_path, 'resumes')
            jd_folder = os.path.join(base_upload_path, 'jds')
            
            # Create folders if they don't exist
            os.makedirs(resume_folder, exist_ok=True)
            os.makedirs(jd_folder, exist_ok=True)

            # 4. Save Files
            resume_filename = secure_filename(resume_file.filename)
            jd_filename = secure_filename(jd_file.filename)
            
            resume_path = os.path.join(resume_folder, resume_filename)
            jd_path = os.path.join(jd_folder, jd_filename)
            
            resume_file.save(resume_path)
            jd_file.save(jd_path)

            # 5. Load Skills from Database (The Dictionary)
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT skill_name FROM Skill_Master")
            db_skills = [row['skill_name'] for row in cursor.fetchall()]

            # 6. Parse RESUME (Using resume_parser.py)
            # Returns: skills, education, experience, etc.
            resume_data = resume_parser.parse_resume(resume_path, db_skills)

            # 7. Parse JOB DESCRIPTION (Extract Text + Skills)
            jd_text = ""
            if jd_filename.endswith('.pdf'):
                jd_text = resume_parser.extract_text_from_pdf(jd_path)
            elif jd_filename.endswith('.docx'):
                jd_text = resume_parser.extract_text_from_docx(jd_path)
            
            # Extract skills from the JD text
            jd_skills = resume_parser.extract_skills(jd_text, db_skills)

            # 8. Calculate Scoring (Set Theory)
            resume_skill_set = set(resume_data['skills'])
            jd_skill_set = set(jd_skills)
            
            if len(jd_skill_set) > 0:
                match_count = len(resume_skill_set.intersection(jd_skill_set))
                skill_score = (match_count / len(jd_skill_set)) * 100
            else:
                skill_score = 0
            
            missing_skills = list(jd_skill_set - resume_skill_set)
            
            # Weighted Score (70% Skills, 30% Formatting - Formatting is static for now)
            formatting_score = 80 
            overall_score = (skill_score * 0.7) + (formatting_score * 0.3)

            # 9. Database Operations
            
            # A. Save Job Posting (UPDATED)
            # We save 'jd_filename' instead of 'jd_text'
            cursor.execute("INSERT INTO Job_Postings (user_id, job_title, filename) VALUES (%s, %s, %s)",
                           (user_id, job_title, jd_filename))
            job_id = cursor.lastrowid

            # B. Save Resume (NO raw_text, just filename)
            cursor.execute("INSERT INTO Resumes (user_id, filename) VALUES (%s, %s)",
                           (user_id, resume_filename))
            resume_id = cursor.lastrowid

            # C. Save Extracted Data (Skills, Edu, Exp)
            skills_str = ", ".join(resume_data['skills'])
            cursor.execute("""
                INSERT INTO Extracted_Data (resume_id, skills_found, education, experience) 
                VALUES (%s, %s, %s, %s)
            """, (
                resume_id, 
                skills_str, 
                resume_data.get('education', 'Not Mentioned'),  # <--- Safe Access
                resume_data.get('experience', 'Not Mentioned')  # <--- Safe Access (Fix this too!)
            ))

            # D. Save Analysis Results
            suggestions = f"Missing Skills: {', '.join(missing_skills)}"
            cursor.execute("""
                INSERT INTO Analysis_Results (resume_id, job_id, skill_score, formatting_score, overall_score, suggestions)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (resume_id, job_id, skill_score, formatting_score, overall_score, suggestions))

            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('dashboard'))

    return render_template('analyze.html')

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
            ar.result_id, 
            ar.overall_score, 
            ar.suggestions,
            ed.skills_found,                  -- <--- THIS FIXES THE KEYERROR
            u.name as candidate_name,
            DATE_FORMAT(jp.posted_date, '%d %b %Y') as date,
            jp.job_title,
            jp.filename as jd_filename,       -- Fetch JD File
            r.filename as resume_filename     -- Fetch Resume File
        FROM Analysis_Results ar
        JOIN Job_Postings jp ON ar.job_id = jp.job_id
        JOIN Resumes r ON ar.resume_id = r.resume_id
        JOIN Users u ON r.user_id = u.user_id
        JOIN Extracted_Data ed ON r.resume_id = ed.resume_id  -- <--- JOIN NEEDED FOR SKILLS
        WHERE ar.resume_id IN (SELECT resume_id FROM Resumes WHERE user_id = %s)
        ORDER BY jp.posted_date DESC
    """
    
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    
    cursor.close()
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
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        else:
            cursor.execute('INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)', (username, email, password))
            conn.commit()  # <--- Commit using 'conn'
            msg = 'You have successfully registered!'
        
        cursor.close()
        conn.close()

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

# --- ROUTE: Login Page ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        # 1. Open Connection
        conn = get_db_connection()
        # 2. Create Cursor (dictionary=True WORKS here!)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM Users WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        
        # 3. Close Connection (Important!)
        cursor.close()
        conn.close()

        if account:
            print("DEBUG CHECK:", account)
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['name'] = account['name']
            return redirect(url_for('analyze'))
        else:
            msg = 'Incorrect email or password!'
            
    return render_template('login.html', msg=msg)

# --- ROUTE: Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/view_resume/<filename>')
def view_resume(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Point to the 'uploads/resumes' folder
    resume_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes')
    
    return send_from_directory(resume_folder, filename)

@app.route('/view_jd/<filename>')
def view_jd(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Point to the 'uploads/jds' folder
    jd_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'jds')
    
    return send_from_directory(jd_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)