import streamlit as st
import os
import sys
import pandas as pd
import sqlite3
import json

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.planner import Planner
from src.memory.db_client import DBClient

st.set_page_config(page_title="Competitor Tracker", layout="wide")

st.title("🕵️ Competitor Pricing & Feature Tracker")
st.write("An autonomous multi-agent system tracking competitor software plans and feature updates.")

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "competitors.db")
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "competitors.json")

# Initialize database client
db_client = DBClient(db_path)

def load_competitors():
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)["competitors"]
    return []

competitors = load_competitors()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Configured Competitors")
    for comp in competitors:
        st.info(f"**{comp['name']}**\n- [Pricing Page]({comp['pricing_url']})\n- [Features Page]({comp['features_url']})")

    # Run tracking button
    if st.button("🚀 Run Tracking Session", use_container_width=True):
        with st.spinner("Agents are crawling and analyzing websites..."):
            planner = Planner(db_path=db_path)
            result = planner.run_tracking_session(competitors)
            st.success("Session completed!")
            st.session_state["latest_summary"] = result["summary"]

with col2:
    st.subheader("Latest Analysis Report")
    if "latest_summary" in st.session_state:
        st.markdown(st.session_state["latest_summary"])
    else:
        st.write("Click 'Run Tracking Session' on the left to start agent analysis.")

# Show snapshots
st.subheader("Stored Snapshots History")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT competitor_id, timestamp, pricing_data, features_data FROM snapshots ORDER BY timestamp DESC", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No snapshots stored yet. Run a session first.")
    except Exception as e:
        st.error(f"Error loading database snapshots: {e}")
    finally:
        conn.close()
else:
    st.info("No database found yet. Run a session to initialize.")
