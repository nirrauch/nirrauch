#!/usr/bin/env python3
"""
Generate a rich, interactive HTML trip overview presentation.

Usage:
    python3 generate_html.py <trip_data.json> <output.html>

See SKILL.md for the full trip_data.json schema.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import quote


def img_url(query: str, w: int = 800, h: int = 500) -> str:
    """Return a Picsum-based placeholder; swap for real image URLs in production."""
    # Use a deterministic seed from the query so the same activity always gets the same image
    seed = abs(hash(query)) % 1000
    return f"https://picsum.photos/seed/{seed}/{w}/{h}"


def render_html(trip: dict) -> str:
    destination = trip.get("destination", "Our Trip")
    dates = trip.get("dates", {})
    date_range = f"{dates.get('from', '')} – {dates.get('to', '')}" if dates else ""
    travelers = ", ".join(trip.get("travelers", []))
    vibe = trip.get("vibe", "")

    # --- Highlights ---
    highlights_html = ""
    for h in trip.get("highlights", []):
        img = img_url(h.get("image_query", h.get("title", destination)))
        cost = f"<div class='tag'>{h['estimated_cost']}</div>" if h.get("estimated_cost") else ""
        highlights_html += f"""
        <div class="highlight-card">
          <div class="highlight-img" style="background-image:url('{img}')"></div>
          <div class="highlight-body">
            <div class="highlight-title">{h.get('title','')}</div>
            <div class="highlight-desc">{h.get('description','')}</div>
            {cost}
          </div>
        </div>"""

    # --- Accommodation ---
    accommodation_html = ""
    for a in trip.get("accommodation", []):
        link = a.get("link", "#")
        desc = f"<div class='card-desc'>{a['description']}</div>" if a.get("description") else ""
        accommodation_html += f"""
        <div class="card">
          <div class="card-title"><a href="{link}" target="_blank">{a.get('name','')}</a></div>
          <div class="card-meta">{a.get('neighborhood','')} &middot; {a.get('dates','')}</div>
          <div class="card-body">{a.get('price_per_night','')} / night</div>
          {desc}
        </div>"""

    # --- Flights ---
    flights_html = ""
    for f in trip.get("flights", []):
        link = f.get("link", "#")
        flights_html += f"""
        <div class="card flight-card">
          <div class="flight-route">
            <span class="flight-city">{f.get('route','').split('→')[0].strip() if '→' in f.get('route','') else f.get('route','')}</span>
            <span class="flight-arrow">✈</span>
            <span class="flight-city">{f.get('route','').split('→')[1].strip() if '→' in f.get('route','') else ''}</span>
          </div>
          <div class="card-meta">{f.get('airline','')} &middot; {f.get('departure','')} → {f.get('arrival','')}</div>
          <div class="card-body"><a href="{link}" target="_blank">{f.get('price_per_person','')} / person</a></div>
        </div>"""

    # --- Itinerary (accordion) ---
    itinerary_html = ""
    for i, day in enumerate(trip.get("itinerary", [])):
        open_attr = "open" if i == 0 else ""
        theme = f"<span class='day-theme'>{day['day_theme']}</span>" if day.get("day_theme") else ""
        cost = f"<span class='day-cost'>{day['day_cost']}</span>" if day.get("day_cost") else ""
        segments = ""
        for segment in ["morning", "afternoon", "evening"]:
            if day.get(segment):
                icon = {"morning": "☀️", "afternoon": "🌤", "evening": "🌙"}.get(segment, "")
                segments += f"""
                <div class="segment">
                  <div class="segment-label">{icon} {segment.capitalize()}</div>
                  <div class="segment-text">{day[segment]}</div>
                </div>"""
        itinerary_html += f"""
        <details class="day-block" {open_attr}>
          <summary class="day-summary">
            <div class="day-summary-left">
              <span class="day-number">Day {i+1}</span>
              <span class="day-date">{day.get('day','').split('–')[-1].strip() if '–' in day.get('day','') else day.get('day','')}</span>
              {theme}
            </div>
            <div class="day-summary-right">{cost}</div>
          </summary>
          <div class="day-content">{segments}</div>
        </details>"""

    # --- Budget ---
    budget_rows = ""
    budget = trip.get("budget_summary", {})
    for k, v in budget.items():
        is_total = k.lower() == "total"
        is_headroom = "headroom" in k.lower()
        row_class = "total-row" if is_total else ("headroom-row" if is_headroom else "")
        budget_rows += f"<tr class='{row_class}'><td>{k}</td><td>{v}</td></tr>"

    # --- Bonus Activities ---
    bonus_html = ""
    for b in trip.get("bonus_activities", []):
        link = b.get("link", "#")
        cost = f"<div class='tag'>{b['estimated_cost']}</div>" if b.get("estimated_cost") else ""
        bonus_html += f"""
        <div class="bonus-card">
          <div class="bonus-title"><a href="{link}" target="_blank">{b.get('title','')}</a></div>
          <div class="bonus-desc">{b.get('description','')}</div>
          {cost}
        </div>"""

    generated = datetime.now().strftime("%B %d, %Y")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{destination} · Trip Overview</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --navy: #0f2a4a;
    --blue: #1a5276;
    --accent: #e8a020;
    --light: #f8f7f4;
    --card-bg: #ffffff;
    --text: #1a1a1a;
    --muted: #6b7280;
    --border: #e5e7eb;
  }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--light); color: var(--text); line-height: 1.65; }}

  /* Hero */
  .hero {{
    position: relative; min-height: 420px; display: flex; align-items: flex-end;
    background: linear-gradient(160deg, var(--navy) 0%, #1b4f72 60%, #2471a3 100%);
    overflow: hidden; padding: 0;
  }}
  .hero-bg {{
    position: absolute; inset: 0;
    background-image: url('{img_url(destination, 1400, 500)}');
    background-size: cover; background-position: center;
    opacity: 0.25; mix-blend-mode: luminosity;
  }}
  .hero-content {{ position: relative; padding: 56px 48px; width: 100%; }}
  .hero h1 {{ font-size: clamp(2rem, 5vw, 3.6rem); font-weight: 800; color: #fff; letter-spacing: -1px; line-height: 1.1; margin-bottom: 12px; }}
  .hero-meta {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 16px; }}
  .hero-pill {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.15); backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.2); border-radius: 100px;
    padding: 6px 16px; font-size: 0.88em; color: #fff;
  }}
  .hero-pill.accent {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }}

  /* Nav */
  .nav {{
    position: sticky; top: 0; z-index: 100;
    background: var(--navy); border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex; gap: 0; overflow-x: auto;
  }}
  .nav a {{
    color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.85em; font-weight: 500;
    padding: 14px 20px; white-space: nowrap; transition: color 0.15s, border-color 0.15s;
    border-bottom: 2px solid transparent;
  }}
  .nav a:hover {{ color: #fff; border-bottom-color: var(--accent); }}

  /* Layout */
  .container {{ max-width: 900px; margin: 0 auto; padding: 48px 24px; }}
  section {{ margin-bottom: 56px; scroll-margin-top: 60px; }}
  h2 {{
    font-size: 1.3em; font-weight: 700; color: var(--navy);
    margin-bottom: 24px; padding-bottom: 10px;
    border-bottom: 2px solid var(--accent); display: inline-block;
  }}

  /* Cards */
  .card {{
    background: var(--card-bg); border-radius: 12px; padding: 22px 26px;
    margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04);
    border: 1px solid var(--border);
  }}
  .card-title {{ font-weight: 700; font-size: 1.05em; margin-bottom: 4px; }}
  .card-title a {{ color: var(--navy); text-decoration: none; }}
  .card-title a:hover {{ text-decoration: underline; color: var(--blue); }}
  .card-meta {{ color: var(--muted); font-size: 0.85em; margin-bottom: 6px; }}
  .card-body {{ color: #374151; font-size: 0.95em; }}
  .card-desc {{ color: var(--muted); font-size: 0.88em; margin-top: 8px; }}
  .tag {{
    display: inline-block; margin-top: 10px;
    background: #eff6ff; color: var(--blue); border: 1px solid #bfdbfe;
    border-radius: 6px; padding: 3px 12px; font-size: 0.82em; font-weight: 500;
  }}

  /* Highlights */
  .highlights-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 16px; }}
  .highlight-card {{
    background: var(--card-bg); border-radius: 14px; overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid var(--border);
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .highlight-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }}
  .highlight-img {{
    height: 180px; background-size: cover; background-position: center;
    background-color: #dde;
  }}
  .highlight-body {{ padding: 18px 20px; }}
  .highlight-title {{ font-weight: 700; font-size: 1em; margin-bottom: 6px; color: var(--navy); }}
  .highlight-desc {{ font-size: 0.88em; color: #4b5563; line-height: 1.55; }}

  /* Flights */
  .flight-card {{ display: flex; flex-direction: column; gap: 6px; }}
  .flight-route {{ display: flex; align-items: center; gap: 12px; margin-bottom: 2px; }}
  .flight-city {{ font-weight: 700; font-size: 1.05em; color: var(--navy); }}
  .flight-arrow {{ color: var(--accent); font-size: 1.2em; }}

  /* Itinerary accordion */
  .day-block {{
    background: var(--card-bg); border-radius: 12px; margin-bottom: 10px;
    border: 1px solid var(--border); overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .day-summary {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 18px 24px; cursor: pointer; list-style: none;
    user-select: none; gap: 12px;
  }}
  .day-summary::-webkit-details-marker {{ display: none; }}
  .day-summary::after {{
    content: '›'; font-size: 1.4em; color: var(--muted);
    transition: transform 0.2s; margin-left: 8px;
  }}
  details[open] .day-summary::after {{ transform: rotate(90deg); }}
  .day-summary:hover {{ background: #f9fafb; }}
  .day-summary-left {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
  .day-number {{ font-weight: 800; font-size: 0.78em; color: var(--accent); text-transform: uppercase; letter-spacing: 0.5px; }}
  .day-date {{ font-weight: 600; color: var(--navy); }}
  .day-theme {{ font-size: 0.85em; color: var(--muted); }}
  .day-cost {{ font-size: 0.82em; font-weight: 600; color: var(--blue); background: #eff6ff; border-radius: 6px; padding: 3px 10px; white-space: nowrap; }}
  .day-content {{ padding: 4px 24px 20px; border-top: 1px solid var(--border); }}
  .segment {{ margin-top: 16px; }}
  .segment-label {{ font-weight: 700; font-size: 0.78em; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
  .segment-text {{ color: #374151; font-size: 0.93em; line-height: 1.6; }}

  /* Budget table */
  .budget-table {{ width: 100%; border-collapse: collapse; background: var(--card-bg); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
  .budget-table th {{ background: var(--navy); color: #fff; padding: 13px 20px; text-align: left; font-size: 0.85em; font-weight: 600; }}
  .budget-table td {{ padding: 12px 20px; border-bottom: 1px solid var(--border); font-size: 0.93em; }}
  .budget-table td:last-child {{ text-align: right; font-variant-numeric: tabular-nums; font-weight: 500; }}
  .budget-table .total-row td {{ font-weight: 800; background: var(--navy); color: #fff; border-bottom: none; font-size: 1em; }}
  .budget-table .headroom-row td {{ font-weight: 600; background: #ecfdf5; color: #065f46; border-bottom: none; }}

  /* Bonus activities */
  .bonus-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }}
  .bonus-card {{
    background: var(--card-bg); border-radius: 10px; padding: 18px 20px;
    border: 1px solid var(--border); border-left: 3px solid var(--accent);
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .bonus-title {{ font-weight: 700; font-size: 0.95em; margin-bottom: 4px; }}
  .bonus-title a {{ color: var(--navy); text-decoration: none; }}
  .bonus-title a:hover {{ text-decoration: underline; }}
  .bonus-desc {{ font-size: 0.87em; color: #4b5563; line-height: 1.5; }}

  /* Footer */
  .footer {{ text-align: center; color: var(--muted); font-size: 0.8em; padding: 32px 20px 56px; border-top: 1px solid var(--border); margin-top: 40px; }}

  /* Responsive */
  @media (max-width: 640px) {{
    .hero-content {{ padding: 36px 20px; }}
    .container {{ padding: 32px 16px; }}
    .day-summary {{ padding: 14px 16px; }}
    .day-content {{ padding: 4px 16px 16px; }}
    .budget-table td, .budget-table th {{ padding: 10px 14px; }}
  }}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-bg"></div>
  <div class="hero-content">
    <h1>{destination}</h1>
    <div class="hero-meta">
      {"<div class='hero-pill'>📅 " + date_range + "</div>" if date_range else ""}
      {"<div class='hero-pill'>👥 " + travelers + "</div>" if travelers else ""}
      {"<div class='hero-pill accent'>✦ " + vibe + "</div>" if vibe else ""}
    </div>
  </div>
</div>

<nav class="nav">
  {"<a href='#highlights'>Highlights</a>" if trip.get('highlights') else ""}
  {"<a href='#stays'>Stays</a>" if trip.get('accommodation') else ""}
  {"<a href='#flights'>Flights</a>" if trip.get('flights') else ""}
  {"<a href='#itinerary'>Itinerary</a>" if trip.get('itinerary') else ""}
  {"<a href='#budget'>Budget</a>" if trip.get('budget_summary') else ""}
  {"<a href='#extras'>Extras</a>" if trip.get('bonus_activities') else ""}
</nav>

<div class="container">

  {('<section id="highlights"><h2>Highlights</h2><div class="highlights-grid">' + highlights_html + '</div></section>') if highlights_html else ''}

  {('<section id="stays"><h2>Where We\'re Staying</h2>' + accommodation_html + '</section>') if accommodation_html else ''}

  {('<section id="flights"><h2>Flights</h2>' + flights_html + '</section>') if flights_html else ''}

  {('<section id="itinerary"><h2>Day by Day</h2>' + itinerary_html + '</section>') if itinerary_html else ''}

  {('<section id="budget"><h2>Budget Summary</h2><table class="budget-table"><thead><tr><th>Category</th><th>Estimated Cost</th></tr></thead><tbody>' + budget_rows + '</tbody></table></section>') if budget_rows else ''}

  {('<section id="extras"><h2>Also Worth Considering</h2><div class="bonus-grid">' + bonus_html + '</div></section>') if bonus_html else ''}

</div>

<div class="footer">Generated {generated} &middot; Travel Planner &middot; {destination}</div>

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
