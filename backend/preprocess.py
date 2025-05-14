import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

stopword_factory = StopWordRemoverFactory()
stemmer_factory = StemmerFactory()

def preprocess(text):
    text = text.lower()
    
    stopword_remover = stopword_factory.create_stop_word_remover()
    text_no_stopwords = stopword_remover.remove(text)
    
    stemmer = stemmer_factory.create_stemmer()
    text_stemmed = stemmer.stem(text_no_stopwords)
    
    text_cleaned = re.sub(r'[^a-z0-9\s]', '', text_stemmed)
    
    return text_cleaned
