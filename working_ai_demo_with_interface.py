#!/usr/bin/env python3
"""
🌍 Triplix WEB DEMO
Interactive web-based demonstration of AI agents.

To run:
1. Install dependencies: pip install "fastapi[all]" uvicorn python-dotenv
2. Run the server: python working_ai_demo_with_interface.py
3. Open your browser to http://127.0.0.1:8000
"""

import json
import os
from textwrap import dedent

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

# Load environment
load_dotenv()

# Import working agents
from discovery_agent import DiscoveryAgent
from itinerary_agent import ItineraryAgent
from group_agent import GroupAgent
from budget_agent import BudgetAgent
from memory_agent import MemoryAgent

def render_result_html(result: dict) -> str:
    """Renders a result dictionary into a user-friendly HTML format."""
    if not result:
        return "<pre>{}</pre>"

    # Handle errors first
    if "error" in result:
        return f"""
            <h4>An Error Occurred</h4>
            <p style="color: #c00;">{result['error']}</p>
            <hr>
            <h4>Raw JSON Response</h4>
            <pre>{json.dumps(result, indent=2, default=str)}</pre>
        """

    html = ""
    # Discovery Agent
    if "recommendations" in result and isinstance(result.get("recommendations"), list):
        html += "<h4>Recommendations</h4><ul>"
        for item in result["recommendations"]:
            html += f"""
                <li>
                    <strong>{item.get('name', 'N/A')}</strong> ({item.get('category', 'N/A')})
                    <p><em>Description:</em> {item.get('description', 'N/A')}</p>
                    <p><em>Reasoning:</em> {item.get('reasoning', 'N/A')}</p>
                </li>
            """
        html += "</ul>"

    # Itinerary Agent
    elif "itinerary" in result and isinstance(result.get("itinerary"), list):
        if result.get("travel_suggestions", {}).get("flights"):
             html += "<h4>Flight Suggestions</h4><ul>"
             for flight in result["travel_suggestions"]["flights"]:
                 html += f"<li>✈️ {flight.get('airline')} {flight.get('flight_number')}: {flight.get('departure_time')} -> {flight.get('arrival_time')} (Est: {flight.get('price_estimate')})</li>"
             html += "</ul>"

        html += "<h4>Itinerary</h4>"
        for day in result["itinerary"]:
            html += f"<h5>Day {day.get('day')}: {day.get('theme', '')}</h5><ul>"
            for event in day.get("schedule", []):
                html += f"<li><strong>{event.get('time')}: {event.get('activity')}</strong><br>{event.get('description')}</li>"
            html += "</ul>"

    # Group Agent
    elif "top_items" in result:
        html += f"<h4>Group Consensus (for {result.get('total_members', 'N/A')} members)</h4><ol>"
        for item in result["top_items"]:
            html += f"<li><strong>{item.get('name', 'N/A')}</strong> ({item.get('category', 'N/A')})<br>Likes: {item.get('likes', 0)}, Approval: {item.get('approval_score_percent', 0)}%</li>"
        html += "</ol>"

    # Budget Agent (Per Diem)
    elif "per_diem_estimate" in result:
        html += "<h4>Per-Diem Budget</h4><ul>"
        html += f"<li>Total Budget: {result.get('total_budget', 0):.2f}</li>"
        html += f"<li>Spent on Bookings: {result.get('spent_on_bookings', 0):.2f}</li>"
        html += f"<li>Remaining for Trip: {result.get('remaining_for_trip', 0):.2f}</li>"
        html += f"<li><strong>Per-Diem Estimate: {result.get('per_diem_estimate', 0):.2f} / day</strong></li>"
        html += "</ul>"

    # Budget Agent (Expense Split)
    elif "balances" in result and "transactions_to_settle" in result:
        html += "<h4>Expense Split Summary</h4>"
        if result.get("balances"):
            html += "<h5>Final Balances</h5><ul>"
            for user, balance in sorted(result["balances"].items()):
                if balance < 0:
                    html += f'<li style="color: #c00;">{user} owes {abs(balance):.2f}</li>'
                elif balance > 0:
                    html += f'<li style="color: #28a745;">{user} is owed {balance:.2f}</li>'
                else:
                    html += f'<li>{user} is settled</li>'
            html += "</ul>"
        if result.get("transactions_to_settle"):
            html += "<h5>How to Settle Up</h5><ul>"
            for txn in result["transactions_to_settle"]:
                html += f"<li><strong>{txn.get('from')}</strong> should pay <strong>{txn.get('to')}</strong> an amount of <strong>{txn.get('amount'):.2f}</strong></li>"
            html += "</ul>"

    # Memory Agent
    elif "memory_reel" in result and isinstance(result.get("memory_reel"), dict):
        reel = result["memory_reel"]
        html += f"<h4>Memory Reel: {reel.get('title', 'My Trip')}</h4>"
        html += f"<p><strong>Style:</strong> {reel.get('style', 'N/A')}</p>"
        html += f"<p><strong>Music:</strong> {reel.get('music_suggestion', 'N/A')}</p>"
        html += "<h5>Storyboard:</h5><ol>"
        for scene in reel.get("storyboard", []):
            html += f"""
                <li>
                    <strong>{scene.get('location')} ({scene.get('day')})</strong><br>
                    <img src="{scene.get('photo_id')}" alt="{scene.get('location')}" class="storyboard-img"><br>
                    <em>Caption:</em> "{scene.get('caption')}"
                </li>"""
        html += "</ol>"

    if not html:
        html = f"<pre>{json.dumps(result, indent=2, default=str)}</pre>"
    else:
        html += f"""
            <hr>
            <details>
                <summary>Show Raw JSON</summary>
                <pre>{json.dumps(result, indent=2, default=str)}</pre>
            </details>
        """
    return html

