from flask import Flask, request, render_template
from transformers import pipeline

app = Flask(__name__)

# Load a summarization model that's better with conversations
summarizer = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")

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

    return render_template("index.html", summary=final_output)

if __name__ == "__main__":
    app.run(debug=True)
