import re

schema_phrases = [
    # Table names
    "rocket general info",
    "rocket technical specs",

    # Shared column
    "name",

    # rocket_general_info
    "cmp",
    "wiki",
    "status",

    # rocket_technical_specs
    "liftoff thrust",
    "payload leo",
    "stages",
    "strap ons",
    "rocket height m",
    "price musd",
    "payload gto",
    "fairing diameter m",
    "fairing height m"
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
        "Find the name, cmp and wiki for rocket Falcon Heavy.",
        "List liftoff thrust and payload leo where stages are 2.",
        "Show price musd and fairing diameter m for any rocket with payload gto over 5000."
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
