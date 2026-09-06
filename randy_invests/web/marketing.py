"""Demo marketing, advertising, and YouTube-channel content for the portal."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VideoEpisode:
    slug: str
    title: str
    duration: str
    playlist: str
    summary: str
    cta_path: str
    cta_label: str


@dataclass(frozen=True)
class Playlist:
    name: str
    blurb: str
    episode_count: int


@dataclass(frozen=True)
class MarketChannel:
    name: str
    audience: str
    why_it_works: str
    first_move: str
    href: str
    href_label: str


@dataclass(frozen=True)
class AdSnippet:
    surface: str
    headline: str
    body: str
    destination: str


@dataclass
class PartnerInquiry:
    name: str
    email: str
    organization: str
    channel: str
    message: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


CHANNEL_HANDLE = "@RandyInvests"
CHANNEL_NAME = "Randy Invests"
PARTNER_CHANNELS = (
    "youtube",
    "newsletter",
    "investment-club",
    "podcast",
    "employer-education",
    "other",
)

EPISODES: tuple[VideoEpisode, ...] = (
    VideoEpisode(
        slug="kitchen-table-10q",
        title="How I read a 10-Q at the kitchen table",
        duration="12:40",
        playlist="Start here",
        summary=(
            "Randy walks through one filing the way a retail investor actually would — "
            "coffee, a yellow pad, and no trading-floor jargon."
        ),
        cta_path="learn",
        cta_label="Read the desk notes",
    ),
    VideoEpisode(
        slug="bronze-vs-silver",
        title="Bronze vs Silver: what $1,000 and $10,000 sleeves buy",
        duration="09:15",
        playlist="Compare the tiers",
        summary=(
            "A plain comparison of the two retail entry programs — minimums, fees, "
            "and what access actually changes. Illustrative, not a recommendation."
        ),
        cta_path="tiers_index",
        cta_label="Open the comparison",
    ),
    VideoEpisode(
        slug="hold-periods",
        title="Why hold periods exist (and when they shouldn't scare you)",
        duration="08:02",
        playlist="Compare the tiers",
        summary=(
            "Liquidity windows in everyday language, including the 30- and 90-day "
            "notes on Silver and Gold."
        ),
        cta_path="tiers_index",
        cta_label="See hold notes by tier",
    ),
    VideoEpisode(
        slug="ml-not-crystal-ball",
        title="ML signals are not crystal balls",
        duration="14:18",
        playlist="Research desk",
        summary=(
            "How the Randy Invests ensemble is trained, what a BUY/HOLD/SELL label "
            "is allowed to mean, and what it must never claim."
        ),
        cta_path="learn",
        cta_label="How the research desk works",
    ),
    VideoEpisode(
        slug="fees-plain-english",
        title="Fees in plain English",
        duration="07:33",
        playlist="Start here",
        summary=(
            "Annual program fees versus brokerage costs, with the four-tier schedule "
            "on one whiteboard."
        ),
        cta_path="tiers_index",
        cta_label="Compare fees",
    ),
)

PLAYLISTS: tuple[Playlist, ...] = (
    Playlist("Start here", "Short, neighborly explainers for first-time viewers.", 2),
    Playlist("Compare the tiers", "Bronze through Platinum, side by side on camera.", 2),
    Playlist("Research desk", "How the CLI models work — and their limits.", 1),
)

MARKET_CHANNELS: tuple[MarketChannel, ...] = (
    MarketChannel(
        name="YouTube education series",
        audience="Retail investors who learn by watching, not by pitch decks",
        why_it_works=(
            "Owned channel with a recognizable face. Episodes send people to /tiers "
            "instead of selling a security on camera."
        ),
        first_move="Publish the Start-here playlist and pin the comparison link.",
        href="channel",
        href_label="Open the channel page",
    ),
    MarketChannel(
        name="Comparison-page SEO",
        audience="People searching for retail minimums, fees, and share-class style tiers",
        why_it_works="/tiers is the product. Rank for 'compare investment access tiers'.",
        first_move="Keep /tiers public, fast, and honest about illustrative figures.",
        href="tiers_index",
        href_label="View /tiers",
    ),
    MarketChannel(
        name="Local investment clubs",
        audience="Middle-class households who already meet to talk 529s, IRAs, and watchlists",
        why_it_works="Randy is cast as a peer, not a closer. Clubs can share the media kit.",
        first_move="Offer a 20-minute 'how to read our fee table' talk with no performance claims.",
        href="advertise_get",
        href_label="Partner notes",
    ),
    MarketChannel(
        name="Partner newsletters",
        audience="Existing personal-finance writers and workplace-education lists",
        why_it_works="Borrowed trust, if the copy stays educational and links to /tiers.",
        first_move="Hand them the ready-to-run snippets on this page.",
        href="advertise_get",
        href_label="Copy the snippets",
    ),
    MarketChannel(
        name="Shareable UTM cards",
        audience="Anyone who already trusts you offline",
        why_it_works="A clean URL with a source tag shows which conversations convert to interest.",
        first_move="Share /tiers?utm_source=club&utm_medium=share from a meeting.",
        href="tiers_index",
        href_label="Copy a tracked link",
    ),
)

AD_SNIPPETS: tuple[AdSnippet, ...] = (
    AdSnippet(
        surface="YouTube description",
        headline="Compare the four retail access tiers",
        body=(
            "Bronze, Silver, Gold, and Platinum — minimums, fees, hold windows, and "
            "what you actually get. Illustrative figures only. Not an offer or advice. "
            "Start at the comparison page."
        ),
        destination="/tiers",
    ),
    AdSnippet(
        surface="Email / newsletter",
        headline="A kitchen-table read on investment access",
        body=(
            "If you have been looking for a retail-sized way to understand program "
            "minimums without a sales call, Randy Invests publishes the four tiers in "
            "one view. No payment on the demo desk."
        ),
        destination="/tiers",
    ),
    AdSnippet(
        surface="Investment-club flyer",
        headline="Bring the fee table, not a hot tip",
        body=(
            "This month: walk through Bronze–Platinum together. Print the comparison. "
            "Ask hard questions about holds and eligibility. Then decide at home."
        ),
        destination="/tiers",
    ),
    AdSnippet(
        surface="Short social post",
        headline="Four tiers. Plain numbers.",
        body=(
            "Randy Invests put Bronze / Silver / Gold / Platinum on one page — "
            "minimums starting at $1,000. Illustrative, not advice."
        ),
        destination="/tiers",
    ),
)

SHARE_LINKS: tuple[dict[str, str], ...] = (
    {
        "label": "YouTube video description",
        "path": "/tiers?utm_source=youtube&utm_medium=video&utm_campaign=channel",
    },
    {
        "label": "Investment club",
        "path": "/tiers?utm_source=club&utm_medium=share&utm_campaign=retail",
    },
    {
        "label": "Newsletter",
        "path": "/tiers?utm_source=newsletter&utm_medium=email&utm_campaign=compare",
    },
    {
        "label": "Channel home",
        "path": "/channel?utm_source=share&utm_medium=social&utm_campaign=randy",
    },
)


def get_episodes() -> tuple[VideoEpisode, ...]:
    return EPISODES


def get_playlists() -> tuple[Playlist, ...]:
    return PLAYLISTS


def get_market_channels() -> tuple[MarketChannel, ...]:
    return MARKET_CHANNELS


def get_ad_snippets() -> tuple[AdSnippet, ...]:
    return AD_SNIPPETS


def get_share_links() -> tuple[dict[str, str], ...]:
    return SHARE_LINKS


def parse_partner_form(form: dict) -> PartnerInquiry:
    """Validate a mocked advertising-partner inquiry."""
    name = (form.get("name") or "").strip()
    email = (form.get("email") or "").strip()
    organization = (form.get("organization") or "").strip()
    channel = (form.get("channel") or "").strip().lower()
    message = (form.get("message") or "").strip()

    errors: list[str] = []
    if len(name) < 2 or len(name) > 80:
        errors.append("Please enter a contact name (2–80 characters).")
    if "@" not in email or "." not in email.split("@")[-1] or len(email) > 120:
        errors.append("Please enter a valid email address.")
    if len(organization) < 2 or len(organization) > 120:
        errors.append("Please enter your club, channel, or organization.")
    if channel not in PARTNER_CHANNELS:
        errors.append("Please choose how you would reach retail investors.")
    if len(message) > 1000:
        errors.append("Notes must be 1,000 characters or fewer.")

    return PartnerInquiry(
        name=name,
        email=email,
        organization=organization,
        channel=channel,
        message=message,
        errors=errors,
    )