def render_page(title: str, description: str, form_html: str, result_html: str, next_url: str, next_text: str = "Next Agent Demo &rarr;"):
    """Renders a standard HTML page for an agent demo."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Triplix - {title}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 2em; background-color: #f4f4f9; color: #333; }}
            h1, h2 {{ color: #444; }}
            .container {{ display: flex; flex-wrap: wrap; gap: 2em; }}
            .form-section, .result-section {{ flex: 1; min-width: 300px; background: white; padding: 1.5em; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            textarea, input, select {{ width: 95%; padding: 10px; margin-bottom: 1em; border-radius: 4px; border: 1px solid #ddd; font-size: 0.9em; }}
            textarea {{ height: 120px; font-family: "SF Mono", "Consolas", "Menlo", monospace; }}
            button {{ background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 1em; }}
            button:hover {{ background-color: #0056b3; }}
            .nav-button {{ background-color: #28a745; margin-top: 1em; }}
            .nav-button:hover {{ background-color: #218838; }}
            pre {{ background-color: #eee; padding: 1em; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; }}
            label {{ font-weight: bold; display: block; margin-bottom: 5px; }}
            /* Result formatting */
            .result-section h4 {{ margin-top: 0; color: #007bff; }}
            .result-section h5 {{ margin-top: 1em; margin-bottom: 0.5em; color: #333; }}
            .result-section ul, .result-section ol {{ padding-left: 20px; }}
            .result-section li {{ margin-bottom: 1em; line-height: 1.4; }}
            .result-section p {{ margin: 0.2em 0; }}
            .tag {{ display: inline-block; background-color: #e0e0e0; color: #333; padding: 3px 8px; border-radius: 12px; font-size: 0.9em; margin-right: 5px; margin-bottom: 5px; }}
            .tag.disliked {{ background-color: #f8d7da; color: #721c24; }}
            details {{ margin-top: 1em; border: 1px solid #ddd; border-radius: 4px; padding: 0.5em; background-color: #f9f9f9; }}
            summary {{ cursor: pointer; font-weight: bold; color: #0056b3; }}
            .storyboard-img {{ max-width: 150px; max-height: 100px; border-radius: 4px; margin-top: 5px; border: 1px solid #ccc; }}
        </style>
    </head>
    <body>
        <h1>🤖 Triplix: {title}</h1>
        <p>{description}</p>
        <hr>
        <div class="container">
            <div class="form-section">
                <h2>Input</h2>
                <form method="post">{form_html}</form>
            </div>
            <div class="result-section"><h2>Result</h2>{result_html}</div>
        </div>
        <hr>
        <a href="{next_url}"><button class="nav-button">{next_text}</button></a>
    </body></html>"""
    return HTMLResponse(content=html_content)

