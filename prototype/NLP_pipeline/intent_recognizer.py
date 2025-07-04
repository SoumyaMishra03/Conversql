import re
from typing import List

INTENT_PATTERNS = [
    (r'\b(count|how many|number of|total number of)\b',                   'COUNT_ROWS'),
    (r'\b(sum of|total sum|add up|total of|combined)\b',                  'AGGREGATE_SUM'),
    (r'\b(average|mean of|avg)\b',                                        'AGGREGATE_AVG'),
    (r'\b(min|max|highest|lowest|minimum|maximum|smallest|largest)\b',    'AGGREGATE_MINMAX'),
    (r'\b(top|most|least|best|first \d+|last \d+)\b',                     'ORDER_BY'),
    (r'\b(first|top|last)\s+\d+',                                         'LIMIT'),
    (r'\b(list|show|display|give|tell me|find|fetch|get|which|what)\b',   'SELECT_ROWS'),
    (r'\b(describe|structure of|schema of|explain|definition of)\b',      'DESCRIPTION'),
]

class IntentRecognizer:
    def __init__(self, patterns: List = INTENT_PATTERNS):
        self.patterns = [
            (re.compile(pat, re.IGNORECASE), intent)
            for pat, intent in patterns
        ]

    def predict_from_tokens(self, tokens: List[str]) -> List[str]:
        text = " ".join(tokens).lower()
        found_intents = set()
        for regex, intent in self.patterns:
            if regex.search(text):
                found_intents.add(intent)
        if not found_intents:
            found_intents.add("SELECT_ROWS")
        return sorted(found_intents)
