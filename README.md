# Align | Intelligent Resume Analyzer 🚀

![Align Logo](static/logo.png)

**Align** is a modern, full-stack **Applicant Tracking System (ATS)** tool designed to bridge the gap between job seekers and recruitment algorithms.

Built with **Python (Flask)** and **MySQL**, it uses Natural Language Processing (NLP) to parse resumes, match them against job descriptions, and provide real-time scoring and keyword suggestions to help candidates get hired.

---

## 📸 Screenshots

| Landing Page | Dashboard | Analysis Tool |
|:---:|:---:|:---:|
| ![Landing](static/screenshots/landing.png) | ![Dashboard](static/screenshots/dashboard.png) | ![Analysis](static/screenshots/analyze.png) |
*(Note: Create a folder named `screenshots` inside `static` and add your images there to see them here)*

---

## ✨ Key Features

* **🔐 User Authentication:** Secure Login and Registration system with session management.
* **📄 Resume Parsing:** Automatically extracts text and metadata from **PDF** and **DOCX** files.
* **🎯 Smart Matching:** Compares resume keywords against Job Descriptions (JD) to calculate a compatibility score (0-100%).
* **💡 AI Suggestions:** Identifies missing keywords and skills required for the job.
* **📊 Analytics Dashboard:** Tracks application history, average scores, and top skills in a clean, monochrome interface.
* **🎨 Modern UI:** Features a high-contrast "Split-Screen" landing page and a professional "Black & White" functional dashboard.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2 Templating.
* **Backend:** Python 3.x, Flask (Micro-framework).
* **Database:** MySQL (Relational Data Storage).
* **NLP Logic:** Custom Keyword Matching Algorithm, Set Theory Intersection.
* **Libraries:** `PyPDF2`, `python-docx`, `mysql-connector-python`.

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/Align_Resume_Analyzer.git](https://github.com/yourusername/Align_Resume_Analyzer.git)
cd Align_Resume_Analyzer
```
### 2. Set Up Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Database Configuration
Open MySQL Workbench or your terminal.

Open the file database_schema.sql provided in this repository.

Run the script to create the ResumeDB database, tables, and populate the Skill_Master dictionary.
