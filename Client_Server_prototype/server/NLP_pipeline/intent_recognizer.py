import os
import json
import re
import httpx
import asyncio
from typing import List, Tuple

class IntentRecognizer:
    def __init__(self, json_file: str = None, use_ai_fallback: bool = True):
        if json_file is None:
            base_dir = os.path.dirname(__file__)
            json_file = os.path.join(base_dir, "json", "intent.json")
        
        with open(json_file, "r") as f:
            patterns_dict = json.load(f)
        
        self.patterns = []
        for intent, phrases in patterns_dict.items():
            for phrase in phrases:
                pattern = re.compile(rf"\b({phrase})\b", re.IGNORECASE)
                self.patterns.append((pattern, intent))
        
        self.use_ai_fallback = use_ai_fallback
        self.available_intents = list(patterns_dict.keys())
        
        # Initialize Ollama client for AI fallback
        if use_ai_fallback:
            self.ollama_client = httpx.AsyncClient(timeout=10.0)
        else:
            self.ollama_client = None
        
        # Track AI usage to enforce single call per query
        self.ai_used_for_current_query = False

    def has_schema_entities(self, entities: List[dict]) -> bool:
        """
        Check if any meaningful schema entities were detected
        """
        meaningful_entities = [
            e for e in entities 
            if e.get('type') in ['database', 'table', 'column'] 
            and e.get('value') 
            and e.get('type') != 'unmatched'
        ]
        return len(meaningful_entities) > 0

    def predict_from_tokens(self, tokens: List[str], entities: List[dict] = None) -> Tuple[List[str], bool]:
        """
        Predict intent from tokens using pattern matching first,
        then AI fallback only if no schema entities detected
        
        Returns: (intents, ai_was_used)
        """
        text = " ".join(tokens).lower()
        found_intents = set()
        ai_was_used = False
        
        # Reset AI usage tracker for new query
        self.ai_used_for_current_query = False
        
        # First, try pattern matching
        for regex, intent in self.patterns:
            if regex.search(text):
                found_intents.add(intent)
        
        # If patterns found intents, return them
        if found_intents:
            print(f"[DEBUG] Intent found via patterns: {sorted(found_intents)}")
            return sorted(found_intents), ai_was_used
        
        # Check if we have schema entities - if yes, don't use AI fallback
        if entities and self.has_schema_entities(entities):
            print(f"[DEBUG] Schema entities detected, skipping AI fallback. Using SELECT_ROWS.")
            return ["SELECT_ROWS"], ai_was_used
        
        # Only use AI fallback if:
        # 1. AI fallback is enabled
        # 2. No schema entities detected (likely general chat)
        # 3. AI hasn't been used for this query yet
        if (self.use_ai_fallback and 
            self.ollama_client and 
            not self.ai_used_for_current_query):
            
            print(f"[DEBUG] No patterns or schema entities found, trying AI fallback for: '{text}'")
            try:
                # Run async AI prediction in sync context
                ai_intents = asyncio.run(self._predict_with_ai(text))
                if ai_intents:
                    print(f"[DEBUG] AI fallback determined intents: {ai_intents}")
                    self.ai_used_for_current_query = True
                    ai_was_used = True
                    return ai_intents, ai_was_used
            except Exception as e:
                print(f"[DEBUG] AI fallback failed: {e}")
        
        # Final fallback to SELECT_ROWS
        print(f"[DEBUG] Using final fallback: SELECT_ROWS")
        return ["SELECT_ROWS"], ai_was_used

    async def _predict_with_ai(self, text: str) -> List[str]:
        """
        Use AI to predict intent when pattern matching fails and no schema entities detected
        """
        try:
            # Check if Ollama is available
            health_response = await self.ollama_client.get("http://localhost:11434/api/tags")
            health_response.raise_for_status()
        except:
            print("[DEBUG] Ollama not available for AI intent prediction")
            return []

        # Create a focused prompt for intent classification
        available_intents_str = ", ".join(self.available_intents)
        
        prompt = f"""Classify this user query into the most appropriate database operation intent.

Query: "{text}"

Available intents: {available_intents_str}

Rules:
- COUNT_ROWS: counting/number queries
- AGGREGATE_*: calculations (sum, average, min, max)
- SELECT_ROWS: basic data retrieval
- INSERT_ROWS: adding new data
- UPDATE_ROWS: modifying data
- DELETE_ROWS: removing data
- DROP_*: removing tables/databases
- DESCRIPTION: asking about structure

Return only the intent name (e.g., "SELECT_ROWS"):"""

        try:
            response = await self.ollama_client.post(
                "http://localhost:11434/api/generate",
                json={
                    "prompt": prompt,
                    "model": "gemma:2b",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Very low temperature for consistent classification
                        "top_p": 0.8,
                        "num_predict": 20,   # Very short response expected
                        "stop": ["\n", ":", "Explanation"]
                    }
                }
            )
            response.raise_for_status()
            
            json_response = response.json()
            ai_response = json_response.get("response", "").strip()
            
            print(f"[DEBUG] AI raw response: '{ai_response}'")
            
            # Parse the AI response to extract valid intents
            predicted_intents = self._parse_ai_response(ai_response)
            return predicted_intents
            
        except Exception as e:
            print(f"[DEBUG] Error in AI intent prediction: {e}")
            return []

    def _parse_ai_response(self, ai_response: str) -> List[str]:
        """
        Parse AI response to extract valid intent names
        """
        # Clean up the response
        ai_response = ai_response.strip().upper()
        
        # Look for exact matches first
        for intent in self.available_intents:
            if intent in ai_response:
                return [intent]
        
        # Final fallback
        return ["SELECT_ROWS"]

    async def close(self):
        """Close the HTTP client"""
        if self.ollama_client:
            await self.ollama_client.aclose()

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.ollama_client:
            try:
                asyncio.run(self.close())
            except:
                pass
