from flask import Flask, render_template, request, redirect, url_for
import requests
import urllib3
import pandas as pd
import mysql.connector

# Suppress the insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# --- MYSQL CONFIGURATION ---
# Change these to match your local MySQL Workbench / PC setup
db_host = "localhost"
db_user = "root"
db_password = "password" # <--- PUT YOUR MYSQL PASSWORD HERE
db_name = "flask_dashboard"

def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

def init_db():
    # 1. Connect to MySQL server to create the database if it doesn't exist
    server_conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password
    )
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    server_conn.close()

    # 2. Connect to the new database to create the table
    db_conn = get_db_connection()
    db_cursor = db_conn.cursor()
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(255) NOT NULL,
            assignment VARCHAR(255) NOT NULL
        )
    ''')
    db_conn.commit()
    db_conn.close()

# Initialize the MySQL database and table on startup
try:
    init_db()
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}. Did you start your MySQL server and update the password?")

@app.route("/")
def home():
    user_url = "https://api.github.com/users/Feartheyc"
    repos_url = "https://api.github.com/users/Feartheyc/repos?sort=updated&per_page=10"
    
    # --- 1. GITHUB API DATA ---
    try:
        user_response = requests.get(user_url, verify=False, timeout=5)
        repos_response = requests.get(repos_url, verify=False, timeout=5)
        
        user_data = user_response.json()
        repos_data = repos_response.json()
        
        if isinstance(repos_data, dict):
            repos_data = [] 
            
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        user_data = {
            "login": "Feartheyc", 
            "name": "Yuvraj Chavan", 
            "bio": "API connection blocked locally. Running in offline mode.", 
            "public_repos": "0", 
            "followers": "0", 
            "avatar_url": "https://github.com/identicons/feartheyc.png",
            "html_url": "https://github.com/Feartheyc"
        }
        repos_data = []

    # --- 2. GITHUB PANDAS TABLE ---
    table_html = ""
    if repos_data:
        df = pd.DataFrame(repos_data)
        if not df.empty and 'name' in df.columns:
            df = df[['name', 'language', 'stargazers_count', 'updated_at']]
            df.columns = ['Repository Name', 'Primary Language', 'Stars', 'Last Updated']
            df['Primary Language'] = df['Primary Language'].fillna('N/A')
            df['Last Updated'] = pd.to_datetime(df['Last Updated']).dt.strftime('%Y-%m-%d')
            table_html = df.to_html(index=False, border=0, classes="pandas-table")
    else:
        table_html = "<p class='text-textMain'>No repository data available for table.</p>"

    # --- 3. LOCAL EXCEL PANDAS TABLE ---
    excel_html = ""
    try:
        excel_df = pd.read_excel('data.xlsx')
        excel_df = excel_df.fillna('N/A')
        excel_html = excel_df.to_html(index=False, border=0, classes="pandas-table")
    except FileNotFoundError:
        excel_html = "<p class='text-textMuted'>[ data.xlsx not found in root directory. Create one to see local data here! ]</p>"
    except Exception as e:
        excel_html = f"<p class='text-red-500'>Error loading Excel file: {e}</p>"

    return render_template("dashboard.html", user=user_data, repos=repos_data, table_html=table_html, excel_html=excel_html)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# --- MYSQL EMPLOYEES/ASSIGNMENT ROUTE ---
@app.route("/employees", methods=["GET", "POST"])
def employees():
    try:
        conn = get_db_connection()
        c = conn.cursor()

        if request.method == "POST":
            name = request.form.get("name")
            role = request.form.get("role")
            assignment = request.form.get("assignment")
            
            # MySQL uses %s for parameter insertion to prevent SQL injection
            c.execute(
                "INSERT INTO employees (name, role, assignment) VALUES (%s, %s, %s)", 
                (name, role, assignment)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for("employees"))

        c.execute("SELECT * FROM employees")
        employee_data = c.fetchall()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        employee_data = []

    return render_template("employees.html", employees=employee_data)

if __name__ == "__main__":
    app.run(debug=True)