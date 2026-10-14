"""Smoke tests: every section and calculator renders, with news fetching stubbed out."""
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from content import TOPICS

STORY = {"title": "Intel ships new Xeon", "summary": "More cores for AI inference.", "source": "Test", "link": "https://example.com", "date": None}


def run(section=None, stories=(STORY,)):
    at = AppTest.from_file("../app.py", default_timeout=30)
    if section is not None:
        at.session_state["section"] = section
    with patch("news.fetch_headlines", return_value=list(stories)):
        at.run()
    assert not at.exception, at.exception
    return at


def test_every_section_renders():
    at = run()
    for section in at.sidebar.radio[0].options:
        run(section)


def test_next_topic_button_advances():
    first = f"{TOPICS[0]['icon']} {TOPICS[0]['title']}"
    at = run(first)
    [b for b in at.button if b.label == "Next topic →"][0].click().run()
    assert at.session_state["section"] == f"{TOPICS[1]['icon']} {TOPICS[1]['title']}"


def test_every_calculator_renders():
    at = run("🧮 Calculators")
    options = at.button_group[0].options
    assert len(options) == 12
    for option in options:
        at.button_group[0].set_value(option).run()
        assert not at.exception, (option, at.exception)


def test_news_failure_shows_friendly_message():
    st.cache_data.clear()
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.session_state["section"] = "🔵 Intel news"
    with patch("news.fetch_headlines", side_effect=OSError("offline")):
        at.run()
    assert not at.exception, at.exception
    assert any("could not be loaded" in w.value for w in at.warning)


def test_home_shows_headline_and_reminders():
    st.cache_data.clear()
    at = run()
    assert any("Intel ships new Xeon" in m.value for m in at.markdown)
    assert any(m.label == "Next reminder" for m in at.metric)


def test_every_page_ends_with_a_mistakes_table():
    for section in run().sidebar.radio[0].options:
        at = run(section)
        assert any("Common mistakes" in h.value for h in at.subheader), section


def test_emergency_card_offers_download_once_named():
    at = run("🆘 Family emergency card")
    assert len(at.get("download_button")) == 0
    at.text_input[0].input("Rao family").run()
    assert not at.exception, at.exception
    assert len(at.get("download_button")) == 1


def test_life_review_score_updates():
    at = run("✅ Annual life review")
    at.checkbox[0].check().run()
    assert at.metric[0].value == f"{1 / len(TOPICS):.0%}"
