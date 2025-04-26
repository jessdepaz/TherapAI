from flask import Flask, request, render_template, redirect, url_for
from transformers import pipeline
from collections import defaultdict
import re
import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Load summarizer
summarizer = pipeline(
    "summarization",
    model="philschmid/bart-large-cnn-samsum"
)

# Load classifier explicitly (instead of relying on default)
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",  # Same default, just now explicit
    revision="d7645e1"  # Optional: version locking for reproducibility
)

def extract_insights(text):
    # Analyze core concerns
    concerns = classifier(
        text,
        candidate_labels=["anxiety", "depression", "relationships", "work stress", "family issues", "self-esteem"],
        multi_label=True
    )

    # Find breakthroughs using key phrases
    breakthrough_patterns = [
        r"(?i)(?:I\s+)?(?:realized|understood|discovered|learned)",
        r"(?i)now\s+I\s+(?:see|understand|know)",
        r"(?i)it\s+(?:becomes|became)\s+clear"
    ]

    def find_sentence_boundaries(text, start_pos, end_pos):
        # Find the start of the sentence
        sentence_start = start_pos
        while sentence_start > 0 and text[sentence_start-1] not in '.!?':
            sentence_start -= 1
        if sentence_start > 0:
            sentence_start += 1  # Skip the period and space

        # Find the end of the sentence
        sentence_end = end_pos
        while sentence_end < len(text) and text[sentence_end] not in '.!?':
            sentence_end += 1
        if sentence_end < len(text):
            sentence_end += 1  # Include the period

        return sentence_start, sentence_end

    breakthroughs = []
    for pattern in breakthrough_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get complete sentences around the breakthrough
            start, end = find_sentence_boundaries(
                text,
                max(0, match.start() - 150),
                min(len(text), match.end() + 150)
            )
            breakthrough_text = text[start:end].strip()
            if breakthrough_text and len(breakthrough_text) > 10:  # Ensure we have meaningful content
                breakthroughs.append(breakthrough_text)

    return {
        "concerns": [label for label, score in zip(concerns["labels"], concerns["scores"]) if score > 0.3],
        "breakthroughs": breakthroughs[:3]  # Limit to top 3 breakthroughs
    }

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

@app.route("/transcribe_audio", methods=["POST"])
def transcribe_audio():
    audio_file = request.files.get("audio")

    if not audio_file:
        return "No audio file uploaded", 400

    # Save uploaded file to a temporary path
    filepath = "temp_audio.wav"
    audio_file.save(filepath)

    # Transcribe using OpenAI Whisper API
    try:
        with open(filepath, "rb") as f:
            # Correct API usage for transcription
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=f
            )
            transcript = transcription.text
            os.remove(filepath)
    except Exception as e:
        os.remove(filepath)
        return f"Transcription failed: {str(e)}", 500

    # Reuse your summarizer and insight logic
    summary = summarizer(
        transcript,
        max_length=150,
        min_length=30,
        do_sample=False
    )
    summary_text = summary[0]['summary_text']

    insights = extract_insights(transcript)

    return render_template(
        "index.html",
        summary=f"<strong>Summary of your therapy session:</strong> {summary_text}",
        concerns=insights["concerns"],
        breakthroughs=insights["breakthroughs"]
    )


@app.route("/summarize_text", methods=["POST"])
def summarize_text():
    transcript = request.form["text"]

    # Generate summary
    summary = summarizer(
        transcript,
        max_length=150,
        min_length=30,
        do_sample=False
    )
    summary_text = summary[0]['summary_text']

    # Extract insights
    insights = extract_insights(transcript)

    return render_template(
        "index.html",
        summary=f"<strong>Summary of your therapy session:</strong> {summary_text}",
        concerns=insights["concerns"],
        breakthroughs=insights["breakthroughs"]
    )

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
# app.py
