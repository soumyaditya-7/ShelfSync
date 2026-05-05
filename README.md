<div align="center">
  <h1>📚 ShelfSync</h1>
  <p><em>Library Management System — Python College Assignment</em></p>

  [![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black.svg?logo=flask)](https://flask.palletsprojects.com/)
  [![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg?logo=sqlite)](https://www.sqlite.org/)
  [![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?logo=vercel)](https://shelf-sync-murex.vercel.app/)

  <br/>
  <a href="https://shelf-sync-murex.vercel.app/">
    <strong>🌐 View Live Demo → shelf-sync-murex.vercel.app</strong>
  </a>
</div>

---

## 📋 About This Project

**ShelfSync** is a **Python-based Library Management System** developed as a college assignment. The entire backend logic — including the web server, REST API, database operations, and business rules — is written in **Python**.

The project is delivered in **two versions**:

| Version | File | Description |
|---|---|---|
| **CLI Application** | `library_management.py` | Pure Python terminal app using OOP (Classes) — primary assignment deliverable |
| **Web Application** | `app.py` | Python Flask web server with a browser-based UI (extended version) |

---

## 🐍 Python Concepts Used

| Concept | Where Used |
|---|---|
| **Classes & Objects (OOP)** | `Book` and `Library` classes in `library_management.py` |
| **Functions & Methods** | `add_book()`, `issue_book()`, `return_book()`, `search_books()` |
| **Loops & Conditionals** | Menu-driven CLI loop, fine calculation logic |
| **Exception Handling** | `try/except` for invalid input and DB migrations |
| **File I/O / Database** | `sqlite3` module for persistent data storage |
| **Modules & Imports** | `sqlite3`, `datetime`, `os`, `flask` |
| **String Formatting** | f-strings throughout for user messages and queries |

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| **Add Books** | Add new titles or restock existing books by ISBN |
| **Register Members** | Add, edit, and delete student records |
| **Issue & Return** | Issue books to students with a configurable loan period |
| **Automated Fine System** | Calculates ₹30/day fine for overdue books automatically |
| **3-Book Limit** | Enforces a maximum of 3 issued books per student |
| **Real-time Search** | Filter the catalog instantly by title, author, or ISBN |
| **Dashboard** | Overview of total titles, copies, availability & active issues |
| **🎮 Trust Score System** | Every student starts with a score of **100**. Score drops **-5/day** for overdue books and gains **+2** for on-time returns. If score falls **below 50**, issuing new books is automatically blocked until fines are paid. |

---

## 🏗️ System Architecture

The web version follows a **Client-Server Architecture** with Python handling all server-side logic.

```
Browser (HTML/CSS/JS)
        │
        │  HTTP Requests (JSON)
        ▼
  Flask Web Server  ◄──── app.py (Python)
        │
        │  SQL Queries via sqlite3 module
        ▼
  SQLite Database  ◄──── library.db
```

### Database Schema

| Table | Columns |
|---|---|
| `books` | `id`, `title`, `author`, `isbn` (unique), `total_copies`, `available_copies` |
| `students` | `id` (primary key), `name`, `trust_score` (default 100) |
| `issued_books` | `id`, `student_id` (FK), `isbn` (FK), `issue_date`, `due_date` |

### Trust Score Rules

| Event | Score Change |
|---|---|
| Book returned on time or early | **+2 points** |
| Book overdue by N days | **-5 × N points** |
| Score drops below 50 | **Blocked from issuing new books** |
| Minimum possible score | **0** |
| Maximum possible score | **100** |

---

## 💻 How to Run Locally

### Prerequisites
- **Python 3.7+** must be installed.

### Option 1 — CLI Application (Primary Assignment)
The standalone terminal app. No extra libraries needed.
```bash
python library_management.py
```
Follow the menu prompts to add books, issue, return, and search.

### Option 2 — Web Application (Extended Version)
1. Install the Flask dependency:
   ```bash
   pip install flask
   ```
2. Run the server:
   ```bash
   python app.py
   ```
3. Open your browser at: **http://127.0.0.1:8000**

> A `library.db` SQLite file is auto-created on first run.

---

## 📁 Project Structure

```
ShelfSync/
│
├── library_management.py   # ✅ CLI app — pure Python OOP (primary deliverable)
├── app.py                  # Flask web server & REST API (extended version)
│
├── templates/
│   └── index.html          # Web UI (Single Page Application)
├── static/
│   ├── style.css           # Glassmorphism CSS styling
│   └── app.js              # Frontend JavaScript
│
├── library.db              # SQLite database (auto-generated)
├── requirements.txt        # Python dependencies (flask)
└── vercel.json             # Deployment configuration
```

---

## 👨‍💼 Submission Details
- **Student:** Soumyaditya
- **Assignment:** Python Programming — Library Management System
- **Language:** Python 3.12
- **Libraries Used:** `flask`, `sqlite3` (stdlib), `datetime` (stdlib), `os` (stdlib)
