import json
import os
import re
import time
from urllib.parse import quote_plus

import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="VirtualCloset AI")

# Models are tried in order. Groq retires models often, so override with the
# GROQ_MODELS env var (comma separated) without touching code.
DEFAULT_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.6-27b", "openai/gpt-oss-20b"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

WMO = {0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 48: "fog",
       51: "light drizzle", 53: "drizzle", 55: "heavy drizzle", 61: "light rain", 63: "rain",
       65: "heavy rain", 71: "light snow", 73: "snow", 75: "heavy snow", 80: "rain showers",
       81: "rain showers", 82: "violent showers", 95: "thunderstorm", 96: "thunderstorm with hail",
       99: "thunderstorm with hail"}

DEFAULT_CLOSET = [
    {"id": "W-01", "name": "Chiffon Embroidered Long Shirt", "category": "top", "style": "eastern", "color": "maroon", "formality": "festive"},
    {"id": "W-02", "name": "Silk Anarkali Frock", "category": "dress", "style": "eastern", "color": "emerald green", "formality": "formal"},
    {"id": "W-03", "name": "Black Velvet Embroidered Kurti", "category": "top", "style": "eastern", "color": "black", "formality": "formal"},
    {"id": "W-04", "name": "Cotton A-Line Printed Kurti", "category": "top", "style": "eastern", "color": "navy blue", "formality": "casual"},
    {"id": "W-05", "name": "Lawn Printed Kurti", "category": "top", "style": "eastern", "color": "peach", "formality": "casual"},
    {"id": "W-06", "name": "Raw Silk Straight Trousers", "category": "bottom", "style": "eastern", "color": "ivory", "formality": "formal"},
    {"id": "W-07", "name": "Cotton Straight Pants", "category": "bottom", "style": "eastern", "color": "white", "formality": "casual"},
    {"id": "W-08", "name": "Floral Summer Midi Dress", "category": "dress", "style": "western", "color": "yellow floral", "formality": "casual"},
    {"id": "W-09", "name": "Black Satin Evening Maxi Dress", "category": "dress", "style": "western", "color": "black", "formality": "formal"},
    {"id": "W-10", "name": "White Linen Button-Down Shirt", "category": "top", "style": "western", "color": "white", "formality": "smart casual"},
    {"id": "W-11", "name": "High-Waisted Denim Jeans", "category": "bottom", "style": "western", "color": "blue", "formality": "casual"},
    {"id": "W-12", "name": "Warm Wool Trench Coat", "category": "outerwear", "style": "western", "color": "camel", "formality": "smart casual"},
    {"id": "A-01", "name": "Gold Embellished Khussa", "category": "footwear", "style": "eastern", "color": "gold", "formality": "festive"},
    {"id": "A-02", "name": "Black Strap High Heels", "category": "footwear", "style": "western", "color": "black", "formality": "formal"},
    {"id": "A-03", "name": "White Canvas Sneakers", "category": "footwear", "style": "western", "color": "white", "formality": "casual"},
    {"id": "A-04", "name": "Leather Walking Boots", "category": "footwear", "style": "western", "color": "brown", "formality": "casual"},
    {"id": "A-05", "name": "Kundan Jhumkas & Pearl Jewelry", "category": "accessory", "style": "eastern", "color": "gold", "formality": "festive"},
    {"id": "M-01", "name": "Black Silk Kurta Pajama", "category": "outfit", "style": "eastern", "color": "black", "formality": "formal"},
    {"id": "M-02", "name": "White Cotton Kurta Shalwar", "category": "outfit", "style": "eastern", "color": "white", "formality": "casual"},
    {"id": "M-03", "name": "Slim-Fit Charcoal Suit", "category": "outfit", "style": "western", "color": "charcoal", "formality": "formal"},
    {"id": "M-04", "name": "Cotton Crew-Neck T-Shirt", "category": "top", "style": "western", "color": "black", "formality": "casual"},
    {"id": "M-05", "name": "Puffer Winter Jacket", "category": "outerwear", "style": "western", "color": "navy", "formality": "casual"},
    {"id": "M-06", "name": "Navy Chino Trousers", "category": "bottom", "style": "western", "color": "navy", "formality": "smart casual"},
    {"id": "M-07", "name": "Black Leather Oxford Shoes", "category": "footwear", "style": "western", "color": "black", "formality": "formal"},
]
# Who each item is for, so the AI never has to guess from the item name.
for _i in DEFAULT_CLOSET:
    _i["gender"] = "male" if _i["id"].startswith("M-") else ("unisex" if _i["id"] in ("A-03", "A-04") else "female")


