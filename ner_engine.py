import json
import re

CROPS = [
    "wheat", "rice", "cotton", "maize", "sugarcane",
    "barley", "millet", "gram", "mustard"
]

LOCATIONS = [
    "lahore", "multan", "faisalabad", "bahawalpur", "sahiwal",
    "gujranwala", "rawalpindi", "sargodha", "dera ghazi khan",
    "dg khan", "rahim yar khan", "sheikhupura"
]

ISSUES = {
    "pest": "Pest Attack",
    "insect": "Pest Attack",
    "attack": "Pest Attack",
    "disease": "Crop Disease",
    "fungus": "Fungal Disease",
    "yellow": "Leaf Yellowing",
    "dry": "Drought Stress",
    "water shortage": "Water Shortage",
    "low production": "Low Production",
    "low yield": "Low Yield",
    "spray": "Pesticide/Spray Issue",
    "fertilizer": "Fertilizer Issue",
    "irrigation": "Irrigation Issue",
    "price": "Market Price Query"
}

BLOCKED_ISSUES = ["price", "rate", "market", "mandi", "buy", "sell"]

def contains_phrase(text, phrase):
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None

def extract_entities(text):
    text_lower = text.lower()

    crop = None
    location = None
    issue = None
    is_blocked = False

    for c in CROPS:
        if contains_phrase(text_lower, c):
            crop = c.title()
            break

    for loc in LOCATIONS:
        if contains_phrase(text_lower, loc):
            location = loc.title()
            break

    for blocked in BLOCKED_ISSUES:
        if contains_phrase(text_lower, blocked):
            is_blocked = True
            issue = "Blocked Market/Price Query"
            break

    if not issue:
        for keyword, label in ISSUES.items():
            if contains_phrase(text_lower, keyword):
                issue = label
                break

    result = {
        "crop": crop,
        "location": location,
        "issue": issue,
        "blocked": is_blocked
    }

    return result

if __name__ == "__main__":
    user_text = input("Enter farmer query: ")
    entities = extract_entities(user_text)

    print("\nExtracted Entities:")
    print(json.dumps(entities, indent=4))