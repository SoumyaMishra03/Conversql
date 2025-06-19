import re

schema_phrases= [
    # Table names
    "organizations",
    "rockets",
    "missions",

    # Common column
    "organisation",

    # organizations table
    "location",

    # rockets table
    "details",
    "rocket_status",
    "price",

    # missions table
    "mission_status",

    # id column
    "id"
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
        "Find the id and rocket_status for Falcon 9 in rockets.",
        "List all missions where mission_status is success.",
        "Show organisation and location from organizations table.",
        "What is the price of the rocket with the highest details?"
    ]

    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
