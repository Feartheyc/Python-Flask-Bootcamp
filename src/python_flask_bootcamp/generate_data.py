import pandas as pd

# Your custom project data
data = {
    "Project Name": [
        "FinQuest RPG", 
        "DIY 3D Printer", 
        "R36S Handheld Customization", 
        "The Swordmaster of the Plague", 
        "Maharashtra Infinite Auto-Publisher"
    ],
    "Category": [
        "Game Development", 
        "Hardware Engineering", 
        "Firmware Modding", 
        "Game Development", 
        "Web Development"
    ],
    "Tech Stack / Hardware": [
        "Python, Streamlit", 
        "Arduino Mega, RAMPS 1.4", 
        "ArkOS, dArkOS", 
        "Unity, Pixel Art", 
        "WordPress, Openverse API"
    ],
    "Status": [
        "In Development", 
        "Completed", 
        "Completed", 
        "Prototype", 
        "Active"
    ]
}

# Convert to Pandas DataFrame and export to Excel
df = pd.DataFrame(data)
df.to_excel("data.xlsx", index=False)

print("data.xlsx successfully created! Refresh your Flask dashboard to see the table.")
