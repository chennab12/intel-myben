"""Intel MyBen: one place for an Intel AI/ML TPM's family in California to manage work, health, money and home."""
import csv
import io
from html import escape
from datetime import date, datetime
from zoneinfo import ZoneInfo

import streamlit as st

import news
from calculations import (
    CA_BRACKETS_MFJ,
    CA_YEAR,
    FED_BRACKETS_MFJ,
    FED_YEAR,
    LIMITS_2026,
    account_gaps,
    build_ics,
    compound_series,
    concentration,
    espp_purchase,
    future_cost,
    life_insurance_need,
    mortgage_payment,
    plan_cost,
    real_value,
    reserve_months,
    rsu_withholding_gap,
    take_home,
    upcoming,
)
from content import BENEFITS_SHEET, GROUPS, KEY_DATES, NEWS, REVIEWED, SOURCES, TOPICS
from insights import INSIGHTS, NEWS_MISTAKES, PAGE_MISTAKES
from visuals import show

st.set_page_config(page_title="Intel MyBen", page_icon="🔷", layout="wide")

HOME = "🏠 My dashboard"
CHEATSHEET = "📌 Master cheatsheet"
NEWS_NAMES = [f"{v['icon']} {k}" for k, v in NEWS.items()]
TOPIC_NAMES = [f"{t['icon']} {t['title']}" for t in TOPICS]
CARD = "🆘 Family emergency card"
REVIEW = "✅ Annual life review"
SHEET = "🗂️ My benefits sheet"
PLANNER = "📅 Year planner"
CALCULATORS = "🧮 Calculators"
ABOUT = "📚 Sources & method"
SECTIONS = [HOME, CHEATSHEET] + NEWS_NAMES + TOPIC_NAMES + [CARD, REVIEW, SHEET, PLANNER, CALCULATORS, ABOUT]
CALCS = [
    "💵 Take-home pay & taxes",
    "🏥 Compare medical plans",
    "📊 Net worth",
    "📈 RSU tax gap",
    "🛒 ESPP purchase",
    "🏦 Max your accounts",
    "🛟 Emergency fund",
    "🛡️ Life insurance need",
    "🎓 College 529",
    "🌅 Retirement",
    "🏠 Mortgage",
    "🎯 Intel stock concentration",
]
PACIFIC = ZoneInfo("America/Los_Angeles")

st.session_state.setdefault("section", HOME)


def go_to(section):
    st.session_state.section = section


def today():
    return datetime.now(PACIFIC).date()


def money(x):
    return f"${x:,.0f}"


def md(text):
    """Escape dollar signs so Streamlit markdown does not render them as math."""
    return text.replace("$", "\\$")


def links_row(names):
    st.markdown("🔗 **Official sources:** " + " · ".join(f"[{n} ↗]({SOURCES[n]})" for n in names))


def md_table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    st.markdown(md("\n".join(lines)))


def mistakes_table(rows):
    st.subheader("⚠️ Common mistakes and how to avoid them")
    md_table(["Mistake ⛔", "Why it hurts", "Recommended steps ✅"], [(f"**{a}**", b, c) for a, b, c in rows])


def draw_chart(spec):
    st.markdown(md(f"**📊 {spec['title']}**"))
    if spec["kind"] == "line":
        st.line_chart(spec["data"], x=spec["x"], y=spec["y"], y_label=spec["y_label"])
    else:
        st.bar_chart(spec["data"], x=spec["x"], y=spec["y"], horizontal=True, sort=False)
    st.caption(md(spec["note"]))


def plan_compare_chart(a, b, max_spend=30_000):
    """Yearly cost of two medical plans across spending levels; a and b are plan_cost keyword dicts."""
    levels = list(range(0, max_spend + 1, 2_500))
    st.line_chart(
        {"Medical spending ($)": levels, "Plan A": [plan_cost(spending=x, **a) for x in levels], "Plan B": [plan_cost(spending=x, **b) for x in levels]},
        x="Medical spending ($)",
        y=["Plan A", "Plan B"],
        y_label="Your yearly cost ($)",
    )


@st.cache_data(ttl=1800, show_spinner="Loading headlines…")
def headlines(url, limit):
    return news.fetch_headlines(url, limit)


with st.sidebar:
    st.title("🔷 MyBen")
    # Only the selected section runs on each rerun, so calculators stay fast.
    st.radio("Section", SECTIONS, key="section")
    st.divider()
    st.markdown("**📅 Coming up**")
    for when, icon, title, _ in upcoming(KEY_DATES, today(), days=45)[:3]:
        st.caption(f"{icon} {when:%b %d} · {title}")

st.title("🔷 Intel MyBen: life and benefits hub")
st.caption(
    f"For an Intel AI/ML TPM in California with a spouse and a 10-year-old · "
    f"Federal figures: {FED_YEAR} · California brackets: {CA_YEAR} · Reviewed {REVIEWED}"
)
st.info(
    "General information, not tax, legal, medical or investment advice. Intel plan details vary by year and grade; "
    "check each one on Intel's internal benefits site and record it in **My benefits sheet**."
)
section = st.session_state.section


