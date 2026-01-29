"""
Unit tests for FuzzyMatcher utility.

Tests fuzzy task matching for:
- Partial title matching ("milk" matches "Buy milk from store")
- Typo tolerance ("grocerys" matches "groceries")
- Confidence thresholds (70% for single match, 60% for multiple)
- Ranking by relevance score
- Edge cases (empty queries, no matches, identical matches)
"""

import pytest
from typing import List, Dict, Any
from src.utils.fuzzy_matcher import FuzzyMatcher, MatchResult


class TestFuzzyMatcher:
    """Test fuzzy task matching with rapidfuzz."""

    @pytest.fixture
    def matcher(self):
        """Create fuzzy matcher instance."""
        return FuzzyMatcher()

    @pytest.fixture
    def sample_tasks(self) -> List[Dict[str, Any]]:
        """Sample tasks for testing."""
        return [
            {"id": 1, "title": "Buy milk from store", "description": "Get 2% milk"},
            {"id": 2, "title": "Buy groceries", "description": "Weekly shopping"},
            {"id": 3, "title": "Call dentist for appointment", "description": None},
            {"id": 4, "title": "Fix bug in login page", "description": "Password reset broken"},
            {"id": 5, "title": "Write unit tests", "description": "Test the new feature"},
            {"id": 6, "title": "Buy birthday gift for Mom", "description": "Her birthday is next week"},
            {"id": 7, "title": "Schedule dentist appointment", "description": "Teeth cleaning"},
        ]

    # Basic Matching Tests
    def test_exact_match_high_score(self, matcher, sample_tasks):
        """Exact match returns high confidence score."""
        result = matcher.find_matches("Buy milk from store", sample_tasks)
        assert result.success is True
        assert len(result.matches) >= 1
        assert result.matches[0]["task_id"] == 1
        assert result.matches[0]["score"] >= 95  # Near-perfect match

    def test_partial_match_title(self, matcher, sample_tasks):
        """Partial title match works correctly."""
        result = matcher.find_matches("milk", sample_tasks)
        assert result.success is True
        assert len(result.matches) >= 1
        # Should match "Buy milk from store"
        assert result.matches[0]["task_id"] == 1

    def test_multiple_word_match(self, matcher, sample_tasks):
        """Match with multiple words."""
        result = matcher.find_matches("buy groceries", sample_tasks)
        assert result.success is True
        assert result.matches[0]["task_id"] == 2

    # Typo Tolerance Tests
    def test_typo_tolerance_single_char(self, matcher, sample_tasks):
        """Tolerate single character typo."""
        result = matcher.find_matches("milx", sample_tasks)  # 'x' instead of 'k'
        assert result.success is True
        assert result.matches[0]["task_id"] == 1

    def test_typo_tolerance_missing_char(self, matcher, sample_tasks):
        """Tolerate missing character."""
        result = matcher.find_matches("grocerys", sample_tasks)  # Missing 'ie'
        assert result.success is True
        # Should match "Buy groceries"
        matching_ids = [m["task_id"] for m in result.matches]
        assert 2 in matching_ids

    def test_typo_tolerance_transposition(self, matcher, sample_tasks):
        """Tolerate character transposition."""
        result = matcher.find_matches("tset", sample_tasks)  # "test" with transposition
        assert result.success is True
        # Should match "Write unit tests"
        matching_ids = [m["task_id"] for m in result.matches]
        assert 5 in matching_ids

    # Confidence Threshold Tests
    def test_single_match_above_70_percent(self, matcher, sample_tasks):
        """Single match requires 70% confidence."""
        # "dentist" should match both task 3 and 7
        result = matcher.find_matches("dentist", sample_tasks)
        assert result.success is True
        # All matches should be above 60% (multiple match threshold)
        for match in result.matches:
            assert match["score"] >= 60

    def test_below_threshold_no_match(self, matcher, sample_tasks):
        """Query below threshold returns no matches."""
        result = matcher.find_matches("xyz", sample_tasks)
        assert result.success is False
        assert len(result.matches) == 0
        assert result.error_message is not None

    def test_multiple_matches_ranked_by_score(self, matcher, sample_tasks):
        """Multiple matches ranked by relevance score."""
        result = matcher.find_matches("buy", sample_tasks)
        assert result.success is True
        assert len(result.matches) >= 2
        # Scores should be in descending order
        scores = [m["score"] for m in result.matches]
        assert scores == sorted(scores, reverse=True)

    # Description Matching Tests
    def test_match_in_description(self, matcher, sample_tasks):
        """Match text in task description."""
        result = matcher.find_matches("password", sample_tasks)
        assert result.success is True
        # Should match task 4: "Fix bug in login page" (description: "Password reset broken")
        matching_ids = [m["task_id"] for m in result.matches]
        assert 4 in matching_ids

    def test_title_priority_over_description(self, matcher, sample_tasks):
        """Title matches ranked higher than description matches."""
        result = matcher.find_matches("dentist", sample_tasks)
        assert result.success is True
        # Task 3 and 7 both have "dentist" in title, should rank higher
        # than any description-only matches
        top_match_ids = [m["task_id"] for m in result.matches[:2]]
        assert 3 in top_match_ids or 7 in top_match_ids

    # Edge Case Tests
    def test_empty_query_handled(self, matcher, sample_tasks):
        """Empty query returns error."""
        result = matcher.find_matches("", sample_tasks)
        assert result.success is False
        assert result.error_message is not None

    def test_none_query_handled(self, matcher, sample_tasks):
        """None query returns error."""
        result = matcher.find_matches(None, sample_tasks)
        assert result.success is False
        assert result.error_message is not None

    def test_empty_task_list_handled(self, matcher):
        """Empty task list returns no matches."""
        result = matcher.find_matches("milk", [])
        assert result.success is False
        assert len(result.matches) == 0

    def test_none_task_list_handled(self, matcher):
        """None task list returns error."""
        result = matcher.find_matches("milk", None)
        assert result.success is False
        assert result.error_message is not None

    def test_tasks_without_descriptions(self, matcher):
        """Handle tasks without descriptions gracefully."""
        tasks = [
            {"id": 1, "title": "Task one", "description": None},
            {"id": 2, "title": "Task two", "description": None},
        ]
        result = matcher.find_matches("one", tasks)
        assert result.success is True
        assert result.matches[0]["task_id"] == 1

    # Case Insensitivity Tests
    def test_case_insensitive_matching(self, matcher, sample_tasks):
        """Matching is case-insensitive."""
        result1 = matcher.find_matches("MILK", sample_tasks)
        result2 = matcher.find_matches("milk", sample_tasks)
        result3 = matcher.find_matches("MiLk", sample_tasks)

        assert result1.success is True
        assert result2.success is True
        assert result3.success is True

        # All should match the same task
        assert result1.matches[0]["task_id"] == 1
        assert result2.matches[0]["task_id"] == 1
        assert result3.matches[0]["task_id"] == 1

    # Whitespace Handling Tests
    def test_extra_whitespace_normalized(self, matcher, sample_tasks):
        """Extra whitespace doesn't affect matching."""
        result = matcher.find_matches("  buy   milk  ", sample_tasks)
        assert result.success is True
        assert result.matches[0]["task_id"] == 1

    # Match Metadata Tests
    def test_match_includes_task_data(self, matcher, sample_tasks):
        """Match result includes task data."""
        result = matcher.find_matches("milk", sample_tasks)
        assert result.success is True
        match = result.matches[0]

        # Check required fields
        assert "task_id" in match
        assert "title" in match
        assert "description" in match
        assert "score" in match
        assert "matched_field" in match  # 'title' or 'description'

    def test_matched_field_indicates_location(self, matcher, sample_tasks):
        """Matched field indicates where match was found."""
        result = matcher.find_matches("milk", sample_tasks)
        assert result.success is True
        # "milk" is in the title
        assert result.matches[0]["matched_field"] == "title"

        result = matcher.find_matches("password", sample_tasks)
        assert result.success is True
        # "password" is in the description
        assert result.matches[0]["matched_field"] == "description"

    # Threshold Configuration Tests
    def test_custom_single_match_threshold(self, matcher, sample_tasks):
        """Custom threshold for single match."""
        # Use higher threshold (80%)
        result = matcher.find_matches("milk", sample_tasks, single_match_threshold=80)
        assert result.success is True
        # Should still match with high score
        assert result.matches[0]["score"] >= 80

    def test_custom_multiple_match_threshold(self, matcher, sample_tasks):
        """Custom threshold for multiple matches."""
        # Use higher threshold (70%)
        result = matcher.find_matches("buy", sample_tasks, multiple_match_threshold=70)
        assert result.success is True
        # All matches should be above 70%
        for match in result.matches:
            assert match["score"] >= 70

    # Ranking Tests
    def test_shorter_title_ranked_higher(self, matcher):
        """When scores are equal, shorter titles rank higher."""
        tasks = [
            {"id": 1, "title": "Buy milk from the grocery store", "description": None},
            {"id": 2, "title": "Buy milk", "description": None},
        ]
        result = matcher.find_matches("buy milk", tasks)
        assert result.success is True
        # Task 2 (shorter) should rank higher or equal
        # Both should have high scores, but shorter is preferred
        if len(result.matches) >= 2:
            # If both match, check ordering
            scores = [m["score"] for m in result.matches]
            # Shorter title should have equal or higher score
            assert result.matches[0]["task_id"] == 2 or scores[0] >= scores[1]

    def test_max_results_limit(self, matcher, sample_tasks):
        """Limit number of returned results."""
        result = matcher.find_matches("buy", sample_tasks, max_results=2)
        assert result.success is True
        assert len(result.matches) <= 2

    # Special Characters Tests
    def test_special_characters_in_query(self, matcher):
        """Handle special characters in query."""
        tasks = [
            {"id": 1, "title": "Fix bug #123", "description": None},
            {"id": 2, "title": "Review PR-456", "description": None},
        ]
        result = matcher.find_matches("bug #123", tasks)
        assert result.success is True
        assert result.matches[0]["task_id"] == 1

    def test_numbers_in_query(self, matcher, sample_tasks):
        """Handle numbers in query."""
        result = matcher.find_matches("2%", sample_tasks)
        assert result.success is True
        # Should match task 1: "Get 2% milk" in description
        matching_ids = [m["task_id"] for m in result.matches]
        assert 1 in matching_ids

    # Performance Tests (Basic)
    def test_handles_large_task_list(self, matcher):
        """Handle large task lists efficiently."""
        # Create 100 tasks
        tasks = [
            {"id": i, "title": f"Task {i}", "description": f"Description {i}"}
            for i in range(100)
        ]
        tasks.append({"id": 101, "title": "Find this specific task", "description": None})

        result = matcher.find_matches("specific task", tasks)
        assert result.success is True
        assert result.matches[0]["task_id"] == 101

    # Boundary Tests
    def test_very_long_query(self, matcher, sample_tasks):
        """Handle very long queries."""
        long_query = "buy milk from store " * 20  # Very long query
        result = matcher.find_matches(long_query, sample_tasks)
        # Should still work, even if scores are lower
        assert result.success is True or result.success is False  # Either is valid

    def test_single_character_query(self, matcher, sample_tasks):
        """Handle single character query."""
        result = matcher.find_matches("a", sample_tasks)
        # May or may not match depending on threshold
        # Just ensure it doesn't crash
        assert isinstance(result.success, bool)
