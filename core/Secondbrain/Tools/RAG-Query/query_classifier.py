import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
Query Classifier - Routes queries to appropriate data store
Distinguishes between analytical queries (SQLite) and exploratory queries (ChromaDB)
"""
import re
from typing import Tuple, Dict, Any, List
from enum import Enum


class QueryType(Enum):
    ANALYTICAL = "analytical"      # Count, sum, list queries -> SQLite
    EXPLORATORY = "exploratory"    # Semantic search -> ChromaDB
    HYBRID = "hybrid"              # Needs both stores


class QueryClassifier:
    """Classifies queries to route them to the appropriate data store"""

    # Analytical patterns - questions about counts, lists, aggregations
    ANALYTICAL_PATTERNS = [
        # Count queries
        r'\bhow many\b',
        r'\bcount\b',
        r'\btotal\b',
        r'\bnumber of\b',

        # List queries
        r'\blist all\b',
        r'\bshow all\b',
        r'\bwhat are the\b.*\b(customers|projects|tickets|employees)\b',
        r'\bwho are\b',
        r'\bwhich\b.*\b(customers|projects|tickets)\b',

        # Aggregation queries
        r'\bsum of\b',
        r'\baverage\b',
        r'\bmost\b',
        r'\btop\s+\d+\b',
        r'\bbottom\s+\d+\b',

        # Status queries
        r'\bstatus\b.*\b(projects|tickets)\b',
        r'\bactive\b.*\b(projects|customers)\b',
        r'\boverdue\b',
        r'\bpending\b.*\b(tickets|projects)\b',

        # Entity-specific queries
        r'\bcustomer\b.*\b(list|count|names?)\b',
        r'\bproject\b.*\b(list|count|status)\b',
        r'\bticket\b.*\b(list|count|status)\b',
        r'\bemployee\b.*\b(list|count)\b',
    ]

    # Exploratory patterns - semantic search, how-to, conceptual
    EXPLORATORY_PATTERNS = [
        r'\bhow (do|does|to|can)\b',
        r'\bwhat is\b',
        r'\bexplain\b',
        r'\bdescribe\b',
        r'\bfind\b.*\b(information|docs?|documents?)\b',
        r'\bsearch\b',
        r'\blook up\b',
        r'\btell me about\b',
        r'\bwhere can i find\b',
        r'\bprocedure\b',
        r'\bprocess\b',
        r'\bsteps\b',
        r'\bguide\b',
        r'\bdocumentation\b',
    ]

    # Entity keywords that suggest structured data
    ENTITY_KEYWORDS = [
        'customer', 'customers', 'client', 'clients',
        'project', 'projects',
        'ticket', 'tickets', 'issue', 'issues',
        'employee', 'employees', 'staff', 'team',
        'document', 'documents', 'file', 'files',
    ]

    def __init__(self):
        # Compile patterns for efficiency
        self.analytical_regex = [re.compile(p, re.IGNORECASE) for p in self.ANALYTICAL_PATTERNS]
        self.exploratory_regex = [re.compile(p, re.IGNORECASE) for p in self.EXPLORATORY_PATTERNS]

    def classify(self, query: str) -> Tuple[QueryType, Dict[str, Any]]:
        """
        Classify a query and return the type plus metadata

        Returns:
            Tuple of (QueryType, metadata dict with entities and intent)
        """
        query_lower = query.lower().strip()

        # Score for each type
        analytical_score = 0
        exploratory_score = 0

        # Check analytical patterns
        for pattern in self.analytical_regex:
            if pattern.search(query_lower):
                analytical_score += 1

        # Check exploratory patterns
        for pattern in self.exploratory_regex:
            if pattern.search(query_lower):
                exploratory_score += 1

        # Extract entities mentioned
        entities = self._extract_entities(query_lower)

        # Determine query intent
        intent = self._determine_intent(query_lower)

        metadata = {
            'entities': entities,
            'intent': intent,
            'analytical_score': analytical_score,
            'exploratory_score': exploratory_score,
        }

        # Classification logic
        if analytical_score > 0 and exploratory_score == 0:
            return QueryType.ANALYTICAL, metadata
        elif exploratory_score > 0 and analytical_score == 0:
            return QueryType.EXPLORATORY, metadata
        elif analytical_score > exploratory_score:
            # Slightly more analytical - check if it's asking for specific counts
            if any(word in query_lower for word in ['how many', 'count', 'total', 'list all']):
                return QueryType.ANALYTICAL, metadata
            return QueryType.HYBRID, metadata
        elif exploratory_score > analytical_score:
            return QueryType.EXPLORATORY, metadata
        else:
            # Default: check for entity keywords as tiebreaker
            if entities and any(word in query_lower for word in ['how many', 'list', 'count', 'show me all', 'show all']):
                return QueryType.ANALYTICAL, metadata
            # If entities mentioned without exploration intent, lean analytical
            if entities and not any(word in query_lower for word in ['about', 'tell me', 'explain', 'how to', 'how do']):
                return QueryType.ANALYTICAL, metadata
            return QueryType.EXPLORATORY, metadata

    def _extract_entities(self, query: str) -> List[str]:
        """Extract entity types mentioned in the query"""
        found = []
        for entity in self.ENTITY_KEYWORDS:
            if entity in query:
                # Normalize to singular form
                normalized = entity.rstrip('s') if entity.endswith('s') and entity not in ['process', 'status'] else entity
                if normalized not in found:
                    found.append(normalized)
        return found

    def _determine_intent(self, query: str) -> str:
        """Determine the high-level intent of the query"""
        if any(word in query for word in ['how many', 'count', 'total', 'number of']):
            return 'count'
        elif any(word in query for word in ['list', 'show all', 'what are']):
            return 'list'
        elif any(word in query for word in ['status', 'active', 'pending', 'overdue']):
            return 'status'
        elif any(word in query for word in ['how to', 'how do', 'explain', 'describe']):
            return 'explain'
        elif any(word in query for word in ['find', 'search', 'look up', 'where']):
            return 'search'
        else:
            return 'general'


class QueryRouter:
    """Routes queries to appropriate handlers based on classification"""

    def __init__(self, structured_store, vector_store):
        self.classifier = QueryClassifier()
        self.structured_store = structured_store
        self.vector_store = vector_store

    def route(self, query: str) -> Dict[str, Any]:
        """
        Route a query to the appropriate store(s) and return results

        Returns:
            Dict with 'type', 'results', and 'metadata'
        """
        query_type, metadata = self.classifier.classify(query)

        results = {
            'query_type': query_type.value,
            'metadata': metadata,
            'structured_results': None,
            'vector_results': None,
        }

        if query_type == QueryType.ANALYTICAL:
            results['structured_results'] = self._handle_analytical(query, metadata)
        elif query_type == QueryType.EXPLORATORY:
            results['vector_results'] = self._handle_exploratory(query)
        else:  # HYBRID
            results['structured_results'] = self._handle_analytical(query, metadata)
            results['vector_results'] = self._handle_exploratory(query)

        return results

    def _handle_analytical(self, query: str, metadata: Dict) -> Dict[str, Any]:
        """Handle analytical queries using structured store"""
        intent = metadata.get('intent')
        entities = metadata.get('entities', [])

        result = {'type': 'analytical', 'data': None, 'summary': ''}

        # Customer queries
        if 'customer' in entities or 'client' in entities:
            if intent == 'count':
                count = self.structured_store.count_customers()
                result['data'] = {'count': count}
                result['summary'] = f"There are {count} customers in the system."
            elif intent == 'list':
                customers = self.structured_store.get_customers(limit=50)
                result['data'] = customers
                result['summary'] = f"Found {len(customers)} customers."
            else:
                # Default: return summary stats
                result['data'] = self.structured_store.get_summary_stats()
                result['summary'] = f"Customer database summary."

        # Project queries
        elif 'project' in entities:
            if intent == 'count':
                count = self.structured_store.count_projects()
                result['data'] = {'count': count}
                result['summary'] = f"There are {count} projects in the system."
            elif intent == 'status':
                stats = self.structured_store.get_project_stats()
                result['data'] = stats
                result['summary'] = f"Project status breakdown."
            else:
                stats = self.structured_store.get_project_stats()
                result['data'] = stats
                result['summary'] = f"Found {stats['total_projects']} projects."

        # Ticket queries
        elif 'ticket' in entities or 'issue' in entities:
            tickets = self.structured_store.query("SELECT COUNT(*) as count FROM tickets")
            count = tickets[0]['count'] if tickets else 0
            result['data'] = {'count': count}
            result['summary'] = f"There are {count} tickets in the system."

        # General stats
        else:
            result['data'] = self.structured_store.get_summary_stats()
            result['summary'] = "Overall system statistics."

        return result

    def _handle_exploratory(self, query: str) -> List[Dict]:
        """Handle exploratory queries using vector store"""
        return self.vector_store.semantic_search(query, n_results=10)


def main():
    """Test the query classifier"""
    classifier = QueryClassifier()

    test_queries = [
        # Analytical queries
        "How many customers does Obera have?",
        "List all active projects",
        "What is the total number of tickets?",
        "Show me all customers",
        "Count of employees by department",
        "Which projects are overdue?",
        "Top 5 customers by project count",

        # Exploratory queries
        "How do I configure the firewall?",
        "What is the process for onboarding?",
        "Find documentation about Azure AD",
        "Explain the backup procedure",
        "Search for network configuration guides",

        # Hybrid/ambiguous queries
        "Tell me about customer ABC Corp",
        "What projects does John work on?",
        "Customer support tickets this week",
    ]

    print("=" * 70)
    print("Query Classifier Test")
    print("=" * 70)

    for query in test_queries:
        query_type, metadata = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"  Type: {query_type.value}")
        print(f"  Intent: {metadata['intent']}")
        print(f"  Entities: {metadata['entities']}")
        print(f"  Scores: analytical={metadata['analytical_score']}, exploratory={metadata['exploratory_score']}")


if __name__ == "__main__":
    main()