def show_stories(url, limit=6):
    try:
        stories = headlines(url, limit)
    except Exception:
        stories = None
    if not stories:
        st.warning("Headlines could not be loaded right now. Try again in a few minutes.")
        return
    for story in stories:
        with st.container(border=True):
            st.markdown(md(f"**{story['title']}**"))
            if story["summary"]:
                st.write(md(story["summary"]))
            when = story["date"].astimezone(PACIFIC).strftime("%b %d, %I:%M %p") if story["date"] else ""
            meta = " · ".join(x for x in [story["source"], when] if x)
            if story["link"]:
                meta += f" · [Read full story ↗]({story['link']})"
            st.caption(meta)


def render_home():
    st.header("🏠 My dashboard")
    a, b, c, d = st.columns(4)
    a.metric("401(k) limit 2026", money(LIMITS_2026["401(k) employee deferral"]), help="Plus $8,000 catch-up at age 50+.")
    b.metric("HSA family 2026", money(LIMITS_2026["HSA family"]), help="California taxes HSA contributions.")
    c.metric("Dependent care FSA", money(LIMITS_2026["Dependent care FSA (per household)"]), help="New 2026 limit; child must be under 13.")
    soon = upcoming(KEY_DATES, today(), days=366)
    when, icon, title, _ = soon[0]
    d.metric("Next reminder", f"{(when - today()).days} days", help=f"{icon} {title}")

    st.subheader("📅 Next 45 days")
    rows = upcoming(KEY_DATES, today(), days=45) or soon[:2]
    for when, icon, title, topic_title in rows:
        left, right = st.columns([5, 2], vertical_alignment="center")
        left.markdown(md(f"{icon} **{when:%a %b %d}** · {title}"))
        target = next(n for n, t in zip(TOPIC_NAMES, TOPICS) if t["title"] == topic_title)
        right.button("Open topic →", key=f"due_{when}_{title}", on_click=go_to, args=(target,), width="stretch")

    st.subheader("🧭 Life topics")
    for group in GROUPS:
        st.markdown(f"#### {group}")
        members = [(n, t) for n, t in zip(TOPIC_NAMES, TOPICS) if t["group"] == group]
        cols = st.columns(3)
        for i, (name, t) in enumerate(members):
            with cols[i % 3].container(border=True):
                st.markdown(f"**{name}**")
                label, value, _ = t["numbers"][0]
                st.caption(md(f"{label}: **{value}**"))
                st.write(md(t["takeaway"]))
                st.button("Open →", key="open_" + name, on_click=go_to, args=(name,), width="stretch")

    st.subheader("📰 Latest headlines")
    cols = st.columns(len(NEWS))
    for col, (name, page) in zip(cols, NEWS.items()):
        with col:
            st.markdown(f"**{page['icon']} {name}**")
            show_stories(next(iter(page["feeds"].values())), limit=3)
            st.button(f"More {name} →", key="more_" + name, on_click=go_to, args=(f"{page['icon']} {name}",))

    st.subheader("🛠️ Tools")
    a, b, c = st.columns(3)
    a.button("🗂️ Fill in my benefits sheet", on_click=go_to, args=(SHEET,), width="stretch")
    b.button("📅 See the year planner", on_click=go_to, args=(PLANNER,), width="stretch")
    c.button("🧮 Open the calculators", on_click=go_to, args=(CALCULATORS,), width="stretch", type="primary")
    a, b, c = st.columns(3)
    a.button("🆘 Family emergency card", on_click=go_to, args=(CARD,), width="stretch")
    b.button(f"✅ Annual life review ({review_score():.0%} done)", on_click=go_to, args=(REVIEW,), width="stretch")
    c.button("🌅 Retirement plan", on_click=go_to, args=(TOPIC_NAMES[[t["title"] for t in TOPICS].index("Retirement: 401(k), IRA & Social Security")],), width="stretch")

    months = [f"{m:%b}" for m in (date(2026, i, 1) for i in range(1, 13))]
    counts = [sum(1 for d in KEY_DATES if d[0] == i) for i in range(1, 13)]
    draw_chart({"kind": "bar", "title": "Yearly reminders by month", "data": {"Month": months, "Reminders": counts}, "x": "Month", "y": "Reminders", "note": "Busiest months are tax season and open enrollment; see the Year planner."})
    links_row(["Intel benefits overview (public)", "IRS 2026 inflation adjustments", "California FTB tax rates", "Ready.gov (FEMA)"])
    mistakes_table(PAGE_MISTAKES["dashboard"])


