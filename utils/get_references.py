import requests

URL = "https://PetaniHandal-searchmantic-hadits-api.hf.space/api/search"

# Mapping kitab untuk display
kitab_mapping = {
    'sunan_nasai': 'Kitab Sunan An-Nasa\'i',
    'sunan_Tirmidzi': 'Kitab Sunan At-Tirmidzi',
    'sunan_abu_daud': 'Kitab Sunan Abu Daud',
    'sunan_ibnu_majah': 'Kitab Sunan Ibnu Majah',
    'shahih_bukhari': 'Kitab Shahih Bukhari',
    'shahih_muslim': 'Kitab Shahih Muslim',
}

# Slug untuk URL hadits.id
kitab_slug_map = {
    'sunan_nasai': 'nasai',
    'sunan_Tirmidzi': 'tirmidzi',
    'sunan_abu_daud': 'dawud',
    'sunan_ibnu_majah': 'majah',
    'shahih_bukhari': 'bukhari',
    'shahih_muslim': 'muslim',
}

greetings = [    "greeting I",
    "greeting II",
    "Hallo",
    "hola",
    "wassup",
    "yo",
    "How day",
    "islamic greetings",
    "Peace be upon you",
    "and upon you be peace",
    "Wa Alaikum Asalam",
    "been fine",
    "day is great",
    "day is great yours",
    "and what about you",
    "how are you",
    "not good",
    "goodbye",
    "Islamic goodbye",
    "noanswer",
    "thanks",
    "thank you",
    "children_stories",
    "chatbot",
    "chatbot name",
    "Al-Siraj",
    "your age",
    "Where you live",
    "Where are you from",
    "Are you married",
    "Do you have children",
    "languages can you speak",
    "Other than english",
    "Other than english and urdu",
    "your goals",
    "Your aim",
    "Your mission",
    "you busy",
    "Are you free?",
    "other chatbots",
    "think of me",
    "Say anything",
    "Say something",
    "weather",
    "time",
    "date",
    "day",
    "know me",
    "interacted before",
    "How many people can you talk",
    "like humans",
    "why like humans",
    "you are good",
    "love humans",
    "why love humans",
    "options",]

def map(data):
    for item in data:
        kitab_raw = item.get("kitab")
        hadits_id = item.get("id")

        # Mapping nama kitab
        item["kitab"] = kitab_mapping.get(kitab_raw, kitab_raw)

        # Generate URL hadits.id
        slug = kitab_slug_map.get(kitab_raw)
        if slug and hadits_id:
            item["url"] = f"https://www.hadits.id/hadits/{slug}/{hadits_id}"
        else:
            item["url"] = None
    return data


def get_references(query, secret, response_tag):
    headers = {
        "Authorization": f"Bearer {secret}"
    }

    payload = {
        "query": query,
        "hadits": "shahih_bukhari",
        "all_source": "true"
    }

    response = requests.post(URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json().get("results", [])
        if result:
            result = map(result)
        if response_tag in greetings:
            return []
        else:
            return result
    else:
        response.raise_for_status()
