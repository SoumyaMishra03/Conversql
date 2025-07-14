import os
import json
import re
from typing import List

class IntentRecognizer:
    def __init__(self, json_file: str = None):
        if json_file is None:
            base_dir = os.path.dirname(__file__)
            json_file = os.path.join(base_dir, "json", "intent.json")
        with open(json_file, "r") as f:
            patterns_dict = json.load(f)
        self.patterns = []
        for intent, phrases in patterns_dict.items():
            for phrase in phrases:
                pattern = re.compile(rf"\b({phrase})\b", re.IGNORECASE)
                self.patterns.append((pattern, intent))

    def predict_from_tokens(self, tokens: List[str]) -> List[str]:
        text = " ".join(tokens).lower()
        found_intents = set()
        for regex, intent in self.patterns:
            if regex.search(text):
                found_intents.add(intent)
        if not found_intents:
            found_intents.add("SELECT_ROWS")
        return sorted(found_intents)