class SimpleAITravelDemo:
    """Container for the initialized AI travel agents."""
    
    def __init__(self):
        """Initialize all agents"""
        print("🚀 Initializing Triplix AI Agents...")
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️  Warning: GEMINI_API_KEY not found. Some agents may not work.")

        # Initialize all agents
        self.discovery_agent = DiscoveryAgent(api_key) if api_key else None
        self.itinerary_agent = ItineraryAgent(api_key) if api_key else None
        self.group_agent = GroupAgent()
        self.budget_agent = BudgetAgent()
        self.memory_agent = MemoryAgent(api_key) if api_key else None

        print("✅ All agents initialized successfully!")


app = FastAPI(title="Triplix Agents Demo")
demo = SimpleAITravelDemo()

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/discovery")

@app.get("/discovery", response_class=HTMLResponse)
async def discovery_page(request: Request):
    form_html = dedent("""
        <h4>User Profile</h4>
        <label for="travel_mode">Travel Mode</label>
        <select name="travel_mode"><option>Pleasure</option><option>Business</option><option>Family</option></select>
        <label for="budget">Budget</label>
        <input type="text" name="budget" value="INR 50,000-100,000">
        <label for="scope">Scope / Destination Area</label>
        <input type="text" name="scope" value="Goa, India">
        <label for="group_size">Group Size</label>
        <input type="number" name="group_size" value="2">

        <h4>User Preferences (Swipes)</h4>
        <label for="liked_swipes">Liked Items (one per line, format: Name,Category)</label>
        <textarea name="liked_swipes">{liked_swipes}</textarea>
        <label for="disliked_swipes">Disliked Items (one per line, format: Name,Category)</label>
        <textarea name="disliked_swipes">{disliked_swipes}</textarea>

        <h4>Real-time Context</h4>
        <label for="weather">Weather</label>
        <input type="text" name="weather" value="sunny">
        <label for="season">Season</label>
        <input type="text" name="season" value="winter">
        <label for="local_events">Local Events</label>
        <input type="text" name="local_events" value="Sunburn Festival">
        <label for="current_location">Current Location</label>
        <input type="text" name="current_location" value="Goa">

        <label for="count">Count</label>
        <input type="number" name="count" value="3">
        <button type="submit">Agent response</button>
    """).format(
        liked_swipes="North Goa Beaches,destination\nScuba Diving,activity",
        disliked_swipes="Crowded markets,activity"
    )
    return render_page("Discovery Agent", "AI-powered personalized recommendations", form_html, render_result_html({}), "/itinerary")

