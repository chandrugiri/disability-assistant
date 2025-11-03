#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system('pip install langchain openai chromadb unstructured pdfminer.six')


# In[10]:


#To clear the exisiting chroma_db
import shutil
import os

if os.path.exists("chroma_db2"):
    shutil.rmtree("chroma_db2")


# In[2]:

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# In[3]:


from pathlib import Path

# Folder with PDFs
doc_folder = Path("C:/Users/giric/Downloads/Training Docs")
all_docs = []

# Load all PDFs in the folder
for file in doc_folder.glob("*.pdf"):
    print(f"Loading: {file.name}")
    loader = PyPDFLoader(str(file))
    documents = loader.load()
    all_docs.extend(documents)

print(f"Total documents loaded: {len(all_docs)}")


# In[4]:


# Use LangChain's recommended splitter
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(all_docs)

print(f"Total text chunks created: {len(chunks)}")


# In[5]:


unique_texts = set()
unique_chunks = []

for doc in chunks:
    if doc.page_content not in unique_texts:
        unique_chunks.append(doc)
        unique_texts.add(doc.page_content)

print(f"Unique chunks: {len(unique_chunks)}")


# In[6]:


# Choose a folder to persist the vector DB
persist_directory = "chroma_db2"

# Embed and store
embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
db = Chroma.from_documents(chunks, embedding, persist_directory=persist_directory)

# Save the DB to disk
db.persist()

print("✅ Done! Embeddings stored in Chroma vector DB.")


# In[7]:


query = "how can we improve the quality of life for people with disabilities?"

results = db.similarity_search(query, k=3)

for i, doc in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content)


# In[12]:


# Reload DB and inspect a document + vector
from langchain.vectorstores import Chroma

embedding = OpenAIEmbeddings()
db = Chroma(persist_directory="chroma_db2", embedding_function=embedding)

# Get all collection contents
query = ""
results = db.similarity_search(query, k=3)

for i, doc in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content)
    print("Source:", doc.metadata)


# In[ ]: