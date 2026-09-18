from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from content_agent import ContentAgent
from models import ContentRequest


app = FastAPI(title="Content Creation Agent")

agent = ContentAgent()
sessions = {}


class GenerateRequest(BaseModel):
    topic: str
    platform: str
    audience: str
    mood: str
    length: str
    goal: str


class SelectRequest(BaseModel):
    session_id: str
    option_id: str


class ReviseRequest(BaseModel):
    session_id: str
    revision_request: str


class ApproveRequest(BaseModel):
    session_id: str


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/api/generate")
def generate(request: GenerateRequest):
    content_request = ContentRequest(
        topic=request.topic,
        platform=request.platform,
        audience=request.audience,
        mood=request.mood,
        length=request.length,
        goal=request.goal,
    )

    session = agent.generate_options(content_request)
    session_id = str(uuid4())
    sessions[session_id] = session

    return {
        "session_id": session_id,
        "state": session.state,
        "options": [
            {
                "id": option.id,
                "title": option.title,
                "content": option.content,
            }
            for option in session.options
        ],
    }


@app.post("/api/select")
def select(request: SelectRequest):
    session = sessions.get(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    session = agent.select_option(session, request.option_id)

    return {
        "session_id": request.session_id,
        "state": session.state,
        "selected_option": session.selected_option,
        "content": session.current_content,
        "revision_count": session.revision_count,
    }


@app.post("/api/revise")
def revise(request: ReviseRequest):
    session = sessions.get(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not request.revision_request.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a revision request."
        )

    session = agent.revise(
        session,
        request.revision_request.strip()
    )

    return {
        "session_id": request.session_id,
        "state": session.state,
        "selected_option": session.selected_option,
        "content": session.current_content,
        "revision_count": session.revision_count,
    }


@app.post("/api/approve")
def approve(request: ApproveRequest):
    session = sessions.get(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    session = agent.approve(session)

    return {
        "session_id": request.session_id,
        "state": session.state,
        "content": session.current_content,
        "approved": session.approved,
    }


app.mount("/static", StaticFiles(directory="static"), name="static")
