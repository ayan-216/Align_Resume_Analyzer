-- DATABASE SETUP SCRIPT FOR ALIGN
-- Run this in MySQL Workbench to set up the project database

-- 1. Create and Select Database
CREATE DATABASE IF NOT EXISTS ResumeDB;
USE ResumeDB;

-- 2. Create Users Table
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- In production, use hashed passwords
    role ENUM('admin', 'student') DEFAULT 'student'
);

-- 3. Create Job Postings Table
CREATE TABLE IF NOT EXISTS Job_Postings (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    job_title VARCHAR(100) DEFAULT 'Unknown Role',
    job_description TEXT,
    posted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 4. Create Resumes Table
CREATE TABLE IF NOT EXISTS Resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    filename VARCHAR(255),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 5. Create Extracted Data Table
CREATE TABLE IF NOT EXISTS Extracted_Data (
    extract_id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT UNIQUE,
    skills_found TEXT,
    education TEXT,
    experience TEXT,
    FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id) ON DELETE CASCADE
);

-- 6. Create Analysis Results Table
CREATE TABLE IF NOT EXISTS Analysis_Results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT UNIQUE,
    job_id INT,
    skill_score DECIMAL(5,2),
    formatting_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    suggestions TEXT,
    FOREIGN KEY (resume_id) REFERENCES Resumes(resume_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES Job_Postings(job_id) ON DELETE SET NULL
);

-- 7. Create Skill Master Table (The Dictionary)
CREATE TABLE IF NOT EXISTS Skill_Master (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(50) UNIQUE,
    category VARCHAR(50)
);

-- ==========================================
-- SEED DATA: POPULATE SKILLS (CRITICAL)
-- ==========================================

TRUNCATE TABLE Skill_Master; -- Clears old data to prevent duplicates

INSERT INTO Skill_Master (skill_name, category) VALUES 
-- Programming Languages
('Python', 'Technical'), ('Java', 'Technical'), ('C++', 'Technical'),
('JavaScript', 'Web'), ('TypeScript', 'Web'), ('SQL', 'Technical'),
('HTML', 'Web'), ('CSS', 'Web'), ('PHP', 'Web'), ('Ruby', 'Technical'),
('Swift', 'Mobile'), ('Kotlin', 'Mobile'), ('Go', 'Technical'), ('Rust', 'Technical'),

-- Frameworks & Libraries
('React', 'Web'), ('Angular', 'Web'), ('Vue', 'Web'), ('Node.js', 'Web'),
('Flask', 'Web'), ('Django', 'Web'), ('Spring Boot', 'Web'),
('Pandas', 'Data Science'), ('NumPy', 'Data Science'), ('TensorFlow', 'Data Science'),
('PyTorch', 'Data Science'), ('Scikit-learn', 'Data Science'),

-- Databases
('MySQL', 'Database'), ('PostgreSQL', 'Database'), ('MongoDB', 'Database'),
('Oracle', 'Database'), ('Redis', 'Database'),

-- Cloud & DevOps
('AWS', 'Cloud'), ('Azure', 'Cloud'), ('Google Cloud', 'Cloud'),
('Docker', 'DevOps'), ('Kubernetes', 'DevOps'), ('Jenkins', 'DevOps'),
('Git', 'Tools'), ('Linux', 'OS'),

-- Soft Skills & Business
('Communication', 'Soft Skill'), ('Leadership', 'Soft Skill'),
('Teamwork', 'Soft Skill'), ('Problem Solving', 'Soft Skill'),
('Project Management', 'Business'), ('Agile', 'Methodology'),
('Scrum', 'Methodology'), ('Excel', 'Business'), ('Tableau', 'Data Science'),
('Power BI', 'Data Science');