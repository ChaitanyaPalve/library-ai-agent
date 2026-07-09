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

SAMPLE_BOOKS = [
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
    make_book("Hands-On Machine Learning with Scikit-Learn and TensorFlow", "Aurélien Géron", "978-1-098-12597-4",
              ["machine learning", "tensorflow", "scikit-learn", "python", "deep learning"], total_copies=3),
    make_book("Introduction to Data Mining", "Pang-Ning Tan", "978-0-13-312890-1",
              ["data mining", "machine learning", "data science", "clustering"], total_copies=2),
]


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
