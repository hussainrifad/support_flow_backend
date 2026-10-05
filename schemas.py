from pydantic import BaseModel, ConfigDict
from enum import Enum


class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: str
    password: str

class TicketCreate(BaseModel):
    title: str
    description: str

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    customer_id: int
    assigned_agent_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class TicketAssign(BaseModel):
    agent_id: int

class MessageCreate(BaseModel):
    message: str

class MessageResponse(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    message: str

    model_config = ConfigDict(from_attributes=True)

class TicketStatusUpdate(BaseModel):
    status: str

class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"

class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TicketPriorityUpdate(BaseModel):
    priority: TicketPriority


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketAssign(BaseModel):
    agent_id: int

class AIAnalysisResponse(BaseModel):
    category: str
    priority: str
    summary: str
    suggested_reply: str