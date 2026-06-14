import json
import pandas as pd
from datetime import datetime

def get_latest_event():
    try:
        with open("kafka_events.jsonl", "r") as file:
            lines = file.readlines()
            if not lines:
                return None
            return json.loads(lines[-1])
    except:
        return None

def weather_agent(event):
    temp = event.get("temperature", 0)
    humidity = event.get("humidity", 0)

    if temp >= 40 or humidity <= 35:
        return {
            "agent": "Weather Agent",
            "status": "High Risk",
            "message": "Weather stress detected due to high temperature or low humidity."
        }
    elif temp >= 35:
        return {
            "agent": "Weather Agent",
            "status": "Medium Risk",
            "message": "Moderate weather stress detected."
        }
    else:
        return {
            "agent": "Weather Agent",
            "status": "Low Risk",
            "message": "Weather conditions are normal."
        }

def pesticide_agent(event):
    pesticide = event.get("pesticide_usage", 0)

    if pesticide >= 200:
        return {
            "agent": "Pesticide Agent",
            "status": "High Risk",
            "message": "High pesticide usage detected. Monitor crop safety."
        }
    elif pesticide >= 120:
        return {
            "agent": "Pesticide Agent",
            "status": "Medium Risk",
            "message": "Moderate pesticide usage detected."
        }
    else:
        return {
            "agent": "Pesticide Agent",
            "status": "Low Risk",
            "message": "Pesticide usage is within normal range."
        }

def crop_agent(event):
    crop = event.get("crop", "Unknown")

    sensitive_crops = ["Wheat", "Cotton", "Rice"]

    if crop in sensitive_crops:
        return {
            "agent": "Crop Agent",
            "status": "Medium Risk",
            "message": f"{crop} is important and should be monitored carefully."
        }
    else:
        return {
            "agent": "Crop Agent",
            "status": "Low Risk",
            "message": f"{crop} is currently stable."
        }

def risk_agent(agent_outputs):
    score = 0

    for output in agent_outputs:
        if output["status"] == "High Risk":
            score += 2
        elif output["status"] == "Medium Risk":
            score += 1

    if score >= 4:
        final_risk = "High Risk"
    elif score >= 2:
        final_risk = "Medium Risk"
    else:
        final_risk = "Low Risk"

    return {
        "agent": "Risk Agent",
        "status": final_risk,
        "message": f"Final combined risk score is {score}."
    }

def recommendation_agent(final_risk):
    if final_risk == "High Risk":
        recommendation = (
            "Immediate action required: increase monitoring, check irrigation, "
            "inspect pest conditions, and alert farm management."
        )
    elif final_risk == "Medium Risk":
        recommendation = (
            "Moderate attention required: monitor crop health, pesticide usage, "
            "and weather conditions regularly."
        )
    else:
        recommendation = (
            "Farm condition appears stable. Continue normal monitoring."
        )

    return {
        "agent": "Recommendation Agent",
        "status": final_risk,
        "message": recommendation
    }

def run_multi_agent_system():
    event = get_latest_event()

    if event is None:
        return {
            "error": "No Kafka events found. Run kafka_producer_sim.py first."
        }

    weather_result = weather_agent(event)
    pesticide_result = pesticide_agent(event)
    crop_result = crop_agent(event)

    agent_outputs = [weather_result, pesticide_result, crop_result]

    risk_result = risk_agent(agent_outputs)
    recommendation_result = recommendation_agent(risk_result["status"])

    final_report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latest_event": event,
        "agents": agent_outputs,
        "final_risk": risk_result,
        "recommendation": recommendation_result
    }

    with open("mas_report.json", "w") as file:
        json.dump(final_report, file, indent=4)

    return final_report

if __name__ == "__main__":
    report = run_multi_agent_system()
    print(json.dumps(report, indent=4))