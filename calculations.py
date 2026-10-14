"""Transparent, simplified household money math for a California family. Estimates only, not tax advice."""
from datetime import date, timedelta

# Federal tax year 2026, married filing jointly (IRS Rev. Proc. 2025-32).
FED_YEAR = 2026
FED_BRACKETS_MFJ = [
    (24_800, 0.10),
    (100_800, 0.12),
    (211_400, 0.22),
    (403_550, 0.24),
    (512_450, 0.32),
    (768_700, 0.35),
    (float("inf"), 0.37),
]
FED_STANDARD_DEDUCTION_MFJ = 32_200
CHILD_TAX_CREDIT = 2_200
SS_RATE, SS_WAGE_BASE = 0.062, 184_500
MEDICARE_RATE, ADDL_MEDICARE_RATE, ADDL_MEDICARE_THRESHOLD_MFJ = 0.0145, 0.009, 250_000

# California tax year 2025 (latest FTB schedule published when this was written), married filing jointly.
CA_YEAR = 2025
CA_BRACKETS_MFJ = [
    (22_158, 0.01),
    (52_528, 0.02),
    (82_904, 0.04),
    (115_084, 0.06),
    (145_448, 0.08),
    (742_958, 0.093),
    (891_542, 0.103),
    (1_485_906, 0.113),
    (float("inf"), 0.123),
]
CA_STANDARD_DEDUCTION_MFJ = 11_412
CA_MENTAL_HEALTH_RATE, CA_MENTAL_HEALTH_THRESHOLD = 0.01, 1_000_000
CA_SDI_RATE = 0.013  # 2026, no wage cap

# Withholding on bonuses and stock vests (supplemental wages).
FED_SUPPLEMENTAL_RATE, FED_SUPPLEMENTAL_RATE_OVER_1M = 0.22, 0.37
CA_SUPPLEMENTAL_STOCK_RATE = 0.1023

# 2026 account limits.
LIMITS_2026 = {
    "401(k) employee deferral": 24_500,
    "401(k) catch-up, age 50+": 8_000,
    "401(k) total incl. employer and after-tax": 72_000,
    "IRA (each spouse)": 7_500,
    "HSA family": 8_750,
    "HSA self-only": 4_400,
    "Health FSA": 3_400,
    "Dependent care FSA (per household)": 7_500,
    "Annual gift exclusion (per recipient)": 19_000,
}


def progressive_tax(taxable, brackets):
    """Tax on taxable income using (upper bound, rate) brackets."""
    tax, lower = 0.0, 0.0
    for upper, rate in brackets:
        if taxable <= lower:
            break
        tax += (min(taxable, upper) - lower) * rate
        lower = upper
    return tax


def marginal_rate(taxable, brackets):
    for upper, rate in brackets:
        if taxable <= upper:
            return rate
    return brackets[-1][1]


def take_home(gross, pretax_401k=0.0, hsa=0.0, health_fsa=0.0, dependent_care_fsa=0.0, premiums=0.0, children=1):
    """Annual paycheck estimate for a married couple filing jointly in California with one earner.

    401(k) deferrals reduce income tax but not FICA. HSA, FSAs and medical premiums paid through
    a cafeteria plan reduce income tax and FICA, except California taxes HSA contributions.
    Ignores itemized deductions, other credits, AMT and spouse income.
    """
    cafeteria = hsa + health_fsa + dependent_care_fsa + premiums
    fica_wages = max(0.0, gross - cafeteria)
    fed_taxable = max(0.0, gross - pretax_401k - cafeteria - FED_STANDARD_DEDUCTION_MFJ)
    fed = max(0.0, progressive_tax(fed_taxable, FED_BRACKETS_MFJ) - CHILD_TAX_CREDIT * children)
    social_security = SS_RATE * min(fica_wages, SS_WAGE_BASE)
    medicare = MEDICARE_RATE * fica_wages + ADDL_MEDICARE_RATE * max(0.0, fica_wages - ADDL_MEDICARE_THRESHOLD_MFJ)
    ca_taxable = max(0.0, gross - pretax_401k - (cafeteria - hsa) - CA_STANDARD_DEDUCTION_MFJ)
    ca = progressive_tax(ca_taxable, CA_BRACKETS_MFJ)
    ca += CA_MENTAL_HEALTH_RATE * max(0.0, ca_taxable - CA_MENTAL_HEALTH_THRESHOLD)
    sdi = CA_SDI_RATE * fica_wages
    taxes = fed + social_security + medicare + ca + sdi
    net = gross - pretax_401k - cafeteria - taxes
    return {
        "Federal income tax": fed,
        "Social Security": social_security,
        "Medicare": medicare,
        "California income tax": ca,
        "CA SDI": sdi,
        "Total taxes": taxes,
        "Take-home pay": net,
        "Federal marginal rate": marginal_rate(fed_taxable, FED_BRACKETS_MFJ),
        "California marginal rate": marginal_rate(ca_taxable, CA_BRACKETS_MFJ),
        "Effective tax rate": taxes / gross if gross > 0 else 0.0,
    }


