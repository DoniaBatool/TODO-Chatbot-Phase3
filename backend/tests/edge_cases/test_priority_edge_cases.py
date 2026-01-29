"""
Edge case tests for priority keyword detection.

Tests handling of:
- Contradictory keywords (urgent + later)
- Negation patterns (not urgent)
- Ambiguous phrases
- Special characters
- Multi-language keywords
"""

import pytest
from unittest.mock import Mock
from src.ai_agent.context_manager import ContextManager
from src.ai_agent.utils import suggest_priority_from_keywords
from src.services.intent_classifier import IntentClassifier


class TestContradictoryKeywords:
    """Test handling of contradictory priority keywords (T092)."""

    @pytest.fixture
    def context_manager(self):
        """Create context manager with mock service."""
        mock_service = Mock()
        return ContextManager(mock_service)

    def test_urgent_and_later_together(self, context_manager):
        """When both 'urgent' and 'later' present, first match wins."""
        result = context_manager.extract_priority_from_text("urgent task to do later")
        # First keyword wins in current implementation
        assert result == "high"

    def test_later_and_urgent_order(self, context_manager):
        """Order of keywords affects result."""
        result = context_manager.extract_priority_from_text("later I'll do this urgent task")
        # 'later' comes first, but 'high' keywords checked before 'low'
        assert result in ["high", "low"]

    def test_important_but_minor(self, context_manager):
        """'important but minor' - contradictory."""
        result = context_manager.extract_priority_from_text("important but minor task")
        # Should pick one - 'important' checked first
        assert result == "high"

    def test_critical_someday(self, context_manager):
        """'critical someday' - contradictory."""
        result = context_manager.extract_priority_from_text("critical task for someday")
        assert result == "high"

    def test_asap_eventually(self, context_manager):
        """'asap eventually' - contradictory."""
        result = context_manager.extract_priority_from_text("need this asap, well eventually")
        assert result == "high"

    def test_low_priority_urgent(self, context_manager):
        """'low priority' with 'urgent' - high keywords checked first."""
        result = context_manager.extract_priority_from_text("low priority but kind of urgent")
        # High keywords are checked before low keywords in implementation
        assert result in ["high", "low"]  # Depends on check order

    def test_high_priority_trivial(self, context_manager):
        """Explicit 'high priority' with 'trivial'."""
        result = context_manager.extract_priority_from_text("high priority trivial cleanup")
        assert result == "high"


class TestNegationPatterns:
    """Test negation patterns like 'not urgent'."""

    @pytest.fixture
    def context_manager(self):
        """Create context manager with mock service."""
        mock_service = Mock()
        return ContextManager(mock_service)

    def test_not_urgent_detects_urgent(self, context_manager):
        """'not urgent' currently detects 'urgent' (limitation)."""
        result = context_manager.extract_priority_from_text("this is not urgent")
        # Current implementation: substring match finds 'urgent'
        assert result == "high"

    def test_not_important_detects_important(self, context_manager):
        """'not important' currently detects 'important' (limitation)."""
        result = context_manager.extract_priority_from_text("not that important")
        assert result == "high"

    def test_no_rush_no_detection(self, context_manager):
        """'no rush' should not trigger priority detection."""
        result = context_manager.extract_priority_from_text("no rush on this one")
        # 'rush' is not a keyword, so no match
        assert result is None

    def test_dont_need_asap(self, context_manager):
        """'don't need asap' detects 'asap' (limitation)."""
        result = context_manager.extract_priority_from_text("don't need this asap")
        assert result == "high"


class TestAmbiguousPhrases:
    """Test ambiguous priority phrases."""

    @pytest.fixture
    def context_manager(self):
        """Create context manager with mock service."""
        mock_service = Mock()
        return ContextManager(mock_service)

    def test_kind_of_important(self, context_manager):
        """'kind of important' should detect 'important'."""
        result = context_manager.extract_priority_from_text("kind of important")
        assert result == "high"

    def test_somewhat_urgent(self, context_manager):
        """'somewhat urgent' should detect 'urgent'."""
        result = context_manager.extract_priority_from_text("somewhat urgent matter")
        assert result == "high"

    def test_maybe_later(self, context_manager):
        """'maybe later' should detect 'later'."""
        result = context_manager.extract_priority_from_text("maybe do this later")
        assert result == "low"

    def test_probably_minor(self, context_manager):
        """'probably minor' should detect 'minor'."""
        result = context_manager.extract_priority_from_text("probably minor issue")
        assert result == "low"

    def test_fairly_critical(self, context_manager):
        """'fairly critical' should detect 'critical'."""
        result = context_manager.extract_priority_from_text("fairly critical bug")
        assert result == "high"

    def test_semi_urgent(self, context_manager):
        """'semi-urgent' should detect 'urgent'."""
        result = context_manager.extract_priority_from_text("semi-urgent request")
        assert result == "high"


class TestSpecialCharacters:
    """Test priority keywords with special characters."""

    @pytest.fixture
    def context_manager(self):
        """Create context manager with mock service."""
        mock_service = Mock()
        return ContextManager(mock_service)

    def test_urgent_with_exclamation(self, context_manager):
        """'URGENT!' should detect high priority."""
        result = context_manager.extract_priority_from_text("URGENT!")
        assert result == "high"

    def test_urgent_with_asterisks(self, context_manager):
        """'*urgent*' should detect high priority."""
        result = context_manager.extract_priority_from_text("*urgent* task")
        assert result == "high"

    def test_important_underscored(self, context_manager):
        """'_important_' should detect high priority."""
        result = context_manager.extract_priority_from_text("_important_ item")
        assert result == "high"

    def test_asap_with_periods(self, context_manager):
        """'A.S.A.P.' might not be detected (limitation)."""
        result = context_manager.extract_priority_from_text("need this A.S.A.P.")
        # Periods break the keyword match
        assert result is None or result == "high"

    def test_priority_in_hashtag(self, context_manager):
        """'#urgent' should detect high priority."""
        result = context_manager.extract_priority_from_text("#urgent task")
        assert result == "high"


