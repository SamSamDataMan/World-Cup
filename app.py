from __future__ import annotations

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st


EASTERN = ZoneInfo("America/New_York")
FIXTURE_SOURCE_URL = "https://www.fourfourtwo.com/competition/world-cup-2026-fixtures-and-results"
TV_SOURCE_URL = "https://www.sbnation.com/soccer/1117513/world-cup-schedule-2026-how-to-watch-every-match-scores-and-more"

POOL_DRAW = {
    "Sam": [
        "Mexico",
        "Qatar",
        "Brazil",
        "United States",
        "Ivory Coast",
        "Netherlands",
        "Belgium",
        "Cape Verde",
        "Jordan",
        "England",
    ],
    "Rob": [
        "Switzerland",
        "Morocco",
        "Turkey",
        "Curacao",
        "Iran",
        "Uruguay",
        "Senegal",
        "Argentina",
        "Portugal",
    ],
    "Jerry": [
        "South Korea",
        "Scotland",
        "Paraguay",
        "Ecuador",
        "Tunisia",
        "New Zealand",
        "Spain",
        "Iraq",
        "DR Congo",
        "Croatia",
    ],
    "David": [
        "Czechia",
        "Canada",
        "Haiti",
        "Sweden",
        "Egypt",
        "France",
        "Algeria",
        "Colombia",
        "Panama",
    ],
    "Steve": [
        "South Africa",
        "Bosnia and Herzegovina",
        "Australia",
        "Germany",
        "Japan",
        "Saudi Arabia",
        "Norway",
        "Austria",
        "Uzbekistan",
        "Ghana",
    ],
}

OWNER_BY_TEAM = {
    team: owner for owner, teams in POOL_DRAW.items() for team in teams
}

