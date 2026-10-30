from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
import requests

app = FastAPI(title="VirtualCloset AI Agent")

# Complete Men's & Women's Eastern & Western Wardrobe Inventory
CLOSET_DATA = [
    # --- WOMEN'S EASTERN ---
    {"item_id": "WE-01", "name": "Chiffon Embroidered Long Shirt", "gender": "female", "style": "eastern", "category": "top", "fabric": "chiffon", "color": "maroon", "formality": "festive/formal"},
    {"item_id": "WE-02", "name": "Silk Anarkali Frock", "gender": "female", "style": "eastern", "category": "top", "fabric": "silk", "color": "emerald green", "formality": "formal/wedding"},
    {"item_id": "WE-03", "name": "Cotton A-Line Printed Kurti", "gender": "female", "style": "eastern", "category": "top", "fabric": "cotton", "color": "navy blue", "formality": "casual/picnic"},
    {"item_id": "WE-04", "name": "Lawn Printed 3-Piece Unstitched Suit", "gender": "female", "style": "eastern", "category": "full_outfit", "fabric": "lawn", "color": "pastel pink", "formality": "casual/daywear"},
    {"item_id": "WE-05", "name": "Raw Silk Straight Trousers", "gender": "female", "style": "eastern", "category": "bottom", "fabric": "raw silk", "color": "ivory", "formality": "formal/festive"},
    {"item_id": "WE-06", "name": "Cotton Straight Pants", "gender": "female", "style": "eastern", "category": "bottom", "fabric": "cotton", "color": "white", "formality": "casual"},
    {"item_id": "WE-07", "name": "Organza Block-Printed Dupatta", "gender": "female", "style": "eastern", "category": "accessory", "fabric": "organza", "color": "gold/multicolor", "formality": "festive"},

    # --- WOMEN'S WESTERN ---
    {"item_id": "WW-01", "name": "Black Elegant Maxi Dress", "gender": "female", "style": "western", "category": "dress", "fabric": "polyester/satin", "color": "black", "formality": "formal/party"},
    {"item_id": "WW-02", "name": "Floral Summer Midi Dress", "gender": "female", "style": "western", "category": "dress", "fabric": "viscose", "color": "yellow/floral", "formality": "casual/picnic"},
    {"item_id": "WW-03", "name": "Classic White Button-Down Shirt", "gender": "female", "style": "western", "category": "top", "fabric": "cotton", "color": "white", "formality": "smart_casual/work"},
    {"item_id": "WW-04", "name": "High-Waisted Wide-Leg Denim Jeans", "gender": "female", "style": "western", "category": "bottom", "fabric": "denim", "color": "light blue", "formality": "casual"},
    {"item_id": "WW-05", "name": "Tailored Beige Blazer", "gender": "female", "style": "western", "category": "outerwear", "fabric": "linen blend", "color": "beige", "formality": "smart_casual/formal"},

    # --- MEN'S EASTERN ---
    {"item_id": "ME-01", "name": "Cotton Kurta Shalwar Set", "gender": "male", "style": "eastern", "category": "full_outfit", "fabric": "cotton", "color": "white", "formality": "casual/jumuah"},
    {"item_id": "ME-02", "name": "Raw Silk Black Kurta Pajama", "gender": "male", "style": "eastern", "category": "full_outfit", "fabric": "raw silk", "color": "black", "formality": "formal/evening"},
    {"item_id": "ME-03", "name": "Jamawar Embroidered Waistcoat", "gender": "male", "style": "eastern", "category": "outerwear", "fabric": "jamawar", "color": "maroon/gold", "formality": "festive/wedding"},
    {"item_id": "ME-04", "name": "Linen Cream Kurta", "gender": "male", "style": "eastern", "category": "top", "fabric": "linen", "color": "cream", "formality": "casual/picnic"},

    # --- MEN'S WESTERN ---
    {"item_id": "MW-01", "name": "Slim-Fit Charcoal 2-Piece Suit", "gender": "male", "style": "western", "category": "suit", "fabric": "wool blend", "color": "charcoal grey", "formality": "formal/business"},
    {"item_id": "MW-02", "name": "Black Crew-Neck Cotton T-Shirt", "gender": "male", "style": "western", "category": "top", "fabric": "cotton", "color": "black", "formality": "casual/outing"},
    {"item_id": "MW-03", "name": "Navy Blue Oxford Button-Down Shirt", "gender": "male", "style": "western", "category": "top", "fabric": "cotton", "color": "navy blue", "formality": "smart_casual"},
    {"item_id": "MW-04", "name": "Dark Wash Slim Denim Jeans", "gender": "male", "style": "western", "category": "bottom", "fabric": "denim", "color": "dark blue", "formality": "casual"},
    {"item_id": "MW-05", "name": "Chino Trousers", "gender": "male", "style": "western", "category": "bottom", "fabric": "cotton twill", "color": "khaki", "formality": "smart_casual"},
    {"item_id": "MW-06", "name": "Leather Biker Jacket", "gender": "male", "style": "western", "category": "outerwear", "fabric": "leather", "color": "black", "formality": "party/casual"},

    # --- FOOTWEAR & ACCESSORIES ---
    {"item_id": "ACC-01", "name": "Gold Embellished Khussa", "gender": "female", "style": "eastern", "category": "footwear", "fabric": "leather/silk", "color": "gold", "formality": "festive"},
    {"item_id": "ACC-02", "name": "Black Strap High Heels", "gender": "female", "style": "western", "category": "footwear", "fabric": "leather", "color": "black", "formality": "formal/party"},
    {"item_id": "ACC-03", "name": "White Canvas Sneakers", "gender": "unisex", "style": "western", "category": "footwear", "fabric": "canvas", "color": "white", "formality": "casual/picnic"},
    {"item_id": "ACC-04", "name": "Men's Leather Peshawari Chappal", "gender": "male", "style": "eastern", "category": "footwear", "fabric": "leather", "color": "tan brown", "formality": "festive/casual"},
    {"item_id": "ACC-05", "name": "Men's Black Oxford Formal Shoes", "gender": "male", "style": "western", "category": "footwear", "fabric": "leather", "color": "black", "formality": "formal"},
    {"item_id": "ACC-06", "name": "Kundan Jhumkas & Statement Ring", "gender": "female", "style": "eastern", "category": "jewelry", "fabric": "metal/pearl", "color": "gold/white", "formality": "festive"},
    {"item_id": "ACC-07", "name": "Classic Leather Wristwatch", "gender": "unisex", "style": "universal", "category": "accessory", "fabric": "leather/metal", "color": "brown/silver", "formality": "smart_casual/formal"}
]

