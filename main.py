from fastapi import FastAPI, Depends, HTTPException, Header
from database import Base, engine
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from database import get_db
from schemas import UserCreate, UserUpdate, UserResponse, UserLogin, TicketCreate, TicketResponse, MessageCreate, MessageResponse, AIAnalysisResponse, TicketAssign, TicketStatusUpdate, TicketStatus, TicketPriority, TicketPriorityUpdate
from models import User, Ticket, TicketMessage
from sqlalchemy.orm import Session
from security import hash_password, verify_password, create_access_token, decode_access_token
from services.ai_service import analyze_ticket

Base.metadata.create_all(bind=engine)
security = HTTPBearer()
app = FastAPI()

def require_role(required_role: str):
    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

        return current_user

    return role_checker

def check_ticket_access(ticket, current_user):
    role = current_user["role"]
    user_id = current_user["user_id"]

    if role == "CUSTOMER":
        if ticket.customer_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif role == "AGENT":
        if ticket.assigned_agent_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif role == "ADMIN":
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload

@app.post("/users", response_model= UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users", response_model= list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users

@app.get("/users/{user_id}", response_model = UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail = "user not found"
        )
    return user

@app.patch("/users/{user_id}", response_model = UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )
    
    if user_data.name is not None:
        user.name = user_data.name
    
    if user_data.email is not None:
        user.email = user_data.email
    
    db.commit()
    db.refresh(user)

    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code= 404,
            detail= "user not found"
        )

    db.delete(user)
    db.commit()

    return{
        "message": "user deleted successfully"
    }

@app.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter( User.email == user_data.email).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
    "user_id": user.id,
    "email": user.email,
    "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == current_user["user_id"]
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@app.get("/admin/test")
def admin_test(
    current_user: dict = Depends(require_role("ADMIN"))
):
    return {
        "message": "Welcome Admin",
        "user": current_user
    }

@app.post("/tickets", response_model=TicketResponse)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        customer_id=current_user["user_id"]
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket

@app.get("/tickets", response_model=list[TicketResponse])
def get_my_tickets(
    current_user: dict = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).filter(
        Ticket.customer_id == current_user["user_id"]
    ).all()

    return tickets

@app.get("/agent/tickets", response_model=list[TicketResponse])
def get_my_assigned_tickets(
    current_user: dict = Depends(require_role("AGENT")),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).filter(
        Ticket.assigned_agent_id == current_user["user_id"]
    ).all()

    return tickets

@app.patch("/tickets/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    assignment: TicketAssign,
    current_user: dict = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    agent = db.query(User).filter(
        User.id == assignment.agent_id,
        User.role == "AGENT"
    ).first()

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    ticket.assigned_agent_id = agent.id

    db.commit()
    db.refresh(ticket)

    return ticket

@app.get("/agent/my-tickets", response_model=list[TicketResponse])
def get_my_assigned_tickets(
    current_user: dict = Depends(require_role("AGENT")),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).filter(
        Ticket.assigned_agent_id == current_user["user_id"]
    ).all()

    return tickets

@app.post(
    "/tickets/{ticket_id}/messages",
    response_model=MessageResponse
)
def send_message(
    ticket_id: int,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if current_user["role"] == "CUSTOMER":
        if ticket.customer_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif current_user["role"] == "AGENT":
        if ticket.assigned_agent_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif current_user["role"] == "ADMIN":
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

    new_message = TicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user["user_id"],
        message=message_data.message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message

@app.get(
    "/tickets/{ticket_id}/messages",
    response_model=list[MessageResponse]
)
def get_ticket_messages(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if current_user["role"] == "CUSTOMER":
        if ticket.customer_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif current_user["role"] == "AGENT":
        if ticket.assigned_agent_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif current_user["role"] == "ADMIN":
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

    messages = db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id
    ).all()

    return messages

@app.patch(
    "/tickets/{ticket_id}/status",
    response_model=TicketResponse
)
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if current_user["role"] == "AGENT":
        if ticket.assigned_agent_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif current_user["role"] == "ADMIN":
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

    ticket.status = status_data.status.value

    db.commit()
    db.refresh(ticket)

    return ticket


@app.post(
    "/tickets/{ticket_id}/ai-analyze",
    response_model=AIAnalysisResponse
)
def ai_analyze_ticket(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if current_user["role"] != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can use AI assistance"
        )

    if ticket.assigned_agent_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

    result = analyze_ticket(
        ticket.title,
        ticket.description
    )

    return result

@app.patch(
    "/tickets/{ticket_id}/priority",
    response_model=TicketResponse
)
def update_ticket_priority(
    ticket_id: int,
    priority_data: TicketPriorityUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if current_user["role"] == "AGENT":

        if ticket.assigned_agent_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission"
            )

    elif current_user["role"] == "ADMIN":
        pass

    else:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

    ticket.priority = priority_data.priority.value

    db.commit()
    db.refresh(ticket)

    return ticket
