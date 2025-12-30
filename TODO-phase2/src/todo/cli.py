"""
Command-Line Interface Module

Provides interactive CLI for the todo application.
"""

from typing import Optional
from .manager import TaskManager
from .task import Task


class TodoCLI:
    """
    Command-line interface for Todo application.
    
    Provides interactive menu and user input handling.
    """
    
    def __init__(self) -> None:
        """Initialize CLI with task manager."""
        self.manager = TaskManager()
    
    def display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("           TODO LIST MANAGER")
        print("=" * 50)
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Update Task")
        print("4. Mark Task Complete/Incomplete")
        print("5. Delete Task")
        print("6. Exit")
        print("=" * 50)
    
    def add_task_interactive(self) -> None:
        """
        Interactive CLI for adding a new task.
        Handles user input, validation, and error display.
        """
        print("\n" + "=" * 50)
        print("           ADD NEW TASK")
        print("=" * 50)
        
        # Get title with validation loop
        while True:
            title = input("\nEnter task title: ").strip()
            if not title:
                print("❌ Error: Title cannot be empty")
                continue
            if len(title) > 200:
                print(f"❌ Error: Title too long ({len(title)}/200 characters)")
                continue
            break
        
        # Get optional description
        while True:
            description = input("Enter description (optional, press Enter to skip): ").strip()
            if len(description) > 1000:
                print(f"❌ Error: Description too long ({len(description)}/1000 characters)")
                continue
            break
        
        # Create task
        try:
            task = self.manager.add_task(title, description)
            print(f"\n✓ Task added successfully!")
            print(f"ID: {task.id}")
            print(f"Title: {task.title}")
            if task.description:
                print(f"Description: {task.description}")
            print(f"Status: Pending")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    def view_tasks_interactive(self) -> None:
        """Display all tasks in a formatted list."""
        print("\n" + "=" * 50)
        print("           ALL TASKS")
        print("=" * 50)
        
        tasks = self.manager.get_all_tasks()
        
        if not tasks:
            print("\nNo tasks found. Add some tasks to get started!")
            return
        
        print(f"\nTotal Tasks: {len(tasks)}")
        print(f"Pending: {len(self.manager.get_pending_tasks())}")
        print(f"Completed: {len(self.manager.get_completed_tasks())}")
        print("\n" + "-" * 50)
        
        for task in tasks:
            status_icon = "✓" if task.completed else "○"
            status_text = "Completed" if task.completed else "Pending"
            
            print(f"\n[{status_icon}] ID: {task.id}")
            print(f"    Title: {task.title}")
            if task.description:
                print(f"    Description: {task.description}")
            print(f"    Status: {status_text}")
            print(f"    Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def update_task_interactive(self) -> None:
        """Interactive CLI for updating a task."""
        print("\n" + "=" * 50)
        print("           UPDATE TASK")
        print("=" * 50)
        
        # Show current tasks first
        tasks = self.manager.get_all_tasks()
        if not tasks:
            print("\nNo tasks to update!")
            return
        
        print("\nCurrent tasks:")
        for task in tasks:
            print(f"  {task}")
        
        # Get task ID
        try:
            task_id = int(input("\nEnter task ID to update: "))
        except ValueError:
            print("❌ Error: Invalid ID. Please enter a number.")
            return
        
        task = self.manager.get_task_by_id(task_id)
        if not task:
            print(f"❌ Error: Task with ID {task_id} not found.")
            return
        
        # Show current task details
        print(f"\nCurrent Title: {task.title}")
        print(f"Current Description: {task.description}")
        
        # Get new values
        print("\nEnter new values (press Enter to keep current):")
        
        new_title = input("New title: ").strip()
        new_description = input("New description: ").strip()
        
        # Update task
        try:
            updated_task = self.manager.update_task(
                task_id,
                title=new_title if new_title else None,
                description=new_description if new_description else None
            )
            if updated_task:
                print(f"\n✓ Task updated successfully!")
                print(f"Title: {updated_task.title}")
                print(f"Description: {updated_task.description}")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    def mark_complete_interactive(self) -> None:
        """Interactive CLI for marking tasks complete/incomplete."""
        print("\n" + "=" * 50)
        print("           MARK TASK COMPLETE/INCOMPLETE")
        print("=" * 50)
        
        # Show current tasks
        tasks = self.manager.get_all_tasks()
        if not tasks:
            print("\nNo tasks found!")
            return
        
        print("\nCurrent tasks:")
        for task in tasks:
            print(f"  {task}")
        
        # Get task ID
        try:
            task_id = int(input("\nEnter task ID: "))
        except ValueError:
            print("❌ Error: Invalid ID. Please enter a number.")
            return
        
        task = self.manager.get_task_by_id(task_id)
        if not task:
            print(f"❌ Error: Task with ID {task_id} not found.")
            return
        
        # Toggle completion status
        new_status = not task.completed
        self.manager.mark_complete(task_id, new_status)
        
        status_text = "completed" if new_status else "pending"
        print(f"\n✓ Task marked as {status_text}!")
        print(f"Title: {task.title}")
    
    def delete_task_interactive(self) -> None:
        """Interactive CLI for deleting a task."""
        print("\n" + "=" * 50)
        print("           DELETE TASK")
        print("=" * 50)
        
        # Show current tasks
        tasks = self.manager.get_all_tasks()
        if not tasks:
            print("\nNo tasks to delete!")
            return
        
        print("\nCurrent tasks:")
        for task in tasks:
            print(f"  {task}")
        
        # Get task ID
        try:
            task_id = int(input("\nEnter task ID to delete: "))
        except ValueError:
            print("❌ Error: Invalid ID. Please enter a number.")
            return
        
        task = self.manager.get_task_by_id(task_id)
        if not task:
            print(f"❌ Error: Task with ID {task_id} not found.")
            return
        
        # Confirm deletion
        print(f"\nTask to delete: {task.title}")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            self.manager.delete_task(task_id)
            print(f"\n✓ Task deleted successfully!")
        else:
            print("\n✗ Deletion cancelled.")
    
    def run(self) -> None:
        """
        Run the main CLI loop.
        
        Displays menu and processes user input until exit.
        """
        print("\n🎯 Welcome to Todo List Manager!")
        
        while True:
            self.display_menu()
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                self.add_task_interactive()
            elif choice == "2":
                self.view_tasks_interactive()
            elif choice == "3":
                self.update_task_interactive()
            elif choice == "4":
                self.mark_complete_interactive()
            elif choice == "5":
                self.delete_task_interactive()
            elif choice == "6":
                print("\n👋 Thank you for using Todo List Manager!")
                print("Goodbye!\n")
                break
            else:
                print("\n❌ Invalid choice. Please enter a number between 1 and 6.")
            
            # Pause before showing menu again
            input("\nPress Enter to continue...")

