import json
import random
import time
from datetime import datetime

crops = ["Wheat", "Rice", "Cotton", "Maize", "Sugarcane"]
districts = ["Lahore", "Multan", "Faisalabad", "Bahawalpur", "Sahiwal"]

while True:
    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "district": random.choice(districts),
        "crop": random.choice(crops),
        "temperature": random.randint(25, 45),
        "humidity": random.randint(30, 80),
        "pesticide_usage": random.randint(50, 250),
        "risk_signal": random.choice(["Low", "Medium", "High"])
    }

    with open("kafka_events.jsonl", "a") as file:
        file.write(json.dumps(event) + "\n")

    print("Produced:", event)
    time.sleep(3)