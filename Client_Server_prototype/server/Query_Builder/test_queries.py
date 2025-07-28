"""
Corrected schema-specific test queries for all query builders
These use actual column names from the database schema and realistic patterns
"""

# Test queries for SELECT operations using actual schema column names
SELECT_TEST_QUERIES = [
    {
        "description": "Basic SELECT all from asteroids close_approach table",
        "intent": ["SELECT_ROWS"],
        "entities": [{"type": "database", "value": "asteroids_db"}, {"type": "table", "value": "close_approach"}],
        "operators": [],
        "values": [],
        "expected_pattern": "SELECT * FROM `asteroids_db`.`close_approach`"
    },
    {
        "description": "SELECT astronaut names from personal_info",
        "intent": ["SELECT_ROWS"],
        "entities": [
            {"type": "database", "value": "astronauts_db"},
            {"type": "table", "value": "personal_info"},
            {"type": "column", "value": "name"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "SELECT `name` FROM `astronauts_db`.`personal_info`"
    },
    {
        "description": "SELECT satellites with launch mass filter",
        "intent": ["SELECT_ROWS"],
        "entities": [
            {"type": "database", "value": "isro_satellites_db"},
            {"type": "table", "value": "launch_info"},
            {"type": "column", "value": "launch mass"}
        ],
        "operators": [("launch mass", ">", "greater than")],
        "values": [{"type": "INTEGER", "value": "1000"}],
        "expected_pattern": "WHERE"
    },
    {
        "description": "COUNT total number of space missions",
        "intent": ["COUNT_ROWS"],
        "entities": [
            {"type": "database", "value": "space_missions_db"},
            {"type": "table", "value": "missions"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "SELECT COUNT(*) FROM `space_missions_db`.`missions`"
    },
    {
        "description": "AVG rocket height from technical specs",
        "intent": ["AGGREGATE_AVG"],
        "entities": [
            {"type": "database", "value": "rockets_db"},
            {"type": "table", "value": "rocket_technical_specs"},
            {"type": "column", "value": "height"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "SELECT AVG("
    },
    {
        "description": "SUM total payload capacity",
        "intent": ["AGGREGATE_SUM"],
        "entities": [
            {"type": "database", "value": "rockets_db"},
            {"type": "table", "value": "rocket_technical_specs"},
            {"type": "column", "value": "payload"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "SELECT SUM("
    },
    {
        "description": "MIN distance of stars",
        "intent": ["AGGREGATE_MIN"],
        "entities": [
            {"type": "database", "value": "stars_db"},
            {"type": "table", "value": "stars"},
            {"type": "column", "value": "distance"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "SELECT MIN("
    },
    {
        "description": "MAX luminosity of stars",
        "intent": ["AGGREGATE_MAX"],
        "entities": [
            {"type": "database", "value": "stars_db"},
            {"type": "table", "value": "stars"},
            {"type": "column", "value": "luminosity"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "SELECT MAX("
    },
    {
        "description": "Show all databases",
        "intent": ["SHOW_DATABASES"],
        "entities": [],
        "operators": [],
        "values": [],
        "expected_pattern": "SHOW DATABASES"
    },
    {
        "description": "Show tables from asteroids database",
        "intent": ["SELECT_ROWS"],
        "entities": [{"type": "database", "value": "asteroids_db"}],
        "operators": [],
        "values": [],
        "expected_pattern": "SHOW TABLES FROM `asteroids_db`"
    },
    {
        "description": "SELECT hazardous asteroids with eccentricity filter",
        "intent": ["SELECT_ROWS"],
        "entities": [
            {"type": "database", "value": "asteroids_db"},
            {"type": "table", "value": "orbit_data"},
            {"type": "column", "value": "hazardous"},
            {"type": "column", "value": "eccentricity"}
        ],
        "operators": [
            ("hazardous", "=", "equals"),
            ("eccentricity", ">", "greater than")
        ],
        "values": [
            {"type": "STRING", "value": "Y"},
            {"type": "DECIMAL", "value": "0.5"}
        ],
        "expected_pattern": "WHERE"
    },
    {
        "description": "SELECT astronauts by nationality",
        "intent": ["SELECT_ROWS"],
        "entities": [
            {"type": "database", "value": "astronauts_db"},
            {"type": "table", "value": "personal_info"},
            {"type": "column", "value": "nationality"}
        ],
        "operators": [("nationality", "=", "equals")],
        "values": [{"type": "STRING", "value": "USA"}],
        "expected_pattern": "WHERE"
    }
]

# Test queries for INSERT operations using realistic data
INSERT_TEST_QUERIES = [
    {
        "description": "INSERT new asteroid close approach data",
        "intent": ["INSERT_ROWS"],
        "entities": [
            {"type": "database", "value": "asteroids_db"},
            {"type": "table", "value": "close_approach"},
            {"type": "column", "value": "reference id"},
            {"type": "column", "value": "approach date"}
        ],
        "operators": [],
        "values": [
            {"type": "STRING", "value": "NEO-2024-001"},
            {"type": "DATE", "value": "2024-06-15"}
        ],
        "expected_pattern": "INSERT INTO `asteroids_db`.`close_approach`"
    },
    {
        "description": "INSERT new astronaut personal info",
        "intent": ["INSERT_ROWS"],
        "entities": [
            {"type": "database", "value": "astronauts_db"},
            {"type": "table", "value": "personal_info"},
            {"type": "column", "value": "name"},
            {"type": "column", "value": "nationality"}
        ],
        "operators": [],
        "values": [
            {"type": "STRING", "value": "Jane Cooper"},
            {"type": "STRING", "value": "USA"}
        ],
        "expected_pattern": "INSERT INTO `astronauts_db`.`personal_info`"
    },
    {
        "description": "INSERT new satellite launch info",
        "intent": ["INSERT_ROWS"],
        "entities": [
            {"type": "database", "value": "isro_satellites_db"},
            {"type": "table", "value": "launch_info"},
            {"type": "column", "value": "launch mass"},
            {"type": "column", "value": "launch date"}
        ],
        "operators": [],
        "values": [
            {"type": "DECIMAL", "value": "2500.0"},
            {"type": "DATE", "value": "2024-03-20"}
        ],
        "expected_pattern": "INSERT INTO `isro_satellites_db`.`launch_info`"
    },
    {
        "description": "INSERT new space mission",
        "intent": ["INSERT_ROWS"],
        "entities": [
            {"type": "database", "value": "space_missions_db"},
            {"type": "table", "value": "missions"},
            {"type": "column", "value": "organisation"},
            {"type": "column", "value": "status"}
        ],
        "operators": [],
        "values": [
            {"type": "STRING", "value": "NASA"},
            {"type": "STRING", "value": "Active"}
        ],
        "expected_pattern": "INSERT INTO `space_missions_db`.`missions`"
    },
    {
        "description": "INSERT new rocket technical specs",
        "intent": ["INSERT_ROWS"],
        "entities": [
            {"type": "database", "value": "rockets_db"},
            {"type": "table", "value": "rocket_technical_specs"},
            {"type": "column", "value": "name"},
            {"type": "column", "value": "payload"}
        ],
        "operators": [],
        "values": [
            {"type": "STRING", "value": "Falcon Heavy"},
            {"type": "INTEGER", "value": "63800"}
        ],
        "expected_pattern": "INSERT INTO `rockets_db`.`rocket_technical_specs`"
    },
    {
        "description": "INSERT new star data",
        "intent": ["INSERT_ROWS"],
        "entities": [
            {"type": "database", "value": "stars_db"},
            {"type": "table", "value": "stars"},
            {"type": "column", "value": "star name"},
            {"type": "column", "value": "distance"}
        ],
        "operators": [],
        "values": [
            {"type": "STRING", "value": "Proxima Centauri B"},
            {"type": "DECIMAL", "value": "4.24"}
        ],
        "expected_pattern": "INSERT INTO `stars_db`.`stars`"
    }
]

# Test queries for UPDATE operations using realistic scenarios
UPDATE_TEST_QUERIES = [
    {
        "description": "UPDATE asteroid hazardous status",
        "intent": ["UPDATE_ROWS"],
        "entities": [
            {"type": "database", "value": "asteroids_db"},
            {"type": "table", "value": "orbit_data"},
            {"type": "column", "value": "hazardous"},
            {"type": "column", "value": "reference id"}
        ],
        "operators": [("reference id", "=", "equals")],
        "values": [
            {"type": "STRING", "value": "Y"},
            {"type": "STRING", "value": "NEO-2024-001"}
        ],
        "expected_pattern": "UPDATE `asteroids_db`.`orbit_data` SET"
    },
    {
        "description": "UPDATE astronaut mission hours",
        "intent": ["UPDATE_ROWS"],
        "entities": [
            {"type": "database", "value": "astronauts_db"},
            {"type": "table", "value": "mission_performance"},
            {"type": "column", "value": "hours mission"},
            {"type": "column", "value": "id"}
        ],
        "operators": [("id", "=", "equals")],
        "values": [
            {"type": "DECIMAL", "value": "168.5"},
            {"type": "INTEGER", "value": "123"}
        ],
        "expected_pattern": "UPDATE `astronauts_db`.`mission_performance` SET"
    },
    {
        "description": "UPDATE satellite lifetime",
        "intent": ["UPDATE_ROWS"],
        "entities": [
            {"type": "database", "value": "isro_satellites_db"},
            {"type": "table", "value": "launch_info"},
            {"type": "column", "value": "expected lifetime"},
            {"type": "column", "value": "satellite id"}
        ],
        "operators": [("satellite id", "=", "equals")],
        "values": [
            {"type": "INTEGER", "value": "15"},
            {"type": "STRING", "value": "SAT-001"}
        ],
        "expected_pattern": "UPDATE `isro_satellites_db`.`launch_info` SET"
    },
    {
        "description": "UPDATE space mission status",
        "intent": ["UPDATE_ROWS"],
        "entities": [
            {"type": "database", "value": "space_missions_db"},
            {"type": "table", "value": "missions"},
            {"type": "column", "value": "status"},
            {"type": "column", "value": "id"}
        ],
        "operators": [("id", "=", "equals")],
        "values": [
            {"type": "STRING", "value": "Completed"},
            {"type": "INTEGER", "value": "456"}
        ],
        "expected_pattern": "UPDATE `space_missions_db`.`missions` SET"
    },
    {
        "description": "UPDATE rocket price",
        "intent": ["UPDATE_ROWS"],
        "entities": [
            {"type": "database", "value": "rockets_db"},
            {"type": "table", "value": "rocket_technical_specs"},
            {"type": "column", "value": "price"},
            {"type": "column", "value": "name"}
        ],
        "operators": [("name", "=", "equals")],
        "values": [
            {"type": "DECIMAL", "value": "95.0"},
            {"type": "STRING", "value": "Falcon Heavy"}
        ],
        "expected_pattern": "UPDATE `rockets_db`.`rocket_technical_specs` SET"
    }
]

# Test queries for DELETE operations using realistic scenarios
DELETE_TEST_QUERIES = [
    {
        "description": "DELETE old asteroid close approach data",
        "intent": ["DELETE_ROWS"],
        "entities": [
            {"type": "database", "value": "asteroids_db"},
            {"type": "table", "value": "close_approach"},
            {"type": "column", "value": "approach date"}
        ],
        "operators": [("approach date", "<", "less than")],
        "values": [{"type": "DATE", "value": "2020-01-01"}],
        "expected_pattern": "DELETE FROM `asteroids_db`.`close_approach`"
    },
    {
        "description": "DELETE astronaut by specific ID",
        "intent": ["DELETE_ROWS"],
        "entities": [
            {"type": "database", "value": "astronauts_db"},
            {"type": "table", "value": "personal_info"},
            {"type": "column", "value": "id"}
        ],
        "operators": [("id", "=", "equals")],
        "values": [{"type": "INTEGER", "value": "999"}],
        "expected_pattern": "DELETE FROM `astronauts_db`.`personal_info`"
    },
    {
        "description": "DELETE satellites with expired lifetime",
        "intent": ["DELETE_ROWS"],
        "entities": [
            {"type": "database", "value": "isro_satellites_db"},
            {"type": "table", "value": "launch_info"},
            {"type": "column", "value": "expected lifetime"}
        ],
        "operators": [("expected lifetime", "<", "less than")],
        "values": [{"type": "INTEGER", "value": "5"}],
        "expected_pattern": "DELETE FROM `isro_satellites_db`.`launch_info`"
    },
    {
        "description": "DELETE cancelled space missions",
        "intent": ["DELETE_ROWS"],
        "entities": [
            {"type": "database", "value": "space_missions_db"},
            {"type": "table", "value": "missions"},
            {"type": "column", "value": "status"}
        ],
        "operators": [("status", "=", "equals")],
        "values": [{"type": "STRING", "value": "Cancelled"}],
        "expected_pattern": "DELETE FROM `space_missions_db`.`missions`"
    },
    {
        "description": "DELETE inactive rocket entries",
        "intent": ["DELETE_ROWS"],
        "entities": [
            {"type": "database", "value": "rockets_db"},
            {"type": "table", "value": "rocket_general_info"},
            {"type": "column", "value": "status"}
        ],
        "operators": [("status", "=", "equals")],
        "values": [{"type": "STRING", "value": "Retired"}],
        "expected_pattern": "DELETE FROM `rockets_db`.`rocket_general_info`"
    }
]

# Test queries for DROP operations - these are straightforward
DROP_TEST_QUERIES = [
    {
        "description": "DROP asteroids database",
        "intent": ["DROP_DATABASE"],
        "entities": [{"type": "database", "value": "asteroids_db"}],
        "operators": [],
        "values": [],
        "expected_pattern": "DROP DATABASE IF EXISTS `asteroids_db`"
    },
    {
        "description": "DROP close_approach table",
        "intent": ["DROP_TABLE"],
        "entities": [
            {"type": "database", "value": "asteroids_db"},
            {"type": "table", "value": "close_approach"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "DROP TABLE IF EXISTS `asteroids_db`.`close_approach`"
    },
    {
        "description": "TRUNCATE mission_performance table",
        "intent": ["TRUNCATE_TABLE"],
        "entities": [
            {"type": "database", "value": "astronauts_db"},
            {"type": "table", "value": "mission_performance"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "TRUNCATE TABLE `astronauts_db`.`mission_performance`"
    },
    {
        "description": "DROP orbital_info table from satellites database",
        "intent": ["DROP_TABLE"],
        "entities": [
            {"type": "database", "value": "isro_satellites_db"},
            {"type": "table", "value": "orbital_info"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "DROP TABLE IF EXISTS `isro_satellites_db`.`orbital_info`"
    },
    {
        "description": "DROP stars database entirely",
        "intent": ["DROP_DATABASE"],
        "entities": [{"type": "database", "value": "stars_db"}],
        "operators": [],
        "values": [],
        "expected_pattern": "DROP DATABASE IF EXISTS `stars_db`"
    }
]

# Combined test queries dictionary
ALL_TEST_QUERIES = {
    "SELECT": SELECT_TEST_QUERIES,
    "INSERT": INSERT_TEST_QUERIES,
    "UPDATE": UPDATE_TEST_QUERIES,
    "DELETE": DELETE_TEST_QUERIES,
    "DROP": DROP_TEST_QUERIES
}
