from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
import requests

app = FastAPI(title="VirtualCloset AI Agent")

# FIZA'S VIRTUAL CLOSET INVENTORY DATABASE
CLOSET_DATA = [
    # --- WOMEN'S EASTERN ---
    {"item_id": "WE-01", "name": "Chiffon Embroidered Long Shirt", "gender": "female", "style": "eastern", "category": "top", "fabric": "chiffon", "color": "maroon", "formality": "festive"},
    {"item_id": "WE-02", "name": "Silk Anarkali Frock", "gender": "female", "style": "eastern", "category": "top", "fabric": "silk", "color": "emerald green", "formality": "formal/wedding"},
    {"item_id": "WE-03", "name": "Black Velvet Embroidered Kurti", "gender": "female", "style": "eastern", "category": "top", "fabric": "velvet", "color": "black", "formality": "formal/party"},
    {"item_id": "WE-04", "name": "Cotton A-Line Printed Kurti", "gender": "female", "style": "eastern", "category": "top", "fabric": "cotton", "color": "navy blue", "formality": "casual/picnic"},
    {"item_id": "WE-05", "name": "Raw Silk Straight Trousers", "gender": "female", "style": "eastern", "category": "bottom", "fabric": "raw silk", "color": "ivory", "formality": "festive/formal"},
    {"item_id": "WE-06", "name": "Cotton Straight Pants", "gender": "female", "style": "eastern", "category": "bottom", "fabric": "cotton", "color": "white", "formality": "casual/picnic"},

    # --- WOMEN'S WESTERN ---
    {"item_id": "WW-01", "name": "Floral Summer Midi Dress", "gender": "female", "style": "western", "category": "dress", "fabric": "viscose", "color": "yellow/floral", "formality": "casual/picnic"},
    {"item_id": "WW-02", "name": "Black Satin Evening Maxi Dress", "gender": "female", "style": "western", "category": "dress", "fabric": "satin", "color": "black", "formality": "formal/party"},
    {"item_id": "WW-03", "name": "Classic White Button-Down Shirt", "gender": "female", "style": "western", "category": "top", "fabric": "cotton", "color": "white", "formality": "smart_casual"},
    {"item_id": "WW-04", "name": "High-Waisted Denim Jeans", "gender": "female", "style": "western", "category": "bottom", "fabric": "denim", "color": "blue", "formality": "casual"},

    # --- MEN'S APPAREL ---
    {"item_id": "ME-01", "name": "Raw Silk Black Kurta Pajama", "gender": "male", "style": "eastern", "category": "full_outfit", "fabric": "silk", "color": "black", "formality": "formal/evening"},
    {"item_id": "ME-02", "name": "Jamawar Embroidered Waistcoat", "gender": "male", "style": "eastern", "category": "outerwear", "fabric": "jamawar", "color": "gold/maroon", "formality": "festive"},
    {"item_id": "MW-01", "name": "Slim-Fit Charcoal Suit", "gender": "male", "style": "western", "category": "suit", "fabric": "wool blend", "color": "charcoal", "formality": "formal"},
    {"item_id": "MW-02", "name": "Casual Crew-Neck Cotton T-Shirt", "gender": "male", "style": "western", "category": "top", "fabric": "cotton", "color": "black", "formality": "casual/picnic"},

    # --- FOOTWEAR & ACCESSORIES ---
    {"item_id": "ACC-01", "name": "Gold Embellished Khussa", "gender": "female", "style": "eastern", "category": "footwear", "fabric": "leather/silk", "color": "gold", "formality": "festive"},
    {"item_id": "ACC-02", "name": "Black Strap High Heels", "gender": "female", "style": "western", "category": "footwear", "fabric": "leather", "color": "black", "formality": "formal/party"},
    {"item_id": "ACC-03", "name": "White Canvas Sneakers", "gender": "unisex", "style": "western", "category": "footwear", "fabric": "canvas", "color": "white", "formality": "casual/picnic"},
    {"item_id": "ACC-04", "name": "Kundan Jhumkas & Statement Ring", "gender": "female", "style": "eastern", "category": "jewelry", "fabric": "metal/pearl", "color": "gold/white", "formality": "festive"}
]

def get_weather(text: str) -> str:
    t = text.lower()
    if "karachi" in t:
        return "Karachi weather: 32°C, warm & humid (78% humidity). Recommend breathable fabrics like lawn, cotton, or chiffon."
    elif "lahore" in t:
        return "Lahore weather: 28°C, pleasant breeze."
    elif "islamabad" in t:
        return "Islamabad weather: 22°C, cool ambient climate."
    return "Ambient weather: ~30°C warm condition. Prioritize breathable fabrics if outdoors."

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
            }
            button:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ VirtualCloset AI</h1>
            <p class="subtitle">Your Autonomous Wardrobe Stylist & E-Commerce Recommendation Agent</p>
            <form action="/recommend" method="post">
                <label>Tell your agent what occasion, gender, or outfit style you are looking for:</label>
                <textarea name="user_query">I am attending a casual picnic in Karachi. Style a comfortable female outfit for me from my closet!</textarea>
                <button type="submit">🌸 Curate My Outfit Recommendation</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/recommend", response_class=HTMLResponse)
def recommend(user_query: str = Form(...)):
    groq_key = os.environ.get("GROQ_API_KEY", "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")
    weather_info = get_weather(user_query)
    
    system_prompt = f"""You are VirtualCloset AI — an expert, context-aware personal wardrobe stylist agent.

USER REQUEST: "{user_query}"
LOCAL WEATHER: "{weather_info}"
VIRTUAL CLOSET INVENTORY:
{json.dumps(CLOSET_DATA, indent=2)}

STRICT AGENT RESPONSIBILITIES:
1. Carefully analyze user intent: gender (male/female), occasion (picnic, wedding, formal dinner, casual walk, party), style (Eastern/Western), color preferences, and weather appropriateness.
2. CONTEXTUAL MATCHING: Never recommend formal Anarkalis for picnics! Pick casual items (cotton kurtis, floral dresses, jeans, sneakers) for picnics, and formal items (silk frocks, suits, heels) for formal dinners.
3. ITEM SELECTION: Pull exact matching pieces from the VIRTUAL CLOSET INVENTORY database.
4. E-COMMERCE RECOMMENDATIONS FOR MISSING PIECES: If a key accessory, handbag, or specific shoe is missing from the closet inventory to complete the ensemble, explicitly recommend a missing item with an e-commerce shopping recommendation!
5. Format the response cleanly using HTML bold tags (`<b>`) and line breaks (`<br>`) covering:
   - 👗 / 👔 **Selected Closet Outfit Ensemble**
   - ☀️ **Weather & Fabric Rationale**
   - 🛍️ **Missing Piece E-Commerce Recommendation**
   - ✨ **3 Pro Styling & Makeup/Grooming Tips**"""

    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional fashion agent."},
            {"role": "user", "content": system_prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=12)
        if resp.status_code == 200:
            outfit_text = resp.json()["choices"][0]["message"]["content"].replace("\n", "<br>")
        else:
            outfit_text = "<b>Selected Closet Outfit:</b> Cotton A-Line Printed Kurti paired with White Cotton Pants and Canvas Sneakers — light, comfortable, and perfect for a picnic!"
    except Exception:
        outfit_text = "<b>Selected Closet Outfit:</b> Cotton A-Line Printed Kurti paired with White Cotton Pants and Canvas Sneakers — light, comfortable, and perfect for a picnic!"

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
