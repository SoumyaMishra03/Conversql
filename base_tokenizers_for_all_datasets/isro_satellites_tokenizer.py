import re

schema_phrases = [
    # Table names
    "basic info",
    "orbital info",
    "launch info",

    # Shared column
    "satellite id(fake)",

    # basic_info 
    "name of satellite alternate names",
    "current official name of satellite",
    "country/org of un registry",
    "country of operator/owner",
    "operator/owner",
    "users",
    "purpose",
    "detailed purpose",

    # orbital_info
    "class of orbit",
    "type of orbit",
    "longitude of geo (degrees)",
    "perigee (km)",
    "apogee (km)",
    "eccentricity",
    "inclination (degrees)",
    "period (minutes)",

    # launch_info 
    "launch mass (kg)",
    "dry mass (kg)",
    "power (watts)",
    "date of launch",
    "expected lifetime (yrs)",
    "contractor",
    "country of contractor",
    "launch site",
    "launch vehicle",
    "cospar number",
    "norad number",
    "comments"
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
                phrase = " ".join(tokens[i:i + j])
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
        "Show me details from basic info where satellite id(fake) is 101.",
        "List launch info for satellite id(fake) 202.",
        "What does the orbital info say about satellite id(fake) 303?",
        "Give me the launch mass (kg) and power (watts) of satellite id(fake) 404.",
        "Which satellite has apogee (km) above 35000 and period (minutes) more than 500?",
        "Fetch all with country of contractor as India and launch site in Sriharikota."
    ]

    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
