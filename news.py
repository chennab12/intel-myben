"""Fetch RSS headlines and make short plain-text summaries. Standard library only, no API key."""
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

TAG = re.compile(r"<[^>]+>")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def clean(text):
    """Strip HTML tags and entities and collapse whitespace."""
    return " ".join(html.unescape(TAG.sub(" ", text or "")).split())


def summarize(text, title="", max_sentences=2, max_chars=280):
    """First sentences of the description, or '' when it only repeats the headline."""
    text = clean(text)
    if not text or (title and text.lower().startswith(clean(title).lower())):
        return ""
    summary = " ".join(SENTENCE_END.split(text)[:max_sentences])
    if len(summary) > max_chars:
        summary = summary[:max_chars].rsplit(" ", 1)[0] + "…"
    return summary


def parse_feed(xml_bytes, limit=6):
    """List of {title, summary, source, link, date} from RSS XML."""
    items = []
    for item in ET.fromstring(xml_bytes).iter("item"):
        title = clean(item.findtext("title"))
        source = clean(item.findtext("source"))
        # Google News appends " - Source" to every title.
        if source and title.endswith(" - " + source):
            title = title[: -len(source) - 3]
        try:
            date = parsedate_to_datetime(item.findtext("pubDate"))
        except (TypeError, ValueError):
            date = None
        items.append({
            "title": title,
            "summary": summarize(item.findtext("description"), title),
            "source": source,
            "link": (item.findtext("link") or "").strip(),
            "date": date,
        })
        if len(items) >= limit:
            break
    return items


def fetch_headlines(url, limit=6, timeout=10):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (intel-myben app)"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_feed(response.read(), limit)
