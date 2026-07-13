"""
IBM WatsonX AI (ibm-watsonx-ai SDK) integration.

Used to:
  1. Generate a natural-language answer/summary when books are found.
  2. Suggest related topics when no exact match exists.
  3. Produce waitlist / reservation confirmation messages.
"""

import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# ---------------------------------------------------------------------------
# Lazy singleton
# ---------------------------------------------------------------------------

_model: ModelInference | None = None


def _get_model() -> ModelInference:
    global _model
    if _model is not None:
        return _model

    credentials = Credentials(
        url=os.environ["WATSONX_URL"],
        api_key=os.environ["WATSONX_API_KEY"],
    )
    project_id = os.environ["WATSONX_PROJECT_ID"]

    params = {
        GenParams.MAX_NEW_TOKENS: 512,
        GenParams.MIN_NEW_TOKENS: 20,
        GenParams.TEMPERATURE: 0.7,
        GenParams.REPETITION_PENALTY: 1.1,
    }

    _model = ModelInference(
        model_id=os.getenv("WATSONX_MODEL_ID", "meta-llama/llama-3-3-70b-instruct"),
        credentials=credentials,
        project_id=project_id,
        params=params,
    )
    return _model


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SEARCH_SUMMARY_PROMPT = """You are a helpful university library assistant.
A student asked: "{query}"

The library found the following relevant books:
{book_list}

Write a friendly, concise response (3–5 sentences) that:
- Confirms you found matching books
- Highlights the most relevant title and why it fits
- Mentions availability where relevant
- Offers to help with reservations or suggest related topics

Response:"""

_NO_RESULTS_PROMPT = """You are a helpful university library assistant.
A student asked: "{query}"

Unfortunately, no matching books were found in the library catalogue for this query.

Write a friendly, concise response (3–5 sentences) that:
- Acknowledges the lack of results
- Suggests 2–3 related academic topics or alternative search terms the student could try
- Offers to place an inter-library loan request

Response:"""

_RESERVATION_PROMPT = """You are a helpful university library assistant.
Compose a short confirmation message (2–3 sentences) for the following reservation:
- Student: {student_id}
- Book: "{book_title}" by {book_author}
- Status: {status}

If the status is "waitlisted", include an estimated wait note.

Message:"""

_RECOMMENDATION_PROMPT = """You are a personalised university library assistant.
A student has read or reserved the following books:
{history_list}

Based on their reading history, recommend 3–5 books they should read next.
For each recommendation give: title, author, and a one-sentence reason why it fits.
Format each as:
  • "<title>" by <author> — <reason>

Recommendations:"""

_CHATBOT_PROMPT = """You are a friendly university library chatbot.

User message: "{message}"
Mode: {mode}

Rules:
- If mode is "mood" or "interest": suggest 3–5 books that match the user's mood, emotion, or topic interest.
  Format each as:  • "<Title>" by <Author> — <one-line reason>
  Prioritise well-known titles the library is likely to stock, such as:
  The Midnight Library, A Man Called Ove, The Perks of Being a Wallflower, The Body Keeps the Score,
  Reasons to Stay Alive, Atomic Habits, The Subtle Art of Not Giving a F*ck, The Power of Now,
  Man's Search for Meaning, Sapiens, Thinking Fast and Slow, The Alchemist, Meditations,
  The Lord of the Rings, Harry Potter and the Philosopher's Stone, A Game of Thrones,
  The Martian, Project Hail Mary, The Three-Body Problem, Ready Player One, Foundation,
  Gone Girl, The Silent Patient, The Girl with the Dragon Tattoo, The Da Vinci Code,
  The Hunger Games, Wonder, The Catcher in the Rye, The Giver,
  Pride and Prejudice, Normal People, The Notebook, It Ends with Us, Beach Read,
  Educated, Born a Crime, Sapiens, Homo Deus, Guns Germs and Steel,
  Shoe Dog, The Power of Habit, Deep Work, Atomic Habits, Rich Dad Poor Dad,
  The Midnight Library, Norwegian Wood, Eleanor & Park, A Little Life,
  The Book Thief, Tuesdays with Morrie, Milk and Honey, The Prophet,
  Good Omens, Eleanor Oliphant is Completely Fine, The 100-Year-Old Man,
  Sophie's World, Siddhartha, The Stranger, Crime and Punishment,
  The Obstacle Is the Way, The Four Agreements, Eat Pray Love.
- If mode is "suggest": the user wants to suggest a book for the library to acquire.
  Acknowledge the suggestion warmly, confirm the title/author if mentioned, and explain the library will review it.
- If mode is "query": the user has a general library question (hours, policies, fines, procedures, etc.).
  Answer helpfully and concisely in 2–4 sentences.
- For any other mode: answer naturally as a library assistant.

Keep the tone warm and concise. Do not include any preamble like "Sure!" or "Of course!".

Response:"""

_SUGGEST_BOOK_PROMPT = """You are a university library acquisition assistant.
A student has suggested the following book for the library to purchase:
- Title: {title}
- Author: {author}
- Reason: {reason}

Write a warm 2-sentence acknowledgement confirming the suggestion has been recorded
and that the library team will review it for acquisition.

Response:"""

_BOOK_DESCRIPTION_PROMPT = """Give a 1-sentence description of the book "{title}" by {author}.
State what it is about and who it is for. No preamble, no quotes around the sentence.

Description:"""

_SUGGEST_VERIFY_PROMPT = """Is "{title}" by {author} a real published book?
Reply with only YES or NO.

Answer:"""

