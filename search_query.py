#!/usr/bin/env python
# coding: utf-8

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os, zipfile
from fastapi.middleware.cors import CORSMiddleware

# ✅ Automatically unzip if chroma_db2 folder doesn’t exist
if not os.path.exists("chroma_db2") and os.path.exists("chroma_db2.zip"):
    with zipfile.ZipFile("chroma_db2.zip", "r") as zip_ref:
        zip_ref.extractall(".")
    print("✅ Unzipped chroma_db2.zip")
# Set API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Load vector DB
persist_dir = "chroma_db2"
embedding = OpenAIEmbeddings()
db = Chroma(persist_directory=persist_dir, embedding_function=embedding)

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