SCHEDULE = [
    ("2026-06-11", "15:00", "A", "Mexico", "South Africa", "FOX"),
    ("2026-06-11", "22:00", "A", "South Korea", "Czechia", "FS1"),
    ("2026-06-12", "15:00", "B", "Canada", "Bosnia and Herzegovina", "FOX"),
    ("2026-06-12", "21:00", "D", "United States", "Paraguay", "FOX"),
    ("2026-06-13", "15:00", "B", "Qatar", "Switzerland", "FOX"),
    ("2026-06-13", "18:00", "C", "Brazil", "Morocco", "FOX"),
    ("2026-06-13", "21:00", "C", "Haiti", "Scotland", "FOX"),
    ("2026-06-14", "00:00", "D", "Australia", "Turkey", "FS1"),
    ("2026-06-14", "13:00", "E", "Germany", "Curacao", "FOX"),
    ("2026-06-14", "16:00", "F", "Netherlands", "Japan", "FOX"),
    ("2026-06-14", "19:00", "E", "Ivory Coast", "Ecuador", "FS1"),
    ("2026-06-14", "22:00", "F", "Sweden", "Tunisia", "FS1"),
    ("2026-06-15", "12:00", "H", "Spain", "Cape Verde", "FOX"),
    ("2026-06-15", "15:00", "G", "Belgium", "Egypt", "FOX"),
    ("2026-06-15", "18:00", "H", "Saudi Arabia", "Uruguay", "FS1"),
    ("2026-06-15", "21:00", "G", "Iran", "New Zealand", "FS1"),
    ("2026-06-16", "15:00", "I", "France", "Senegal", "FOX"),
    ("2026-06-16", "18:00", "I", "Iraq", "Norway", "FOX"),
    ("2026-06-16", "21:00", "J", "Argentina", "Algeria", "FOX"),
    ("2026-06-17", "00:00", "J", "Austria", "Jordan", "FS1"),
    ("2026-06-17", "13:00", "K", "Portugal", "DR Congo", "FOX"),
    ("2026-06-17", "16:00", "L", "England", "Croatia", "FOX"),
    ("2026-06-17", "19:00", "L", "Ghana", "Panama", "FS1"),
    ("2026-06-17", "22:00", "K", "Uzbekistan", "Colombia", "FS1"),
    ("2026-06-18", "12:00", "A", "Czechia", "South Africa", "FOX"),
    ("2026-06-18", "15:00", "B", "Switzerland", "Bosnia and Herzegovina", "FOX"),
    ("2026-06-18", "18:00", "B", "Canada", "Qatar", "FS1"),
    ("2026-06-18", "21:00", "A", "Mexico", "South Korea", "FOX"),
    ("2026-06-19", "15:00", "D", "United States", "Australia", "FOX"),
    ("2026-06-19", "18:00", "C", "Scotland", "Morocco", "FOX"),
    ("2026-06-19", "21:00", "C", "Brazil", "Haiti", "FOX"),
    ("2026-06-19", "23:00", "D", "Turkey", "Paraguay", "FS1"),
    ("2026-06-20", "13:00", "F", "Netherlands", "Sweden", "FOX"),
    ("2026-06-20", "16:00", "E", "Germany", "Ivory Coast", "FOX"),
    ("2026-06-20", "20:00", "E", "Ecuador", "Curacao", "FS1"),
    ("2026-06-21", "00:00", "F", "Tunisia", "Japan", "FS1"),
    ("2026-06-21", "12:00", "H", "Spain", "Saudi Arabia", "FOX"),
    ("2026-06-21", "15:00", "G", "Belgium", "Iran", "FS1"),
    ("2026-06-21", "18:00", "H", "Uruguay", "Cape Verde", "FS1"),
    ("2026-06-21", "21:00", "G", "New Zealand", "Egypt", "FS1"),
    ("2026-06-22", "13:00", "J", "Argentina", "Austria", "FOX"),
    ("2026-06-22", "17:00", "I", "France", "Iraq", "FOX"),
    ("2026-06-22", "20:00", "I", "Norway", "Senegal", "FOX"),
    ("2026-06-22", "23:00", "J", "Jordan", "Algeria", "FS1"),
    ("2026-06-23", "13:00", "K", "Portugal", "Uzbekistan", "FOX"),
    ("2026-06-23", "16:00", "L", "England", "Ghana", "FOX"),
    ("2026-06-23", "19:00", "L", "Panama", "Croatia", "FOX"),
    ("2026-06-23", "22:00", "K", "Colombia", "DR Congo", "FS1"),
    ("2026-06-24", "15:00", "B", "Switzerland", "Canada", "FOX"),
    ("2026-06-24", "15:00", "B", "Bosnia and Herzegovina", "Qatar", "FS1"),
    ("2026-06-24", "18:00", "C", "Morocco", "Haiti", "FS1"),
    ("2026-06-24", "18:00", "C", "Scotland", "Brazil", "FOX"),
    ("2026-06-24", "21:00", "A", "South Africa", "South Korea", "FS1"),
    ("2026-06-24", "21:00", "A", "Czechia", "Mexico", "FOX"),
    ("2026-06-25", "16:00", "E", "Curacao", "Ivory Coast", "FS1"),
    ("2026-06-25", "16:00", "E", "Ecuador", "Germany", "FOX"),
    ("2026-06-25", "19:00", "F", "Tunisia", "Netherlands", "FOX"),
    ("2026-06-25", "19:00", "F", "Japan", "Sweden", "FS1"),
    ("2026-06-25", "22:00", "D", "Turkey", "United States", "FOX"),
    ("2026-06-25", "22:00", "D", "Paraguay", "Australia", "FS1"),
    ("2026-06-26", "15:00", "I", "Norway", "France", "FOX"),
    ("2026-06-26", "15:00", "I", "Senegal", "Iraq", "FS1"),
    ("2026-06-26", "20:00", "H", "Cape Verde", "Saudi Arabia", "FS1"),
    ("2026-06-26", "20:00", "H", "Uruguay", "Spain", "FOX"),
    ("2026-06-26", "23:00", "G", "New Zealand", "Belgium", "FOX"),
    ("2026-06-26", "23:00", "G", "Egypt", "Iran", "FS1"),
    ("2026-06-27", "17:00", "L", "Panama", "England", "FOX"),
    ("2026-06-27", "17:00", "L", "Croatia", "Ghana", "FS1"),
    ("2026-06-27", "19:30", "K", "Colombia", "Portugal", "FOX"),
    ("2026-06-27", "19:30", "K", "DR Congo", "Uzbekistan", "FS1"),
    ("2026-06-27", "22:00", "J", "Algeria", "Austria", "FS1"),
    ("2026-06-27", "22:00", "J", "Jordan", "Argentina", "FOX"),
]


