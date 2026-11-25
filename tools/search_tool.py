import json
import os
import re
from typing import Dict, Any, List
import requests

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "campus_info.json")


def load_campus_info() -> List[Dict[str, Any]]:
    """Loads campus directory & info."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _live_web_lookup(query: str) -> List[Dict[str, Any]]:
    """
    Lightweight live web lookup (DuckDuckGo Instant Answer + Wikipedia REST summary)
    for general academic and world info when not found in the campus directory.
    Fails silently if offline.
    """
    web_hits: List[Dict[str, Any]] = []
    headers = {"User-Agent": "CampusBuddyAgentForge/1.0"}

    # 1. DuckDuckGo Instant Answer API
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            headers=headers,
            timeout=4,
        )
        if resp.status_code == 200:
            ddg = resp.json()
            abstract = (ddg.get("AbstractText") or "").strip()
            answer = (ddg.get("Answer") or "").strip()
            heading = (ddg.get("Heading") or query.title()).strip()
            if answer:
                web_hits.append({
                    "score": 12,
                    "category": "Web Search",
                    "title": heading,
                    "content": answer,
                })
            if abstract:
                web_hits.append({
                    "score": 11,
                    "category": "Web Search",
                    "title": heading,
                    "content": abstract,
                })
    except Exception:
        pass

    # 2. Wikipedia Search + Summary fallback if DDG had no abstract
    if not web_hits:
        try:
            sr = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 1,
                    "format": "json",
                },
                headers=headers,
                timeout=4,
            )
            if sr.status_code == 200:
                items = sr.json().get("query", {}).get("search", [])
                if items:
                    top_title = items[0]["title"]
                    sum_r = requests.get(
                        f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(top_title)}",
                        headers=headers,
                        timeout=4,
                    )
                    if sum_r.status_code == 200:
                        sdata = sum_r.json()
                        extract = (sdata.get("extract") or "").strip()
                        if extract:
                            web_hits.append({
                                "score": 10,
                                "category": "Web Reference",
                                "title": sdata.get("title", top_title),
                                "content": extract,
                            })
        except Exception:
            pass

    return web_hits


def campus_search(query: str, include_web: bool = True) -> Dict[str, Any]:
    """
    Search for campus facilities, timings, clubs, policies, and general web info.
    """
    cleaned_query = (query or "").strip().lower()
    if not cleaned_query:
        return {
            "success": False,
            "query": query,
            "results": [],
            "message": "Please specify a topic or question to search.",
        }

    info_docs = load_campus_info()
    tokens = [w for w in re.findall(r"\b\w+\b", cleaned_query) if len(w) > 2]

    scored_results: List[Dict[str, Any]] = []
    for doc in info_docs:
        score = 0
        title_lower = doc.get("title", "").lower()
        category_lower = doc.get("category", "").lower()
        content_lower = doc.get("content", "").lower()
        keywords = [k.lower() for k in doc.get("keywords", [])]

        if cleaned_query in title_lower:
            score += 15
        if cleaned_query in content_lower:
            score += 8
        if any(cleaned_query == k for k in keywords):
            score += 20

        for token in tokens:
            if token in category_lower:
                score += 5
            if token in title_lower:
                score += 6
            if any(token in k for k in keywords):
                score += 7
            if token in content_lower:
                score += 2

        if score > 0:
            scored_results.append({
                "score": score,
                "category": doc.get("category"),
                "title": doc.get("title"),
                "content": doc.get("content"),
            })

    scored_results.sort(key=lambda x: x["score"], reverse=True)

    # Supplement with live web lookup when campus directory has no match
    if not scored_results and include_web:
        scored_results = _live_web_lookup(query)

    if not scored_results:
        return {
            "success": True,
            "query": query,
            "count": 0,
            "results": [],
            "message": f"No verified campus or web records found for '{query}'. Could you clarify what details you need?",
        }

    top_results = scored_results[:3]
    formatted = [
        f"📌 **{res['title']}** ({res['category']}):\n{res['content']}"
        for res in top_results
    ]

    return {
        "success": True,
        "query": query,
        "count": len(top_results),
        "results": top_results,
        "summary": "\n\n".join(formatted),
        "message": f"Found {len(top_results)} relevant information item(s).",
    }
