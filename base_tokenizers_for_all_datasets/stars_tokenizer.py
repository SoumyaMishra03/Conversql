import re


schema_phrases= [
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

def base_tokenize(text):
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    combined_tokens = []
    i = 0
    max_phrase_length = 5 
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
        "Find details for star name Betelgeuse including spectral type and luminosity.",
        "List all stars in the constellation Orion with apparent magnitude below 3.",
        "Show mass, radius, and surface temperature for star name Sirius.",
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
