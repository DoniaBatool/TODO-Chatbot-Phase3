"""
Fuzzy task matching utility using rapidfuzz.

Matches user queries to tasks with:
- Partial title matching ("milk" → "Buy milk from store")
- Typo tolerance ("grocerys" → "groceries")
- Configurable confidence thresholds:
  - Single match: 70% (high confidence needed)
  - Multiple matches: 60% (lower threshold for suggestions)
- Ranking by relevance score
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from rapidfuzz import fuzz, process


@dataclass
class MatchResult:
    """Result of fuzzy matching operation."""

    success: bool
    matches: List[Dict[str, Any]]
    query: Optional[str] = None
    error_message: Optional[str] = None


class FuzzyMatcher:
    """Fuzzy match user queries to task titles and descriptions."""

    # Default thresholds
    DEFAULT_SINGLE_MATCH_THRESHOLD = 70  # High confidence for single match
    DEFAULT_MULTIPLE_MATCH_THRESHOLD = 60  # Lower threshold for suggestions
    DEFAULT_MAX_RESULTS = 5  # Maximum matches to return

    def __init__(self):
        """Initialize fuzzy matcher."""
        pass

    def find_matches(
        self,
        query: Optional[str],
        tasks: Optional[List[Dict[str, Any]]],
        single_match_threshold: int = DEFAULT_SINGLE_MATCH_THRESHOLD,
        multiple_match_threshold: int = DEFAULT_MULTIPLE_MATCH_THRESHOLD,
        max_results: int = DEFAULT_MAX_RESULTS
    ) -> MatchResult:
        """
        Find tasks matching the query using fuzzy matching.

        Args:
            query: User's search query
            tasks: List of task dictionaries with 'id', 'title', 'description'
            single_match_threshold: Minimum score for single match (default: 70)
            multiple_match_threshold: Minimum score for multiple matches (default: 60)
            max_results: Maximum number of matches to return (default: 5)

        Returns:
            MatchResult with matched tasks ranked by relevance score

        Matching Strategy:
            1. Match against task titles (primary)
            2. Match against task descriptions (secondary)
            3. Title matches ranked higher than description matches
            4. Use partial ratio for flexible matching (handles substrings)

        Examples:
            >>> matcher = FuzzyMatcher()
            >>> tasks = [{"id": 1, "title": "Buy milk", "description": None}]
            >>> result = matcher.find_matches("milk", tasks)
            >>> assert result.success is True
            >>> assert result.matches[0]["task_id"] == 1
        """
        # Validation: Check query
        if not query or not str(query).strip():
            return MatchResult(
                success=False,
                matches=[],
                query=query,
                error_message="Query cannot be empty"
            )

        # Validation: Check tasks
        if tasks is None:
            return MatchResult(
                success=False,
                matches=[],
                query=query,
                error_message="Task list cannot be None"
            )

        if not tasks:
            return MatchResult(
                success=False,
                matches=[],
                query=query,
                error_message="No tasks to search"
            )

        query_normalized = str(query).strip().lower()

        # Find matches in titles and descriptions
        matches = []

        for task in tasks:
            task_id = task.get("id")
            title = task.get("title", "")
            description = task.get("description") or ""

            # Match against title (primary)
            title_score = self._calculate_match_score(query_normalized, title)

            # Match against description (secondary)
            description_score = 0
            if description:
                description_score = self._calculate_match_score(query_normalized, description)

            # Use best score
            best_score = max(title_score, description_score)
            matched_field = "title" if title_score >= description_score else "description"

            # Apply threshold
            threshold = multiple_match_threshold  # Use lower threshold initially

            if best_score >= threshold:
                matches.append({
                    "task_id": task_id,
                    "title": title,
                    "description": description,
                    "score": best_score,
                    "matched_field": matched_field
                })

        # No matches found
        if not matches:
            return MatchResult(
                success=False,
                matches=[],
                query=query,
                error_message=f"No tasks found matching '{query}'"
            )

        # Sort by score (descending), then by title length (ascending - prefer shorter)
        matches.sort(key=lambda m: (-m["score"], len(m["title"])))

        # Check if single match with high confidence
        if len(matches) == 1 and matches[0]["score"] < single_match_threshold:
            return MatchResult(
                success=False,
                matches=[],
                query=query,
                error_message=f"No confident match found for '{query}' (best score: {matches[0]['score']}%)"
            )

        # Limit results
        matches = matches[:max_results]

        return MatchResult(
            success=True,
            matches=matches,
            query=query,
            error_message=None
        )

    def _calculate_match_score(self, query: str, text: str) -> float:
        """
        Calculate fuzzy match score between query and text.

        Uses rapidfuzz's partial_ratio for flexible substring matching.
        This allows "milk" to match "Buy milk from store" with high score.

        Args:
            query: Normalized query string (lowercase, trimmed)
            text: Text to match against

        Returns:
            Match score between 0-100

        Examples:
            >>> matcher = FuzzyMatcher()
            >>> score = matcher._calculate_match_score("milk", "Buy milk from store")
            >>> assert score >= 80  # High score for substring match
        """
        if not text:
            return 0.0

        text_normalized = text.lower().strip()

        # Use partial_ratio for substring matching
        # This is more flexible than ratio for partial matches
        score = fuzz.partial_ratio(query, text_normalized)

        return float(score)

    def find_best_match(
        self,
        query: str,
        tasks: List[Dict[str, Any]],
        threshold: int = DEFAULT_SINGLE_MATCH_THRESHOLD
    ) -> Optional[Dict[str, Any]]:
        """
        Find single best matching task.

        Convenience method for getting one result with high confidence.

        Args:
            query: User's search query
            tasks: List of task dictionaries
            threshold: Minimum confidence score (default: 70)

        Returns:
            Best matching task dictionary or None if no confident match

        Examples:
            >>> matcher = FuzzyMatcher()
            >>> tasks = [{"id": 1, "title": "Buy milk", "description": None}]
            >>> match = matcher.find_best_match("milk", tasks)
            >>> assert match is not None
            >>> assert match["task_id"] == 1
        """
        result = self.find_matches(
            query=query,
            tasks=tasks,
            single_match_threshold=threshold,
            multiple_match_threshold=threshold,
            max_results=1
        )

        if result.success and len(result.matches) > 0:
            return result.matches[0]

        return None

    def find_exact_match(
        self,
        query: str,
        tasks: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find exact title match (case-insensitive).

        Args:
            query: User's search query
            tasks: List of task dictionaries

        Returns:
            Task with exact matching title or None

        Examples:
            >>> matcher = FuzzyMatcher()
            >>> tasks = [{"id": 1, "title": "Buy milk", "description": None}]
            >>> match = matcher.find_exact_match("buy milk", tasks)
            >>> assert match is not None
        """
        query_normalized = query.lower().strip()

        for task in tasks:
            title = task.get("title", "").lower().strip()
            if title == query_normalized:
                return {
                    "task_id": task.get("id"),
                    "title": task.get("title"),
                    "description": task.get("description"),
                    "score": 100.0,
                    "matched_field": "title"
                }

        return None
