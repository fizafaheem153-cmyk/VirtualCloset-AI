from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent

app = FastAPI(title="VirtualCloset AI Agent")

# Wardrobe Inventory Dataset
CLOSET_DATA = [
    {"item_id": "TOP-01", "name": "Chiffon Embroidered Long Shirt", "category": "top", "fabric": "chiffon", "color": "maroon", "formality": "festive", "comfort_rating": 8},
    {"item_id": "TOP-02", "name": "Silk Anarkali Frock", "category": "top", "fabric": "silk", "color": "emerald green", "formality": "formal", "comfort_rating": 7},
    {"item_id": "TOP-03", "name": "Black Velvet Embroidered Kurti", "category": "top", "fabric": "velvet", "color": "black", "formality": "formal", "comfort_rating": 9},
    {"item_id": "TOP-05", "name": "Cotton A-Line Kurti", "category": "top", "fabric": "cotton", "color": "navy blue", "formality": "casual", "comfort_rating": 10},
    {"item_id": "BOT-01", "name": "Silk Straight Trousers", "category": "bottom", "fabric": "silk", "color": "ivory", "formality": "festive", "comfort_rating": 9},
    {"item_id": "BOT-02", "name": "Black Bell-Bottom Trousers", "category": "bottom", "fabric": "cotton/silk", "color": "black", "formality": "formal", "comfort_rating": 9},
    {"item_id": "BOT-03", "name": "Cotton Straight Trousers", "category": "bottom", "fabric": "cotton", "color": "white", "formality": "casual", "comfort_rating": 10},
    {"item_id": "SH-01", "name": "Embellished Khussa", "category": "footwear", "fabric": "leather/silk", "color": "gold", "formality": "festive", "comfort_rating": 7},
    {"item_id": "SH-02", "name": "Black Strap Heels", "category": "footwear", "fabric": "leather", "color": "black", "formality": "formal", "comfort_rating": 8},
    {"item_id": "SH-03", "name": "Minimalist Leather Slides", "category": "footwear", "fabric": "leather", "color": "tan", "formality": "casual", "comfort_rating": 10},
    {"item_id": "DUP-01", "name": "Chiffon Printed Dupatta", "category": "accessory", "fabric": "chiffon", "color": "multicolor maroon/gold", "formality": "festive", "comfort_rating": 9},
    {"item_id": "ACC-01", "name": "Kundan Jhumkas", "category": "accessory", "fabric": "metal/pearl", "color": "gold/white", "formality": "festive", "comfort_rating": 8},
    {"item_id": "ACC-02", "name": "Silver Statement Earrings", "category": "accessory", "fabric": "silver", "color": "silver", "formality": "formal", "comfort_rating": 9}
]

@tool
def get_closet_items(category: str = "", formality: str = "", color: str = "") -> list:
    """Searches digital wardrobe inventory filtered by category, formality, or color preference."""
    filtered = CLOSET_DATA
    if category:
        filtered = [i for i in filtered if i["category"].lower() == category.lower()]
    if formality:
        filtered = [i for i in filtered if i["formality"].lower() == formality.lower()]
    if color:
        filtered = [i for i in filtered if color.lower() in i["color"].lower()]
    return filtered

@tool
def get_weather_context(city: str) -> dict:
    """Retrieves weather conditions for outfit planning."""
    weather_db = {
        "karachi": {"temperature_c": 32, "humidity_pct": 78, "condition": "humid & warm"},
        "lahore": {"temperature_c": 28, "humidity_pct": 55, "condition": "pleasant breeze"},
        "islamabad": {"temperature_c": 22, "humidity_pct": 40, "condition": "cool"}
    }
    return weather_db.get(city.lower().strip(), {"temperature_c": 30, "humidity_pct": 65, "condition": "moderate"})

