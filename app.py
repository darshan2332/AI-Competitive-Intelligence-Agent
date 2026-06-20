from fastapi import FastAPI
import os
import json
import sys

# Ensure root directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.planner import Planner

app = FastAPI(title="AI Competitive Intelligence Agent")

@app.get("/")
def greet_json():
    return {
        "status": "online",
        "message": "AI Competitive Intelligence Agent is running!",
        "endpoints": {
            "run_tracking": "/run",
            "view_history": "/history"
        }
    }

@app.get("/run")
def run_tracker():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "competitors.json")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitors.db")
    
    with open(config_path, "r") as f:
        competitors = json.load(f)["competitors"]
        
    planner = Planner(db_path=db_path)
    res = planner.run_tracking_session(competitors)
    return res

@app.get("/history")
def view_history():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitors.db")
    if not os.path.exists(db_path):
        return {"message": "No database found. Run a session first at /run."}
        
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT competitor_id, timestamp, pricing_data, features_data, trace_id FROM snapshots ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        snapshots = []
        for r in rows:
            snapshots.append({
                "competitor_id": r["competitor_id"],
                "timestamp": r["timestamp"],
                "pricing_data": json.loads(r["pricing_data"]),
                "features_data": json.loads(r["features_data"]),
                "trace_id": r["trace_id"]
            })
            
        return {"snapshots": snapshots}
