from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
import requests

app = FastAPI(title="VirtualCloset AI Agent")

# COMPREHENSIVE DIGITAL CLOSET DATABASE
CLOSET_DATA = [
    # --- WOMEN'S EASTERN ---
    {"item_id": "W-01", "name": "Chiffon Embroidered Long Shirt", "gender": "female", "style": "eastern", "category": "top", "fabric": "chiffon", "color": "maroon", "formality": "festive/formal"},
    {"item_id": "W-02", "name": "Silk Anarkali Frock", "gender": "female", "style": "eastern", "category": "top", "fabric": "silk", "color": "emerald green", "formality": "formal/wedding"},
    {"item_id": "W-03", "name": "Black Velvet Embroidered Kurti", "gender": "female", "style": "eastern", "category": "top", "fabric": "velvet", "color": "black", "formality": "formal/winter"},
    {"item_id": "W-04", "name": "Cotton A-Line Printed Kurti", "gender": "female", "style": "eastern", "category": "top", "fabric": "cotton", "color": "navy blue", "formality": "casual/university/dayout"},
    {"item_id": "W-05", "name": "Lawn Printed Kurti", "gender": "female", "style": "eastern", "category": "top", "fabric": "lawn/cotton", "color": "peach/pastel", "formality": "casual/university"},
    {"item_id": "W-11", "name": "Raw Silk Straight Trousers", "gender": "female", "style": "eastern", "category": "bottom", "fabric": "raw silk", "color": "ivory", "formality": "festive/formal"},
    {"item_id": "W-12", "name": "Cotton Straight Pants", "gender": "female", "style": "eastern", "category": "bottom", "fabric": "cotton", "color": "white", "formality": "casual/university"},

    # --- WOMEN'S WESTERN ---
    {"item_id": "W-06", "name": "Floral Summer Midi Dress", "gender": "female", "style": "western", "category": "dress", "fabric": "viscose", "color": "yellow/floral", "formality": "casual/picnic"},
    {"item_id": "W-07", "name": "Black Satin Evening Maxi Dress", "gender": "female", "style": "western", "category": "dress", "fabric": "satin", "color": "black", "formality": "formal/party"},
    {"item_id": "W-08", "name": "Classic White Linen Button-Down Shirt", "gender": "female", "style": "western", "category": "top", "fabric": "linen", "color": "white", "formality": "smart_casual"},
    {"item_id": "W-09", "name": "Warm Wool Trench Coat", "gender": "female", "style": "western", "category": "outerwear", "fabric": "wool", "color": "camel brown", "formality": "winter/travel"},
    {"item_id": "W-10", "name": "High-Waisted Denim Jeans", "gender": "female", "style": "western", "category": "bottom", "fabric": "denim", "color": "blue", "formality": "casual"},

    # --- MEN'S APPAREL ---
    {"item_id": "M-01", "name": "Raw Silk Black Kurta Pajama", "gender": "male", "style": "eastern", "category": "full_outfit", "fabric": "silk", "color": "black", "formality": "formal/evening"},
    {"item_id": "M-02", "name": "White Breathable Cotton Kurta Shalwar", "gender": "male", "style": "eastern", "category": "full_outfit", "fabric": "cotton", "color": "white", "formality": "casual/dayout"},
    {"item_id": "M-03", "name": "Jamawar Embroidered Waistcoat", "gender": "male", "style": "eastern", "category": "outerwear", "fabric": "jamawar", "color": "gold/maroon", "formality": "festive"},
    {"item_id": "M-04", "name": "Slim-Fit Charcoal Suit", "gender": "male", "style": "western", "category": "suit", "fabric": "wool blend", "color": "charcoal", "formality": "formal/business"},
    {"item_id": "M-05", "name": "Casual Crew-Neck Cotton T-Shirt", "gender": "male", "style": "western", "category": "top", "fabric": "cotton", "color": "black", "formality": "casual"},
    {"item_id": "M-06", "name": "Puffer Winter Jacket", "gender": "male", "style": "western", "category": "outerwear", "fabric": "polyester/down", "color": "navy blue", "formality": "winter/travel"},

    # --- FOOTWEAR & ACCESSORIES ---
    {"item_id": "A-01", "name": "Gold Embellished Khussa", "gender": "female", "style": "eastern", "category": "footwear", "fabric": "leather/silk", "color": "gold", "formality": "festive"},
    {"item_id": "A-02", "name": "Black Strap High Heels", "gender": "female", "style": "western", "category": "footwear", "fabric": "leather", "color": "black", "formality": "formal/party"},
    {"item_id": "A-03", "name": "White Canvas Comfortable Sneakers", "gender": "unisex", "style": "western", "category": "footwear", "fabric": "canvas", "color": "white", "formality": "casual/university/travel"},
    {"item_id": "A-04", "name": "Leather Walking Boots", "gender": "unisex", "style": "western", "category": "footwear", "fabric": "leather", "color": "brown", "formality": "winter/travel"},
    {"item_id": "A-05", "name": "Kundan Jhumkas & Pearl Statement Jewelry", "gender": "female", "style": "eastern", "category": "jewelry", "fabric": "metal/pearl", "color": "gold/white", "formality": "festive"}
]

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
            <p class="subtitle">Autonomous Wardrobe Stylist & E-Commerce Recommendation Agent</p>
            <form action="/recommend" method="post">
                <label>Tell your AI agent what occasion, city, gender, or outfit style you are looking for:</label>
                <textarea name="user_query" placeholder="e.g., I am attending a class at University of Karachi. Style a comfortable female outfit for me from my closet!">I am attending a class at University of Karachi. Style a comfortable female outfit for me from my closet!</textarea>
                <button type="submit">🌸 Curate My Outfit Recommendation</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/recommend", response_class=HTMLResponse)