def render_cheatsheet():
    st.header("📌 Master cheatsheet")
    st.caption("One row per life topic. Scroll sideways for more columns.")
    st.dataframe(
        [
            {
                "Area": t["group"],
                "Topic": f"{t['icon']} {t['title']}",
                "Key number 🔢": f"{t['numbers'][0][0]}: {t['numbers'][0][1]}",
                "Big idea": t["takeaway"],
                "Do ✅": t["do"],
                "Don't ⛔": t["dont"],
                "Official link": SOURCES[t["links"][0]],
            }
            for t in TOPICS
        ],
        hide_index=True,
        width="stretch",
        height=560,
        column_config={"Official link": st.column_config.LinkColumn("Official link", display_text="Open ↗")},
    )
    left, right = st.columns(2)
    with left:
        st.subheader(f"💰 {FED_YEAR} account limits")
        st.dataframe([{"Account": k, "Limit": money(v)} for k, v in LIMITS_2026.items()], hide_index=True, width="stretch")
    with right:
        st.subheader("🧾 Tax brackets (married filing jointly)")
        fed = [f"{int(r * 100)}%" for _, r in FED_BRACKETS_MFJ]
        fed_top = [money(u) if u != float("inf") else "and above" for u, _ in FED_BRACKETS_MFJ]
        st.dataframe(
            [{f"Federal {FED_YEAR} rate": r, "Taxable income up to": u} for r, u in zip(fed, fed_top)],
            hide_index=True,
            width="stretch",
        )
        st.dataframe(
            [
                {f"California {CA_YEAR} rate": f"{r * 100:g}%", "Taxable income up to": money(u) if u != float("inf") else "and above"}
                for u, r in CA_BRACKETS_MFJ
            ],
            hide_index=True,
            width="stretch",
        )
        st.caption("California adds 1% on taxable income over \\$1M and 1.3% SDI on all wages (2026).")
    st.subheader("🔢 Master formulas")
    md_table(["Topic", "Metric", "Formula", "Example"], [(t["title"], f"**{a}**", b, c) for t in TOPICS for a, b, c in INSIGHTS[t["title"]]["formulas"][:2]])
    links_row(["IRS 2026 inflation adjustments", "IRS 401(k) and IRA limits", "California FTB tax rates", "CA EDD rates and withholding"])
    mistakes_table(PAGE_MISTAKES["cheatsheet"])


def render_news(index):
    name = list(NEWS)[index]
    page = NEWS[name]
    st.header(f"{page['icon']} {name}")
    st.caption(md(page["takeaway"]) + " Headlines refresh about every 30 minutes from Google News.")
    feed = st.segmented_control("Feed", list(page["feeds"]), default=list(page["feeds"])[0], key="feed_" + name)
    if feed:
        show_stories(page["feeds"][feed], limit=8)
    st.success(md("💡 " + page["tip"]))
    st.metric("Feeds on this page", len(page["feeds"]), help="Each feed shows up to 8 recent stories.")
    links_row(page["links"])
    mistakes_table(NEWS_MISTAKES)


def render_topic(index):
    t = TOPICS[index]
    st.header(f"{t['icon']} {t['title']}")
    st.caption(f"{t['group']} · Topic {index + 1} of {len(TOPICS)}")
    st.markdown(md(f"#### {t['takeaway']}"))
    cols = st.columns(len(t["numbers"]))
    for col, (label, value, note) in zip(cols, t["numbers"]):
        with col.container(border=True, height="stretch"):
            st.caption(md(label))
            st.markdown(md(f"#### {value}"))
            st.caption(md(note))

    info = INSIGHTS[t["title"]]
    st.subheader("🔢 Key metrics & formulas")
    md_table(["Metric", "Formula", "Example"], [(f"**{a}**", b, c) for a, b, c in info["formulas"]])
    if info["chart"]:
        draw_chart(info["chart"])
    if info.get("chart2"):
        draw_chart(info["chart2"])
    if t["title"] == "Medical plan & HSA":
        st.markdown("**📊 Worked example: high-deductible plan vs PPO (yearly cost by medical spending)**")
        plan_compare_chart(
            dict(premiums=1_800, deductible=3_400, coinsurance_percent=20, oop_max=8_000, employer_hsa=1_000),
            dict(premiums=4_800, deductible=500, coinsurance_percent=10, oop_max=5_000),
        )
        st.caption("Illustrative plan numbers. Put your Intel plan's numbers into the Compare medical plans calculator.")

    st.subheader("📋 What to know and do")
    table = ["| Item | What it means | Do this 👉 |", "|---|---|---|"]
    table += [f"| **{a}** | {b} | {c} |" for a, b, c in t["items"]]
    st.markdown(md("\n".join(table)))
    do, dont = st.columns(2)
    do.success(md("✅ **Do:** " + t["do"]))
    dont.error(md("⛔ **Don't:** " + t["dont"]))

    st.subheader("🔷 Check in your Intel benefits")
    st.caption("These change by year and grade. Tick each one once you have looked it up, and write the value in My benefits sheet.")
    for item in t["intel"]:
        st.checkbox(md(item), key=f"chk_{t['title']}_{item}")
    st.button("🗂️ Record values in My benefits sheet", key="sheet_" + t["title"], on_click=go_to, args=(SHEET,))

    st.subheader("🔗 Official Intel and government sources")
    cols = st.columns(min(3, len(t["links"])))
    for i, name in enumerate(t["links"]):
        cols[i % len(cols)].markdown(f"[{name} ↗]({SOURCES[name]})")
    show(t["title"], t["visual"])
    mistakes_table(info["mistakes"])

    prev_col, next_col = st.columns(2)
    if index > 0:
        prev_col.button("← Previous topic", on_click=go_to, args=(TOPIC_NAMES[index - 1],), width="stretch")
    nxt = TOPIC_NAMES[index + 1] if index + 1 < len(TOPICS) else SHEET
    next_col.button("Next topic →" if index + 1 < len(TOPICS) else "My benefits sheet →", on_click=go_to, args=(nxt,), type="primary", width="stretch")


