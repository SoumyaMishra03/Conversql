import re

# === SCHEMA VOCABULARY ===
SCHEMA_PHRASES = [
    # DATABASES
    "asteroids", "astronauts_db", "isro_satellites_db", "natural_satellites_db",
    "rockets_db", "space_missions_db", "spacenews_db", "stars_db",

    # TABLES
    # asteroids
    "neo_reference", "close_approach", "orbit_data",

    # astronauts_db
    "personal_info", "mission_info", "mission_performance",

    # isro_satellites_db
    "basic_info", "orbital_info", "launch_info",

    # natural_satellites_db
    "satellite_identity", "satellite_physical",

    # rockets_db
    "rocket_general_info", "rocket_technical_specs",

    # space_missions_db
    "organizations", "rockets", "missions",

    # spacenews_db
    "news_articles_table", "publishing_info",

    # stars_db
    "stars",

    # COLUMNS
    "neo reference id", "name", "absolute magnitude", "est dia in km(min)", "est dia in km(max)",
    "est dia in m(min)", "est dia in m(max)", "est dia in miles(min)", "est dia in miles(max)",
    "est dia in feet(min)", "est dia in feet(max)", "close approach date", "epoch date close approach",
    "relative velocity km per sec", "relative velocity km per hr", "miles per hour",
    "miss dist.(astronomical)", "miss dist.(lunar)", "miss dist.(kilometers)", "miss dist.(miles)",
    "orbiting body", "orbit id", "orbit determination date", "orbit uncertainity",
    "minimum orbit intersection", "jupiter tisserand invariant", "epoch osculation",
    "eccentricity", "semi major axis", "inclination", "asc node longitude", "orbital period",
    "perihelion distance", "perihelion arg", "aphelion dist", "perihelion time", "mean anomaly",
    "mean motion", "equinox", "hazardous",

    "id", "number", "nationwide_number", "original_name", "sex", "year_of_birth", "nationality",
    "military_civilian", "selection", "year_of_selection", "mission_number", "total_number_of_missions",
    "occupation", "year_of_mission", "mission_title", "ascend_shuttle", "in_orbit",
    "descend_shuttle", "hours_mission", "total_hrs_sum", "field21", "eva_hrs_mission", "total_eva_hrs",

    "satellite id(fake)", "name of satellite, alternate names", "current official name of satellite",
    "country/org of un registry", "country of operator/owner", "operator/owner", "users",
    "purpose", "detailed purpose", "class of orbit", "type of orbit", "longitude of geo (degrees)",
    "perigee (km)", "apogee (km)", "inclination (degrees)", "period (minutes)",

    "launch mass (kg.)", "dry mass (kg.)", "power (watts)", "date of launch", "expected lifetime (yrs.)",
    "contractor", "country of contractor", "launch site", "launch vehicle", "cospar number",
    "norad number", "comments",

    "planet", "gm", "radius", "density", "magnitude", "albedo",

    "cmp", "wiki", "status", "liftoff_thrust", "payload_leo", "stages", "strap_ons",
    "rocket_height_m", "price_musd", "payload_gto", "fairing_diameter_m", "fairing_height_m",

    "organisation", "location", "details", "rocket_status", "price", "mission_status",

    "title", "url", "content", "postexcerpt", "author", "date",

    "star name", "distance", "mass", "luminosity"
]

def base_tokenize(text):
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    combined_tokens = []
    i = 0
    max_phrase_length = 6  
    while i < len(tokens):
        match_found = False
        for j in range(max_phrase_length, 0, -1):
            if i + j <= len(tokens):
                phrase = " ".join(tokens[i:i+j])
                if phrase in SCHEMA_PHRASES:
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
        "Give me the est dia in km(max) and name from neo_reference in asteroids.",
        "Find all astronauts with eva_hrs_mission > 10 from mission_performance in astronauts_db.",
        "What is the albedo of natural satellites orbiting Mars?",
        "List payload_leo and rocket_height_m for Falcon 9 from rockets_db.",
        "Show me news articles published by author Elon Musk in spacenews_db.",
        "What is the mission_status and organisation from missions in space_missions_db?",
        "Display star name, distance and luminosity from stars_db where distance < 50."
    ]
    
    for query in queries:
        print("Query:", query)
        print("Tokens:", tokenize(query))
        print("-" * 60)