@app.post("/discovery", response_class=HTMLResponse)
async def discovery_run(
    travel_mode: str = Form(), budget: str = Form(), scope: str = Form(), group_size: int = Form(),
    liked_swipes: str = Form(), disliked_swipes: str = Form(),
    weather: str = Form(), season: str = Form(), local_events: str = Form(), current_location: str = Form(),
    count: int = Form()
):
    result = {}
    form_html = dedent("""
        <h4>User Profile</h4>
        <label for="travel_mode">Travel Mode</label>
        <select name="travel_mode"><option selected>{travel_mode}</option><option>Pleasure</option><option>Business</option><option>Family</option></select>
        <label for="budget">Budget</label>
        <input type="text" name="budget" value="{budget}">
        <label for="scope">Scope / Destination Area</label>
        <input type="text" name="scope" value="{scope}">
        <label for="group_size">Group Size</label>
        <input type="number" name="group_size" value="{group_size}">

        <h4>User Preferences (Swipes)</h4>
        <label for="liked_swipes">Liked Items (one per line, format: Name,Category)</label>
        <textarea name="liked_swipes">{liked_swipes}</textarea>
        <label for="disliked_swipes">Disliked Items (one per line, format: Name,Category)</label>
        <textarea name="disliked_swipes">{disliked_swipes}</textarea>

        <h4>Real-time Context</h4>
        <label for="weather">Weather</label>
        <input type="text" name="weather" value="{weather}">
        <label for="season">Season</label>
        <input type="text" name="season" value="{season}">
        <label for="local_events">Local Events</label>
        <input type="text" name="local_events" value="{local_events}">
        <label for="current_location">Current Location</label>
        <input type="text" name="current_location" value="{current_location}">

        <label for="count">Count</label>
        <input type="number" name="count" value="{count}">
        <button type="submit">Agent response</button>
    """).format(
        travel_mode=travel_mode, budget=budget, scope=scope, group_size=group_size,
        liked_swipes=liked_swipes, disliked_swipes=disliked_swipes,
        weather=weather, season=season, local_events=local_events, current_location=current_location,
        count=count
    )
    
    try:
        # Reconstruct inputs for the agent
        user_profile = {"travel_mode": travel_mode, "budget": budget, "scope": scope, "group_size": group_size}
        context = {"weather": weather, "season": season, "local_events": local_events, "current_location": current_location}
        
        swipes = []
        for line in liked_swipes.strip().splitlines():
            if ',' in line:
                name, category = line.split(',', 1)
                swipes.append({"name": name.strip(), "liked": True, "category": category.strip()})
        for line in disliked_swipes.strip().splitlines():
            if ',' in line:
                name, category = line.split(',', 1)
                swipes.append({"name": name.strip(), "liked": False, "category": category.strip()})

        if demo.discovery_agent:
            result = demo.discovery_agent.execute(user_profile, swipes, context, count)
        else:
            result = {"error": "Discovery Agent not initialized (GEMINI_API_KEY missing)."}
    except Exception as e:
        result = {"error": str(e)}
    result_html = render_result_html(result)
    return render_page("Discovery Agent", "AI-powered personalized recommendations", form_html, result_html, "/itinerary")

@app.get("/itinerary", response_class=HTMLResponse)
async def itinerary_page(request: Request):
    form_html = dedent("""
        <label for="liked_items">Liked Items (one per line, format: Name,Category,Location)</label>
        <textarea name="liked_items">{liked_items}</textarea>
        <label for="duration_days">Trip Duration (Days)</label>
        <input type="number" name="duration_days" value="3">
        <label for="travel_pace">Travel Pace</label>
        <select name="travel_pace"><option>Moderate</option><option>Relaxed</option><option>Packed</option></select>
        <label for="origin_location">Origin Location</label>
        <input type="text" name="origin_location" value="Bangalore">
        <label for="base_location">Destination (Base Location)</label>
        <input type="text" name="base_location" value="Panjim, Goa">
        <button type="submit">Agent response</button>
    """).format(liked_items="Baga Beach,destination,Goa\nDudhsagar Falls,activity,Goa\nFort Aguada,destination,Goa")
    return render_page("Itinerary Agent", "AI-powered travel planning", form_html, render_result_html({}), "/group")

