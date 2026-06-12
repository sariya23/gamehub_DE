#!/usr/bin/env python3
"""
Synthetic data generator for the GameHub DE educational project.

It creates file-based source exports:

data/raw/
├── user_service/
│   └── users.csv
├── developer_portal/
│   ├── developers.csv
│   └── published_games.csv
├── game_catalog/
│   └── games.json
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
    python generate_gamehub_data.py --users 10000 --games 1000 --developers 200 --out data/raw
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

PLATFORMS = [
    "windows", "macos", "linux", "steam_deck",
    "playstation", "xbox", "nintendo_switch",
]
LANGUAGES = ["en", "ru", "de", "fr", "es", "pt", "ja", "ko", "zh"]
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
    start_date: datetime
    end_date: datetime


def dt_to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def random_dt(start: datetime, end: datetime) -> datetime:
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, max(delta_seconds, 0)))


def weighted_choice(items: list[str], weights: list[float]) -> str:
    return random.choices(items, weights=weights, k=1)[0]


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
                "country": random.choice(COUNTRIES),
                "birth_year": random.randint(1975, 2012),
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
                "studio_name": f"{random.choice(prefixes)}_{random.choice(suffixes)}_{i:04d}",
                "country": random.choice(COUNTRIES),
                "created_at": dt_to_iso(created_at),
                "verification_status": weighted_choice(
                    ["verified", "pending", "rejected"],
                    [0.72, 0.23, 0.05],
                ),
            }
        )

    return developers


def make_games(cfg: Config, developers: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    adjectives = [
        "ancient", "neon", "silent", "broken", "cosmic", "tiny", "lost", "furious",
        "hidden", "crimson", "golden", "frozen", "electric", "lonely", "wild",
    ]
    nouns = [
        "kingdom", "voyage", "arena", "dungeon", "frontier", "factory", "legacy",
        "storm", "signal", "island", "station", "garden", "citadel", "planet", "archive",
    ]

    verified_devs = [d for d in developers if d["verification_status"] != "rejected"]
    if not verified_devs:
        verified_devs = developers

    games = []
    published_games = []

    for i in range(1, cfg.games + 1):
        game_id = f"g_{i:07d}"
        developer = random.choice(verified_devs)
        release_date = random_dt(cfg.start_date + timedelta(days=30), cfg.end_date - timedelta(days=5))
        main_genre = random.choice(GENRES)
        other_genres = random.sample([g for g in GENRES if g != main_genre], k=random.randint(0, 2))
        game_genres = [main_genre] + other_genres
        game_tags = random.sample(TAGS, k=random.randint(3, 8))

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
                "description": f"Synthetic {main_genre} game generated for GameHub data engineering practice.",
                "genres": game_genres,
                "tags": game_tags,
                "platforms": random.sample(PLATFORMS, k=random.randint(1, len(PLATFORMS))),
                "languages": random.sample(LANGUAGES, k=random.randint(1, min(5, len(LANGUAGES)))),
                "age_rating": random.choice(["3+", "7+", "12+", "16+", "18+"]),
                "price_usd": price,
                "release_date": release_date.date().isoformat(),
                "catalog_created_at": dt_to_iso(release_date - timedelta(days=random.randint(7, 120))),
                "is_free": price == 0,
                "publication_status": publication_status,
            }
        )

        published_games.append(
            {
                "developer_id": developer["developer_id"],
                "game_id": game_id,
                "submitted_at": dt_to_iso(release_date - timedelta(days=random.randint(7, 120))),
                "published_at": dt_to_iso(release_date),
                "publication_status": publication_status,
                "moderation_score": round(random.uniform(0.55, 0.99), 3),
            }
        )

    return games, published_games


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
                    "source": source,
                    "is_wishlist": random.random() < 0.22,
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
                    "reason": weighted_choice(
                        ["not_interested", "too_expensive", "bad_reviews", "wrong_genre", "already_played_elsewhere"],
                        [0.46, 0.18, 0.16, 0.14, 0.06],
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
                "sessions_count": 0 if playtime == 0 else random.randint(1, max(1, playtime // 20)),
                "first_played_at": None if playtime == 0 else dt_to_iso(random_dt(added_at, cfg.end_date)),
                "last_played_at": None if last_played_at is None else dt_to_iso(last_played_at),
                "achievements_total": achievements_total,
                "achievements_unlocked": achievements_unlocked,
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
                    "updated_at": dt_to_iso(created_at + timedelta(days=random.randint(0, 30))),
                    "is_spoiler": random.random() < 0.08,
                    "likes_count": random.randint(0, 500),
                    "dislikes_count": random.randint(0, 80),
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
                "budget_usd": round(random.uniform(100, 10000), 2),
                "bid_cpc_usd": round(random.uniform(0.05, 2.50), 2),
                "target_country": random.choice(COUNTRIES + ["all"]),
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
        extra: dict[str, Any] | None = None,
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
            "device_type": weighted_choice(["desktop", "mobile", "tablet", "console"], [0.58, 0.24, 0.06, 0.12]),
            "country": random.choice(COUNTRIES),
            "properties": extra or {},
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
                extra={"source": row["source"]},
            )

    for row in anti_rows:
        if random.random() < 0.90:
            add_event(
                event_type="anti_library_add",
                user_id=row["user_id"],
                game_id=row["game_id"],
                occurred_at=datetime.fromisoformat(row["added_at"].replace("Z", "+00:00")),
                extra={"reason": row["reason"]},
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
                extra={
                    "placement": campaign["placement"],
                    "target_country": campaign["target_country"],
                },
            )

        elif event_type == "review_view" and review_ids:
            review = random.choice(review_rows)
            add_event(
                event_type=event_type,
                user_id=user_id,
                game_id=review["game_id"],
                occurred_at=occurred_at,
                review_id=review["review_id"],
                extra={
                    "reaction": weighted_choice(REVIEW_REACTIONS + ["none"], [0.14, 0.04, 0.05, 0.12, 0.65]),
                },
            )

        else:
            add_event(
                event_type=event_type,
                user_id=user_id,
                game_id=random.choice(game_ids),
                occurred_at=occurred_at,
                extra={
                    "page": random.choice(["catalog", "game", "genre", "search", "recommendations"]),
                    "referrer": random.choice(["direct", "search", "friend", "promo", "review"]),
                },
            )

    events.sort(key=lambda e: e["occurred_at"])
    return events


def validate_consistency(
    users: list[dict[str, Any]],
    developers: list[dict[str, Any]],
    games: list[dict[str, Any]],
    published_games: list[dict[str, Any]],
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

    for row in published_games:
        if row["developer_id"] not in developer_ids:
            errors.append(f"published game {row['game_id']} has missing developer_id")
        if row["game_id"] not in game_ids:
            errors.append(f"published game {row['game_id']} is missing in catalog")
        if row["game_id"] in game_to_dev and row["developer_id"] != game_to_dev[row["game_id"]]:
            errors.append(f"published game {row['game_id']} developer mismatch")

    for row in library_rows + anti_rows:
        if row["user_id"] not in user_ids:
            errors.append(f"user-game row has missing user_id {row['user_id']}")
        if row["game_id"] not in game_ids:
            errors.append(f"user-game row has missing game_id {row['game_id']}")

    for row in stats_rows:
        if (row["user_id"], row["game_id"]) not in library_pairs:
            errors.append(f"stats row is not based on library pair: {row['user_id']}, {row['game_id']}")

    for row in review_rows:
        if (row["user_id"], row["game_id"]) not in library_pairs:
            errors.append(f"review row is not based on library pair: {row['user_id']}, {row['game_id']}")

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
        start_date=start_date,
        end_date=end_date,
    )


def main() -> None:
    cfg = parse_args()
    random.seed(cfg.seed)

    dirs = ensure_dirs(cfg.out)

    users = make_users(cfg)
    developers = make_developers(cfg)
    games, published_games = make_games(cfg, developers)
    library_rows, anti_rows, _, _ = make_user_game_sets(cfg, users, games)
    stats_rows, review_rows = make_game_stats_and_reviews(cfg, library_rows)
    campaigns = make_campaigns(cfg, games)
    events = make_events(cfg, users, games, campaigns, library_rows, anti_rows, review_rows)

    validate_consistency(
        users=users,
        developers=developers,
        games=games,
        published_games=published_games,
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
        library_rows=library_rows,
        anti_rows=anti_rows,
        stats_rows=stats_rows,
        review_rows=review_rows,
        campaigns=campaigns,
        events=events,
    )

    print_summary(
        cfg.out,
        {
            "users.csv": len(users),
            "developers.csv": len(developers),
            "published_games.csv": len(published_games),
            "games.json": len(games),
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
