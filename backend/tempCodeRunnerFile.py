# —————————————
# Cell 1: Import dan Setup
# —————————————
import json, time, re, os
import numpy as np
from nltk.stem import PorterStemmer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ps = PorterStemmer()
factory = StemmerFactory()
indo_stemmer = factory.create_stemmer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def stem_en(text):
    return ' '.join([ps.stem(word) for word in text.split()])

def stem_both(text):
    # terjemahkan dulu pakai Sastrawi, lalu stem hasilnya
    return ' '.join([ps.stem(w) for w in indo_stemmer.stem(text).split()])

# —————————————
# Cell 2: Load Dataset
# —————————————
with open("all_sinta_journals.json", "r", encoding="utf-8") as f:
    data = json.load(f)

journals = data.get('journals', [])
articles = []
for j in journals:
    journal_name = j.get('basic_info', {}).get('name', '')
    institution  = j.get('basic_info', {}).get('institution', '')
    subject_area = j.get('basic_info', {}).get('subject_area', '')
    url = j.get('external_links', {}).get('website', '')

    for art in j.get('articles', []):
        title = art.get('title', '')
        if title:
            full_text = f"{title} {subject_area}"
            articles.append({
                'title': title,
                'journal_name': journal_name,
                'institution': institution,
                'url': url,
                'full_text': full_text
            })

print(f"Total artikel: {len(articles)}")

# —————————————
# Cell 3: Fungsi Pengukuran Waktu
# —————————————
def measure_time_for_query(articles, query, stem_fn, n_reps=3):
    """
    Mengembalikan:
      - fit_times    = list panjang n_reps (detik) untuk fit_transform(corpus)
      - search_times = list panjang n_reps (detik) untuk transform(query) + cosine_similarity
      - num_results  = list panjang n_reps (# dokumen similarity>0)
    """
    fit_times = []
    search_times = []
    num_results = []

    # Siapkan corpus sekali (tanpa stem); akan di‐stem per rep
    raw_corpus = [clean_text(a['full_text']) for a in articles]

    for _ in range(n_reps):
        # 1) Buat corpus_stem: apply clean_text + stem_fn
        corpus_stem = [stem_fn(doc) for doc in raw_corpus]

        # 2) Fit TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        t0 = time.time()
        tfidf_matrix = vectorizer.fit_transform(corpus_stem)
        t_fit = time.time() - t0

        # 3) Preprocess query
        q_clean = clean_text(query)
        q_stem  = stem_fn(q_clean)

        # 4) Hitung cosine similarity
        t1 = time.time()
        q_vec = vectorizer.transform([q_stem])
        sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
        t_search = time.time() - t1

        # 5) Hitung # hasil (similarity>0)
        cnt = np.sum(sims > 0)

        fit_times.append(t_fit)
        search_times.append(t_search)
        num_results.append(int(cnt))

    return fit_times, search_times, num_results

# —————————————
# Cell 4: Daftar Query & Loop Pengukuran
# —————————————
queries = [
    "machine learning",
    "pemodelan prediksi",
    "analisis data",
    "deep learning application",
    "pengolahan citra medis",
    "clustering dokumen",
    "evaluasi sistem rekomendasi",
    "neural network bagi pertanian",
    "sentiment analysis",
    "tata kelola pemerintah data besar"
]

# Struktur untuk menyimpan hasil
all_results = []

for q in queries:
    # EN_ONLY
    f_en, s_en, n_en = measure_time_for_query(articles, q, stem_en, n_reps=3)
    # EN_ID (stem both)
    f_both, s_both, n_both = measure_time_for_query(articles, q, stem_both, n_reps=3)

    # Hitung statistik: rata‐rata dan std
    entry_en = {
        "query": q,
        "scheme": "EN_ONLY",
        "fit_avg":    np.mean(f_en),
        "fit_std":    np.std(f_en),
        "search_avg": np.mean(s_en),
        "search_std": np.std(s_en),
        "docs_avg":   np.mean(n_en),
        "docs_std":   np.std(n_en),
    }
    entry_both = {
        "query": q,
        "scheme": "EN_ID",
        "fit_avg":    np.mean(f_both),
        "fit_std":    np.std(f_both),
        "search_avg": np.mean(s_both),
        "search_std": np.std(s_both),
        "docs_avg":   np.mean(n_both),
        "docs_std":   np.std(n_both),
    }
    all_results.append(entry_en)
    all_results.append(entry_both)

# —————————————
# Cell 5: Buat DataFrame & Tampilkan
# —————————————
import pandas as pd

df = pd.DataFrame(all_results)
# Agar kolom terurut: query, scheme, fit_avg, fit_std, search_avg, search_std, docs_avg, docs_std
df = df[[
    "query","scheme",
    "fit_avg","fit_std",
    "search_avg","search_std",
    "docs_avg","docs_std"
]]

# Tambahkan baris "Overall" untuk masing-masing skema
def compute_overall(df, scheme_name):
    sub = df[df["scheme"] == scheme_name]
    return {
        "query": "Overall",
        "scheme": scheme_name,
        "fit_avg":    sub["fit_avg"].mean(),
        "fit_std":    sub["fit_avg"].std(),
        "search_avg": sub["search_avg"].mean(),
        "search_std": sub["search_avg"].std(),
        "docs_avg":   sub["docs_avg"].mean(),
        "docs_std":   sub["docs_avg"].std(),
    }

overall_en   = compute_overall(df, "EN_ONLY")
overall_both = compute_overall(df, "EN_ID")
df = df.append(overall_en, ignore_index=True).append(overall_both, ignore_index=True)

# Tampilkan tabel
df.style.format({
    "fit_avg":    "{:.3f}",
    "fit_std":    "{:.3f}",
    "search_avg": "{:.3f}",
    "search_std": "{:.3f}",
    "docs_avg":   "{:.1f}",
    "docs_std":   "{:.1f}"
})
