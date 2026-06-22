from __future__ import annotations

import base64
import json
import re
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from html import escape
from html import unescape
from pathlib import Path
from urllib.request import Request
from urllib.request import urlopen
from zoneinfo import ZoneInfo

import streamlit as st


EASTERN = ZoneInfo("America/New_York")
PLAYER_IMAGE_DIR = Path(__file__).parent / "assets" / "players"
FIXTURE_SOURCE_URL = "https://www.fourfourtwo.com/competition/world-cup-2026-fixtures-and-results"
TV_SOURCE_URL = "https://www.sbnation.com/soccer/1117513/world-cup-schedule-2026-how-to-watch-every-match-scores-and-more"
SCORE_SOURCE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates=20260611-20260627&limit=200"
TITLE_ODDS_SOURCE_URL = "https://www.fourfourtwo.com/competition/world-cup-2026-sweepstakes-kit-download-and-print-our-sweepstake-template"

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

PLAYER_COLORS = {
    "Sam": "#d6ff79",
    "Rob": "#7bdff2",
    "Jerry": "#ffb703",
    "David": "#ff8fab",
    "Steve": "#b8f2e6",
    "Unclaimed": "#d7ded5",
}

TEAM_ALIASES = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Cabo Verde": "Cape Verde",
    "Cape Verde": "Cape Verde",
    "Congo DR": "DR Congo",
    "Cote d'Ivoire": "Ivory Coast",
    "Côte d’Ivoire": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Curaçao": "Curacao",
    "Curacao": "Curacao",
    "Korea Republic": "South Korea",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
    "USA": "United States",
    "USMNT": "United States",
}

