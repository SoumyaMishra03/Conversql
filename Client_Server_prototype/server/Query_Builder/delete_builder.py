from NLP_pipeline.tokenizer_stanza import SCHEMA_MAP

OPERATOR_MAP = {
    "equals": "=",
    "equal": "=",
    "greater than": ">",
    "greaterthan": ">",
    "more than": ">",
    "less than": "<",
    "lessthan": "<",
    "greater than or equal to": ">=",
    "less than or equal to": "<=",
    "not equal": "!=",
    "!=": "!=",
    "=": "=",
    ">": ">",
    "<": "<",
    ">=": ">=",
    "<=": "<=",
}

class DeleteQueryBuilder:
    def normalize_for_lookup(self, text):
        """Normalize text for schema lookups - handles spaces and case"""
        return text.lower().strip()

    def get_original_column_name(self, normalized_column, table_name):
        """Get the original column name from the normalized version with improved matching"""
        table_to_columns = SCHEMA_MAP.get("table_to_columns", {})
    
        if table_name in table_to_columns:
            table_columns = table_to_columns[table_name]
        
            # First try exact match (case-insensitive)
            normalized_target = normalized_column.lower().strip()
            for original_col in table_columns:
                if original_col.lower().strip() == normalized_target:
                    return original_col
        
            # Then try partial matching for columns with special characters
            for original_col in table_columns:
                original_lower = original_col.lower().strip()
                # Handle special characters and spaces
                if (normalized_target in original_lower or 
                    original_lower in normalized_target or
                    normalized_target.replace(' ', '') == original_lower.replace(' ', '') or
                    normalized_target.replace('_', ' ') == original_lower or
                    normalized_target.replace(' ', '_') == original_lower or
                    normalized_target.replace('(', '').replace(')', '').replace('.', '') == 
                    original_lower.replace('(', '').replace(')', '').replace('.', '')):
                    return original_col
    
        # Fallback to the normalized name if no mapping found
        return normalized_column

    def resolve_schema_context(self, schema_entities):
        """Enhanced schema resolution using the SCHEMA_MAP structure"""
        database = None
        table = None
        columns = []
        resolved_entities = []
    
        # Get all mapping dictionaries
        db_to_tables = SCHEMA_MAP.get("db_to_tables", {})
        table_to_db = SCHEMA_MAP.get("table_to_db", {})
        table_to_columns = SCHEMA_MAP.get("table_to_columns", {})
        column_to_table_db = SCHEMA_MAP.get("column_to_table_db", {})
    
        # First pass: collect explicit entities
        for entity in schema_entities:
            if entity['type'] == 'database' and database is None:
                # Find exact database name (case-insensitive lookup)
                entity_value_lower = entity['value'].lower()
                for db_name in db_to_tables.keys():
                    if db_name.lower() == entity_value_lower:
                        database = db_name
                        break
                if not database:
                    database = entity['value']  # fallback
                
            elif entity['type'] == 'table' and table is None:
                # Find exact table name (case-insensitive lookup)
                entity_value_lower = entity['value'].lower()
                for table_name in table_to_db.keys():
                    if table_name.lower() == entity_value_lower:
                        table = table_name
                        break
                if not table:
                    table = entity['value']  # fallback
                
            elif entity['type'] == 'column':
                # Store original value for processing
                columns.append(entity['value'])
    
        # Second pass: resolve missing context using mappings
        if table and not database:
            database = table_to_db.get(table)
            if database:
                resolved_entities.append(f"Resolved database '{database}' from table '{table}'")
    
        if database and not table and len(columns) == 1:
            # If we have a database and single column, try to find the most likely table
            col = columns[0]
            # Look for column in column_to_table_db (case-insensitive)
            for col_key, col_info in column_to_table_db.items():
                if col_key.lower() == col.lower():
                    if isinstance(col_info, dict):
                        resolved_db, resolved_table = col_info.get('db'), col_info.get('table')
                    elif isinstance(col_info, tuple) and len(col_info) >= 2:
                        resolved_db, resolved_table = col_info[0], col_info[1]
                    else:
                        resolved_db, resolved_table = None, None
                    
                    if resolved_db and resolved_db.lower() == database.lower():
                        table = resolved_table
                        resolved_entities.append(f"Resolved table '{table}' from column '{col}' in database '{database}'")
                        break
    
        if not database and not table and columns:
            # Try to resolve from first column that has mapping
            found_mapping = False
            for col in columns:
                if found_mapping:
                    break
                for col_key, col_info in column_to_table_db.items():
                    if col_key.lower() == col.lower():
                        if isinstance(col_info, dict):
                            database, table = col_info.get('db'), col_info.get('table')
                        elif isinstance(col_info, tuple) and len(col_info) >= 2:
                            database, table = col_info[0], col_info[1]
                        
                        if database and table:
                            resolved_entities.append(f"Resolved database '{database}' and table '{table}' from column '{col}'")
                            found_mapping = True
                            break
    
        # Convert column names to original names for SQL generation
        if table and columns:
            original_columns = []
            for col in columns:
                original_col = self.get_original_column_name(col, table)
                original_columns.append(original_col)
                if original_col.lower() != col.lower():
                    resolved_entities.append(f"Mapped column '{col}' to original name '{original_col}'")
            columns = original_columns
    
        return database, table, columns, resolved_entities

    def build_query(self, intent, schema_entities, operators, values):
        """Build DELETE query"""
        database, table, columns, resolved_entities = self.resolve_schema_context(schema_entities)
        
        if not database or not table:
            return f"ERROR: DELETE requires both database and table. Found db='{database}', table='{table}'", None
        
        full_table = f"`{database}`.`{table}`"
        
        if not operators or not values:
            # Dangerous - delete all rows, add safety comment
            return f"DELETE FROM {full_table}; -- WARNING: This will delete ALL rows!", database
        
        # Build WHERE clause
        where_clauses = []
        for i, val in enumerate(values):
            if i < len(operators):
                operator_info = operators[i]
                
                if isinstance(operator_info, tuple) and len(operator_info) >= 2:
                    op_symbol = operator_info[1] if len(operator_info) >= 2 else operator_info[0]
                    target_column = operator_info[0] if operator_info[0] and operator_info[0] != 'None' else (columns[i] if i < len(columns) else columns[-1] if columns else 'id')
                else:
                    op_symbol = str(operator_info)
                    target_column = columns[i] if i < len(columns) else (columns[-1] if columns else 'id')
                
                clean_op = OPERATOR_MAP.get(op_symbol.lower().strip(), op_symbol)
                
                if val["type"] in ("STRING", "DATE"):
                    formatted_value = f"'{val['value']}'"
                else:
                    formatted_value = str(val['value'])
                
                clause = f"`{target_column}` {clean_op} {formatted_value}"
                where_clauses.append(clause)
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"DELETE FROM {full_table} WHERE {where_clause};"
        return query, database
