from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#kalvin disini :3

app = Flask(__name__)
CORS(app)

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

DATA_PATH = 'journals.json'
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

journals = data.get('journals', [])

articles = []
for journal in journals:
    journal_name = journal.get('basic_info', {}).get('name', '')
    institution = journal.get('basic_info', {}).get('institution', '')
    subject_area = journal.get('basic_info', {}).get('subject_area', '')
    url = journal.get('external_links', {}).get('website', '')
    
    for article in journal.get('articles', []):
        title = article.get('title', '')
        if title:
            full_text = f"{title} {subject_area}"
            articles.append({
                'title': title,
                'journal_name': journal_name,
                'institution': institution,
                'url': url,
                'full_text': preprocess(full_text)
            })

corpus = [article['full_text'] for article in articles]
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(corpus)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'results': [], 'search_time': 0.0})

    start_time = time.time()
    
    processed_query = preprocess(query)
    query_vec = vectorizer.transform([processed_query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    ranked_indices = similarities.argsort()[::-1]
    results = []
    for idx in ranked_indices:
        if similarities[idx] > 0:
            article = articles[idx]
            results.append({
                'title': article['title'],
                'journal_name': article['journal_name'],
                'institution': article['institution'],
                'url': article['url'],
                'score': round(float(similarities[idx]), 4)
            })

    search_time = round(time.time() - start_time, 4)
    return jsonify({'results': results, 'search_time': search_time})

if __name__ == '__main__':
    app.run(debug=True)