def sheet_csv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(BENEFITS_SHEET[0]))
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def render_sheet():
    st.header("🗂️ My benefits sheet")
    st.write(
        "One page for your actual Intel plan numbers. Fill in **My value** from the internal benefits site, add rows for anything else, "
        "then download it. Nothing is saved on the server; upload your file next time to continue."
    )
    uploaded = st.file_uploader("Load a saved sheet (CSV)", type="csv")
    rows = BENEFITS_SHEET
    if uploaded is not None:
        rows = list(csv.DictReader(io.StringIO(uploaded.getvalue().decode("utf-8"))))
    edited = st.data_editor(rows, num_rows="dynamic", hide_index=True, width="stretch", key="sheet_editor")
    filled = sum(1 for r in edited if (r.get("My value") or "").strip())
    st.progress(filled / max(1, len(edited)), text=f"{filled} of {len(edited)} filled in")
    st.download_button("⬇️ Download my sheet (CSV)", sheet_csv(edited), file_name="my-intel-benefits.csv", mime="text/csv", type="primary")
    st.caption("Do not enter account numbers, passwords or Social Security numbers.")
    links_row(["Intel benefits overview (public)", "DOL health plans and benefits", "IRS HSA (Pub 969)"])
    mistakes_table(PAGE_MISTAKES["sheet"])


def render_planner():
    st.header("📅 Year planner")
    st.write("Every yearly deadline and check-up in one list. Download the calendar file to get them in Outlook, Google or Apple Calendar.")
    now = today()
    soon = upcoming(KEY_DATES, now, days=366)
    month = st.segmented_control("Show", ["Next 60 days", "All year"], default="Next 60 days")
    rows = [r for r in soon if month != "Next 60 days" or (r[0] - now).days <= 60]
    st.dataframe(
        [{"Date": f"{w:%a %b %d, %Y}", "In": f"{(w - now).days} days", "": icon, "What": title, "Topic": topic} for w, icon, title, topic in rows],
        hide_index=True,
        width="stretch",
    )
    ics = build_ics([(w, f"{icon} {title}") for w, icon, title, _ in soon])
    st.download_button("⬇️ Add all to my calendar (.ics, repeats yearly)", ics, file_name="intel-myben-reminders.ics", mime="text/calendar", type="primary")
    st.caption("Intel-specific dates (open enrollment, vests, ESPP purchases) vary; add them to your calendar from the benefits and stock plan sites.")
    show("A family year", ["Taxes Q1", "Health mid-year", "School Aug", "Enroll Nov"])
    links_row(["IRS estimated taxes", "California FTB estimated payments", "CA Board of Equalization property tax", "Ready.gov (FEMA)"])
    mistakes_table(PAGE_MISTAKES["planner"])


def calc_take_home():
    a, b = st.columns(2)
    salary = a.number_input("Base salary ($/yr)", 0.0, value=210_000.0, step=5_000.0, format="%.0f")
    bonus = a.number_input("Bonus ($/yr)", 0.0, value=25_000.0, step=1_000.0, format="%.0f")
    rsu = a.number_input("RSU vests ($/yr)", 0.0, value=40_000.0, step=1_000.0, format="%.0f")
    k401 = b.number_input("Pre-tax 401(k) ($/yr)", 0.0, value=24_500.0, step=500.0, format="%.0f")
    hsa = b.number_input("HSA, your part ($/yr)", 0.0, value=6_000.0, step=250.0, format="%.0f")
    fsa = b.number_input("Health FSA ($/yr)", 0.0, value=0.0, step=100.0, format="%.0f", help="Usually 0 if you have a full HSA.")
    dcfsa = b.number_input("Dependent care FSA ($/yr)", 0.0, value=7_500.0, step=500.0, format="%.0f")
    premiums = b.number_input("Medical/dental/vision premiums ($/yr)", 0.0, value=3_600.0, step=100.0, format="%.0f")
    gross = salary + bonus + rsu
    r = take_home(gross, k401, hsa, fsa, dcfsa, premiums, children=1)
    x, y, z, w = st.columns(4)
    x.metric("Take-home per year", money(r["Take-home pay"]))
    y.metric("Per month", money(r["Take-home pay"] / 12))
    z.metric("Effective tax rate", f"{r['Effective tax rate']:.1%}")
    w.metric("Top rates (fed + CA)", f"{r['Federal marginal rate']:.0%} + {r['California marginal rate']:.1%}")
    st.bar_chart(
        {"Part": ["Federal tax", "Social Security", "Medicare", "CA tax", "CA SDI", "Pre-tax savings", "Take-home"],
         "Dollars": [r["Federal income tax"], r["Social Security"], r["Medicare"], r["California income tax"], r["CA SDI"], k401 + hsa + fsa + dcfsa + premiums, r["Take-home pay"]]},
        x="Part", y="Dollars", horizontal=True, sort=False,
    )
    st.caption(
        f"Married filing jointly, one earner, one child, standard deductions, {FED_YEAR} federal and {CA_YEAR} California brackets. "
        "Ignores itemizing, other credits, AMT and spouse income. California taxes HSA contributions."
    )