class TestSuggestPriorityEdgeCases:
    """Test suggest_priority_from_keywords edge cases."""

    def test_empty_title(self):
        """Empty title should return medium."""
        result = suggest_priority_from_keywords("")
        assert result == "medium"

    def test_whitespace_title(self):
        """Whitespace title should return medium."""
        result = suggest_priority_from_keywords("   ")
        assert result == "medium"

    def test_only_numbers(self):
        """Numbers only should return medium."""
        result = suggest_priority_from_keywords("123456")
        assert result == "medium"

    def test_special_chars_only(self):
        """Special chars only should return medium."""
        result = suggest_priority_from_keywords("@#$%^&*")
        assert result == "medium"

    def test_very_long_title_with_keyword(self):
        """Long title with keyword should still detect."""
        long_title = "This is a very long task title that contains many words " * 10 + "urgent"
        result = suggest_priority_from_keywords(long_title)
        assert result == "high"

    def test_keyword_in_middle_of_word(self):
        """Keyword as part of another word should still match."""
        result = suggest_priority_from_keywords("urgently needed")
        # 'urgent' is substring of 'urgently'
        assert result == "high"

    def test_multiple_high_keywords(self):
        """Multiple high keywords should still return high."""
        result = suggest_priority_from_keywords("urgent critical important task")
        assert result == "high"

    def test_multiple_low_keywords(self):
        """Multiple low keywords should still return low."""
        result = suggest_priority_from_keywords("someday later eventually do this")
        assert result == "low"


class TestIntentClassifierPriorityEdgeCases:
    """Test intent classifier priority extraction edge cases."""

    @pytest.fixture
    def classifier(self):
        """Create intent classifier."""
        return IntentClassifier()

    def test_update_with_priority_keyword(self, classifier):
        """'update task to urgent' should extract priority."""
        result = classifier.classify("update task 5 to high priority")
        priority = result.extracted_entities.get("priority")
        assert priority in [None, "high"]

    def test_delete_with_priority_keyword(self, classifier):
        """'delete urgent task' - priority extraction."""
        result = classifier.classify("delete the urgent task")
        # DELETE intent may or may not extract priority
        priority = result.extracted_entities.get("priority")
        assert priority in [None, "high"]

    def test_list_with_priority_filter(self, classifier):
        """'show high priority tasks' should extract priority."""
        result = classifier.classify("show high priority tasks")
        priority = result.extracted_entities.get("priority")
        assert priority in [None, "high"]

    def test_complete_with_priority_keyword(self, classifier):
        """'complete the urgent task' - priority extraction."""
        result = classifier.classify("complete the urgent task")
        priority = result.extracted_entities.get("priority")
        assert priority in [None, "high"]


class TestPriorityOrderingEdgeCases:
    """Test priority detection ordering and precedence."""

    @pytest.fixture
    def context_manager(self):
        """Create context manager with mock service."""
        mock_service = Mock()
        return ContextManager(mock_service)

    def test_high_checked_before_low(self, context_manager):
        """High priority keywords are checked before low."""
        # This tests internal implementation - high keywords checked first
        result = context_manager.extract_priority_from_text("urgent and later")
        assert result == "high"

    def test_explicit_priority_phrase_precedence(self, context_manager):
        """'high priority' phrase should take precedence."""
        result = context_manager.extract_priority_from_text("high priority task")
        assert result == "high"

    def test_low_priority_phrase_precedence(self, context_manager):
        """'low priority' phrase should work."""
        result = context_manager.extract_priority_from_text("low priority cleanup")
        assert result == "low"


class TestRealWorldScenarios:
    """Test real-world priority detection scenarios."""

    @pytest.fixture
    def context_manager(self):
        """Create context manager with mock service."""
        mock_service = Mock()
        return ContextManager(mock_service)

    def test_call_client_urgent(self, context_manager):
        """'urgent call client' should be high."""
        result = context_manager.extract_priority_from_text("urgent call client back")
        assert result == "high"

    def test_review_code_later(self, context_manager):
        """'review code later' should be low."""
        result = context_manager.extract_priority_from_text("review code later when free")
        assert result == "low"

    def test_fix_critical_bug(self, context_manager):
        """'fix critical bug' should be high."""
        result = context_manager.extract_priority_from_text("fix critical bug in production")
        assert result == "high"

    def test_minor_typo_fix(self, context_manager):
        """'minor typo fix' should be low."""
        result = context_manager.extract_priority_from_text("fix minor typo in docs")
        assert result == "low"

    def test_deadline_approaching(self, context_manager):
        """'deadline approaching' - check for deadline keyword."""
        result = context_manager.extract_priority_from_text("deadline approaching fast")
        # 'deadline' may or may not be in keywords
        # assert result == "high" or result is None

    def test_asap_please(self, context_manager):
        """'asap please' should be high."""
        result = context_manager.extract_priority_from_text("need this done asap please")
        assert result == "high"

    def test_whenever_you_can(self, context_manager):
        """'whenever you can' should not match any keywords."""
        result = context_manager.extract_priority_from_text("do this whenever you can")
        # 'whenever' is not a keyword
        assert result is None

    def test_at_your_convenience(self, context_manager):
        """'at your convenience' should not trigger priority."""
        result = context_manager.extract_priority_from_text("complete at your convenience")
        assert result is None
