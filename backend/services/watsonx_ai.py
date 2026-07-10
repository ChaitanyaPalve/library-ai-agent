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