FALLBACK_TITLE_ODDS = {
    "Spain": "4/1",
    "France": "9/2",
    "England": "6/1",
    "Brazil": "8/1",
    "Argentina": "8/1",
    "Portugal": "10/1",
    "Germany": "14/1",
    "Netherlands": "20/1",
    "Norway": "25/1",
    "Belgium": "33/1",
    "Colombia": "33/1",
    "United States": "40/1",
    "Morocco": "40/1",
    "Japan": "50/1",
    "Uruguay": "50/1",
    "Czechia": "50/1",
    "Mexico": "66/1",
    "Croatia": "66/1",
    "Switzerland": "66/1",
    "Sweden": "66/1",
    "Ecuador": "66/1",
    "Senegal": "66/1",
    "Turkey": "66/1",
    "Austria": "100/1",
    "Ivory Coast": "100/1",
    "South Korea": "100/1",
    "Egypt": "150/1",
    "Canada": "150/1",
    "Paraguay": "150/1",
    "Australia": "200/1",
    "Bosnia and Herzegovina": "200/1",
    "Iran": "250/1",
    "Scotland": "250/1",
    "DR Congo": "250/1",
    "Algeria": "250/1",
    "Saudi Arabia": "300/1",
    "Ghana": "300/1",
    "Tunisia": "300/1",
    "South Africa": "400/1",
    "Panama": "400/1",
    "Cape Verde": "500/1",
    "Uzbekistan": "500/1",
    "Qatar": "500/1",
    "Iraq": "500/1",
    "Jordan": "500/1",
    "Curacao": "1000/1",
    "Haiti": "1000/1",
    "New Zealand": "1000/1",
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
    return f"{kickoff:%A} {kickoff:%B} {kickoff.day}"


def format_time(kickoff: datetime) -> str:
    hour = kickoff.hour % 12 or 12
    am_pm = "AM" if kickoff.hour < 12 else "PM"
    return f"{hour}:{kickoff.minute:02d} {am_pm} ET"


def format_tv(network: str) -> str:
    return "Fox" if network.upper() == "FOX" else network


def canonical_team_name(team: str) -> str:
    cleaned = unescape(team).replace("\xa0", " ").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return TEAM_ALIASES.get(cleaned, cleaned)


def owner(team: str) -> str:
    return OWNER_BY_TEAM.get(team, "Unclaimed")


def player_image_path(person: str, mood: str = "normal") -> Path:
    suffix = "_sad" if mood == "sad" else ""
    return PLAYER_IMAGE_DIR / f"{person.lower()}{suffix}.jpg"


@st.cache_data(show_spinner=False)
def image_data_uri(path_text: str) -> str | None:
    path = Path(path_text)
    if not path.exists():
        return None
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def player_avatar(person: str, mood: str = "normal") -> str:
    image_path = player_image_path(person, mood)
    data_uri = image_data_uri(str(image_path))
    if data_uri:
        return f'<img src="{data_uri}" alt="{escape(person)}">'
    return escape(person[:1].upper())


def player_pill(person: str, mood: str = "normal") -> str:
    color = PLAYER_COLORS.get(person, PLAYER_COLORS["Unclaimed"])
    return (
        f'<div class="player-pill" style="--avatar-color: {color};">'
        f'<span class="player-avatar">{player_avatar(person, mood)}</span>'
        f"<span>{escape(person)}</span>"
        "</div>"
    )


def avatar_nameplate(person: str, mood: str = "normal", size: str = "medium") -> str:
    color = PLAYER_COLORS.get(person, PLAYER_COLORS["Unclaimed"])
    return (
        f'<div class="avatar-nameplate avatar-{escape(size)}" style="--avatar-color: {color};">'
        f'<div class="avatar-photo">{player_avatar(person, mood)}</div>'
        f'<div class="avatar-label">{escape(person)}</div>'
        "</div>"
    )


def blank_record() -> dict[str, int]:
    return {
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "gf": 0,
        "ga": 0,
        "gd": 0,
        "points": 0,
    }


def score_key(team_a: str, team_b: str) -> frozenset[str]:
    return frozenset({canonical_team_name(team_a), canonical_team_name(team_b)})


def parse_scores_from_espn(payload: dict[str, object]) -> dict[frozenset[str], dict[str, object]]:
    scores = {}
    for event in payload.get("events", []):
        competitions = event.get("competitions") or []
        if not competitions:
            continue
        competition = competitions[0]
        competitors = competition.get("competitors") or []
        if len(competitors) != 2:
            continue

        status = competition.get("status") or {}
        status_type = status.get("type") or {}
        state = status_type.get("state", "pre")
        completed = bool(status_type.get("completed"))
        status_label = (
            status_type.get("shortDetail")
            or status_type.get("detail")
            or status_type.get("description")
            or state.title()
        )

        teams = []
        for competitor in competitors:
            team = competitor.get("team") or {}
            team_name = canonical_team_name(
                team.get("displayName") or team.get("shortDisplayName") or ""
            )
            if not team_name:
                continue
            teams.append(
                {
                    "team": team_name,
                    "score": int(competitor.get("score") or 0),
                }
            )
        if len(teams) != 2:
            continue

        scores[score_key(teams[0]["team"], teams[1]["team"])] = {
            "team_a": teams[0]["team"],
            "team_b": teams[1]["team"],
            "score_a": teams[0]["score"],
            "score_b": teams[1]["score"],
            "state": state,
            "completed": completed,
            "status_label": status_label,
        }
    return scores


@st.cache_data(ttl=60, show_spinner=False)
def fetch_live_scores() -> tuple[dict[frozenset[str], dict[str, object]], str | None]:
    try:
        request = Request(
            SCORE_SOURCE_URL,
            headers={"User-Agent": "Mozilla/5.0 World Cup Pool Tracker"},
        )
        with urlopen(request, timeout=8) as response:
            payload = json.load(response)
    except Exception as exc:
        return {}, f"Could not refresh live scores from ESPN: {exc}"

    return parse_scores_from_espn(payload), None


def parse_fractional_odds(odds_text: str) -> float | None:
    cleaned = odds_text.replace(",", "").strip()
    match = re.fullmatch(r"(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)", cleaned)
    if not match:
        return None
    numerator = float(match.group(1))
    denominator = float(match.group(2))
    if denominator <= 0:
        return None
    return denominator / (numerator + denominator)


def format_pool_chance(probability: float) -> str:
    if probability >= 0.1:
        return f"{probability * 100:.1f}%"
    return f"{probability * 100:.2f}%"


def parse_title_odds_from_html(html: str) -> dict[str, str]:
    odds: dict[str, str] = {}
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    pattern = re.compile(
        r"\b\d+\s*-\s*([A-Za-z][A-Za-z\s.&'\u00c0-\u017f]+?)\s*\(([\d,]+(?:\.\d+)?/\d+)\)"
    )
    for raw_team, raw_odds in pattern.findall(text):
        team = canonical_team_name(re.sub(r"\s+", " ", raw_team).strip())
        if team in OWNER_BY_TEAM:
            odds[team] = raw_odds.replace(",", "")
    return odds


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_title_odds() -> tuple[dict[str, str], dict[str, object]]:
    fallback_meta: dict[str, object] = {
        "message": None,
        "fallback_teams": set(),
    }
    try:
        request = Request(
            TITLE_ODDS_SOURCE_URL,
            headers={"User-Agent": "Mozilla/5.0 World Cup Pool Tracker"},
        )
        with urlopen(request, timeout=8) as response:
            html = response.read().decode("utf-8", errors="replace")
        odds = parse_title_odds_from_html(html)
    except Exception as exc:
        fallback_meta["message"] = (
            f"Could not refresh title odds from FourFourTwo; using saved odds: {exc}"
        )
        fallback_meta["fallback_teams"] = set(FALLBACK_TITLE_ODDS)
        return FALLBACK_TITLE_ODDS.copy(), fallback_meta

    missing = set(OWNER_BY_TEAM) - set(odds)
    if missing:
        odds.update({team: FALLBACK_TITLE_ODDS[team] for team in missing})
        fallback_meta["message"] = (
            "FourFourTwo odds were missing "
            f"{', '.join(sorted(missing))}; filled from saved odds."
        )
        fallback_meta["fallback_teams"] = missing
    return odds, fallback_meta


def build_title_odds_table(odds: dict[str, str]) -> dict[str, dict[str, object]]:
    implied = {
        team: probability
        for team, odds_text in odds.items()
        if (probability := parse_fractional_odds(odds_text)) is not None
    }
    total = sum(implied.values()) or 1
    return {
        team: {
            "odds": odds[team],
            "implied": probability,
            "normalized": probability / total,
        }
        for team, probability in implied.items()
    }


def player_title_chance(
    teams: list[str], title_odds: dict[str, dict[str, object]]
) -> float:
    return sum(float(title_odds.get(team, {}).get("normalized", 0)) for team in teams)


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
                "score_a": None,
                "score_b": None,
                "status": "scheduled",
                "status_label": None,
                "owners": {owner_a, owner_b},
                "teams": {team_a, team_b},
            }
        )
    return matches