def kickoff_at(date_text: str, time_text: str) -> datetime:
    return datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M").replace(
        tzinfo=EASTERN
    )


def format_kickoff(kickoff: datetime) -> str:
    hour = kickoff.hour % 12 or 12
    am_pm = "AM" if kickoff.hour < 12 else "PM"
    return f"{kickoff:%a}, {kickoff:%b} {kickoff.day} at {hour}:{kickoff.minute:02d} {am_pm} ET"


def format_day(kickoff: datetime) -> str:
    return f"{kickoff:%A}, {kickoff:%B} {kickoff.day}"


def format_time(kickoff: datetime) -> str:
    hour = kickoff.hour % 12 or 12
    am_pm = "AM" if kickoff.hour < 12 else "PM"
    return f"{hour}:{kickoff.minute:02d} {am_pm} ET"


def owner(team: str) -> str:
    return OWNER_BY_TEAM.get(team, "Unclaimed")


def team_badge(team: str) -> str:
    return f"{escape(team)} <span>{escape(owner(team))}</span>"


def group_play_record(team: str) -> str:
    return "0-0-0"


def build_matches() -> list[dict[str, object]]:
    matches = []
    for index, (date_text, time_text, group, team_a, team_b, tv) in enumerate(
        SCHEDULE, start=1
    ):
        kickoff = kickoff_at(date_text, time_text)
        owner_a = owner(team_a)
        owner_b = owner(team_b)
        matches.append(
            {
                "match_no": index,
                "kickoff": kickoff,
                "date": kickoff.date(),
                "group": group,
                "team_a": team_a,
                "team_b": team_b,
                "owner_a": owner_a,
                "owner_b": owner_b,
                "tv": tv,
                "owners": {owner_a, owner_b},
                "teams": {team_a, team_b},
            }
        )
    return matches


