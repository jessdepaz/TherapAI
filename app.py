from flask import Flask, request, render_template
from transformers import pipeline
from collections import defaultdict
import re

app = Flask(__name__)

# Load models
summarizer = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")
classifier = pipeline("zero-shot-classification")

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

if __name__ == "__main__":
    app.run(debug=True)
# app.py