def get_weather(city: str, day: int):
    """Live weather from Open-Meteo (free, no API key). Returns dict or raises."""
    g = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                     params={"name": city, "count": 1}, timeout=10).json()
    if not g.get("results"):
        raise ValueError(f"Could not find city '{city}'")
    p = g["results"][0]
    f = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": p["latitude"], "longitude": p["longitude"], "timezone": "auto", "forecast_days": 7,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max",
    }, timeout=10).json()
    d, c = f["daily"], f["current"]
    day = max(0, min(day, len(d["time"]) - 1))
    w = {
        "city": f'{p["name"]}, {p.get("country", "")}'.strip(", "),
        "date": d["time"][day],
        "is_today": day == 0,
        "condition": WMO.get(d["weather_code"][day], "mixed conditions"),
        "temp_max": d["temperature_2m_max"][day],
        "temp_min": d["temperature_2m_min"][day],
        "rain_chance": d["precipitation_probability_max"][day],
        "uv": d["uv_index_max"][day],
    }
    if day == 0:
        w.update(now_temp=c["temperature_2m"], feels_like=c["apparent_temperature"],
                 humidity=c["relative_humidity_2m"], wind=c["wind_speed_10m"],
                 now_condition=WMO.get(c["weather_code"], "mixed conditions"))
    return w


def call_llm(prompt: str, max_tokens: int = 2500):
    """Returns (parsed_json, meta). meta has the model used, token counts and latency."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set in Vercel Environment Variables")
    models = [m.strip() for m in os.environ.get("GROQ_MODELS", "").split(",") if m.strip()] or DEFAULT_MODELS
    errors = []
    for model in models:
        for use_json_mode in (True, False):
            body = {"model": model, "temperature": 0.4, "max_completion_tokens": max_tokens,
                    "messages": [{"role": "system", "content": "You are an expert personal fashion stylist. Reply with JSON only."},
                                 {"role": "user", "content": prompt}]}
            if use_json_mode:
                body["response_format"] = {"type": "json_object"}
            t0 = time.time()
            try:
                r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=25)
            except Exception as e:
                errors.append(f"{model}: {e}")
                break
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"] or ""
                m = re.search(r"\{.*\}", text, re.S)
                if m:
                    try:
                        usage = r.json().get("usage") or {}
                        meta = {"model": model, "prompt_tokens": usage.get("prompt_tokens", 0),
                                "completion_tokens": usage.get("completion_tokens", 0),
                                "latency_ms": int((time.time() - t0) * 1000), "failed_attempts": len(errors)}
                        return json.loads(m.group(0)), meta
                    except Exception:
                        pass
                errors.append(f"{model}: unreadable reply")
                continue
            errors.append(f"{model}: HTTP {r.status_code} {r.text[:160]}")
            if r.status_code in (401, 403):
                raise RuntimeError("Groq rejected the API key. Create a new key and update GROQ_API_KEY in Vercel.")
    raise RuntimeError("All models failed: " + " | ".join(errors))


def shop_links(item: str):
    q = quote_plus(item)
    return [{"store": "Google Shopping", "url": f"https://www.google.com/search?tbm=shop&q={q}"},
            {"store": "Daraz", "url": f"https://www.daraz.pk/catalog/?q={q}"},
            {"store": "Amazon", "url": f"https://www.amazon.com/s?k={q}"},
            {"store": "ASOS", "url": f"https://www.asos.com/search/?q={q}"}]


def rule_based(closet, w, query):
    """Backup stylist so the demo never shows an error even if the AI is down."""
    hot = w["temp_max"] >= 30
    cold = w["temp_max"] <= 15
    wet = (w["rain_chance"] or 0) >= 50
    formal = any(k in query.lower() for k in ("wedding", "party", "dinner", "formal", "interview", "festive", "eid"))
    want = ("formal", "festive") if formal else ("casual", "smart casual")

    def pick(cat):
        c = [i for i in closet if i.get("category") == cat and i.get("formality") in want] or \
            [i for i in closet if i.get("category") == cat]
        return c[0]["id"] if c else None

    ids = [pick("outfit")] if (pick("outfit") and not pick("top")) else [pick("top"), pick("bottom")]
    ids += [pick("footwear")]
    if cold or wet:
        ids.append(pick("outerwear"))
    ids = [i for i in ids if i]
    missing = []
    if wet:
        missing.append({"item": "compact umbrella", "why": f"{w['rain_chance']}% chance of rain"})
    if hot or w["uv"] >= 6:
        missing.append({"item": "sunglasses", "why": "strong sun and UV today"})
    return {"summary": "Quick pick based on live weather and your closet.",
            "reasoning": f"It will be {w['condition']} with a high of {w['temp_max']}°C, so this outfit stays comfortable.",
            "item_ids": ids, "missing": missing,
            "tips": ["Check the weather again before leaving.", "Carry water if it is hot.", "Layer up if you will be outside late."]}


@app.get("/api/health")
def health():
    return {"groq_key_set": bool(os.environ.get("GROQ_API_KEY")),
            "models": os.environ.get("GROQ_MODELS") or DEFAULT_MODELS}


@app.get("/api/selftest")
def selftest():
    """Makes one tiny real AI call, to prove the key and models still work."""
    try:
        out, meta = call_llm('Reply with exactly this JSON: {"ok": true}', max_tokens=800)
        return {"ok": bool(out.get("ok")), **meta}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)[:400]}, status_code=503)


@app.post("/api/recommend")
def recommend(payload: dict):
    query = (payload.get("query") or "").strip()[:600] or "Style me an outfit for today"
    city = (payload.get("city") or "Karachi").strip()[:80]
    day = int(payload.get("day") or 0)
    gender = payload.get("gender") or "any"
    closet = payload.get("closet") or DEFAULT_CLOSET
    closet = [i for i in closet if isinstance(i, dict) and i.get("id") and i.get("name")][:150]

    try:
        w = get_weather(city, day)
    except Exception as e:
        return JSONResponse({"error": f"Weather lookup failed: {e}"}, status_code=400)

    prompt = f"""USER REQUEST: "{query}"
