from typing import List, Optional, Literal
from motor.motor_asyncio import AsyncIOMotorDatabase
import re


class FuzzySearchService:
    """Service for performing fuzzy search across different collections"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    def _create_fuzzy_pattern(self, search_term: str) -> str:
        """
        Create a regex pattern for fuzzy matching.
        Allows for minor typos and partial matches.
        """
        # Remove extra spaces and special characters
        cleaned = re.sub(r'[^\w\s]', '', search_term).strip()

        # Split into words for multi-word search
        words = cleaned.split()

        # Create pattern that allows partial matching
        if len(words) == 1:
            # For single word, allow character variations
            return f".*{re.escape(cleaned)}.*"
        else:
            # For multiple words, search for all words (order independent)
            return ".*".join([re.escape(word) for word in words])

    def _calculate_score(self, document: dict, search_term: str, fields: List[str]) -> float:
        """
        Calculate relevance score for a document based on how well it matches the search term.
        Higher score = better match.
        """
        score = 0.0
        search_lower = search_term.lower()

        for field in fields:
            value = str(document.get(field, "")).lower()

            if not value:
                continue

            # Exact match gets highest score
            if search_lower == value:
                score += 100
            # Starts with search term
            elif value.startswith(search_lower):
                score += 50
            # Contains search term
            elif search_lower in value:
                score += 25
            # Partial word match
            else:
                # Check if any word in the value starts with search term
                words = value.split()
                for word in words:
                    if word.startswith(search_lower):
                        score += 15
                        break

        return score

    async def search(
        self,
        collection_name: Literal["users", "candidates"],
        search_term: str,
        page: int = 1,
        page_size: int = 20,
        min_score: float = 0.0
    ) -> tuple[List[dict], int]:
        """
        Perform fuzzy search on the specified collection.

        Args:
            collection_name: Name of the collection to search ('users' or 'candidates')
            search_term: The search query string
            page: Page number for pagination (default: 1)
            page_size: Number of results per page (default: 20)
            min_score: Minimum relevance score to include in results (default: 0.0)

        Returns:
            Tuple of (list of matching documents, total count)
        """
        if not search_term or not search_term.strip():
            return [], 0

        collection = self.database.get_collection(collection_name)

        # Define searchable fields based on collection
        search_fields = ["first_name", "last_name", "email", "phone_number"]

        # Create fuzzy regex pattern
        pattern = self._create_fuzzy_pattern(search_term)

        # Build MongoDB query with $or for multiple fields
        query = {
            "$or": [
                {field: {"$regex": pattern, "$options": "i"}}
                for field in search_fields
            ]
        }

        # Also search for full name (first_name + last_name)
        # This is done by adding a computed field search
        name_pattern = self._create_fuzzy_pattern(search_term)

        # Get all matching documents
        cursor = collection.find(query)
        all_results = []

        async for doc in cursor:
            # Calculate relevance score
            score = self._calculate_score(doc, search_term, search_fields)

            # Also check full name match
            if "first_name" in doc and "last_name" in doc:
                full_name = f"{doc.get('first_name', '')} {doc.get('last_name', '')}".lower()
                search_lower = search_term.lower()

                if search_lower == full_name:
                    score += 150  # Exact full name match
                elif full_name.startswith(search_lower):
                    score += 75
                elif search_lower in full_name:
                    score += 40

            if score >= min_score:
                doc["_search_score"] = score
                all_results.append(doc)

        # Sort by relevance score (highest first)
        all_results.sort(key=lambda x: x.get("_search_score", 0), reverse=True)

        # Get total count
        total = len(all_results)

        # Apply pagination
        skip = (page - 1) * page_size
        paginated_results = all_results[skip:skip + page_size]

        # Clean up search score from results (optional, keep if you want to show it)
        for doc in paginated_results:
            doc.pop("_search_score", None)

        return paginated_results, total

    async def search_advanced(
        self,
        collection_name: Literal["users", "candidates"],
        search_term: str,
        filters: Optional[dict] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[dict], int]:
        """
        Perform advanced fuzzy search with additional filters.

        Args:
            collection_name: Name of the collection to search
            search_term: The search query string
            filters: Additional MongoDB filters to apply (e.g., {"role_id": 1})
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            Tuple of (list of matching documents, total count)
        """
        if not search_term or not search_term.strip():
            # If no search term but filters provided, just filter
            if filters:
                collection = self.database.get_collection(collection_name)
                total = await collection.count_documents(filters)
                skip = (page - 1) * page_size
                cursor = collection.find(filters).skip(skip).limit(page_size)
                results = []
                async for doc in cursor:
                    results.append(doc)
                return results, total
            return [], 0

        collection = self.database.get_collection(collection_name)
        search_fields = ["first_name", "last_name", "email", "phone_number"]
        pattern = self._create_fuzzy_pattern(search_term)

        # Build query with fuzzy search
        fuzzy_query = {
            "$or": [
                {field: {"$regex": pattern, "$options": "i"}}
                for field in search_fields
            ]
        }

        # Combine with additional filters if provided
        if filters:
            query = {"$and": [fuzzy_query, filters]}
        else:
            query = fuzzy_query

        # Get matching documents
        cursor = collection.find(query)
        all_results = []

        async for doc in cursor:
            score = self._calculate_score(doc, search_term, search_fields)

            # Check full name match
            if "first_name" in doc and "last_name" in doc:
                full_name = f"{doc.get('first_name', '')} {doc.get('last_name', '')}".lower()
                search_lower = search_term.lower()

                if search_lower == full_name:
                    score += 150
                elif full_name.startswith(search_lower):
                    score += 75
                elif search_lower in full_name:
                    score += 40

            doc["_search_score"] = score
            all_results.append(doc)

        # Sort by relevance
        all_results.sort(key=lambda x: x.get("_search_score", 0), reverse=True)

        total = len(all_results)
        skip = (page - 1) * page_size
        paginated_results = all_results[skip:skip + page_size]

        # Remove search score
        for doc in paginated_results:
            doc.pop("_search_score", None)

        return paginated_results, total
