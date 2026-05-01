import requests

books = [
    {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "9780132350884", "copies": 5},
    {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "isbn": "9780135957059", "copies": 3},
    {"title": "Design Patterns", "author": "Erich Gamma", "isbn": "9780201633610", "copies": 4},
    {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "isbn": "9780262033848", "copies": 2},
    {"title": "You Don't Know JS", "author": "Kyle Simpson", "isbn": "9781491924464", "copies": 6},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "9780743273565", "copies": 10},
    {"title": "1984", "author": "George Orwell", "isbn": "9780451524935", "copies": 8},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "9780061120084", "copies": 7}
]

url = "http://127.0.0.1:8000/api/add"

for book in books:
    try:
        response = requests.post(url, json=book)
        if response.status_code == 200:
            print(f"Successfully added: {book['title']}")
        else:
            print(f"Failed to add {book['title']}: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error connecting to server for {book['title']}: {e}")
