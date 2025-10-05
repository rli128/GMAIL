import pickle
import re
from bs4 import BeautifulSoup
import spacy
import json
import datetime
from datetime import timezone
import itertools

with open("messages_cache.pkl", "rb") as f:
    loaded_messages = pickle.load(f)

def strip_html(html):
    soup = BeautifulSoup(html, "html.parser")
    
    for element in soup(['script', 'style', 'meta', 'link', 'title', 'head']):
        element.decompose()
    
    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r'\s+', ' ', text).strip()    
    return text

nlp = spacy.load('role_model')

for msg in loaded_messages[:15]:
    
    subject_preview = strip_html(msg['subject'])
    body_preview = strip_html(msg['body'][:300])
    text = (subject_preview + " | " + body_preview)
    text = re.sub(r"\s+", " ", text).strip()
    print(text)
    print("@" * 40)