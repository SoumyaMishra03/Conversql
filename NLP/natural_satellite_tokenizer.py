import re

# Define a vocabulary containing schema phrases for the natural_satellite database.
SCHEMA_PHRASES = [
    "satellite name",
    "planet",
    "orbital period",
    "mean radius",
    "mass",
    "surface gravity"
]

# Create a lowercased set out of the schema phrases for matching
SCHEMA_VOCAB = set(phrase.lower() for phrase in SCHEMA_PHRASES)

def base_tokenize(text):
    """
    Tokenize the input text using basic rules:
    - Lowercase conversion.
    - Extract words using regex.
    """
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    """
    Combine consecutive tokens into multi-word schema phrases if they match phrases in SCHEMA_VOCAB.
    
    This function tests contiguous token sequences (up to a given maximum length) and combines them
    if the resulting phrase appears in our schema vocabulary.
    """
    combined_tokens = []
    i = 0
    # We'll try to combine up to 4 consecutive tokens (adjust if necessary)
    max_phrase_length = 4
    while i < len(tokens):
        match_found = False
        # Try to form phrases from longest possible to single token
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
    Perform base tokenization followed by schema phrase combination.
    """
    tokens = base_tokenize(text)
    tokens = combine_schema_tokens(tokens)
    return tokens

if __name__ == '__main__':
    # Example user queries regarding the natural_satellite database.
    queries = [
        "Find the mass and orbital period of satellite name Titan.",
        "What is the surface gravity of the natural satellite orbiting Jupiter?",
        "Show me the mean radius and mass for satellite name Europa."
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)