def calc_rsu():
    vest = st.number_input("RSU vest value this year ($)", 0.0, value=40_000.0, step=1_000.0, format="%.0f")
    fed_options = [0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    ca_options = [0.06, 0.08, 0.093, 0.103, 0.113, 0.123]
    a, b = st.columns(2)
    fed = a.selectbox("Your federal bracket", fed_options, index=2, format_func=lambda r: f"{r:.0%}")
    ca = b.selectbox("Your California bracket", ca_options, index=2, format_func=lambda r: f"{r * 100:g}%")
    withheld, owed, gap = rsu_withholding_gap(vest, fed, ca)
    x, y, z = st.columns(3)
    x.metric("Withheld at vest", money(withheld))
    y.metric("Likely income tax", money(owed))
    z.metric("Set aside for April" if gap > 0 else "Likely refund", money(abs(gap)), delta=f"{gap / vest:.1%} of vest" if vest else None, delta_color="inverse")
    st.caption("Uses 22% federal (37% above \\$1M of supplemental pay) and 10.23% California withholding. Find your brackets with the take-home calculator.")


def calc_espp():
    a, b = st.columns(2)
    contrib = a.number_input("Payroll contributions this period ($)", 0.0, value=12_500.0, step=500.0, format="%.0f")
    discount = a.number_input("Plan discount (%) — enter your plan's", 0.0, 50.0, value=15.0, step=1.0)
    lookback = a.toggle("Plan has a lookback (lower of start or end price)", value=True)
    start = b.number_input("Share price at offering start ($)", 0.01, value=20.0, step=0.5)
    end = b.number_input("Share price at purchase ($)", 0.01, value=24.0, step=0.5)
    price, shares, value, gain, pct = espp_purchase(contrib, start, end, discount, lookback)
    x, y, z = st.columns(3)
    x.metric("You pay per share", f"${price:,.2f}")
    y.metric("Shares bought", f"{shares:,.1f}")
    z.metric("Gain if sold at purchase", money(gain), delta=f"{pct:.1f}% return")
    st.caption("The discount part is ordinary income when you sell. Selling right away locks in the gain but makes it a disqualifying disposition; see IRS Topic 427.")


def calc_accounts():
    st.write("Enter what you are putting in this year; see the room left under the 2026 limits.")
    names = ["401(k) employee deferral", "HSA family", "IRA (each spouse)", "Dependent care FSA (per household)"]
    defaults = [18_000.0, 6_000.0, 0.0, 5_000.0]
    paychecks = st.number_input("Paychecks left this year", 1, 26, value=6)
    contributions = {n: st.number_input(f"{n} ($ this year)", 0.0, value=d, step=500.0, key="acct_" + n) for n, d in zip(names, defaults)}
    for name, limit, amount, room in account_gaps(contributions):
        st.progress(min(1.0, amount / limit), text=md(f"{name}: {money(amount)} of {money(limit)} · room {money(room)} · {money(room / paychecks)} per paycheck"))
    st.caption("Add \\$8,000 401(k) catch-up at 50+ and \\$1,000 HSA catch-up at 55+. HSA limit includes Intel's contribution. IRA is per spouse.")


def calc_emergency():
    cash = st.number_input("Emergency cash ($)", 0.0, value=40_000.0, step=1_000.0, format="%.0f")
    essentials = st.number_input("Essential monthly costs ($)", 0.0, value=9_000.0, step=250.0, format="%.0f", help="Mortgage/rent, food, insurance, utilities, childcare, minimum debt payments.")
    target = st.slider("Months you want covered", 3, 12, 6)
    months = reserve_months(cash, essentials)
    if months is None:
        st.warning("Enter essential monthly costs above zero.")
        return
    a, b = st.columns(2)
    a.metric("Months covered", f"{months:.1f}")
    b.metric(f"Gap to {target} months", money(max(0.0, target * essentials - cash)))
    st.progress(min(1.0, months / target), text=f"{min(100, 100 * months / target):.0f}% of target")
    st.caption("A single-employer tech household often aims higher than 6 months. Count only cash you can reach within days.")


def calc_life():
    a, b = st.columns(2)
    income = a.number_input("Income to replace ($/yr)", 0.0, value=210_000.0, step=5_000.0, format="%.0f")
    years = a.slider("Years to replace it", 1, 30, 12, help="Until your child finishes college is a common choice.")
    debts = a.number_input("Debts other than mortgage ($)", 0.0, value=20_000.0, step=1_000.0, format="%.0f")
    mortgage = a.number_input("Mortgage balance ($)", 0.0, value=800_000.0, step=10_000.0, format="%.0f")
    college = b.number_input("College fund needed ($)", 0.0, value=250_000.0, step=10_000.0, format="%.0f")
    final = b.number_input("Final costs ($)", 0.0, value=20_000.0, step=1_000.0, format="%.0f")
    existing = b.number_input("Existing life cover incl. Intel ($)", 0.0, value=420_000.0, step=10_000.0, format="%.0f")
    savings = b.number_input("Savings that could be used ($)", 0.0, value=300_000.0, step=10_000.0, format="%.0f")
    need = life_insurance_need(income, years, debts, mortgage, college, final, existing, savings)
    st.metric("Additional term life to consider", money(need))
    st.caption("A DIME-style estimate (debts, income, mortgage, education). Work coverage usually ends with the job; a private term policy does not.")


def calc_college():
    a, b = st.columns(2)
    balance = a.number_input("529 balance today ($)", 0.0, value=30_000.0, step=1_000.0, format="%.0f")
    monthly = a.number_input("Monthly contribution ($)", 0.0, value=600.0, step=50.0, format="%.0f")
    years = a.slider("Years until college", 1, 18, 8)
    ret = b.slider("Assumed return (%/yr)", 0.0, 10.0, 6.0, 0.5)
    cost = b.number_input("4-year cost in today's dollars ($)", 0.0, value=160_000.0, step=5_000.0, format="%.0f", help="Your estimate; UC in-state total cost of attendance is a common benchmark.")
    infl = b.slider("College cost inflation (%/yr)", 0.0, 8.0, 4.0, 0.5)
    series = compound_series(balance, monthly, ret, years)
    needed = future_cost(cost, infl, years)
    x, y, z = st.columns(3)
    x.metric("Projected 529", money(series[-1]))
    y.metric("Projected cost", money(needed))
    z.metric("Covered", f"{min(100, 100 * series[-1] / needed) if needed else 100:.0f}%")
    st.line_chart({"Year": list(range(len(series))), "529 value": series}, x="Year", y_label="Dollars")
    st.caption("Constant return is a simplification; real returns vary and can be negative.")


def calc_retirement():
    a, b = st.columns(2)
    saved = a.number_input("Retirement savings today ($)", 0.0, value=650_000.0, step=10_000.0, format="%.0f")
    yearly = a.number_input("Yearly contributions incl. employer ($)", 0.0, value=35_000.0, step=1_000.0, format="%.0f")
    years = a.slider("Years until retirement", 1, 30, 15)
    ret = b.slider("Assumed return (%/yr)", -2.0, 10.0, 6.0, 0.5)
    infl = b.slider("Inflation (%/yr)", 0.0, 6.0, 2.5, 0.5)
    rate = b.slider("Withdrawal rate (%)", 3.0, 5.0, 4.0, 0.25)
    series = compound_series(saved, yearly / 12, ret, years)
    today_dollars = real_value(series[-1], infl, years)
    x, y, z = st.columns(3)
    x.metric("Projected savings", money(series[-1]))
    y.metric("In today's dollars", money(today_dollars))
    z.metric(f"Income at {rate:g}%/yr", money(today_dollars * rate / 100) + "/yr")
    st.line_chart({"Year": list(range(len(series))), "Savings": series}, x="Year", y_label="Dollars")
    st.caption("Add Social Security from your my Social Security statement. Taxes on pre-tax withdrawals are not included.")


def calc_mortgage():
    a, b = st.columns(2)
    price = a.number_input("Loan amount ($)", 0.0, value=900_000.0, step=10_000.0, format="%.0f")
    rate = a.number_input("Interest rate (%)", 0.0, 15.0, value=6.25, step=0.125)
    years = a.selectbox("Term (years)", [30, 20, 15], index=0)
    value = b.number_input("Home assessed value ($)", 0.0, value=1_200_000.0, step=10_000.0, format="%.0f")
    tax_rate = b.number_input("Property tax rate (%)", 0.0, 3.0, value=1.15, step=0.05, help="1% base plus local bonds.")
    insurance = b.number_input("Home insurance ($/yr)", 0.0, value=2_400.0, step=100.0, format="%.0f")
    pi = mortgage_payment(price, rate, years)
    tax = max(0.0, value - 7_000) * tax_rate / 100 / 12
    x, y, z = st.columns(3)
    x.metric("Principal + interest", money(pi) + "/mo")
    y.metric("Property tax", money(tax) + "/mo", help="After the $7,000 homeowners' exemption.")
    z.metric("Total housing", money(pi + tax + insurance / 12) + "/mo")
    st.caption(md(f"Total interest over the loan: {money(pi * years * 12 - price)}. Excludes HOA, earthquake insurance and maintenance (budget ~1% of value per year)."))


def calc_concentration():
    holding = st.number_input("Intel stock you hold (RSU, ESPP, 401(k)) ($)", 0.0, value=120_000.0, step=5_000.0, format="%.0f")
    total = st.number_input("Total investments ($)", 0.0, value=900_000.0, step=10_000.0, format="%.0f")
    share = concentration(holding, total)
    if share is None:
        st.warning("Enter total investments above zero.")
        return
    st.metric("Share in Intel", f"{share:.1f}%")
    st.progress(min(1.0, share / 100), text="A common guideline is 10% or less in any single company")
    if share > 10:
        st.warning(md(f"Selling {money(holding - 0.10 * total)} would bring Intel to 10%. Check taxes and trading windows first."))
    st.caption("Your paycheck and bonus already depend on Intel, so many planners suggest less, not more, in the stock.")


def calc_plans():
    st.write("Compare two medical plans' total yearly cost for your family. Use the numbers from Intel's open-enrollment plan summaries.")
    plans = []
    for col, name, d in zip(st.columns(2), ["Plan A", "Plan B"], [(1_800, 3_400, 20, 8_000, 1_000), (4_800, 500, 10, 5_000, 0)]):
        with col:
            st.markdown(f"**{name}**")
            plans.append(dict(
                premiums=st.number_input("Your premiums ($/yr)", 0.0, value=float(d[0]), step=100.0, format="%.0f", key=name + "p"),
                deductible=st.number_input("Family deductible ($)", 0.0, value=float(d[1]), step=100.0, format="%.0f", key=name + "d"),
                coinsurance_percent=st.number_input("Your coinsurance after deductible (%)", 0.0, 100.0, value=float(d[2]), step=5.0, key=name + "c"),
                oop_max=st.number_input("Family out-of-pocket max ($)", 0.0, value=float(d[3]), step=500.0, format="%.0f", key=name + "o"),
                employer_hsa=st.number_input("Employer HSA money ($/yr)", 0.0, value=float(d[4]), step=100.0, format="%.0f", key=name + "h"),
            ))
    spend = st.slider("Expected medical spending this year ($)", 0, 30_000, 6_000, 500)
    a_cost, b_cost = (plan_cost(spending=spend, **p) for p in plans)
    x, y, z = st.columns(3)
    x.metric("Plan A yearly cost", money(a_cost))
    y.metric("Plan B yearly cost", money(b_cost))
    z.metric("Cheaper at this spending", "Plan A" if a_cost <= b_cost else "Plan B", delta=money(abs(a_cost - b_cost)) + " less")
    plan_compare_chart(*plans)
    st.caption("Cost = premiums + what you pay for care (capped at the out-of-pocket max) − employer HSA money. Copays and drug tiers are ignored; HSA plans also save federal tax on your contributions.")


def calc_net_worth():
    a, b = st.columns(2)
    a.markdown("**Assets**")
    assets = {n: a.number_input(f"{n} ($)", 0.0, value=v, step=1_000.0, format="%.0f", key="nw_" + n) for n, v in [
        ("Cash and savings", 60_000.0), ("401(k) and IRAs", 650_000.0), ("HSA", 30_000.0), ("Brokerage (non-Intel)", 150_000.0),
        ("Intel stock", 120_000.0), ("529", 30_000.0), ("Home value", 1_400_000.0), ("Cars", 30_000.0)]}
    b.markdown("**Liabilities**")
    debts = {n: b.number_input(f"{n} ($)", 0.0, value=v, step=1_000.0, format="%.0f", key="nw_" + n) for n, v in [
        ("Mortgage", 800_000.0), ("Car loans", 15_000.0), ("Credit cards and other", 0.0)]}
    total_assets, total_debts = sum(assets.values()), sum(debts.values())
    investable = total_assets - assets["Home value"] - assets["Cars"]
    x, y, z = st.columns(3)
    x.metric("Net worth", money(total_assets - total_debts))
    y.metric("Investable assets", money(investable), help="Excludes home and cars.")
    z.metric("Intel share of investable", f"{concentration(assets['Intel stock'], investable) or 0:.1f}%")
    st.bar_chart({"Item": list(assets) + list(debts), "Dollars": list(assets.values()) + [-v for v in debts.values()]}, x="Item", y="Dollars", horizontal=True, sort=False)
    st.caption("Net worth = assets − liabilities. Update it every quarter; home equity is not spendable cash.")


def review_score():
    return sum(bool(st.session_state.get("rev_" + t["title"])) for t in TOPICS) / len(TOPICS)


def render_review():
    st.header("✅ Annual life review")
    st.write("One key action per life topic. Tick what is done this year; the score shows where to focus next. Repeat every January.")
    score = review_score()
    st.metric("Done this year", f"{score:.0%}", help="Ticks are kept for this browser session only.")
    st.progress(score)
    for group in GROUPS:
        st.markdown(f"#### {group}")
        for t in TOPICS:
            if t["group"] == group:
                st.checkbox(md(f"{t['icon']} **{t['title']}**: {t['do']}"), key="rev_" + t["title"])
    by_group = [100 * sum(bool(st.session_state.get("rev_" + t["title"])) for t in TOPICS if t["group"] == g) / sum(t["group"] == g for t in TOPICS) for g in GROUPS]
    draw_chart({"kind": "bar", "title": "Progress by area (% done)", "data": {"Area": GROUPS, "% done": by_group}, "x": "Area", "y": "% done", "note": "Fix the lowest area first."})
    todo = [t for t in TOPICS if not st.session_state.get("rev_" + t["title"])][:3]
    if todo:
        st.info(md("**Next three:** " + " · ".join(f"{t['icon']} {t['do']}" for t in todo)))
    links_row(["Intel benefits overview (public)", "IRS withholding estimator", "Social Security my account", "Ready.gov (FEMA)"])
    mistakes_table(PAGE_MISTAKES["review"])


HOTLINES = [
    ("🚑 Emergency (police, fire, ambulance)", "911"),
    ("🧠 Suicide & Crisis Lifeline", "988"),
    ("☠️ Poison Help", "1-800-222-1222"),
    ("👵 Eldercare Locator", "1-800-677-1116"),
]


def card_html(rows):
    body = "".join(f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in rows if v.strip())
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Family emergency card</title>"
        "<style>body{font-family:system-ui,Arial;font-size:18px;margin:24px}h1{color:#0068b5}"
        "table{border-collapse:collapse;width:100%}th,td{border:1px solid #9ab;padding:8px;text-align:left;vertical-align:top}"
        "th{background:#e8f1fb;width:35%}</style></head><body><h1>🆘 Family emergency card</h1>"
        f"<table>{body}</table><p>Print it, keep a copy in each phone, car and go-bag. Update it when anything changes.</p></body></html>"
    )


