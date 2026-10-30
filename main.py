from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent

app = FastAPI(title="VirtualCloset AI Agent")

# FIZA'S PERSONAL DIGITAL CLOSET INVENTORY
CLOSET_DATA = [
    # Tops
    {"item_id": "TOP-01", "name": "Chiffon Embroidered Long Shirt", "category": "top", "fabric": "chiffon", "color": "maroon", "formality": "festive", "comfort": "breathable/light"},
    {"item_id": "TOP-02", "name": "Silk Anarkali Frock", "category": "top", "fabric": "silk", "color": "emerald green", "formality": "formal", "comfort": "medium"},
    {"item_id": "TOP-03", "name": "Black Velvet Embroidered Kurti", "category": "top", "fabric": "velvet", "color": "black", "formality": "formal/party", "comfort": "warm"},
    {"item_id": "TOP-04", "name": "Cotton A-Line Printed Kurti", "category": "top", "fabric": "cotton", "color": "navy blue", "formality": "casual/picnic", "comfort": "high/breathable"},
    
    # Bottoms
    {"item_id": "BOT-01", "name": "Raw Silk Straight Trousers", "category": "bottom", "fabric": "raw silk", "color": "ivory", "formality": "festive/formal"},
    {"item_id": "BOT-02", "name": "Cotton Straight Pants", "category": "bottom", "fabric": "cotton", "color": "white", "formality": "casual/picnic"},
    {"item_id": "BOT-03", "name": "Black Tailored Trousers", "category": "bottom", "fabric": "cotton blend", "color": "black", "formality": "formal/party"},
    
    # Footwear
    {"item_id": "SH-01", "name": "Gold Embellished Khussa", "category": "footwear", "fabric": "leather/silk", "color": "gold", "formality": "festive"},
    {"item_id": "SH-02", "name": "Black Strap High Heels", "category": "footwear", "fabric": "leather", "color": "black", "formality": "formal/party"},
    {"item_id": "SH-03", "name": "White Comfort Canvas Sneakers", "category": "footwear", "fabric": "canvas", "color": "white", "formality": "casual/picnic"},
    
    # Accessories & Jewelry
    {"item_id": "ACC-01", "name": "Organza Printed Dupatta", "category": "accessory", "fabric": "organza", "color": "multicolor maroon/gold", "formality": "festive"},
    {"item_id": "ACC-02", "name": "Kundan Jhumkas & Pearl Ring", "category": "jewelry", "fabric": "metal/pearl", "color": "gold/white", "formality": "festive"},
    {"item_id": "ACC-03", "name": "Silver Minimalist Hoop Earrings", "category": "jewelry", "fabric": "silver", "color": "silver", "formality": "casual/party"}
]

@tool
def get_closet_items(category: str = "", formality: str = "", color: str = "") -> list:
    """Queries Fiza's digital closet inventory filtered by category, formality, or color preference."""
    filtered = CLOSET_DATA
    if category:
        filtered = [i for i in filtered if i["category"].lower() == category.lower()]
    if formality:
        filtered = [i for i in filtered if formality.lower() in i["formality"].lower()]
    if color:
        filtered = [i for i in filtered if color.lower() in i["color"].lower()]
    return filtered

@tool
def get_weather_context(city: str) -> dict:
    """Retrieves weather context for location-aware wardrobe styling."""
    c = city.lower().strip()
    if "karachi" in c:
        return {"city": "Karachi", "temp_c": 32, "humidity_pct": 78, "condition": "warm & humid", "advice": "Recommend light cotton, lawn, or chiffon fabrics."}
    elif "lahore" in c:
        return {"city": "Lahore", "temp_c": 28, "humidity_pct": 55, "condition": "pleasant breeze", "advice": "Ideal for silk or cotton blends."}
    return {"city": city.title(), "temp_c": 25, "humidity_pct": 50, "condition": "moderate", "advice": "Suitable for general wardrobe styling."}

TOOLS = [get_closet_items, get_weather_context]

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VirtualCloset AI — Personal Stylist Agent</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
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
                max-width: 740px;
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
                font-size: 34px;
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
                font-weight: 600;
                font-size: 14px;
                color: #734850;
            }
            textarea {
                width: 100%;
                height: 120px;
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
                padding: 15px 28px;
                border-radius: 12px;
                font-size: 15px;
                cursor: pointer;
                margin-top: 20px;
                width: 100%;
                font-weight: 600;
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
            <p class="subtitle">Your Autonomous Wardrobe Stylist & E-Commerce Recommendation Agent</p>
            <form action="/recommend" method="post">
                <label>Tell your agent what occasion or outfit you are styling for:</label>
                <textarea name="user_query">I am attending a festive dinner in Karachi tonight. Style an outfit from my digital closet!</textarea>
                <button type="submit">🌸 Curate My Outfit Recommendation</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/recommend", response_class=HTMLResponse)
def recommend(user_query: str = Form(...)):
    groq_key = os.environ.get("GROQ_API_KEY", "")
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_key, temperature=0.3)
    system_prompt = """You are VirtualCloset AI — an expert, context-aware personal wardrobe stylist agent.
    
    CORE RESPONSIBILITIES:
    1. Call `get_weather_context` if a city is mentioned to determine fabric and temperature constraints.
    2. Call `get_closet_items` to query the user's personal digital closet.
    3. Assemble an outfit from the user's closet (Top, Bottom, Footwear, Accessories).
    4. REORGANIZATION & MISSING PIECE RECOMMENDATIONS: If a critical piece (e.g. matching footwear, specific handbag, or specific jewelry) is missing from the closet inventory to complete the look for the event, explicitly recommend a missing item piece with an e-commerce shopping recommendation!
    5. Format output with clear headers, weather rationale, and styling tips."""
    
    agent = create_agent(llm, TOOLS, system_prompt=system_prompt)
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    outfit_text = result["messages"][-1].content.replace("\n", "<br>")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Curated Outfit Card</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
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
                max-width: 740px;
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
                padding: 24px;
                border-radius: 12px;
                margin-top: 20px;
                line-height: 1.8;
                font-size: 14.5px;
            }}
            a {{
                display: inline-block;
                margin-top: 25px;
                color: #8c535d;
                text-decoration: none;
                font-weight: 600;
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
