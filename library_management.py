class Book:
    def __init__(self, title, author, isbn, copies):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.total_copies = copies
        self.available_copies = copies

    def __str__(self):
        return f"'{self.title}' by {self.author} (ISBN: {self.isbn}) - Available: {self.available_copies}/{self.total_copies}"

class Library:
    def __init__(self):
        self.books = []

    def add_book(self, title, author, isbn, copies):
        for book in self.books:
            if book.isbn == isbn:
                book.total_copies += copies
                book.available_copies += copies
                print(f"Added {copies} more copies of '{title}'.")
                return
        
        new_book = Book(title, author, isbn, copies)
        self.books.append(new_book)
        print(f"Book '{title}' added to the library with {copies} copies.")

    def search_books(self, query):
        query = query.lower()
        results = [book for book in self.books if query in book.title.lower() or query in book.author.lower() or query in book.isbn.lower()]
        
        if results:
            print(f"\nSearch results for '{query}':")
            for book in results:
                print(book)
        else:
            print(f"\nNo books found matching '{query}'.")

    def issue_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                if book.available_copies > 0:
                    book.available_copies -= 1
                    print(f"Successfully issued '{book.title}'. Copies left: {book.available_copies}")
                else:
                    print(f"Sorry, '{book.title}' is currently out of stock.")
                return
        print(f"Book with ISBN '{isbn}' not found in the library.")

    def return_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                if book.available_copies < book.total_copies:
                    book.available_copies += 1
                    print(f"Successfully returned '{book.title}'. Copies available: {book.available_copies}")
                else:
                    print(f"Cannot return '{book.title}'. It seems all copies are already in the library.")
                return
        print(f"Book with ISBN '{isbn}' not found in the library.")

    def display_available_books(self):
        print("\nAvailable Books in Library:")
        found = False
        for book in self.books:
            if book.available_copies > 0:
                print(book)
                found = True
        if not found:
            print("No books are currently available.")

def main():
    library = Library()

    # Pre-populate library for demonstration
    library.add_book("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", 3)
    library.add_book("1984", "George Orwell", "9780451524935", 5)
    library.add_book("To Kill a Mockingbird", "Harper Lee", "9780060935467", 2)

    while True:
        print("\n=== ShelfSync – Next Gen Library Management ===")
        print("1. Add a Book")
        print("2. Search Books")
        print("3. Issue a Book")
        print("4. Return a Book")
        print("5. View Available Books")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            isbn = input("Enter ISBN: ")
            try:
                copies = int(input("Enter number of copies: "))
                if copies <= 0:
                    print("Number of copies must be greater than 0.")
                    continue
                library.add_book(title, author, isbn, copies)
            except ValueError:
                print("Invalid input for copies. Please enter a number.")
        
        elif choice == '2':
            query = input("Enter search query (Title, Author, or ISBN): ")
            library.search_books(query)
            
        elif choice == '3':
            isbn = input("Enter ISBN of the book to issue: ")
            library.issue_book(isbn)
            
        elif choice == '4':
            isbn = input("Enter ISBN of the book to return: ")
            library.return_book(isbn)
            
        elif choice == '5':
            library.display_available_books()
            
        elif choice == '6':
            print("Exiting ShelfSync. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()
