import re

schema_phrases = [
    # Table names
    "personal info",
    "mission info",
    "mission performance",

    # Shared column
    "id",

    # personal_info
    "number",
    "nationwide number",
    "name",
    "original name",
    "sex",
    "year of birth",
    "nationality",
    "military civilian",

    # mission_info
    "selection",
    "year of selection",
    "mission number",
    "total number of missions",
    "occupation",
    "year of mission",
    "mission title",

    # mission_performance
    "ascend shuttle",
    "in orbit",
    "descend shuttle",
    "hours mission",
    "total hrs sum",
    "field21",
    "eva hrs mission",
    "total eva hrs"
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
        "Find details about id 1001 including nationality and total hrs sum.",
        "List all mission info where mission performance is above average.",
        "Show mission performance data for id 2003.",
        "Give me the original name and occupation from personal info.",
        "How many spacewalks based on total eva hrs in mission performance?"
    ]
    
    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
