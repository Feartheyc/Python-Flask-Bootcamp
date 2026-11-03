from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def home():
    # Fetch live GitHub data for your profile
    user_url = "https://api.github.com/users/Feartheyc"
    repos_url = "https://api.github.com/users/Feartheyc/repos?sort=updated&per_page=6"
    
    user_data = requests.get(user_url).json()
    repos_data = requests.get(repos_url).json()
    
    # Pass the data to the HTML template
    return render_template("dashboard.html", user=user_data, repos=repos_data)

@app.route("/about")
def about():
    return "My name is Feartheyc"

@app.route("/contact")
def contact():
    return "github.com/Feartheyc"

if __name__ == "__main__":
    app.run(debug=True)