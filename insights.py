"""Per-section formulas, charts and common-mistake tables.

Charts are either public figures (stated with their source year) or worked examples from calculations.py,
labelled as illustrations.
"""
from calculations import (
    CA_BRACKETS_MFJ,
    FED_BRACKETS_MFJ,
    compound_series,
    marginal_rate,
    mortgage_payment,
    probate_fee,
    rsu_withholding_gap,
    take_home,
)


def _bar(title, labels, values, y_label, note, x="Item"):
    return {"kind": "bar", "title": title, "data": {x: labels, y_label: values}, "x": x, "y": y_label, "note": note}


def _line(title, series, y_label, note, x="Year"):
    return {"kind": "line", "title": title, "data": series, "x": x, "y": list(k for k in series if k != x), "y_label": y_label, "note": note}


_example = take_home(275_000, 24_500, 6_000, 0, 7_500, 3_600)
_years = 15
_max_401k = compound_series(150_000, (24_500 + 6_000) / 12, 6, _years)
_half_401k = compound_series(150_000, (12_000 + 3_000) / 12, 6, _years)
_fees = {f: compound_series(500_000, 0, 6 - f, 20)[-1] for f in (0.05, 0.5, 1.0)}


def _combined(taxable):
    return round(100 * (marginal_rate(taxable, FED_BRACKETS_MFJ) + marginal_rate(taxable, CA_BRACKETS_MFJ)), 1)


