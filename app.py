from flask import Flask, request, render_template
from transformers import pipeline

app = Flask(__name__)

# Load model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/summarize_text", methods=["POST"])
def summarize_text():
    transcript = request.form["text"]

    summary = summarizer(
    transcript, 
    max_length=250,      # You can tweak this value for a shorter or longer summary
    min_length=50,       # This ensures the summary is not too short
    do_sample=False,     # Ensures deterministic output (no randomness)
    length_penalty=2.0   # Higher value encourages a more concise summary
)
    return render_template("index.html", summary=summary[0]['summary_text'])

if __name__ == "__main__":
    app.run(debug=True)
