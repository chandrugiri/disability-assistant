import os, time, jwt
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional
from flask import Flask, request, jsonify

# --- Load environment variables ---
load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

app = FastAPI(title="LiveKit Token Server")

# Allow calls from Flutter or web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_join_token(identity: str, room: str, ttl: int = 3600):
    """Create a signed JWT join token for LiveKit."""
    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": identity,
        "exp": int(time.time()) + ttl,
        "video": {
            "room": room,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True
        }
    }
    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
    return token

@app.get("/get_token")
def get_token(identity: str = Query(...), room: Optional[str] = None):
    """Return token + room name + URL for given user identity."""
    if not room:
        room = f"disability_room_{identity}"
    token = create_join_token(identity, room)
    return {
        "identity": identity,
        "room_name": room,
        "token": token,
        "livekit_url": LIVEKIT_URL
    }

@app.get("/")
def root():
    return {"status": "ok", "message": "LiveKit Token Server running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
