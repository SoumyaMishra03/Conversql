import re
from typing import List, Tuple

# Regex patterns
FLOAT_PATTERN = r"\b-?\d+\.\d+\b"
INTEGER_PATTERN = r"\b-?\d+\b"
BOOLEAN_PATTERN = r"\b(?:true|false|yes|no)\b"
STRING_PATTERN = r"'([^']*)'|\"([^\"]*)\""
DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?\b"
]

# Pattern for unquoted string values (proper nouns, names, etc.)
UNQUOTED_STRING_PATTERNS = [
    # Proper nouns (capitalized words) - common for names like "Apophis", "NASA", etc.
    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
    
    # Alphanumeric identifiers (like satellite codes, mission names)
    r'\b[A-Z]{2,}[-_]?\d*[A-Z]*\b',  # GSAT-30, ISS, etc.
    
    # Mixed case identifiers
    r'\b[A-Za-z]+\d+[A-Za-z]*\b',  # Falcon9, Atlas5, etc.
    
    # Simple words that could be values (3+ characters)
    r'\b[a-zA-Z]{3,}\b'
]

VALUE_REGEX = re.compile(
    "(" + "|".join(
        [FLOAT_PATTERN, INTEGER_PATTERN, BOOLEAN_PATTERN, STRING_PATTERN] + DATE_PATTERNS
    ) + ")",
    flags=re.IGNORECASE
)

def is_likely_value_context(text: str, match_start: int, match_end: int) -> bool:
    """
    Determine if a word appears in a context where it's likely to be a value
    """
    # Get surrounding context (20 chars before and after)
    context_start = max(0, match_start - 20)
    context_end = min(len(text), match_end + 20)
    
    # Value indicators - words that suggest the following word is a value
    value_indicators = [
        'name', 'called', 'named', 'title', 'with', 'values', 'value',
        'equals', 'equal', '=', 'set', 'to', 'as', 'is'
    ]
    
    # Check if any value indicator appears before our match
    before_match = text[context_start:match_start].lower()
    for indicator in value_indicators:
        if indicator in before_match:
            return True
    
    # Check for patterns like "name Apophis", "called Jupiter", etc.
    word_before_patterns = [
        r'\b(?:name|called|named|title)\s+$',
        r'\bwith\s+(?:name\s+)?$',
        r'\bvalues?\s+$',
        r'\bequals?\s+$',
        r'\bset\s+\w+\s+(?:to\s+)?$'
    ]
    
    for pattern in word_before_patterns:
        if re.search(pattern, before_match):
            return True
    
    return False

def value_entity_recognizer(text: str) -> List[Tuple[str, str, int, int]]:
    results: List[Tuple[str, str, int, int]] = []
    
    # First pass: Find quoted strings, numbers, dates, booleans
    for m in VALUE_REGEX.finditer(text):
        raw = m.group(0)
        lo, hi = m.span()
        raw_clean = raw.strip()
        
        if re.fullmatch(FLOAT_PATTERN, raw_clean):
            typ = "FLOAT"
        elif re.fullmatch(INTEGER_PATTERN, raw_clean):
            typ = "INTEGER"
        elif re.fullmatch(BOOLEAN_PATTERN, raw_clean, flags=re.IGNORECASE):
            typ = "BOOLEAN"
        elif re.fullmatch(STRING_PATTERN, raw_clean):
            typ = "STRING"
            raw_clean = raw_clean[1:-1]  # Remove quotes
        elif any(re.fullmatch(pat, raw_clean, flags=re.IGNORECASE) for pat in DATE_PATTERNS):
            typ = "DATE"
        else:
            continue
        
        results.append((typ, raw_clean, lo, hi))
    
    # Second pass: Find unquoted string values (names, identifiers, etc.)
    for pattern in UNQUOTED_STRING_PATTERNS:
        for match in re.finditer(pattern, text):
            word = match.group(0)
            lo, hi = match.span()
            
            # Skip if it's too short (likely not a meaningful value)
            if len(word) < 2:
                continue
            
            # Check if this word appears in a value context
            if is_likely_value_context(text, lo, hi):
                # Avoid duplicates from first pass
                if not any(existing_lo <= lo < existing_hi or existing_lo < hi <= existing_hi
                          for _, _, existing_lo, existing_hi in results):
                    results.append(("STRING", word, lo, hi))
    
    # Sort results by position in text
    results.sort(key=lambda x: x[2])
    
    return results

# Enhanced function for INSERT query context
def extract_insert_values(text: str, columns: List[str]) -> List[Tuple[str, str, int, int]]:
    """
    Enhanced value extraction specifically for INSERT queries
    Tries to match values to columns in order
    """
    all_values = value_entity_recognizer(text)
    
    # For INSERT queries, try to be more aggressive about finding string values
    # Look for patterns like "name Apophis", "title Mars Mission", etc.
    insert_value_patterns = [
        # Pattern: "name Apophis" -> extract "Apophis"
        r'\b(?:name|title|called|named)\s+([A-Za-z][A-Za-z0-9\s\-_]*?)(?:\s+(?:and|with|magnitude|mass|distance|radius)\b|$)',
        
        # Pattern: "with Apophis" -> extract "Apophis" 
        r'\bwith\s+([A-Za-z][A-Za-z0-9\s\-_]*?)(?:\s+(?:and|magnitude|mass|distance|radius)\b|$)',
        
        # Pattern: "values Apophis and 19.7" -> extract "Apophis"
        r'\bvalues?\s+([A-Za-z][A-Za-z0-9\s\-_]*?)(?:\s+(?:and|with)\b|$)',
        
        # Pattern: "Apophis and magnitude" -> extract "Apophis"
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:and|with)\s+(?:magnitude|mass|distance|radius|absolute)',
    ]
    
    for pattern in insert_value_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group(1).strip()
            if (len(value) > 1 and
                not any(existing_value == value for _, existing_value, _, _ in all_values)):
                
                all_values.append(("STRING", value, match.start(1), match.end(1)))
    
    # Sort by position and return
    all_values.sort(key=lambda x: x[2])
    return all_values

# Print debug info
if __name__ == "__main__":
    print("Value Entity Recognizer - Simplified version without schema filtering")
