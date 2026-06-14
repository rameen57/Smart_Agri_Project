import os
from google import genai

def ask_agri_llm(question, entities=None, rag_context="", ml_risk="", mas_risk="", mas_recommendation=""):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Gemini API key not found. Please set GEMINI_API_KEY first."

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are Agribot, a strict agriculture-only assistant.

Rules:
- Answer ONLY agriculture-related questions.
- Do NOT answer politics, celebrities, coding, general math, entertainment, or unrelated topics.
- If the question is outside agriculture, reply exactly:
"I am an AI specialized exclusively in agriculture. I cannot answer questions outside of farming, crops, soil, or livestock. Please ask an agriculture-related question."

Farmer question:
{question}

Extracted entities:
{entities}

Project model crisis risk:
{ml_risk}

MAS live risk:
{mas_risk}

MAS recommendation:
{mas_recommendation}

Local RAG context:
{rag_context}

Now give a helpful, easy, farmer-friendly agriculture answer.
Keep it practical and short.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text