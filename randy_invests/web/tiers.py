"""Demo investment-tier catalogue for the retail investor portal.

The figures below are hardcoded demonstration data — not a live offering.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InvestmentTier:
    """A single retail investment access tier."""

    slug: str
    name: str
    metal: str
    tagline: str
    audience: str
    minimum_usd: int
    annual_fee_pct: float
    hold_period: str
    liquidity_note: str
    eligibility: str
    benefits: tuple[str, ...]
    access: tuple[str, ...]
    featured: bool = False
    cta_label: str = "Express interest"

    def format_minimum(self) -> str:
        return f"${self.minimum_usd:,.0f}"

    def format_fee(self) -> str:
        return f"{self.annual_fee_pct:.2f}%"


COMPARISON_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "minimum",
        "label": "Minimum investment",
        "help": "Illustrative initial commitment to open the program.",
    },
    {
        "id": "fee",
        "label": "Annual program fee",
        "help": "Charged on assets in the program. Brokerage costs may apply separately.",
    },
    {
        "id": "hold",
        "label": "Hold / liquidity",
        "help": "Soft window before routine withdrawals. Hardship exceptions are reviewed case by case.",
    },
    {
        "id": "signals",
        "label": "ML research access",
        "help": "Universe size and freshness of Randy Invests model signals.",
    },
    {
        "id": "support",
        "label": "Human support",
        "help": "Who you can reach, and how often.",
    },
    {
        "id": "reviews",
        "label": "Reviews & reporting",
        "help": "Cadence of written updates and live check-ins.",
    },
    {
        "id": "eligibility",
        "label": "Eligibility notes",
        "help": "Retail-focused gates. Additional KYC/AML always applies.",
    },
)


# Seeded catalogue. Order is lowest minimum → highest.
TIERS: tuple[InvestmentTier, ...] = (
    InvestmentTier(
        slug="bronze",
        name="Bronze",
        metal="bronze",
        tagline="Start a research-backed habit with a retail-sized commitment.",
        audience="New and returning self-directed investors",
        minimum_usd=1_000,
        annual_fee_pct=0.75,
        hold_period="No lock-up",
        liquidity_note="Withdrawals typically settle in 3–5 business days.",
        eligibility=(
            "U.S. residents 18+ with a completed suitability questionnaire. "
            "Accredited-investor status is not required."
        ),
        benefits=(
            "Weekly market digest written for retail readers",
            "Guided watchlist of up to 10 tickers",
            "Access to the Randy Invests education academy",
            "Email alerts when a watched name triggers a model signal",
        ),
        access=(
            "Delayed quotes and educational ML recaps",
            "Starter universe of widely held U.S. large-caps",
            "Self-serve help center",
        ),
    ),
    InvestmentTier(
        slug="silver",
        name="Silver",
        metal="silver",
        tagline="More of the model, more of the book — still built for retail accounts.",
        audience="Active retail investors building a core sleeve",
        minimum_usd=10_000,
        annual_fee_pct=0.55,
        hold_period="30-day notice",
        liquidity_note="Routine redemptions after 30 days' notice; cash typically in 5–7 business days.",
        eligibility=(
            "U.S. residents 18+ who complete KYC and a risk-tolerance review. "
            "Joint and IRA registrations are accepted in the demo flow."
        ),
        benefits=(
            "Full technical-pattern library (crosses, squeezes, RSI regimes)",
            "Watchlist of up to 50 tickers with same-session alerts",
            "Monthly written portfolio commentary",
            "Tax-lot style activity export (illustrative CSV)",
        ),
        access=(
            "Near-real-time quotes during U.S. cash-session hours",
            "ML ensemble buy/hold/sell labels on the Silver universe",
            "In-app chat with the research desk (business days)",
        ),
    ),
    InvestmentTier(
        slug="gold",
        name="Gold",
        metal="gold",
        tagline="A high-touch retail program with a named research liaison.",
        audience="Households concentrating a larger taxable or retirement sleeve",
        minimum_usd=50_000,
        annual_fee_pct=0.40,
        hold_period="90-day soft hold",
        liquidity_note="Initial 90-day window; thereafter quarterly liquidity with 15 days' notice.",
        eligibility=(
            "Suitability and concentrated-position review required. "
            "Available to retail clients; not limited to accredited investors."
        ),
        benefits=(
            "Named research liaison and a quarterly strategy conversation",
            "Custom watchlists and sector overlays",
            "Priority publication of model changes",
            "Household-level reporting across linked accounts",
        ),
        access=(
            "Full Randy Invests ML suite on an expanded equity universe",
            "Optional options-education module (no options trading advice)",
            "Priority email and scheduled video review",
        ),
        featured=True,
        cta_label="Start Gold review",
    ),
    InvestmentTier(
        slug="platinum",
        name="Platinum",
        metal="platinum",
        tagline="Private-client cadence for larger retail and family pools.",
        audience="Private-client households and multi-account families",
        minimum_usd=250_000,
        annual_fee_pct=0.25,
        hold_period="180-day initial hold",
        liquidity_note="Initial commitment has a 180-day illustrative hold; later windows are semi-annual.",
        eligibility=(
            "Enhanced KYC. May be offered to accredited or qualified clients "
            "after a suitability determination. Not a hedge-fund or 3(c)(7) product."
        ),
        benefits=(
            "Dedicated analyst and a weekly written briefing",
            "Custom model constraints (exclusions, factor tilts) on request",
            "Family-office style consolidated reporting",
            "Invitation-only research calls with the model team",
        ),
        access=(
            "Uncapped ticker universe within supported U.S. listed equities",
            "Custom research memos on names you already hold",
            "Direct scheduling with the private-client desk",
        ),
        cta_label="Request a private-client conversation",
    ),
)

_TIERS_BY_SLUG = {tier.slug: tier for tier in TIERS}


def get_tiers() -> tuple[InvestmentTier, ...]:
    """Return the seeded catalogue in display order."""
    return TIERS


def get_tier(slug: str) -> InvestmentTier | None:
    """Look up a tier by URL slug, or ``None`` if unknown."""
    return _TIERS_BY_SLUG.get((slug or "").strip().lower())


def recommend_tier(amount_usd: float) -> InvestmentTier:
    """Return the highest tier whose minimum is at or below *amount_usd*.

    Amounts below Bronze still recommend Bronze as the entry path.
    """
    eligible = [tier for tier in TIERS if amount_usd >= tier.minimum_usd]
    if not eligible:
        return TIERS[0]
    return eligible[-1]


def comparison_matrix() -> list[dict]:
    """Build a label + per-tier value grid for the comparison table."""
    values: dict[str, dict[str, str]] = {tier.slug: {} for tier in TIERS}
    signals = {
        "bronze": "Educational recaps · 10 names",
        "silver": "Live session labels · 50 names",
        "gold": "Full ML suite · expanded book",
        "platinum": "Custom universe · dedicated memos",
    }
    support = {
        "bronze": "Help center",
        "silver": "Research-desk chat",
        "gold": "Named liaison",
        "platinum": "Dedicated analyst",
    }
    reviews = {
        "bronze": "Weekly digest",
        "silver": "Monthly commentary",
        "gold": "Quarterly live review",
        "platinum": "Weekly briefing",
    }
    for tier in TIERS:
        values[tier.slug] = {
            "minimum": tier.format_minimum(),
            "fee": f"{tier.format_fee()} / year",
            "hold": tier.hold_period,
            "signals": signals[tier.slug],
            "support": support[tier.slug],
            "reviews": reviews[tier.slug],
            "eligibility": _eligibility_short(tier),
        }

    rows = []
    for spec in COMPARISON_ROWS:
        rows.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "help": spec["help"],
                "values": {slug: values[slug][spec["id"]] for slug in values},
            }
        )
    return rows


def _eligibility_short(tier: InvestmentTier) -> str:
    if tier.slug == "bronze":
        return "18+ U.S. · suitability form"
    if tier.slug == "silver":
        return "KYC + risk review"
    if tier.slug == "gold":
        return "Retail + concentration review"
    return "Enhanced KYC · suitability"


@dataclass
class InterestInquiry:
    """A mocked 'express interest' submission (no payment, no persistence)."""

    name: str
    email: str
    tier_slug: str
    intended_amount: int | None = None
    message: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_interest_form(form: dict) -> InterestInquiry:
    """Validate a posted interest form. Does not persist or charge anything."""
    name = (form.get("name") or "").strip()
    email = (form.get("email") or "").strip()
    tier_slug = (form.get("tier") or "").strip().lower()
    message = (form.get("message") or "").strip()
    raw_amount = (form.get("amount") or "").strip().replace(",", "").replace("$", "")

    errors: list[str] = []
    if len(name) < 2 or len(name) > 80:
        errors.append("Please enter your name (2–80 characters).")
    if "@" not in email or "." not in email.split("@")[-1] or len(email) > 120:
        errors.append("Please enter a valid email address.")
    if get_tier(tier_slug) is None:
        errors.append("Please choose an investment tier.")
    if len(message) > 1000:
        errors.append("Notes must be 1,000 characters or fewer.")

    intended_amount: int | None = None
    if raw_amount:
        try:
            intended_amount = int(float(raw_amount))
            if intended_amount < 0:
                raise ValueError
        except ValueError:
            errors.append("Intended amount must be a positive number, or left blank.")
            intended_amount = None

    return InterestInquiry(
        name=name,
        email=email,
        tier_slug=tier_slug,
        intended_amount=intended_amount,
        message=message,
        errors=errors,
    )
