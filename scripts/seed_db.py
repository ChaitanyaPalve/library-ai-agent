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

SAMPLE_BOOKS = (
    ML_BOOKS + DATA_SCIENCE_BOOKS + ALGORITHM_BOOKS + PYTHON_BOOKS +
    NLP_BOOKS + DATABASE_BOOKS + NETWORKING_BOOKS + MATHEMATICS_BOOKS +
    CLOUD_BOOKS + FICTION_BOOKS + HORROR_BOOKS + ROMANCE_BOOKS +
    GRAPHIC_NOVEL_BOOKS + BIOGRAPHY_BOOKS
)


def seed():
    db = get_db()
    ensure_indexes()

    inserted = 0
    skipped  = 0
    for book in SAMPLE_BOOKS:
        try:
            db.books.insert_one(book)
            inserted += 1
            print(f"  + {book['title']}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "E11000" in str(e):
                skipped += 1
                print(f"  - {book['title']} (already exists)")
            else:
                print(f"  x {book['title']}: {e}")

    print(f"\nDone. {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    seed()