_AI_PICKS_PROMPT = """You are a passionate university librarian recommending books to students.
Here are {count} books currently available in the library:
{book_list}

For each book write one punchy sentence (max 18 words) explaining WHY a student should read it right now.
Format — one line per book, exactly as:
  <isbn>|<sentence>

Do not add any preamble. Reply with only the lines.

Picks:"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_search_response(query: str, books: list[dict]) -> str:
    """Generate a natural-language reply summarising the search results."""
    model = _get_model()

    if not books:
        prompt = _NO_RESULTS_PROMPT.format(query=query)
    else:
        book_lines = "\n".join(
            f'- "{b["title"]}" by {b["author"]} '
            f'({"Available" if b.get("available_copies", 0) > 0 else "Unavailable"})'
            for b in books[:5]
        )
        prompt = _SEARCH_SUMMARY_PROMPT.format(query=query, book_list=book_lines)

    result = model.generate_text(prompt=prompt)
    return result.strip() if isinstance(result, str) else result


def recommend_books(reading_history: list[dict]) -> str:
    """
    Given a list of book dicts (each with at least 'title' and 'author'),
    return an AI-generated reading recommendation paragraph.
    """
    model = _get_model()
    if not reading_history:
        return "No reading history found — search for and reserve a few books first!"
    history_lines = "\n".join(
        f'- "{b.get("title", "Unknown")}" by {b.get("author", "Unknown")}'
        for b in reading_history[:10]
    )
    prompt = _RECOMMENDATION_PROMPT.format(history_list=history_lines)
    result = model.generate_text(prompt=prompt)
    return result.strip() if isinstance(result, str) else result


def generate_reservation_message(student_id: str, book: dict, status: str) -> str:
    """Generate a personalised reservation or waitlist confirmation."""
    model = _get_model()
    prompt = _RESERVATION_PROMPT.format(
        student_id=student_id,
        book_title=book.get("title", "Unknown"),
        book_author=book.get("author", "Unknown"),
        status=status,
    )
    result = model.generate_text(prompt=prompt)
    return result.strip() if isinstance(result, str) else result


def generate_chatbot_response(message: str, mode: str = "general") -> str:
    """
    Generate a chatbot reply.
    mode: "mood" | "interest" | "suggest" | "query" | "general"
    """
    model = _get_model()
    prompt = _CHATBOT_PROMPT.format(message=message, mode=mode)
    result = model.generate_text(prompt=prompt)
    return result.strip() if isinstance(result, str) else result


def generate_suggest_book_reply(title: str, author: str, reason: str) -> str:
    """Generate an acknowledgement for a student book-acquisition suggestion."""
    model = _get_model()
    prompt = _SUGGEST_BOOK_PROMPT.format(title=title, author=author, reason=reason)
    result = model.generate_text(prompt=prompt)
    return result.strip() if isinstance(result, str) else result


def generate_book_description(title: str, author: str) -> str:
    """Return a one-sentence description for a book (token-efficient)."""
    model = _get_model()
    prompt = _BOOK_DESCRIPTION_PROMPT.format(title=title, author=author)
    # Use a small token budget — one sentence is enough
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GP
    result = model.generate_text(
        prompt=prompt,
        params={GP.MAX_NEW_TOKENS: 60, GP.MIN_NEW_TOKENS: 10, GP.TEMPERATURE: 0.3},
    )
    return (result.strip() if isinstance(result, str) else result) or ""


def verify_book_is_real(title: str, author: str) -> bool:
    """Ask the model whether the book title/author combination is a real book."""
    model = _get_model()
    prompt = _SUGGEST_VERIFY_PROMPT.format(title=title, author=author)
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GP
    result = model.generate_text(
        prompt=prompt,
        params={GP.MAX_NEW_TOKENS: 5, GP.MIN_NEW_TOKENS: 1, GP.TEMPERATURE: 0.0},
    )
    answer = (result.strip() if isinstance(result, str) else result).upper()
    return answer.startswith("YES")


def generate_ai_picks(books: list[dict]) -> list[dict]:
    """
    Given a list of book dicts (each with isbn, title, author),
    return the same list with an added 'ai_blurb' key containing a
    one-sentence WatsonX-generated reason to read it.
    Falls back to the book's own description if AI call fails.
    """
    if not books:
        return []
    model = _get_model()
    book_lines = "\n".join(
        f'{b.get("isbn", b.get("_id", "?"))}|"{b["title"]}" by {b["author"]}'
        for b in books
    )
    prompt = _AI_PICKS_PROMPT.format(count=len(books), book_list=book_lines)
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GP
    try:
        raw = model.generate_text(
            prompt=prompt,
            params={GP.MAX_NEW_TOKENS: 300, GP.MIN_NEW_TOKENS: 20, GP.TEMPERATURE: 0.75},
        )
        raw = raw.strip() if isinstance(raw, str) else raw
        # Parse isbn|sentence lines
        blurb_map: dict[str, str] = {}
        for line in raw.splitlines():
            line = line.strip().lstrip("•- ")
            if "|" in line:
                isbn_part, _, sentence = line.partition("|")
                blurb_map[isbn_part.strip()] = sentence.strip()
        for book in books:
            key = book.get("isbn", book.get("_id", ""))
            book["ai_blurb"] = blurb_map.get(key, book.get("description", ""))
    except Exception:
        for book in books:
            book["ai_blurb"] = book.get("description", "")
    return books
