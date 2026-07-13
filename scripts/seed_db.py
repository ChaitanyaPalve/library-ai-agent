"""
Database seed script – populates the *library* MongoDB database
with books across diverse genres and subjects.
Every genre has at least 10 books.

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

# ── Machine Learning (10+) ────────────────────────────────────────────────────
ML_BOOKS = [
    make_book("Introduction to Machine Learning", "Alpaydin Ethem", "978-0-262-01243-0",
              ["machine learning", "AI", "data science", "algorithms"], total_copies=3),
    make_book("Deep Learning", "Ian Goodfellow", "978-0-262-03561-3",
              ["machine learning", "deep learning", "neural networks", "AI"], total_copies=2),
    make_book("Hands-On Machine Learning with Scikit-Learn and TensorFlow", "Aurélien Géron", "978-1-098-12597-4",
              ["machine learning", "tensorflow", "scikit-learn", "python"], total_copies=3),
    make_book("Pattern Recognition and Machine Learning", "Christopher Bishop", "978-0-387-31073-2",
              ["machine learning", "Bayesian", "statistics", "AI"], total_copies=2),
    make_book("The Hundred-Page Machine Learning Book", "Andriy Burkov", "978-1-99-729640-6",
              ["machine learning", "supervised learning", "unsupervised learning"], total_copies=4),
    make_book("Machine Learning Yearning", "Andrew Ng", "978-0-9995a-0-0",
              ["machine learning", "AI", "deep learning", "best practices"], total_copies=3),
    make_book("Machine Learning: A Probabilistic Perspective", "Kevin Murphy", "978-0-262-01802-9",
              ["machine learning", "probability", "graphical models", "AI"], total_copies=2),
    make_book("Applied Machine Learning", "David Forsyth", "978-3-030-18113-0",
              ["machine learning", "applied AI", "regression", "classification"], total_copies=2),
    make_book("Mathematics for Machine Learning", "Marc Deisenroth", "978-1-108-47004-9",
              ["machine learning", "mathematics", "linear algebra", "calculus"], total_copies=3),
    make_book("Artificial Intelligence: A Modern Approach", "Stuart Russell", "978-0-13-461099-3",
              ["machine learning", "AI", "search", "planning"], total_copies=3),
    make_book("Reinforcement Learning: An Introduction", "Richard Sutton", "978-0-262-19398-6",
              ["machine learning", "reinforcement learning", "AI", "reward"], total_copies=2),
]

# ── Data Science (10+) ────────────────────────────────────────────────────────
DATA_SCIENCE_BOOKS = [
    make_book("Python for Data Analysis", "Wes McKinney", "978-1-491-95766-0",
              ["data science", "python", "pandas", "data analysis"], total_copies=4),
    make_book("Introduction to Data Mining", "Pang-Ning Tan", "978-0-13-312890-1",
              ["data science", "data mining", "machine learning", "clustering"], total_copies=2),
    make_book("Data Science from Scratch", "Joel Grus", "978-1-492-04113-8",
              ["data science", "python", "statistics", "algorithms"], total_copies=3),
    make_book("Storytelling with Data", "Cole Nussbaumer Knaflic", "978-1-119-00225-3",
              ["data science", "data visualization", "communication"], total_copies=3),
    make_book("The Data Science Handbook", "Field Cady", "978-1-119-50807-2",
              ["data science", "statistics", "python", "machine learning"], total_copies=2),
    make_book("Practical Statistics for Data Scientists", "Peter Bruce", "978-1-492-07294-2",
              ["data science", "statistics", "regression", "probability"], total_copies=3),
    make_book("Data Science for Business", "Foster Provost", "978-1-449-36132-7",
              ["data science", "business analytics", "machine learning"], total_copies=2),
    make_book("Python Data Science Handbook", "Jake VanderPlas", "978-1-491-91205-8",
              ["data science", "python", "NumPy", "Matplotlib", "pandas"], total_copies=3),
    make_book("Big Data: A Revolution", "Viktor Mayer-Schönberger", "978-0-544-00269-2",
              ["data science", "big data", "analytics", "society"], total_copies=2),
    make_book("Fundamentals of Data Visualization", "Claus Wilke", "978-1-492-03108-6",
              ["data science", "data visualization", "ggplot", "R"], total_copies=2),
    make_book("The Art of Data Science", "Roger Peng", "978-1-365-06469-1",
              ["data science", "exploratory analysis", "statistics"], total_copies=3),
]

# ── Algorithms (10+) ─────────────────────────────────────────────────────────
ALGORITHM_BOOKS = [
    make_book("Introduction to Algorithms", "Thomas Cormen", "978-0-262-04630-5",
              ["algorithms", "data structures", "complexity", "computer science"], total_copies=3),
    make_book("The Algorithm Design Manual", "Steven Skiena", "978-3-030-54255-9",
              ["algorithms", "data structures", "problem solving"], total_copies=2),
    make_book("Algorithms", "Robert Sedgewick", "978-0-321-57351-3",
              ["algorithms", "Java", "data structures", "graphs"], total_copies=3),
    make_book("Algorithm Design", "Jon Kleinberg", "978-0-321-29535-4",
              ["algorithms", "graph algorithms", "dynamic programming"], total_copies=2),
    make_book("Grokking Algorithms", "Aditya Y. Bhargava", "978-1-617-29223-4",
              ["algorithms", "beginners", "data structures", "visual learning"], total_copies=4),
    make_book("The Art of Computer Programming Vol. 1", "Donald Knuth", "978-0-201-89683-1",
              ["algorithms", "computer science", "mathematics", "sorting"], total_copies=1),
    make_book("Competitive Programming 3", "Steven Halim", "978-9-81-142903-7",
              ["algorithms", "competitive programming", "data structures"], total_copies=2),
    make_book("Cracking the Coding Interview", "Gayle Laakmann McDowell", "978-0-984-78285-2",
              ["algorithms", "interview prep", "data structures", "problem solving"], total_copies=5),
    make_book("Elements of Programming Interviews", "Adnan Aziz", "978-1-479-27428-5",
              ["algorithms", "interview prep", "problem solving"], total_copies=3),
    make_book("Algorithms Unlocked", "Thomas Cormen", "978-0-262-51880-2",
              ["algorithms", "beginners", "computer science"], total_copies=3),
    make_book("Data Structures and Algorithms in Python", "Michael Goodrich", "978-1-118-29027-9",
              ["algorithms", "data structures", "python", "object-oriented"], total_copies=2),
]

# ── Python (10+) ──────────────────────────────────────────────────────────────
PYTHON_BOOKS = [
    make_book("Learning Python", "Mark Lutz", "978-1-449-35573-9",
              ["python", "programming", "object-oriented", "beginners"], total_copies=4),
    make_book("Python Crash Course", "Eric Matthes", "978-1-593-27603-4",
              ["python", "beginners", "projects", "programming"], total_copies=5),
    make_book("Fluent Python", "Luciano Ramalho", "978-1-492-05635-5",
              ["python", "advanced", "idioms", "programming"], total_copies=3),
    make_book("Python Cookbook", "David Beazley", "978-1-449-34037-7",
              ["python", "recipes", "advanced", "programming"], total_copies=2),
    make_book("Automate the Boring Stuff with Python", "Al Sweigart", "978-1-593-27992-9",
              ["python", "automation", "beginners", "scripts"], total_copies=4),
    make_book("Effective Python", "Brett Slatkin", "978-0-134-85398-0",
              ["python", "best practices", "advanced", "idiomatic"], total_copies=3),
    make_book("Python for Everybody", "Charles Severance", "978-1-530-99254-2",
              ["python", "beginners", "web", "data"], total_copies=5),
    make_book("Dive into Python 3", "Mark Pilgrim", "978-1-430-22415-0",
              ["python", "advanced", "unicode", "testing"], total_copies=2),
    make_book("Natural Language Processing with Python", "Steven Bird", "978-0-596-51649-9",
              ["python", "NLP", "text mining", "AI"], total_copies=2),
    make_book("Python Machine Learning", "Sebastian Raschka", "978-1-789-95575-0",
              ["python", "machine learning", "scikit-learn", "deep learning"], total_copies=3),
    make_book("High Performance Python", "Micha Gorelick", "978-1-492-05502-0",
              ["python", "performance", "optimization", "advanced"], total_copies=2),
]

# ── NLP (10+) ─────────────────────────────────────────────────────────────────
NLP_BOOKS = [
    make_book("Speech and Language Processing", "Dan Jurafsky", "978-0-131-87321-6",
              ["NLP", "natural language processing", "speech recognition", "AI"], total_copies=2),
    make_book("Natural Language Processing with Transformers", "Lewis Tunstall", "978-1-098-10398-8",
              ["NLP", "transformers", "BERT", "deep learning", "python"], total_copies=3),
    make_book("Foundations of Statistical Natural Language Processing", "Christopher Manning", "978-0-262-13360-9",
              ["NLP", "statistics", "language models", "AI"], total_copies=2),
    make_book("Applied Text Analysis with Python", "Benjamin Bengfort", "978-1-491-96367-8",
              ["NLP", "python", "text analysis", "machine learning"], total_copies=3),
    make_book("Text Mining with R", "Julia Silge", "978-1-491-98165-8",
              ["NLP", "R", "text mining", "data science"], total_copies=2),
    make_book("Neural Network Methods for Natural Language Processing", "Yoav Goldberg", "978-1-627-05298-7",
              ["NLP", "neural networks", "deep learning", "embeddings"], total_copies=2),
    make_book("Practical Natural Language Processing", "Sowmya Vajjala", "978-1-492-05405-4",
              ["NLP", "python", "applied AI", "text processing"], total_copies=3),
    make_book("Linguistic Fundamentals for Natural Language Processing", "Emily Bender", "978-1-627-05108-9",
              ["NLP", "linguistics", "semantics", "syntax"], total_copies=2),
    make_book("Deep Learning for NLP", "Palash Goyal", "978-1-484-23840-4",
              ["NLP", "deep learning", "python", "word embeddings"], total_copies=2),
    make_book("Mastering NLP from Foundations to LLMs", "Lior Gazit", "978-1-804-61897-6",
              ["NLP", "LLM", "GPT", "BERT", "transformers"], total_copies=3),
    make_book("Building Chatbots with Python", "Sumit Raj", "978-1-484-23960-9",
              ["NLP", "chatbots", "python", "deep learning"], total_copies=2),
]

# ── Database (10+) ────────────────────────────────────────────────────────────
DATABASE_BOOKS = [
    make_book("Database System Concepts", "Abraham Silberschatz", "978-0-07-352332-3",
              ["database", "SQL", "MongoDB", "data modeling"], total_copies=2),
    make_book("MongoDB: The Definitive Guide", "Kristina Chodorow", "978-1-491-95402-7",
              ["database", "MongoDB", "NoSQL", "data modeling"], total_copies=3),
    make_book("Learning SQL", "Alan Beaulieu", "978-1-492-05756-7",
              ["database", "SQL", "relational databases", "MySQL"], total_copies=4),
    make_book("Designing Data-Intensive Applications", "Martin Kleppmann", "978-1-449-37332-0",
              ["database", "distributed systems", "data engineering", "scalability"], total_copies=3),
    make_book("Database Internals", "Alex Petrov", "978-1-492-04034-6",
              ["database", "storage engines", "distributed databases"], total_copies=2),
    make_book("Seven Databases in Seven Weeks", "Luc Perkins", "978-1-680-50253-4",
              ["database", "Redis", "PostgreSQL", "Neo4j", "Cassandra"], total_copies=2),
    make_book("NoSQL Distilled", "Martin Fowler", "978-0-321-82662-6",
              ["database", "NoSQL", "document store", "key-value"], total_copies=3),
    make_book("PostgreSQL: Up and Running", "Regina Obe", "978-1-492-08048-0",
              ["database", "PostgreSQL", "SQL", "relational databases"], total_copies=2),
    make_book("Redis in Action", "Josiah Carlson", "978-1-617-29016-2",
              ["database", "Redis", "caching", "NoSQL"], total_copies=2),
    make_book("Fundamentals of Database Systems", "Ramez Elmasri", "978-0-133-46979-3",
              ["database", "SQL", "relational model", "normalization"], total_copies=3),
    make_book("Graph Databases", "Ian Robinson", "978-1-491-93097-1",
              ["database", "Neo4j", "graph theory", "NoSQL"], total_copies=2),
]

# ── Networking (10+) ──────────────────────────────────────────────────────────
NETWORKING_BOOKS = [
    make_book("Computer Networking: A Top-Down Approach", "James Kurose", "978-0-13-359414-0",
              ["networking", "TCP/IP", "internet", "protocols"], total_copies=3),
    make_book("TCP/IP Illustrated Vol. 1", "W. Richard Stevens", "978-0-321-33631-6",
              ["networking", "TCP/IP", "protocols", "internet"], total_copies=2),
    make_book("Computer Networks", "Andrew Tanenbaum", "978-0-13-212695-3",
              ["networking", "protocols", "OSI model", "internet"], total_copies=3),
    make_book("Network Warrior", "Gary Donahue", "978-1-449-33879-4",
              ["networking", "Cisco", "routing", "switching"], total_copies=2),
    make_book("Wireshark Network Analysis", "Laura Chappell", "978-1-893-64299-7",
              ["networking", "packet analysis", "Wireshark", "troubleshooting"], total_copies=2),
    make_book("Hacking: The Art of Exploitation", "Jon Erickson", "978-1-593-27194-7",
              ["networking", "security", "exploitation", "C programming"], total_copies=2),
    make_book("Network Security Essentials", "William Stallings", "978-0-13-452733-2",
              ["networking", "security", "cryptography", "firewalls"], total_copies=3),
    make_book("Software Defined Networks", "Paul Goransson", "978-0-128-00737-1",
              ["networking", "SDN", "OpenFlow", "cloud"], total_copies=2),
    make_book("The Practice of Network Security Monitoring", "Richard Bejtlich", "978-1-593-27534-1",
              ["networking", "security", "monitoring", "intrusion detection"], total_copies=2),
    make_book("Cloud Networking", "Gary Lee", "978-0-128-02325-8",
              ["networking", "cloud", "virtual networking", "SDN"], total_copies=2),
    make_book("High Performance Browser Networking", "Ilya Grigorik", "978-1-449-34476-4",
              ["networking", "HTTP", "web performance", "protocols"], total_copies=3),
]

# ── Mathematics (10+) ─────────────────────────────────────────────────────────
MATHEMATICS_BOOKS = [
    make_book("Calculus: Early Transcendentals", "James Stewart", "978-1-285-74155-0",
              ["mathematics", "calculus", "differentiation", "integration"], total_copies=6),
    make_book("Linear Algebra and Its Applications", "Gilbert Strang", "978-0-03-010567-8",
              ["mathematics", "linear algebra", "vectors", "matrices"], total_copies=4),
    make_book("Statistics", "David Freedman", "978-0-393-92972-0",
              ["mathematics", "statistics", "probability", "data analysis"], total_copies=3),
    make_book("Discrete Mathematics and Its Applications", "Kenneth Rosen", "978-0-07-288008-3",
              ["mathematics", "discrete math", "graph theory", "logic"], total_copies=3),
    make_book("Introduction to Probability", "Joseph Blitzstein", "978-1-466-57560-9",
              ["mathematics", "probability", "statistics", "combinatorics"], total_copies=3),
    make_book("Abstract Algebra", "David Dummit", "978-0-471-43334-7",
              ["mathematics", "algebra", "groups", "rings"], total_copies=2),
    make_book("Real Analysis", "Walter Rudin", "978-0-070-54235-8",
              ["mathematics", "real analysis", "topology", "sequences"], total_copies=2),
    make_book("Numerical Methods for Scientists and Engineers", "Richard Hamming", "978-0-486-65241-2",
              ["mathematics", "numerical methods", "computation", "algorithms"], total_copies=2),
    make_book("The Art of Problem Solving Vol. 1", "Richard Rusczyk", "978-0-977-78502-5",
              ["mathematics", "competition math", "problem solving", "beginners"], total_copies=3),
    make_book("Graph Theory", "Reinhard Diestel", "978-3-662-53622-3",
              ["mathematics", "graph theory", "combinatorics", "algorithms"], total_copies=2),
    make_book("Mathematical Analysis", "Tom Apostol", "978-0-201-00288-1",
              ["mathematics", "analysis", "sequences", "series"], total_copies=2),
]

# ── Cloud Computing (10+) ─────────────────────────────────────────────────────
CLOUD_BOOKS = [
    make_book("Cloud Computing: Concepts, Technology & Architecture", "Thomas Erl", "978-0-13-324069-9",
              ["cloud computing", "IBM Cloud", "AWS", "infrastructure"], total_copies=2),
    make_book("The Cloud Adoption Playbook", "Moe Abdula", "978-1-119-47801-3",
              ["cloud computing", "IBM", "digital transformation", "strategy"], total_copies=3),
    make_book("AWS Certified Solutions Architect Study Guide", "Ben Piper", "978-1-119-71331-9",
              ["cloud computing", "AWS", "certification", "architecture"], total_copies=3),
    make_book("Google Cloud Platform in Action", "JJ Geewax", "978-1-617-29425-2",
              ["cloud computing", "GCP", "Google", "microservices"], total_copies=2),
    make_book("Kubernetes in Action", "Marko Luksa", "978-1-617-29372-9",
              ["cloud computing", "Kubernetes", "containers", "orchestration"], total_copies=3),
    make_book("Docker Deep Dive", "Nigel Poulton", "978-1-521-82242-7",
              ["cloud computing", "Docker", "containers", "DevOps"], total_copies=4),
    make_book("Serverless Architectures on AWS", "Peter Sbarski", "978-1-617-29277-7",
              ["cloud computing", "AWS Lambda", "serverless", "microservices"], total_copies=2),
    make_book("Cloud Native Patterns", "Cornelia Davis", "978-1-617-29480-2",
              ["cloud computing", "microservices", "patterns", "containers"], total_copies=2),
    make_book("Infrastructure as Code", "Kief Morris", "978-1-098-11467-9",
              ["cloud computing", "IaC", "Terraform", "automation"], total_copies=2),
    make_book("Site Reliability Engineering", "Niall Richard Murphy", "978-1-491-92912-8",
              ["cloud computing", "SRE", "reliability", "Google"], total_copies=3),
    make_book("Cloud Architecture Patterns", "Bill Wilder", "978-1-449-31977-9",
              ["cloud computing", "patterns", "scalability", "Azure"], total_copies=2),
]

# ── Fiction (10+) ─────────────────────────────────────────────────────────────
FICTION_BOOKS = [
    make_book("1984", "George Orwell", "978-0-452-28423-4",
              ["fiction", "dystopia", "classic", "political fiction"], total_copies=4),
    make_book("Brave New World", "Aldous Huxley", "978-0-06-085052-4",
              ["fiction", "dystopia", "classic", "science fiction"], total_copies=3),
    make_book("To Kill a Mockingbird", "Harper Lee", "978-0-06-112008-4",
              ["fiction", "classic", "social justice", "coming of age"], total_copies=4),
    make_book("The Great Gatsby", "F. Scott Fitzgerald", "978-0-7432-7356-5",
              ["fiction", "classic", "american literature", "tragedy"], total_copies=3),
    make_book("Dune", "Frank Herbert", "978-0-441-17271-9",
              ["fiction", "science fiction", "epic", "ecology"], total_copies=3),
    make_book("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", "978-0-345-39180-3",
              ["fiction", "science fiction", "comedy", "satire"], total_copies=4),
    make_book("Ender's Game", "Orson Scott Card", "978-0-7653-2963-0",
              ["fiction", "science fiction", "military", "young adult"], total_copies=3),
    make_book("Neuromancer", "William Gibson", "978-0-441-56956-4",
              ["fiction", "science fiction", "cyberpunk", "AI"], total_copies=2),
    make_book("The Name of the Wind", "Patrick Rothfuss", "978-0-7564-0407-9",
              ["fiction", "fantasy", "epic fantasy", "magic"], total_copies=3),
    make_book("The Kite Runner", "Khaled Hosseini", "978-1-59448-000-3",
              ["fiction", "contemporary", "literary fiction", "war"], total_copies=3),
    make_book("The Alchemist", "Paulo Coelho", "978-0-06-112241-5",
              ["fiction", "philosophical fiction", "contemporary", "fable"], total_copies=4),
    make_book("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "978-0-06-088328-7",
              ["fiction", "magical realism", "classic", "latin american literature"], total_copies=2),
    make_book("The Way of Kings", "Brandon Sanderson", "978-0-7653-2637-0",
              ["fiction", "fantasy", "epic fantasy", "magic system"], total_copies=2),
]

# ── Horror (10+) ──────────────────────────────────────────────────────────────
HORROR_BOOKS = [
    make_book("It", "Stephen King", "978-1-5011-6216-1",
              ["horror", "supernatural", "coming of age", "fiction"], total_copies=3),
    make_book("Dracula", "Bram Stoker", "978-0-14-143984-6",
              ["horror", "gothic", "classic", "fiction"], total_copies=2),
    make_book("The Shining", "Stephen King", "978-0-307-74391-8",
              ["horror", "supernatural", "psychological", "fiction"], total_copies=3),
    make_book("Frankenstein", "Mary Shelley", "978-0-14-143947-1",
              ["horror", "gothic", "classic", "science fiction"], total_copies=4),
    make_book("The Haunting of Hill House", "Shirley Jackson", "978-0-14-303998-7",
              ["horror", "psychological", "gothic", "classic"], total_copies=2),
    make_book("American Gods", "Neil Gaiman", "978-0-380-78901-7",
              ["horror", "fantasy", "mythology", "contemporary fiction"], total_copies=3),
    make_book("Bird Box", "Josh Malerman", "978-0-385-53533-1",
              ["horror", "post-apocalyptic", "psychological", "fiction"], total_copies=3),
    make_book("House of Leaves", "Mark Z. Danielewski", "978-0-375-70376-8",
              ["horror", "experimental", "postmodern", "psychological"], total_copies=2),
    make_book("World War Z", "Max Brooks", "978-0-307-34660-0",
              ["horror", "zombies", "apocalypse", "fiction"], total_copies=3),
    make_book("Interview with the Vampire", "Anne Rice", "978-0-345-40964-3",
              ["horror", "vampires", "gothic", "fiction"], total_copies=2),
    make_book("Pet Sematary", "Stephen King", "978-0-743-41261-4",
              ["horror", "supernatural", "grief", "fiction"], total_copies=3),
]

# ── Romance (10+) ─────────────────────────────────────────────────────────────
ROMANCE_BOOKS = [
    make_book("Pride and Prejudice", "Jane Austen", "978-0-14-143951-8",
              ["romance", "classic", "regency", "fiction"], total_copies=3),
    make_book("Jane Eyre", "Charlotte Brontë", "978-0-14-144114-6",
              ["romance", "classic", "gothic", "fiction"], total_copies=3),
    make_book("Outlander", "Diana Gabaldon", "978-0-440-21256-1",
              ["romance", "historical fiction", "adventure", "fiction"], total_copies=2),
    make_book("The Notebook", "Nicholas Sparks", "978-0-446-60523-3",
              ["romance", "contemporary", "love story", "fiction"], total_copies=4),
    make_book("Me Before You", "Jojo Moyes", "978-0-143-12454-3",
              ["romance", "contemporary", "drama", "fiction"], total_copies=3),
    make_book("Twilight", "Stephenie Meyer", "978-0-316-01584-4",
              ["romance", "paranormal", "young adult", "fiction"], total_copies=4),
    make_book("The Fault in Our Stars", "John Green", "978-0-525-47881-2",
              ["romance", "young adult", "coming of age", "fiction"], total_copies=5),
    make_book("It Ends with Us", "Colleen Hoover", "978-1-501-16054-9",
              ["romance", "contemporary", "drama", "fiction"], total_copies=4),
    make_book("The Hating Game", "Sally Thorne", "978-0-062-67029-3",
              ["romance", "contemporary", "office romance", "comedy"], total_copies=3),
    make_book("Beach Read", "Emily Henry", "978-1-984-80585-1",
              ["romance", "contemporary", "summer", "fiction"], total_copies=4),
    make_book("People We Meet on Vacation", "Emily Henry", "978-1-984-80589-9",
              ["romance", "contemporary", "travel", "best friends"], total_copies=3),
]

# ── Graphic Novel (10+) ───────────────────────────────────────────────────────
GRAPHIC_NOVEL_BOOKS = [
    make_book("Persepolis", "Marjane Satrapi", "978-0-375-71457-3",
              ["graphic novel", "memoir", "iran", "fiction"], total_copies=2),
    make_book("Watchmen", "Alan Moore", "978-1-4012-0713-1",
              ["graphic novel", "superhero", "dystopia", "fiction"], total_copies=2),
    make_book("Maus", "Art Spiegelman", "978-0-679-74840-1",
              ["graphic novel", "memoir", "world war ii", "historical"], total_copies=3),
    make_book("V for Vendetta", "Alan Moore", "978-1-401-20814-9",
              ["graphic novel", "dystopia", "anarchism", "fiction"], total_copies=2),
    make_book("Saga Vol. 1", "Brian K. Vaughan", "978-1-607-06601-9",
              ["graphic novel", "science fiction", "epic", "fantasy"], total_copies=3),
    make_book("Batman: The Dark Knight Returns", "Frank Miller", "978-1-563-89342-1",
              ["graphic novel", "superhero", "Batman", "DC Comics"], total_copies=2),
    make_book("Fun Home", "Alison Bechdel", "978-0-618-47106-0",
              ["graphic novel", "memoir", "LGBTQ", "coming of age"], total_copies=2),
    make_book("Bone Vol. 1", "Jeff Smith", "978-0-545-01347-4",
              ["graphic novel", "fantasy", "adventure", "young adult"], total_copies=3),
    make_book("Scott Pilgrim Vol. 1", "Bryan Lee O'Malley", "978-1-932-66418-3",
              ["graphic novel", "romance", "comedy", "video games"], total_copies=3),
    make_book("The Complete Sandman", "Neil Gaiman", "978-1-401-28359-8",
              ["graphic novel", "fantasy", "mythology", "horror"], total_copies=2),
    make_book("Black Panther: A Nation Under Our Feet", "Ta-Nehisi Coates", "978-1-302-90024-5",
              ["graphic novel", "superhero", "political", "Marvel"], total_copies=2),
]

# ── Biography (10+) ───────────────────────────────────────────────────────────
BIOGRAPHY_BOOKS = [
    make_book("The Diary of a Young Girl", "Anne Frank", "978-0-553-29698-3",
              ["biography", "memoir", "world war ii", "historical"], total_copies=4),
    make_book("Educated", "Tara Westover", "978-0-399-59050-4",
              ["biography", "memoir", "coming of age", "contemporary"], total_copies=3),
    make_book("Steve Jobs", "Walter Isaacson", "978-1-451-64853-9",
              ["biography", "technology", "entrepreneurship", "Apple"], total_copies=3),
    make_book("Becoming", "Michelle Obama", "978-1-524-76313-8",
              ["biography", "memoir", "politics", "inspiration"], total_copies=4),
    make_book("The Story of My Experiments with Truth", "Mahatma Gandhi", "978-0-807-05909-0",
              ["biography", "memoir", "historical", "philosophy"], total_copies=3),
    make_book("Long Walk to Freedom", "Nelson Mandela", "978-0-316-54818-3",
              ["biography", "memoir", "politics", "historical"], total_copies=3),
    make_book("Leonardo da Vinci", "Walter Isaacson", "978-1-501-12979-4",
              ["biography", "Renaissance", "art", "science"], total_copies=2),
    make_book("The Innovators", "Walter Isaacson", "978-1-476-70869-3",
              ["biography", "technology", "history", "computing"], total_copies=2),
    make_book("Elon Musk", "Walter Isaacson", "978-1-982-18128-4",
              ["biography", "technology", "entrepreneurship", "SpaceX"], total_copies=4),
    make_book("When Breath Becomes Air", "Paul Kalanithi", "978-0-812-98840-5",
              ["biography", "memoir", "medicine", "mortality"], total_copies=3),
    make_book("The Glass Castle", "Jeannette Walls", "978-0-743-24753-7",
              ["biography", "memoir", "family", "coming of age"], total_copies=3),
]

# ── Mood: Sad / Emotional (10+) ───────────────────────────────────────────────
SAD_BOOKS = [
    make_book("The Bell Jar", "Sylvia Plath", "978-0-06-083493-9",
              ["mood:sad", "fiction", "mental health", "memoir", "classic"], total_copies=3),
    make_book("A Little Life", "Hanya Yanagihara", "978-0-385-53925-4",
              ["mood:sad", "fiction", "trauma", "friendship", "literary fiction"], total_copies=2),
    make_book("Flowers for Algernon", "Daniel Keyes", "978-0-15-603008-5",
              ["mood:sad", "fiction", "science fiction", "intelligence", "classic"], total_copies=3),
    make_book("The Book Thief", "Markus Zusak", "978-0-375-84220-7",
              ["mood:sad", "fiction", "world war ii", "historical", "coming of age"], total_copies=4),
    make_book("Tuesdays with Morrie", "Mitch Albom", "978-0-767-90592-6",
              ["mood:sad", "biography", "memoir", "life lessons", "death"], total_copies=3),
    make_book("When Breath Becomes Air", "Paul Kalanithi", "978-0-812-98840-5",
              ["mood:sad", "biography", "memoir", "medicine", "mortality"], total_copies=3),
    make_book("The Lovely Bones", "Alice Sebold", "978-0-316-16984-0",
              ["mood:sad", "fiction", "grief", "supernatural", "family"], total_copies=2),
    make_book("Me Before You", "Jojo Moyes", "978-0-143-12454-3",
              ["mood:sad", "romance", "contemporary", "drama", "fiction"], total_copies=3),
    make_book("The Fault in Our Stars", "John Green", "978-0-525-47881-2",
              ["mood:sad", "romance", "young adult", "illness", "coming of age"], total_copies=5),
    make_book("Grief Is the Thing with Feathers", "Max Porter", "978-0-571-32710-7",
              ["mood:sad", "poetry", "grief", "experimental fiction"], total_copies=2),
    make_book("Extremely Loud and Incredibly Close", "Jonathan Safran Foer", "978-0-618-71165-5",
              ["mood:sad", "fiction", "grief", "9/11", "coming of age"], total_copies=2),
]

# ── Mood: Happy / Uplifting (10+) ─────────────────────────────────────────────
HAPPY_BOOKS = [
    make_book("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", "978-0-345-39180-3",
              ["mood:happy", "fiction", "science fiction", "comedy", "satire"], total_copies=4),
    make_book("Good Omens", "Terry Pratchett & Neil Gaiman", "978-0-060-85398-3",
              ["mood:happy", "fiction", "fantasy", "comedy", "satire"], total_copies=3),
    make_book("The House in the Cerulean Sea", "TJ Klune", "978-1-250-21738-4",
              ["mood:happy", "fiction", "fantasy", "romance", "cozy"], total_copies=3),
    make_book("Eleanor Oliphant is Completely Fine", "Gail Honeyman", "978-0-735-22032-8",
              ["mood:happy", "fiction", "contemporary", "uplifting", "humour"], total_copies=4),
    make_book("The Rosie Project", "Graeme Simsion", "978-1-476-72495-2",
              ["mood:happy", "fiction", "romance", "comedy", "contemporary"], total_copies=3),
    make_book("Three Men in a Boat", "Jerome K. Jerome", "978-0-14-043091-0",
              ["mood:happy", "fiction", "comedy", "classic", "adventure"], total_copies=2),
    make_book("The Secret Life of Bees", "Sue Monk Kidd", "978-0-14-200174-3",
              ["mood:happy", "fiction", "contemporary", "uplifting", "family"], total_copies=3),
    make_book("Big Magic", "Elizabeth Gilbert", "978-1-594-63403-7",
              ["mood:happy", "non-fiction", "creativity", "inspiration", "self-help"], total_copies=4),
    make_book("The Year of Magical Thinking", "Joan Didion", "978-0-307-38774-8",
              ["mood:happy", "biography", "memoir", "resilience", "contemporary"], total_copies=2),
    make_book("Winnie-the-Pooh", "A. A. Milne", "978-0-525-44443-4",
              ["mood:happy", "fiction", "classic", "children", "whimsy"], total_copies=4),
    make_book("The Alchemist", "Paulo Coelho", "978-0-06-112241-5",
              ["mood:happy", "fiction", "philosophical fiction", "inspirational", "fable"], total_copies=4),
]

# ── Mood: Stressed / Anxious (10+) ────────────────────────────────────────────
STRESSED_BOOKS = [
    make_book("The Power of Now", "Eckhart Tolle", "978-1-57731-480-6",
              ["mood:stressed", "self-help", "mindfulness", "spirituality", "anxiety"], total_copies=4),
    make_book("Why Zebras Don't Get Ulcers", "Robert Sapolsky", "978-0-8050-7369-0",
              ["mood:stressed", "non-fiction", "stress", "biology", "health"], total_copies=3),
    make_book("Feeling Good: The New Mood Therapy", "David Burns", "978-0-380-73176-5",
              ["mood:stressed", "self-help", "CBT", "mental health", "anxiety"], total_copies=3),
    make_book("The Anxiety and Worry Workbook", "Clark & Beck", "978-1-606-23308-1",
              ["mood:stressed", "self-help", "CBT", "anxiety", "workbook"], total_copies=2),
    make_book("Wherever You Go, There You Are", "Jon Kabat-Zinn", "978-1-401-30778-4",
              ["mood:stressed", "mindfulness", "meditation", "self-help"], total_copies=3),
    make_book("The Gifts of Imperfection", "Brené Brown", "978-1-592-85870-4",
              ["mood:stressed", "self-help", "vulnerability", "wholehearted living"], total_copies=4),
    make_book("Ikigai: The Japanese Secret to a Long and Happy Life", "Francesc Miralles", "978-0-143-13047-6",
              ["mood:stressed", "self-help", "purpose", "Japanese philosophy", "wellbeing"], total_copies=3),
    make_book("The Subtle Art of Not Giving a F*ck", "Mark Manson", "978-0-062-45773-5",
              ["mood:stressed", "self-help", "philosophy", "mindset", "contemporary"], total_copies=5),
    make_book("Breath: The New Science of a Lost Art", "James Nestor", "978-0-735-23491-2",
              ["mood:stressed", "non-fiction", "health", "mindfulness", "science"], total_copies=3),
    make_book("Lost Connections", "Johann Hari", "978-1-632-86830-0",
              ["mood:stressed", "non-fiction", "depression", "mental health", "society"], total_copies=3),
    make_book("Atomic Habits", "James Clear", "978-0-735-21129-6",
              ["mood:stressed", "self-help", "habits", "productivity", "motivation"], total_copies=5),
]

# ── Mood: Adventurous / Excited (10+) ─────────────────────────────────────────
ADVENTUROUS_BOOKS = [
    make_book("Into the Wild", "Jon Krakauer", "978-0-385-48680-4",
              ["mood:adventurous", "biography", "adventure", "nature", "travel"], total_copies=3),
    make_book("Wild: From Lost to Found on the Pacific Crest Trail", "Cheryl Strayed", "978-1-400-06691-1",
              ["mood:adventurous", "biography", "memoir", "hiking", "self-discovery"], total_copies=3),
    make_book("Around the World in 80 Days", "Jules Verne", "978-0-14-044905-9",
              ["mood:adventurous", "fiction", "classic", "adventure", "travel"], total_copies=3),
    make_book("The Count of Monte Cristo", "Alexandre Dumas", "978-0-14-044926-4",
              ["mood:adventurous", "fiction", "classic", "adventure", "revenge"], total_copies=2),
    make_book("Treasure Island", "Robert Louis Stevenson", "978-0-14-043572-4",
              ["mood:adventurous", "fiction", "classic", "pirates", "adventure"], total_copies=4),
    make_book("The Hobbit", "J. R. R. Tolkien", "978-0-618-00221-3",
              ["mood:adventurous", "fiction", "fantasy", "epic", "adventure"], total_copies=5),
    make_book("Life of Pi", "Yann Martel", "978-0-156-02998-6",
              ["mood:adventurous", "fiction", "survival", "philosophical", "adventure"], total_copies=4),
    make_book("Into Thin Air", "Jon Krakauer", "978-0-385-49208-9",
              ["mood:adventurous", "biography", "mountaineering", "disaster", "adventure"], total_copies=3),
    make_book("The Secret", "Rhonda Byrne", "978-1-582-70170-1",
              ["mood:adventurous", "self-help", "motivation", "law of attraction"], total_copies=3),
    make_book("Endurance: Shackleton's Incredible Voyage", "Alfred Lansing", "978-0-465-02439-2",
              ["mood:adventurous", "biography", "survival", "history", "polar exploration"], total_copies=2),
    make_book("On the Road", "Jack Kerouac", "978-0-140-28300-2",
              ["mood:adventurous", "fiction", "classic", "beat generation", "travel"], total_copies=3),
]

# ── Mood: Motivated / Inspired (10+) ──────────────────────────────────────────
MOTIVATED_BOOKS = [
    make_book("Think and Grow Rich", "Napoleon Hill", "978-1-585-42433-3",
              ["mood:motivated", "self-help", "success", "mindset", "classic"], total_copies=4),
    make_book("Deep Work", "Cal Newport", "978-1-455-58669-1",
              ["mood:motivated", "self-help", "productivity", "focus", "work"], total_copies=4),
    make_book("The 7 Habits of Highly Effective People", "Stephen Covey", "978-1-982-13701-5",
              ["mood:motivated", "self-help", "habits", "leadership", "classic"], total_copies=5),
    make_book("Grit: The Power of Passion and Perseverance", "Angela Duckworth", "978-1-501-11110-5",
              ["mood:motivated", "self-help", "psychology", "resilience", "success"], total_copies=3),
    make_book("Mindset: The New Psychology of Success", "Carol Dweck", "978-0-345-47232-8",
              ["mood:motivated", "self-help", "psychology", "growth mindset", "education"], total_copies=4),
    make_book("Man's Search for Meaning", "Viktor Frankl", "978-0-807-01427-1",
              ["mood:motivated", "biography", "memoir", "philosophy", "psychology"], total_copies=4),
    make_book("Start with Why", "Simon Sinek", "978-1-591-84280-8",
              ["mood:motivated", "self-help", "leadership", "business", "inspiration"], total_copies=3),
    make_book("Can't Hurt Me", "David Goggins", "978-1-544-51273-3",
              ["mood:motivated", "biography", "memoir", "resilience", "discipline"], total_copies=4),
    make_book("The Lean Startup", "Eric Ries", "978-0-307-88789-4",
              ["mood:motivated", "self-help", "entrepreneurship", "business", "innovation"], total_copies=3),
    make_book("Zero to One", "Peter Thiel", "978-0-804-13930-3",
              ["mood:motivated", "self-help", "entrepreneurship", "startups", "business"], total_copies=3),
    make_book("Dare to Lead", "Brené Brown", "978-0-399-59214-0",
              ["mood:motivated", "self-help", "leadership", "vulnerability", "courage"], total_copies=3),
]

# ── Mood: Curious / Intellectual (10+) ────────────────────────────────────────
CURIOUS_BOOKS = [
    make_book("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "978-0-062-31609-7",
              ["mood:curious", "non-fiction", "history", "anthropology", "science"], total_copies=5),
    make_book("A Brief History of Time", "Stephen Hawking", "978-0-553-38016-3",
              ["mood:curious", "non-fiction", "physics", "cosmology", "science"], total_copies=3),
    make_book("The Selfish Gene", "Richard Dawkins", "978-0-19-857519-1",
              ["mood:curious", "non-fiction", "biology", "evolution", "science"], total_copies=3),
    make_book("Thinking, Fast and Slow", "Daniel Kahneman", "978-0-374-53355-7",
              ["mood:curious", "non-fiction", "psychology", "decision making", "behavioural economics"], total_copies=4),
    make_book("The Innovators", "Walter Isaacson", "978-1-476-70869-3",
              ["mood:curious", "biography", "technology", "history", "computing"], total_copies=2),
    make_book("Freakonomics", "Steven Levitt", "978-0-060-73132-1",
              ["mood:curious", "non-fiction", "economics", "data", "social science"], total_copies=4),
    make_book("The Demon-Haunted World", "Carl Sagan", "978-0-345-40946-9",
              ["mood:curious", "non-fiction", "science", "critical thinking", "skepticism"], total_copies=3),
    make_book("Cosmos", "Carl Sagan", "978-0-345-53943-4",
              ["mood:curious", "non-fiction", "astronomy", "science", "philosophy"], total_copies=3),
    make_book("The Gene: An Intimate History", "Siddhartha Mukherjee", "978-1-476-73350-8",
              ["mood:curious", "non-fiction", "biology", "genetics", "history"], total_copies=2),
    make_book("Outliers: The Story of Success", "Malcolm Gladwell", "978-0-316-01792-3",
              ["mood:curious", "non-fiction", "sociology", "success", "psychology"], total_copies=4),
    make_book("The Man from the Future", "Ananyo Bhattacharya", "978-0-393-86783-0",
              ["mood:curious", "biography", "science", "mathematics", "history"], total_copies=2),
]

# ── Mood: Romantic / Dreamy (10+) ─────────────────────────────────────────────
ROMANTIC_MOOD_BOOKS = [
    make_book("Call Me By Your Name", "André Aciman", "978-0-312-42678-1",
              ["mood:romantic", "fiction", "romance", "literary fiction", "coming of age"], total_copies=3),
    make_book("The Notebook", "Nicholas Sparks", "978-0-446-60523-3",
              ["mood:romantic", "romance", "contemporary", "love story", "fiction"], total_copies=4),
    make_book("Jane Eyre", "Charlotte Brontë", "978-0-14-144114-6",
              ["mood:romantic", "romance", "classic", "gothic", "fiction"], total_copies=3),
    make_book("Normal People", "Sally Rooney", "978-0-571-33481-5",
              ["mood:romantic", "fiction", "romance", "contemporary", "literary fiction"], total_copies=4),
    make_book("The Time Traveler's Wife", "Audrey Niffenegger", "978-0-156-02943-6",
              ["mood:romantic", "fiction", "romance", "time travel", "literary fiction"], total_copies=3),
    make_book("Wuthering Heights", "Emily Brontë", "978-0-14-143955-6",
              ["mood:romantic", "romance", "classic", "gothic", "fiction"], total_copies=3),
    make_book("Attachment", "Isabel Allende", "978-0-062-75757-6",
              ["mood:romantic", "fiction", "magical realism", "love", "contemporary"], total_copies=2),
    make_book("Everything I Never Told You", "Celeste Ng", "978-0-143-12771-1",
              ["mood:romantic", "fiction", "family drama", "literary fiction", "romance"], total_copies=3),
    make_book("The Bridges of Madison County", "Robert James Waller", "978-0-446-51652-7",
              ["mood:romantic", "romance", "contemporary", "love story", "fiction"], total_copies=2),
    make_book("Beach Read", "Emily Henry", "978-1-984-80585-1",
              ["mood:romantic", "romance", "contemporary", "summer", "fiction"], total_copies=4),
    make_book("Daisy Jones and the Six", "Taylor Jenkins Reid", "978-1-524-79894-9",
              ["mood:romantic", "fiction", "romance", "music", "contemporary"], total_copies=3),
]

# ── Mood: Bored / Need Thrill (10+) ───────────────────────────────────────────
THRILLING_BOOKS = [
    make_book("Gone Girl", "Gillian Flynn", "978-0-307-58836-4",
              ["mood:bored", "fiction", "thriller", "psychological", "mystery"], total_copies=4),
    make_book("The Girl with the Dragon Tattoo", "Stieg Larsson", "978-0-307-45454-1",
              ["mood:bored", "fiction", "thriller", "crime", "mystery"], total_copies=3),
    make_book("The Da Vinci Code", "Dan Brown", "978-0-385-50420-5",
              ["mood:bored", "fiction", "thriller", "mystery", "adventure"], total_copies=5),
    make_book("Big Little Lies", "Liane Moriarty", "978-0-399-58767-1",
              ["mood:bored", "fiction", "thriller", "mystery", "drama"], total_copies=4),
    make_book("Sharp Objects", "Gillian Flynn", "978-0-307-34150-6",
              ["mood:bored", "fiction", "thriller", "psychological", "mystery"], total_copies=3),
    make_book("The Silent Patient", "Alex Michaelides", "978-1-250-30169-5",
              ["mood:bored", "fiction", "thriller", "psychological", "mystery"], total_copies=5),
    make_book("In the Woods", "Tana French", "978-0-670-03862-6",
              ["mood:bored", "fiction", "thriller", "crime", "mystery"], total_copies=3),
    make_book("The Woman in the Window", "A. J. Finn", "978-0-062-72420-2",
              ["mood:bored", "fiction", "thriller", "psychological", "mystery"], total_copies=4),
    make_book("1Q84", "Haruki Murakami", "978-0-307-59312-2",
              ["mood:bored", "fiction", "thriller", "magical realism", "literary fiction"], total_copies=2),
    make_book("And Then There Were None", "Agatha Christie", "978-0-062-07399-0",
              ["mood:bored", "fiction", "thriller", "crime", "classic mystery"], total_copies=4),
    make_book("The Maze Runner", "James Dashner", "978-0-385-73795-5",
              ["mood:bored", "fiction", "thriller", "dystopia", "young adult"], total_copies=4),
]

MOOD_BOOKS = (
    SAD_BOOKS + HAPPY_BOOKS + STRESSED_BOOKS + ADVENTUROUS_BOOKS +
    MOTIVATED_BOOKS + CURIOUS_BOOKS + ROMANTIC_MOOD_BOOKS + THRILLING_BOOKS
)

# =============================================================================
# CHATBOT-SUGGESTED BOOKS
# These are the titles WatsonX AI actually recommends in the chatbot for each
# mood / interest keyword. Organised by the user phrase that triggers them.
# =============================================================================

# ── "I feel lonely / isolated" ────────────────────────────────────────────────
LONELY_BOOKS = [
    make_book("The Midnight Library", "Matt Haig", "978-0-525-55947-4",
              ["mood:sad", "mood:lonely", "fiction", "magical realism", "self-discovery"], total_copies=4),
    make_book("Norwegian Wood", "Haruki Murakami", "978-0-375-70402-0",
              ["mood:sad", "mood:lonely", "fiction", "literary fiction", "coming of age"], total_copies=3),
    make_book("The Perks of Being a Wallflower", "Stephen Chbosky", "978-1-451-69696-3",
              ["mood:sad", "mood:lonely", "fiction", "young adult", "coming of age"], total_copies=4),
    make_book("Eleanor & Park", "Rainbow Rowell", "978-1-250-01257-1",
              ["mood:sad", "mood:lonely", "fiction", "young adult", "romance"], total_copies=3),
    make_book("All the Bright Places", "Jennifer Niven", "978-0-385-75588-7",
              ["mood:sad", "mood:lonely", "fiction", "young adult", "mental health"], total_copies=3),
    make_book("A Man Called Ove", "Fredrik Backman", "978-1-476-73801-5",
              ["mood:sad", "mood:lonely", "fiction", "contemporary", "uplifting"], total_copies=4),
    make_book("The Little Prince", "Antoine de Saint-Exupéry", "978-0-156-01219-5",
              ["mood:sad", "mood:lonely", "fiction", "classic", "philosophical"], total_copies=5),
]

# ── "I feel anxious / overwhelmed / burned out" ───────────────────────────────
ANXIOUS_BOOKS = [
    make_book("First, We Make the Beast Beautiful", "Sarah Wilson", "978-0-062-85961-4",
              ["mood:stressed", "mood:anxious", "self-help", "anxiety", "mindfulness"], total_copies=3),
    make_book("The Anxiety Solution", "Chloe Brotheridge", "978-0-718-18529-7",
              ["mood:stressed", "mood:anxious", "self-help", "anxiety", "CBT"], total_copies=3),
    make_book("Burnout: The Secret to Unlocking the Stress Cycle", "Emily Nagoski", "978-1-984-82300-3",
              ["mood:stressed", "mood:anxious", "self-help", "burnout", "women"], total_copies=3),
    make_book("Full Catastrophe Living", "Jon Kabat-Zinn", "978-0-345-53972-4",
              ["mood:stressed", "mood:anxious", "mindfulness", "MBSR", "health"], total_copies=2),
    make_book("The Body Keeps the Score", "Bessel van der Kolk", "978-0-143-12742-1",
              ["mood:stressed", "mood:anxious", "non-fiction", "trauma", "mental health"], total_copies=3),
    make_book("Reasons to Stay Alive", "Matt Haig", "978-0-143-10723-2",
              ["mood:stressed", "mood:anxious", "biography", "memoir", "mental health"], total_copies=4),
    make_book("How to Stop Worrying and Start Living", "Dale Carnegie", "978-0-671-73335-0",
              ["mood:stressed", "mood:anxious", "self-help", "classic", "worry"], total_copies=3),
    make_book("Untamed", "Glennon Doyle", "978-1-984-80125-9",
              ["mood:stressed", "mood:anxious", "biography", "memoir", "empowerment"], total_copies=4),
]

# ── "I feel happy / excited / joyful" ────────────────────────────────────────
JOYFUL_BOOKS = [
    make_book("The 100-Year-Old Man Who Climbed Out the Window and Disappeared", "Jonas Jonasson", "978-1-401-31026-5",
              ["mood:happy", "fiction", "comedy", "adventure", "contemporary"], total_copies=3),
    make_book("Catch-22", "Joseph Heller", "978-1-451-62634-8",
              ["mood:happy", "fiction", "classic", "satire", "war"], total_copies=2),
    make_book("P.G. Wodehouse: The Code of the Woosters", "P. G. Wodehouse", "978-0-393-31306-1",
              ["mood:happy", "fiction", "classic", "comedy", "british"], total_copies=2),
    make_book("Where the Crawdads Sing", "Delia Owens", "978-0-735-22454-8",
              ["mood:happy", "fiction", "mystery", "nature", "coming of age"], total_copies=5),
    make_book("The Guernsey Literary and Potato Peel Pie Society", "Mary Ann Shaffer", "978-0-385-34099-1",
              ["mood:happy", "fiction", "historical fiction", "books about books", "heartwarming"], total_copies=3),
    make_book("The Thursday Murder Club", "Richard Osman", "978-0-241-42557-3",
              ["mood:happy", "fiction", "mystery", "comedy", "cozy"], total_copies=4),
    make_book("Klara and the Sun", "Kazuo Ishiguro", "978-0-593-31817-1",
              ["mood:happy", "fiction", "science fiction", "literary fiction", "AI"], total_copies=3),
]

# ── "I want something inspirational / life-changing" ─────────────────────────
LIFE_CHANGING_BOOKS = [
    make_book("The Power of Habit", "Charles Duhigg", "978-0-812-98160-4",
              ["mood:motivated", "non-fiction", "habits", "psychology", "neuroscience"], total_copies=4),
    make_book("Essentialism: The Disciplined Pursuit of Less", "Greg McKeown", "978-0-804-13714-9",
              ["mood:motivated", "self-help", "productivity", "simplicity", "focus"], total_copies=3),
    make_book("The 4-Hour Work Week", "Tim Ferriss", "978-0-307-35313-9",
              ["mood:motivated", "self-help", "entrepreneurship", "lifestyle", "productivity"], total_copies=3),
    make_book("Rich Dad Poor Dad", "Robert T. Kiyosaki", "978-1-612-68097-9",
              ["mood:motivated", "self-help", "personal finance", "entrepreneurship"], total_copies=4),
    make_book("The Road Less Travelled", "M. Scott Peck", "978-0-743-24315-7",
              ["mood:motivated", "self-help", "psychology", "spirituality", "growth"], total_copies=3),
    make_book("Meditations", "Marcus Aurelius", "978-0-140-44140-6",
              ["mood:motivated", "mood:curious", "philosophy", "stoicism", "classic"], total_copies=4),
    make_book("Letters from a Stoic", "Seneca", "978-0-140-44210-6",
              ["mood:motivated", "mood:curious", "philosophy", "stoicism", "classic"], total_copies=3),
    make_book("How to Win Friends and Influence People", "Dale Carnegie", "978-0-671-02735-1",
              ["mood:motivated", "self-help", "communication", "leadership", "classic"], total_copies=5),
    make_book("Never Split the Difference", "Chris Voss", "978-0-062-40780-1",
              ["mood:motivated", "non-fiction", "negotiation", "communication", "FBI"], total_copies=3),
    make_book("The War of Art", "Steven Pressfield", "978-1-936-89120-7",
              ["mood:motivated", "self-help", "creativity", "writing", "discipline"], total_copies=3),
]

# ── "I want a fantasy / escape / magic" ──────────────────────────────────────
FANTASY_BOOKS = [
    make_book("The Lord of the Rings", "J. R. R. Tolkien", "978-0-544-00341-5",
              ["mood:adventurous", "fiction", "fantasy", "epic", "classic"], total_copies=3),
    make_book("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "978-0-439-70818-8",
              ["mood:adventurous", "fiction", "fantasy", "magic", "young adult"], total_copies=6),
    make_book("The Name of the Wind", "Patrick Rothfuss", "978-0-756-40407-9",
              ["mood:adventurous", "fiction", "fantasy", "magic", "epic fantasy"], total_copies=3),
    make_book("A Game of Thrones", "George R. R. Martin", "978-0-553-57340-2",
              ["mood:adventurous", "fiction", "fantasy", "epic", "political"], total_copies=4),
    make_book("The Night Circus", "Erin Morgenstern", "978-0-307-74441-0",
              ["mood:adventurous", "mood:romantic", "fiction", "fantasy", "magical realism"], total_copies=3),
    make_book("Six of Crows", "Leigh Bardugo", "978-1-250-07643-9",
              ["mood:adventurous", "fiction", "fantasy", "heist", "young adult"], total_copies=4),
    make_book("The Priory of the Orange Tree", "Samantha Shannon", "978-1-635-57525-3",
              ["mood:adventurous", "fiction", "fantasy", "feminism", "dragons"], total_copies=2),
    make_book("Jonathan Strange & Mr Norrell", "Susanna Clarke", "978-0-765-35615-3",
              ["mood:adventurous", "fiction", "fantasy", "alternate history", "magic"], total_copies=2),
    make_book("The Final Empire (Mistborn)", "Brandon Sanderson", "978-0-765-31178-2",
              ["mood:adventurous", "fiction", "fantasy", "magic system", "epic"], total_copies=3),
    make_book("The Lies of Locke Lamora", "Scott Lynch", "978-0-553-58894-9",
              ["mood:adventurous", "mood:bored", "fiction", "fantasy", "heist"], total_copies=2),
]

# ── "I want science fiction / future / space" ────────────────────────────────
SCI_FI_BOOKS = [
    make_book("The Martian", "Andy Weir", "978-0-553-41802-6",
              ["mood:adventurous", "mood:curious", "fiction", "science fiction", "survival"], total_copies=5),
    make_book("Project Hail Mary", "Andy Weir", "978-0-593-13520-4",
              ["mood:adventurous", "mood:curious", "fiction", "science fiction", "space"], total_copies=4),
    make_book("Ender's Game", "Orson Scott Card", "978-0-765-32963-0",
              ["mood:adventurous", "fiction", "science fiction", "military", "young adult"], total_copies=3),
    make_book("The Three-Body Problem", "Liu Cixin", "978-0-765-38260-4",
              ["mood:curious", "fiction", "science fiction", "physics", "China"], total_copies=3),
    make_book("Hyperion", "Dan Simmons", "978-0-553-28368-5",
              ["mood:adventurous", "mood:curious", "fiction", "science fiction", "epic", "space"], total_copies=2),
    make_book("Foundation", "Isaac Asimov", "978-0-553-80371-0",
              ["mood:curious", "fiction", "science fiction", "classic", "empire"], total_copies=3),
    make_book("Flowers for Algernon", "Daniel Keyes", "978-0-15-603008-5",
              ["mood:sad", "mood:curious", "fiction", "science fiction", "intelligence", "classic"], total_copies=3),
    make_book("Ready Player One", "Ernest Cline", "978-0-307-88743-6",
              ["mood:adventurous", "mood:happy", "fiction", "science fiction", "gaming", "nostalgia"], total_copies=5),
    make_book("The Left Hand of Darkness", "Ursula K. Le Guin", "978-0-441-47812-5",
              ["mood:curious", "fiction", "science fiction", "gender", "literary fiction"], total_copies=2),
    make_book("Recursion", "Blake Crouch", "978-1-524-75978-1",
              ["mood:bored", "mood:curious", "fiction", "science fiction", "thriller", "time"], total_copies=3),
    make_book("Dark Matter", "Blake Crouch", "978-1-101-90422-3",
              ["mood:bored", "mood:curious", "fiction", "science fiction", "thriller", "parallel universe"], total_copies=4),
]

# ── "I want a mystery / detective / crime" ───────────────────────────────────
MYSTERY_BOOKS = [
    make_book("The Murder of Roger Ackroyd", "Agatha Christie", "978-0-062-07389-1",
              ["mood:bored", "fiction", "mystery", "classic", "detective"], total_copies=3),
    make_book("Murder on the Orient Express", "Agatha Christie", "978-0-062-07392-1",
              ["mood:bored", "fiction", "mystery", "classic", "detective"], total_copies=4),
    make_book("The Hound of the Baskervilles", "Arthur Conan Doyle", "978-0-140-43757-7",
              ["mood:bored", "fiction", "mystery", "classic", "Sherlock Holmes"], total_copies=3),
    make_book("Big Little Lies", "Liane Moriarty", "978-0-399-58767-1",
              ["mood:bored", "fiction", "thriller", "mystery", "drama"], total_copies=4),
    make_book("The Girl on the Train", "Paula Hawkins", "978-1-594-63480-8",
              ["mood:bored", "fiction", "psychological thriller", "mystery"], total_copies=4),
    make_book("In the Woods", "Tana French", "978-0-670-03862-6",
              ["mood:bored", "fiction", "thriller", "crime", "mystery"], total_copies=3),
    make_book("The Secret History", "Donna Tartt", "978-0-679-41032-8",
              ["mood:bored", "mood:curious", "fiction", "literary thriller", "mystery"], total_copies=3),
    make_book("Verity", "Colleen Hoover", "978-1-538-72468-7",
              ["mood:bored", "fiction", "thriller", "psychological", "romance"], total_copies=4),
    make_book("The Thursday Murder Club", "Richard Osman", "978-0-241-42557-3",
              ["mood:happy", "mood:bored", "fiction", "mystery", "comedy", "cozy"], total_copies=4),
]

# ── "I want history / non-fiction / real events" ─────────────────────────────
HISTORY_BOOKS = [
    make_book("Guns, Germs, and Steel", "Jared Diamond", "978-0-393-31755-8",
              ["mood:curious", "non-fiction", "history", "anthropology", "science"], total_copies=3),
    make_book("The Silk Roads", "Peter Frankopan", "978-1-101-94344-4",
              ["mood:curious", "non-fiction", "history", "global history", "trade"], total_copies=3),
    make_book("Homo Deus", "Yuval Noah Harari", "978-0-062-46465-8",
              ["mood:curious", "non-fiction", "history", "future", "technology"], total_copies=3),
    make_book("The Diary of a Young Girl", "Anne Frank", "978-0-553-29698-3",
              ["mood:sad", "mood:curious", "biography", "memoir", "world war ii", "historical"], total_copies=4),
    make_book("Night", "Elie Wiesel", "978-0-374-50001-6",
              ["mood:sad", "biography", "memoir", "holocaust", "historical"], total_copies=3),
    make_book("The Immortal Life of Henrietta Lacks", "Rebecca Skloot", "978-1-400-05218-9",
              ["mood:curious", "non-fiction", "science", "ethics", "history"], total_copies=3),
    make_book("Educated", "Tara Westover", "978-0-399-59050-4",
              ["mood:curious", "mood:motivated", "biography", "memoir", "coming of age"], total_copies=3),
    make_book("Born a Crime", "Trevor Noah", "978-0-399-58805-0",
              ["mood:happy", "mood:curious", "biography", "memoir", "South Africa", "humour"], total_copies=4),
    make_book("The Wright Brothers", "David McCullough", "978-1-476-72883-7",
              ["mood:curious", "mood:motivated", "biography", "history", "aviation"], total_copies=2),
    make_book("Alexander Hamilton", "Ron Chernow", "978-0-143-03475-9",
              ["mood:curious", "biography", "history", "American history"], total_copies=2),
]

# ── "I want philosophy / meaning / deep thinking" ────────────────────────────
PHILOSOPHY_BOOKS = [
    make_book("Sophie's World", "Jostein Gaarder", "978-0-374-53087-7",
              ["mood:curious", "fiction", "philosophy", "history of philosophy", "young adult"], total_copies=3),
    make_book("The Republic", "Plato", "978-0-872-20316-4",
              ["mood:curious", "philosophy", "classic", "political philosophy"], total_copies=2),
    make_book("Beyond Good and Evil", "Friedrich Nietzsche", "978-0-679-72465-5",
              ["mood:curious", "philosophy", "classic", "ethics", "existentialism"], total_copies=2),
    make_book("Being and Nothingness", "Jean-Paul Sartre", "978-0-671-82725-2",
              ["mood:curious", "philosophy", "existentialism", "classic"], total_copies=2),
    make_book("The Stranger", "Albert Camus", "978-0-679-72020-1",
              ["mood:sad", "mood:curious", "fiction", "existentialism", "classic", "absurdism"], total_copies=3),
    make_book("Crime and Punishment", "Fyodor Dostoevsky", "978-0-140-44913-6",
              ["mood:sad", "mood:curious", "fiction", "classic", "psychological", "Russian literature"], total_copies=2),
    make_book("The Brothers Karamazov", "Fyodor Dostoevsky", "978-0-374-52837-7",
              ["mood:curious", "fiction", "classic", "philosophy", "Russian literature"], total_copies=2),
    make_book("When Nietzsche Wept", "Irvin D. Yalom", "978-0-061-09699-1",
              ["mood:curious", "fiction", "philosophy", "psychology", "historical fiction"], total_copies=2),
    make_book("The Courage to Be Disliked", "Ichiro Kishimi", "978-1-501-15713-2",
              ["mood:motivated", "mood:stressed", "self-help", "philosophy", "Adlerian psychology"], total_copies=4),
    make_book("Man's Search for Meaning", "Viktor Frankl", "978-0-807-01427-1",
              ["mood:motivated", "mood:sad", "biography", "memoir", "philosophy", "psychology"], total_copies=4),
]

# ── "I want something funny / comedy" ────────────────────────────────────────
COMEDY_BOOKS = [
    make_book("Yes Please", "Amy Poehler", "978-0-062-69386-6",
              ["mood:happy", "biography", "memoir", "comedy", "feminism"], total_copies=3),
    make_book("Bossypants", "Tina Fey", "978-0-316-05686-8",
              ["mood:happy", "biography", "memoir", "comedy", "feminism"], total_copies=3),
    make_book("Is Everyone Hanging Out Without Me?", "Mindy Kaling", "978-0-307-88691-0",
              ["mood:happy", "biography", "memoir", "comedy", "pop culture"], total_copies=3),
    make_book("The Naked Ape", "Desmond Morris", "978-0-385-33430-3",
              ["mood:curious", "non-fiction", "anthropology", "human behaviour", "science"], total_copies=2),
    make_book("Bill Bryson: A Short History of Nearly Everything", "Bill Bryson", "978-0-767-90818-7",
              ["mood:happy", "mood:curious", "non-fiction", "science", "history", "humour"], total_copies=3),
    make_book("Notes from a Small Island", "Bill Bryson", "978-0-552-99600-0",
              ["mood:happy", "biography", "memoir", "travel", "humour"], total_copies=3),
    make_book("The Inimitable Jeeves", "P. G. Wodehouse", "978-0-140-01685-2",
              ["mood:happy", "fiction", "classic", "comedy", "british"], total_copies=2),
    make_book("Good Talk: A Memoir in Conversations", "Mira Jacob", "978-1-250-29647-0",
              ["mood:happy", "biography", "memoir", "graphic memoir", "identity"], total_copies=2),
]

# ── "I want self-improvement / career / productivity" ─────────────────────────
PRODUCTIVITY_BOOKS = [
    make_book("Getting Things Done", "David Allen", "978-0-143-12640-0",
              ["mood:motivated", "self-help", "productivity", "time management", "GTD"], total_copies=3),
    make_book("The One Thing", "Gary Keller", "978-1-885-16711-8",
              ["mood:motivated", "self-help", "productivity", "focus", "success"], total_copies=3),
    make_book("Digital Minimalism", "Cal Newport", "978-0-525-53657-4",
              ["mood:motivated", "mood:stressed", "self-help", "technology", "focus"], total_copies=3),
    make_book("So Good They Can't Ignore You", "Cal Newport", "978-1-455-50912-8",
              ["mood:motivated", "self-help", "career", "mastery", "passion"], total_copies=3),
    make_book("Make It Stick", "Peter Brown", "978-0-674-72901-8",
              ["mood:motivated", "mood:curious", "non-fiction", "learning", "memory", "education"], total_copies=3),
    make_book("Eat That Frog!", "Brian Tracy", "978-1-626-56941-3",
              ["mood:motivated", "self-help", "productivity", "procrastination"], total_copies=3),
    make_book("Range: Why Generalists Triumph in a Specialized World", "David Epstein", "978-0-735-21404-4",
              ["mood:curious", "mood:motivated", "non-fiction", "psychology", "career", "skills"], total_copies=3),
    make_book("Principles", "Ray Dalio", "978-1-501-12408-2",
              ["mood:motivated", "self-help", "leadership", "business", "decision making"], total_copies=3),
    make_book("Ultralearning", "Scott Young", "978-0-062-88268-3",
              ["mood:motivated", "self-help", "learning", "skill acquisition", "education"], total_copies=3),
]

# ── "I want romance / love / relationships" ───────────────────────────────────
ROMANCE_CHAT_BOOKS = [
    make_book("Love in the Time of Cholera", "Gabriel Garcia Marquez", "978-0-307-38973-5",
              ["mood:romantic", "fiction", "literary fiction", "love story", "magical realism"], total_copies=2),
    make_book("Anna Karenina", "Leo Tolstoy", "978-0-143-10430-9",
              ["mood:romantic", "mood:sad", "fiction", "classic", "Russian literature", "tragedy"], total_copies=2),
    make_book("Pride and Prejudice", "Jane Austen", "978-0-14-143951-8",
              ["mood:romantic", "romance", "classic", "regency", "fiction"], total_copies=3),
    make_book("Sense and Sensibility", "Jane Austen", "978-0-14-143966-2",
              ["mood:romantic", "romance", "classic", "regency", "fiction"], total_copies=3),
    make_book("Outlander", "Diana Gabaldon", "978-0-440-21256-1",
              ["mood:romantic", "romance", "historical fiction", "adventure", "time travel"], total_copies=2),
    make_book("The Hating Game", "Sally Thorne", "978-0-062-67029-3",
              ["mood:romantic", "romance", "contemporary", "office romance", "comedy"], total_copies=3),
    make_book("Book Lovers", "Emily Henry", "978-0-593-33499-7",
              ["mood:romantic", "mood:happy", "romance", "contemporary", "books about books"], total_copies=4),
    make_book("It Ends with Us", "Colleen Hoover", "978-1-501-16054-9",
              ["mood:romantic", "mood:sad", "romance", "contemporary", "drama"], total_copies=4),
    make_book("Ugly Love", "Colleen Hoover", "978-1-476-75482-1",
              ["mood:romantic", "romance", "contemporary", "drama", "new adult"], total_copies=3),
]

# ── "I want horror / dark / creepy" ───────────────────────────────────────────
HORROR_CHAT_BOOKS = [
    make_book("The Stand", "Stephen King", "978-0-307-74365-9",
              ["mood:bored", "fiction", "horror", "post-apocalyptic", "epic"], total_copies=2),
    make_book("Misery", "Stephen King", "978-1-501-16646-6",
              ["mood:bored", "fiction", "horror", "psychological", "thriller"], total_copies=3),
    make_book("The Silence of the Lambs", "Thomas Harris", "978-0-312-92458-1",
              ["mood:bored", "fiction", "thriller", "psychological", "crime"], total_copies=3),
    make_book("Rebecca", "Daphne du Maurier", "978-0-380-73040-9",
              ["mood:bored", "mood:romantic", "fiction", "gothic", "psychological thriller"], total_copies=3),
    make_book("Mexican Gothic", "Silvia Moreno-Garcia", "978-0-525-62069-1",
              ["mood:bored", "fiction", "horror", "gothic", "historical fiction"], total_copies=3),
    make_book("Piranesi", "Susanna Clarke", "978-1-635-57535-2",
              ["mood:bored", "mood:curious", "fiction", "fantasy", "mystery", "surreal"], total_copies=3),
    make_book("The Haunting of Hill House", "Shirley Jackson", "978-0-14-303998-7",
              ["mood:bored", "fiction", "horror", "psychological", "gothic", "classic"], total_copies=2),
    make_book("Mexican Gothic", "Silvia Moreno-Garcia", "978-0-525-62070-7",
              ["mood:bored", "fiction", "horror", "gothic", "dark"], total_copies=2),
]

# ── "I want sports / fitness / health" ────────────────────────────────────────
SPORTS_BOOKS = [
    make_book("Born to Run", "Christopher McDougall", "978-0-307-27990-0",
              ["mood:adventurous", "mood:motivated", "non-fiction", "running", "fitness"], total_copies=3),
    make_book("Shoe Dog", "Phil Knight", "978-1-476-71808-1",
              ["mood:motivated", "biography", "memoir", "entrepreneurship", "Nike"], total_copies=4),
    make_book("The Champion's Mind", "Jim Afremow", "978-1-623-36356-0",
              ["mood:motivated", "self-help", "sports psychology", "mental performance"], total_copies=3),
    make_book("Endure: Mind, Body, and the Curiously Elastic Limits of Human Performance", "Alex Hutchinson", "978-0-062-65992-9",
              ["mood:motivated", "mood:adventurous", "non-fiction", "sports science", "endurance"], total_copies=2),
    make_book("The Obstacle Is the Way", "Ryan Holiday", "978-1-591-84660-8",
              ["mood:motivated", "mood:stressed", "self-help", "stoicism", "resilience"], total_copies=4),
    make_book("Finding Ultra", "Rich Roll", "978-0-307-95267-9",
              ["mood:motivated", "mood:adventurous", "biography", "memoir", "triathlon", "plant-based"], total_copies=2),
    make_book("Open: An Autobiography", "Andre Agassi", "978-0-307-38818-9",
              ["mood:motivated", "biography", "memoir", "tennis", "sport"], total_copies=3),
]

# ── "I want technology / coding / computer science" ────────────────────────────
TECH_BOOKS = [
    make_book("The Pragmatic Programmer", "David Thomas", "978-0-135-95705-9",
              ["mood:motivated", "non-fiction", "programming", "software engineering", "career"], total_copies=3),
    make_book("Clean Code", "Robert C. Martin", "978-0-132-35088-4",
              ["mood:motivated", "non-fiction", "programming", "software engineering", "best practices"], total_copies=3),
    make_book("The Mythical Man-Month", "Frederick P. Brooks Jr.", "978-0-201-83595-3",
              ["mood:curious", "non-fiction", "software engineering", "management", "classic"], total_copies=2),
    make_book("Code: The Hidden Language of Computer Hardware and Software", "Charles Petzold", "978-0-735-61103-4",
              ["mood:curious", "non-fiction", "computer science", "technology", "education"], total_copies=3),
    make_book("The Innovators", "Walter Isaacson", "978-1-476-70869-3",
              ["mood:curious", "biography", "technology", "history", "computing"], total_copies=2),
    make_book("Zero to One", "Peter Thiel", "978-0-804-13930-3",
              ["mood:motivated", "self-help", "entrepreneurship", "startups", "technology"], total_copies=3),
    make_book("The Phoenix Project", "Gene Kim", "978-1-942-78807-7",
              ["mood:motivated", "mood:curious", "fiction", "technology", "DevOps", "business"], total_copies=3),
    make_book("Superintelligence", "Nick Bostrom", "978-0-199-67811-2",
              ["mood:curious", "non-fiction", "AI", "philosophy", "future"], total_copies=2),
    make_book("Life 3.0", "Max Tegmark", "978-1-101-94659-9",
              ["mood:curious", "non-fiction", "AI", "future", "science"], total_copies=2),
]

# ── "I want travel / culture / world" ─────────────────────────────────────────
TRAVEL_BOOKS = [
    make_book("In Patagonia", "Bruce Chatwin", "978-0-14-011291-2",
              ["mood:adventurous", "biography", "travel", "South America", "adventure"], total_copies=2),
    make_book("Eat, Pray, Love", "Elizabeth Gilbert", "978-0-143-03841-2",
              ["mood:adventurous", "mood:motivated", "biography", "memoir", "travel", "self-discovery"], total_copies=4),
    make_book("The Motorcycle Diaries", "Ernesto Che Guevara", "978-1-920-88823-5",
              ["mood:adventurous", "biography", "memoir", "travel", "South America"], total_copies=2),
    make_book("The Beach", "Alex Garland", "978-0-140-27393-5",
              ["mood:adventurous", "fiction", "thriller", "travel", "backpacking"], total_copies=3),
    make_book("Shantaram", "Gregory David Roberts", "978-0-312-33052-3",
              ["mood:adventurous", "fiction", "memoir", "India", "crime"], total_copies=2),
    make_book("A Year in Provence", "Peter Mayle", "978-0-679-73114-9",
              ["mood:happy", "biography", "memoir", "travel", "France"], total_copies=2),
    make_book("The Alchemist", "Paulo Coelho", "978-0-06-112241-5",
              ["mood:adventurous", "mood:motivated", "fiction", "philosophical fiction", "travel"], total_copies=4),
]

# ── "I want young adult / teen / coming of age" ───────────────────────────────
YA_BOOKS = [
    make_book("The Hunger Games", "Suzanne Collins", "978-0-439-02352-8",
              ["mood:adventurous", "mood:bored", "fiction", "young adult", "dystopia", "action"], total_copies=5),
    make_book("Divergent", "Veronica Roth", "978-0-062-02402-5",
              ["mood:adventurous", "fiction", "young adult", "dystopia", "action"], total_copies=4),
    make_book("The Giver", "Lois Lowry", "978-0-544-33615-0",
              ["mood:curious", "mood:sad", "fiction", "young adult", "dystopia", "classic"], total_copies=4),
    make_book("Wonder", "R. J. Palacio", "978-0-375-86902-0",
              ["mood:sad", "mood:motivated", "fiction", "young adult", "disability", "kindness"], total_copies=5),
    make_book("The Outsiders", "S. E. Hinton", "978-0-141-31239-6",
              ["mood:sad", "fiction", "young adult", "classic", "gang", "coming of age"], total_copies=3),
    make_book("Speak", "Laurie Halse Anderson", "978-0-312-67439-1",
              ["mood:sad", "fiction", "young adult", "trauma", "mental health"], total_copies=3),
    make_book("The House on Mango Street", "Sandra Cisneros", "978-0-679-73477-5",
              ["mood:sad", "mood:curious", "fiction", "young adult", "identity", "Chicana"], total_copies=3),
    make_book("To Kill a Mockingbird", "Harper Lee", "978-0-06-112008-4",
              ["mood:curious", "mood:sad", "fiction", "classic", "social justice", "coming of age"], total_copies=4),
    make_book("The Catcher in the Rye", "J. D. Salinger", "978-0-316-76948-0",
              ["mood:sad", "mood:lonely", "fiction", "classic", "young adult", "coming of age"], total_copies=3),
    make_book("Paper Towns", "John Green", "978-0-525-47818-8",
              ["mood:adventurous", "mood:romantic", "fiction", "young adult", "mystery", "road trip"], total_copies=3),
]

# ── "I want poetry / literary / art" ─────────────────────────────────────────
LITERARY_BOOKS = [
    make_book("Milk and Honey", "Rupi Kaur", "978-1-449-47171-1",
              ["mood:sad", "mood:motivated", "poetry", "feminism", "healing"], total_copies=4),
    make_book("The Sun and Her Flowers", "Rupi Kaur", "978-1-449-48623-4",
              ["mood:sad", "mood:motivated", "poetry", "feminism", "nature"], total_copies=3),
    make_book("Leaves of Grass", "Walt Whitman", "978-0-199-55345-9",
              ["mood:happy", "mood:curious", "poetry", "American literature", "classic"], total_copies=2),
    make_book("Invisible Man", "Ralph Ellison", "978-0-679-73276-4",
              ["mood:curious", "fiction", "classic", "African American literature", "identity"], total_copies=2),
    make_book("The Great Gatsby", "F. Scott Fitzgerald", "978-0-743-27356-5",
              ["mood:sad", "mood:curious", "fiction", "classic", "American literature", "Jazz Age"], total_copies=3),
    make_book("Lolita", "Vladimir Nabokov", "978-0-679-72020-1",
              ["mood:curious", "fiction", "classic", "literary fiction", "controversial"], total_copies=2),
    make_book("The Sound and the Fury", "William Faulkner", "978-0-679-73224-5",
              ["mood:curious", "fiction", "classic", "American literature", "stream of consciousness"], total_copies=2),
    make_book("Their Eyes Were Watching God", "Zora Neale Hurston", "978-0-061-96096-9",
              ["mood:motivated", "mood:curious", "fiction", "classic", "African American literature"], total_copies=2),
]

# ── "I want business / finance / economics" ───────────────────────────────────
BUSINESS_BOOKS = [
    make_book("Good to Great", "Jim Collins", "978-0-066-62099-8",
              ["mood:motivated", "non-fiction", "business", "management", "leadership"], total_copies=3),
    make_book("The Innovator's Dilemma", "Clayton M. Christensen", "978-1-422-19602-3",
              ["mood:curious", "mood:motivated", "non-fiction", "business", "innovation", "disruption"], total_copies=2),
    make_book("Thinking in Systems", "Donella Meadows", "978-1-603-58055-7",
              ["mood:curious", "non-fiction", "systems thinking", "environment", "education"], total_copies=3),
    make_book("The Psychology of Money", "Morgan Housel", "978-0-857-19780-0",
              ["mood:curious", "mood:motivated", "non-fiction", "personal finance", "psychology"], total_copies=4),
    make_book("Nudge", "Richard Thaler", "978-0-143-11526-7",
              ["mood:curious", "non-fiction", "behavioural economics", "psychology", "policy"], total_copies=2),
    make_book("Bad Blood", "John Carreyrou", "978-1-524-73165-6",
              ["mood:bored", "mood:curious", "non-fiction", "business", "fraud", "Silicon Valley"], total_copies=3),
    make_book("Shoe Dog", "Phil Knight", "978-1-476-71808-1",
              ["mood:motivated", "biography", "entrepreneurship", "Nike", "memoir"], total_copies=4),
    make_book("Barbarians at the Gate", "Bryan Burrough", "978-0-061-09692-2",
              ["mood:bored", "mood:curious", "non-fiction", "business", "finance", "LBO"], total_copies=2),
]

# ── "I want spiritual / religious / mindful" ──────────────────────────────────
SPIRITUAL_BOOKS = [
    make_book("The Prophet", "Kahlil Gibran", "978-0-394-40428-5",
              ["mood:motivated", "mood:sad", "poetry", "philosophy", "spirituality", "classic"], total_copies=3),
    make_book("Siddhartha", "Hermann Hesse", "978-0-553-20884-7",
              ["mood:motivated", "mood:curious", "fiction", "philosophy", "Buddhism", "classic"], total_copies=3),
    make_book("The Road", "Cormac McCarthy", "978-0-307-38789-2",
              ["mood:sad", "mood:adventurous", "fiction", "post-apocalyptic", "literary fiction"], total_copies=3),
    make_book("A New Earth", "Eckhart Tolle", "978-0-452-28996-3",
              ["mood:stressed", "mood:motivated", "self-help", "spirituality", "mindfulness"], total_copies=3),
    make_book("The Celestine Prophecy", "James Redfield", "978-0-446-67100-7",
              ["mood:adventurous", "mood:curious", "fiction", "spirituality", "adventure"], total_copies=2),
    make_book("The Four Agreements", "Don Miguel Ruiz", "978-1-878-43414-5",
              ["mood:motivated", "mood:stressed", "self-help", "spirituality", "Toltec wisdom"], total_copies=4),
    make_book("Way of the Peaceful Warrior", "Dan Millman", "978-1-932-07301-9",
              ["mood:motivated", "mood:adventurous", "fiction", "spirituality", "self-improvement"], total_copies=3),
]

CHATBOT_SUGGESTED_BOOKS = (
    LONELY_BOOKS + ANXIOUS_BOOKS + JOYFUL_BOOKS + LIFE_CHANGING_BOOKS +
    FANTASY_BOOKS + SCI_FI_BOOKS + MYSTERY_BOOKS + HISTORY_BOOKS +
    PHILOSOPHY_BOOKS + COMEDY_BOOKS + PRODUCTIVITY_BOOKS + ROMANCE_CHAT_BOOKS +
    HORROR_CHAT_BOOKS + SPORTS_BOOKS + TECH_BOOKS + TRAVEL_BOOKS +
    YA_BOOKS + LITERARY_BOOKS + BUSINESS_BOOKS + SPIRITUAL_BOOKS
)

MOOD_BOOKS = (
    SAD_BOOKS + HAPPY_BOOKS + STRESSED_BOOKS + ADVENTUROUS_BOOKS +
    MOTIVATED_BOOKS + CURIOUS_BOOKS + ROMANTIC_MOOD_BOOKS + THRILLING_BOOKS
)

SAMPLE_BOOKS = (
    ML_BOOKS + DATA_SCIENCE_BOOKS + ALGORITHM_BOOKS + PYTHON_BOOKS +
    NLP_BOOKS + DATABASE_BOOKS + NETWORKING_BOOKS + MATHEMATICS_BOOKS +
    CLOUD_BOOKS + FICTION_BOOKS + HORROR_BOOKS + ROMANCE_BOOKS +
    GRAPHIC_NOVEL_BOOKS + BIOGRAPHY_BOOKS + MOOD_BOOKS + CHATBOT_SUGGESTED_BOOKS
)


def reset_availability():
    """
    Reset available_copies = total_copies for EVERY book in the catalogue.
    Run this whenever books appear stuck as 'Unavailable' after testing.
    """
    db = get_db()
    result = db.books.update_many(
        {},
        [{"$set": {"available_copies": "$total_copies"}}],
    )
    print(f"Reset availability: {result.modified_count} books updated.")


def seed(reset=False):
    db = get_db()
    ensure_indexes()

    if reset:
        print("Resetting available_copies for all existing books…")
        reset_availability()

    inserted = 0
    skipped  = 0
    for book in SAMPLE_BOOKS:
        try:
            db.books.insert_one(book)
            inserted += 1
            print(f"  + {book['title']}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "E11000" in str(e):
                # Book already exists — update available_copies back to total_copies
                db.books.update_one(
                    {"isbn": book["isbn"]},
                    {"$set": {
                        "available_copies": book["total_copies"],
                        "subject_tags": book["subject_tags"],
                    }},
                )
                skipped += 1
                print(f"  ~ {book['title']} (exists — availability restored)")
            else:
                print(f"  x {book['title']}: {e}")

    print(f"\nDone. {inserted} inserted, {skipped} refreshed.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed / reset the library database.")
    parser.add_argument("--reset", action="store_true",
                        help="Reset available_copies=total_copies for all books before seeding")
    args = parser.parse_args()
    seed(reset=args.reset)
