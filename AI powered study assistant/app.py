from flask import Flask,render_template,request
import PyPDF2
from transformers import pipeline
from gtts import gTTS
import sqlite3

app = Flask(__name__)

summarizer = pipeline("summarization")

def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def get_summary(text):
    summary = summarizer(text[:1000],max_length=120,min_length=30,do_sample=False)
    return summary[0]['summary_text']

def extract_keywords(text):
    words = text.split()
    keywords = list(set(words[:20]))
    return keywords

def generate_question(text):
    return "What is the main concept of the uploaded notes?"

def concept_gap(answer):
    if len(answer) < 5:
        return "Weak understanding detected"
    else:
        return "Good understanding"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload",methods=["POST"])
def upload():
    file = request.files["file"]
    text = extract_text(file)
    summary = get_summary(text)
    keywords = extract_keywords(text)
    question = generate_question(text)

    tts = gTTS(summary)
    tts.save("static/voice.mp3")

    return render_template("index.html",
                           summary=summary,
                           keywords=keywords,
                           questions=question,
                           voice="/static/voice.mp3")

@app.route("/check_answer",methods=["POST"])
def check_answer():
    answer = request.form["answer"]
    result = concept_gap(answer)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO student_answers(question,answer,result) VALUES(?,?,?)",
                   ("Generated Question",answer,result))
    conn.commit()
    conn.close()

    return render_template("index.html",result=result)

if __name__ == "__main__":
    app.run(debug=True)
