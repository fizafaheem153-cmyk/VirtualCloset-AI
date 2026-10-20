from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import os
import json
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent

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

@tool
def get_closet_items(category: str = "", formality: str = "") -> list:
    """Searches digital wardrobe inventory filtered by category or formality."""
    filtered = CLOSET_DATA
    if category:
        filtered = [i for i in filtered if i["category"].lower() == category.lower()]
    if formality:
        filtered = [i for i in filtered if i["formality"].lower() == formality.lower()]
    return filtered

@tool
def get_weather_context(city: str) -> dict:
    """Retrieves real-time weather details for outfit planning."""
    weather_db = {
        "karachi": {"temperature_c": 32, "humidity_pct": 78, "condition": "humid & warm"},
        "lahore": {"temperature_c": 28, "humidity_pct": 55, "condition": "pleasant"},
        "islamabad": {"temperature_c": 22, "humidity_pct": 40, "condition": "cool"}
    }
    return weather_db.get(city.lower(), {"temperature_c": 30, "humidity_pct": 65, "condition": "moderate"})

TOOLS = [get_closet_items, get_weather_context]

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VirtualCloset AI — Agentic Stylist</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; padding: 40px; margin: 0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; font-size: 26px; margin-bottom: 8px; }
            p { color: #7f8c8d; font-size: 14px; margin-bottom: 24px; }
            textarea { width: 100%; height: 100px; padding: 12px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
            button { background: #3498db; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 15px; cursor: pointer; margin-top: 15px; width: 100%; font-weight: bold; }
            button:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👗 VirtualCloset AI — Agentic Stylist</h1>
            <p>Built with FastAPI + HTML + LangChain for Vercel Deployment</p>
            <form action="/recommend" method="post">
                <label><strong>Describe your occasion & preferences:</strong></label><br><br>
                <textarea name="user_query">I am attending a festive indoor dinner in Karachi tonight. I want a comfortable, elegant outfit with maroon or gold tones.</textarea>
                <button type="submit">✨ Generate Outfit Recommendation</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/recommend", response_class=HTMLResponse)
def recommend(user_query: str = Form(...)):
    groq_key = os.environ.get("GROQ_API_KEY", "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")
    os.environ["GROQ_API_KEY"] = groq_key
    
    llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=500)
    system_prompt = """You are VirtualCloset AI, an expert personal wardrobe stylist.
    1. Call `get_weather_context` first if a city is mentioned.
    2. Call `get_closet_items` to retrieve choices.
    3. Assemble a complete matching outfit.
    4. Provide clear styling details."""
    
    agent = create_agent(llm, TOOLS, system_prompt=system_prompt)
    result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    outfit_text = result["messages"][-1].content.replace("\n", "<br>")
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Recommended Outfit Card</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f6f9; padding: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; }}
            a {{ display: inline-block; margin-top: 20px; color: #3498db; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>✨ Assembled Outfit Card</h2>
            <hr>
            <div>{outfit_text}</div>
            <a href="/">← Back to Stylist Input</a>
        </div>
    </body>
    </html>
    """
