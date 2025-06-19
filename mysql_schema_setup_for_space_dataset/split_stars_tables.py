import re

schema_phrases = [
    "star name",
    "distance",
    "mass",
    "radius",
    "luminosity",
    "stars"  
]

def base_tokenize(text):
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    combined_tokens = []
    i = 0
    max_phrase_length = 3
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
        "Find details for star name Betelgeuse including mass and luminosity.",
        "Show all stars with radius above 2 and distance below 50.",
        "Give me the radius and star name for the brightest stars."
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
