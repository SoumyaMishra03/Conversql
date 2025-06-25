# intent_recognizer.py

import re
from typing import List

# Patterns for each intent category
INTENT_PATTERNS = [
    (r'\b(count|how many|number of|total number of)\b',       'COUNT_ROWS'),
    (r'\b(sum of|total sum|add up|aggregate)\b',              'AGGREGATE_SUM'),
    (r'\b(average|mean of|avg)\b',                             'AGGREGATE_AVG'),
    (r'\b(min|max|highest|lowest|minimum|maximum)\b',         'AGGREGATE_MINMAX'),
    (r'\b(list|show|display|give|tell me|find|which)\b',      'SELECT_ROWS'),
    (r'.*',                                                    'SELECT_ROWS'),
]

class IntentRecognizer:
    """
    Rule-based intent recognizer that matches regex patterns 
    against the final token list from the tokenizer.
    """
    def __init__(self, patterns: List = INTENT_PATTERNS):
        self.patterns = [
            (re.compile(pat, re.IGNORECASE), intent)
            for pat, intent in patterns
        ]

    def predict_from_tokens(self, tokens: List[str]) -> str:
        """
        Join final tokens and run regex patterns to determine intent.
        """
        text = " ".join(tokens)
        for regex, intent in self.patterns:
            if regex.search(text):
                return intent
        return 'SELECT_ROWS'
