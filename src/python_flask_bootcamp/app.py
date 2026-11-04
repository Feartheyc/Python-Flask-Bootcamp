from flask import Flask, render_template
import requests
import urllib3
import pandas as pd # Added Pandas

# Suppress the insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route("/")
def home():
    user_url = "https://api.github.com/users/Feartheyc"
    repos_url = "https://api.github.com/users/Feartheyc/repos?sort=updated&per_page=10" # Bumped to 10 for a better table
    
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

    # --- PANDAS INTEGRATION ---
    table_html = ""
    if repos_data:
        # 1. Load the raw JSON list into a Pandas DataFrame
        df = pd.DataFrame(repos_data)
        
        # 2. Filter only the columns we want to show
        if not df.empty and 'name' in df.columns:
            df = df[['name', 'language', 'stargazers_count', 'updated_at']]
            df.columns = ['Repository Name', 'Primary Language', 'Stars', 'Last Updated']
            
            # 3. Clean up the data
            df['Primary Language'] = df['Primary Language'].fillna('N/A')
            # Convert ISO 8601 date strings into readable YYYY-MM-DD format
            df['Last Updated'] = pd.to_datetime(df['Last Updated']).dt.strftime('%Y-%m-%d')
            
            # 4. Export the DataFrame directly to HTML
            table_html = df.to_html(index=False, border=0, classes="pandas-table")
    else:
        table_html = "<p class='text-textMain'>No repository data available for table.</p>"

    return render_template("dashboard.html", user=user_data, repos=repos_data, table_html=table_html)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)