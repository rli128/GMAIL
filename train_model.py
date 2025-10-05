<<<<<<< HEAD
import spacy
import json
import random
from spacy.training import Example

with open("train_data.json", "r", encoding="utf-8") as f:
    train_data = json.load(f)

TRAIN_DATA = [
    (item["text"], {"entities": [tuple(ent) for ent in item["entities"]]})
    for item in train_data
]

# Load pretrained medium English model
nlp = spacy.load("en_core_web_md")

# Get NER pipe
ner = nlp.get_pipe("ner")

# Add your new label
ner.add_label("ROLE")

# Disable other pipes for training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.resume_training()
    
    for i in range(10):  # number of iterations
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, losses=losses)
        print(f"Iteration {i}, Losses: {losses}")
    
=======
import spacy
import json
import random
from spacy.training import Example

with open("train_data.json", "r", encoding="utf-8") as f:
    train_data = json.load(f)

TRAIN_DATA = [
    (item["text"], {"entities": [tuple(ent) for ent in item["entities"]]})
    for item in train_data
]

# Load pretrained medium English model
nlp = spacy.load("en_core_web_md")

# Get NER pipe
ner = nlp.get_pipe("ner")

# Add your new label
ner.add_label("ROLE")

# Disable other pipes for training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.resume_training()
    
    for i in range(10):  # number of iterations
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, losses=losses)
        print(f"Iteration {i}, Losses: {losses}")

>>>>>>> c4c946ccc4f56955ef00e8fa2d45381220a83708
nlp.to_disk('models/role_model')