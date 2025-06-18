import re

# Define a schema vocabulary for the isro_satellites database.
# You can add more phrases as needed.
SCHEMA_PHRASES = [
    "satellite id(fake)",
    "basic info",
    "launch info",
    "orbital info"
]

# Preprocess the vocabulary: lowercase for consistent matching.
SCHEMA_VOCAB = set(phrase.lower() for phrase in SCHEMA_PHRASES)

def base_tokenize(text):
    """
    Basic tokenization:
      - Converts text to lowercase.
      - Extracts words using a regular expression.
    """
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    """
    Combine consecutive tokens into multi-word schema phrases if they match
    any of the phrases in the schema vocabulary.

    This function scans through the token list and attempts to match sequences
    (up to a maximum length) with terms in SCHEMA_VOCAB.
    """
    combined_tokens = []
    i = 0
    max_phrase_length = 5  # Adjust maximum phrase length as needed
    while i < len(tokens):
        match_found = False
        # Try from longest to shortest sequence.
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
    Tokenizes the input text with base tokenization followed by
    combining tokens that match isro_satellites schema names.
    """
    tokens = base_tokenize(text)
    tokens = combine_schema_tokens(tokens)
    return tokens

if __name__ == '__main__':
    # Example queries that might be posed to the isro_satellites database.
    queries = [
        "Show me details from basic info where satellite id(fake) is 101.",
        "List launch info for satellite id(fake) 202.",
        "What does the orbital info say about satellite id(fake) 303?"
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
