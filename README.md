# :brain: TherapAI

TherapAI is a web-based mental health tool that helps therapists and clients gain deeper insights from therapy sessions. It supports both **audio transcription** and **text analysis** using OpenAI’s GPT-4o, extracting emotional breakthroughs and highlighting recurring topics.

---

## :rocket: Features

- :studio_microphone: **Transcribe Audio**  
  Upload therapy session audio and get accurate transcripts using OpenAI’s `gpt-4o-transcribe`.

- :memo::pencil: **Summarize Conversations**  
  NLP summarization condenses long sessions into digestible overviews.

- :bulb: **Highlight Emotional Breakthroughs**  
  Detect statements indicating realizations, emotional clarity, or new understanding using regular expressions.

---

## :computer: Technologies Used

- **Python 3.10+**
- **Flask** - Lightweight web framework
- **Transformers (Hugging Face)** - Summarization and classification models
- **OpenAI API** - Audio transcription with `gpt-4o-transcribe`
- **HTML/CSS** - Templating and styling
- **Regex** - Pattern matching for emotional insights

---

## 🛠 Setup Instructions

Follow these steps to run TherapAI locally:

### 1. Clone the Repository

```
git clone https://github.com/jessdepaz/TherapAI
cd TherapAI
```

### 2. Create and Activate Virtual Environment
To isolate dependencies, create and activate a virtual environment:

macOS/Linux:

```
python3 -m venv .venv
source .venv/bin/activate
```

Windows (CMD):

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Required Dependencies
Use pip to install the required packages:
```pip install -r requirements.txt```

This installs Flask, Hugging Face transformers, and other necessary libraries.

### 4. Set Up Your OpenAI API Key
TherapAI requires an OpenAI API key to transcribe audio. Once you receive your key:

macOS/Linux:

```export OPENAI_API_KEY="your-api-key-here"```

Windows (CMD):

```set OPENAI_API_KEY="your-api-key-here"```

💡 To avoid resetting every session, add the export/set command to your shell profile file (e.g., .bashrc, .zshrc, or PowerShell profile).

### 5. Run the Application
Once everything is set up, start the Flask app:

``` python app.py```

Open your browser and go to: [http://127.0.0.1:5000]
You should now be able to upload audio or paste text for analysis.

# :open_file_folder: Project Structure

```
therapAI/ 
├── app.py                  # Main Flask application 
├── templates/ 
│   └── index.html          # Main user interface 
├── static/ 
│   └── style.css           # Frontend styling 
├── requirements.txt        # Python dependencies 
└── README.md               # Project documentation 
```

# :closed_lock_with_key: Security Notes
Do not commit API keys — use environment variables. Never hardcode secrets in code.
Consider using a .env file and tools like python-dotenv for local development.

# :bar_chart: Example Use Case
A user uploads a therapy session audio file.

GPT-4o transcribes the session.

The app summarizes the session and highlights statements like:

"I realized I’ve been holding back."

"It became clear what I needed to do."

These insights are surfaced for therapist review or journaling.

## :pushpin: Future Improvements
:closed_lock_with_key: User authentication

:floppy_disk: Session history storage

:globe_with_meridians: Multilingual transcription and summarization

:brain: Dashboard for emotional and thematic analytics

:writing_hand: Editable transcripts before final analysis


# :busts_in_silhouette: Contributors
Jessica De-Paz - Project Manager & Lead Developer
 - Set up the development environment and implemented the audio-to-analysis functionality.

Anelys Izquierdo - Insight Architect & Feature Developer
 - Led the development of emotional breakthrough detection and the key insights sidebar.

Rickny Sanon - UX/UI Specialist & NLP Integrator
 - Enhanced interface aesthetics and refined the text-to-analysis functionality.


