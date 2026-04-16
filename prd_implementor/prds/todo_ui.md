# PRD: Todo List UI

## Overview
Using Todo UI Build a react frondend that support all the operations of the Todo List API.

## Requirements

### Core Data Model
- Each todo has: id (auto-generated UUID), title (string, required), description (string, optional), status (pending/in_progress/done), created_at (datetime), updated_at (datetime)
- Todos are stored in memory (no database)

### Operations
- **Create**: Add a new todo with title and optional description. Status defaults to "pending".
- **List**: Return all todos. Support filtering by status.
- **Get**: Retrieve a single todo by ID. Raise error if not found.
- **Update**: Modify title, description, or status of an existing todo. Updates `updated_at`.
- **Delete**: Remove a todo by ID. Raise error if not found.
- **Statistics**: Return count of todos per status.

### Validation
- Title must be non-empty and max 200 characters
- Status transitions: pending -> in_progress -> done (no skipping, no going back)
- Description max 2000 characters

### Acceptance Criteria
- [ ] Can create a todo and retrieve it by ID
- [ ] Creating a todo with empty title raises ValueError
- [ ] Listing with status filter returns only matching todos
- [ ] Invalid status transition raises ValueError
- [ ] Statistics correctly counts todos per status
- [ ] Delete removes the todo and subsequent get raises error
