from sentence_transformers import SentenceTransformer, util
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

for resource, path in [('punkt', 'tokenizers/punkt'), ('punkt_tab', 'tokenizers/punkt_tab'),
                        ('stopwords', 'corpora/stopwords')]:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(resource)

similarity_model = SentenceTransformer('all-MiniLM-L6-v2')


def generate_summary(text):
    if not text or not text.strip():
        return "No text provided."
    text = ' '.join(text.split())
    sentences = nltk.sent_tokenize(text)
    if len(sentences) <= 3:
        return text[:1000]
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    word_freq = Counter([w for w in words if w.isalnum() and w not in stop_words])
    sentence_scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in word_freq:
                sentence_scores[sent] = sentence_scores.get(sent, 0) + word_freq[word]
    # Extract top sentences to create a 10-line summary
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:10]
    summary_lines = [s.strip() for s in sentences if s in top_sentences]
    summary = '\n'.join(summary_lines)
    return summary if summary.strip() else text[:500]


def extract_keywords(text):
    if not text:
        return []
    text = ' '.join(text.split())
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    word_freq = Counter([w for w in words if w.isalnum() and w not in stop_words])
    return [word for word, freq in word_freq.most_common(10)]


def generate_questions(text):
    if not text:
        return []
    text = ' '.join(text.split())
    sentences = nltk.sent_tokenize(text)
    return [f"What does the following sentence mean: {s}" for s in sentences[:5]]


def detect_concept_gap(student_answer, expected_answer):
    if not student_answer or not expected_answer:
        return {"score": 0, "gap_detected": True}
    embeddings = similarity_model.encode([student_answer, expected_answer])
    score = round(util.cos_sim(embeddings[0], embeddings[1]).item() * 100, 2)
    return {"score": score, "gap_detected": score < 50}


def generate_voice_explanation(concept):
    if not concept:
        return "No concept provided."
    return f"The concept of {concept} is fundamental in understanding the topic. It refers to the key principles and ideas that form the basis of the subject matter."
