# SupportFlow API

SupportFlow is a role-based customer support backend built with FastAPI and PostgreSQL.

It provides a complete support-ticket workflow where customers create tickets, admins assign tickets to agents, and agents use AI assistance to analyze tickets and prepare suggested replies.

The project was built as a practical backend project to demonstrate authentication, authorization, database design, REST APIs, AI integration, and role-based access control.

---

## Features

- User registration and authentication
- Password hashing with Argon2
- JWT-based authentication
- Role-based authorization
- Customer, Agent, and Admin roles
- Customer ticket creation
- Admin ticket management
- Admin-to-Agent ticket assignment
- Agent assigned-ticket management
- Ticket status management
- Ticket priority management
- Ticket messaging
- Customer-Agent conversation
- AI-powered ticket analysis
- AI-generated suggested replies
- PostgreSQL database
- SQLAlchemy ORM
- Pydantic request/response validation
- Environment-based configuration

---

## User Roles

### Customer

Customers can:

- Create support tickets
- View their own tickets
- View messages from their tickets
- Send messages on their own tickets

### Agent

Agents can:

- View tickets assigned to them
- View ticket conversations
- Send replies to customers
- Update ticket status
- Update ticket priority
- Use AI assistance to analyze tickets

### Admin

Admins can:

- View all tickets
- Assign tickets to agents
- Manage users
- Update ticket status
- Update ticket priority
- Access administrative functionality

---

## Ticket Workflow

```text
Customer
   |
   | Create Ticket
   v
Ticket
   |
   | Admin assigns
   v
Agent
   |
   | AI analyzes ticket
   v
AI Suggestion
   |
   | Agent reviews/edits
   v
Agent Reply
   |
   v
Customer
   |
   | Issue solved
   v
RESOLVED