import re

schema_phrases = [
    # Table names
    "satellite identity",
    "satellite physical",

    # Shared columns
    "planet",
    "name",

    # Additional columns from satellite_physical
    "gm",
    "radius",
    "density",
    "magnitude",
    "albedo"
]

def base_tokenize(text):
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    combined_tokens = []
    i = 0
    max_phrase_length = 4
    while i < len(tokens):
        match_found = False
        for j in range(max_phrase_length, 0, -1):
            if i + j <= len(tokens):
                phrase = " ".join(tokens[i:i+j])
                if phrase in schema_phrases:
                    combined_tokens.append(phrase)
                    i += j
                    match_found = True
                    break
        if not match_found:
            combined_tokens.append(tokens[i])
            i += 1
    return combined_tokens

def tokenize(text):
    tokens = base_tokenize(text)
    tokens = combine_schema_tokens(tokens)
    return tokens

if __name__ == '__main__':
    queries = [
        "Find the gm and radius of satellite name Titan.",
        "What is the albedo of the natural satellite orbiting Jupiter?",
        "Show me the name and planet from satellite identity for Europa.",
        "List magnitude and density of any moon with radius over 2000."
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
