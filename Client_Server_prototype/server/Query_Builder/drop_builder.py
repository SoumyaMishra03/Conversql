from NLP_pipeline.tokenizer_stanza import SCHEMA_MAP

class DropQueryBuilder:
    def normalize_for_lookup(self, text):
        """Normalize text for schema lookups - handles spaces and case"""
        return text.lower().strip()

    def resolve_schema_context(self, schema_entities):
        """Enhanced schema resolution using the SCHEMA_MAP structure"""
        database = None
        table = None
        resolved_entities = []
        
        # Get all mapping dictionaries
        table_to_db = SCHEMA_MAP.get("table_to_db", {})
        
        # First pass: collect explicit entities
        for entity in schema_entities:
            if entity['type'] == 'database' and database is None:
                database = self.normalize_for_lookup(entity['value'])
            elif entity['type'] == 'table' and table is None:
                table = self.normalize_for_lookup(entity['value'])
        
        # Second pass: resolve missing context using mappings
        if table and not database:
            database = table_to_db.get(table)
            if database:
                resolved_entities.append(f"Resolved database '{database}' from table '{table}'")
        
        return database, table, resolved_entities

    def build_query(self, intent, schema_entities, operators, values):
        """Build DROP/TRUNCATE query"""
        database, table, resolved_entities = self.resolve_schema_context(schema_entities)
        
        print(f"[DEBUG] Building DROP: intent={intent}, db={database}, table={table}")
        
        if "DROP_DATABASE" in intent:
            if not database:
                return "ERROR: DROP DATABASE requires a database name", None
            return f"DROP DATABASE IF EXISTS `{database}`;", database
        
        elif "DROP_TABLE" in intent:
            if not table:
                return "ERROR: DROP TABLE requires a table name", None
            
            if database:
                full_table = f"`{database}`.`{table}`"
            else:
                full_table = f"`{table}`"
            
            return f"DROP TABLE IF EXISTS {full_table};", database
        
        elif "TRUNCATE_TABLE" in intent:
            if not table:
                return "ERROR: TRUNCATE TABLE requires a table name", None
            
            if database:
                full_table = f"`{database}`.`{table}`"
            else:
                full_table = f"`{table}`"
            
            return f"TRUNCATE TABLE {full_table};", database
        
        else:
            return "ERROR: Unknown DROP operation", None

# Test queries for DROP operations
DROP_TEST_QUERIES = [
    {
        "description": "DROP DATABASE",
        "intent": ["DROP_DATABASE"],
        "entities": [{"type": "database", "value": "test_db"}],
        "operators": [],
        "values": [],
        "expected_pattern": "DROP DATABASE IF EXISTS `test_db`"
    },
    {
        "description": "DROP TABLE",
        "intent": ["DROP_TABLE"],
        "entities": [
            {"type": "database", "value": "company_db"},
            {"type": "table", "value": "temp_users"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "DROP TABLE IF EXISTS `company_db`.`temp_users`"
    },
    {
        "description": "TRUNCATE TABLE",
        "intent": ["TRUNCATE_TABLE"],
        "entities": [
            {"type": "database", "value": "logs_db"},
            {"type": "table", "value": "access_logs"}
        ],
        "operators": [],
        "values": [],
        "expected_pattern": "TRUNCATE TABLE `logs_db`.`access_logs`"
    }
]
