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
            name TEXT NOT NULL,
            trust_score INTEGER DEFAULT 100
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
            
    try:
        conn.execute('ALTER TABLE students ADD COLUMN trust_score INTEGER DEFAULT 100')
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()

# Initialize Database Schema
init_db()

def seed_db():
    """Populate DB with sample data if empty."""
    conn = get_db_connection()
    book_count = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    if book_count > 0:
        conn.close()
        return  # Already seeded

    today = datetime.utcnow().date()

    books = [
        ("Clean Code",                   "Robert C. Martin",   "9780132350884", 5, 3),
        ("The Pragmatic Programmer",      "David Thomas",       "9780135957059", 4, 4),
        ("Introduction to Algorithms",   "Thomas H. Cormen",   "9780262033848", 6, 5),
        ("Python Crash Course",          "Eric Matthes",       "9781593279288", 8, 6),
        ("You Don't Know JS",            "Kyle Simpson",       "9781491924464", 3, 2),
        ("Design Patterns",              "Gang of Four",       "9780201633610", 4, 4),
        ("The Great Gatsby",             "F. Scott Fitzgerald","9780743273565", 3, 3),
        ("1984",                         "George Orwell",      "9780451524935", 5, 3),
        ("To Kill a Mockingbird",        "Harper Lee",         "9780060935467", 4, 4),
        ("Sapiens",                      "Yuval Noah Harari",  "9780062316097", 6, 5),
        ("Atomic Habits",               "James Clear",        "9780735211292", 7, 5),
        ("Deep Work",                    "Cal Newport",        "9781455586691", 3, 2),
    ]
    conn.executemany(
        'INSERT OR IGNORE INTO books (title, author, isbn, total_copies, available_copies) VALUES (?,?,?,?,?)',
        books
    )

    students = [
        ("240012292870", "NILADREE NASKAR"),
        ("240012300856", "ANANT KUMAR JHA"),
        ("240012327526", "PRAJWAL SAHA"),
        ("240012333749", "BIPRAJIT MONDAL"),
        ("240012343451", "DIPAYAN GHOSH"),
        ("240012358101", "SOURAV MAITY"),
        ("240012362486", "ANANT GUPTA"),
        ("240012395929", "ATISH KUMAR TIWARI"),
        ("240012418909", "RAHUL DUTTA"),
        ("240012421027", "SATYAJIT HALDAR"),
        ("240012430872", "KAMRAN HUSSAIN"),
        ("240012447517", "ARYA BANERJEE"),
        ("240012465577", "AAKASH KUMAR SHAW"),
        ("240012483821", "SOUBHIK DHARA"),
        ("240012490908", "ANUBHAV MAJUMDER"),
        ("240012500844", "MOHAMMAD ANAS KHAN"),
        ("240012518173", "SK. MINHAJ WAHID"),
        ("240012537316", "ARYAN SHARMA"),
        ("240012548427", "AYAAN ALI"),
        ("240012557975", "RAJ KUMAR SINGH"),
        ("240012567039", "ARKA MAJUMDER"),
        ("240012571276", "MD AMINUR RAHAMAN"),
        ("240012587960", "MD SALMAN BISWAS"),
        ("240012609170", "REESAV MAHATA"),
        ("240012632044", "RANANGAN PAL"),
        ("240012644056", "SOUVIK KUNDU"),
        ("240012658021", "DIMAN GORAI"),
        ("240012665391", "KUNTAL DAS"),
        ("240012672954", "AFSHAN AHMED"),
        ("240012681922", "SANTANU RAJAK"),
        ("240012692943", "WASHIM REJA"),
        ("240012704452", "NOWARUSH ALAM"),
        ("240012726145", "SOUMYADITYA DEBNATH"),
        ("240012730906", "KRISHNADAS DUTTA"),
        ("240012742994", "ABU SAHIL ISLAM SARDAR"),
        ("240012758687", "ATIF ANWAR SIDDIQUE"),
        ("240012768191", "ARNAB GAYEN"),
        ("240012770162", "SUSHIL KUMAR"),
        ("240012793031", "ADITYA MAJI"),
        ("240012807913", "KRISHNENDU HAZRA"),
        ("240012840234", "ABHIJEET DUBEY"),
        ("240012865477", "SUBHRAJEET DE"),
        ("240012875538", "ARKADEB DUTTA"),
        ("240012881321", "SUBHAYAN PAUL"),
        ("240012912458", "MD YOUSUF ALI"),
        ("240012921141", "SRIMANTA KUMAR ROY"),
        ("240012938220", "ZIDANE KARMAKAR"),
        ("240012952677", "SAHIN AFTAB"),
        ("240012964180", "ROHIT KUMAR"),
        ("240012987892", "AYAN GUPTA"),
        ("240012993148", "SOURADIP JANA"),
        ("240013018139", "PRIYAMJIT CHAKRABORTY"),
        ("240013044103", "ADARSH RAJ"),
        ("240013052648", "SAUMYADEEP PAUL"),
        ("240013062019", "MRIGANKA GANGULY"),
        ("240013086258", "HARDIK BASU"),
        ("240013116833", "SAYAN DAS"),
        ("240013123991", "SAIKAT SAHOO"),
        ("240013149800", "SUMANTA BAG"),
        ("240013158478", "SAYAN ANKUR"),
        ("240013161836", "MD WASIM ALAM"),
        ("240013177508", "SOUMYADIP DALUI"),
        ("240013183571", "RISHU KUMAR"),
        ("240013211451", "SAMIR KUMAR METE"),
        ("240013233720", "ARESH ANSARY"),
        ("240013244740", "ANKIT ACHARYA")
    ]
    conn.executemany('INSERT OR IGNORE INTO students (id, name) VALUES (?,?)', students)

    # Removed hardcoded issued books to ensure the ledger starts completely empty.

    conn.commit()
    conn.close()

# Seed with sample data
seed_db()

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
            "trust_score": s.get('trust_score', 100) if 'trust_score' in s.keys() else 100,
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
        
    trust_score = student.get('trust_score', 100) if 'trust_score' in student.keys() else 100
    if trust_score < 50:
        conn.close()
        return jsonify({"error": f"Issue blocked! Trust score is {trust_score} (Below 50). Fines must be paid."}), 400
        
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
    trust_change_str = ""
    current_trust = student.get('trust_score', 100) if 'trust_score' in student.keys() else 100
    new_trust = current_trust
    
    due_date_str = dict(issued_record).get('due_date')
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            today = datetime.utcnow().date()
            if today > due_date:
                days_overdue = (today - due_date).days
                fine = days_overdue * 30
                fine_str = f" Late payment of ₹{fine} collected."
                
                # Trust score penalty: -5 per day overdue
                penalty = days_overdue * 5
                new_trust = max(0, current_trust - penalty)
                trust_change_str = f" Trust Score: -{penalty} (Now {new_trust})"
            else:
                # Trust score reward: +2 for on-time/early return
                reward = 2
                new_trust = min(100, current_trust + reward)
                trust_change_str = f" Trust Score: +{reward} (Now {new_trust})"
        except ValueError:
            pass

    if dict(book)['available_copies'] < dict(book)['total_copies']:
        conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE isbn = ?', (isbn,))
        conn.execute('DELETE FROM issued_books WHERE id = (SELECT id FROM issued_books WHERE student_id = ? AND isbn = ? LIMIT 1)', (student_id, isbn))
        if new_trust != current_trust:
            conn.execute('UPDATE students SET trust_score = ? WHERE id = ?', (new_trust, student_id))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Returned '{dict(book)['title']}' successfully.{fine_str}{trust_change_str}"})
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
