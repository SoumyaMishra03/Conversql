import re
from typing import List

INTENT_PATTERNS = [
    # English patterns
    (r'\b(count|how many|number of|total number of)\b',                    'COUNT_ROWS'),
    (r'\b(sum of|total sum|add up|total of|combined|sum|total|overall|addition)\b', 'AGGREGATE_SUM'),
    (r'\b(average|mean of|avg)\b',                                         'AGGREGATE_AVG'),
    (r'\b(min|lowest|minimum|smallest)\b',                                 'AGGREGATE_MIN'),
    (r'\b(max|highest|maximum|largest)\b',                                 'AGGREGATE_MAX'),
    (r'\b(top|most|least|best|first \d+|last \d+)\b',                      'ORDER_BY'),
    (r'\b(first|top|last)\s+\d+',                                          'LIMIT'),
    (r'\b(list|show|display|give|tell me|find|fetch|get|which|what)\b',    'SELECT_ROWS'),
    (r'\b(describe|structure of|schema of|explain|definition of)\b',       'DESCRIPTION'),

    # Hindi patterns
    (r'\b(कितनी संख्या|कितने लोग|कितनी बार|कितनी प्रविष्टियाँ|कितनी एंट्री)\b', 'COUNT_ROWS'),
    (r'\b(कुल जोड़|कुल योग|कुल मिलाकर|सभी जोड़ो|टोटल)\b',                     'AGGREGATE_SUM'),
    (r'\b(औसत|माध्य|मीन|मध्य मान|मध्यम)\b',                                  'AGGREGATE_AVG'),
    (r'\b(सबसे कम|न्यूनतम|नीचा|छोटा)\b',                                      'AGGREGATE_MIN'),
    (r'\b(सबसे ज्यादा|सबसे बड़ा|अधिकतम|ऊँचा|बड़ा)\b',                           'AGGREGATE_MAX'),
    (r'\b(टॉप|सबसे अच्छे|सबसे बुरे|पहले \d+|अंतिम \d+)\b',                     'ORDER_BY'),
    (r'\b(पहले|टॉप|अंतिम)\s*\d+',                                             'LIMIT'),
    (r'\b(सूची|दिखाओ|प्रदर्शित|दे दो|बताओ|खोजो|निकालो|लाओ|कौन सा|क्या)\b',    'SELECT_ROWS'),
    (r'\b(विवरण|संरचना|स्कीमा|परिभाषा|समझाओ)\b',                              'DESCRIPTION'),
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
