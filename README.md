# VirtualCloset AI

A weather-aware outfit stylist. You give it a plan, a city and a day, and it builds an outfit from your own closet using live weather. If something is missing, it links to where you can buy it.

**Live app:** https://virtual-closet-ai-ptkm.vercel.app

## How it works
1. The browser sends the plan, city, day and closet.
2. The app fetches the live forecast from Open-Meteo.
3. It builds one prompt (request + weather + closet) and asks a Groq model, with two backup models.
4. It validates the reply. Items not in the closet are dropped and counted.
5. If every model fails, a rule-based backup stylist answers.
6. It builds shopping links for missing items.

This is a fixed pipeline with one AI call, not a true agent.

## Stack
FastAPI, Groq, Open-Meteo, Vercel. The closet is synthetic (24 items).

## Limits
Photo upload and receipt reading from my Phase 1 plan are not built. Evaluation is small (13 test cases). See the notebook for scores and the honesty section.

*DATA722 Phase 2 project, Fiza Binte Faheem.*
