from fastapi import APIRouter, Depends, HTTPException
from openai import RateLimitError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.session import Session as SessionModel
from app.models.message import Message
from app.schemas.session import SessionCreate
from app.schemas.message import MessageCreate
from app.services.openai_service import generate_response, get_usage
from app.services.pricing_service import calculate_cost


router = APIRouter()


@router.post("/sessions")
def create_session(
    request: SessionCreate,
    db: Session = Depends(get_db)
):
    session = SessionModel(
        model=request.model
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "model": session.model
    }


@router.post("/sessions/{session_id}/messages")
def send_message(
    session_id: str,
    request: MessageCreate,
    db: Session = Depends(get_db)
):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    history = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in history
    ]

    messages.append({
        "role": "user",
        "content": request.content
    })

    try:
        response = generate_response(
            model=session.model,
            messages=messages
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="OpenAI API quota exceeded"
        )

    usage = get_usage(response)

    input_tokens = usage["input_tokens"]
    output_tokens = usage["output_tokens"]
    total_tokens = usage["total_tokens"]

    cost = calculate_cost(
        model=session.model,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )

    assistant_content = response.output_text

    user_message = Message(
        session_id=session.id,
        role="user",
        content=request.content
    )

    assistant_message = Message(
    session_id=session.id,
    role="assistant",
    content=assistant_content,
    input_tokens=input_tokens,
    output_tokens=output_tokens,
    total_tokens=total_tokens,
    cost=cost
    )

    db.add(user_message)
    db.add(assistant_message)
    db.commit()

    return {
    "session_id": session.id,
    "response": assistant_content,
    "usage": {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    },
    "cost": cost
    }

@router.get("/sessions/{session_id}/messages")
def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return [
    {
        "id": message.id,
        "session_id": message.session_id,
        "role": message.role,
        "content": message.content,
        "input_tokens": message.input_tokens,
        "output_tokens": message.output_tokens,
        "total_tokens": message.total_tokens,
        "cost": message.cost,
        "created_at": message.created_at
    }
    for message in messages
    ]

@router.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    total_tokens = sum(
        message.total_tokens or 0
        for message in messages
    )

    total_cost = sum(
        float(message.cost or 0)
        for message in messages
    )

    return {
        "session_id": session.id,
        "model": session.model,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "input_tokens": message.input_tokens,
                "output_tokens": message.output_tokens,
                "total_tokens": message.total_tokens,
                "cost": message.cost,
                "created_at": message.created_at
            }
            for message in messages
        ],
        "total_tokens": total_tokens,
        "total_cost": total_cost
    }