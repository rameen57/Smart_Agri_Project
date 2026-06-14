import pandas as pd
import joblib

from ner_engine import extract_entities
from rag_engine import simple_rag_answer
from multi_agent_system import run_multi_agent_system

try:
    from llm_agri_api import ask_agri_llm
    LLM_AVAILABLE = True
except:
    LLM_AVAILABLE = False


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

    crop = entities.get("crop")
    location = entities.get("location")
    issue = entities.get("issue")

    # Allow agriculture questions even if issue is None
    if not any([crop, location, issue]):
        agriculture_words = [
            "crop", "crops", "agriculture", "farm", "farming", "farmer",
            "soil", "irrigation", "fertilizer", "pesticide", "yield",
            "production", "harvest", "season", "summer", "winter",
            "rice", "wheat", "cotton", "maize", "sugarcane"
        ]

        if not any(word in question.lower() for word in agriculture_words):
            return refusal

    # 1. ML crisis prediction
    crisis_risk = predict_crop_risk(crop)

    # 2. RAG answer
    try:
        rag_answer = simple_rag_answer(question)
    except:
        rag_answer = "No local RAG answer available."

    # 3. MAS live analysis
    mas_risk = "Not available"
    mas_recommendation = "No live stream found. Run kafka_producer_sim.py for live MAS analysis."

    try:
        mas_report = run_multi_agent_system()

        if "error" not in mas_report:
            mas_risk = mas_report["final_risk"]["status"]
            mas_recommendation = mas_report["recommendation"]["message"]
    except:
        pass

    # 4. API/LLM answer if available
    if LLM_AVAILABLE:
        try:
            api_answer = ask_agri_llm(
                question=question,
                entities=entities,
                rag_context=rag_answer,
                ml_risk=crisis_risk,
                mas_risk=mas_risk,
                mas_recommendation=mas_recommendation
            )
        except Exception as e:
            api_answer = f"API answer unavailable. Reason: {str(e)}"
    else:
        api_answer = "API layer is not connected yet. Showing local system response only."

    final_answer = api_answer
    return final_answer

if __name__ == "__main__":
    q = input("Ask Smart Agribot: ")
    print(smart_agri_assistant(q))