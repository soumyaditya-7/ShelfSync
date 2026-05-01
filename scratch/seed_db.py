import sqlite3

books = [
    ("Clean Code", "Robert C. Martin", "9780132350884", 5, 5),
    ("The Pragmatic Programmer", "Andrew Hunt", "9780135957059", 3, 3),
    ("Design Patterns", "Erich Gamma", "9780201633610", 4, 4),
    ("Introduction to Algorithms", "Thomas H. Cormen", "9780262033848", 2, 2),
    ("You Don't Know JS", "Kyle Simpson", "9781491924464", 6, 6),
    ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", 10, 10),
    ("1984", "George Orwell", "9780451524935", 8, 8),
    ("To Kill a Mockingbird", "Harper Lee", "9780061120084", 7, 7)
]

db_path = 'library.db'

def seed():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for book in books:
            title, author, isbn, total, available = book
            # Check if ISBN already exists
            cursor.execute("SELECT isbn FROM books WHERE isbn = ?", (isbn,))
            if cursor.fetchone():
                print(f"Skipping {title} (ISBN {isbn} already exists)")
                continue
                
            cursor.execute(
                "INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)",
                (title, author, isbn, total, available)
            )
            print(f"Added: {title}")
            
        conn.commit()
        conn.close()
        print("Seeding complete.")
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    seed()
