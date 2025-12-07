import os
import re
from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(file_path):
    """
    Helper function to extract text from PDF files.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """
    Helper function to extract text from DOCX files.
    """
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def clean_text(text):
    """
    Basic NLP preprocessing: lowercase, remove special characters.
    """
    text = text.lower()
    # Remove special characters but keep valid text and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text) 
    return text

def extract_skills(text, db_skills):
    """
    Matches text against database skills (Case Insensitive).
    """
    found_skills = set()
    
    # 1. Convert the entire resume text to lowercase once
    # This ensures 'Python' and 'python' look the same
    text_lower = text.lower()
    
    for skill in db_skills:
        # 2. Check if the skill (in lowercase) exists in the resume text
        if skill.lower() in text_lower:
            # 3. CRITICAL: Add the *original* skill name from the DB
            # This ensures your Dashboard shows "Python" (pretty), not "python" (lowercase)
            found_skills.add(skill)
            
    return list(found_skills)

def extract_contact_info(text):
    """
    Extracts email and phone using Regex (Regular Expressions).
    """
    email = None
    phone = None
    
    # Regex for Email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    if email_match:
        email = email_match.group(0)
        
    # Regex for Phone (Handles various formats like +91, dashes, spaces)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        phone = phone_match.group(0)
        
    return email, phone

def parse_resume(file_path, db_skills):
    """
    Main entry point function.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif ext == '.docx':
        raw_text = extract_text_from_docx(file_path)
    else:
        raw_text = ""
        
    if not raw_text:
        return None

    # Extract Data
    email, phone = extract_contact_info(raw_text)
    skills = extract_skills(raw_text, db_skills)
    
    return {
        "raw_text": raw_text,
        "email": email,
        "phone": phone,
        "skills": skills,
        "skill_count": len(skills)
    }