def rsu_withholding_gap(vest_value, fed_marginal, ca_marginal, ytd_supplemental=0.0):
    """Extra tax likely owed at filing because vests are withheld at flat supplemental rates.

    Returns (withheld, likely_owed, gap). Medicare and SDI are ignored; they are withheld in full.
    """
    under_1m = max(0.0, min(vest_value, 1_000_000 - ytd_supplemental))
    withheld = under_1m * FED_SUPPLEMENTAL_RATE + (vest_value - under_1m) * FED_SUPPLEMENTAL_RATE_OVER_1M
    withheld += vest_value * CA_SUPPLEMENTAL_STOCK_RATE
    owed = vest_value * (fed_marginal + ca_marginal)
    return withheld, owed, owed - withheld


def espp_purchase(contribution, offer_price, purchase_price_market, discount_percent=15.0, lookback=True):
    """Shares bought and the immediate discount gain for an ESPP purchase.

    With a lookback the price is the discount applied to the lower of the offering-date and
    purchase-date prices. Returns (price_paid, shares, market_value, gain, return_percent).
    """
    base = min(offer_price, purchase_price_market) if lookback else purchase_price_market
    price = base * (1 - discount_percent / 100)
    if price <= 0 or contribution <= 0:
        return price, 0.0, 0.0, 0.0, 0.0
    shares = contribution / price
    value = shares * purchase_price_market
    gain = value - contribution
    return price, shares, value, gain, 100 * gain / contribution


def reserve_months(liquid_cash, essential_monthly):
    if essential_monthly <= 0:
        return None
    return liquid_cash / essential_monthly


def life_insurance_need(annual_income, years_to_replace, debts, mortgage, college, final_costs, existing_cover, savings):
    """DIME-style estimate: debts + income replacement + mortgage + education, minus resources already in place."""
    need = debts + annual_income * years_to_replace + mortgage + college + final_costs
    return max(0.0, need - existing_cover - savings)


def compound_series(initial, monthly, annual_return_percent, years):
    """Year-end values with end-of-month contributions and a constant effective annual return."""
    rate = (1 + annual_return_percent / 100) ** (1 / 12) - 1
    value = float(initial)
    values = [value]
    for month in range(1, int(years * 12) + 1):
        value = value * (1 + rate) + monthly
        if month % 12 == 0:
            values.append(value)
    return values


def future_cost(cost_today, inflation_percent, years):
    return cost_today * (1 + inflation_percent / 100) ** years


def real_value(nominal, inflation_percent, years):
    return nominal / (1 + inflation_percent / 100) ** years


def mortgage_payment(principal, annual_rate_percent, years):
    """Monthly principal and interest for a fixed-rate loan."""
    n = int(years * 12)
    if principal <= 0 or n <= 0:
        return 0.0
    r = annual_rate_percent / 1200
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)


def plan_cost(premiums, deductible, coinsurance_percent, oop_max, spending, employer_hsa=0.0):
    """Yearly cost of a medical plan: premiums plus what you pay for care, minus employer HSA money.

    You pay all spending up to the deductible, then the coinsurance share, capped at the out-of-pocket maximum.
    """
    covered = min(spending, deductible) + max(0.0, spending - deductible) * coinsurance_percent / 100
    return premiums + min(covered, oop_max) - employer_hsa


def probate_fee(estate):
    """California statutory probate fee for the attorney (the executor gets the same again)."""
    tiers = [(100_000, 0.04), (100_000, 0.03), (800_000, 0.02), (9_000_000, 0.01), (15_000_000, 0.005)]
    fee, left = 0.0, estate
    for size, rate in tiers:
        part = min(left, size)
        fee += part * rate
        left -= part
        if left <= 0:
            break
    return fee


def concentration(holding, total):
    return 100 * holding / total if total > 0 else None


def account_gaps(contributions, limits=LIMITS_2026):
    """Rows of (account, limit, contributing, room left) for the accounts the user entered."""
    return [(name, limits[name], amount, max(0.0, limits[name] - amount)) for name, amount in contributions.items()]


def upcoming(dates, today, days=60):
    """Yearly (month, day, icon, title, topic) reminders falling within the next `days`, soonest first."""
    items = []
    for month, day, icon, title, topic in dates:
        when = date(today.year, month, day)
        if when < today:
            when = date(today.year + 1, month, day)
        if (when - today).days <= days:
            items.append((when, icon, title, topic))
    return sorted(items)


def build_ics(events, name="Intel MyBen"):
    """A calendar file of yearly all-day reminders; events are (date, title)."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//{name}//EN", "CALSCALE:GREGORIAN"]
    for i, (when, title) in enumerate(events):
        title = title.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
        lines += [
            "BEGIN:VEVENT",
            f"UID:intel-myben-{i}-{when:%m%d}@intel-myben",
            "DTSTAMP:20260101T000000Z",
            f"DTSTART;VALUE=DATE:{when:%Y%m%d}",
            f"DTEND;VALUE=DATE:{when + timedelta(days=1):%Y%m%d}",
            "RRULE:FREQ=YEARLY",
            f"SUMMARY:{title}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
