import sqlite3
import pandas as pd
from sentence_transformers import SentenceTransformer
import os

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Construct the absolute path to the CSV file
csv_path = os.path.join(script_dir, '..', 'Echo - Guided Prayer Lists.xlsx - GP Cards.csv')

# Read the CSV file
df = pd.read_csv(csv_path)

# Construct the absolute path to the database file
db_path = os.path.join(script_dir, '..', 'db', 'guided_prayers.db')

# Create a connection to the SQLite database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create the table
c.execute('''
    CREATE TABLE IF NOT EXISTS guided_prayers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feed_title TEXT,
        prayer_title TEXT,
        prayer_description TEXT,
        prayer_steps TEXT,
        description_embedding BLOB
    )
''')

# Iterate over the rows of the dataframe and insert them into the database
for index, row in df.iterrows():
    feed_title = row['Feed Title']
    prayer_title = row['Guided Prayer Title']
    prayer_description = row['Guided Prayer Description']
    prayer_steps = row['Guided Prayer Description Formatted']

    # Generate the embedding for the description
    description_embedding = model.encode(prayer_description)

    # Insert the data into the table
    c.execute(
        "INSERT INTO guided_prayers (feed_title, prayer_title, prayer_description, prayer_steps, description_embedding) VALUES (?, ?, ?, ?, ?)",
        (feed_title, prayer_title, prayer_description, prayer_steps, description_embedding.tobytes())
    )

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created and populated successfully.")