def recommend(user_query: str = Form(...)):
    groq_key = os.environ.get("GROQ_API_KEY", "")
    
    system_prompt = f"""You are VirtualCloset AI — a world-class, context-aware global personal fashion stylist.

USER REQUEST: "{user_query}"

AVAILABLE DIGITAL CLOSET INVENTORY:
{json.dumps(CLOSET_DATA, indent=2)}

EXPERT STYLING DIRECTIVES:
1. DEEP REASONING: Analyze the exact location, specific activity (university, picnic, formal dinner, travel, museum), gender (male/female), and climate/weather expectations.
2. DETAILED OUTPUT STRUCTURE: Generate a thorough, multi-part styling response (3 paragraphs total) formatted in clean HTML:
   - 🌍 **Destination, Climate & Occasion Analysis**: Explain the local setting, expected weather conditions, and styling etiquette.
   - 👗 / 👔 **Selected Closet Outfit Ensemble**: Detail the exact Top/Outfit, Bottom, Footwear, and Accessories picked from the wardrobe.
   - 🛍️ **E-Commerce Missing Piece Recommendation**: Identify an accessory, handbag, sunglasses, or outerwear missing from the closet and recommend buying it.
   - ✨ **Pro Styling, Fabric Comfort & Grooming Tips**: Give 3 practical tips tailored directly to the event.
3. Keep the tone warm, highly descriptive, professional, and engaging."""

    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
    
    # Try llama-3.1-70b-versatile first, fallback to llama3-70b-8192
    models_to_try = ["llama-3.1-70b-versatile", "llama3-70b-8192"]
    outfit_text = None

    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are an expert AI fashion stylist."},
                {"role": "user", "content": system_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1200
        }
        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                outfit_text = resp.json()["choices"][0]["message"]["content"].replace("\n", "<br>")
                break
        except Exception:
            continue

    if not outfit_text:
        outfit_text = "<b>Styling Agent Update:</b> Service temporarily unreachable. Please check your GROQ_API_KEY in Vercel settings."

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
