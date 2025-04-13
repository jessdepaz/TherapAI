from flask import Flask, request, render_template
from transformers import pipeline
from collections import defaultdict
import re
import os
from openai import OpenAI

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

    breakthroughs = []
    for pattern in breakthrough_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Increase context window from 50 to 150 characters
            start = max(0, match.start() - 150)
            end = min(len(text), match.end() + 150)
            breakthroughs.append(text[start:end].strip())

    return {
        "concerns": [label for label, score in zip(concerns["labels"], concerns["scores"]) if score > 0.3],
        "breakthroughs": breakthroughs[:3]  # Limit to top 3 breakthroughs
    }

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
        concerns=insights["concern