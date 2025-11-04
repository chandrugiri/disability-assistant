#!/usr/bin/env python
# coding: utf-8

import uvicorn
import time, jwt
from fastapi import FastAPI, Query
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os, zipfile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from dotenv import load_dotenv

# ✅ Automatically unzip if chroma_db2 folder doesn’t exist
if not os.path.exists("chroma_db2") and os.path.exists("chroma_db2.zip"):
    with zipfile.ZipFile("chroma_db2.zip", "r") as zip_ref:
        zip_ref.extractall(".")
    print("✅ Unzipped chroma_db2.zip")

# ✅ Auto-detect nested folder
persist_dir = "chroma_db2"
if os.path.exists("chroma.sqlite3"):
    persist_dir = "."
else:
    persist_dir = "chroma_db2"
# if not os.path.exists(os.path.join(persist_dir, "chroma.sqlite3")):
#     nested_path = os.path.join(persist_dir, "chroma_db2")
#     if os.path.exists(nested_path):
#         persist_dir = nested_path

print("📁 Using persist_directory:", persist_dir)
# Set API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Load vector DB
# persist_dir = "chroma_db2"
embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
db = Chroma(persist_directory=persist_dir, embedding_function=embedding, collection_name="langchain")

try:
    print("📦 Server collection count:", db._collection.count())
except Exception as e:
    print("⚠️ count() failed:", e)

# 🧪 Diagnostic: check collections
try:
    print("🧪 Checking Chroma collections...")
    collections = db._client.list_collections()
    print("📚 Found collections:", collections)
except Exception as e:
    print("⚠️ Could not list collections:", e)

# Define FastAPI app
app = FastAPI()

# CORS middleware (optional for n8n access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class QueryRequest(BaseModel):
    query: str
    k: int = 10

@app.post("/search")
async def search_vectors(request: QueryRequest):
    results = db.max_marginal_relevance_search(request.query, k=request.k, fetch_k=12)
    return {
        "matches": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            } for doc in results
        ]
    }


# In[3]:


# Start Uvicorn server inside notebook
#uvicorn.run(app, host="0.0.0.0", port=8000)


# In[ ]:


# --- Load environment variables ---
load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# app = FastAPI(title="LiveKit Token Server")

# Allow calls from Flutter or web apps
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],          # tighten later in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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

class TokenRequest(BaseModel):
    identity: str
    room: Optional[str] = None

@app.post("/get_token")
def get_token(req: TokenRequest):
    """Return token + room name + URL for given user identity."""
    identity = req.identity
    room = req.room or f"disability_room_{identity}"
    token = create_join_token(identity, room)
    return {
        "identity": identity,
        "room_name": room,
        "token": token,
        "livekit_url": LIVEKIT_URL
    }
# @app.get("/get_token")
# def get_token(identity: str = Query(...), room: Optional[str] = None):
#     """Return token + room name + URL for given user identity."""
#     if not room:
#         room = f"disability_room_{identity}"
#     token = create_join_token(identity, room)
#     return {
#         "identity": identity,
#         "room_name": room,
#         "token": token,
#         "livekit_url": LIVEKIT_URL
#     }



