# 🔷 Intel MyBen

One Streamlit app where an Intel AI/ML technical program manager in California, with a spouse and a 10-year-old, can manage every life topic: work news, benefits, health, money, stock, taxes, insurance, home and family. It follows the layout of [finance-faqs](https://github.com/chennab12/finance-faqs): a sidebar menu, one page per topic, previous/next buttons, a master cheatsheet and calculators.

## Pages

- 🏠 **My dashboard**: 2026 limits, the next reminder, deadlines in the next 45 days, every topic as a card, and the latest Intel and AI headlines.
- 📌 **Master cheatsheet**: one row per topic, 2026 account limits, and federal (2026) and California (2025) tax brackets.
- 🔵 **Intel news** and 🤖 **AI & ML news**: Google News headlines with two-sentence summaries, refreshed every 30 minutes, no API key.
- **21 life topics**. Each has four key numbers, a key metrics and formulas table, charts, a "what to know and do" table, do/don't, a "Check in your Intel benefits" checklist, links to official Intel and government sources only, and a common-mistakes table at the bottom:
  - Work & career: Career & TPM growth · Time off & leave · Intel perks & extras
  - Health: Medical plan & HSA · Preventive health · Dental · Vision · Mental health & wellbeing
  - Money, stock & taxes: Paycheck, budget & cash · Intel stock: RSUs & ESPP · Retirement: 401(k), IRA & Social Security · Investing & net worth · Taxes: federal & California · Insurance
  - Family & home: Home & property · Kid: school, 529 & childcare · Will, estate & family · Car & commute · Documents, identity & security · Family emergencies & disasters · Aging parents & caregiving
- 🆘 **Family emergency card**: 911, 988, Poison Help and Eldercare numbers, a printable family card and a go-bag checklist.
- ✅ **Annual life review**: one key action per topic, a score and progress chart by area, and the next three things to do.
- 🗂️ **My benefits sheet**: an editable table for your actual Intel plan numbers; download it as CSV and upload it next time.
- 📅 **Year planner**: tax, enrollment, health and school dates, with a calendar file that repeats every year.
- 🧮 **Calculators**: take-home pay and taxes (federal + California), compare medical plans, net worth, RSU tax gap, ESPP purchase, max your accounts, emergency fund, life insurance need, college 529, retirement, mortgage, and Intel stock concentration.

## About the numbers

Every link points to an Intel or government source (a test checks the domains). Formulas, charts and mistake tables live in `insights.py`.


Federal figures are for tax year 2026. California brackets are the 2025 FTB schedule, the latest published when this was written. Update `calculations.py` and `content.py` each January.

Intel plan details (401(k) contribution, ESPP discount, HSA money, life and disability multiples, perks) change by year and grade, so the app does not state them as facts. Each topic lists them as items to check on Intel's internal benefits site and record in **My benefits sheet**.

Everything is general information, not tax, legal, medical or investment advice.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pip install pytest && python -m pytest -q`. GitHub Actions runs them on every push. Tests stub out news fetching so they work offline.

For Streamlit Community Cloud, deploy this repository with `app.py` as the entry point.