@app.post("/itinerary", response_class=HTMLResponse)
async def itinerary_run(liked_items: str = Form(), duration_days: int = Form(), travel_pace: str = Form(), base_location: str = Form(), origin_location: str = Form()):
    result = {}
    form_html = dedent("""
        <label for="liked_items">Liked Items (one per line, format: Name,Category,Location)</label>
        <textarea name="liked_items">{liked_items}</textarea>
        <label for="duration_days">Trip Duration (Days)</label>
        <input type="number" name="duration_days" value="{duration_days}">
        <label for="travel_pace">Travel Pace</label>
        <select name="travel_pace"><option selected>{travel_pace}</option><option>Relaxed</option><option>Moderate</option><option>Packed</option></select>
        <label for="origin_location">Origin Location</label>
        <input type="text" name="origin_location" value="{origin_location}">
        <label for="base_location">Destination (Base Location)</label>
        <input type="text" name="base_location" value="{base_location}">
        <button type="submit">Agent response</button>
    """).format(liked_items=liked_items, duration_days=duration_days, travel_pace=travel_pace, base_location=base_location, origin_location=origin_location)

    try:
        parsed_liked_items = []
        for line in liked_items.strip().splitlines():
            if line.count(',') >= 2:
                name, category, location = line.split(',', 2)
                parsed_liked_items.append({"name": name.strip(), "category": category.strip(), "location": location.strip()})

        if demo.itinerary_agent:
            result = demo.itinerary_agent.execute(parsed_liked_items, duration_days, travel_pace, base_location, origin_location)
        else:
            result = {"error": "Itinerary Agent not initialized (GEMINI_API_KEY missing)."}
    except Exception as e:
        result = {"error": str(e)}
    result_html = render_result_html(result)
    return render_page("Itinerary Agent", "AI-powered travel planning", form_html, result_html, "/group")

@app.get("/group", response_class=HTMLResponse)
async def group_page(request: Request):
    form_html = dedent("""
        <label for="group_id">Group ID</label>
        <input type="number" name="group_id" value="1">
        <label for="member_1_swipes">Member 1 Likes (one per line, format: ItemID,Name,Category)</label>
        <textarea name="member_1_swipes">{member_1_swipes}</textarea>
        <label for="member_2_swipes">Member 2 Likes (one per line, format: ItemID,Name,Category)</label>
        <textarea name="member_2_swipes">{member_2_swipes}</textarea>
        <button type="submit">Agent response</button>
    """).format(
        member_1_swipes="101,Baga Beach,destination\n201,Scuba Diving,activity",
        member_2_swipes="101,Baga Beach,destination\n102,Palolem Beach,destination\n301,Beachside Shack,accommodation"
    )
    return render_page("Group Agent", "Group preference consensus", form_html, render_result_html({}), "/budget")

@app.post("/group", response_class=HTMLResponse)
async def group_run(group_id: int = Form(), member_1_swipes: str = Form(), member_2_swipes: str = Form()):
    result = {}
    form_html = dedent("""
        <label for="group_id">Group ID</label>
        <input type="number" name="group_id" value="{group_id}">
        <label for="member_1_swipes">Member 1 Likes (one per line, format: ItemID,Name,Category)</label>
        <textarea name="member_1_swipes">{member_1_swipes}</textarea>
        <label for="member_2_swipes">Member 2 Likes (one per line, format: ItemID,Name,Category)</label>
        <textarea name="member_2_swipes">{member_2_swipes}</textarea>
        <button type="submit">Agent response</button>
    """).format(group_id=group_id, member_1_swipes=member_1_swipes, member_2_swipes=member_2_swipes)
    try:
        swipes_data = {1: [], 2: []}
        for line in member_1_swipes.strip().splitlines():
            if line.count(',') >= 2:
                item_id, name, category = line.split(',', 2)
                swipes_data[1].append({'item_id': int(item_id.strip()), 'name': name.strip(), 'category': category.strip(), 'liked': True})
        
        for line in member_2_swipes.strip().splitlines():
            if line.count(',') >= 2:
                item_id, name, category = line.split(',', 2)
                swipes_data[2].append({'item_id': int(item_id.strip()), 'name': name.strip(), 'category': category.strip(), 'liked': True})

        result = demo.group_agent.execute(group_id, swipes_data)
    except Exception as e:
        result = {"error": str(e)}
    result_html = render_result_html(result)
    return render_page("Group Agent", "Group preference consensus", form_html, result_html, "/budget")