TOOLS = [get_closet_items, get_weather_context]

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VirtualCloset AI — Personal Stylist</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Poppins:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background-color: #fdf8f5;
                background-image: radial-gradient(#e8d3cb 1px, transparent 1px);
                background-size: 20px 20px;
                padding: 40px 20px;
                margin: 0;
                color: #4a3e3d;
            }
            .container {
                max-width: 720px;
                margin: 0 auto;
                background: #ffffff;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(218, 185, 178, 0.3);
                border: 1px solid #f2e2dc;
            }
            h1 {
                font-family: 'Playfair Display', serif;
                color: #8c535d;
                font-size: 32px;
                margin-bottom: 6px;
                text-align: center;
            }
            p.subtitle {
                text-align: center;
                color: #a37f86;
                font-size: 14px;
                margin-bottom: 30px;
                font-style: italic;
            }
            label {
                font-weight: 500;
                font-size: 14px;
                color: #734850;
            }
            textarea {
                width: 100%;
                height: 110px;
                padding: 16px;
                margin-top: 8px;
                border: 1.5px solid #f3d5d8;
                border-radius: 12px;
                font-size: 14px;
                font-family: 'Poppins', sans-serif;
                background-color: #fcf0f2;
                color: #4a3e3d;
                box-sizing: border-box;
                outline: none;
                transition: border 0.3s ease;
            }
            textarea:focus { border-color: #d9929d; }
            button {
                background: linear-gradient(135deg, #e6a5af 0%, #c97987 100%);
                color: white;
                border: none;
                padding: 14px 28px;
                border-radius: 12px;
                font-size: 15px;
                cursor: pointer;
                margin-top: 20px;
                width: 100%;
                font-weight: 500;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 15px rgba(201, 121, 135, 0.3);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(201, 121, 135, 0.4);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ VirtualCloset AI</h1>
            <p class="subtitle">Your Agentic Wardrobe & Event Stylist</p>
            <form action="/recommend" method="post">
                <label>Describe your occasion, location & styling preferences:</label>
                <textarea name="user_query">I am attending a dinner party in Karachi and want to dress in something black. Style me!</textarea>
                <button type="submit">🌸 Curate My Outfit Recommendation</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/recommend", response_class=HTMLResponse)
def recommend(user_query: str = Form(...)):
    groq_key = os.environ.get("GROQ_API_KEY", "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")
    os.environ["GROQ_API_KEY"] = groq_key
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
    system_prompt = """You are VirtualCloset AI, an expert personal wardrobe stylist.
    1. Check `get_weather_context` first if a city is mentioned or implied.
    2. Search `get_closet_items` to retrieve wardrobe choices based on user preferences.
    3. Synthesize a unique, custom outfit recommendation matching the exact request."""
    
    agent = create_agent(llm, TOOLS, system_prompt=system_prompt)
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    outfit_text = result["messages"][-1].content.replace("\n", "<br>")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Curated Outfit Card</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Poppins:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Poppins', sans-serif;
                background-color: #fdf8f5;
                background-image: radial-gradient(#e8d3cb 1px, transparent 1px);
                background-size: 20px 20px;
                padding: 40px 20px;
                color: #4a3e3d;
            }}
            .container {{
                max-width: 720px;
                margin: 0 auto;
                background: #ffffff;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(218, 185, 178, 0.3);
                border: 1px solid #f2e2dc;
            }}
            h2 {{
                font-family: 'Playfair Display', serif;
                color: #8c535d;
                font-size: 26px;
                border-bottom: 1px solid #f2d2d6;
                padding-bottom: 12px;
                margin-top: 0;
            }}
            .card {{
                background-color: #fcf0f2;
                border-left: 4px solid #d9929d;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                line-height: 1.7;
                font-size: 14.5px;
            }}
            a {{
                display: inline-block;
                margin-top: 25px;
                color: #8c535d;
                text-decoration: none;
                font-weight: 500;
            }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🌸 Your Curated Outfit Recommendation</h2>
            <div class="card">{outfit_text}</div>
            <a href="/">← Back to Stylist Input</a>
        </div>
    </body>
    </html>
    """
