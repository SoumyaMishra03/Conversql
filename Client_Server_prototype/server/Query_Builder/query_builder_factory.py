from .select_builder import SelectQueryBuilder
from .insert_builder import InsertQueryBuilder
from .update_builder import UpdateQueryBuilder
from .delete_builder import DeleteQueryBuilder
from .drop_builder import DropQueryBuilder

def is_destructive_operation(intent):
    """Check if the operation is destructive and requires admin privileges"""
    destructive_intents = [
        "INSERT_ROWS", "UPDATE_ROWS", "DELETE_ROWS", 
        "DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"
    ]
    return any(destructive_intent in intent for destructive_intent in destructive_intents)

def build_query(intent, schema_entities, operators, values,
                db_host='localhost', db_user='root', db_pass='root'):
    """
    Enhanced query builder factory that routes to appropriate builder based on intent
    """
    print(f"[DEBUG] Query Builder Factory - Intent: {intent}")
    print(f"[DEBUG] Schema entities: {schema_entities}")
    print(f"[DEBUG] Operators: {operators}")
    print(f"[DEBUG] Values: {values}")
    
    # Determine which builder to use based on intent
    if "INSERT_ROWS" in intent:
        builder = InsertQueryBuilder()
        return builder.build_query(intent, schema_entities, operators, values)
    
    elif "UPDATE_ROWS" in intent:
        builder = UpdateQueryBuilder()
        return builder.build_query(intent, schema_entities, operators, values)
    
    elif "DELETE_ROWS" in intent:
        builder = DeleteQueryBuilder()
        return builder.build_query(intent, schema_entities, operators, values)
    
    elif any(drop_intent in intent for drop_intent in ["DROP_TABLE", "DROP_DATABASE", "TRUNCATE_TABLE"]):
        builder = DropQueryBuilder()
        return builder.build_query(intent, schema_entities, operators, values)
    
    else:
        # Default to SELECT builder for all other cases
        builder = SelectQueryBuilder()
        return builder.build_query(intent, schema_entities, operators, values)

# Export test queries for all builders
from .test_queries import ALL_TEST_QUERIES
