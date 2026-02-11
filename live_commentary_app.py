import streamlit as st
import requests
import time
from ollama import Client

# =======================
# 🔧 CONFIGURATION
# =======================
API_KEY = "***************************"  # ← your key
OLLAMA_HOST = "http://localhost:11434"       # Ollama server
MODEL_NAME = "llama3.2"                      # model name
POLL_INTERVAL = 30                           # seconds between refreshes (manual)

client = Client(host=OLLAMA_HOST)
headers = {"x-apisports-key": API_KEY}


# =======================
# ⚽ FETCH LIVE FIXTURES
# =======================
def get_live_fixtures():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json().get("response", [])
        return data
    except Exception as e:
        st.error(f"Error fetching live fixtures: {e}")
        return []


# =======================
# ⚙️ FETCH LIVE EVENTS
# =======================
def get_live_events(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return res.json().get("response", [])
    except Exception as e:
        st.error(f"Error fetching events: {e}")
        return []


# =======================
# 🧠 BUILD PROMPT
# =======================
def build_commentary_prompt(event):
    minute = event.get("time", {}).get("elapsed", "?")
    team = event.get("team", {}).get("name", "Unknown Team")
    player = event.get("player", {}).get("name", "Unknown Player")
    event_type = event.get("type", "Unknown Event")
    detail = event.get("detail", event.get("comments", "")) or ""

    return (
        "You are a professional football commentator.\n"
        "Generate an exciting, natural-sounding live commentary for this football event.\n"
        f"Minute: {minute}\n"
        f"Team: {team}\n"
        f"Player: {player}\n"
        f"Event: {event_type}\n"
        f"Details: {detail}\n"
        "Keep it short (1–2 sentences) and emotional, like a live TV broadcast."
    )


# =======================
# 🗣️ GENERATE COMMENTARY
# =======================
def generate_commentary(event):
    prompt = build_commentary_prompt(event)
    try:
        response = client.generate(model=MODEL_NAME, prompt=prompt)
        return response.get("response", "").strip()
    except Exception as e:
        return f"(Model error: {e})"


# =======================
# 🏟️ STREAMLIT UI
# =======================
st.set_page_config(page_title="Live AI Football Commentator", page_icon="⚽", layout="centered")
st.title("⚽ Live AI Football Commentator")
st.write("Powered by **API-Football** + **LLaMA 3.2 via Ollama**")

# --- Step 1: Get Live Fixtures ---
fixtures = get_live_fixtures()

if not fixtures:
    st.warning("No live matches found right now. Try again later.")
    st.stop()

fixture_names = [
    f"{f['teams']['home']['name']} vs {f['teams']['away']['name']} ({f['fixture']['status']['short']})"
    for f in fixtures
]
fixture_choice = st.selectbox("Select a Live Match:", fixture_names)
fixture_id = fixtures[fixture_names.index(fixture_choice)]["fixture"]["id"]

# --- Initialize session state for this fixture ---
if "fixture_id" not in st.session_state or st.session_state.fixture_id != fixture_id:
    st.session_state.fixture_id = fixture_id
    st.session_state.seen_events = set()
    st.session_state.commentary_feed = []

st.write(f"📺 Tracking match: **{fixture_choice}**")
st.write(f"⏱️ Refresh interval suggestion: {POLL_INTERVAL} seconds (manual refresh)")

# --- Step 2: Button to fetch latest events once ---
if st.button("🔄 Fetch Latest Commentary"):
    with st.spinner("Fetching events and generating commentary..."):
        events = get_live_events(fixture_id)
        new_lines = []

        for e in events:
            # Unique key per event to avoid duplicates
            event_key = (
                e.get("time", {}).get("elapsed"),
                (e.get("player") or {}).get("name"),
                e.get("type"),
                e.get("detail") or e.get("comments") or ""
            )
            if event_key not in st.session_state.seen_events:
                st.session_state.seen_events.add(event_key)
                minute = e.get("time", {}).get("elapsed", "?")
                team = (e.get("team") or {}).get("name", "Unknown Team")
                commentary_text = generate_commentary(e)
                line = f"**{minute}' | {team}** — {commentary_text}"
                new_lines.append(line)

        # Add new lines to the top of the feed
        for line in reversed(new_lines):
            st.session_state.commentary_feed.insert(0, line)

        if not new_lines:
            st.info("No new events since last check.")

# --- Step 3: Display commentary feed ---
st.markdown("### 🗣️ Live Commentary Feed (latest on top)")
if not st.session_state.commentary_feed:
    st.write("No commentary yet. Click **Fetch Latest Commentary** to check for new events.")
else:
    for line in st.session_state.commentary_feed:
        st.markdown(line)

