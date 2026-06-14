import pandas as pd
import joblib

from ner_engine import extract_entities
from rag_engine import simple_rag_answer
from multi_agent_system import run_multi_agent_system

df = pd.read_csv("final_agriculture_crisis_dataset.csv")
model = joblib.load("agri_crisis_model.pkl")
target_encoder = joblib.load("target_encoder.pkl")

features = [
    "Crop_Encoded", "Pesticide_Usage", "Cropped_Area", "Area_Percent",
    "Total_Area_Sown", "Area_Thousand_Hect", "Production_Thousand_Tons",
    "Index_Area_Sown", "Index_Production",
    "Pesticide_per_Area", "Production_per_Area"
]

def predict_crop_risk(crop):
    if crop is None:
        return "Not available"

    crop_rows = df[df["Crop"].str.lower() == crop.lower()]

    if crop_rows.empty:
        return "Crop not found in dataset"

    row = crop_rows.iloc[0]
    X = row[features].to_frame().T

    prediction = model.predict(X)
    risk = target_encoder.inverse_transform(prediction)[0]

    return risk

def smart_agri_assistant(question):
    refusal = (
        "I am an AI specialized exclusively in agriculture. "
        "I cannot answer questions outside of farming, crops, soil, or livestock. "
        "Please ask an agriculture-related question."
    )

    entities = extract_entities(question)

    if entities.get("blocked"):
        return refusal

    if not any([entities.get("crop"), entities.get("location"), entities.get("issue")]):
        return refusal

    crop = entities.get("crop")
    location = entities.get("location")
    issue = entities.get("issue")

    crisis_risk = predict_crop_risk(crop)
    rag_answer = simple_rag_answer(question)
    mas_report = run_multi_agent_system()

    mas_risk = "Not available"
    mas_recommendation = "No live stream found. Run kafka_producer_sim.py for live MAS analysis."

    if "error" not in mas_report:
        mas_risk = mas_report["final_risk"]["status"]
        mas_recommendation = mas_report["recommendation"]["message"]

    final_answer = f"""
    <b>Detected Information</b><br>
    Crop: {crop}<br>
    Location: {location}<br>
    Issue: {issue}<br><br>

    <b>ML Crisis Prediction</b><br>
    {crisis_risk}<br><br>

    <b>MAS Live Analysis</b><br>
    {mas_risk}<br>
    {mas_recommendation}<br><br>

    <b>RAG Agriculture Advice</b><br>
    {rag_answer}
    """

    return final_answer

if __name__ == "__main__":
    q = input("Ask Smart Agribot: ")
    print(smart_agri_assistant(q))