def get_weather(text: str) -> str:
    t = text.lower()
    if "karachi" in t:
        return "Karachi weather: 32°C, warm and humid (78% humidity). Recommend light, breathable fabrics like cotton, lawn, or chiffon."
    elif "lahore" in t:
        return "Lahore weather: 28°C, pleasant breeze. Comfortable for most clothing."
    elif "islamabad" in t:
        return "Islamabad weather: 22°C, cool ambient temperature. Suitable for light layering."
    return "Ambient weather: ~30°C warm condition. Prioritize breathable fabric if outdoors."

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
                max-width: 760px;
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
            <p class="subtitle">Agentic Wardrobe & Event Stylist (Men & Women | Eastern & Western)</p>
            <form action="/recommend" method="post">
                <label>Tell me who you are styling for, the occasion, city, and your preferences:</label>
                <textarea name="user_query" placeholder="e.g. I am going on a casual picnic in Karachi, style me in something relaxed and comfortable for a female. OR I am a male going to a formal dinner in black.">I am going on a relaxed casual picnic in Karachi. Style a comfortable female outfit for me!</textarea>
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
    
    system_prompt = f"""You are VirtualCloset AI, an extremely intelligent, empathetic, and context-aware personal fashion stylist.

USER QUERY: "{user_query}"
WEATHER CONTEXT: "{weather_info}"
AVAILABLE CLOSET INVENTORY DATABASE:
{json.dumps(CLOSET_DATA, indent=2)}

STRICT STYLING INSTRUCTIONS:
1. Carefully analyze the user's intent: gender (male/female), occasion (picnic, wedding, formal dinner, casual walk, party), style (Eastern/Western), color preference, and weather appropriateness.
2. CRITICAL MATCHING: Do NOT give formal clothes or Anarkalis for casual picnics! Pick casual clothes (like floral midi dresses, cotton kurtis, jeans/t-shirts, sneakers) for picnics, and formal clothes (suits, velvet kurtis, anarkalis, heels) for formal events.
3. Select exact items from the AVAILABLE CLOSET INVENTORY DATABASE that fit the exact query and weather.
4. If the user asks for men's clothing, select strictly from men's items. If female, select female items.
5. Provide a personalized, conversational styling response formatted with:
   - 👔 / 👗 **Selected Outfit Ensemble** (Top/Outfit, Bottom, Footwear, Accessories)
   - ☀️ **Weather & Comfort Rationale** (Why this works for the location/temperature)
   - ✨ **3 Pro Styling & Makeup/Grooming Tips** tailored specifically to the occasion.

Respond directly in clean HTML with smooth paragraph breaks (`<br>`) and bold tags (`<b>`). Do NOT wrap response in markdown code blocks."""

    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional fashion agent."},
            {"role": "user", "content": system_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 800
    }
    
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            outfit_text = resp.json()["choices"][0]["message"]["content"].replace("\n", "<br>")
        else:
            outfit_text = f"<b>Styling Agent Update:</b> Could not connect to Groq API (Status {resp.status_code}). Please verify GROQ_API_KEY."
    except Exception as e:
        outfit_text = f"<b>Styling Agent Notice:</b> Connection timeout. Please try submitting your query again."

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
                max-width: 760px;
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
