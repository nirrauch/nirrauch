#!/usr/bin/env python3
"""
Generate a self-contained HTML trip overview presentation.

Usage:
    python3 generate_html.py <trip_data.json> <output.html>

Schema for trip_data.json:
{
  "destination": "Tokyo, Japan",
  "dates": {"from": "2025-09-01", "to": "2025-09-10"},
  "travelers": ["Alice", "Bob"],
  "vibe": "cultural + foodie",
  "highlights": [
    {"title": "Tsukiji Outer Market", "description": "...", "estimated_cost": "$30/person"}
  ],
  "accommodation": [
    {"name": "Trunk Hotel", "neighborhood": "Shibuya", "dates": "Sep 1–5", "price_per_night": "$220", "link": "https://..."}
  ],
  "flights": [
    {"route": "NYC → Tokyo", "airline": "ANA", "departure": "Sep 1, 10:00am", "arrival": "Sep 2, 2:00pm", "price_per_person": "$850", "link": "https://..."}
  ],
  "itinerary": [
    {"day": "Day 1 – Sep 1", "morning": "...", "afternoon": "...", "evening": "..."}
  ],
  "budget_summary": {
    "Flights": "$1,700",
    "Accommodation": "$1,980",
    "Total": "$5,180"
  }
}
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def render_html(trip: dict) -> str:
    destination = trip.get("destination", "Our Trip")
    dates = trip.get("dates", {})
    date_range = f"{dates.get('from', '')} – {dates.get('to', '')}" if dates else ""
    travelers = ", ".join(trip.get("travelers", []))
    vibe = trip.get("vibe", "")

    highlights_html = ""
    for h in trip.get("highlights", []):
        highlights_html += f"""
        <div class="card">
          <div class="card-title">{h.get('title','')}</div>
          <div class="card-body">{h.get('description','')}</div>
          {"<div class='tag'>" + h.get('estimated_cost','') + "</div>" if h.get('estimated_cost') else ""}
        </div>"""

    accommodation_html = ""
    for a in trip.get("accommodation", []):
        link = a.get("link", "#")
        accommodation_html += f"""
        <div class="card">
          <div class="card-title"><a href="{link}" target="_blank">{a.get('name','')}</a></div>
          <div class="card-meta">{a.get('neighborhood','')} &middot; {a.get('dates','')}</div>
          <div class="card-body">{a.get('price_per_night','')} / night</div>
        </div>"""

    flights_html = ""
    for f in trip.get("flights", []):
        link = f.get("link", "#")
        flights_html += f"""
        <div class="card">
          <div class="card-title"><a href="{link}" target="_blank">{f.get('route','')}</a></div>
          <div class="card-meta">{f.get('airline','')} &middot; {f.get('departure','')} → {f.get('arrival','')}</div>
          <div class="card-body">{f.get('price_per_person','')} / person</div>
        </div>"""

    itinerary_html = ""
    for day in trip.get("itinerary", []):
        segments = ""
        for segment in ["morning", "afternoon", "evening"]:
            if day.get(segment):
                segments += f"<div class='segment'><span class='segment-label'>{segment.capitalize()}</span> {day[segment]}</div>"
        itinerary_html += f"""
        <div class="day-block">
          <div class="day-header">{day.get('day','')}</div>
          {segments}
        </div>"""

    budget_rows = ""
    budget = trip.get("budget_summary", {})
    for k, v in budget.items():
        row_class = "total-row" if k.lower() == "total" else ""
        budget_rows += f"<tr class='{row_class}'><td>{k}</td><td>{v}</td></tr>"

    generated = datetime.now().strftime("%B %d, %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{destination} Trip Overview</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f7f7f5; color: #222; line-height: 1.6; }}
  .hero {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 60px 40px 50px; text-align: center; }}
  .hero h1 {{ font-size: 2.8em; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 12px; }}
  .hero .meta {{ opacity: 0.8; font-size: 1.1em; margin-bottom: 8px; }}
  .hero .vibe {{ display: inline-block; margin-top: 16px; background: rgba(255,255,255,0.15); border-radius: 20px; padding: 4px 16px; font-size: 0.9em; }}
  .container {{ max-width: 860px; margin: 0 auto; padding: 40px 20px; }}
  h2 {{ font-size: 1.4em; font-weight: 700; margin-bottom: 20px; padding-bottom: 8px; border-bottom: 2px solid #e8e8e4; color: #1a1a2e; }}
  section {{ margin-bottom: 48px; }}
  .card {{ background: white; border-radius: 10px; padding: 20px 24px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.07); }}
  .card-title {{ font-weight: 600; font-size: 1.05em; margin-bottom: 4px; }}
  .card-title a {{ color: #0f3460; text-decoration: none; }}
  .card-title a:hover {{ text-decoration: underline; }}
  .card-meta {{ color: #777; font-size: 0.88em; margin-bottom: 6px; }}
  .card-body {{ color: #444; font-size: 0.95em; }}
  .tag {{ display: inline-block; margin-top: 10px; background: #f0f4ff; color: #0f3460; border-radius: 4px; padding: 2px 10px; font-size: 0.85em; }}
  .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }}
  .day-block {{ background: white; border-radius: 10px; padding: 20px 24px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.07); }}
  .day-header {{ font-weight: 700; font-size: 1em; color: #0f3460; margin-bottom: 12px; }}
  .segment {{ margin-bottom: 8px; font-size: 0.93em; color: #444; }}
  .segment-label {{ font-weight: 600; color: #888; text-transform: uppercase; font-size: 0.78em; letter-spacing: 0.5px; margin-right: 6px; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.07); }}
  th, td {{ padding: 13px 20px; text-align: left; border-bottom: 1px solid #f0f0ec; }}
  th {{ background: #f5f5f2; font-weight: 600; font-size: 0.9em; color: #555; }}
  td:last-child {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .total-row td {{ font-weight: 700; background: #f0f4ff; color: #0f3460; border-bottom: none; }}
  .footer {{ text-align: center; color: #aaa; font-size: 0.82em; padding: 30px 20px 50px; }}
  @media (max-width: 600px) {{
    .hero h1 {{ font-size: 2em; }}
    .hero {{ padding: 40px 20px 36px; }}
    .container {{ padding: 28px 14px; }}
  }}
</style>
</head>
<body>
<div class="hero">
  <h1>{destination}</h1>
  <div class="meta">{date_range}</div>
  <div class="meta">{travelers}</div>
  {"<div class='vibe'>" + vibe + "</div>" if vibe else ""}
</div>
<div class="container">
  {"<section><h2>Highlights</h2><div class='cards-grid'>" + highlights_html + "</div></section>" if highlights_html else ""}
  {"<section><h2>Where We're Staying</h2>" + accommodation_html + "</section>" if accommodation_html else ""}
  {"<section><h2>Flights</h2>" + flights_html + "</section>" if flights_html else ""}
  {"<section><h2>Day by Day</h2>" + itinerary_html + "</section>" if itinerary_html else ""}
  {"<section><h2>Budget Summary</h2><table><thead><tr><th>Category</th><th>Estimated Cost</th></tr></thead><tbody>" + budget_rows + "</tbody></table></section>" if budget_rows else ""}
</div>
<div class="footer">Generated {generated} · Travel Planner</div>
</body>
</html>"""


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_html.py <trip_data.json> <output.html>")
        sys.exit(1)
    data_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    with open(data_path) as f:
        trip = json.load(f)
    html = render_html(trip)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✓ HTML written to {output_path}")


if __name__ == "__main__":
    main()