@app.get("/budget", response_class=HTMLResponse)
async def budget_page(request: Request):
    form_html = dedent("""
        <h3>Per-Diem Calculation</h3>
        <label for="total_budget">Total Budget</label>
        <input type="number" name="total_budget" value="50000">
        <label for="pre_booked_costs">Pre-Booked Costs (one per line, format: Item Name,Amount)</label>
        <textarea name="pre_booked_costs">{pre_booked_costs}</textarea>
        <label for="duration_days">Duration (Days)</label>
        <input type="number" name="duration_days" value="4">
        <button type="submit" name="task" value="calculate_per_diem">Calculate Per-Diem</button>
        <hr>
        <h3>Expense Split</h3>
        <label for="expenses">Expenses (one per line, format: Amount,Payer,Participants comma-separated)</label>
        <textarea name="expenses">{expenses}</textarea>
        <button type="submit" name="task" value="get_split_summary">Calculate Expense Split</button>
    """).format(
        pre_booked_costs="Flights to Goa,15000\nHotel in Calangute,22000",
        expenses="2000,Alice,Alice,Bob\n1500,Bob,Alice,Bob"
    )
    return render_page("Budget Agent", "Smart budget calculations", form_html, render_result_html({}), "/memory")

@app.post("/budget", response_class=HTMLResponse)
async def budget_run(request: Request, task: str = Form(), total_budget: float = Form(0), pre_booked_costs: str = Form("[]"), duration_days: int = Form(0), expenses: str = Form("[]")):
    result = {}

    form_html = dedent("""
        <h3>Per-Diem Calculation</h3>
        <label for="total_budget">Total Budget</label>
        <input type="number" name="total_budget" value="{total_budget}">
        <label for="pre_booked_costs">Pre-Booked Costs (one per line, format: Item Name,Amount)</label>
        <textarea name="pre_booked_costs">{pre_booked_costs}</textarea>
        <label for="duration_days">Duration (Days)</label>
        <input type="number" name="duration_days" value="{duration_days}">
        <button type="submit" name="task" value="calculate_per_diem">Calculate Per-Diem</button>
        <hr>
        <h3>Expense Split</h3>
        <label for="expenses">Expenses (one per line, format: Amount,Payer,Participants comma-separated)</label>
        <textarea name="expenses">{expenses}</textarea>
        <button type="submit" name="task" value="get_split_summary">Calculate Expense Split</button>
    """).format(total_budget=total_budget, pre_booked_costs=pre_booked_costs, duration_days=duration_days, expenses=expenses)

    try:
        if task == "calculate_per_diem":
            parsed_costs = []
            for line in pre_booked_costs.strip().splitlines():
                if ',' in line:
                    name, amount = line.rsplit(',', 1)
                    try:
                        parsed_costs.append({'name': name.strip(), 'amount': float(amount.strip())})
                    except ValueError:
                        continue # ignore malformed lines
            result = demo.budget_agent.execute(task="calculate_per_diem", total_budget=total_budget, pre_booked_costs=parsed_costs, duration_days=duration_days)
        else:
            parsed_expenses = []
            for line in expenses.strip().splitlines():
                if line.count(',') >= 2:
                    parts = line.split(',')
                    try:
                        amount = float(parts[0].strip())
                        payer = parts[1].strip()
                        participants = [p.strip() for p in parts[2:]]
                        parsed_expenses.append({'amount': amount, 'payer_id': payer, 'participants': participants})
                    except (ValueError, IndexError):
                        continue # ignore malformed lines
            result = demo.budget_agent.execute(task="get_split_summary", expenses=parsed_expenses)
    except Exception as e:
        result = {"error": str(e)}
    result_html = render_result_html(result)
    return render_page("Budget Agent", "Smart budget calculations", form_html, result_html, "/memory")

