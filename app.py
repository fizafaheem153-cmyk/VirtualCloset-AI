import streamlit as st
import json
import os
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain.agents import create_agent

# Page Config
st.set_page_config(page_title="VirtualCloset AI", page_icon="👗", layout="wide")

st.title("👗 VirtualCloset AI — Agentic Wardrobe & Stylist")
st.markdown("An AI personal wardrobe manager and occasion stylist that dynamically balances event formality, weather, and fabric comfort.")

# Load Wardrobe Dataset
@st.cache_data
def load_closet():
    return [
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

closet_items = load_closet()

# Tools
@tool
def get_closet_items(category: str = "", formality: str = "") -> list:
    """Searches the digital wardrobe inventory filtered by category or formality."""
    filtered = closet_items
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

# Sidebar
st.sidebar.header("🔑 API Configuration")
api_key = st.sidebar.text_input("Enter Groq API Key:", value=os.environ.get("GROQ_API_KEY", ""), type="password")
st.sidebar.header("👗 Wardrobe Quick Look")
st.sidebar.json(closet_items[:3])

# User Request Form
col1, col2 = st.columns([2, 1])

with col1:
    user_query = st.text_area(
        "Describe your occasion & preferences:",
        value="I am attending a festive indoor dinner in Karachi tonight. I want a comfortable, elegant outfit with maroon or gold tones."
    )
    submit_btn = st.button("✨ Assembled Outfit Card", type="primary")

if submit_btn:
    if not api_key:
        st.error("Please provide a valid Groq API Key.")
    else:
        os.environ["GROQ_API_KEY"] = api_key
        try:
            llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=500)
            
            system_prompt = """You are VirtualCloset AI, an expert personal wardrobe stylist.
            1. Call `get_weather_context` first if a city is mentioned.
            2. Call `get_closet_items` to retrieve wardrobe choices.
            3. Assemble a complete outfit (Top + Bottom + Footwear + Accessory).
            4. Provide a structured Markdown summary with styling rationale and weather fit."""
            
            agent = create_agent(llm, TOOLS, system_prompt=system_prompt)
            
            with st.spinner("Analyzing weather context and assembling wardrobe choices..."):
                result = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
                
            st.success("Outfit Assembled Successfully!")
            st.markdown(result["messages"][-1].content)
            
        except Exception as e:
            st.error(f"Error during agent invocation: {str(e)}")