Wearer: {gender}
LIVE WEATHER (real forecast): {json.dumps(w)}
CLOSET (only these exist): {json.dumps(closet)}

Style one complete outfit using ONLY closet items (use their exact "id"). Consider the weather numbers, rain chance, UV, the occasion and dress code, and the wearer.
Only pick items whose "gender" matches the wearer or is "unisex".
Describe the weather strictly with the LIVE WEATHER fields above (condition, temperatures, rain_chance, uv). Never invent weather words: do not say "overcast", "humid" or "sunny" unless the data says so.
If something important is missing (umbrella, jacket, sunglasses, bag, shoes...), list it in "missing" so the user can buy it.
Return JSON exactly like:
{{"summary": "one friendly sentence", "reasoning": "2-3 sentences linking weather + occasion to the choices",
 "item_ids": ["id1","id2"], "missing": [{{"item": "search-friendly product name", "why": "short reason"}}],
 "tips": ["tip 1", "tip 2", "tip 3"]}}"""

    ai_used = True
    rule_meta = {"model": "rule-based", "prompt_tokens": 0, "completion_tokens": 0, "latency_ms": 0, "failed_attempts": None}
    try:
        out, meta = call_llm(prompt)
    except Exception as e:
        print("LLM failure:", e)
        out, ai_used, meta = rule_based(closet, w, query), False, rule_meta
        out["note"] = str(e)[:300]

    by_id = {i["id"]: i for i in closet}
    # item ids the AI returned that are NOT in the closet (hallucinated). Counted, then dropped.
    dropped = [i for i in out.get("item_ids", []) if i not in by_id]
    items = [by_id[i] for i in out.get("item_ids", []) if i in by_id]
    if not items:
        out = rule_based(closet, w, query)
        items = [by_id[i] for i in out["item_ids"] if i in by_id]
        ai_used, meta = False, rule_meta
    missing = [{**m, "links": shop_links(m.get("item", ""))} for m in out.get("missing", []) if m.get("item")][:4]
    return {"weather": w, "summary": out.get("summary", ""), "reasoning": out.get("reasoning", ""),
            "items": items, "missing": missing, "tips": out.get("tips", [])[:4],
            "ai_used": ai_used, "note": out.get("note"), "meta": meta, "dropped_ids": dropped}


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE.replace("__CLOSET__", json.dumps(DEFAULT_CLOSET))


PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VirtualCloset AI</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
<style>
:root{--bg1:#fde7ef;--bg2:#e9defa;--bg3:#dff3f0;--ink:#4a3e3d;--rose:#c97987;--deep:#8c535d}
*{box-sizing:border-box}
body{margin:0;font-family:Poppins,sans-serif;color:var(--ink);min-height:100vh;padding:28px 14px;
background:linear-gradient(135deg,var(--bg1),var(--bg2) 50%,var(--bg3)) fixed}
.wrap{max-width:820px;margin:0 auto}
.card{background:rgba(255,255,255,.88);border-radius:20px;padding:26px;margin-bottom:18px;box-shadow:0 10px 30px rgba(140,83,93,.15)}
h1{font-family:'Playfair Display',serif;color:var(--deep);text-align:center;margin:0 0 4px;font-size:34px}
.sub{text-align:center;color:#a37f86;font-style:italic;margin:0 0 6px}
h3{font-family:'Playfair Display',serif;color:var(--deep);margin:0 0 10px}
label{font-weight:600;font-size:13px;color:#734850}
input,select,textarea{width:100%;padding:11px 13px;border:1.5px solid #f3d5d8;border-radius:12px;font:inherit;background:#fff8fa;margin-top:5px}
textarea{height:90px}
.row{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:12px 0}
@media(max-width:600px){.row{grid-template-columns:1fr}}
button{background:linear-gradient(135deg,#e6a5af,#c97987);color:#fff;border:0;border-radius:12px;padding:14px;font:600 15px Poppins;cursor:pointer;width:100%}
button.small{width:auto;padding:8px 14px;font-size:13px}
button:disabled{opacity:.6}
.wx{display:flex;gap:18px;flex-wrap:wrap;align-items:center}
.temp{font:600 44px 'Playfair Display',serif;color:var(--deep)}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{background:#fcf0f2;border-left:4px solid #d9929d;border-radius:12px;padding:10px 14px;font-size:14px}
.chip small{display:block;color:#a37f86}
.links a{display:inline-block;margin:6px 8px 0 0;padding:6px 12px;border-radius:20px;background:#fff;border:1px solid #f0c9cf;color:var(--deep);text-decoration:none;font-size:13px}
.err{background:#fff1f1;border-left:4px solid #e57373;padding:12px;border-radius:10px}
.note{font-size:12px;color:#a37f86;margin-top:8px}
.closet-item{display:flex;justify-content:space-between;gap:8px;padding:6px 0;border-bottom:1px solid #f6e3e6;font-size:14px}
.closet-item span.x{cursor:pointer;color:#c97987}
.add{display:grid;grid-template-columns:2fr 1fr 1fr 1fr auto;gap:8px;margin-top:12px}
@media(max-width:700px){.add{grid-template-columns:1fr 1fr}}
</style></head><body><div class="wrap">
<div class="card"><h1>✨ VirtualCloset AI</h1><p class="sub">Your personal stylist, powered by live weather</p>
<label>What's the plan?</label>
<textarea id="q" placeholder="e.g. Attending class at University of Karachi, I want something comfortable">I'm attending a class at the university and want something comfortable.</textarea>
<div class="row">
<div><label>City (live weather)</label><input id="city" value="Karachi" placeholder="Karachi, London, Dubai..."></div>
<div><label>When?</label><select id="day"></select></div>
<div><label>Style for</label><select id="gender"><option value="female">Women</option><option value="male">Men</option><option value="any">Any</option></select></div>
</div>
<button id="go" onclick="go()">🌸 Style My Outfit</button></div>
<div id="out"></div>
<div class="card"><h3>👗 My Closet</h3><div id="closet"></div>
<div class="add"><input id="n" placeholder="Item name (e.g. Red wool scarf)"><select id="cat"><option>top</option><option>bottom</option><option>dress</option><option>outfit</option><option>outerwear</option><option>footwear</option><option>accessory</option></select>
<input id="col" placeholder="Color"><select id="sty"><option>eastern</option><option>western</option></select><button class="small" onclick="addItem()">Add</button></div>
<p class="note">Your closet is saved in this browser. <a href="#" onclick="resetCloset();return false">Reset to default</a></p></div>
</div>
<script>
const DEFAULT=__CLOSET__;
let closet=[];
try{closet=JSON.parse(localStorage.getItem('closet')||'null')||DEFAULT}catch(e){closet=DEFAULT}
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function save(){try{localStorage.setItem('closet',JSON.stringify(closet))}catch(e){}renderCloset()}
function renderCloset(){$('closet').innerHTML=closet.map((i,k)=>`<div class="closet-item"><div><b>${esc(i.name)}</b> <small>${esc(i.category)} · ${esc(i.color)} · ${esc(i.style)}</small></div><span class="x" onclick="del(${k})">✕</span></div>`).join('')}
function del(k){closet.splice(k,1);save()}
function addItem(){const n=$('n').value.trim();if(!n)return;closet.push({id:'U-'+Date.now(),name:n,category:$('cat').value,color:$('col').value||'-',style:$('sty').value,formality:'casual',gender:'unisex'});$('n').value='';$('col').value='';save()}
function resetCloset(){closet=DEFAULT.slice();save()}
const days=['Today','Tomorrow'];for(let i=0;i<7;i++){const d=new Date();d.setDate(d.getDate()+i);$('day').innerHTML+=`<option value="${i}">${i<2?days[i]+' — ':''}${d.toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'})}</option>`}
async function go(){
 const b=$('go');b.disabled=true;b.textContent='Checking live weather & styling…';$('out').innerHTML='';
 try{
  const r=await fetch('/api/recommend',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:$('q').value,city:$('city').value,day:+$('day').value,gender:$('gender').value,closet})});
  const d=await r.json();
  if(!r.ok){$('out').innerHTML=`<div class="card err">${esc(d.error||'Something went wrong')}</div>`;return}
  const w=d.weather;
  const now=w.is_today?`<div class="temp">${Math.round(w.now_temp)}°C</div><div>Feels like ${Math.round(w.feels_like)}°C · ${esc(w.now_condition)}<br>Humidity ${w.humidity}% · Wind ${w.wind} km/h</div>`:`<div class="temp">${Math.round(w.temp_max)}°C</div><div>${esc(w.condition)}</div>`;
  let h=`<div class="card"><h3>🌍 Live weather — ${esc(w.city)}</h3><div class="wx">${now}<div>Low ${Math.round(w.temp_min)}° / High ${Math.round(w.temp_max)}°<br>Rain chance ${w.rain_chance??0}% · UV ${w.uv}<br><small>${esc(w.date)}</small></div></div></div>`;
  h+=`<div class="card"><h3>👗 Your outfit</h3><p><b>${esc(d.summary)}</b></p><div class="chips">${d.items.map(i=>`<div class="chip">${esc(i.name)}<small>${esc(i.category)} · ${esc(i.color)}</small></div>`).join('')}</div><p>${esc(d.reasoning)}</p>`;
  if(d.tips.length)h+=`<h3 style="margin-top:14px">✨ Styling tips</h3><ul>${d.tips.map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`;
  h+=`</div>`;
  if(d.missing.length)h+=`<div class="card"><h3>🛍️ Missing from your closet</h3>${d.missing.map(m=>`<p><b>${esc(m.item)}</b> — ${esc(m.why)}<br><span class="links">${m.links.map(l=>`<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.store)}</a>`).join('')}</span></p>`).join('')}</div>`;
  if(!d.ai_used)h+=`<p class="note">AI stylist was unavailable, so a quick weather-based pick was used.</p>`;
  if(d.meta)h+=`<p class="note">Answered by ${esc(d.meta.model)} · ${(d.meta.prompt_tokens||0)+(d.meta.completion_tokens||0)} tokens · ${d.meta.latency_ms||0} ms</p>`;
  $('out').innerHTML=h;
 }catch(e){$('out').innerHTML=`<div class="card err">Network error: ${esc(e.message)}</div>`}
 finally{b.disabled=false;b.textContent='🌸 Style My Outfit'}
}
renderCloset();
</script></body></html>"""