def render_card():
    st.header("🆘 Family emergency card")
    st.write("The one page your family, a babysitter or a first responder needs. Fill it in, then download and print it. Nothing is saved.")
    cols = st.columns(len(HOTLINES))
    for col, (name, number) in zip(cols, HOTLINES):
        with col.container(border=True):
            st.caption(name)
            st.markdown(f"#### [📞 {number}](tel:{number.replace('-', '')})")
    a, b = st.columns(2)
    fields = [
        (a, "Family name"), (a, "Parent 1 name and phone"), (a, "Parent 2 name and phone"), (a, "Child name, age and school"),
        (a, "School office phone"), (a, "Out-of-area contact and phone"), (b, "Meeting place near home"),
        (b, "Meeting place outside the neighborhood"), (b, "Blood types and allergies"), (b, "Daily medicines"),
        (b, "Doctor / pediatrician and phone"), (b, "Health plan member services and nurse line"),
    ]
    rows = [(label, col.text_input(label, key="card_" + label)) for col, label in fields]
    rows += [(name, number) for name, number in HOTLINES]
    if rows[0][1].strip():
        st.download_button("⬇️ Download printable card (HTML)", card_html(rows), file_name="family-emergency-card.html", mime="text/html", type="primary")
    else:
        st.info("Type the family name to enable the download.")
    st.subheader("🎒 Go-bag checklist")
    for item in ["Water (1 gallon per person per day)", "Non-perishable food", "Medicines and copies of prescriptions", "Phone chargers and power bank",
                 "Flashlight and batteries", "Cash in small bills", "Copies of IDs and insurance cards", "N95 masks", "Comfort item for your child"]:
        st.checkbox(item, key="bag_" + item)
    links_row(["Ready.gov (FEMA)", "Cal OES", "Earthquake Warning California (MyShake)", "CAL FIRE Ready for Wildfire", "Poison Help (HRSA)", "SAMHSA 988 Lifeline"])
    mistakes_table(PAGE_MISTAKES["card"])


