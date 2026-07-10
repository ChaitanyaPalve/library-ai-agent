"""
Database seed script – populates the *library* MongoDB database
with a set of sample books across diverse academic subjects.

Usage:
    python scripts/seed_db.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from backend.models.db import get_db, ensure_indexes, make_book

# ── Technical / Academic ──────────────────────────────────────────────────────
TECHNICAL_BOOKS = [
    make_book("Introduction to Machine Learning", "Alpaydin Ethem", "978-0-262-01243-0",
              ["machine learning", "AI", "data science", "algorithms"], total_copies=3),
    make_book("Deep Learning", "Ian Goodfellow", "978-0-262-03561-3",
              ["deep learning", "neural networks", "AI", "machine learning"], total_copies=2),
    make_book("Python for Data Analysis", "Wes McKinney", "978-1-491-95766-0",
              ["python", "data analysis", "pandas", "data science"], total_copies=4),
    make_book("Artificial Intelligence: A Modern Approach", "Stuart Russell", "978-0-13-461099-3",
              ["AI", "artificial intelligence", "search", "planning"], total_copies=3),
    make_book("Database System Concepts", "Abraham Silberschatz", "978-0-07-352332-3",
              ["database", "SQL", "MongoDB", "data modeling"], total_copies=2),
    make_book("Clean Code", "Robert C. Martin", "978-0-13-235088-4",
              ["software engineering", "programming", "best practices"], total_copies=5),
    make_book("The Algorithm Design Manual", "Steven Skiena", "978-3-030-54255-9",
              ["algorithms", "data structures", "computer science"], total_copies=2),
    make_book("Computer Networking: A Top-Down Approach", "James Kurose", "978-0-13-359414-0",
              ["networking", "TCP/IP", "computer science", "internet"], total_copies=3),
    make_book("Operating System Concepts", "Abraham Silberschatz", "978-1-119-32091-3",
              ["operating systems", "concurrency", "memory management", "computer science"], total_copies=2),
    make_book("Calculus: Early Transcendentals", "James Stewart", "978-1-285-74155-0",
              ["calculus", "mathematics", "differentiation", "integration"], total_copies=6),
    make_book("Linear Algebra and Its Applications", "Gilbert Strang", "978-0-03-010567-8",
              ["linear algebra", "mathematics", "vectors", "matrices"], total_copies=4),
    make_book("Statistics", "David Freedman", "978-0-393-92972-0",
              ["statistics", "probability", "data analysis", "mathematics"], total_copies=3),
    make_book("Introduction to Algorithms", "Thomas Cormen", "978-0-262-04630-5",
              ["algorithms", "data structures", "computer science", "complexity"], total_copies=3),
    make_book("The Pragmatic Programmer", "David Thomas", "978-0-13-595705-9",
              ["software engineering", "programming", "agile", "best practices"], total_copies=2),
    make_book("Natural Language Processing with Python", "Steven Bird", "978-0-596-51649-9",
              ["NLP", "natural language processing", "python", "AI", "text mining"], total_copies=2),
    make_book("Cloud Computing: Concepts, Technology & Architecture", "Thomas Erl", "978-0-13-324069-9",
              ["cloud computing", "IBM Cloud", "AWS", "infrastructure"], total_copies=2),
    make_book("Hands-On Machine Learning with Scikit-Learn and TensorFlow", "Aurelien Geron", "978-1-098-12597-4",
              ["machine learning", "tensorflow", "scikit-learn", "python", "deep learning"], total_copies=3),
    make_book("Introduction to Data Mining", "Pang-Ning Tan", "978-0-13-312890-1",
              ["data mining", "machine learning", "data science", "clustering"], total_copies=2),
]

# ── Fiction — diverse range ───────────────────────────────────────────────────
FICTION_BOOKS = [
    # Classic literary fiction
    make_book("1984", "George Orwell", "978-0-452-28423-4",
              ["fiction", "dystopia", "classic", "political fiction"], total_copies=4),
    make_book("Brave New World", "Aldous Huxley", "978-0-06-085052-4",
              ["fiction", "dystopia", "classic", "science fiction"], total_copies=3),
    make_book("To Kill a Mockingbird", "Harper Lee", "978-0-06-112008-4",
              ["fiction", "classic", "social justice", "coming of age"], total_copies=4),
    make_book("The Great Gatsby", "F. Scott Fitzgerald", "978-0-7432-7356-5",
              ["fiction", "classic", "american literature", "tragedy"], total_copies=3),
    make_book("Pride and Prejudice", "Jane Austen", "978-0-14-143951-8",
              ["fiction", "classic", "romance", "regency"], total_copies=3),
    make_book("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "978-0-06-088328-7",
              ["fiction", "magical realism", "classic", "latin american literature"], total_copies=2),
    # Science fiction
    make_book("Dune", "Frank Herbert", "978-0-441-17271-9",
              ["fiction", "science fiction", "epic", "ecology"], total_copies=3),
    make_book("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", "978-0-345-39180-3",
              ["fiction", "science fiction", "comedy", "satire"], total_copies=4),
    make_book("Ender's Game", "Orson Scott Card", "978-0-7653-2963-0",
              ["fiction", "science fiction", "military", "young adult"], total_copies=3),
    make_book("The Left Hand of Darkness", "Ursula K. Le Guin", "978-0-441-47812-5",
              ["fiction", "science fiction", "gender", "anthropology"], total_copies=2),
    make_book("Neuromancer", "William Gibson", "978-0-441-56956-4",
              ["fiction", "science fiction", "cyberpunk", "AI"], total_copies=2),
    # Fantasy
    make_book("The Name of the Wind", "Patrick Rothfuss", "978-0-7564-0407-9",
              ["fiction", "fantasy", "epic fantasy", "magic"], total_copies=3),
    make_book("A Wizard of Earthsea", "Ursula K. Le Guin", "978-0-547-85389-3",
              ["fiction", "fantasy", "classic", "coming of age"], total_copies=2),
    make_book("The Way of Kings", "Brandon Sanderson", "978-0-7653-2637-0",
              ["fiction", "fantasy", "epic fantasy", "magic system"], total_copies=2),
    # Contemporary / literary fiction
    make_book("The Kite Runner", "Khaled Hosseini", "978-1-59448-000-3",
              ["fiction", "contemporary", "literary fiction", "war"], total_copies=3),
    make_book("The Alchemist", "Paulo Coelho", "978-0-06-112241-5",
              ["fiction", "philosophical fiction", "contemporary", "fable"], total_copies=4),
    make_book("Americanah", "Chimamanda Ngozi Adichie", "978-0-307-96213-4",
              ["fiction", "contemporary", "literary fiction", "immigration"], total_copies=2),
    make_book("The Remains of the Day", "Kazuo Ishiguro", "978-0-679-73172-5",
              ["fiction", "literary fiction", "classic", "memory"], total_copies=2),
    # Mystery / Thriller
    make_book("And Then There Were None", "Agatha Christie", "978-0-06-207348-8",
              ["fiction", "mystery", "thriller", "classic"], total_copies=4),
    make_book("The Girl with the Dragon Tattoo", "Stieg Larsson", "978-0-307-47347-9",
              ["fiction", "thriller", "mystery", "crime"], total_copies=3),
    # Historical fiction
    make_book("The Pillars of the Earth", "Ken Follett", "978-0-451-16689-5",
              ["fiction", "historical fiction", "medieval", "epic"], total_copies=2),
    make_book("Wolf Hall", "Hilary Mantel", "978-0-312-42905-6",
              ["fiction", "historical fiction", "tudor", "political"], total_copies=2),
    # Horror
    make_book("It", "Stephen King", "978-1-5011-6216-1",
              ["fiction", "horror", "supernatural", "coming of age"], total_copies=3),
    make_book("Dracula", "Bram Stoker", "978-0-14-143984-6",
              ["fiction", "horror", "gothic", "classic"], total_copies=2),
    # Romance
    make_book("Jane Eyre", "Charlotte Brontë", "978-0-14-144114-6",
              ["fiction", "romance", "classic", "gothic"], total_copies=3),
    make_book("Outlander", "Diana Gabaldon", "978-0-440-21256-1",
              ["fiction", "romance", "historical fiction", "adventure"], total_copies=2),
    # Graphic novel / visual storytelling
    make_book("Persepolis", "Marjane Satrapi", "978-0-375-71457-3",
              ["fiction", "graphic novel", "memoir", "iran"], total_copies=2),
    make_book("Watchmen", "Alan Moore", "978-1-4012-0713-1",
              ["fiction", "graphic novel", "superhero", "dystopia"], total_copies=2),
    # Biography / Memoir
    make_book("The Diary of a Young Girl", "Anne Frank", "978-0-553-29698-3",
              ["biography", "memoir", "world war ii", "historical"], total_copies=4),
    make_book("Educated", "Tara Westover", "978-0-399-59050-4",
              ["biography", "memoir", "coming of age", "contemporary"], total_copies=3),
    # Short stories / anthology
    make_book("The Stories of Anton Chekhov", "Anton Chekhov", "978-0-553-38100-7",
              ["fiction", "short stories", "classic", "russian literature"], total_copies=2),
    make_book("Interpreter of Maladies", "Jhumpa Lahiri", "978-0-395-92720-0",
              ["fiction", "short stories", "literary fiction", "immigration"], total_copies=2),
]

SAMPLE_BOOKS = TECHNICAL_BOOKS + FICTION_BOOKS


def seed():
    db = get_db()
    ensure_indexes()

    inserted = 0
    skipped  = 0
    for book in SAMPLE_BOOKS:
        try:
            db.books.insert_one(book)
            inserted += 1
            print(f"  ✓ {book['title']}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "E11000" in str(e):
                skipped += 1
                print(f"  – {book['title']} (already exists)")
            else:
                print(f"  ✗ {book['title']}: {e}")

    print(f"\nDone. {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    seed()
