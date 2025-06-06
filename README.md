# Cursorless GPT Help Assistant

A local FastAPI-based tool that answers questions using only the content from a custom knowledge base built from a list of web pages.

This project is designed to:

- Scrape a list of URLs
- Chunk and embed their content using OpenAI's `text-embedding-3-small`
- Answer natural language questions using GPT-4 and only that knowledge
- Automatically rebuild the knowledge base on first launch if it's missing

---

## 📁 Project Files

All files are assumed to live in the same directory.
For myself I put them in my `~/.bin/` directory:

```
~/.bin/
├── serveCursorlessHelp.py        # FastAPI server with embedded index builder
├── cursorlessDocuments.txt       # List of URLs for the knowledge base (you can extend this)
├── askgptCursorless.sh           # CLI script to ask questions interactively
```

---

## 🛠 Setup Instructions

### ✅ 1. Install Python Dependencies

In your virtual environment, run:

```bash
pip install fastapi uvicorn openai faiss-cpu numpy requests beautifulsoup4
```

### ✅ 2. Set Your OpenAI API Key

Export your OpenAI key to the environment:

```bash
export OPENAI_API_KEY="sk-..."  # add to ~/.zshrc for persistence
```

### ✅ 3. Make CLI Script Executable

```bash
chmod +x ~/.bin/askgptCursorless.sh
```

---

## 🚀 How to Run

### ✅ Start the API Server

In the `~/.bin` directory:

```bash
uvicorn serveCursorlessHelp:app --reload
```

On first launch, it will:
- Scrape and embed all documents listed in `cursorlessDocuments.txt`
- Create `kb.index` and `kb_docs.pkl`
- Serve API at `http://localhost:8000`

### ✅ Ask Questions via Terminal

Run:

```bash
~/.bin/askgptCursorless.sh
```

It will prompt with:

```
askgpt: 
```

Type a natural-language question based on the knowledge base. It will return the best match or say "I don't know" if the info isn't present.

To exit: press `Ctrl+D` or enter a blank line.

---

## ✅ Example Usage

```bash
askgpt: how do I put the the cursor in front of a word
You can use the "pre <TARGET>" command to put the cursor in front of a target word. For example, "pre blue air" would move the cursor to before the token containing the letter 'a' with a blue hat.
```

Or in debug mode:

```bash
~/.bin/askgptCursorless.sh --debug
```
