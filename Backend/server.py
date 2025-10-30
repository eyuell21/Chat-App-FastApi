from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global storage

messages = []
active_connections: list[WebSocket] = []

# Pydantic models

class MessageCreate(BaseModel):
    message: str

class Reaction(BaseModel):
    timestamp: str

# HTTP endpoints

@app.get("/messages")
async def get_messages():
    """Return all messages as JSON."""
    return JSONResponse(content=messages)

@app.post("/messages")
async def post_message(data: MessageCreate):
    """Add a new message and broadcast it to all WebSocket clients."""
    text = data.message.strip()
    if not text:
        return JSONResponse(status_code=400, content={"error": "Message is required"})

    new_msg = {
        "text": text,
        "timestamp": datetime.utcnow().isoformat(),
        "likes": 0,
        "dislikes": 0,
    }
    messages.append(new_msg)

    await broadcast(new_msg)
    return JSONResponse(status_code=201, content={"success": True})

@app.post("/like")
async def like_message(data: Reaction):
    """Increment likes for a message."""
    msg = next((m for m in messages if m["timestamp"] == data.timestamp), None)
    if not msg:
        return JSONResponse(status_code=404, content={"error": "Message not found"})

    msg["likes"] += 1
    await broadcast(msg)
    return JSONResponse(status_code=200, content=msg)

@app.post("/dislike")
async def dislike_message(data: Reaction):
    """Increment dislikes for a message."""
    msg = next((m for m in messages if m["timestamp"] == data.timestamp), None)
    if not msg:
        return JSONResponse(status_code=404, content={"error": "Message not found"})

    msg["dislikes"] += 1
    await broadcast(msg)
    return JSONResponse(status_code=200, content=msg)

# WebSocket endpoint

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections and disconnections."""
    await websocket.accept()
    active_connections.append(websocket)
    print("WebSocket client connected")

    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("WebSocket client disconnected")

# Helper function to broadcast updates

async def broadcast(message: dict):
    """Send a JSON message to all connected WebSocket clients."""
    data = json.dumps(message)
    for connection in active_connections:
        try:
            await connection.send_text(data)
        except Exception:
            pass  # ignore disconnected clients


# Entry point

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # use Coolify's dynamic port if provided
    uvicorn.run("main:app", host="0.0.0.0", port=port)
