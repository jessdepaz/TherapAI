TherapAI
TherapAI is a mental health tool that analyzes audio or text from therapy sessions to extract key insights and breakthroughs using OpenAI’s language models.

Setup Instructions
Follow the steps below to get TherapAI running locally.

1. Clone the Repository

git clone https://github.com/jessdepaz/TherapAI

cd therapAI

3. Create and Activate Virtual Environment
macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

Windows (CMD):

python -m venv .venv
.venv\Scripts\activate

3. Install Requirements

pip install -r requirements.txt

5. Add Your OpenAI API Key
You will need an OpenAI API key with access to gpt-4o-transcribe. This will be provided securely. Once you have it:
Set it as an environment variable:

macOS/Linux:

export OPENAI_API_KEY="your-api-key-here"

Windows (CMD):

set OPENAI_API_KEY="your-api-key-here"

Note: You must run this command every time you start a new terminal session, unless you add it to your shell profile (e.g., .bashrc, .zshrc, or PowerShell profile).

5. Run the Application

python app.py

The app will start on http://127.0.0.1:5000 and should be fully functional.

Features: 
 - Transcribe audio sessions with gpt-4o-transcribe
 - Summarize therapy conversations using state-of-the-art NLP
 - Highlight emotional breakthroughs and core mental health topics

📂 Project Structure

therapAI/
│
├── app.py                # Flask app entry point
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── requirements.txt      # Python dependencies
└── README.md             # This file

🔐 Security Notes
API keys are not committed to the repository. Always use environment variables.

We will not share our API key publicly.

