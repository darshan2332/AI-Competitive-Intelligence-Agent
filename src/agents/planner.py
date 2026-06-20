import uuid
from typing import Dict, Any, List
from src.agents.worker_scraper import WorkerScraper
from src.agents.worker_parser import WorkerParser
from src.agents.evaluator import Evaluator
from src.memory.db_client import DBClient
from src.utils.logger import logger, set_trace_id

class Planner:
    def __init__(self, db_path: str = "competitors.db"):
        self.db_client = DBClient(db_path)
        self.scraper = WorkerScraper()
        self.parser = WorkerParser()
        self.evaluator = Evaluator(self.db_client)

    def run_tracking_session(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Coordinates the pipeline run for all configured competitors.
        """
        # Set trace ID for log grouping
        session_trace_id = f"session_{uuid.uuid4().hex[:8]}"
        set_trace_id(session_trace_id)
        
        logger.info(f"Starting tracking session: {session_trace_id}")
        
        results = {}

        for competitor in competitors:
            comp_id = competitor["id"]
            pricing_url = competitor["pricing_url"]
            features_url = competitor["features_url"]

            logger.info(f"Processing competitor: {competitor['name']} ({comp_id})")

            # 1. Scrape raw page details
            raw_scraped = self.scraper.scrape_competitor(pricing_url, features_url)

            # 2. Parse into structured pricing & features maps
            parsed_data = self.parser.parse_data(raw_scraped)

            # 3. Evaluate parsed structured layout against database history
            evaluation = self.evaluator.evaluate(comp_id, parsed_data)

            if evaluation["is_valid"]:
                # If there are changes (or it's the baseline), store the new snapshot
                if evaluation["has_changes"]:
                    self.db_client.save_snapshot(
                        competitor_id=comp_id,
                        pricing_data=parsed_data["plans"],
                        features_data=parsed_data["features"],
                        trace_id=session_trace_id
                    )
                
                results[comp_id] = {
                    "status": "success",
                    "evaluation": evaluation,
                    "parsed_data": parsed_data
                }
            else:
                logger.error(f"Validation failed for competitor {comp_id}; snapshot not stored.")
                results[comp_id] = {
                    "status": "failed",
                    "reason": "validation_error",
                    "evaluation": evaluation
                }

        summary = self._generate_session_summary(results)
        logger.info(f"Tracking session finished: {session_trace_id}")
        
        return {
            "session_id": session_trace_id,
            "results": results,
            "summary": summary
        }

    def _generate_session_summary(self, results: Dict[str, Any]) -> str:
        """
        Summarizes changes detected across all competitors in this session.
        """
        summary_lines = ["### Session Pricing & Feature Tracker Summary"]
        
        for comp_id, details in results.items():
            if details["status"] == "failed":
                summary_lines.append(f"- **{comp_id}**: Failed processing (Validation Error).")
                continue
            
            eval_report = details["evaluation"]
            if eval_report.get("is_baseline"):
                summary_lines.append(f"- **{comp_id}**: Baseline snapshot generated and saved.")
                continue

            if not eval_report.get("has_changes"):
                summary_lines.append(f"- **{comp_id}**: No pricing or feature changes detected.")
                continue

            summary_lines.append(f"- **{comp_id}**: Changes detected:")
            
            # Pricing details
            p_diff = eval_report.get("pricing_diff", {})
            if p_diff.get("added"):
                added_names = ", ".join(p["name"] for p in p_diff["added"])
                summary_lines.append(f"  - *Added Plans*: {added_names}")
            if p_diff.get("removed"):
                removed_names = ", ".join(p["name"] for p in p_diff["removed"])
                summary_lines.append(f"  - *Removed Plans*: {removed_names}")
            if p_diff.get("modified"):
                for mod in p_diff["modified"]:
                    summary_lines.append(f"  - *Modified Price*: Plan '{mod['name']}' changed from {mod['old_price']} to {mod['new_price']}")

            # Feature details
            f_diff = eval_report.get("features_diff", {})
            if f_diff.get("added"):
                added_feats = ", ".join(f_diff["added"])
                summary_lines.append(f"  - *Added Features*: {added_feats}")
            if f_diff.get("removed"):
                removed_feats = ", ".join(f_diff["removed"])
                summary_lines.append(f"  - *Removed Features*: {removed_feats}")

        return "\n".join(summary_lines)