def infer_time_status(kickoff: datetime) -> str:
    now_et = datetime.now(EASTERN)
    if now_et < kickoff:
        return "scheduled"
    if now_et <= kickoff + timedelta(hours=3):
        return "live"
    return "scheduled"


def enrich_matches_with_scores(
    matches: list[dict[str, object]],
    score_results: dict[frozenset[str], dict[str, object]],
) -> list[dict[str, object]]:
    enriched_matches = []
    for match in matches:
        enriched = dict(match)
        result = score_results.get(score_key(str(match["team_a"]), str(match["team_b"])))
        if result:
            if canonical_team_name(str(match["team_a"])) == result["team_a"]:
                enriched["score_a"] = result["score_a"]
                enriched["score_b"] = result["score_b"]
            else:
                enriched["score_a"] = result["score_b"]
                enriched["score_b"] = result["score_a"]
            enriched["status_label"] = result.get("status_label")
            if result.get("completed") or result.get("state") == "post":
                enriched["status"] = "final"
            elif result.get("state") == "in":
                enriched["status"] = "live"
            else:
                enriched["status"] = infer_time_status(enriched["kickoff"])
        else:
            enriched["status"] = infer_time_status(enriched["kickoff"])
        enriched_matches.append(enriched)
    return enriched_matches


