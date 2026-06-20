from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import json
import sys

# Ensure root directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.planner import Planner

app = FastAPI(title="AI Competitive Intelligence Agent")

def load_competitors():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "competitors.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)["competitors"]
    return []

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    competitors = load_competitors()
    competitors_html = ""
    for comp in competitors:
        competitors_html += f"""
        <div class="competitor-card">
            <div class="competitor-name">🏢 {comp['name']}</div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Competitive Intelligence Agent</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --accent-blue: #3b82f6;
                --accent-green: #10b981;
                --border-color: #334155;
                --glow-color: rgba(59, 130, 246, 0.15);
            }}
            body {{
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-primary);
                margin: 0;
                padding: 24px;
                display: flex;
                justify-content: center;
            }}
            .container {{
                max-width: 1200px;
                width: 100%;
            }}
            header {{
                margin-bottom: 32px;
                text-align: center;
            }}
            h1 {{
                font-size: 2.5rem;
                margin: 0 0 8px 0;
                background: linear-gradient(135deg, #60a5fa, #3b82f6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .subtitle {{
                color: var(--text-secondary);
                font-size: 1.1rem;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 24px;
                margin-bottom: 32px;
            }}
            @media (max-width: 768px) {{
                .grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            .card {{
                background-color: var(--card-bg);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
                transition: border-color 0.3s ease, box-shadow 0.3s ease;
            }}
            .card:hover {{
                border-color: var(--accent-blue);
                box-shadow: 0 0 20px var(--glow-color);
            }}
            h2 {{
                font-size: 1.4rem;
                margin-top: 0;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 8px;
                color: #60a5fa;
            }}
            .competitor-list {{
                display: flex;
                flex-direction: column;
                gap: 16px;
            }}
            .competitor-card {{
                background: rgba(15, 23, 42, 0.4);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 16px;
            }}
            .competitor-name {{
                font-weight: 600;
                font-size: 1.1rem;
                margin-bottom: 8px;
            }}
            .competitor-link {{
                color: var(--accent-blue);
                text-decoration: none;
                font-size: 0.9rem;
                display: inline-block;
                margin-right: 16px;
                margin-top: 4px;
            }}
            .competitor-link:hover {{
                text-decoration: underline;
            }}
            button {{
                width: 100%;
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px;
                font-weight: 600;
                font-size: 1.05rem;
                cursor: pointer;
                transition: opacity 0.2s, transform 0.1s;
                margin-top: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
            button:hover {{
                opacity: 0.9;
            }}
            button:active {{
                transform: scale(0.98);
            }}
            button:disabled {{
                background: var(--border-color);
                cursor: not-allowed;
                opacity: 0.6;
            }}
            .report-content {{
                background-color: rgba(15, 23, 42, 0.6);
                border: 1px dashed var(--border-color);
                border-radius: 12px;
                padding: 20px;
                min-height: 200px;
                white-space: pre-wrap;
                font-size: 0.95rem;
                line-height: 1.6;
                color: var(--text-secondary);
            }}
            .report-content.active {{
                color: var(--text-primary);
                border-style: solid;
            }}
            .spinner {{
                display: none;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 0.8s linear infinite;
            }}
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            .history-card {{
                width: 100%;
                margin-top: 24px;
            }}
            .table-container {{
                overflow-x: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 16px;
            }}
            th, td {{
                text-align: left;
                padding: 14px;
                border-bottom: 1px solid var(--border-color);
            }}
            th {{
                color: var(--text-secondary);
                font-weight: 500;
            }}
            tr:hover td {{
                background-color: rgba(255, 255, 255, 0.02);
            }}
            .tag {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 0.8rem;
                font-weight: 600;
            }}
            .tag-competitor {{
                background-color: rgba(59, 130, 246, 0.15);
                color: #93c5fd;
            }}
            .nested-list {{
                margin: 0;
                padding-left: 20px;
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🕵️ AI Competitive Intelligence Agent</h1>
                <div class="subtitle">Autonomous competitor software tracking and difference evaluation service</div>
            </header>

            <div class="grid">
                <!-- Left Sidebar -->
                <div class="card">
                    <h2>🏢 Configured Competitors</h2>
                    <div class="competitor-list">
                        {competitors_html}
                    </div>
                    
                    <button id="runBtn" onclick="runTracking()">
                        <div class="spinner" id="btnSpinner"></div>
                        <span id="btnText">🚀 Run Tracking Session</span>
                    </button>
                </div>

                <!-- Right Side Analysis -->
                <div class="card">
                    <h2>📊 Latest Analysis Report</h2>
                    <div id="reportBox" class="report-content">Click 'Run Tracking Session' to start agent analysis.</div>
                </div>
            </div>

            <!-- Snapshots History Table -->
            <div class="card history-card">
                <h2>📜 Stored Snapshots History</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Competitor</th>
                                <th>Timestamp</th>
                                <th>Plans & Pricing</th>
                                <th>Features</th>
                                <th>Trace ID</th>
                            </tr>
                        </thead>
                        <tbody id="historyBody">
                            <tr>
                                <td colspan="5" style="text-align: center; color: var(--text-secondary);">Loading history logs...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            async function loadHistory() {{
                try {{
                    const res = await fetch('/history');
                    const data = await res.json();
                    const tbody = document.getElementById('historyBody');
                    tbody.innerHTML = '';
                    
                    if (!data.snapshots || data.snapshots.length === 0) {{
                        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">No snapshots stored yet. Run a session first.</td></tr>';
                        return;
                    }}
                    
                    data.snapshots.forEach(snap => {{
                        let plansHtml = '<ul class="nested-list">';
                        snap.pricing_data.forEach(p => {{
                            const price = typeof p.price === 'number' ? `$${{p.price}}` : p.price;
                            plansHtml += `<li><strong>${{p.name}}</strong>: ${{price}} ${{p.currency || 'USD'}}</li>`;
                        }});
                        plansHtml += '</ul>';
                        
                        let featsHtml = '<ul class="nested-list">';
                        snap.features_data.forEach(f => {{
                            featsHtml += `<li>${{f}}</li>`;
                        }});
                        featsHtml += '</ul>';

                        const row = `<tr>
                            <td><span class="tag tag-competitor">${{snap.competitor_id}}</span></td>
                            <td>${{new Date(snap.timestamp).toLocaleString()}}</td>
                            <td>${{plansHtml}}</td>
                            <td>${{featsHtml}}</td>
                            <td><code style="color: var(--text-secondary); font-size: 0.85rem;">${{snap.trace_id}}</code></td>
                        </tr>`;
                        tbody.insertAdjacentHTML('beforeend', row);
                    }});
                }} catch (e) {{
                    console.error("Error loading history:", e);
                }}
            }}

            async function runTracking() {{
                const runBtn = document.getElementById('runBtn');
                const btnSpinner = document.getElementById('btnSpinner');
                const btnText = document.getElementById('btnText');
                const reportBox = document.getElementById('reportBox');
                
                runBtn.disabled = true;
                btnSpinner.style.display = 'block';
                btnText.innerText = 'Analyzing websites...';
                reportBox.innerText = 'Agents are fetching page content and analyzing details...';
                reportBox.classList.remove('active');
                
                try {{
                    const res = await fetch('/run');
                    const data = await res.json();
                    
                    if (data.summary) {{
                        reportBox.innerText = data.summary;
                        reportBox.classList.add('active');
                    }} else {{
                        reportBox.innerText = "Error running analysis: " + JSON.stringify(data);
                    }}
                }} catch (e) {{
                    reportBox.innerText = "Failed to communicate with the agent backend: " + e;
                }} finally {{
                    runBtn.disabled = false;
                    btnSpinner.style.display = 'none';
                    btnText.innerText = '🚀 Run Tracking Session';
                    loadHistory();
                }}
            }}

            // Load on start
            loadHistory();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/run")
def run_tracker():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "competitors.json")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitors.db")
    
    with open(config_path, "r") as f:
        competitors = json.load(f)["competitors"]
        
    planner = Planner(db_path=db_path)
    res = planner.run_tracker_api(competitors) if hasattr(planner, "run_tracker_api") else planner.run_tracking_session(competitors)
    return res

@app.get("/history")
def view_history():
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitors.db")
    if not os.path.exists(db_path):
        return {"snapshots": []}
        
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