INSIGHTS = {
    "Career & TPM growth": {
        "formulas": [
            ("Months of runway", "Liquid cash ÷ essential monthly costs", "$60,000 ÷ $9,000 = 6.7 months"),
            ("Severance runway", "(Severance + unemployment) ÷ essential monthly costs", "Add to cash runway for a job-loss plan"),
            ("Program impact", "Value delivered ÷ cost (or time saved × loaded hourly cost)", "Write one number per launch in your impact log"),
        ],
        "chart": _bar("Cash buffer for $9,000/month of essentials", ["3 months", "6 months", "9 months", "12 months"], [27_000, 54_000, 81_000, 108_000], "Dollars", "Worked example: months × essential monthly costs.", x="Target"),
        "mistakes": [
            ("No written record of impact", "Reviews and promotions rely on memory.", "Keep a weekly impact log with numbers."),
            ("Only work copies of key documents", "Access ends the day a job ends.", "Keep personal copies of offer letters, pay stubs and benefits summaries."),
            ("Skills frozen on one stack", "AI tools and practices change every year.", "Pick one AI/ML skill per half-year and ship something with it."),
            ("Tiny cash buffer with one employer", "Job, bonus and stock all depend on Intel.", "Hold 6–12 months of essentials in cash."),
        ],
    },
    "Time off & leave": {
        "formulas": [
            ("PTO hours left", "Balance + accrual per pay period × pay periods left − planned hours", "Plan to stay below the carryover cap"),
            ("PFL weekly benefit", "About 70–90% of weekly wages, up to the state maximum", "Check the EDD calculator for your number"),
        ],
        "chart": _bar("Leave available in California (weeks)", ["Paid sick leave", "Bereavement", "Intel sabbatical*", "CA Paid Family Leave", "CFRA/FMLA job protection", "CA SDI (own disability)"], [1, 1, 4, 8, 12, 52], "Weeks", "State and federal law; *Intel's public benefits page lists a 4-week sabbatical for eligible US employees.", x="Leave type"),
        "mistakes": [
            ("Losing vacation to the carryover cap", "Unused days disappear.", "Book school breaks and one trip in January."),
            ("Mixing up PFL and job protection", "PFL pays; CFRA/FMLA protect the job.", "Tell HR first, then file the PFL or SDI claim with EDD."),
            ("Filing SDI late", "Claims have deadlines.", "File within 49 days of the start of the disability."),
        ],
    },
    "Intel perks & extras": {
        "formulas": [
            ("Value of a pre-tax benefit", "Amount × (federal + state + FICA rate)", "$4,080 commuter × 40% ≈ $1,632 saved"),
            ("Matched giving", "Your gift × (1 + match ratio)", "$1,000 with 1:1 match = $2,000 to the charity"),
        ],
        "chart": _bar("2026 tax-free or pre-tax limits per year", ["Commuter ($340×12)", "Tuition assistance", "Health FSA", "Dependent care FSA", "HSA (family)"], [4_080, 5_250, 3_400, 7_500, 8_750], "Dollars", "IRS 2026 figures; whether Intel offers each one varies.", x="Benefit"),
        "mistakes": [
            ("Never reading the perks list", "Easy money is left unused.", "Review perks each January and at open enrollment."),
            ("Assuming last year's perk still exists", "Perks changed in 2024–2025 cost cuts.", "Re-check each perk before relying on it."),
            ("Giving without the match", "The charity gets half as much.", "Give through Intel's matching portal."),
        ],
    },
    "Medical plan & HSA": {
        "formulas": [
            ("Total yearly cost", "Premiums + min(out-of-pocket max, deductible + coinsurance × (spending − deductible)) − employer HSA money", "Compare for low, medium and high spending years"),
            ("HSA federal tax saved", "HSA contribution × (federal marginal rate + 7.65% FICA)", "$8,750 × 29.65% ≈ $2,594 (CA still taxes it)"),
        ],
        "chart": None,  # drawn live from the plan comparison calculator
        "mistakes": [
            ("Choosing by premium alone", "A low premium can mean a big bill in a bad year.", "Use the plan comparison calculator for three spending levels."),
            ("Spending the HSA every year", "Loses decades of tax-free growth.", "Pay small bills from cash, invest the HSA, keep receipts."),
            ("Forgetting California taxes the HSA", "Surprise state tax on contributions and earnings.", "Expect to report HSA contributions on your CA return."),
            ("Out-of-network surprises", "Bills can be much larger.", "Confirm doctors, labs and urgent care are in network."),
        ],
    },
    "Preventive health": {
        "formulas": [
            ("Body mass index", "Weight (kg) ÷ height (m)²", "A screening number, not a diagnosis"),
            ("Weekly activity", "Minutes per day × active days", "30 × 5 = 150 minutes"),
        ],
        "chart": _bar("Age when key screenings start (USPSTF)", ["Cervical", "Diabetes (if overweight)", "Mammogram", "Colorectal"], [21, 35, 40, 45], "Age", "USPSTF recommendations; ask your doctor what fits you.", x="Screening"),
        "mistakes": [
            ("Skipping the free annual physical", "Problems are found late.", "Book all three check-ups in one 'health month'."),
            ("Missing the colon screening at 45", "It is one of the most preventable cancers.", "Ask your doctor which test and put it on the calendar."),
            ("Long sitting days", "Back pain, weight gain, poor sleep.", "Stand or walk every hour; aim for 150 minutes a week."),
        ],
    },
    "Dental": {
        "formulas": [
            ("Plan benefit used", "Claims paid ÷ annual maximum", "Plan big work across two plan years if not urgent"),
            ("Ortho cost after FSA", "Cost − plan payment − (remaining cost × tax rate)", "Paying with pre-tax money saves your marginal rate"),
        ],
        "chart": _bar("Worked example: $6,000 braces", ["Plan pays (lifetime max)", "You pay with FSA/HSA", "Tax saved by paying pre-tax"], [2_000, 4_000, 1_268], "Dollars", "Illustration: $2,000 ortho max and a 31.7% combined tax saving (22% federal + 9.3% CA, ignoring FICA). Use your own plan numbers.", x="Part"),
        "mistakes": [
            ("Missing the early ortho check", "Some problems are easier to fix young.", "Get an orthodontic opinion now; AAO suggests by age 7."),
            ("Leaving the annual maximum unused", "It resets every year.", "Book two cleanings and finish work within the plan year."),
            ("Paying ortho with after-tax money", "Costs 30–40% more in effect.", "Use the health FSA or HSA."),
        ],
    },
    "Vision": {
        "formulas": [
            ("20-20-20 rule", "Every 20 minutes, look 20 feet away for 20 seconds", "Set a reminder on long work days"),
            ("Glasses net cost", "Price − plan allowance − tax saved via FSA/HSA", "Use the allowance first"),
        ],
        "chart": None,
        "mistakes": [
            ("Relying on the school screening", "It can miss problems.", "Book a full eye exam for your child yearly."),
            ("Ignoring a rising prescription", "Nearsightedness often grows through school years.", "Ask about myopia control and more outdoor time."),
            ("Paying after-tax for glasses", "They are FSA/HSA eligible.", "Pay with pre-tax money."),
        ],
    },
    "Mental health & wellbeing": {
        "formulas": [
            ("Sleep debt", "(Target hours − actual hours) × nights", "1 hour short × 5 nights = 5 hours"),
            ("Focus time", "Hours without meetings per week", "Protect at least two 2-hour blocks"),
        ],
        "chart": _bar("Minimum recommended sleep (hours per night)", ["Adult", "Teen 13–18", "Child 6–12"], [7, 8, 9], "Hours", "CDC sleep guidance (minimums of each age range).", x="Age group"),
        "mistakes": [
            ("Waiting until burnout", "Recovery takes much longer.", "Use EAP counseling early; it is free and confidential."),
            ("Not knowing the crisis number", "Seconds matter in a crisis.", "Save 988 and the EAP number in every family phone."),
            ("Screens until bedtime", "Worse sleep for you and your child.", "Screens off one hour before bed."),
        ],
    },
    "Paycheck, budget & cash": {
        "formulas": [
            ("Savings rate", "(401(k) + HSA + other savings) ÷ gross pay", "Aim for 15–20% or more"),
            ("Monthly sinking fund", "Total yearly irregular bills ÷ 12", "$12,000 of yearly bills = $1,000/month"),
            ("Cash flow", "Take-home pay − all spending", "Run monthly life on base pay"),
        ],
        "chart": _bar(
            "Where $275,000 of pay goes (worked example)",
            ["Federal tax", "Social Security", "Medicare", "CA tax", "CA SDI", "Pre-tax savings and premiums", "Take-home"],
            [round(_example["Federal income tax"]), round(_example["Social Security"]), round(_example["Medicare"]), round(_example["California income tax"]), round(_example["CA SDI"]), 41_600, round(_example["Take-home pay"])],
            "Dollars",
            "From the take-home calculator: married filing jointly, one child, 401(k) $24,500, HSA $6,000, DCFSA $7,500, premiums $3,600.",
            x="Part",
        ),
        "mistakes": [
            ("Budgeting on bonus and RSUs", "They vary and are taxed differently.", "Live on base pay; send variable pay to goals."),
            ("Forgetting yearly bills", "Property tax and insurance cause cash crunches.", "Set up sinking funds."),
            ("Over $250,000 at one bank", "Above FDIC insurance limits.", "Spread cash across banks or ownership categories."),
        ],
    },
    "Intel stock: RSUs & ESPP": {
        "formulas": [
            ("RSU income at vest", "Shares vested × price at vest", "Taxed like salary"),
            ("Tax gap at vest", "Vest × (your federal + CA marginal rates − 22% − 10.23%)", "Set the gap aside for April"),
            ("ESPP return", "Market price ÷ (lower of start/end price × (1 − discount)) − 1", "15% discount with no price change ≈ 17.6%"),
            ("Concentration", "Intel holdings ÷ total investments", "Guideline: 10% or less"),
        ],
        "chart": _bar(
            "Tax owed vs withheld on a $100,000 vest (with 9.3% CA)",
            ["22% bracket", "24% bracket", "32% bracket", "35% bracket"],
            [round(rsu_withholding_gap(100_000, r, 0.093)[2]) for r in (0.22, 0.24, 0.32, 0.35)],
            "Extra tax due",
            "Worked example: default withholding is 22% federal + 10.23% CA.",
            x="Your federal bracket",
        ),
        "mistakes": [
            ("Double-paying tax on sold shares", "1099-B often shows $0 basis.", "Use the supplemental statement and Form 3922 on Form 8949."),
            ("Assuming withholding covers it", "Higher brackets owe more in April.", "Use the RSU tax-gap calculator and adjust W-4 or estimates."),
            ("Holding every vest", "Job and savings tied to one company.", "Write a sell schedule and follow it."),
            ("Wash sales from automatic buys", "Losses get disallowed.", "Avoid selling Intel at a loss within 30 days of a vest or ESPP purchase."),
        ],
    },
    "Retirement: 401(k), IRA & Social Security": {
        "formulas": [
            ("Retirement target", "Yearly spending in retirement ÷ withdrawal rate", "$120,000 ÷ 4% = $3,000,000"),
            ("Savings growth", "FV = PV × (1 + r)ⁿ + PMT × ((1 + r)ⁿ − 1) ÷ r", "Used by the retirement calculator"),
            ("Pay per paycheck to max", "(Limit − contributed so far) ÷ paychecks left", "Avoid missing the match on per-paycheck plans"),
        ],
        "chart": _line(
            f"401(k) growth over {_years} years from $150,000 (6% a year)",
            {"Year": list(range(_years + 1)), "Max out ($24,500 + $6,000 employer)": [round(v) for v in _max_401k], "Half ($12,000 + $3,000 employer)": [round(v) for v in _half_401k]},
            "Dollars",
            "Worked example with a constant 6% return; real returns vary. Employer amounts are placeholders.",
        ),
        "chart2": _bar("Social Security: share of full benefit by claiming age (born 1960+)", ["62", "67 (full)", "70"], [70, 100, 124], "% of full benefit", "SSA rules for a full retirement age of 67.", x="Claiming age"),
        "mistakes": [
            ("Missing the full employer contribution", "Free money lost.", "Contribute at least enough for the full match every paycheck."),
            ("Pre-tax IRA balance blocks backdoor Roth", "Pro-rata rule makes conversions taxable.", "Roll old IRAs into the 401(k) first, if the plan allows."),
            ("Old beneficiary forms", "Forms override the will.", "Review beneficiaries every year."),
            ("Claiming Social Security early by default", "Benefit is permanently lower.", "Compare 62, 67 and 70 on my Social Security."),
        ],
    },
    "Investing & net worth": {
        "formulas": [
            ("Net worth", "Assets − liabilities", "Update each quarter"),
            ("Fee drag", "Value × expense ratio each year, compounded", "1% fee can cost ~17% of the ending value over 20 years"),
            ("Rebalance amount", "(Target % − current %) × total portfolio", "Do it once a year or at ±5% drift"),
        ],
        "chart": _bar("$500,000 after 20 years at 6% before fees", ["0.05% fee", "0.5% fee", "1% fee"], [round(v) for v in _fees.values()], "Dollars", "Worked example; returns are not guaranteed.", x="Annual fee"),
        "mistakes": [
            ("Trading on headlines", "Buys high, sells low.", "Automate monthly investing into broad index funds."),
            ("High-fee funds", "Fees compound every year.", "Check expense ratios; prefer low-cost index funds."),
            ("Never rebalancing", "Risk drifts upward after good years.", "Rebalance once a year."),
        ],
    },
    "Taxes: federal & California": {
        "formulas": [
            ("Marginal rate", "Federal bracket rate + CA bracket rate", "24% + 9.3% = 33.3% on the next dollar"),
            ("Effective rate", "Total tax ÷ gross income", "Shown in the take-home calculator"),
            ("Federal safe harbor", "Pay ≥ 110% of last year's tax (AGI > $150k)", "Avoids underpayment penalties"),
        ],
        "chart": _bar("Combined federal 2026 + CA 2025 marginal rate by taxable income", ["$150k", "$250k", "$450k", "$650k", "$900k"], [_combined(x) for x in (150_000, 250_000, 450_000, 650_000, 900_000)], "Marginal rate (%)", "Married filing jointly; excludes FICA, SDI and the 1% CA tax over $1M.", x="Taxable income"),
        "mistakes": [
            ("Under-withholding on RSUs", "Large April bill plus penalties.", "Check withholding in June and September."),
            ("Forgetting CA's uneven estimate schedule", "CA wants 30/40/0/30%.", "Pay 40% of CA estimates in June."),
            ("Not comparing itemizing vs standard", "Missed SALT and mortgage savings.", "Add CA tax + property tax (up to $40,400) + mortgage interest + gifts."),
            ("No IP PIN", "Someone can file in your name.", "Get IRS IP PINs for every family member."),
        ],
    },
    "Insurance": {
        "formulas": [
            ("Life insurance need (DIME)", "Debts + income × years + mortgage + education − existing cover − savings", "Use the life insurance calculator"),
            ("Disability income", "Salary × LTD % (capped) − taxes if premiums were employer-paid", "Check if LTD benefit is taxable"),
        ],
        "chart": _bar("Worked example: DIME life insurance need", ["Debts", "Income (12 yrs × $210k)", "Mortgage", "College", "Minus existing cover + savings"], [20_000, 2_520_000, 800_000, 250_000, -720_000], "Dollars", "Defaults from the life insurance calculator.", x="Part"),
        "mistakes": [
            ("Only employer life insurance", "It usually ends with the job.", "Own a private term policy until your child finishes college."),
            ("No earthquake cover", "Home policies exclude it in California.", "Price a CEA or private earthquake policy."),
            ("Low liability limits", "Lawsuits can reach savings.", "Raise auto/home limits and add a $1–2M umbrella."),
        ],
    },
    "Home & property": {
        "formulas": [
            ("Monthly payment", "P × r ÷ (1 − (1 + r)^−n)", "r = rate ÷ 12, n = months"),
            ("Property tax", "(Assessed value − $7,000) × local rate", "About 1.1–1.25% in many counties"),
            ("Refinance break-even", "Closing costs ÷ monthly savings", "$6,000 ÷ $300 = 20 months"),
        ],
        "chart": _bar("Monthly principal + interest on a $900,000, 30-year loan", ["5%", "6%", "7%"], [round(mortgage_payment(900_000, r, 30)) for r in (5, 6, 7)], "Dollars per month", "Worked example; excludes tax and insurance.", x="Rate"),
        "mistakes": [
            ("No maintenance fund", "Roofs and water heaters fail suddenly.", "Save about 1% of home value a year."),
            ("Missing a property tax installment", "10% penalty.", "Calendar Dec 10 and Apr 10, or use escrow."),
            ("Not filing the homeowners' exemption", "Pay tax on $7,000 more value.", "File once with your county assessor."),
        ],
    },
    "Kid: school, 529 & childcare": {
        "formulas": [
            ("Future college cost", "Cost today × (1 + college inflation)^years", "$160,000 × 1.04⁸ ≈ $219,000"),
            ("Monthly saving needed", "Gap × r ÷ ((1 + r)ⁿ − 1)", "Used by the 529 calculator"),
            ("DCFSA tax saved", "$7,500 × (federal + CA + FICA rate)", "≈ $2,900 at 22% + 9.3% + 7.65%"),
        ],
        "chart": _bar("529 value in 8 years at 6% (starting from $30,000)", ["$300/month", "$600/month", "$1,000/month"], [round(compound_series(30_000, m, 6, 8)[-1]) for m in (300, 600, 1_000)], "Dollars", "Worked example; returns are not guaranteed.", x="Monthly saving"),
        "mistakes": [
            ("Skipping the dependent care FSA", "Loses about $2,900 a year in tax savings.", "Elect it at open enrollment until your child turns 13."),
            ("Using 529 for K-12 in California", "CA tax plus 2.5% penalty.", "Use 529 money only for college in CA."),
            ("Waiting to open a 529", "Less growth; 15-year clock for Roth rollover.", "Open it now, even with a small amount."),
        ],
    },
    "Will, estate & family": {
        "formulas": [
            ("CA statutory probate fee", "4% of first $100k + 3% of next $100k + 2% of next $800k + 1% of next $9M", "Paid to the attorney and again to the executor"),
            ("Estate outside a trust", "Total assets − assets with beneficiaries or in trust", "Above $208,850 usually means probate"),
        ],
        "chart": _bar("California statutory probate fees (attorney + executor)", ["$500k estate", "$1M estate", "$2M estate"], [2 * probate_fee(v) for v in (500_000, 1_000_000, 2_000_000)], "Dollars", "California Probate Code statutory fees, based on gross estate value; a living trust usually avoids them.", x="Estate size"),
        "mistakes": [
            ("No guardian named", "A court decides who raises your child.", "Sign wills naming a guardian and a backup."),
            ("Trust signed but not funded", "Assets still go through probate.", "Retitle the home and accounts into the trust."),
            ("Outdated beneficiaries", "Money goes to the wrong person.", "Review all beneficiary forms yearly."),
        ],
    },
    "Car & commute": {
        "formulas": [
            ("Cost per month", "Payment + insurance + fuel/charging + upkeep + registration ÷ 12", "Compare cars on this, not the payment"),
            ("Commuter tax saving", "$340 × 12 × your combined tax rate", "≈ $1,600 a year at 40%"),
        ],
        "chart": None,
        "mistakes": [
            ("Missing registration or smog", "Late fees and tickets.", "Put DMV and smog dates on the calendar."),
            ("Expecting the federal EV credit", "It ended for cars acquired after 30 Sep 2025.", "Look at utility rebates and charging rates instead."),
            ("Paying commute costs after tax", "Lose about 40% in tax savings.", "Use pre-tax commuter benefits if offered."),
        ],
    },
    "Documents, identity & security": {
        "formulas": [
            ("Accounts with 2FA", "Accounts with 2FA ÷ total key accounts", "Target 100% for email, bank, brokerage, stock plan"),
        ],
        "chart": None,
        "mistakes": [
            ("Child's credit not frozen", "Child identity theft goes unnoticed for years.", "Freeze your child's credit at all three bureaus."),
            ("Reused passwords", "One breach opens many accounts.", "Use a password manager and unique passwords."),
            ("Passport expiry surprise", "Trips get cancelled.", "Check passports 9 months before travel."),
        ],
    },
    "Family emergencies & disasters": {
        "formulas": [
            ("Water to store", "People × days × 1 gallon", "3 × 14 = 42 gallons"),
            ("Food to store", "People × days × meals per day", "3 × 14 × 3 = 126 meals"),
        ],
        "chart": _bar("Gallons of water for a family of 3", ["3 days", "7 days", "14 days"], [9, 21, 42], "Gallons", "Ready.gov: one gallon per person per day.", x="Days"),
        "mistakes": [
            ("No meeting place", "Family can't find each other when phones fail.", "Choose a nearby and an out-of-area meeting place."),
            ("Expired supplies", "Water, food and batteries go bad.", "Check go-bags every spring and fall."),
            ("No alerts on phones", "Warnings arrive too late.", "Install MyShake and sign up for county alerts."),
            ("School contacts out of date", "Child can't be released to you or your helper.", "Update school emergency contacts every August."),
        ],
    },
    "Aging parents & caregiving": {
        "formulas": [
            ("Care hours per week", "Visits × hours + calls + admin time", "Track it to plan leave and help"),
            ("Monthly care cost", "Hours of paid help × hourly rate", "Compare in-home help with adult day programs"),
        ],
        "chart": None,
        "mistakes": [
            ("Waiting for a crisis to talk", "Decisions made in a hurry.", "Hold a yearly family meeting about wishes and money."),
            ("No POA or health directive", "Court process needed to help them.", "Help parents sign both documents."),
            ("Carrying it alone", "Burnout affects work and family.", "Use PFL, the EAP and the Eldercare Locator."),
        ],
    },
}

