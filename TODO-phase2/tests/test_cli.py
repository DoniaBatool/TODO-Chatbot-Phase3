"""
Unit Tests for CLI Interface

Tests the TodoCLI class and user interaction handling.
"""

import pytest
from todo.cli import TodoCLI


class TestCLIInitialization:
    """Test CLI initialization."""
    
    def test_cli_initializes_with_manager(self):
        """Test that CLI initializes with TaskManager."""
        cli = TodoCLI()
        assert cli.manager is not None
        assert len(cli.manager.get_all_tasks()) == 0


# Additional CLI tests will require mocking user input
# These tests verify the core structure is in place
class TestCLIStructure:
    """Test CLI structure and methods exist."""
    
    def test_cli_has_display_menu_method(self):
        """Test that display_menu method exists."""
        cli = TodoCLI()
        assert hasattr(cli, 'display_menu')
        assert callable(cli.display_menu)
    
    def test_cli_has_add_task_interactive_method(self):
        """Test that add_task_interactive method exists."""
        cli = TodoCLI()
        assert hasattr(cli, 'add_task_interactive')
        assert callable(cli.add_task_interactive)
    
    def test_cli_has_view_tasks_interactive_method(self):
        """Test that view_tasks_interactive method exists."""
        cli = TodoCLI()
        assert hasattr(cli, 'view_tasks_interactive')
        assert callable(cli.view_tasks_interactive)
    
    def test_cli_has_update_task_interactive_method(self):
        """Test that update_task_interactive method exists."""
        cli = TodoCLI()
        assert hasattr(cli, 'update_task_interactive')
        assert callable(cli.update_task_interactive)
    
    def test_cli_has_mark_complete_interactive_method(self):
        """Test that mark_complete_interactive method exists."""
        cli = TodoCLI()
        assert hasattr(cli, 'mark_complete_interactive')
        assert callable(cli.mark_complete_interactive)
    
    def test_cli_has_delete_task_interactive_method(self):
        """Test that delete_task_interactive method exists."""
        cli = TodoCLI()
        assert hasattr(cli, 'delete_task_interactive')
        assert callable(cli.delete_task_interactive)
    
    def test_cli_has_run_method(self):
        """Test that run method exists."""
        cli = TodoCLI()
        assert hasattr(cli, 'run')
        assert callable(cli.run)

