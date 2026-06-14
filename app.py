from flask import Flask, request
import pandas as pd
import joblib
import json

from smart_assistant import smart_agri_assistant
from multi_agent_system import run_multi_agent_system

app = Flask(__name__)

df = pd.read_csv("final_agriculture_crisis_dataset.csv")
model = joblib.load("agri_crisis_model.pkl")
target_encoder = joblib.load("target_encoder.pkl")

features = [
    "Crop_Encoded", "Pesticide_Usage", "Cropped_Area", "Area_Percent",
    "Total_Area_Sown", "Area_Thousand_Hect", "Production_Thousand_Tons",
    "Index_Area_Sown", "Index_Production",
    "Pesticide_per_Area", "Production_per_Area"
]

def get_model_accuracy():
    try:
        return round(model.score(df[features], df["Target"]) * 100, 2)
    except:
        return "N/A"

def load_table(file_name):
    try:
        return pd.read_csv(file_name).to_html(index=False, classes="data-table")
    except:
        return "<p class='muted'>Run sql_analytics.py first.</p>"

def load_kafka_events():
    try:
        with open("kafka_events.jsonl", "r") as file:
            lines = file.readlines()[-8:]
        events = [json.loads(line) for line in lines]
        return pd.DataFrame(events).to_html(index=False, classes="data-table")
    except:
        return "<p class='muted'>No live events found. Run kafka_producer_sim.py first.</p>"

