from typing import Dict, Any, List

class DiffTool:
    @staticmethod
    def compute_pricing_diff(old_plans: List[Dict[str, Any]], new_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compares two lists of pricing plan dictionaries.
        Each plan is expected to have 'name', 'price', and optional 'currency' keys.
        """
        old_map = {p["name"].lower(): p for p in old_plans if "name" in p}
        new_map = {p["name"].lower(): p for p in new_plans if "name" in p}

        added = []
        removed = []
        modified = []

        for name, plan in new_map.items():
            if name not in old_map:
                added.append(plan)
            else:
                old_plan = old_map[name]
                price_changed = old_plan.get("price") != plan.get("price")
                currency_changed = old_plan.get("currency") != plan.get("currency")
                
                if price_changed or currency_changed:
                    modified.append({
                        "name": plan["name"],
                        "old_price": old_plan.get("price"),
                        "new_price": plan.get("price"),
                        "old_currency": old_plan.get("currency"),
                        "new_currency": plan.get("currency")
                    })

        for name, plan in old_map.items():
            if name not in new_map:
                removed.append(plan)

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "has_changes": bool(added or removed or modified)
        }

    @staticmethod
    def compute_features_diff(old_features: List[str], new_features: List[str]) -> Dict[str, Any]:
        """
        Compares list of features.
        """
        old_set = set(f.strip().lower() for f in old_features)
        new_set = set(f.strip().lower() for f in new_features)

        # Map back to original case if possible
        old_orig = {f.strip().lower(): f for f in old_features}
        new_orig = {f.strip().lower(): f for f in new_features}

        added = [new_orig[f] for f in (new_set - old_set)]
        removed = [old_orig[f] for f in (old_set - new_set)]

        return {
            "added": added,
            "removed": removed,
            "has_changes": bool(added or removed)
        }
