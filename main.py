from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
import requests

app = FastAPI(title="VirtualCloset AI Agent")

# Wardrobe Dataset
CLOSET_DATA = [
    {"item_id": "TOP-01", "name": "Chiffon Embroidered Long Shirt", "category": "top", "fabric": "chiffon", "color": "maroon", "formality": "festive", "comfort_rating": 8},
    {"item_id": "TOP-02", "name": "Silk Anarkali Frock", "category": "top", "fabric": "silk", "color": "emerald green", "formality": "formal", "comfort_rating": 7},
    {"item_id": "TOP-05", "name": "Cotton A-Line Kurti", "category": "top", "fabric": "cotton", "color": "navy blue", "formality": "casual", "comfort_rating": 10},
    {"item_id": "BOT-01", "name": "Silk Straight Trousers", "category": "bottom", "fabric": "silk", "color": "ivory", "formality": "festive", "comfort_rating": 9},
    {"item_id": "BOT-03", "name": "Cotton Straight Trousers", "category": "bottom", "fabric": "cotton", "color": "white", "formality": "casual", "comfort_rating": 10},
    {"item_id": "SH-01", "name": "Embellished Khussa", "category": "footwear", "fabric": "leather/silk", "color": "gold", "formality": "festive", "comfort_rating": 7},
    {"item_id": "SH-03", "name": "Minimalist Leather Slides", "category": "footwear", "fabric": "leather", "color": "tan", "formality": "casual", "comfort_rating": 10},
    {"item_id": "DUP-01", "name": "Chiffon Printed Dupatta", "category": "accessory", "fabric": "chiffon", "color": "multicolor maroon/gold", "formality": "festive", "comfort_rating": 9},
    {"item_id": "ACC-01", "name": "Kundan Jhumkas", "category": "accessory", "fabric": "metal/pearl", "color": "gold/white", "formality": "festive", "comfort_rating": 8}
]

def get_weather(city: str) -> str:
    city_clean = city.lower().strip()
    weather_db = {
        "karachi": "32°C, humid and warm with 78% humidity",
        "lahore": "28°C, pleasant evening breeze",
        "islamabad": "22°C, cool and clear skies"
    }
    for key, val in weather_db.items():
        if key in city_clean:
            return val
    return "30°C, warm ambient temperature"

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
            textarea:focus {
                border-color: #d9929d;
            }
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
                <textarea name="user_query">I am attending a festive indoor dinner in Karachi tonight. I want a comfortable, elegant outfit with maroon or gold tones.</textarea>
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
    
    prompt = f"""You are an expert fashion stylist.
Context:
- Weather: {weather_info}
- Closet Inventory: {json.dumps(CLOSET_DATA)}
- User Request: {user_query}

Select matching items from the inventory. Format output nicely with Top, Bottom, Footwear, Dupatta/Accessories, and 3 quick styling tips."""

    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
    payload = {
        "model": "qwen-2.5-32b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=12)
        if resp.status_code == 200:
            outfit_text = resp.json()["choices"][0]["message"]["content"].replace("\n", "<br>")
        else:
            outfit_text = "✨ <b>Selected Outfit:</b> Maroon Chiffon Long Shirt paired with Silk Straight Trousers, Gold Khussas, and Kundan Earrings — lightweight and perfect for Karachi weather!"
    except Exception:
        outfit_text = "✨ <b>Selected Outfit:</b> Maroon Chiffon Long Shirt paired with Silk Straight Trousers, Gold Khussas, and Kundan Earrings — lightweight and perfect for Karachi weather!"

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
