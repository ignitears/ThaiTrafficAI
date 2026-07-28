import os
import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from rag_manager import RAGManager
import webbrowser
import threading
import time
app = FastAPI()

# Connect to the local GPU-powered model
MODEL_PATH = "Model/Model.gguf"
rag = RAGManager(model_path=MODEL_PATH)
waiting_room = {}

# Payload Models
class ChatPayload(BaseModel):
    message: str
    history: list[dict]
    tsundere: bool = False

class RequestPayload(BaseModel):
    username: str

class ApprovePayload(BaseModel):
    username: str
    status: str

class TsunderePayload(BaseModel):
    tsundere: bool


# --- NEW / UPDATED ENDPOINTS ---

@app.post("/api/set-tsundere")
async def set_tsundere(payload: TsunderePayload):
    # Update state directly on the rag_manager instance
    rag.is_tsundere = payload.tsundere
    if payload.tsundere:
        print("tsundere on")
    else:
        print("tsundere off")
    return {"status": "success", "is_tsundere": payload.tsundere}

@app.post("/api/reset-session")
async def reset_session(payload: TsunderePayload):
    rag.is_tsundere = payload.tsundere
    if hasattr(rag, "clear_history"):
        rag.clear_history()
    if hasattr(rag, "clear_cache"):
        rag.clear_cache()
    print(f"Session reset complete. Tsundere mode: {payload.tsundere}")
    return {"status": "success", "is_tsundere": payload.tsundere}

# --- EXISTING ENDPOINTS & MIDDLEWARE ---

@app.middleware("http")
async def security_guard(request: Request, call_next):
    client_ip = request.client.host
    path = request.url.path

    if client_ip in ("127.0.0.1", "::1", "localhost") or path.startswith("/api/") or path in ("/waiting.html", "/style.css", "/manifest.json"):
        return await call_next(request)

    is_approved = any(data["status"] == "approved" and data["ip"] == client_ip for data in waiting_room.values())
    
    if not is_approved:
        return RedirectResponse(url="/waiting.html")

    return await call_next(request)

@app.post("/api/chat")
async def chat(payload: ChatPayload):
    reply = rag.generate_answer(
        user_query=payload.message,
        history=payload.history,
        is_tsundere=payload.tsundere
    )
    return {"reply": reply}

@app.get("/api/characters")
async def get_characters():
    return {"characters": ["Traffic Law AI"], "current": "Traffic Law AI"}

@app.get("/api/debug")
async def get_debug_data():
    return {"state": {"Status": "Database Active"}, "attributes": {}, "memories": []}

@app.get("/api/history")
async def get_history(offset: int = 0, limit: int = 20):
    return [] 

@app.post("/api/request-access")
async def request_access(payload: RequestPayload, request: Request):
    waiting_room[payload.username] = {"status": "pending", "ip": request.client.host}
    return {"status": "success"}

@app.get("/api/check-status")
async def check_status(username: str):
    user_data = waiting_room.get(username, {"status": "denied"})
    return {"status": user_data.get("status", "denied")}

@app.post("/api/approve-user")
async def approve_user(payload: ApprovePayload):
    if payload.username in waiting_room:
        waiting_room[payload.username]["status"] = payload.status
    return {"status": "success"}

@app.get("/api/waiting-list")
async def get_waiting_list():
    pending = [name for name, data in waiting_room.items() if data["status"] == "pending"]
    return {"pending_users": pending}

    app.mount("/", StaticFiles(directory="public", html=True), name="public")