CALC_FUNCS = dict(zip(CALCS, [calc_take_home, calc_plans, calc_net_worth, calc_rsu, calc_espp, calc_accounts, calc_emergency, calc_life, calc_college, calc_retirement, calc_mortgage, calc_concentration]))


def render_calculators():
    st.header("🧮 Calculators")
    st.caption("Inputs stay in this browser session and are not saved. Use round numbers; no account details needed.")
    tool = st.segmented_control("Choose a calculator", CALCS, default=CALCS[0])
    if tool is None:
        st.info("Pick a calculator above.")
    else:
        CALC_FUNCS[tool]()
    links_row(["IRS withholding estimator", "California FTB tax rates", "SEC Investor.gov", "SSA retirement age calculator"])
    mistakes_table(PAGE_MISTAKES["calculators"])


def render_about():
    st.header("📚 Sources & method")
    st.write(
        f"Federal numbers are for tax year {FED_YEAR} (IRS). California brackets are the {CA_YEAR} FTB schedule, the latest published when this was written; "
        "update them in `calculations.py` each year. Intel details come only from Intel's public benefits page and are shown as items to check, "
        "because plans change by year, location and grade. Headlines come from Google News RSS, with a short summary from each story's description."
    )
    st.dataframe(
        [{"Source": k, "Link": v} for k, v in SOURCES.items()],
        hide_index=True,
        width="stretch",
        column_config={"Link": st.column_config.LinkColumn("Link")},
    )
    show("How to use this hub", ["Check numbers", "Fill sheet", "Set reminders", "Review yearly"])
    mistakes_table(PAGE_MISTAKES["about"])


if section == HOME:
    render_home()
elif section == CHEATSHEET:
    render_cheatsheet()
elif section in NEWS_NAMES:
    render_news(NEWS_NAMES.index(section))
elif section in TOPIC_NAMES:
    render_topic(TOPIC_NAMES.index(section))
elif section == CARD:
    render_card()
elif section == REVIEW:
    render_review()
elif section == SHEET:
    render_sheet()
elif section == PLANNER:
    render_planner()
elif section == CALCULATORS:
    render_calculators()
else:
    render_about()