NEWS_MISTAKES = [
    ("Reading headlines only", "Headlines exaggerate.", "Open the full story before sharing it."),
    ("Trading Intel stock on news", "Short-term moves are noise; you may be in a blackout window.", "Follow your written sell plan instead."),
    ("Sharing internal views in public", "Company confidentiality rules apply.", "Discuss Intel news only through approved channels."),
]

PAGE_MISTAKES = {
    "dashboard": [
        ("Never coming back", "Deadlines pass quietly.", "Add the year planner to your calendar."),
        ("Treating limits as targets you can't reach", "Missed tax savings.", "Use Max your accounts to spread the rest over remaining paychecks."),
    ],
    "cheatsheet": [
        ("Using last year's numbers", "Limits change every year.", "Check the year shown beside each number."),
        ("Copying a rule of thumb as a rule", "Your situation differs.", "Run the calculators with your own numbers."),
    ],
    "sheet": [
        ("Leaving values blank", "You can't act on what you don't know.", "Fill one area a week until every row is done."),
        ("Typing account numbers or passwords", "Sensitive data in a file.", "Record plan values only."),
    ],
    "planner": [
        ("Keeping dates in your head", "Things get missed.", "Download the calendar file."),
        ("Ignoring Intel-specific dates", "Enrollment and vest dates vary by year.", "Add them from the benefits and stock plan sites."),
    ],
    "calculators": [
        ("Trusting one projection", "Returns and taxes change.", "Try low, medium and high assumptions."),
        ("Using gross pay for budgets", "Overestimates what you can spend.", "Budget on take-home pay."),
    ],
    "review": [
        ("Doing the review once", "Life and plans change.", "Repeat it every January."),
        ("Trying to fix everything at once", "Nothing finishes.", "Pick the three lowest areas and fix one per month."),
    ],
    "card": [
        ("Only one copy", "It may not be with you.", "Keep one on each phone, in each car and in the go-bag."),
        ("Outdated medicines", "Doctors act on wrong information.", "Update the card when anything changes."),
    ],
    "about": [
        ("Relying on a summary", "Rules have details and exceptions.", "Open the official source for your decision."),
    ],
}
