import re

# Define a schema vocabulary for the asteroids database.
SCHEMA_PHRASES = [
    "neo reference id",
    "name",
    "absolute magnitude",
    "est dia in km(min)",
    "est dia in km(max)",
    "est dia in m(min)",
    "est dia in m(max)",
    "est dia in miles(min)",
    "est dia in miles(max)",
    "est dia in feet(min)",
    "est dia in feet(max)",
    "close approach date",
    "epoch date close approach",
    "relative velocity km per sec",
    "relative velocity km per hr",
    "miles per hour",
    "miss dist.(astronomical)",
    "miss dist.(lunar)",
    "miss dist.(kilometers)",
    "miss dist.(miles)",
    "orbiting body",
    "orbit id",
    "orbit determination date",
    "orbit uncertainity",
    "minimum orbit intersection",
    "jupiter tisserand invariant",
    "epoch osculation",
    "eccentricity",
    "semi major axis",
    "inclination",
    "asc node longitude",
    "orbital period",
    "perihelion distance",
    "perihelion arg",
    "aphelion dist",
    "perihelion time",
    "mean anomaly",
    "mean motion",
    "equinox",
    "hazardous"
]

# Convert schema phrases to lowercase for consistency
SCHEMA_VOCAB = set(phrase.lower() for phrase in SCHEMA_PHRASES)

def base_tokenize(text):
    """
    Basic tokenization:
    - Lowercases the text.
    - Extracts words using regex.
    """
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    """
    Combines consecutive tokens if they match schema phrases from the asteroids database.
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
    # Example user queries related to the asteroids database.
    queries = [
        "Find the neo reference id and absolute magnitude for asteroid Apollo.",
        "What is the close approach date and relative velocity km per sec of asteroid 2023 FK?",
        "List orbital period, eccentricity, and mean anomaly for all known hazardous asteroids.",
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
