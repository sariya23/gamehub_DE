#!/usr/bin/env python3
"""
Synthetic data generator for the GameHub DE educational project.

It creates file-based source exports:

data/raw/
├── user_service/
│   └── users.csv
├── developer_portal/
│   ├── developers.csv
│   └── published_games.csv  # only games added through developer portal
├── game_catalog/
│   ├── games.json
│   ├── genres.csv
│   ├── tags.csv
│   ├── platforms.csv
│   ├── languages.csv
│   ├── game_genres.csv
│   ├── game_tags.csv
│   ├── game_platforms.csv
│   └── game_languages.csv
├── library_service/
│   └── library.csv
├── anti_library_service/
│   └── anti_library.ndjson
├── reviews_service/
│   └── reviews.csv
├── game_stats/
│   └── game_stats.parquet
├── promotion_system/
│   └── promo_campaigns.csv
└── product_analytics/
    └── events.ndjson.gz

Install dependency for parquet:
    pip install pandas pyarrow

Run:
    python generate_gamehub_data.py
    python generate_gamehub_data.py --users 10000 --games 1000 --developers 200 --dirty-rate 0.04 --out data/raw
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd


COUNTRIES = [
    "FI", "RU", "US", "DE", "FR", "PL", "SE", "NO", "GB", "BR",
    "JP", "KR", "CA", "ES", "IT", "NL", "TR", "IN", "CN", "AU",
]

GENRES = [
    "rpg", "action", "adventure", "strategy", "simulation", "survival",
    "horror", "platformer", "puzzle", "racing", "sports", "shooter",
    "roguelike", "sandbox", "visual_novel", "mmo", "fighting", "card_game",
]

TAGS = [
    "singleplayer", "multiplayer", "co-op", "open_world", "story_rich",
    "pixel_art", "souls_like", "crafting", "base_building", "procedural",
    "turn_based", "real_time", "competitive", "casual", "hardcore",
    "atmospheric", "short", "early_access", "controller_support",
]

GENRE_IDS = {genre: f"genre_{i:03d}" for i, genre in enumerate(GENRES, start=1)}
TAG_IDS = {tag: f"tag_{i:03d}" for i, tag in enumerate(TAGS, start=1)}

PLATFORMS = [
    "windows", "macos", "linux", "steam_deck",
    "playstation", "xbox", "nintendo_switch",
]
LANGUAGES = ["en", "ru", "de", "fr", "es", "pt", "ja", "ko", "zh"]

PLATFORM_IDS = {platform: f"platform_{i:03d}" for i, platform in enumerate(PLATFORMS, start=1)}
LANGUAGE_IDS = {language: f"language_{i:03d}" for i, language in enumerate(LANGUAGES, start=1)}

PLACEMENTS = ["home_top", "genre_page", "search_results", "game_page_sidebar", "library_recommendations"]
EVENT_TYPES = ["game_view", "library_add", "anti_library_add", "review_view", "promo_impression", "promo_click"]
COMPLETION_STATUSES = ["not_started", "playing", "completed", "dropped"]
REVIEW_REACTIONS = ["like", "dislike", "funny", "useful"]


@dataclass(frozen=True)
class Config:
    out: Path
    seed: int
    users: int
    developers: int
    games: int
    library_min: int
    library_max: int
    anti_library_min: int
    anti_library_max: int
    campaigns: int
    events: int
    dirty_rate: float
    start_date: datetime
    end_date: datetime


def dt_to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def random_dt(start: datetime, end: datetime) -> datetime:
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, max(delta_seconds, 0)))


def weighted_choice(items: list[str], weights: list[float]) -> str:
    return random.choices(items, weights=weights, k=1)[0]


def dirty_p(cfg: Any, multiplier: float = 1.0) -> float:
    """Return bounded probability for soft data quality issues."""
    return max(0.0, min(0.35, cfg.dirty_rate * multiplier))


def maybe_none(value: Any, cfg: Any, multiplier: float = 1.0) -> Any:
    return None if random.random() < dirty_p(cfg, multiplier) else value


def maybe_blank(value: Any, cfg: Any, multiplier: float = 1.0) -> Any:
    return "" if random.random() < dirty_p(cfg, multiplier) else value


def maybe_dirty_country(value: str, cfg: Any) -> str | None:
    """Keep country mostly clean, but sometimes missing or badly cased."""
    roll = random.random()
    if roll < dirty_p(cfg, 0.35):
        return None
    if roll < dirty_p(cfg, 0.55):
        return value.lower()
    return value


def ensure_dirs(out: Path) -> dict[str, Path]:
    dirs = {
        "user_service": out / "user_service",
        "developer_portal": out / "developer_portal",
        "game_catalog": out / "game_catalog",
        "library_service": out / "library_service",
        "anti_library_service": out / "anti_library_service",
        "reviews_service": out / "reviews_service",
        "game_stats": out / "game_stats",
        "promotion_system": out / "promotion_system",
        "product_analytics": out / "product_analytics",
    }

    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    return dirs


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_ndjson(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_ndjson_gz(path: Path, rows: list[dict[str, Any]]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def make_users(cfg: Config) -> list[dict[str, Any]]:
    users = []

    for i in range(1, cfg.users + 1):
        user_id = f"u_{i:07d}"
        registered_at = random_dt(cfg.start_date, cfg.end_date - timedelta(days=30))

        users.append(
            {
                "user_id": user_id,
                "username": f"user_{i:07d}",
                "email": f"user_{i:07d}@gamehub.example",
                "country": maybe_dirty_country(random.choice(COUNTRIES), cfg),
                "birth_year": maybe_none(random.randint(1975, 2012), cfg, 0.9),
                "registered_at": dt_to_iso(registered_at),
                "account_status": weighted_choice(
                    ["active", "blocked", "deleted"],
                    [0.94, 0.03, 0.03],
                ),
            }
        )

    return users


def make_developers(cfg: Config) -> list[dict[str, Any]]:
    prefixes = ["red", "blue", "silent", "pixel", "iron", "lazy", "wild", "nordic", "tiny", "dark"]
    suffixes = ["fox", "owl", "forge", "games", "studio", "interactive", "labs", "works", "byte", "quest"]

    developers = []

    for i in range(1, cfg.developers + 1):
        developer_id = f"d_{i:06d}"
        created_at = random_dt(cfg.start_date, cfg.end_date - timedelta(days=60))

        developers.append(
            {
                "developer_id": developer_id,
                "studio_name": maybe_blank(f"{random.choice(prefixes)}_{random.choice(suffixes)}_{i:04d}", cfg, 0.1),
                "country": maybe_dirty_country(random.choice(COUNTRIES), cfg),
                "created_at": dt_to_iso(created_at),
                "verification_status": weighted_choice(
                    ["verified", "pending", "rejected"],
                    [0.72, 0.23, 0.05],
                ),
            }
        )

    return developers


def make_games(
    cfg: Config,
    users: list[dict[str, Any]],
    developers: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    adjectives = [
        "ancient", "neon", "silent", "broken", "cosmic", "tiny", "lost", "furious",
        "hidden", "crimson", "golden", "frozen", "electric", "lonely", "wild",
    ]
    nouns = [
        "kingdom", "voyage", "arena", "dungeon", "frontier", "factory", "legacy",
        "storm", "signal", "island", "station", "garden", "citadel", "planet", "archive",
    ]

    genre_rows = [
        {
            "genre_id": GENRE_IDS[genre],
            "genre_name": genre,
            "created_at": dt_to_iso(cfg.start_date),
        }
        for genre in GENRES
    ]

    tag_rows = [
        {
            "tag_id": TAG_IDS[tag],
            "tag_name": tag,
            "created_at": dt_to_iso(cfg.start_date),
        }
        for tag in TAGS
    ]

    platform_rows = [
        {
            "platform_id": PLATFORM_IDS[platform],
            "platform_name": platform,
            "created_at": dt_to_iso(cfg.start_date),
        }
        for platform in PLATFORMS
    ]

    language_rows = [
        {
            "language_id": LANGUAGE_IDS[language],
            "language_code": language,
            "created_at": dt_to_iso(cfg.start_date),
        }
        for language in LANGUAGES
    ]

    active_users = [u for u in users if u["account_status"] == "active"]
    if not active_users:
        active_users = users

    known_devs = [d for d in developers if d["verification_status"] != "rejected"]
    if not known_devs:
        known_devs = developers

    games = []
    published_games = []
    game_genre_rows = []
    game_tag_rows = []
    game_platform_rows = []
    game_language_rows = []

    for i in range(1, cfg.games + 1):
        game_id = f"g_{i:07d}"

        # developer_id is the real developer/owner of the game.
        developer = random.choice(known_devs)

        # added_by_* describes who added the game to the GameHub catalog.
        # A game can be added either by its developer or by a regular user.
        added_by_type = weighted_choice(["developer", "user"], [0.42, 0.58])
        added_by_developer_id = developer["developer_id"] if added_by_type == "developer" else None
        added_by_user_id = random.choice(active_users)["user_id"] if added_by_type == "user" else None

        release_date = random_dt(cfg.start_date + timedelta(days=30), cfg.end_date - timedelta(days=5))
        catalog_created_at = release_date - timedelta(days=random.randint(7, 120))

        main_genre = random.choice(GENRES)
        other_genres = random.sample([g for g in GENRES if g != main_genre], k=random.randint(0, 2))
        game_genres = [main_genre] + other_genres
        game_tags = random.sample(TAGS, k=random.randint(3, 8))
        game_platforms = random.sample(PLATFORMS, k=random.randint(1, len(PLATFORMS)))
        game_languages = random.sample(LANGUAGES, k=random.randint(1, min(5, len(LANGUAGES))))

        publication_status = weighted_choice(
            ["published", "early_access", "unlisted"],
            [0.82, 0.13, 0.05],
        )

        price = random.choice([0, 4.99, 9.99, 14.99, 19.99, 24.99, 29.99, 39.99, 49.99, 59.99])

        games.append(
            {
                "game_id": game_id,
                "developer_id": developer["developer_id"],
                "title": f"{random.choice(adjectives).title()} {random.choice(nouns).title()} {i}",
                "description": maybe_none(
                    maybe_blank(f"Synthetic {main_genre} game generated for GameHub data engineering practice.", cfg, 0.3),
                    cfg,
                    0.55,
                ),
                "age_rating": maybe_none(random.choice(["3+", "7+", "12+", "16+", "18+"]), cfg, 0.6),
                "price_usd": maybe_none(price, cfg, 0.25),
                "release_date": maybe_none(release_date.date().isoformat(), cfg, 0.2),
                "catalog_created_at": dt_to_iso(catalog_created_at),
                "added_by_type": added_by_type,
                "added_by_user_id": added_by_user_id,
                "added_by_developer_id": added_by_developer_id,
                "is_free": price == 0,
                "publication_status": publication_status,
            }
        )

        for position, genre in enumerate(game_genres, start=1):
            game_genre_rows.append(
                {
                    "game_id": game_id,
                    "genre_id": GENRE_IDS[genre],
                    "is_primary": position == 1,
                    "position": position,
                }
            )

        for tag in game_tags:
            game_tag_rows.append(
                {
                    "game_id": game_id,
                    "tag_id": TAG_IDS[tag],
                }
            )

        for platform in game_platforms:
            game_platform_rows.append(
                {
                    "game_id": game_id,
                    "platform_id": PLATFORM_IDS[platform],
                }
            )

        for language in game_languages:
            game_language_rows.append(
                {
                    "game_id": game_id,
                    "language_id": LANGUAGE_IDS[language],
                }
            )

        # Developer Portal contains only games that were added through the developer flow.
        # User-added catalog entries do not appear in this source.
        if added_by_type == "developer":
            published_games.append(
                {
                    "developer_id": developer["developer_id"],
                    "game_id": game_id,
                    "submitted_at": maybe_none(dt_to_iso(catalog_created_at), cfg, 0.25),
                    "published_at": dt_to_iso(release_date),
                    "publication_status": publication_status,
                    "moderation_score": maybe_none(round(random.uniform(0.55, 0.99), 3), cfg, 0.8),
                }
            )

    return (
        games,
        published_games,
        genre_rows,
        tag_rows,
        platform_rows,
        language_rows,
        game_genre_rows,
        game_tag_rows,
        game_platform_rows,
        game_language_rows,
    )


def make_user_game_sets(
    cfg: Config,
    users: list[dict[str, Any]],
    games: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, set[str]], dict[str, set[str]]]:
    active_users = [u for u in users if u["account_status"] == "active"]
    available_games = [g for g in games if g["publication_status"] in {"published", "early_access"}]
    game_ids = [g["game_id"] for g in available_games]

    library_rows = []
    anti_rows = []
    library_by_user: dict[str, set[str]] = {}
    anti_by_user: dict[str, set[str]] = {}

    for user in active_users:
        user_id = user["user_id"]
        registered_at = datetime.fromisoformat(user["registered_at"].replace("Z", "+00:00"))

        library_size = random.randint(cfg.library_min, cfg.library_max)
        anti_size = random.randint(cfg.anti_library_min, cfg.anti_library_max)

        max_total = min(len(game_ids), library_size + anti_size)
        selected = set(random.sample(game_ids, k=max_total))
        selected_list = list(selected)
        random.shuffle(selected_list)

        user_library = set(selected_list[: min(library_size, len(selected_list))])
        user_anti = set(selected_list[len(user_library): len(user_library) + anti_size])

        library_by_user[user_id] = user_library
        anti_by_user[user_id] = user_anti

        for game_id in user_library:
            added_at = random_dt(max(registered_at, cfg.start_date), cfg.end_date)
            source = weighted_choice(
                ["catalog", "review", "friend_library", "promo", "search"],
                [0.36, 0.22, 0.16, 0.16, 0.10],
            )

            library_rows.append(
                {
                    "library_id": f"lib_{len(library_rows) + 1:010d}",
                    "user_id": user_id,
                    "game_id": game_id,
                    "added_at": dt_to_iso(added_at),
                    "source": maybe_none(source, cfg, 0.9),
                    "is_wishlist": maybe_none(random.random() < 0.22, cfg, 0.35),
                }
            )

        for game_id in user_anti:
            added_at = random_dt(max(registered_at, cfg.start_date), cfg.end_date)
            anti_rows.append(
                {
                    "anti_library_id": f"anti_{len(anti_rows) + 1:010d}",
                    "user_id": user_id,
                    "game_id": game_id,
                    "added_at": dt_to_iso(added_at),
                    "reason": maybe_none(
                        weighted_choice(
                            ["not_interested", "too_expensive", "bad_reviews", "wrong_genre", "already_played_elsewhere"],
                            [0.46, 0.18, 0.16, 0.14, 0.06],
                        ),
                        cfg,
                        1.25,
                    ),
                }
            )

    return library_rows, anti_rows, library_by_user, anti_by_user


def make_game_stats_and_reviews(
    cfg: Config,
    library_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stats_rows = []
    review_rows = []

    for row in library_rows:
        user_id = row["user_id"]
        game_id = row["game_id"]
        added_at = datetime.fromisoformat(row["added_at"].replace("Z", "+00:00"))

        status = weighted_choice(
            COMPLETION_STATUSES,
            [0.18, 0.46, 0.22, 0.14],
        )

        if status == "not_started":
            playtime = 0
            last_played_at = None
        elif status == "playing":
            playtime = random.randint(15, 6000)
            last_played_at = random_dt(added_at, cfg.end_date)
        elif status == "completed":
            playtime = random.randint(240, 20000)
            last_played_at = random_dt(added_at, cfg.end_date)
        else:
            playtime = random.randint(10, 3000)
            last_played_at = random_dt(added_at, cfg.end_date)

        achievements_total = random.randint(10, 80)
        achievements_unlocked = 0 if playtime == 0 else random.randint(0, achievements_total)

        stats_rows.append(
            {
                "user_id": user_id,
                "game_id": game_id,
                "completion_status": status,
                "playtime_minutes": playtime,
                "sessions_count": maybe_none(0 if playtime == 0 else random.randint(1, max(1, playtime // 20)), cfg, 0.25),
                "first_played_at": None if playtime == 0 else maybe_none(dt_to_iso(random_dt(added_at, cfg.end_date)), cfg, 0.25),
                "last_played_at": None if last_played_at is None else maybe_none(dt_to_iso(last_played_at), cfg, 0.25),
                "achievements_total": maybe_none(achievements_total, cfg, 0.2),
                "achievements_unlocked": maybe_none(achievements_unlocked, cfg, 0.2),
            }
        )

        can_review = playtime >= 30 and random.random() < 0.28
        if can_review:
            created_at = random_dt(added_at, cfg.end_date)
            rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.22, 0.36, 0.27], k=1)[0]
            review_rows.append(
                {
                    "review_id": f"rev_{len(review_rows) + 1:010d}",
                    "user_id": user_id,
                    "game_id": game_id,
                    "rating": rating,
                    "review_text": f"synthetic review with rating {rating} for {game_id}",
                    "created_at": dt_to_iso(created_at),
                    "updated_at": maybe_none(dt_to_iso(created_at + timedelta(days=random.randint(0, 30))), cfg, 0.9),
                    "is_spoiler": maybe_none(random.random() < 0.08, cfg, 0.25),
                    "likes_count": maybe_none(random.randint(0, 500), cfg, 0.2),
                    "dislikes_count": maybe_none(random.randint(0, 80), cfg, 0.2),
                }
            )

    return stats_rows, review_rows


def make_campaigns(
    cfg: Config,
    games: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    promotable_games = [g for g in games if g["publication_status"] in {"published", "early_access"}]
    campaigns = []

    for i in range(1, cfg.campaigns + 1):
        game = random.choice(promotable_games)
        start_at = random_dt(cfg.start_date + timedelta(days=60), cfg.end_date - timedelta(days=14))
        duration_days = random.randint(7, 45)
        end_at = min(start_at + timedelta(days=duration_days), cfg.end_date)

        campaigns.append(
            {
                "campaign_id": f"camp_{i:08d}",
                "developer_id": game["developer_id"],
                "game_id": game["game_id"],
                "placement": random.choice(PLACEMENTS),
                "started_at": dt_to_iso(start_at),
                "ended_at": dt_to_iso(end_at),
                "budget_usd": maybe_none(round(random.uniform(100, 10000), 2), cfg, 0.2),
                "bid_cpc_usd": maybe_none(round(random.uniform(0.05, 2.50), 2), cfg, 0.45),
                "target_country": maybe_dirty_country(random.choice(COUNTRIES + ["all"]), cfg),
                "campaign_status": "finished" if end_at < cfg.end_date else "active",
            }
        )

    return campaigns


def make_events(
    cfg: Config,
    users: list[dict[str, Any]],
    games: list[dict[str, Any]],
    campaigns: list[dict[str, Any]],
    library_rows: list[dict[str, Any]],
    anti_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    active_user_ids = [u["user_id"] for u in users if u["account_status"] == "active"]
    game_ids = [g["game_id"] for g in games if g["publication_status"] in {"published", "early_access"}]
    campaign_by_id = {c["campaign_id"]: c for c in campaigns}
    campaign_ids = list(campaign_by_id.keys())
    review_ids = [r["review_id"] for r in review_rows]

    events: list[dict[str, Any]] = []

    def add_event(
        event_type: str,
        user_id: str | None,
        game_id: str | None,
        occurred_at: datetime,
        campaign_id: str | None = None,
        review_id: str | None = None,
        source: str | None = None,
        reason: str | None = None,
        page: str | None = None,
        referrer: str | None = None,
        placement: str | None = None,
        target_country: str | None = None,
        review_reaction: str | None = None,
    ) -> None:
        event_id = f"evt_{len(events) + 1:012d}"
        payload = {
            "event_id": event_id,
            "event_type": event_type,
            "occurred_at": dt_to_iso(occurred_at),
            "user_id": user_id,
            "game_id": game_id,
            "campaign_id": campaign_id,
            "review_id": review_id,
            "session_id": f"s_{random.randint(1, max(cfg.users * 5, 1)):010d}",
            "device_type": maybe_none(weighted_choice(["desktop", "mobile", "tablet", "console"], [0.58, 0.24, 0.06, 0.12]), cfg, 0.35),
            "country": maybe_dirty_country(random.choice(COUNTRIES), cfg),
            "source": source,
            "reason": reason,
            "page": page,
            "referrer": referrer,
            "placement": placement,
            "target_country": target_country,
            "review_reaction": review_reaction,
        }
        events.append(payload)

    # Deterministic business events from source rows.
    # These make library and anti-library changes visible in event tracking.
    for row in library_rows:
        if random.random() < 0.95:
            add_event(
                event_type="library_add",
                user_id=row["user_id"],
                game_id=row["game_id"],
                occurred_at=datetime.fromisoformat(row["added_at"].replace("Z", "+00:00")),
                source=row["source"],
            )

    for row in anti_rows:
        if random.random() < 0.90:
            add_event(
                event_type="anti_library_add",
                user_id=row["user_id"],
                game_id=row["game_id"],
                occurred_at=datetime.fromisoformat(row["added_at"].replace("Z", "+00:00")),
                reason=row["reason"],
            )

    # Random behavioral events until required volume.
    while len(events) < cfg.events:
        event_type = weighted_choice(
            EVENT_TYPES,
            [0.56, 0.05, 0.03, 0.16, 0.16, 0.04],
        )

        user_id = random.choice(active_user_ids) if random.random() < 0.86 else None
        occurred_at = random_dt(cfg.start_date, cfg.end_date)

        if event_type in {"promo_impression", "promo_click"} and campaign_ids:
            campaign_id = random.choice(campaign_ids)
            campaign = campaign_by_id[campaign_id]
            campaign_start = datetime.fromisoformat(campaign["started_at"].replace("Z", "+00:00"))
            campaign_end = datetime.fromisoformat(campaign["ended_at"].replace("Z", "+00:00"))
            occurred_at = random_dt(campaign_start, campaign_end)
            add_event(
                event_type=event_type,
                user_id=user_id,
                game_id=campaign["game_id"],
                occurred_at=occurred_at,
                campaign_id=campaign_id,
                placement=campaign["placement"],
                target_country=campaign["target_country"],
            )

        elif event_type == "review_view" and review_ids:
            review = random.choice(review_rows)
            add_event(
                event_type=event_type,
                user_id=user_id,
                game_id=review["game_id"],
                occurred_at=occurred_at,
                review_id=review["review_id"],
                review_reaction=weighted_choice(REVIEW_REACTIONS + ["none"], [0.14, 0.04, 0.05, 0.12, 0.65]),
            )

        else:
            add_event(
                event_type=event_type,
                user_id=user_id,
                game_id=random.choice(game_ids),
                occurred_at=occurred_at,
                page=random.choice(["catalog", "game", "genre", "search", "recommendations"]),
                referrer=random.choice(["direct", "search", "friend", "promo", "review"]),
            )

    events.sort(key=lambda e: e["occurred_at"])
    return events


def validate_consistency(
    users: list[dict[str, Any]],
    developers: list[dict[str, Any]],
    games: list[dict[str, Any]],
    published_games: list[dict[str, Any]],
    genre_rows: list[dict[str, Any]],
    tag_rows: list[dict[str, Any]],
    platform_rows: list[dict[str, Any]],
    language_rows: list[dict[str, Any]],
    game_genre_rows: list[dict[str, Any]],
    game_tag_rows: list[dict[str, Any]],
    game_platform_rows: list[dict[str, Any]],
    game_language_rows: list[dict[str, Any]],
    library_rows: list[dict[str, Any]],
    anti_rows: list[dict[str, Any]],
    stats_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    campaigns: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> None:
    user_ids = {u["user_id"] for u in users}
    developer_ids = {d["developer_id"] for d in developers}
    game_ids = {g["game_id"] for g in games}
    genre_ids = {g["genre_id"] for g in genre_rows}
    tag_ids = {t["tag_id"] for t in tag_rows}
    platform_ids = {p["platform_id"] for p in platform_rows}
    language_ids = {l["language_id"] for l in language_rows}
    game_to_dev = {g["game_id"]: g["developer_id"] for g in games}
    campaign_ids = {c["campaign_id"] for c in campaigns}
    review_ids = {r["review_id"] for r in review_rows}

    library_pairs = {(r["user_id"], r["game_id"]) for r in library_rows}
    anti_pairs = {(r["user_id"], r["game_id"]) for r in anti_rows}
    stats_pairs = {(r["user_id"], r["game_id"]) for r in stats_rows}

    errors = []

    if library_pairs & anti_pairs:
        errors.append("some user-game pairs exist both in library and anti-library")

    for row in games:
        if row["developer_id"] not in developer_ids:
            errors.append(f"game {row['game_id']} has missing developer_id")

        if row["added_by_type"] not in {"developer", "user"}:
            errors.append(f"game {row['game_id']} has invalid added_by_type")

        if row["added_by_type"] == "developer":
            if row["added_by_developer_id"] != row["developer_id"]:
                errors.append(f"game {row['game_id']} added by developer mismatch")
            if row["added_by_user_id"] is not None:
                errors.append(f"game {row['game_id']} has user adder for developer-added game")

        if row["added_by_type"] == "user":
            if row["added_by_user_id"] not in user_ids:
                errors.append(f"game {row['game_id']} has missing added_by_user_id")
            if row["added_by_developer_id"] is not None:
                errors.append(f"game {row['game_id']} has developer adder for user-added game")

    developer_added_game_ids = {
        row["game_id"]
        for row in games
        if row["added_by_type"] == "developer"
    }
    developer_portal_game_ids = {row["game_id"] for row in published_games}

    if developer_portal_game_ids != developer_added_game_ids:
        errors.append("developer_portal/published_games.csv must contain exactly developer-added games")

    for row in published_games:
        if row["developer_id"] not in developer_ids:
            errors.append(f"published game {row['game_id']} has missing developer_id")
        if row["game_id"] not in game_ids:
            errors.append(f"published game {row['game_id']} is missing in catalog")
        if row["game_id"] in game_to_dev and row["developer_id"] != game_to_dev[row["game_id"]]:
            errors.append(f"published game {row['game_id']} developer mismatch")
        if row["game_id"] not in developer_added_game_ids:
            errors.append(f"published game {row['game_id']} was not added by developer")

    game_genre_pairs = {(row["game_id"], row["genre_id"]) for row in game_genre_rows}
    game_tag_pairs = {(row["game_id"], row["tag_id"]) for row in game_tag_rows}
    game_platform_pairs = {(row["game_id"], row["platform_id"]) for row in game_platform_rows}
    game_language_pairs = {(row["game_id"], row["language_id"]) for row in game_language_rows}

    if len(game_genre_pairs) != len(game_genre_rows):
        errors.append("game_genres.csv has duplicate game_id + genre_id pairs")

    if len(game_tag_pairs) != len(game_tag_rows):
        errors.append("game_tags.csv has duplicate game_id + tag_id pairs")

    if len(game_platform_pairs) != len(game_platform_rows):
        errors.append("game_platforms.csv has duplicate game_id + platform_id pairs")

    if len(game_language_pairs) != len(game_language_rows):
        errors.append("game_languages.csv has duplicate game_id + language_id pairs")

    games_with_genre = {row["game_id"] for row in game_genre_rows}
    games_with_primary_genre = {row["game_id"] for row in game_genre_rows if row["is_primary"] is True}
    games_with_platform = {row["game_id"] for row in game_platform_rows}
    games_with_language = {row["game_id"] for row in game_language_rows}

    for game_id in game_ids:
        if game_id not in games_with_genre:
            errors.append(f"game {game_id} has no genres")
        if game_id not in games_with_primary_genre:
            errors.append(f"game {game_id} has no primary genre")
        if game_id not in games_with_platform:
            errors.append(f"game {game_id} has no platforms")
        if game_id not in games_with_language:
            errors.append(f"game {game_id} has no languages")

    for row in game_genre_rows:
        if row["game_id"] not in game_ids:
            errors.append(f"game_genres row has missing game_id {row['game_id']}")
        if row["genre_id"] not in genre_ids:
            errors.append(f"game_genres row has missing genre_id {row['genre_id']}")

    for row in game_tag_rows:
        if row["game_id"] not in game_ids:
            errors.append(f"game_tags row has missing game_id {row['game_id']}")
        if row["tag_id"] not in tag_ids:
            errors.append(f"game_tags row has missing tag_id {row['tag_id']}")

    for row in game_platform_rows:
        if row["game_id"] not in game_ids:
            errors.append(f"game_platforms row has missing game_id {row['game_id']}")
        if row["platform_id"] not in platform_ids:
            errors.append(f"game_platforms row has missing platform_id {row['platform_id']}")

    for row in game_language_rows:
        if row["game_id"] not in game_ids:
            errors.append(f"game_languages row has missing game_id {row['game_id']}")
        if row["language_id"] not in language_ids:
            errors.append(f"game_languages row has missing language_id {row['language_id']}")

    for row in library_rows + anti_rows:
        if row["user_id"] not in user_ids:
            errors.append(f"user-game row has missing user_id {row['user_id']}")
        if row["game_id"] not in game_ids:
            errors.append(f"user-game row has missing game_id {row['game_id']}")

    for row in stats_rows:
        if (row["user_id"], row["game_id"]) not in library_pairs:
            errors.append(f"stats row is not based on library pair: {row['user_id']}, {row['game_id']}")

    for row in users:
        if not row["username"]:
            errors.append(f"user {row['user_id']} has empty username")
        if not row["email"]:
            errors.append(f"user {row['user_id']} has empty email")

    for row in review_rows:
        if (row["user_id"], row["game_id"]) not in library_pairs:
            errors.append(f"review row is not based on library pair: {row['user_id']}, {row['game_id']}")
        if not row["review_text"]:
            errors.append(f"review {row['review_id']} has empty review_text")
        if row["rating"] is None:
            errors.append(f"review {row['review_id']} has empty rating")
        if row["rating"] is not None and not 1 <= int(row["rating"]) <= 5:
            errors.append(f"review {row['review_id']} has invalid rating")

    for row in campaigns:
        if row["game_id"] not in game_ids:
            errors.append(f"campaign {row['campaign_id']} has missing game_id")
        if row["developer_id"] != game_to_dev.get(row["game_id"]):
            errors.append(f"campaign {row['campaign_id']} developer does not own game")

    for row in events:
        if row["user_id"] is not None and row["user_id"] not in user_ids:
            errors.append(f"event {row['event_id']} has missing user_id")
        if row["game_id"] is not None and row["game_id"] not in game_ids:
            errors.append(f"event {row['event_id']} has missing game_id")
        if row["campaign_id"] is not None and row["campaign_id"] not in campaign_ids:
            errors.append(f"event {row['event_id']} has missing campaign_id")
        if row["review_id"] is not None and row["review_id"] not in review_ids:
            errors.append(f"event {row['event_id']} has missing review_id")

    if errors:
        preview = "\n".join(errors[:20])
        raise ValueError(f"consistency validation failed, first errors:\n{preview}")


def save_outputs(
    dirs: dict[str, Path],
    users: list[dict[str, Any]],
    developers: list[dict[str, Any]],
    games: list[dict[str, Any]],
    published_games: list[dict[str, Any]],
    genre_rows: list[dict[str, Any]],
    tag_rows: list[dict[str, Any]],
    platform_rows: list[dict[str, Any]],
    language_rows: list[dict[str, Any]],
    game_genre_rows: list[dict[str, Any]],
    game_tag_rows: list[dict[str, Any]],
    game_platform_rows: list[dict[str, Any]],
    game_language_rows: list[dict[str, Any]],
    library_rows: list[dict[str, Any]],
    anti_rows: list[dict[str, Any]],
    stats_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    campaigns: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> None:
    write_csv(
        dirs["user_service"] / "users.csv",
        users,
        ["user_id", "username", "email", "country", "birth_year", "registered_at", "account_status"],
    )

    write_csv(
        dirs["developer_portal"] / "developers.csv",
        developers,
        ["developer_id", "studio_name", "country", "created_at", "verification_status"],
    )

    write_csv(
        dirs["developer_portal"] / "published_games.csv",
        published_games,
        ["developer_id", "game_id", "submitted_at", "published_at", "publication_status", "moderation_score"],
    )

    with (dirs["game_catalog"] / "games.json").open("w", encoding="utf-8") as file:
        json.dump(games, file, ensure_ascii=False, indent=2)

    write_csv(
        dirs["game_catalog"] / "genres.csv",
        genre_rows,
        ["genre_id", "genre_name", "created_at"],
    )

    write_csv(
        dirs["game_catalog"] / "tags.csv",
        tag_rows,
        ["tag_id", "tag_name", "created_at"],
    )

    write_csv(
        dirs["game_catalog"] / "platforms.csv",
        platform_rows,
        ["platform_id", "platform_name", "created_at"],
    )

    write_csv(
        dirs["game_catalog"] / "languages.csv",
        language_rows,
        ["language_id", "language_code", "created_at"],
    )

    write_csv(
        dirs["game_catalog"] / "game_genres.csv",
        game_genre_rows,
        ["game_id", "genre_id", "is_primary", "position"],
    )

    write_csv(
        dirs["game_catalog"] / "game_tags.csv",
        game_tag_rows,
        ["game_id", "tag_id"],
    )

    write_csv(
        dirs["game_catalog"] / "game_platforms.csv",
        game_platform_rows,
        ["game_id", "platform_id"],
    )

    write_csv(
        dirs["game_catalog"] / "game_languages.csv",
        game_language_rows,
        ["game_id", "language_id"],
    )

    write_csv(
        dirs["library_service"] / "library.csv",
        library_rows,
        ["library_id", "user_id", "game_id", "added_at", "source", "is_wishlist"],
    )

    write_ndjson(dirs["anti_library_service"] / "anti_library.ndjson", anti_rows)

    write_csv(
        dirs["reviews_service"] / "reviews.csv",
        review_rows,
        [
            "review_id", "user_id", "game_id", "rating", "review_text", "created_at",
            "updated_at", "is_spoiler", "likes_count", "dislikes_count",
        ],
    )

    pd.DataFrame(stats_rows).to_parquet(
        dirs["game_stats"] / "game_stats.parquet",
        index=False,
        engine="pyarrow",
    )

    write_csv(
        dirs["promotion_system"] / "promo_campaigns.csv",
        campaigns,
        [
            "campaign_id", "developer_id", "game_id", "placement", "started_at",
            "ended_at", "budget_usd", "bid_cpc_usd", "target_country", "campaign_status",
        ],
    )

    write_ndjson_gz(dirs["product_analytics"] / "events.ndjson.gz", events)


def print_summary(out: Path, rows_count: dict[str, int]) -> None:
    print(f"generated GameHub source files in: {out.resolve()}")
    for name, count in rows_count.items():
        print(f"{name}: {count}")


def parse_args() -> Config:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/raw"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--users", type=int, default=3000)
    parser.add_argument("--developers", type=int, default=120)
    parser.add_argument("--games", type=int, default=600)
    parser.add_argument("--library-min", type=int, default=2)
    parser.add_argument("--library-max", type=int, default=25)
    parser.add_argument("--anti-library-min", type=int, default=0)
    parser.add_argument("--anti-library-max", type=int, default=8)
    parser.add_argument("--campaigns", type=int, default=250)
    parser.add_argument("--events", type=int, default=150000)
    parser.add_argument("--dirty-rate", type=float, default=0.03)
    parser.add_argument("--start-date", type=str, default="2025-01-01")
    parser.add_argument("--end-date", type=str, default="2026-06-01")

    args = parser.parse_args()

    start_date = datetime.fromisoformat(args.start_date).replace(tzinfo=timezone.utc)
    end_date = datetime.fromisoformat(args.end_date).replace(tzinfo=timezone.utc)

    if start_date >= end_date:
        raise ValueError("--start-date must be before --end-date")

    if args.users < 1 or args.developers < 1 or args.games < 1:
        raise ValueError("--users, --developers and --games must be positive")

    if args.library_min < 0 or args.library_max < args.library_min:
        raise ValueError("invalid library range")

    if args.anti_library_min < 0 or args.anti_library_max < args.anti_library_min:
        raise ValueError("invalid anti-library range")

    if args.library_max + args.anti_library_max > args.games:
        raise ValueError("--library-max + --anti-library-max must be <= --games")

    if not 0 <= args.dirty_rate <= 0.2:
        raise ValueError("--dirty-rate must be between 0 and 0.2")

    return Config(
        out=args.out,
        seed=args.seed,
        users=args.users,
        developers=args.developers,
        games=args.games,
        library_min=args.library_min,
        library_max=args.library_max,
        anti_library_min=args.anti_library_min,
        anti_library_max=args.anti_library_max,
        campaigns=args.campaigns,
        events=args.events,
        dirty_rate=args.dirty_rate,
        start_date=start_date,
        end_date=end_date,
    )


def main() -> None:
    cfg = parse_args()
    random.seed(cfg.seed)

    dirs = ensure_dirs(cfg.out)

    users = make_users(cfg)
    developers = make_developers(cfg)
    (
        games,
        published_games,
        genre_rows,
        tag_rows,
        platform_rows,
        language_rows,
        game_genre_rows,
        game_tag_rows,
        game_platform_rows,
        game_language_rows,
    ) = make_games(cfg, users, developers)
    library_rows, anti_rows, _, _ = make_user_game_sets(cfg, users, games)
    stats_rows, review_rows = make_game_stats_and_reviews(cfg, library_rows)
    campaigns = make_campaigns(cfg, games)
    events = make_events(cfg, users, games, campaigns, library_rows, anti_rows, review_rows)

    validate_consistency(
        users=users,
        developers=developers,
        games=games,
        published_games=published_games,
        genre_rows=genre_rows,
        tag_rows=tag_rows,
        platform_rows=platform_rows,
        language_rows=language_rows,
        game_genre_rows=game_genre_rows,
        game_tag_rows=game_tag_rows,
        game_platform_rows=game_platform_rows,
        game_language_rows=game_language_rows,
        library_rows=library_rows,
        anti_rows=anti_rows,
        stats_rows=stats_rows,
        review_rows=review_rows,
        campaigns=campaigns,
        events=events,
    )

    save_outputs(
        dirs=dirs,
        users=users,
        developers=developers,
        games=games,
        published_games=published_games,
        genre_rows=genre_rows,
        tag_rows=tag_rows,
        platform_rows=platform_rows,
        language_rows=language_rows,
        game_genre_rows=game_genre_rows,
        game_tag_rows=game_tag_rows,
        game_platform_rows=game_platform_rows,
        game_language_rows=game_language_rows,
        library_rows=library_rows,
        anti_rows=anti_rows,
        stats_rows=stats_rows,
        review_rows=review_rows,
        campaigns=campaigns,
        events=events,
    )

    print(f"soft dirty data rate: {cfg.dirty_rate}")
    print_summary(
        cfg.out,
        {
            "users.csv": len(users),
            "developers.csv": len(developers),
            "published_games.csv": len(published_games),
            "games.json": len(games),
            "developer_added_games": sum(1 for row in games if row["added_by_type"] == "developer"),
            "user_added_games": sum(1 for row in games if row["added_by_type"] == "user"),
            "genres.csv": len(genre_rows),
            "tags.csv": len(tag_rows),
            "platforms.csv": len(platform_rows),
            "languages.csv": len(language_rows),
            "game_genres.csv": len(game_genre_rows),
            "game_tags.csv": len(game_tag_rows),
            "game_platforms.csv": len(game_platform_rows),
            "game_languages.csv": len(game_language_rows),
            "library.csv": len(library_rows),
            "anti_library.ndjson": len(anti_rows),
            "reviews.csv": len(review_rows),
            "game_stats.parquet": len(stats_rows),
            "promo_campaigns.csv": len(campaigns),
            "events.ndjson.gz": len(events),
        },
    )


if __name__ == "__main__":
    main()
