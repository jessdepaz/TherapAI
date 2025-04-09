from flask import Flask, request, render_template, redirect, url_for
from transformers import pipeline
import sqlite3
import datetime
import os

app = Flask(__name__)

# Create a database directory if it doesn't exist
if not os.path.exists('database'):
    os.makedirs('database')

# Load a summarization model that's better with conversations
summarizer = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")

# Initialize the database
def init_db():
    conn = sqlite3.connect('database/therapy_sessions.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        transcript TEXT NOT NULL,
        summary TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/summarize_text", methods=["POST"])
def summarize_text():
    transcript = request.form["text"]

    # Generate summary
    summary = summarizer(
        transcript,
        max_length=150,  # Keeps it concise but still meaningful
        min_length=30,   # Avoids too-short outputs
        do_sample=False  # Keeps it deterministic
    )

    summary_text = summary[0]['summary_text']
    final_output = f"<strong>Summary of your therapy session:</strong>  {summary_text}"
    
    # Save to database
    conn = sqlite3.connect('database/therapy_sessions.db')
    cursor = conn.cursor()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO sessions (date, transcript, summary) VALUES (?, ?, ?)",
        (current_date, transcript, summary_text)
    )
    conn.commit()
    conn.close()

    return render_template("index.html", summary=final_output)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    # Get all sessions from database
    conn = sqlite3.connect('database/therapy_sessions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, summary FROM sessions ORDER BY date DESC LIMIT 1024")
    sessions = cursor.fetchall()
    conn.close()
    
    return render_template("dashboard.html", sessions=sessions)

@app.route("/view_session/<int:session_id>", methods=["GET"])
def view_session(session_id):
    # Get specific session from database
    conn = sqlite3.connect('database/therapy_sessions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, transcript, summary FROM sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    conn.close()
    
    if not session:
        return redirect(url_for('dashboard'))
    
    return render_template("view_session.html", session=session)

@app.route("/re_summarize/<int:session_id>", methods=["POST"])
def re_summarize(session_id):
    # Get transcript from database
    conn = sqlite3.connect('database/therapy_sessions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT transcript FROM sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        return redirect(url_for('dashboard'))
    
    transcript = session[0]
    
    # Generate new summary
    summary = summarizer(
        transcript,
        max_length=150,
        min_length=30,
        do_sample=False
    )
    
    summary_text = summary[0]['summary_text']
    
    # Update the database with new summary
    cursor.execute(
        "UPDATE sessions SET summary = ? WHERE id = ?",
        (summary_text, session_id)
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_session', session_id=session_id))

if __name__ == "__main__":
    app.run(debug=True)