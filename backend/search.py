from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import load_journal_titles

documents, journal_data = load_journal_titles()
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

def search(query, top_n=10):
    query_vec = vectorizer.transform([query])
    cosine_sim = cosine_similarity(query_vec, tfidf_matrix).flatten()
    ranked_indices = cosine_sim.argsort()[::-1][:top_n]
    
    results = []
    for idx in ranked_indices:
        results.append({
            "title": journal_data[idx]["title"],
            "journal": journal_data[idx]["journal_name"],
            "url": journal_data[idx]["url"],
            "score": float(cosine_sim[idx])
        })
    return results
