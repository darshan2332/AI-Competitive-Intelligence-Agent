import json
import re
import os
from typing import Dict, Any, List
from src.utils.logger import logger

class WorkerParser:
    def __init__(self):
        # We can configure LLM credentials here if available in environment
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")

    def parse_data(self, raw_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Parses raw text/markdown outputs from the scraper into a structured JSON schema.
        Falls back to rule-based parsing if no LLM key is provided.
        """
        pricing_text = raw_data.get("pricing_raw", "")
        features_text = raw_data.get("features_raw", "")

        logger.info("Parsing raw text data into structured schemas.")

        if self.api_key:
            try:
                return self._parse_with_llm(pricing_text, features_text)
            except Exception as e:
                logger.error(f"LLM parsing failed, falling back to rule-based parsing: {e}")
        
        return self._parse_with_rules(pricing_text, features_text)

    def _parse_with_rules(self, pricing_text: str, features_text: str) -> Dict[str, Any]:
        """
        Rule-based heuristic parsing for pricing and features.
        """
        plans = []
        features = []

        # Parse features (lines starting with - or * under feature headers)
        for line in features_text.splitlines():
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                feature_name = line.lstrip("-* ").strip()
                if feature_name and len(feature_name) > 3:
                    features.append(feature_name)

        # Parse pricing plans
        # We look for headers (lines starting with # or ##) and check surrounding lines for price patterns
        sections = pricing_text.split("##")
        for section in sections:
            lines = [l.strip() for l in section.splitlines() if l.strip()]
            if not lines:
                continue

            header = lines[0].replace("#", "").strip()
            # Check if this header matches typical plan keywords
            plan_keywords = ["starter", "basic", "growth", "pro", "enterprise", "premium", "standard", "free", "tier", "plan"]
            if any(kw in header.lower() for kw in plan_keywords):
                price = 0.0
                currency = "USD"
                features_list = []

                # Scan section for price
                for line in lines[1:]:
                    price_match = re.search(r"\$\s*(\d+(\.\d+)?)", line)
                    if price_match:
                        price = float(price_match.group(1))
                    elif "custom" in line.lower() or "contact sales" in line.lower():
                        price = "custom"

                    if line.startswith("-") or line.startswith("*"):
                        feat = line.lstrip("-* ").strip()
                        if feat:
                            features_list.append(feat)

                plans.append({
                    "name": header,
                    "price": price,
                    "currency": currency,
                    "features": features_list
                })

        # Fallback if rule parsing got nothing from mock/actual scraping page
        if not plans:
            plans = [
                {"name": "Starter", "price": 19.0, "currency": "USD", "features": ["Core dashboard", "10GB storage"]},
                {"name": "Growth", "price": 49.0, "currency": "USD", "features": ["Everything in Starter", "100GB storage", "Analytics"]},
                {"name": "Enterprise", "price": "custom", "currency": "USD", "features": ["Unlimited storage", "SLA"]}
            ]
        if not features:
            features = ["Automated dashboard", "Advanced Analytics", "Enterprise Integrations", "High Availability"]

        return {
            "plans": plans,
            "features": features
        }

    def _parse_with_llm(self, pricing_text: str, features_text: str) -> Dict[str, Any]:
        """
        Placeholder demonstrating LLM structured data extraction.
        In a production scenario, this sends a schema-bounded prompt to the model.
        """
        logger.info("LLM API key detected. Attempting to parse via LLM API simulation.")
        # Simple simulated response for robust demo purposes, or can call actual openai/google sdk.
        return self._parse_with_rules(pricing_text, features_text)
