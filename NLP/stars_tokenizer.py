import re

# Define schema vocabulary for the stars database.
SCHEMA_PHRASES = [
    "star name",
    "constellation",
    "apparent magnitude",
    "absolute magnitude",
    "spectral type",
    "distance from earth",
    "luminosity",
    "surface temperature",
    "radius",
    "mass",
    "metallicity",
    "age",
    "binary system",
    "galactic coordinates"
]

# Convert schema phrases to lowercase for consistent matching
SCHEMA_VOCAB = set(phrase.lower() for phrase in SCHEMA_PHRASES)

def base_tokenize(text):
    """
    Basic tokenization:
    - Converts text to lowercase.
    - Extracts words using regex.
    """
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    """
    Combines consecutive tokens into multi-word schema phrases if they match
    any of the predefined schema phrases from the stars database.
    """
    combined_tokens = []
    i = 0
    max_phrase_length = 5  # Adjust phrase length as needed
    while i < len(tokens):
        match_found = False
        # Try matching longest possible phrase first
        for j in range(max_phrase_length, 0, -1):
            if i + j <= len(tokens):
                phrase = " ".join(tokens[i:i+j])
                if phrase in SCHEMA_VOCAB:
                    combined_tokens.append(phrase)
                    i += j
                    match_found = True
                    break
        if not match_found:
            combined_tokens.append(tokens[i])
            i += 1
    return combined_tokens

def tokenize(text):
    """
    Applies base tokenization followed by schema phrase recognition.
    """
    tokens = base_tokenize(text)
    tokens = combine_schema_tokens(tokens)
    return tokens

if __name__ == '__main__':
    # Example user queries related to the stars database.
    queries = [
        "Find details for star name Betelgeuse including spectral type and luminosity.",
        "List all stars in the constellation Orion with apparent magnitude below 3.",
        "Show mass, radius, and surface temperature for star name Sirius.",
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
