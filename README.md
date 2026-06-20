# AI Competitive Intelligence Agent

An agentic system designed to track competitor websites, scrape features and pricing plans, detect adjustments/modifications over time, and log snapshot reports to a local history database. 

This tool helps businesses automatically monitor changes in their landscape by alerting them to adjustments in plan prices, currencies, and features.

---

## Key Features

- **Multi-Agent Orchestration**: Utilizes worker scraper and worker parser sub-agents coordinated by a central planner.
- **Robust Scraping Tool**: Automatically sanitizes scraped page HTML into clean Markdown and respects target `robots.txt` policies.
- **Rule & LLM-Based Parser**: Structure unstructured webpage outputs into structured schemas for pricing plans and features.
- **Automated Diff Engine**: Instantly computes pricing differences (added, removed, or modified plans) and feature updates (added or removed features).
- **Interactive CLI**: Includes built-in subcommands to run pipelines, simulate changes, query stored snapshots, or clear history without external tools.

---

## Directory Structure

```
├── config/
│   └── competitors.json       # Configured target URLs for competitors
├── src/
│   ├── agents/
│   │   ├── planner.py         # Coordinates worker sub-agents
│   │   ├── worker_scraper.py  # Handles data fetching
│   │   ├── worker_parser.py   # Processes text data into structured schemas
│   │   └── evaluator.py       # Compares data against historical records
│   ├── memory/
│   │   └── db_client.py       # Local SQLite client connection wrapper
│   ├── tools/
│   │   ├── scraper_tool.py    # Sanitizes HTML to Markdown
│   │   └── diff_tool.py       # Computes structured differences
│   ├── utils/
│   │   └── logger.py          # Structured JSON logging context logger
│   └── main.py                # Command Line Interface (CLI) entry point
├── requirements.txt           # Dependency requirements
└── .gitignore                 # Excludes local databases and compiler caches
```

---

## Setup & Installation

### Prerequisite
Make sure you have **Python 3.8+** installed.

1. **Install Dependencies**:
   Install the required packages from the root directory:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Targets**:
   Update `config/competitors.json` with the competitor sites you'd like to monitor:
   ```json
   {
     "competitors": [
       {
         "id": "saas_corp",
         "name": "SaaS Corp",
         "pricing_url": "https://example.com/pricing",
         "features_url": "https://example.com/features"
       }
     ]
   }
   ```

---

## Usage (CLI Command Reference)

Interact with the tool using the following console subcommands:

### 1. Run live tracking session
Query and record the current state of all configured competitors:
```bash
python src/main.py run
```

### 2. Simulate baseline and changes (Demo Mode)
Clear your database, run a baseline tracking snapshot, simulate website updates, and run evaluation again to verify that modified pricing and new features are successfully captured:
```bash
python src/main.py demo
```

### 3. View saved snapshots history
Print stored snapshots directly from the SQLite database in a formatted view:
* **Show all database records:**
  ```bash
  python src/main.py view
  ```
* **Filter by a specific competitor ID:**
  ```bash
  python src/main.py view --competitor saas_corp
  ```
* **Limit the output to the last $N$ records:**
  ```bash
  python src/main.py view --limit 5
  ```

### 4. Clear snapshot logs
Wipe/delete the SQLite snapshots database to start fresh:
```bash
python src/main.py clear
```
