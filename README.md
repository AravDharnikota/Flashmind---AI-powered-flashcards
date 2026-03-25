# FlashMind 🧠

An AI-powered flashcard web app. Upload your notes or PDFs and FlashMind automatically generates study flashcards using GPT.

---

## Features

- **AI Flashcard Generation** — Upload PDFs and GPT-4o generates flashcards from your notes
- **Multiple File Support** — Upload multiple files per set; all content is combined into one cohesive deck
- **Flip Cards** — Click any card to reveal the answer
- **Flag Cards** — Mark cards you got wrong so you can focus on them later
- **User Accounts** — Sign up, log in, and keep your sets saved to your profile

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | MongoDB Atlas (PyMongo) |
| AI | OpenAI GPT-4o Mini |
| PDF Parsing | pdfplumber |
| Frontend | Bootstrap 5 + Jinja2 |
| Auth | passlib (sha256_crypt) |

---

## Getting Started

### 1. Clone the repo

```bash
git clone <repo-url>
cd ai-flashcards
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install flask pymongo python-dotenv passlib pdfplumber openai
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```
MONGO_USER=your_mongo_username
MONGO_PASSWORD=your_mongo_password
OPENAI_API_KEY=sk-...
SECRET_KEY=any_random_string
```

### 5. Run the app

```bash
python app.py
```

Visit `http://localhost:5000`

---

## How It Works

1. Sign up and log in
2. Create a new flashcard set
3. Upload your PDF notes
4. FlashMind extracts the text and sends it to GPT
5. GPT returns flashcards as JSON — they're saved to MongoDB and displayed instantly
6. Click cards to flip, use arrows to navigate, flag ones you miss
