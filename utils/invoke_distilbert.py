from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.preprocessing import LabelEncoder
import json
import random
import numpy as np

with open('resource/label_map.json') as f:
    label_map = json.load(f)


with open('resource/responses.json') as f:
    responses = json.load(f)

tokenizer = AutoTokenizer.from_pretrained("PetaniHandal/distilbert-finetuned-islamq-v2")
model = AutoModelForSequenceClassification.from_pretrained(
    "PetaniHandal/distilbert-finetuned-islamq-v2",
    num_labels=2031
)

def tokenizing_distilbert(text):
    return tokenizer(text, padding="max_length", truncation=True, max_length=35)

def predicting_distilbert(inputs):
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        _, preds = torch.max(logits, dim=1)  # <- sesuai dengan latihan

    return preds.cpu().numpy()

def invoke_distilbert(text):
    text_processed = text
    inputs = tokenizing_distilbert(text_processed)
    inputs = {k: torch.tensor(v).unsqueeze(0) for k, v in inputs.items()}
    result = predicting_distilbert(inputs)
    response_tag = label_map[result[0]]
    print(response_tag)
    return random.choice(responses[response_tag]), response_tag

