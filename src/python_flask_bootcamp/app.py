from flask import Flask, render_template, request, redirect, url_for
import requests
import urllib3
import pandas as pd
import mysql.connector

# Suppress the insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# --- MYSQL CONFIGURATION ---
db_host = "localhost"
db_port = 8808 
db_user = "root"
db_password = "Yuvi91207"  # <--- REPLACE WITH YOUR ACTUAL PASSWORD
db_name = "flask_dashboard"

def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )

def init_db():
    server_conn = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )
    server_cursor = server_conn.cursor()
    server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    server_conn.close()

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

try:
    init_db()
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")

@app.route("/")
def home():
    user_url = "https://api.github.com/users/Feartheyc"
    repos_url = "https://api.github.com/users/Feartheyc/repos?sort=updated&per_page=10"
    
    try:
        user_response = requests.get(user_url, verify=False, timeout=5)
        repos_response = requests.get(repos_url, verify=False, timeout=5)
        user_data = user_response.json()
        repos_data = repos_response.json()
        if isinstance(repos_data, dict):
            repos_data = [] 
    except requests.exceptions.RequestException as e:
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

    excel_html = ""
    try:
        excel_df = pd.read_excel('data.xlsx')
        excel_df = excel_df.fillna('N/A')
        excel_html = excel_df.to_html(index=False, border=0, classes="pandas-table")
    except FileNotFoundError:
        excel_html = "<p class='text-textMuted'>[ data.xlsx not found ]</p>"
    except Exception as e:
        excel_html = f"<p class='text-red-500'>Error loading Excel file: {e}</p>"

    employee_data = []
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM employees ORDER BY id DESC LIMIT 5")
        employee_data = c.fetchall()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Database error on dashboard: {err}")

    return render_template("dashboard.html", user=user_data, repos=repos_data, table_html=table_html, excel_html=excel_html, employees=employee_data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/employees", methods=["GET", "POST"])
def employees():
    try:
        conn = get_db_connection()
        c = conn.cursor()

        if request.method == "POST":
            emp_id = request.form.get("emp_id")
            name = request.form.get("name")
            role = request.form.get("role")
            assignment = request.form.get("assignment")
            
            if emp_id: 
                c.execute("UPDATE employees SET name=%s, role=%s, assignment=%s WHERE id=%s", (name, role, assignment, emp_id))
            else:
                c.execute("INSERT INTO employees (name, role, assignment) VALUES (%s, %s, %s)", (name, role, assignment))
                
            conn.commit()
            conn.close()
            return redirect(url_for("employees"))

        search_query = request.args.get("q")
        if search_query:
            wildcard_query = f"%{search_query}%"
            c.execute("SELECT * FROM employees WHERE name LIKE %s OR role LIKE %s OR assignment LIKE %s", 
                      (wildcard_query, wildcard_query, wildcard_query))
        else:
            c.execute("SELECT * FROM employees")
            
        employee_data = c.fetchall()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        employee_data = []
        search_query = ""

    return render_template("employees.html", employees=employee_data, search_query=search_query or "")

@app.route("/delete_employee/<int:emp_id>")
def delete_employee(emp_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM employees WHERE id = %s", (emp_id,))
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    return redirect(url_for("employees"))

# --- API ROUTES ---

@app.route("/images")
def images():
    return render_template("images.html")

@app.route("/jokes")
def jokes():
    jokes_data = []
    try:
        # Fetching 10 two-part jokes from JokeAPI
        response = requests.get("https://v2.jokeapi.dev/joke/Programming,Pun,Miscellaneous?amount=10&type=twopart", verify=False, timeout=5)
        if response.status_code == 200:
            jokes_data = response.json().get("jokes", [])
    except requests.exceptions.RequestException as e:
        print(f"Joke API Error: {e}")
        
    return render_template("jokes.html", jokes=jokes_data)

if __name__ == "__main__":
    app.run(debug=True)