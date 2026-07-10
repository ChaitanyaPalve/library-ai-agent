"""
IBM Cloud + MongoDB Atlas connectivity test script.

Checks:
  1. MongoDB Atlas connection
  2. IBM Watson NLU – test analyse call
  3. IBM WatsonX AI  – test generate call

Run:
    python scripts/test_connections.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Force UTF-8 output on Windows so tick/cross chars don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def test_mongodb():
    print("\n[1] Testing MongoDB Atlas connection ...")
    from backend.models.db import get_client
    try:
        client = get_client()
        db = client["library"]
        count = db.books.count_documents({})
        print(f"    OK  Ping successful - Atlas cluster is reachable")
        print(f"    OK  library.books documents: {count}")
        first = db.books.find_one({}, {"title": 1})
        if first:
            print(f"    OK  Sample book: {first.get('title')}")
        else:
            print("    --  No books yet — run: python scripts/seed_db.py")
        client.close()
        return True
    except Exception as e:
        print(f"    FAIL  Atlas connection failed: {e}")
        print("      --> Fix: Atlas dashboard -> Network Access -> Add 0.0.0.0/0")
        return False


def test_watson_nlu():
    print("\n[2] Testing IBM Watson NLU ...")
    try:
        from backend.services.watson_nlu import analyse_query
        result = analyse_query("I need books about machine learning and data science")
        terms = result.get("search_terms", [])
        print(f"    OK  NLU response received")
        print(f"    OK  Extracted search terms: {terms}")
        return True
    except Exception as e:
        print(f"    FAIL  Watson NLU: {e}")
        print("      --> Fix: Check WATSON_NLU_API_KEY and WATSON_NLU_URL in .env")
        return False


def test_watsonx():
    print("\n[3] Testing IBM WatsonX AI (Llama 3.3 70B) ...")
    try:
        from backend.services.watsonx_ai import generate_search_response
        reply = generate_search_response("machine learning books", [
            {"title": "Deep Learning", "author": "Goodfellow", "available_copies": 1}
        ])
        snippet = str(reply)[:120] if reply else "(empty)"
        print(f"    OK  WatsonX response received")
        print(f"    OK  Snippet: {snippet}")
        return True
    except Exception as e:
        print(f"    FAIL  WatsonX AI: {e}")
        print("      --> Fix: Check WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL in .env")
        return False


if __name__ == "__main__":
    results = {
        "mongodb":     test_mongodb(),
        "watson_nlu":  test_watson_nlu(),
        "watsonx_ai":  test_watsonx(),
    }
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    for svc, ok in results.items():
        status = "OK  " if ok else "FAIL"
        print(f"  [{status}] {svc}")
    all_ok = all(results.values())
    print("\nAll services connected." if all_ok else "\nSome services need attention (see above).")
    print()
