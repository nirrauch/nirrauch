#!/usr/bin/env python3
"""
Travel Planner – Traveler Profile Survey Generator

Generates a creative, scenario-based survey to build rich traveler profiles.
Results are saved to ~/repos/nirrauch/travelplans/travel-data/surveys/ and can be ingested by the
travel-planner skill to populate traveler profiles in travel-data.json.

Usage:
  # Interactive local web app (auto-opens browser, saves JSON on submit):
  python3 profile_survey.py --mode web --name "Nir"

  # Offline markdown questionnaire (fill in manually, Claude ingests later):
  python3 profile_survey.py --mode doc --name "Sarah"

  # Custom output directory:
  python3 profile_survey.py --mode doc --name "Sarah" --output ~/Desktop/

Options:
  --mode    web | doc           (required)
  --name    Traveler's name     (required)
  --output  Output directory    (default: ~/repos/nirrauch/travelplans/travel-data/surveys/)
  --port    Web server port     (default: 8765, web mode only)
"""

import argparse
import json
import os
import sys
import textwrap
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote_plus


# ---------------------------------------------------------------------------
# Survey questions — scenario-based, open-ended, non-leading
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "id": "perfect_saturday",
        "label": "The Open Day",
        "prompt": (
            "It's Saturday. No plans, no obligations, no one counting on you. "
            "Walk me through your ideal version of the day — from waking up to going to sleep."
        ),
        "hint": "There's no right answer — just describe what actually sounds good to you.",
    },
    {
        "id": "the_scene",
        "label": "The Scene",
        "prompt": (
            "A documentary crew is following you on your ideal trip. "
            "They end up with 200 hours of footage. "
            "In the edit room, there's one scene the director keeps rewinding. "
            "What's happening in it?"
        ),
        "hint": "Could be a moment, a place, a meal, a conversation — whatever you keep seeing.",
    },
    {
        "id": "arrival_instinct",
        "label": "First Three Hours",
        "prompt": (
            "You've just landed somewhere new. It's 3pm, you've dropped your bags, "
            "and you have no itinerary. What do you actually do?"
        ),
        "hint": "Instinct, not aspiration — what would you really do?",
    },
    {
        "id": "the_table",
        "label": "What's on the Table",
        "prompt": (
            "You're at a small restaurant you've never heard of, in a neighborhood "
            "you're exploring for the first time. The meal is already ordered. "
            "Describe what arrives."
        ),
        "hint": "Think about the setting, the food, the drink — the whole scene.",
    },
    {
        "id": "one_splurge",
        "label": "The Blank Check Moment",
        "prompt": (
            "You have a single moment on a trip where cost is completely irrelevant. "
            "What do you spend it on?"
        ),
        "hint": "Could be a place to stay, an experience, a meal, a view — anything.",
    },
    {
        "id": "overrated",
        "label": "The Tourist Trap",
        "prompt": (
            "Name something that a lot of travelers rave about that you personally "
            "find overrated, exhausting, or just not your thing."
        ),
        "hint": "Be honest — this helps us skip the wrong stuff.",
    },
    {
        "id": "worth_it_moment",
        "label": "The Anchor",
        "prompt": (
            "Looking back on trips you've loved, what's the kind of moment — "
            "a meal, a view, an unexpected encounter — that most reliably makes "
            "you feel like it was all worth it?"
        ),
        "hint": "Could be a specific memory or a recurring type of experience.",
    },
    {
        "id": "pace_instinct",
        "label": "One More Thing",
        "prompt": (
            "It's the end of a full day. You've done a lot. Your travel partner "
            "wants to add one more thing before heading back. "
            "What's your gut reaction — and does it change depending on what 'one more thing' is?"
        ),
        "hint": "No wrong answers — this is about energy and pace preferences.",
    },
    {
        "id": "hotel_first_ten",
        "label": "The Room",
        "prompt": (
            "You check into a hotel or rental you've never stayed at. "
            "Describe your first ten minutes in the room — what do you notice, "
            "what do you check, what tells you it's going to be a good stay?"
        ),
        "hint": "Details matter here — the small stuff reveals a lot.",
    },
    {
        "id": "the_recommendation",
        "label": "The Recommendation",
        "prompt": (
            "A close friend who travels completely differently from you asks for one honest tip "
            "from somewhere you've been. You end up recommending something "
            "you'd never have predicted you'd suggest — but you mean it. "
            "What do you tell them, and why?"
        ),
        "hint": "The more unexpected the recommendation, the more interesting.",
    },
    {
        "id": "romanticized_place",
        "label": "The Dream",
        "prompt": (
            "Name a place you've romanticized but never been to. "
            "What do you imagine about it — and what drew you there in the first place?"
        ),
        "hint": "Could be a city, a region, a specific kind of landscape.",
    },
    {
        "id": "non_negotiable",
        "label": "The One Thing",
        "prompt": (
            "If someone were planning a trip tailored entirely to you, "
            "what's the single thing they'd have to include to get it right?"
        ),
        "hint": "Think of it as your travel signature.",
    },
    {
        "id": "the_photo",
        "label": "The Photo",
        "prompt": (
            "You're mid-trip and you send one photo home. "
            "Not a landmark shot, not a selfie — something that just felt true about where you are. "
            "Describe what's in it."
        ),
        "hint": "The mundane ones are usually more revealing than the obvious ones.",
    },
    {
        "id": "depth_vs_breadth",
        "label": "The Trade-off",
        "prompt": (
            "Two options for a two-week trip: (A) one region, explored slowly and deeply — "
            "you know the neighborhood, have a regular café, make a local friend. "
            "(B) four different places, each distinct, always moving. "
            "Which do you choose, and why?"
        ),
        "hint": "Or describe a version that's something in between.",
    },
    {
        "id": "the_flashback",
        "label": "The Flashback",
        "prompt": (
            "Six months after a great trip, you're somewhere completely mundane — "
            "stuck in traffic, waiting in a line. Your mind wanders back to one specific "
            "moment from that trip. What is it?"
        ),
        "hint": "Not the highlight reel moment — the one that just keeps coming back.",
    },
]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def surveys_dir(output: Path) -> Path:
    d = output.expanduser().resolve()
    d.mkdir(parents=True, exist_ok=True)
    return d


