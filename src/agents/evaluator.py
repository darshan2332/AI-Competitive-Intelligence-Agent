from typing import Dict, Any, Optional
from src.tools.diff_tool import DiffTool
from src.memory.db_client import DBClient
from src.utils.logger import logger

class Evaluator:
    def __init__(self, db_client: DBClient):
        self.db_client = db_client
        self.diff_tool = DiffTool()

    def evaluate(self, competitor_id: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates structure and computes the diff against database history.
        """
        logger.info(f"Evaluating data for competitor: {competitor_id}")
        
        # 1. Structural validation check
        is_valid = self._validate_schema(new_data)
        confidence = 1.0 if is_valid else 0.0

        if not is_valid:
            logger.warning(f"Validation failed for competitor data structure: {competitor_id}")
            return {
                "competitor_id": competitor_id,
                "is_valid": False,
                "confidence": 0.0,
                "pricing_diff": {},
                "features_diff": {},
                "has_changes": False
            }

        # 2. Retrieve history snapshot
        history = self.db_client.get_latest_snapshot(competitor_id)

        pricing_diff = {}
        features_diff = {}
        has_changes = False

        if history:
            logger.info(f"Found historical snapshot from {history.get('timestamp')}. Computing diffs.")
            pricing_diff = self.diff_tool.compute_pricing_diff(
                history.get("pricing_data", []), 
                new_data.get("plans", [])
            )
            features_diff = self.diff_tool.compute_features_diff(
                history.get("features_data", []), 
                new_data.get("features", [])
            )
            has_changes = pricing_diff.get("has_changes", False) or features_diff.get("has_changes", False)
        else:
            logger.info("No historical snapshot found. Marking as baseline snapshot.")
            has_changes = True # Baseline snapshot is technically a change (creation)

        return {
            "competitor_id": competitor_id,
            "is_valid": True,
            "confidence": confidence,
            "pricing_diff": pricing_diff,
            "features_diff": features_diff,
            "has_changes": has_changes,
            "is_baseline": history is None
        }

    def _validate_schema(self, data: Dict[str, Any]) -> bool:
        """
        Confirms the extracted dictionary adheres to required keys and types.
        """
        if not isinstance(data, dict):
            return False
        if "plans" not in data or "features" not in data:
            return False
        if not isinstance(data["plans"], list) or not isinstance(data["features"], list):
            return False
        
        # Validate plan inner dicts
        for plan in data["plans"]:
            if not isinstance(plan, dict):
                return False
            if "name" not in plan or "price" not in plan:
                return False
                
        return True