@app.get("/memory", response_class=HTMLResponse)
async def memory_page(request: Request):
    form_html = dedent("""
        <label for="itinerary">Itinerary (one per line, format: Day X: Activity 1, Activity 2, ...)</label>
        <textarea name="itinerary">{itinerary}</textarea>
        <label for="photo_metadata">Photo Metadata (JSON)</label><p style="font-size: 0.8em; color: #666;">This field is kept as JSON to demonstrate the agent's ability to process rich, structured data like photo quality scores and tags, which is crucial for selecting the best images.</p>
        <textarea name="photo_metadata">{photo_metadata}</textarea>
        <label for="reel_style">Reel Style</label>
        <input type="text" name="reel_style" value="Upbeat and Fun">
        <button type="submit">Agent response</button>
    """).format(
        itinerary="Day 1: Relax at Calangute Beach, Explore Fort Aguada\nDay 2: Visit Dudhsagar Falls, Explore Old Goa Churches\nDay 3: Shopping at Anjuna Flea Market",
        photo_metadata=json.dumps([
            {"photo_id": "https://images.pexels.com/photos/1078983/pexels-photo-1078983.jpeg", "location": "Calangute Beach", "description": "Golden hour sunset over the ocean with waves washing ashore.", "quality_score": 0.92, "tags": ["beach", "sunset", "ocean"]},
            {"photo_id": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Dudhsagar_Falls_in_Goa.jpg/800px-Dudhsagar_Falls_in_Goa.jpg", "location": "Dudhsagar Falls", "description": "Majestic multi-tiered waterfall cascading through lush green forest.", "quality_score": 0.88, "tags": ["waterfall", "nature", "forest"]},
            {"photo_id": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Aguada_Fort_Goa.jpg/1024px-Aguada_Fort_Goa.jpg", "location": "Fort Aguada", "description": "Historic Portuguese fort overlooking the sea with a lighthouse.", "quality_score": 0.85, "tags": ["fort", "history", "sea"]},
            {"photo_id": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Basilica_of_Bom_Jesus_in_2023.jpg/1024px-Basilica_of_Bom_Jesus_in_2023.jpg", "location": "Old Goa", "description": "Baroque architecture of the Basilica of Bom Jesus, a UNESCO World Heritage site.", "quality_score": 0.9, "tags": ["church", "history", "architecture"]},
            {"photo_id": "https://images.pexels.com/photos/161039/market-stall-bazaar-vendor-161039.jpeg", "location": "Anjuna Flea Market", "description": "Colorful stalls and bustling crowd at a local market.", "quality_score": 0.82, "tags": ["market", "shopping", "culture"]}
        ], indent=2)
    )
    return render_page("Memory Agent", "AI-powered memory reel creation", form_html, render_result_html({}), "/discovery", "Back to Start &rarr;")

@app.post("/memory", response_class=HTMLResponse)
async def memory_run(itinerary: str = Form(), photo_metadata: str = Form(), reel_style: str = Form()):
    result = {}
    form_html = dedent("""
        <label for="itinerary">Itinerary (one per line, format: Day X: Activity 1, Activity 2, ...)</label>
        <textarea name="itinerary">{itinerary}</textarea>
        <label for="photo_metadata">Photo Metadata (JSON)</label><p style="font-size: 0.8em; color: #666;">This field is kept as JSON to demonstrate the agent's ability to process rich, structured data like photo quality scores and tags, which is crucial for selecting the best images.</p>
        <textarea name="photo_metadata">{photo_metadata}</textarea>
        <label for="reel_style">Reel Style</label>
        <input type="text" name="reel_style" value="{reel_style}">
        <button type="submit">Agent response</button>
    """).format(itinerary=itinerary, photo_metadata=photo_metadata, reel_style=reel_style)
    try:
        parsed_itinerary = {}
        for line in itinerary.strip().splitlines():
            if ':' in line:
                day_part, activities_part = line.split(':', 1)
                day_key = day_part.strip()
                activities = [act.strip() for act in activities_part.split(',')]
                parsed_itinerary[day_key] = activities

        if demo.memory_agent:
            result = demo.memory_agent.execute(parsed_itinerary, json.loads(photo_metadata), reel_style)
        else:
            result = {"error": "Memory Agent not initialized (GEMINI_API_KEY missing)."}
    except Exception as e:
        result = {"error": str(e)}
    result_html = render_result_html(result)
    return render_page("Memory Agent", "AI-powered memory reel creation", form_html, result_html, "/discovery", "Back to Start &rarr;")

def main():
    """Main web server execution"""
    print("Starting Triplix Web Demo...")
    print("Access at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()