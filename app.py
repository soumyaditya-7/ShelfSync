import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Use /tmp on Vercel (read-only filesystem), local path otherwise
DB_PATH = '/tmp/library.db' if os.environ.get('VERCEL') else 'library.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            isbn TEXT NOT NULL,
            issue_date TEXT,
            due_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (isbn) REFERENCES books (isbn)
        )
    ''')
    # Migrate existing DB: safely add columns if they don't exist
    for col, default in [('issue_date', 'NULL'), ('due_date', 'NULL')]:
        try:
            conn.execute(f'ALTER TABLE issued_books ADD COLUMN {col} TEXT DEFAULT {default}')
        except sqlite3.OperationalError:
            pass  # Column already exists
    conn.commit()
    conn.close()

# Initialize Database Schema
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return jsonify([dict(b) for b in books])

@app.route('/api/add', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    isbn = data.get('isbn')
    try:
        copies = int(data.get('copies', 1))
        if copies <= 0:
            return jsonify({"error": "Copies must be greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid copies amount"}), 400

    if not title or not author or not isbn:
        return jsonify({"error": "Missing book details"}), 400

    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE isbn = ?', (isbn,)).fetchone()
    if book:
        conn.execute('UPDATE books SET total_copies = total_copies + ?, available_copies = available_copies + ? WHERE isbn = ?', (copies, copies, isbn))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Added {copies} copies to existing book."})
    else:
        conn.execute('INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)', (title, author, isbn, copies, copies))
        conn.commit()
        conn.close()
        return jsonify({"message": "New book added successfully."})

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students_data = conn.execute('SELECT * FROM students').fetchall()
    
    students_list = []
    for s in students_data:
        issued = conn.execute('SELECT isbn, due_date FROM issued_books WHERE student_id = ?', (s['id'],)).fetchall()
        issued_isbns = [i['isbn'] for i in issued]
        due_dates = [i['due_date'] for i in issued]
        students_list.append({
            "id": s['id'],
            "name": s['name'],
            "issued_books": issued_isbns,
            "due_dates": due_dates
        })
    conn.close()
    return jsonify(students_list)

@app.route('/api/add_student', methods=['POST'])
def add_student():
    data = request.json
    student_id = data.get('id')
    name = data.get('name')
    if not student_id or not name:
        return jsonify({"error": "Missing student details"}), 400
        
    conn = get_db_connection()
    existing = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Student ID already exists"}), 400
        
    conn.execute('INSERT INTO students (id, name) VALUES (?, ?)', (student_id, name))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student added successfully"})

@app.route('/api/edit_student', methods=['POST'])
def edit_student():
    data = request.json
    student_id = data.get('id')
    new_name = data.get('name')
    if not student_id or not new_name:
        return jsonify({"error": "Missing student details"}), 400
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    conn.execute('UPDATE students SET name = ? WHERE id = ?', (new_name, student_id))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Student {student_id} updated successfully."})

@app.route('/api/delete_student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    # Restore books to inventory before deleting
    issued = conn.execute('SELECT isbn FROM issued_books WHERE student_id = ?', (student_id,)).fetchall()
    for book in issued:
        conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE isbn = ?', (book['isbn'],))
    conn.execute('DELETE FROM issued_books WHERE student_id = ?', (student_id,))
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Student {student_id} deleted and {len(issued)} book(s) returned to inventory."})

@app.route('/api/issue', methods=['POST'])
def issue_book():
    data = request.json
    isbn = data.get('isbn')
    student_id = data.get('student_id')
    
    if not student_id or not isbn:
        return jsonify({"error": "Student ID and ISBN are required."}), 400
        
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found."}), 404
        
    issued_count = conn.execute('SELECT COUNT(*) as count FROM issued_books WHERE student_id = ?', (student_id,)).fetchone()['count']
    if issued_count >= 3:
        conn.close()
        return jsonify({"error": "Issue limit reached. Maximum 3 books allowed per student."}), 400
    
    book = conn.execute('SELECT * FROM books WHERE isbn = ?', (isbn,)).fetchone()
    if not book:
        conn.close()
        return jsonify({"error": "Book not found in library."}), 404
        
    if dict(book)['available_copies'] > 0:
        duration_days = int(data.get('duration_days', 10))
        issue_date = datetime.utcnow()
        due_date = (issue_date + timedelta(days=duration_days)).strftime('%Y-%m-%d')
        issue_date_str = issue_date.strftime('%Y-%m-%d')

        conn.execute('UPDATE books SET available_copies = available_copies - 1 WHERE isbn = ?', (isbn,))
        conn.execute('INSERT INTO issued_books (student_id, isbn, issue_date, due_date) VALUES (?, ?, ?, ?)', 
                     (student_id, isbn, issue_date_str, due_date))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Issued '{dict(book)['title']}' to {dict(student)['name']} successfully. Due: {due_date}"})
    else:
        conn.close()
        return jsonify({"error": "Book is currently out of stock."}), 400

@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.json
    isbn = data.get('isbn')
    student_id = data.get('student_id')
    
    if not student_id or not isbn:
        return jsonify({"error": "Student ID and ISBN are required."}), 400
        
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found."}), 404
        
    issued_record = conn.execute('SELECT * FROM issued_books WHERE student_id = ? AND isbn = ?', (student_id, isbn)).fetchone()
    if not issued_record:
        conn.close()
        return jsonify({"error": "This book was not issued to this student."}), 400
    
    book = conn.execute('SELECT * FROM books WHERE isbn = ?', (isbn,)).fetchone()
    if not book:
        conn.close()
        return jsonify({"error": "Book not found in library."}), 404
        
    fine_str = ""
    due_date_str = dict(issued_record).get('due_date')
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            today = datetime.utcnow().date()
            if today > due_date:
                days_overdue = (today - due_date).days
                fine = days_overdue * 30
                fine_str = f" Late payment of ₹{fine} collected."
        except ValueError:
            pass

    if dict(book)['available_copies'] < dict(book)['total_copies']:
        conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE isbn = ?', (isbn,))
        conn.execute('DELETE FROM issued_books WHERE id = (SELECT id FROM issued_books WHERE student_id = ? AND isbn = ? LIMIT 1)', (student_id, isbn))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Returned '{dict(book)['title']}' successfully.{fine_str}"})
    else:
        conn.close()
        return jsonify({"error": "All copies of this book are already in the library."}), 400

@app.route('/api/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    conn = get_db_connection()
    like_query = f"%{query}%"
    results = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?', 
                           (like_query, like_query, like_query)).fetchall()
    conn.close()
    return jsonify([dict(b) for b in results])

@app.route('/api/issued_books', methods=['GET'])
def get_issued_books():
    conn = get_db_connection()
    query = '''
        SELECT ib.id, ib.student_id, s.name as student_name, ib.isbn, b.title as book_title,
               ib.issue_date, ib.due_date
        FROM issued_books ib
        JOIN students s ON ib.student_id = s.id
        JOIN books b ON ib.isbn = b.isbn
    '''
    issued_records = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(r) for r in issued_records])

if __name__ == '__main__':
    app.run(debug=True, port=8000)
