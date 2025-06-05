import os
import requests
import pickle
import faiss
import numpy as np
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

# === CONFIG ===
URL_LIST_FILE = "cursorlessDocuments.txt"
INDEX_FILE = "kb.index"
DOCS_FILE = "kb_docs.pkl"
OPENAI_MODEL = "text-embedding-3-small"
GPT_MODEL = "gpt-4"
CHUNK_SIZE = 1000
MIN_CHUNK_LEN = 50

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
dimension = 1536

# === Scraping & Embedding Utilities ===

def scrape_text(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return ""

def get_embedding(text):
    try:
        response = client.embeddings.create(
            model=OPENAI_MODEL,
            input=text
        )
        return np.array(response.data[0].embedding, dtype='float32')
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return None

def build_knowledge_base():
    print("🔨 Building knowledge base...")
    with open(URL_LIST_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    index = faiss.IndexFlatL2(dimension)
    documents = []
    vector_count = 0

    for url in urls:
        print(f"🔗 Scraping: {url}")
        full_text = scrape_text(url)
        chunks = [full_text[i:i+CHUNK_SIZE] for i in range(0, len(full_text), CHUNK_SIZE)]
        for chunk in chunks:
            if len(chunk.strip()) >= MIN_CHUNK_LEN:
                embedding = get_embedding(chunk)
                if embedding is not None:
                    index.add(np.array([embedding]))
                    documents.append(chunk)
                    vector_count += 1

    faiss.write_index(index, INDEX_FILE)
    with open(DOCS_FILE, "wb") as f:
        pickle.dump(documents, f)

    print(f"📦 Total documents added: {len(documents)}")
    print(f"📦 FAISS vectors indexed: {index.ntotal}")

def ensure_kb():
    if not (os.path.exists(INDEX_FILE) and os.path.exists(DOCS_FILE)):
        print("⚠️  Knowledge base missing. Rebuilding...")
        build_knowledge_base()

# === FastAPI Logic ===

class Query(BaseModel):
    question: str

def embed_question(question):
    response = client.embeddings.create(
        input=question,
        model=OPENAI_MODEL
    )
    return np.array(response.data[0].embedding, dtype='float32')

def create_prompt(context, question):
    return f"""Answer using only the following knowledge. If unsure, say "I don't know."

---
{context}
---

Q: {question}
A:"""

# === App Startup ===

ensure_kb()
index = faiss.read_index(INDEX_FILE)
with open(DOCS_FILE, "rb") as f:
    documents = pickle.load(f)

@app.post("/ask")
async def ask(query: Query):
    try:
        print(f"🔍 Received question: {query.question}")

        if index.ntotal == 0 or len(documents) == 0:
            raise RuntimeError("Knowledge base is empty. Check that URLs scraped properly and embeddings succeeded.")

        embedding = embed_question(query.question)
        _, I = index.search(np.array([embedding]), k=3)

        context = "\n".join([
            documents[i] for i in I[0] if i < len(documents)
        ])

        prompt = create_prompt(context, query.question)

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "Use only the provided context."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
        print("✅ Answer generated.")
        return {"answer": answer}
    except Exception as e:
        print("❌ Error in /ask endpoint:", e)
        return {"error": str(e)}
