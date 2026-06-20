import os
import sys
import json
import argparse
import sqlite3

# Ensure parent directory of 'src' is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.planner import Planner
from src.utils.logger import logger

def load_competitors(config_path: str):
    with open(config_path, "r") as f:
        return json.load(f)["competitors"]

def run_session(config_path: str, db_path: str):
    competitors = load_competitors(config_path)
    planner = Planner(db_path=db_path)
    res = planner.run_tracking_session(competitors)
    print("\n" + res["summary"] + "\n")

def run_demo(config_path: str, db_path: str):
    logger.info("=== Starting Demo Simulation ===")
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info("Cleared previous database for fresh demo run.")

    competitors = load_competitors(config_path)
    planner = Planner(db_path=db_path)

    # 1. First run - establishes baseline snap
    logger.info("=== RUN 1: Establishing Baselines ===")
    res_1 = planner.run_tracking_session(competitors)
    print("\n" + res_1["summary"] + "\n")

    # 2. Simulate page changes for next cycle
    logger.info("=== Simulating website updates in competitor data ===")
    original_parse = planner.parser.parse_data
    
    def mock_modified_parse(raw_data):
        parsed = original_parse(raw_data)
        # Adjust plan price and add a feature
        for plan in parsed["plans"]:
            plan_name = plan["name"].lower()
            if "growth" in plan_name:
                plan["price"] = 59.0 # Price increase from 49 to 59
            elif "starter" in plan_name:
                plan["price"] = 24.0 # Price increase from 19 to 24
        parsed["features"].append("Real-time Alerting API")
        return parsed
        
    planner.parser.parse_data = mock_modified_parse

    # 3. Second run - evaluates modifications against baselines
    logger.info("=== RUN 2: Detecting Modifications ===")
    res_2 = planner.run_tracking_session(competitors)
    print("\n" + res_2["summary"] + "\n")

def view_snapshots(db_path: str, competitor_id: str = None, limit: int = None):
    if not os.path.exists(db_path):
        print("\nDatabase does not exist yet. Run a tracking session or demo first.\n")
        return
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT id, competitor_id, timestamp, pricing_data, features_data, trace_id FROM snapshots"
        params = []
        if competitor_id:
            query += " WHERE competitor_id = ?"
            params.append(competitor_id)
        query += " ORDER BY timestamp DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            print("\nNo snapshots found in database.\n")
            return
            
        print("\n========================= Saved Competitor Snapshots =========================")
        for row in rows:
            print(f"\nSnapshot ID: {row['id']} | Competitor: {row['competitor_id']} | Timestamp: {row['timestamp']}")
            print(f"Trace ID: {row['trace_id']}")
            
            # Format pricing
            try:
                plans = json.loads(row['pricing_data'])
                print("  Plans:")
                for p in plans:
                    currency = p.get('currency', 'USD')
                    price = p.get('price')
                    price_str = f"${price}" if isinstance(price, (int, float)) else str(price)
                    print(f"    - {p['name']}: {price_str} {currency}")
            except Exception as e:
                print(f"  Error parsing pricing: {e}")
                
            # Format features
            try:
                features = json.loads(row['features_data'])
                print("  Features:")
                for f in features:
                    print(f"    - {f}")
            except Exception as e:
                print(f"  Error parsing features: {e}")
            print("-" * 78)
        print()

def clear_database(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
        print("\nDatabase cleared successfully.\n")
    else:
        print("\nDatabase does not exist or is already cleared.\n")

def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "competitors.json")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "competitors.db")

    parser = argparse.ArgumentParser(description="Competitor Tracker CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 'run' command
    subparsers.add_parser("run", help="Run the tracking session on all configured competitors")

    # 'demo' command
    subparsers.add_parser("demo", help="Simulate a two-cycle tracking session run showing changes")

    # 'view' command
    view_parser = subparsers.add_parser("view", help="View saved database snapshots")
    view_parser.add_argument("--competitor", type=str, help="Filter snapshots by competitor ID")
    view_parser.add_argument("--limit", type=int, help="Limit the number of snapshots returned")

    # 'clear' command
    subparsers.add_parser("clear", help="Clear/delete the database snapshots history")

    args = parser.parse_args()

    if args.command == "run":
        run_session(config_path, db_path)
    elif args.command == "demo":
        run_demo(config_path, db_path)
    elif args.command == "view":
        view_snapshots(db_path, competitor_id=args.competitor, limit=args.limit)
    elif args.command == "clear":
        clear_database(db_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