def build_groups(matches: list[dict[str, object]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for match in matches:
        group = str(match["group"])
        groups.setdefault(group, [])
        for team in (str(match["team_a"]), str(match["team_b"])):
            if team not in groups[group]:
                groups[group].append(team)
    return dict(sorted(groups.items()))


def group_matches_by_day(
    matches: list[dict[str, object]]
) -> list[tuple[object, list[dict[str, object]]]]:
    matches_by_day = {}
    for match in matches:
        matches_by_day.setdefault(match["date"], []).append(match)

    return [
        (match_day, sorted(day_matches, key=lambda match: match["kickoff"]))
        for match_day, day_matches in sorted(matches_by_day.items())
    ]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=Fraunces:opsz,wght@9..144,700&display=swap');

        :root {
            --pitch: #0f3d2e;
            --ink: #10231c;
            --lime: #d6ff79;
            --sand: #fff7df;
            --coral: #ff785a;
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 10%, rgba(214, 255, 121, 0.32), transparent 28rem),
                radial-gradient(circle at 90% 0%, rgba(255, 120, 90, 0.18), transparent 24rem),
                linear-gradient(135deg, #fffaf0 0%, #eef8e8 45%, #dcecd4 100%);
            color: var(--ink);
        }

        h1, h2, h3, .pool-hero, .match-title {
            font-family: 'Bricolage Grotesque', Georgia, serif !important;
        }

        .pool-hero {
            border: 1px solid rgba(16, 35, 28, 0.16);
            border-radius: 28px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            background:
                linear-gradient(120deg, rgba(15, 61, 46, 0.96), rgba(26, 88, 62, 0.94)),
                repeating-linear-gradient(90deg, transparent 0 32px, rgba(255,255,255,0.04) 32px 34px);
            color: white;
            box-shadow: 0 28px 70px rgba(15, 61, 46, 0.22);
        }

        .pool-kicker {
            color: var(--lime);
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            font-size: 0.8rem;
        }

        .pool-hero h1 {
            font-size: clamp(2.3rem, 6vw, 4.8rem);
            line-height: 0.94;
            margin: 0.25rem 0 0;
        }

        .hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 1.15rem;
        }

        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            border-radius: 999px;
            padding: 0.52rem 0.78rem;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: white;
            font-weight: 800;
        }

        .hero-pill span {
            border-radius: 999px;
            padding: 0.18rem 0.52rem;
            background: var(--lime);
            color: #10231c;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .match-card {
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(16, 35, 28, 0.12);
            border-radius: 24px;
            padding: 1.15rem 1.25rem;
            margin: 0.85rem 0;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 18px 42px rgba(16, 35, 28, 0.10);
            backdrop-filter: blur(10px);
        }

        .match-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 8px;
            background: linear-gradient(180deg, var(--coral), var(--lime));
        }

        .match-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            color: rgba(16, 35, 28, 0.68);
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .day-header {
            display: inline-flex;
            align-items: center;
            gap: 0.65rem;
            margin: 2rem 0 0.25rem;
            border-radius: 999px;
            padding: 0.55rem 0.85rem;
            background: rgba(16, 35, 28, 0.92);
            color: white;
            font-family: 'Bricolage Grotesque', Georgia, serif;
            font-weight: 800;
            letter-spacing: 0.02em;
            box-shadow: 0 14px 32px rgba(16, 35, 28, 0.14);
        }

        .day-header span {
            border-radius: 999px;
            padding: 0.18rem 0.5rem;
            background: var(--lime);
            color: #10231c;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .match-title {
            font-size: clamp(1.3rem, 3vw, 2rem);
            font-weight: 800;
            margin: 0.45rem 0 0.75rem;
        }

        .team-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.65rem;
        }

        .team-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            border-radius: 999px;
            padding: 0.52rem 0.78rem;
            background: #10231c;
            color: white;
            font-weight: 800;
        }

        .team-pill span {
            border-radius: 999px;
            padding: 0.16rem 0.48rem;
            background: var(--lime);
            color: #10231c;
            font-size: 0.78rem;
        }

        .versus {
            font-weight: 900;
            color: rgba(16, 35, 28, 0.52);
        }

        .source-note {
            color: rgba(16, 35, 28, 0.64);
            font-size: 0.9rem;
        }

        .page-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .panel-card {
            border: 1px solid rgba(16, 35, 28, 0.12);
            border-radius: 24px;
            padding: 1.15rem;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 18px 42px rgba(16, 35, 28, 0.09);
        }

        .panel-card h3 {
            margin: 0 0 0.85rem;
            font-size: 1.55rem;
        }

        .team-line {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 0.75rem;
            align-items: center;
            border-top: 1px solid rgba(16, 35, 28, 0.10);
            padding: 0.65rem 0;
        }

        .team-line:first-of-type {
            border-top: 0;
        }

        .team-name {
            font-weight: 800;
        }

        .team-owner {
            color: rgba(16, 35, 28, 0.64);
            font-size: 0.9rem;
        }

        .record-pill {
            border-radius: 999px;
            padding: 0.25rem 0.55rem;
            background: var(--lime);
            color: #10231c;
            font-weight: 900;
            font-size: 0.85rem;
        }

        .player-teams {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .player-team {
            border-radius: 999px;
            padding: 0.45rem 0.65rem;
            background: #10231c;
            color: white;
            font-weight: 800;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_match_card(match: dict[str, object]) -> None:
    kickoff = match["kickoff"]
    team_a = str(match["team_a"])
    team_b = str(match["team_b"])
    html = (
        '<div class="match-card">'
        '<div class="match-meta">'
        f'<span>Match {match["match_no"]}</span>'
        f'<span>Group {escape(str(match["group"]))}</span>'
        f'<span>{escape(str(match["tv"]))}</span>'
        f"<span>{escape(format_time(kickoff))}</span>"
        "</div>"
        f'<div class="match-title">{escape(team_a)} vs. {escape(team_b)}</div>'
        '<div class="team-row">'
        f'<div class="team-pill">{team_badge(team_a)}</div>'
        '<div class="versus">against</div>'
        f'<div class="team-pill">{team_badge(team_b)}</div>'
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_hero(title: str, highlight: str | None = None) -> None:
    highlight_html = ""
    if highlight:
        highlight_html = (
            '<div class="hero-meta">'
            f'<div class="hero-pill"><span>Next kickoff</span>{escape(highlight)}</div>'
            "</div>"
        )
    st.markdown(
        (
            '<section class="pool-hero">'
            '<div class="pool-kicker">2026 World Cup pool</div>'
            f"<h1>{escape(title)}</h1>"
            f"{highlight_html}"
            "</section>"
        ),
        unsafe_allow_html=True,
    )


def render_day_header(kickoff: datetime, match_count: int) -> None:
    label = "match" if match_count == 1 else "matches"
    st.markdown(
        (
            '<div class="day-header">'
            f"{escape(format_day(kickoff))}"
            f"<span>{match_count} {label}</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def filter_schedule_matches(
    matches: list[dict[str, object]], upcoming_only: bool
) -> list[dict[str, object]]:
    now_et = datetime.now(EASTERN)
    filtered_matches = matches
    if upcoming_only:
        filtered_matches = [
            match for match in filtered_matches if match["kickoff"] >= now_et
        ]

    return sorted(filtered_matches, key=lambda match: match["kickoff"])


def render_schedule_page(filtered_matches: list[dict[str, object]]) -> None:
    if not filtered_matches:
        st.info("No upcoming fixtures are available for this page right now.")
    for _match_day, day_matches in group_matches_by_day(filtered_matches):
        render_day_header(day_matches[0]["kickoff"], len(day_matches))
        for match in day_matches:
            render_match_card(match)

    source_html = (
        '<p class="source-note">'
        f'Fixture source: <a href="{FIXTURE_SOURCE_URL}" target="_blank">FourFourTwo full schedule</a>. '
        "TV labels were cross-checked from "
        f'<a href="{TV_SOURCE_URL}" target="_blank">SB Nation\'s Eastern-time schedule</a>. '
        "Known-team coverage is limited to the group stage because knockout opponents depend on group results."
        "</p>"
    )
    st.markdown(source_html, unsafe_allow_html=True)


def render_groups_page(matches: list[dict[str, object]]) -> None:
    cards = []
    for group, teams in build_groups(matches).items():
        rows = "".join(
            (
                '<div class="team-line">'
                "<div>"
                f'<div class="team-name">{escape(team)}</div>'
                f'<div class="team-owner">{escape(owner(team))}</div>'
                "</div>"
                f'<div class="record-pill">{escape(group_play_record(team))}</div>'
                "</div>"
            )
            for team in teams
        )
        cards.append(
            '<div class="panel-card">'
            f"<h3>Group {escape(group)}</h3>"
            f"{rows}"
            "</div>"
        )

    st.markdown('<div class="page-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def render_players_page() -> None:
    cards = []
    for person, teams in POOL_DRAW.items():
        team_pills = "".join(
            f'<span class="player-team">{escape(team)}</span>' for team in teams
        )
        cards.append(
            '<div class="panel-card">'
            f"<h3>{escape(person)}</h3>"
            f'<div class="player-teams">{team_pills}</div>'
            "</div>"
        )

    st.markdown('<div class="page-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="World Cup Pool Tracker",
        page_icon="soccer",
        layout="wide",
    )
    inject_styles()

    matches = build_matches()

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Page", ["Group Schedule", "Groups", "Players"])
    upcoming_only = False
    if page == "Group Schedule":
        st.sidebar.divider()
        upcoming_only = st.sidebar.checkbox("Upcoming only", value=True)

    if page == "Group Schedule":
        filtered_matches = filter_schedule_matches(matches, upcoming_only)
        next_match = filtered_matches[0] if filtered_matches else None
        render_hero(
            "Group Play Schedule",
            format_kickoff(next_match["kickoff"]) if next_match else "No upcoming matches",
        )
        render_schedule_page(filtered_matches)
    elif page == "Groups":
        render_hero("Groups")
        render_groups_page(matches)
    else:
        render_hero("Players")
        render_players_page()


if __name__ == "__main__":
    main()
