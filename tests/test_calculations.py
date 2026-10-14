from datetime import date

import pytest

from calculations import (
    FED_BRACKETS_MFJ,
    account_gaps,
    build_ics,
    compound_series,
    concentration,
    espp_purchase,
    future_cost,
    life_insurance_need,
    mortgage_payment,
    progressive_tax,
    reserve_months,
    rsu_withholding_gap,
    take_home,
    upcoming,
)
from content import KEY_DATES, SOURCES, TOPICS


def test_progressive_tax_matches_2026_brackets():
    assert progressive_tax(24_800, FED_BRACKETS_MFJ) == pytest.approx(2_480)
    # 10% of 24,800 + 12% of 76,000 + 22% of 10,000
    assert progressive_tax(110_800, FED_BRACKETS_MFJ) == pytest.approx(2_480 + 9_120 + 2_200)
    assert progressive_tax(0, FED_BRACKETS_MFJ) == 0


def test_take_home_adds_up():
    r = take_home(250_000, pretax_401k=24_500, hsa=6_000, dependent_care_fsa=7_500, premiums=3_600)
    pretax = 24_500 + 6_000 + 7_500 + 3_600
    assert r["Take-home pay"] + r["Total taxes"] + pretax == pytest.approx(250_000)
    assert r["Federal marginal rate"] == 0.22
    assert r["California marginal rate"] == 0.093


def test_california_taxes_hsa_but_federal_does_not():
    without = take_home(200_000)
    with_hsa = take_home(200_000, hsa=8_000)
    assert with_hsa["Federal income tax"] < without["Federal income tax"]
    assert with_hsa["California income tax"] == pytest.approx(without["California income tax"])


def test_social_security_stops_at_wage_base():
    assert take_home(500_000)["Social Security"] == pytest.approx(0.062 * 184_500)


def test_rsu_gap_positive_for_high_brackets():
    withheld, owed, gap = rsu_withholding_gap(100_000, 0.32, 0.093)
    assert withheld == pytest.approx(32_230)
    assert gap == pytest.approx(41_300 - 32_230)
    assert rsu_withholding_gap(100_000, 0.12, 0.06)[2] < 0


def test_espp_lookback_uses_lower_price():
    price, shares, value, gain, pct = espp_purchase(8_500, 20, 30, 15, lookback=True)
    assert price == pytest.approx(17)
    assert shares == pytest.approx(500)
    assert gain == pytest.approx(15_000 - 8_500)
    no_lookback = espp_purchase(8_500, 20, 30, 15, lookback=False)
    assert no_lookback[4] == pytest.approx(100 / 85 * 100 - 100)


def test_mortgage_payment():
    assert mortgage_payment(120_000, 0, 10) == pytest.approx(1_000)
    assert mortgage_payment(500_000, 6, 30) == pytest.approx(2_997.75, abs=0.01)


def test_compound_and_future_cost():
    assert compound_series(1_000, 0, 10, 2)[-1] == pytest.approx(1_210)
    assert future_cost(100, 10, 1) == pytest.approx(110)


def test_small_helpers():
    assert reserve_months(9_000, 3_000) == 3
    assert reserve_months(1, 0) is None
    assert concentration(25, 100) == 25
    assert concentration(1, 0) is None
    assert life_insurance_need(100_000, 10, 0, 0, 0, 0, 500_000, 600_000) == 0
    assert account_gaps({"HSA family": 8_000})[0][3] == 750


def test_upcoming_wraps_into_next_year():
    items = upcoming([(1, 5, "x", "New year", "t")], date(2026, 12, 20), days=30)
    assert items[0][0] == date(2027, 1, 5)
    assert upcoming([(6, 1, "x", "June", "t")], date(2026, 12, 20), days=30) == []


def test_ics_escapes_and_repeats():
    ics = build_ics([(date(2026, 4, 15), "Tax day, file; pay")])
    assert r"SUMMARY:Tax day\, file\; pay" in ics
    assert "RRULE:FREQ=YEARLY" in ics


def test_content_is_consistent():
    titles = {t["title"] for t in TOPICS}
    for t in TOPICS:
        assert len(t["numbers"]) == 4, t["title"]
        assert all(link in SOURCES for link in t["links"]), t["title"]
        assert t["intel"] and t["items"]
    for _, _, _, _, topic in KEY_DATES:
        assert topic in titles, topic


def test_plan_cost_caps_at_out_of_pocket_max():
    from calculations import plan_cost

    assert plan_cost(1_000, 3_400, 20, 8_000, 10_000, 1_000) == pytest.approx(1_000 + 3_400 + 1_320 - 1_000)
    assert plan_cost(1_000, 3_400, 20, 8_000, 1_000_000) == pytest.approx(9_000)
    assert plan_cost(1_000, 3_400, 20, 8_000, 0) == 1_000


def test_probate_fee_matches_statutory_schedule():
    from calculations import probate_fee

    assert probate_fee(100_000) == pytest.approx(4_000)
    assert probate_fee(1_000_000) == pytest.approx(23_000)
    assert probate_fee(2_000_000) == pytest.approx(33_000)


OFFICIAL = (".gov", "intel.com", "intc.com", "openvino.ai", "uspreventiveservicestaskforce.org", "scholarshare529.com",
            "earthquakeauthority.com", "annualcreditreport.com", "coveredca.com", "readyforwildfire.org")


def test_every_section_links_only_to_intel_or_government_sources():
    from urllib.parse import urlparse

    from content import NEWS

    for name in [l for t in TOPICS for l in t["links"]] + [l for p in NEWS.values() for l in p["links"]]:
        host = urlparse(SOURCES[name]).hostname
        assert host.endswith(OFFICIAL), (name, host)


def test_every_topic_has_formulas_and_mistakes():
    from insights import INSIGHTS

    assert set(INSIGHTS) == {t["title"] for t in TOPICS}
    for title, info in INSIGHTS.items():
        assert len(info["formulas"]) >= 1 and len(info["mistakes"]) >= 3, title
        for chart in (info.get("chart"), info.get("chart2")):
            if chart and chart["kind"] == "bar":
                values = chart["data"][chart["y"]]
                assert len(values) == len(chart["data"][chart["x"]]), title
