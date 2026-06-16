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

Formatting Rules:
- Do NOT use markdown.
- Do NOT use ** symbols.
- Do NOT use bullet points.
- Use simple HTML tags only.
- Use <h3> for headings.
- Use <p> for paragraphs.
- Use <br> for line breaks.
- Keep the answer clean, professional, and farmer-friendly.
- Structure the answer using:
<h3>🌾 Recommendation</h3>
<p>...</p>
<h3>⚠ Important Notes</h3>
<p>...</p>
<h3>✅ Suggested Action</h3>
<p>...</p>

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

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = response.text

        answer = answer.replace("**", "")
        answer = answer.replace("* ", "• ")

        return answer

    except Exception as e:
        return f"""
        <h3>🌾 Agribot Recommendation</h3>
        <p>API answer is temporarily unavailable.</p>
        <h3>⚠ Important Notes</h3>
        <p>{str(e)}</p>
        <h3>✅ Suggested Action</h3>
        <p>Please try again after a few minutes.</p>
        """