def survey_json_path(output: Path, name: str) -> Path:
    slug = name.lower().replace(" ", "_")
    return surveys_dir(output) / f"{slug}_survey.json"


def survey_doc_path(output: Path, name: str) -> Path:
    slug = name.lower().replace(" ", "_")
    return surveys_dir(output) / f"{slug}_survey.md"


# ---------------------------------------------------------------------------
# WEB MODE
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} · Travel Profile</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --navy:   #0f2a4a;
    --blue:   #1a5276;
    --accent: #e8a020;
    --light:  #f8f7f4;
    --card:   #ffffff;
    --text:   #1a1a1a;
    --muted:  #6b7280;
    --border: #e5e7eb;
    --green:  #065f46;
    --green-bg: #ecfdf5;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--light);
    color: var(--text);
    line-height: 1.65;
    min-height: 100vh;
  }}

  /* Hero */
  .hero {{
    background: linear-gradient(135deg, var(--navy) 0%, #1b4f72 60%, #2471a3 100%);
    padding: 56px 32px 48px;
    text-align: center;
    color: #fff;
  }}
  .hero h1 {{ font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight: 800; letter-spacing: -0.5px; margin-bottom: 12px; }}
  .hero p {{ color: rgba(255,255,255,0.75); font-size: 1.05em; max-width: 520px; margin: 0 auto; }}
  .hero-pill {{
    display: inline-block; margin-top: 20px;
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2);
    border-radius: 100px; padding: 6px 18px; font-size: 0.85em; color: rgba(255,255,255,0.9);
  }}

  /* Progress */
  .progress-bar-wrap {{
    background: var(--border); height: 4px; width: 100%;
    position: sticky; top: 0; z-index: 10;
  }}
  .progress-bar {{
    background: var(--accent); height: 4px;
    transition: width 0.3s ease;
    width: 0%;
  }}

  /* Form */
  .container {{ max-width: 720px; margin: 0 auto; padding: 40px 24px 80px; }}
  .q-block {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 30px 32px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.03);
    transition: box-shadow 0.2s;
  }}
  .q-block:focus-within {{
    box-shadow: 0 0 0 2px var(--accent), 0 4px 16px rgba(0,0,0,0.08);
  }}
  .q-number {{
    font-size: 0.72em; font-weight: 700; color: var(--accent);
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
  }}
  .q-label {{
    font-size: 1.05em; font-weight: 700; color: var(--navy); margin-bottom: 10px;
  }}
  .q-prompt {{ color: #374151; font-size: 0.97em; line-height: 1.65; margin-bottom: 12px; }}
  .q-hint {{
    font-size: 0.82em; color: var(--muted); font-style: italic;
    margin-bottom: 14px; padding-left: 12px; border-left: 2px solid var(--border);
  }}
  textarea {{
    width: 100%; min-height: 100px; resize: vertical;
    padding: 12px 14px; border: 1px solid var(--border);
    border-radius: 8px; font-size: 0.95em; font-family: inherit;
    color: var(--text); background: var(--light);
    transition: border-color 0.15s, box-shadow 0.15s;
    line-height: 1.6;
  }}
  textarea:focus {{
    outline: none; border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(26,82,118,0.1);
    background: #fff;
  }}
  textarea::placeholder {{ color: #9ca3af; }}

  /* Submit */
  .submit-wrap {{ text-align: center; padding-top: 8px; }}
  .submit-btn {{
    background: var(--navy); color: #fff;
    border: none; border-radius: 10px;
    padding: 16px 48px; font-size: 1em; font-weight: 700;
    cursor: pointer; letter-spacing: 0.2px;
    transition: background 0.15s, transform 0.1s;
  }}
  .submit-btn:hover {{ background: var(--blue); transform: translateY(-1px); }}
  .submit-btn:active {{ transform: translateY(0); }}
  .submit-note {{
    font-size: 0.82em; color: var(--muted); margin-top: 10px;
  }}

  /* Thank-you page */
  .thankyou {{
    max-width: 540px; margin: 80px auto; text-align: center; padding: 0 24px;
  }}
  .thankyou-icon {{ font-size: 4em; margin-bottom: 16px; }}
  .thankyou h2 {{ font-size: 1.8em; font-weight: 800; color: var(--navy); margin-bottom: 12px; }}
  .thankyou p {{ color: var(--muted); font-size: 1em; line-height: 1.7; }}
  .thankyou .path-note {{
    display: inline-block; margin-top: 24px;
    background: var(--green-bg); color: var(--green);
    border: 1px solid #a7f3d0; border-radius: 8px;
    padding: 10px 20px; font-size: 0.85em; font-family: monospace;
    word-break: break-all;
  }}

  @media (max-width: 600px) {{
    .hero {{ padding: 40px 20px 32px; }}
    .q-block {{ padding: 22px 20px; }}
    .container {{ padding: 28px 16px 60px; }}
  }}
</style>
</head>
<body>

<div class="hero">
  <h1>Travel Profile · {name}</h1>
  <p>A few questions to understand how you travel — not what you've done, but how you feel about it.</p>
  <div class="hero-pill">✦ {question_count} questions · ~10 minutes</div>
</div>

<div class="progress-bar-wrap"><div class="progress-bar" id="progress"></div></div>

<div class="container">
<form method="POST" action="/submit" id="survey-form">
  <input type="hidden" name="traveler_name" value="{name}">
{questions_html}
  <div class="submit-wrap">
    <button type="submit" class="submit-btn">Save My Profile →</button>
    <div class="submit-note">Your answers are saved locally — they never leave your machine.</div>
  </div>
</form>
</div>

<script>
  const textareas = document.querySelectorAll('textarea');
  const bar = document.getElementById('progress');
  function updateProgress() {{
    const filled = [...textareas].filter(t => t.value.trim().length > 0).length;
    bar.style.width = (filled / textareas.length * 100) + '%';
  }}
  textareas.forEach(t => t.addEventListener('input', updateProgress));
  updateProgress();
</script>
</body>
</html>
"""

THANKYOU_HTML = """\
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Profile Saved</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #f8f7f4; display: flex; align-items: center; justify-content: center;
         min-height: 100vh; margin: 0; padding: 24px; }}
  .card {{ background: #fff; border-radius: 16px; padding: 48px 40px; max-width: 480px;
           text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
  .icon {{ font-size: 3.5em; margin-bottom: 16px; }}
  h2 {{ font-size: 1.7em; font-weight: 800; color: #0f2a4a; margin-bottom: 10px; }}
  p {{ color: #6b7280; line-height: 1.65; margin-bottom: 8px; }}
  .path {{ display: inline-block; margin-top: 20px; background: #ecfdf5; color: #065f46;
           border: 1px solid #a7f3d0; border-radius: 8px; padding: 10px 18px;
           font-family: monospace; font-size: 0.82em; word-break: break-all; }}
  .close {{ display: inline-block; margin-top: 28px; background: #0f2a4a; color: #fff;
            border-radius: 8px; padding: 12px 32px; font-weight: 700; text-decoration: none; }}
</style>
</head><body>
<div class="card">
  <div class="icon">✅</div>
  <h2>Profile saved, {name}!</h2>
  <p>Your answers have been saved. Claude will use them to personalize your travel plans.</p>
  <p>You can close this tab and return to your planning session.</p>
  <div class="path">{save_path}</div>
</div>
</body></html>
"""


def build_questions_html(name: str) -> str:
    blocks = []
    for i, q in enumerate(QUESTIONS, 1):
        hint_html = f'<div class="q-hint">{q["hint"]}</div>' if q.get("hint") else ""
        blocks.append(f"""  <div class="q-block">
    <div class="q-number">Question {i} of {len(QUESTIONS)} · {q['label']}</div>
    <div class="q-label">{q['prompt']}</div>
    {hint_html}
    <textarea name="{q['id']}" placeholder="Your answer…" rows="4"></textarea>
  </div>""")
    return "\n".join(blocks)


class SurveyHandler(BaseHTTPRequestHandler):
    save_path: Path = None
    name: str = ""

    def log_message(self, format, *args):
        pass  # Suppress default HTTP log spam

    def do_GET(self):
        if self.path == "/" or self.path == "/survey":
            html = HTML_TEMPLATE.format(
                name=self.name,
                question_count=len(QUESTIONS),
                questions_html=build_questions_html(self.name),
            )
            self._respond(200, "text/html", html)
        else:
            self._respond(404, "text/plain", "Not found")

    def do_POST(self):
        if self.path == "/submit":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            fields = parse_qs(raw, keep_blank_values=True)

            answers = {}
            traveler_name = fields.get("traveler_name", [self.name])[0]
            for q in QUESTIONS:
                answers[q["id"]] = unquote_plus(
                    fields.get(q["id"], [""])[0]
                ).strip()

            result = {
                "traveler_name": traveler_name,
                "completed_at": datetime.now().isoformat(),
                "answers": answers,
            }

            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"\n✓ Survey saved → {self.save_path}")

            html = THANKYOU_HTML.format(name=traveler_name, save_path=str(self.save_path))
            self._respond(200, "text/html", html)

            # Trigger clean shutdown after a brief delay
            import threading
            threading.Timer(1.5, self.server.shutdown).start()
        else:
            self._respond(404, "text/plain", "Not found")

    def _respond(self, code: int, content_type: str, body: str):
        encoded = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_web(name: str, output: Path, port: int):
    save_path = survey_json_path(output, name)

    # Patch class-level attrs so the handler can access them
    SurveyHandler.save_path = save_path
    SurveyHandler.name = name

    server = HTTPServer(("127.0.0.1", port), SurveyHandler)
    url = f"http://localhost:{port}/"

    print(f"""
╔══════════════════════════════════════════════════════╗
║        Travel Profile Survey — {name:<22}║
╠══════════════════════════════════════════════════════╣
║  Opening survey in your browser…                    ║
║  URL: {url:<47}║
║  Results will be saved to:                          ║
║  {str(save_path)[:50]:<50}  ║
║                                                      ║
║  The server shuts down automatically after submit.  ║
║  Press Ctrl+C to quit early.                        ║
╚══════════════════════════════════════════════════════╝
""")

    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⚠ Survey cancelled.")


# ---------------------------------------------------------------------------
# DOC MODE — Markdown questionnaire
# ---------------------------------------------------------------------------

DOC_HEADER = """\
# Travel Profile Survey — {name}

*Fill in your answers below each question. A sentence or two is plenty — write more if you're inspired.*
*When you're done, save the file and tell Claude: "I've completed my travel survey — please ingest it."*

---

"""

DOC_FOOTER = """\
---

**Completed by:** {name}
**Date completed:** *(fill in)*

*Return this file to Claude to update your traveler profile.*
"""


def run_doc(name: str, output: Path):
    path = survey_doc_path(output, name)
    lines = [DOC_HEADER.format(name=name)]

    for i, q in enumerate(QUESTIONS, 1):
        lines.append(f"## {i}. {q['label']}\n")
        lines.append(f"**{q['prompt']}**\n")
        if q.get("hint"):
            lines.append(f"*{q['hint']}*\n")
        lines.append("\n> *(your answer here)*\n")
        lines.append("\n---\n\n")

    lines.append(DOC_FOOTER.format(name=name))
    path.write_text("".join(lines), encoding="utf-8")

    print(f"""
╔══════════════════════════════════════════════════════╗
║     Travel Profile Questionnaire — {name:<18}║
╠══════════════════════════════════════════════════════╣
║  File created:                                      ║
║  {str(path)[:50]:<50}  ║
║                                                      ║
║  Open the file, fill in your answers under each     ║
║  question, then tell Claude:                        ║
║  "I've completed my survey — please ingest it."    ║
╚══════════════════════════════════════════════════════╝
""")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Travel Profile Survey Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python3 profile_survey.py --mode web --name "Nir"
              python3 profile_survey.py --mode doc --name "Sarah"
              python3 profile_survey.py --mode web --name "Nir" --port 9000
              python3 profile_survey.py --mode doc --name "Sarah" --output ~/Desktop/
        """),
    )
    parser.add_argument("--mode", required=True, choices=["web", "doc"],
                        help="web = interactive browser app | doc = markdown questionnaire file")
    parser.add_argument("--name", required=True,
                        help="Traveler's first name (used for the file and personalisation)")
    parser.add_argument("--output", default="~/repos/nirrauch/travelplans/travel-data/surveys/",
                        help="Output directory (default: ~/repos/nirrauch/travelplans/travel-data/surveys/)")
    parser.add_argument("--port", type=int, default=8765,
                        help="Port for web mode (default: 8765)")

    args = parser.parse_args()
    output = Path(args.output)

    if args.mode == "web":
        run_web(name=args.name, output=output, port=args.port)
    else:
        run_doc(name=args.name, output=output)


if __name__ == "__main__":
    main()
