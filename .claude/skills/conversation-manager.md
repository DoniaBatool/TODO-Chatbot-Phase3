---
description: Manage conversation state in database with message history, user isolation, and efficient querying (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Creates database-centric conversation management following Phase 3 constitution.

### 1. Create Conversation Models

```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(index=True)
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Create Conversation Manager

```python
class ConversationManager:
    async def create_conversation(self, user_id: str) -> Conversation:
        """Create new conversation"""
        pass

    async def get_conversation(self, user_id: str, conversation_id: int) -> Optional[Conversation]:
        """Get conversation with user isolation"""
        pass

    async def get_message_history(self, conversation_id: int, user_id: str, limit: int = 50) -> List[Message]:
        """Fetch message history (limited per constitution)"""
        pass

    async def add_message(self, conversation_id: int, user_id: str, role: str, content: str) -> Message:
        """Store message in database"""
        pass
```

### 3. Success Criteria

- [ ] Conversations stored in database
- [ ] Messages persist with conversation_id
- [ ] User isolation enforced
- [ ] History limited to 50 messages
- [ ] Indexes on user_id and conversation_id

## Notes
- Used by chat endpoint for state management
- Enables stateless server architecture