def dashboard(chatbot_result=None, mas_result=None):
    low = len(df[df["Crisis_Level"] == "Low Risk"])
    medium = len(df[df["Crisis_Level"] == "Medium Risk"])
    high = len(df[df["Crisis_Level"] == "High Risk"])
    accuracy = get_model_accuracy()

    chatbot_html = ""
    if chatbot_result:
        chatbot_html = f"""
        <div class="answer-box">
            <h3>🌸 Smart Agribot Response</h3>
            <p><b>Question:</b> {chatbot_result['question']}</p>
            <p>{chatbot_result['answer']}</p>
        </div>
        """

    mas_html = mas_result if mas_result else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AgriCrisis AI Dashboard</title>

        <style>
            body {{
                margin: 0;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #f0fff4, #fff7ed);
                color: #1b4332;
            }}

            .hero {{
                padding: 40px;
                text-align: center;
                color: white;
                background: linear-gradient(135deg, #2d6a4f, #95d5b2);
                border-bottom-left-radius: 40px;
                border-bottom-right-radius: 40px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }}

            .hero h1 {{
                margin: 0;
                font-size: 36px;
            }}

            .hero p {{
                margin-top: 10px;
                font-size: 16px;
            }}

            .container {{
                width: 92%;
                margin: 30px auto;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 18px;
                margin-bottom: 25px;
            }}

            .card, .panel {{
                background: rgba(255,255,255,0.95);
                border-radius: 24px;
                padding: 24px;
                box-shadow: 0 8px 22px rgba(45,106,79,0.14);
                border: 1px solid #d8f3dc;
            }}

            .card h2 {{
                margin: 0;
                font-size: 16px;
                color: #40916c;
            }}

            .card h1 {{
                margin: 10px 0 0;
                font-size: 30px;
            }}

            .main-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 22px;
                align-items: start;
                margin-bottom: 25px;
            }}

            input {{
                width: 94%;
                padding: 14px;
                border: 1px solid #b7e4c7;
                border-radius: 14px;
                outline: none;
                margin-top: 10px;
                font-size: 14px;
            }}

            button {{
                background: linear-gradient(135deg, #2d6a4f, #52b788);
                color: white;
                padding: 12px 22px;
                border: none;
                border-radius: 14px;
                margin-top: 12px;
                cursor: pointer;
                font-weight: 700;
            }}

            button:hover {{
                transform: scale(1.03);
            }}

            .answer-box {{
                background: #fff8e7;
                border-left: 6px solid #f4a261;
                padding: 18px;
                border-radius: 18px;
                margin-top: 18px;
                line-height: 1.6;
            }}

            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
                font-size: 14px;
            }}

            .data-table th {{
                background: #2d6a4f;
                color: white;
                padding: 10px;
            }}

            .data-table td {{
                padding: 9px;
                border: 1px solid #d8f3dc;
                text-align: center;
            }}

            .data-table tr:nth-child(even) {{
                background: #f1faee;
            }}

            .live-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: #e9f7ef;
                border-radius: 18px;
                padding: 15px;
                margin-bottom: 15px;
            }}

            .clock {{
                font-size: 24px;
                font-weight: bold;
            }}

            .muted {{
                color: #6c757d;
            }}

            .big-risk {{
                font-size: 26px;
                font-weight: bold;
                color: #d9480f;
            }}

            @media(max-width: 900px) {{
                .cards, .main-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>

        <script>
            function updateClock() {{
                const now = new Date();
                document.getElementById("clock").innerHTML = now.toLocaleTimeString();
            }}
            setInterval(updateClock, 1000);
            window.onload = updateClock;
        </script>
    </head>

    <body>
        <div class="hero">
            <h1>🌾 AgriCrisis AI Dashboard</h1>
            <p>Made with ❤️ by Rameen & Rida | ML • MAS • NER • RAG • Kafka Streaming</p>
        </div>

        <div class="container">

            <div class="cards">
                <div class="card">
                    <h2>Total Records</h2>
                    <h1>{len(df)}</h1>
                </div>

                <div class="card">
                    <h2>Total Crops</h2>
                    <h1>{df['Crop'].nunique()}</h1>
                </div>

                <div class="card">
                    <h2>Model Accuracy</h2>
                    <h1>{accuracy}%</h1>
                </div>

                <div class="card">
                    <h2>Risk Summary</h2>
                    <p>Low: {low}</p>
                    <p>Medium: {medium}</p>
                    <p>High: {high}</p>
                </div>
            </div>

            <div class="main-grid">

                <div class="panel">
                    <h2>🤖 Smart Agribot Assistant</h2>
                    <p>
                        Ask one agriculture question. Agribot will use
                        <b>NER + ML Crisis Prediction + MAS + RAG</b> together.
                    </p>

                    <form action="/chatbot" method="post">
                        <input
                            type="text"
                            name="question"
                            placeholder="Example: Wheat crop in Multan has severe pest attack"
                            required
                        >
                        <button type="submit">Ask Smart Agribot</button>
                    </form>

                    {chatbot_html}
                </div>

                <div class="panel">
                    <div class="live-header">
                        <div>
                            <h2>📡 Kafka Live Stream</h2>
                            <p class="muted">Real-time agricultural event monitoring</p>
                        </div>

                        <div>
                            <div class="clock" id="clock"></div>
                            <form action="/" method="get">
                                <button type="submit">Refresh Stream</button>
                            </form>
                        </div>
                    </div>

                    {load_kafka_events()}
                </div>

            </div>

            <div class="panel">
                <h2>🧠 Multi-Agent System</h2>
                <p>Weather Agent • Pesticide Agent • Crop Agent • Risk Agent • Recommendation Agent</p>

                <form action="/mas" method="post">
                    <button type="submit">Run MAS Analysis</button>
                </form>

                {mas_html}
            </div>

            <div class="panel">
                <h2>📈 SQL Analytics Dashboard</h2>

                <h3>Top Crops by Pesticide Usage</h3>
                {load_table("top_crops_by_pesticide_usage.csv")}

                <h3>Crop Production Summary</h3>
                {load_table("crop_production_summary.csv")}

                <h3>Crisis Risk Count</h3>
                {load_table("crisis_risk_count.csv")}

                <h3>Cropped Area Analysis</h3>
                {load_table("cropped_area_analysis.csv")}
            </div>

        </div>
    </body>
    </html>
    """

@app.route("/")
def home():
    return dashboard()

@app.route("/chatbot", methods=["POST"])
def chatbot():
    question = request.form["question"].strip()
    answer = smart_agri_assistant(question)

    return dashboard(chatbot_result={
        "question": question,
        "answer": answer
    })

@app.route("/mas", methods=["GET", "POST"])
def mas():
    report = run_multi_agent_system()

    if "error" in report:
        return dashboard(mas_result=f"<div class='answer-box'><p>{report['error']}</p></div>")

    latest = report["latest_event"]
    agents = report["agents"]
    final_risk = report["final_risk"]
    recommendation = report["recommendation"]

    rows = ""
    for agent in agents:
        rows += f"""
        <tr>
            <td>{agent['agent']}</td>
            <td>{agent['status']}</td>
            <td>{agent['message']}</td>
        </tr>
        """

    mas_html = f"""
    <div class="answer-box">
        <h3>Latest Event</h3>
        <p><b>District:</b> {latest['district']}</p>
        <p><b>Crop:</b> {latest['crop']}</p>
        <p><b>Temperature:</b> {latest['temperature']}°C</p>
        <p><b>Humidity:</b> {latest['humidity']}%</p>

        <h3>Agent Outputs</h3>
        <table class="data-table">
            <tr>
                <th>Agent</th>
                <th>Status</th>
                <th>Message</th>
            </tr>
            {rows}
        </table>

        <h3>Final Risk</h3>
        <p class="big-risk">{final_risk['status']}</p>

        <h3>Recommendation</h3>
        <p>{recommendation['message']}</p>
    </div>
    """

    return dashboard(mas_result=mas_html)

if __name__ == "__main__":
    app.run(debug=True)