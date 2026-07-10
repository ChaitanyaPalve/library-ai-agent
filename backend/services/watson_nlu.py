"""
IBM Watson Natural Language Understanding service wrapper.

Analyses a student's free-text query and extracts:
  - keywords  (what topics / subjects they need)
  - entities  (book titles, authors, organisations, concepts)
  - categories (broad subject classification)

Also analyses the sentiment of book reviews.

The results are used downstream to build a MongoDB query that retrieves
the most relevant books from the library collection.
"""

import os
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import (
    Features,
    KeywordsOptions,
    EntitiesOptions,
    CategoriesOptions,
    ConceptsOptions,
    SentimentOptions,
)
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

_nlu_client: NaturalLanguageUnderstandingV1 | None = None


def _get_nlu() -> NaturalLanguageUnderstandingV1:
    global _nlu_client
    if _nlu_client is not None:
        return _nlu_client

    api_key = os.environ["WATSON_NLU_API_KEY"]
    service_url = os.environ["WATSON_NLU_URL"]

    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version="2022-04-07",
        authenticator=authenticator,
    )
    nlu.set_service_url(service_url)
    _nlu_client = nlu
    return _nlu_client


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_query(text: str) -> dict:
    """
    Send *text* to Watson NLU and return a structured dict:

    {
        "keywords":   [{"text": "...", "relevance": 0.95}, ...],
        "entities":   [{"text": "...", "type": "...", "relevance": 0.8}, ...],
        "categories": [{"label": "/science/...", "score": 0.7}, ...],
        "concepts":   [{"text": "...", "relevance": 0.9}, ...],
        "search_terms": ["machine learning", "neural network", ...]  # flat list
    }
    """
    nlu = _get_nlu()
    response = nlu.analyze(
        text=text,
        features=Features(
            keywords=KeywordsOptions(limit=10),
            entities=EntitiesOptions(limit=10),
            categories=CategoriesOptions(limit=5),
            concepts=ConceptsOptions(limit=10),
        ),
    ).get_result()

    keywords  = response.get("keywords", [])
    entities  = response.get("entities", [])
    categories = response.get("categories", [])
    concepts   = response.get("concepts", [])

    # Build a flat list of the most relevant terms to drive the DB search
    search_terms: list[str] = []
    for kw in keywords:
        if kw.get("relevance", 0) >= 0.4:
            search_terms.append(kw["text"].lower())
    for ent in entities:
        if ent.get("relevance", 0) >= 0.4 and ent["text"].lower() not in search_terms:
            search_terms.append(ent["text"].lower())
    for concept in concepts:
        if concept.get("relevance", 0) >= 0.5 and concept["text"].lower() not in search_terms:
            search_terms.append(concept["text"].lower())

    return {
        "keywords": keywords,
        "entities": entities,
        "categories": categories,
        "concepts": concepts,
        "search_terms": search_terms,
    }


def analyse_sentiment(text: str) -> dict:
    """
    Analyse the sentiment of a book review text.

    Returns:
    {
        "label":  "positive" | "negative" | "neutral",
        "score":  float (-1.0 … +1.0)
    }
    """
    nlu = _get_nlu()
    response = nlu.analyze(
        text=text,
        features=Features(sentiment=SentimentOptions()),
    ).get_result()

    doc_sentiment = response.get("sentiment", {}).get("document", {})
    return {
        "label": doc_sentiment.get("label", "neutral"),
        "score": doc_sentiment.get("score", 0.0),
    }
