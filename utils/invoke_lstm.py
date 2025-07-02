import random
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import json
import numpy as np
import string

# Load tokenizer dari file JSON
with open('resource/tokenizer.json') as f:
    data = json.load(f)
    tokenizer = tokenizer_from_json(data)

model = load_model('resource/my_model.h5')

with open('resource/label_encoder.json') as f:
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(json.load(f))

# replacing words using dictionary
with open("resource/dict.txt", "r") as f:
    replacement_dict = eval(f.read())

with open("resource/other_words.txt", "r") as f:
    special_words = [word.strip() for word in f.readlines()]



# Load responses from a JSON file (adjust path as needed)
with open('resource/responses.json') as f:
    responses = json.load(f)

def invoke_lstm(chat_input):
    input_shape = 97  # Adjust this based on your model's expected input shape
    texts_p = []
    prediction_input = chat_input

    prediction_input = prediction_input.lower()  # convert to lowercase
    prediction_input = ''.join(c for c in prediction_input if c not in string.punctuation)  # remove punctuation
    prediction_input = ' '.join(prediction_input.split())

    if prediction_input in special_words:
        pass
    else:
        prediction_words = prediction_input.split()
        prediction_words = [replacement_dict[word] if word in replacement_dict else word for word in prediction_words]
        prediction_input = ' '.join(prediction_words)

    texts_p.append(prediction_input)
    # Tokenizing and padding
    prediction_input = tokenizer.texts_to_sequences(texts_p)
    prediction_input = np.array(prediction_input).reshape(-1)
    prediction_input = pad_sequences([prediction_input],input_shape)

    # Getting output from model
    output = model.predict(prediction_input)

    # 1. Ambil INDEKS dari probabilitas tertinggi.
    # np.argmax() akan memberikan posisi nilai terbesar dalam array.
    output_idx = np.argmax(output)

    # 2. Berikan INDEKS tersebut ke inverse_transform.
    # Inputnya harus di dalam list, misal: [2]
    response_tag = label_encoder.inverse_transform([output_idx])[0]

    return random.choice(responses[response_tag]), response_tag


