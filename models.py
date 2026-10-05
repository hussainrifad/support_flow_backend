from sqlalchemy import Integer, Column, String
from database import Base

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="CUSTOMER")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    status = Column(String, default="OPEN")
    priority = Column(String, default="MEDIUM")

    customer_id = Column(Integer, nullable=False)
    assigned_agent_id = Column(Integer, nullable=True)

class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True)

    ticket_id = Column(Integer, nullable=False)
    sender_id = Column(Integer, nullable=False)

    message = Column(String, nullable=False)