def build_records(matches: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    records = defaultdict(blank_record)
    for match in matches:
        if match["status"] != "final":
            continue
        team_a = str(match["team_a"])
        team_b = str(match["team_b"])
        score_a = int(match["score_a"])
        score_b = int(match["score_b"])

        records[team_a]["played"] += 1
        records[team_b]["played"] += 1
        records[team_a]["gf"] += score_a
        records[team_a]["ga"] += score_b
        records[team_b]["gf"] += score_b
        records[team_b]["ga"] += score_a

        if score_a > score_b:
            records[team_a]["wins"] += 1
            records[team_a]["points"] += 3
            records[team_b]["losses"] += 1
        elif score_b > score_a:
            records[team_b]["wins"] += 1
            records[team_b]["points"] += 3
            records[team_a]["losses"] += 1
        else:
            records[team_a]["draws"] += 1
            records[team_b]["draws"] += 1
            records[team_a]["points"] += 1
            records[team_b]["points"] += 1

    all_teams = {team for match in matches for team in (match["team_a"], match["team_b"])}
    for team in all_teams:
        records[str(team)]["gd"] = records[str(team)]["gf"] - records[str(team)]["ga"]
    return dict(records)


def format_record(record: dict[str, int]) -> str:
    return f'{record["wins"]}-{record["draws"]}-{record["losses"]}'


def format_record_detail(record: dict[str, int]) -> str:
    gd = record["gd"]
    gd_text = f"+{gd}" if gd > 0 else str(gd)
    return f'{format_record(record)} - {record["points"]} pts - GD {gd_text}'


def sweep_status(record: dict[str, int]) -> dict[str, object]:
    wins = record["wins"]
    impossible = record["draws"] > 0 or record["losses"] > 0
    if impossible:
        return {
            "label": "Sweep ended",
            "class": "is-dead",
            "progress": 0,
            "width": "0%",
        }
    meter_class = "is-charged" if wins == 2 else "is-live"
    return {
        "label": f"Sweep {wins}/3",
        "class": meter_class,
        "progress": wins,
        "width": f"{min(wins, 3) / 3 * 100:.0f}%",
    }


def sweep_meter(record: dict[str, int]) -> str:
    status = sweep_status(record)
    label = escape(str(status["label"]))
    ticks = "".join(
        '<span class="sweep-tick is-filled"></span>'
        if index < int(status["progress"])
        else '<span class="sweep-tick"></span>'
        for index in range(3)
    )
    return (
        f'<div class="sweep-meter {status["class"]}">'
        f'<div class="sweep-copy"><span>{label}</span></div>'
        '<div class="sweep-track">'
        f'<div class="sweep-fill" style="width: {status["width"]};"></div>'
        f"{ticks}"
        "</div>"
        "</div>"
    )


def build_groups(matches: list[dict[str, object]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for match in matches:
        group = str(match["group"])
        groups.setdefault(group, [])
        for team in (str(match["team_a"]), str(match["team_b"])):
            if team not in groups[group]:
                groups[group].append(team)
    return dict(sorted(groups.items()))


def build_group_standings(
    matches: list[dict[str, object]], records: dict[str, dict[str, int]]
) -> dict[str, list[str]]:
    groups = build_groups(matches)
    standings = {}
    for group, teams in groups.items():
        original_order = {team: index for index, team in enumerate(teams)}
        standings[group] = sorted(
            teams,
            key=lambda team: (
                -records.get(team, blank_record())["points"],
                -records.get(team, blank_record())["gd"],
                -records.get(team, blank_record())["gf"],
                original_order[team],
            ),
        )
    return standings


def player_details_html(
    person: str,
    title_odds: dict[str, dict[str, object]],
    odds_meta: dict[str, object],
) -> str:
    fallback_teams = set(odds_meta.get("fallback_teams", set()))
    teams = sorted(
        POOL_DRAW.get(person, []),
        key=lambda team: float(title_odds.get(team, {}).get("normalized", 0)),
        reverse=True,
    )
    team_rows = "".join(
        (
            '<div class="popup-row">'
            '<div>'
            f'<strong>{escape(team)}{"*" if team in fallback_teams else ""}</strong>'
            f'<span>{escape(format_pool_chance(float(title_odds.get(team, {}).get("normalized", 0))))} title share</span>'
            "</div>"
            f'<b>{escape(str(title_odds.get(team, {}).get("odds", "N/A")))}</b>'
            "</div>"
        )
        for team in teams
    )
    pool_chance = format_pool_chance(player_title_chance(teams, title_odds))
    return (
        '<div class="popup-panel player-popup-panel">'
        f'<div class="popup-title">{escape(person)} pool</div>'
        f'<div class="popup-kpi">{escape(pool_chance)} chance this pool has the champion</div>'
        f"{team_rows}"
        "</div>"
    )


def player_popover(
    person: str,
    mood: str,
    title_odds: dict[str, dict[str, object]],
    odds_meta: dict[str, object],
    size: str = "medium",
) -> str:
    return (
        '<details class="click-popover player-popover">'
        f"<summary>{avatar_nameplate(person, mood, size)}</summary>"
        f"{player_details_html(person, title_odds, odds_meta)}"
        "</details>"
    )


def group_details_html(
    group: str, matches: list[dict[str, object]], records: dict[str, dict[str, int]]
) -> str:
    teams = build_group_standings(matches, records).get(group, [])
    rows = "".join(
        (
            '<div class="popup-row">'
            "<div>"
            f"<strong>{escape(team)}</strong>"
            f"<span>{escape(owner(team))}</span>"
            "</div>"
            f"<b>{escape(format_record_detail(records.get(team, blank_record())))}</b>"
            "</div>"
        )
        for team in teams
    )
    return (
        '<div class="popup-panel group-popup-panel">'
        f'<div class="popup-title">Group {escape(group)} standings</div>'
        f"{rows}"
        "</div>"
    )


def group_popover(
    group: str, matches: list[dict[str, object]], records: dict[str, dict[str, int]]
) -> str:
    return (
        '<details class="click-popover group-popover">'
        f'<summary class="group-trigger group-{escape(group.lower())}">{escape(group)}</summary>'
        f"{group_details_html(group, matches, records)}"
        "</details>"
    )


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
            z-index: 1;
            overflow: visible;
            border: 1px solid rgba(16, 35, 28, 0.12);
            border-radius: 30px;
            padding: 1.35rem 1.45rem 1.5rem;
            margin: 0.9rem 0 1.35rem;
            min-height: 23rem;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 18px 42px rgba(16, 35, 28, 0.10);
            backdrop-filter: blur(10px);
        }

        .match-card:has(.click-popover[open]) {
            z-index: 80;
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
            padding-right: 4rem;
            color: rgba(16, 35, 28, 0.62);
            font-size: 0.9rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .day-header {
            margin: 2rem 0 0.45rem;
            color: rgba(16, 35, 28, 0.52);
            font-family: 'Bricolage Grotesque', Georgia, serif;
            font-weight: 800;
            font-size: 1.05rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .match-title {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-size: clamp(1.75rem, 4vw, 3.1rem);
            font-weight: 800;
            margin: 0.52rem 4rem 1.25rem 0;
            line-height: 0.98;
        }

        .group-dot {
            display: inline-grid;
            place-items: center;
            flex: 0 0 auto;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            color: white;
            font-size: 1rem;
            font-weight: 900;
            box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.16);
        }

        .matchup-text {
            display: inline-flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.55rem;
        }

        .score-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 0.16rem 0.58rem;
            background: #10231c;
            color: var(--lime);
            font-size: 0.95rem;
            font-weight: 900;
            letter-spacing: 0.04em;
        }

        .group-a { background: #d94141; }
        .group-b { background: #2563eb; }
        .group-c { background: #0f9f6e; }
        .group-d { background: #f97316; }
        .group-e { background: #7c3aed; }
        .group-f { background: #0891b2; }
        .group-g { background: #be123c; }
        .group-h { background: #4d7c0f; }
        .group-i { background: #9333ea; }
        .group-j { background: #0369a1; }
        .group-k { background: #ca8a04; }
        .group-l { background: #475569; }

        .player-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.55rem;
        }

        .match-avatars {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: clamp(1rem, 4vw, 3rem);
            margin-top: 1.35rem;
        }

        .avatar-nameplate {
            --avatar-size: 172px;
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            min-width: calc(var(--avatar-size) + 18px);
            color: #10231c;
            text-align: center;
        }

        .avatar-photo {
            display: grid;
            place-items: center;
            width: var(--avatar-size);
            height: var(--avatar-size);
            overflow: hidden;
            border-radius: 999px;
            background: var(--avatar-color);
            color: #10231c;
            border: 7px solid rgba(255, 255, 255, 0.92);
            box-shadow: 0 16px 34px rgba(16, 35, 28, 0.22);
            font-size: calc(var(--avatar-size) * 0.42);
            font-weight: 900;
        }

        .avatar-photo img {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
        }

        .avatar-label {
            position: relative;
            z-index: 1;
            margin-top: -1.15rem;
            border-radius: 999px;
            padding: 0.45rem 1.2rem;
            min-width: 7.2rem;
            background: #10231c;
            color: white;
            font-weight: 900;
            box-shadow: 0 10px 22px rgba(16, 35, 28, 0.22);
        }

        .avatar-small {
            --avatar-size: 70px;
            min-width: 5rem;
        }

        .avatar-small .avatar-photo {
            border-width: 4px;
            box-shadow: 0 8px 18px rgba(16, 35, 28, 0.18);
        }

        .avatar-small .avatar-label {
            min-width: 4.6rem;
            margin-top: -0.75rem;
            padding: 0.28rem 0.65rem;
            font-size: 0.76rem;
        }

        .click-popover {
            position: relative;
            display: inline-block;
        }

        .click-popover > summary {
            list-style: none;
            cursor: pointer;
        }

        .click-popover > summary::-webkit-details-marker {
            display: none;
        }

        .popup-panel {
            position: absolute;
            z-index: 30;
            min-width: 17rem;
            max-width: min(22rem, calc(100vw - 2rem));
            border-radius: 20px;
            padding: 0.85rem;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(16, 35, 28, 0.14);
            box-shadow: 0 24px 58px rgba(16, 35, 28, 0.22);
            color: #10231c;
            text-align: left;
        }

        .player-popup-panel {
            top: calc(100% + 0.8rem);
            left: 50%;
            transform: translateX(-50%);
        }

        .group-popup {
            position: absolute;
            top: 1rem;
            right: 1rem;
            z-index: 20;
        }

        .group-popup-panel {
            top: calc(100% + 0.65rem);
            right: 0;
        }

        .group-trigger {
            display: inline-grid;
            place-items: center;
            width: 2.65rem;
            height: 2.65rem;
            border-radius: 999px;
            color: white;
            font-size: 1.12rem;
            font-weight: 900;
            box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.16), 0 10px 20px rgba(16, 35, 28, 0.14);
        }

        .popup-title {
            margin-bottom: 0.5rem;
            font-size: 0.92rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(16, 35, 28, 0.66);
        }

        .popup-kpi {
            margin-bottom: 0.65rem;
            border-radius: 14px;
            padding: 0.55rem 0.65rem;
            background: var(--lime);
            font-weight: 900;
        }

        .popup-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            border-top: 1px solid rgba(16, 35, 28, 0.08);
            padding: 0.48rem 0;
        }

        .popup-row:first-of-type {
            border-top: 0;
        }

        .popup-row strong,
        .popup-row span {
            display: block;
        }

        .popup-row span {
            color: rgba(16, 35, 28, 0.58);
            font-size: 0.78rem;
            font-weight: 700;
        }

        .popup-row b {
            white-space: nowrap;
            font-size: 0.82rem;
        }

        .player-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.42rem;
            border-radius: 999px;
            padding: 0.28rem 0.68rem 0.28rem 0.28rem;
            background: #10231c;
            color: white;
            font-weight: 800;
        }

        .player-avatar {
            display: inline-grid;
            place-items: center;
            width: 1.7rem;
            height: 1.7rem;
            border-radius: 999px;
            background: var(--avatar-color);
            color: #10231c;
            font-size: 0.78rem;
            font-weight: 900;
            overflow: hidden;
            flex: 0 0 auto;
        }

        .player-avatar img {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
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
            grid-template-columns: auto minmax(0, 1fr);
            gap: 0.75rem;
            align-items: start;
            border-top: 1px solid rgba(16, 35, 28, 0.10);
            padding: 0.65rem 0;
        }

        .team-line:first-of-type {
            border-top: 0;
        }

        .team-summary {
            min-width: 0;
        }

        .team-topline {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
        }

        .team-identity {
            min-width: 0;
        }

        .team-name {
            font-weight: 800;
            line-height: 1.15;
        }

        .team-owner {
            color: rgba(16, 35, 28, 0.64);
            font-size: 0.9rem;
        }

        .record-pill {
            border-radius: 999px;
            padding: 0.24rem 0.56rem;
            background: var(--lime);
            color: #10231c;
            font-weight: 900;
            font-size: 0.72rem;
            white-space: nowrap;
            line-height: 1;
            margin-top: 0.12rem;
        }

        .sweep-meter {
            width: min(100%, 14rem);
            margin-top: 0.45rem;
        }

        .sweep-copy {
            display: flex;
            justify-content: flex-start;
            color: rgba(16, 35, 28, 0.66);
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.25rem;
        }

        .sweep-track {
            position: relative;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.3rem;
            overflow: hidden;
            border-radius: 999px;
            padding: 0.18rem;
            background: rgba(16, 35, 28, 0.10);
        }

        .sweep-track::after {
            content: "";
            position: absolute;
            inset: -40% auto -40% -35%;
            width: 38%;
            z-index: 2;
            transform: skewX(-18deg);
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.82), transparent);
            opacity: 0;
            pointer-events: none;
        }

        .sweep-fill {
            position: absolute;
            inset: 0 auto 0 0;
            border-radius: inherit;
            background: rgba(214, 255, 121, 0.95);
            transition: width 240ms ease;
        }

        .sweep-tick {
            position: relative;
            z-index: 1;
            height: 0.46rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.66);
            border: 1px solid rgba(16, 35, 28, 0.10);
        }

        .sweep-tick.is-filled {
            background: #10231c;
        }

        .sweep-meter.is-charged .sweep-copy {
            color: #0f6b42;
            text-shadow: 0 0 14px rgba(214, 255, 121, 0.7);
        }

        .sweep-meter.is-charged .sweep-track {
            background: rgba(214, 255, 121, 0.28);
            box-shadow:
                0 0 0 1px rgba(15, 107, 66, 0.12),
                0 0 22px rgba(214, 255, 121, 0.72);
        }

        .sweep-meter.is-charged .sweep-track::after {
            animation: sweep-spark 1.4s ease-in-out infinite;
        }

        .sweep-meter.is-charged .sweep-fill {
            background: linear-gradient(90deg, #d6ff79, #5cff9a, #d6ff79);
            background-size: 220% 100%;
            animation: sweep-charge 1.2s linear infinite;
        }

        .sweep-meter.is-charged .sweep-tick.is-filled {
            background: #082d20;
            box-shadow: 0 0 12px rgba(214, 255, 121, 0.95);
        }

        @keyframes sweep-charge {
            from { background-position: 0% 50%; }
            to { background-position: 220% 50%; }
        }

        @keyframes sweep-spark {
            0% {
                left: -35%;
                opacity: 0;
            }
            28% {
                opacity: 0.9;
            }
            65% {
                opacity: 0;
            }
            100% {
                left: 105%;
                opacity: 0;
            }
        }

        .sweep-meter.is-dead .sweep-fill {
            background: rgba(16, 35, 28, 0.16);
        }

        .sweep-meter.is-dead .sweep-copy {
            color: rgba(16, 35, 28, 0.42);
        }

        .sweep-meter.is-dead .sweep-track {
            opacity: 0.86;
        }

        .sweep-meter.is-dead .sweep-tick {
            background: rgba(16, 35, 28, 0.18);
        }

        @media (max-width: 760px) {
            .match-card {
                min-height: 0;
                padding: 1.15rem;
            }

            .match-title {
                margin-right: 3.2rem;
            }

            .avatar-nameplate {
                --avatar-size: 124px;
                min-width: 8.2rem;
            }

            .avatar-label {
                min-width: 5.7rem;
            }

            .match-avatars {
                gap: 0.75rem;
            }

            .popup-panel {
                min-width: min(17rem, calc(100vw - 2rem));
            }

            .player-popup-panel {
                left: 0;
                transform: none;
            }

            .team-topline {
                flex-direction: column;
                gap: 0.35rem;
            }

            .record-pill {
                align-self: flex-start;
            }
        }

        .player-teams {
            display: grid;
            gap: 0.55rem;
        }

        .player-team {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 0.7rem;
            align-items: center;
            border-radius: 16px;
            padding: 0.62rem 0.7rem;
            background: rgba(16, 35, 28, 0.06);
            border: 1px solid rgba(16, 35, 28, 0.08);
        }

        .player-team-name {
            color: #10231c;
            font-weight: 900;
            line-height: 1.1;
        }

        .player-team-chance {
            color: rgba(16, 35, 28, 0.58);
            font-size: 0.8rem;
            font-weight: 800;
        }

        .odds-pill {
            border-radius: 999px;
            padding: 0.35rem 0.58rem;
            background: #10231c;
            color: #ffffff;
            font-size: 0.82rem;
            font-weight: 900;
            white-space: nowrap;
        }

        .player-card-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.9rem;
        }

        .player-card-head h3 {
            margin-bottom: 0.15rem;
        }

        .pool-chance {
            min-width: 6rem;
            border-radius: 18px;
            padding: 0.55rem 0.7rem;
            background: var(--lime);
            color: #10231c;
            text-align: right;
            box-shadow: inset 0 0 0 1px rgba(16, 35, 28, 0.08);
        }

        .pool-chance span {
            display: block;
            color: rgba(16, 35, 28, 0.58);
            font-size: 0.68rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .pool-chance strong {
            display: block;
            font-size: 1.3rem;
            line-height: 1;
        }

        .odds-source {
            margin-top: 1rem;
            color: rgba(16, 35, 28, 0.56);
            font-size: 0.86rem;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_match_card(
    match: dict[str, object],
    matches: list[dict[str, object]],
    records: dict[str, dict[str, int]],
    title_odds: dict[str, dict[str, object]],
    odds_meta: dict[str, object],
) -> None:
    kickoff = match["kickoff"]
    team_a = str(match["team_a"])
    team_b = str(match["team_b"])
    group = str(match["group"])
    owner_a = str(match["owner_a"])
    owner_b = str(match["owner_b"])
    is_final = match["status"] == "final"
    is_live = match["status"] == "live"
    has_score = match["score_a"] is not None and match["score_b"] is not None
    status_label = str(match["status_label"] or "").strip()
    mood_a = "normal"
    mood_b = "normal"
    if is_final and has_score:
        score_a = int(match["score_a"])
        score_b = int(match["score_b"])
        if score_a < score_b:
            mood_a = "sad"
        elif score_b < score_a:
            mood_b = "sad"
    if is_final:
        meta_lead = "Final"
    elif is_live:
        meta_lead = f"Live - {status_label}" if status_label else "Live"
    else:
        meta_lead = format_time(kickoff)

    if has_score and (is_final or is_live):
        matchup = (
            f"{escape(team_a)}"
            f'<span class="score-chip">{match["score_a"]}-{match["score_b"]}</span>'
            f"{escape(team_b)}"
        )
    else:
        matchup = f"{escape(team_a)} vs. {escape(team_b)}"

    html = (
        '<div class="match-card">'
        f"{group_popover(group, matches, records)}"
        '<div class="match-meta">'
        f"<span>{escape(meta_lead)}</span>"
        "<span>-</span>"
        f'<span>{escape(format_tv(str(match["tv"])))}</span>'
        "</div>"
        '<div class="match-title">'
        f'<span class="matchup-text">{matchup}</span>'
        "</div>"
        '<div class="match-avatars">'
        f"{player_popover(owner_a, mood_a, title_odds, odds_meta, 'medium')}"
        '<div class="versus">vs</div>'
        f"{player_popover(owner_b, mood_b, title_odds, odds_meta, 'medium')}"
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
            f"{escape(format_day(kickoff))} - {match_count} {label}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def filter_schedule_matches(
    matches: list[dict[str, object]], upcoming_only: bool
) -> list[dict[str, object]]:
    filtered_matches = matches
    if upcoming_only:
        filtered_matches = [
            match for match in filtered_matches if match["status"] != "final"
        ]

    return sorted(filtered_matches, key=lambda match: match["kickoff"])


def render_schedule_page(
    filtered_matches: list[dict[str, object]],
    all_matches: list[dict[str, object]],
    records: dict[str, dict[str, int]],
    title_odds: dict[str, dict[str, object]],
    odds_meta: dict[str, object],
    score_error: str | None,
) -> None:
    if score_error:
        st.warning(score_error)
    if not filtered_matches:
        st.info("No upcoming fixtures are available for this page right now.")
    for _match_day, day_matches in group_matches_by_day(filtered_matches):
        render_day_header(day_matches[0]["kickoff"], len(day_matches))
        for match in day_matches:
            render_match_card(match, all_matches, records, title_odds, odds_meta)

    odds_note = (
        f" {escape(str(odds_meta.get('message')))}" if odds_meta.get("message") else ""
    )
    source_html = (
        '<p class="source-note">'
        f'Fixture source: <a href="{FIXTURE_SOURCE_URL}" target="_blank">FourFourTwo full schedule</a>. '
        "Live scores are refreshed from ESPN; TV labels were cross-checked from "
        f'<a href="{TV_SOURCE_URL}" target="_blank">SB Nation\'s Eastern-time schedule</a>. '
        f'Title odds source: <a href="{TITLE_ODDS_SOURCE_URL}" target="_blank">FourFourTwo sweepstake odds</a>.'
        f"{odds_note} "
        "Known-team coverage is limited to the group stage because knockout opponents depend on group results."
        "</p>"
    )
    st.markdown(source_html, unsafe_allow_html=True)


def render_groups_page(
    matches: list[dict[str, object]],
    records: dict[str, dict[str, int]],
    title_odds: dict[str, dict[str, object]],
    odds_meta: dict[str, object],
) -> None:
    cards = []
    for group, teams in build_group_standings(matches, records).items():
        rows = "".join(
            (
                '<div class="team-line">'
                f"{player_popover(owner(team), 'normal', title_odds, odds_meta, 'small')}"
                '<div class="team-summary">'
                '<div class="team-topline">'
                '<div class="team-identity">'
                f'<div class="team-name">{escape(team)}</div>'
                f'<div class="team-owner">{escape(owner(team))}</div>'
                "</div>"
                f'<div class="record-pill">{escape(format_record_detail(records.get(team, blank_record())))}</div>'
                "</div>"
                f"{sweep_meter(records.get(team, blank_record()))}"
                "</div>"
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


def render_players_page(
    title_odds: dict[str, dict[str, object]], odds_meta: dict[str, object]
) -> None:
    fallback_teams = set(odds_meta.get("fallback_teams", set()))
    odds_message = odds_meta.get("message")
    cards = []
    ranked_players = sorted(
        POOL_DRAW.items(),
        key=lambda item: player_title_chance(item[1], title_odds),
        reverse=True,
    )
    for person, teams in ranked_players:
        pool_chance = player_title_chance(teams, title_odds)
        sorted_teams = sorted(
            teams,
            key=lambda team: float(title_odds.get(team, {}).get("normalized", 0)),
            reverse=True,
        )
        team_rows = "".join(
            (
                '<div class="player-team">'
                "<div>"
                '<div class="player-team-name">'
                f'{escape(team)}{"*" if team in fallback_teams else ""}'
                "</div>"
                '<div class="player-team-chance">'
                f'{escape(format_pool_chance(float(title_odds.get(team, {}).get("normalized", 0))))} title share'
                "</div>"
                "</div>"
                f'<span class="odds-pill">{escape(str(title_odds.get(team, {}).get("odds", "N/A")))}</span>'
                "</div>"
            )
            for team in sorted_teams
        )
        cards.append(
            '<div class="panel-card">'
            '<div class="player-card-head">'
            "<div>"
            f"<h3>{escape(person)}</h3>"
            "</div>"
            '<div class="pool-chance">'
            "<span>Pool odds</span>"
            f"<strong>{escape(format_pool_chance(pool_chance))}</strong>"
            "</div>"
            "</div>"
            f'<div class="player-teams">{team_rows}</div>'
            "</div>"
        )

    st.markdown('<div class="page-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)
    odds_note = f" {escape(str(odds_message))}" if odds_message else ""
    st.markdown(
        '<div class="odds-source">'
        f'Title odds source: <a href="{TITLE_ODDS_SOURCE_URL}" target="_blank">FourFourTwo sweepstake odds</a>. '
        "Pool odds are normalized implied probabilities across the drawn teams."
        f"{odds_note}"
        "</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="World Cup Pool Tracker",
        page_icon="soccer",
        layout="wide",
    )
    inject_styles()

    base_matches = build_matches()

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Page", ["Group Schedule", "Groups", "Players"])
    upcoming_only = False
    if page == "Group Schedule":
        st.sidebar.divider()
        upcoming_only = st.sidebar.checkbox("Upcoming only", value=True)
    st.sidebar.divider()
    if st.sidebar.button("Refresh title odds"):
        fetch_title_odds.clear()
    if st.sidebar.button("Refresh scores"):
        fetch_live_scores.clear()

    score_results, score_error = fetch_live_scores()
    matches = enrich_matches_with_scores(base_matches, score_results)
    records = build_records(matches)
    odds_results, odds_meta = fetch_title_odds()
    title_odds = build_title_odds_table(odds_results)

    if page == "Group Schedule":
        filtered_matches = filter_schedule_matches(matches, upcoming_only)
        next_match = filtered_matches[0] if filtered_matches else None
        render_hero(
            "Group Play Schedule",
            format_kickoff(next_match["kickoff"]) if next_match else "No upcoming matches",
        )
        render_schedule_page(
            filtered_matches, matches, records, title_odds, odds_meta, score_error
        )
    elif page == "Groups":
        render_hero("Groups")
        if score_error:
            st.warning(score_error)
        render_groups_page(matches, records, title_odds, odds_meta)
    else:
        render_hero("Players")
        render_players_page(title_odds, odds_meta)


if __name__ == "__main__":
    main()
