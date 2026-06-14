# GameHub

## Содержание

- [GameHub](#gamehub)
  - [Содержание](#содержание)
  - [Доменная область](#доменная-область)
    - [Сценарии аналитик и бизнес-вопросы](#сценарии-аналитик-и-бизнес-вопросы)
    - [Боли](#боли)
    - [Источники данных](#источники-данных)
    - [Основные сущности](#основные-сущности)
      - [Пользователь](#пользователь)
      - [Профиль пользователя](#профиль-пользователя)
      - [Подписка / дружба](#подписка--дружба)
      - [Игра](#игра)
      - [Жанр](#жанр)
      - [Тег](#тег)
      - [Разработчик](#разработчик)
      - [Библиотека](#библиотека)
      - [Антибиблиотека](#антибиблиотека)
      - [Статус прохождения](#статус-прохождения)
      - [Игровая статистика](#игровая-статистика)
      - [Рецензия](#рецензия)
      - [Реакция на рецензию](#реакция-на-рецензию)
      - [Просмотр / клик / событие](#просмотр--клик--событие)
      - [Промо-кампания](#промо-кампания)
      - [Промо-показ](#промо-показ)
      - [Промо-клик](#промо-клик)
  - [Техническая информация](#техническая-информация)
    - [Источники данных](#источники-данных-1)
    - [Описание данных](#описание-данных)
      - [Users](#users)
      - [Anti Library](#anti-library)
      - [Developers](#developers)
        - [Developers](#developers-1)
        - [Published Games](#published-games)
      - [Game Catalog](#game-catalog)
        - [Games](#games)
        - [Tags](#tags)
        - [Genres](#genres)
        - [Platforms](#platforms)
        - [Languages](#languages)
        - [Game tags](#game-tags)
        - [Game genres](#game-genres)
        - [Game platforms](#game-platforms)
        - [Game languages](#game-languages)
      - [Game stats](#game-stats)
      - [Library](#library)
      - [Promoution](#promoution)
        - [Promo campaigns](#promo-campaigns)
      - [Product analytics](#product-analytics)
        - [Events](#events)
      - [Reviews](#reviews)

## Доменная область

GameHub — это платформа для игроков и независимых разработчиков игр. Игроки могут вести игровую библиотеку и антибиблиотеку, фиксировать игровой опыт, писать рецензии, читать рецензии других пользователей и смотреть личную статистику: любимые жанры, время в играх, статус прохождения и активность.

Также GameHub позволяет новым разработчикам публиковать свои игры, получать первые реакции игроков, анализировать интерес аудитории и продвигать свои проекты внутри платформы. Разработчикам доступны инструменты аналитики: просмотры страницы игры, добавления в библиотеку, рецензии, оценки, динамика интереса и эффективность продвижения.

### Сценарии аналитик и бизнес-вопросы

Нам нужны данные, чтобы:

1. Что интересно игрокам, самые популярыне жанры, наибольшая конверсия от рецензий и их авторов к привлечению к игре
2. Насколько наша платформа помогает разработчкам продвигать свои игры

Бизнез-вопросы:
1. Какие игры чаще всего добавляют в библиотеку?
2. Какие игры чаще всего добавляют в антибиблиотеку?
3. Какие игры получают много просмотров, но мало добавлений в библиотеку?
4. Какие игры получают мало просмотров, но высокий процент добавлений?
5. Какие жанры лучше всего заходят пользователям?
6. Какие рецензии влияют на интерес к игре?
7. Какие игры молодых разработчиков получают лучший отклик?
8. Какие промо-кампании дают лучший результат: просмотры, клики, добавления в библиотеку и переходы к игре?

### Боли

- Нет self-BI
- Владение данными
- Долгое и неудобное формирование отчетов

### Источники данных

1. User Platform — пользователи, профили, друзья/подписки.
2. Library Service — игры, которые пользователь добавил к себе, которые интересные.
3. Anti Library Service – игры, которые юзеру не интересны
4. Game Catalog — вся информация об играх.
5. Reviews Service — рецензии, оценки, реакции.
6. Game Stats — время в игре, статусы прохождения.
7. Developer Portal — аккаунты разработчиков, опубликованные игры, аналитика.
8. Promotion System — промо-кампании, бюджеты, размещения.
9. Product Analytics / Event Tracking — просмотры, клики, показы, действия на сайте.

### Основные сущности

#### Пользователь
Игрок, который использует платформу.

#### Профиль пользователя
Публичная информация: ник, страна, язык, дата регистрации, описание.

#### Подписка / дружба
Связь между пользователями: кто на кого подписан или кто с кем дружит.

#### Игра
Вся информация об игре

#### Жанр
Жанры игры: rpg, strategy, horror, action и так далее.

#### Тег
Более гибкие признаки: indie, pixel art, roguelike, story rich, co-op.

#### Разработчик
Человек или студия, которые публикуют игру.

#### Библиотека
Факт, что пользователь добавил игру к себе.

#### Антибиблиотека
Факт, что пользователь не хочет видеть игру или не хочет в нее играть.

#### Статус прохождения
Состояние игры у пользователя: не начал, играет, прошел, бросил, отложил.

#### Игровая статистика
Сколько времени пользователь провел в игре, когда играл последний раз.

#### Рецензия
Текстовая оценка игры от пользователя.

#### Реакция на рецензию
Лайк, дизлайк, полезно, жалоба.

#### Просмотр / клик / событие
Действие пользователя на платформе.

#### Промо-кампания
Продвижение игры внутри платформы.

#### Промо-показ
Факт, что пользователю показали игру в рекламном/промо-блоке.

#### Промо-клик
Факт, что пользователь кликнул по промо.

## Техническая информация

### Источники данных

| Сервис | Источник |
|---|---|
| User Service | csv |
| Developer Portal | csv |
| Game Catalog | json |
| Library Service | csv |
| Anti Library Service | ndjson |
| Reviews Service | csv |
| Game Stats | parquet |
| Promotion System | csv |
| Product Analytics / Events | ndjson.gz |

### Описание данных

#### Users

Список зарегестрированных пользователей

```python
user_id               str
username              str
email                 str
country               str
birth_year        float64
registered_at         str # iso 8601 timestamp
account_status        ['active', 'deleted', 'blocked']
```

Ограничения:
- `country` может быть `null`
- `birth_year` может быть `null`
- `user_id` PK
- `username` unique
- `email` unique

#### Anti Library

Содержит игр, которые не нравятся пользователю

```python
anti_library_id                    str
user_id                            str
game_id                            str
added_at           datetime64[us, UTC]
reason                             ['too_expensive', 'wrong_genre', 'bad_reviews', 'not_interested', 'already_played_elsewhere']
```

Ограничения:
- reason может быть `null`
- `user_id` -> `users.user_id`
- `game_id` -> `games.game_id`
- `anti_library_id` PK
- `user_id` + `game_id` unique

#### Developers

##### Developers

Содержит список разработчиков, представленных на платформе

```python
developer_id           str
studio_name            str
country                str
created_at             str # iso 8601 timestamp
verification_status    ['verified', 'pending', 'rejected']
```

Ограничения:
- `studio_name` может быть `null`
- `country` может быть `null`
- `developer_id` PK
- `studio_name` unique

##### Published Games

Содержит список игр, которые выложили разработчики на платформу

```python
developer_id              str
game_id                   str
submitted_at              str # iso 8601 timestamp
published_at              str # iso 8601 timestamp
publication_status        ['published', 'early_access', 'unlisted']
moderation_score      float64
```

Ограничения:
- `submitted_at` может быть `null`, но не должно
- `moderation_score` может быть `null`
- `game_id` -> `games.game_id`
- `developer_id` -> `developers.developer_id`
- `developer_id + game_id` PK

#### Game Catalog

##### Games

Основная информация об игре

```python
game_id                                  str
developer_id                             str
title                                    str
description                              str
age_rating                               str
price_usd                            float64
release_date                             str # iso 8601 timestamp, UTC
catalog_created_at       datetime64[us, UTC]
added_by_type                            ['user', 'developer']
added_by_user_id                         str
added_by_developer_id                    str
is_free                                 bool
publication_status                       str
```

Ограничения:
- `developer_id` -> `developers.developer_id`
- `added_by_developer_id` -> `developers.developer_id`
- `added_by_user_id` -> `users.user_id`
- `description` может быть `null`
- `age_rating` может быть `null`
- `price_usd` может быть `null`
- `added_by_user_id` может быть `null`
- `added_by_developer_id` может быть `null`
- `game_id` PK

##### Tags

Список тегов, которые могут быть у игр

```python
tag_id        str
tag_name      str
created_at    str # iso 8601 timestamp, UTC
```

Ограничения:
- `tag_id` PK
- `tag_name` unique

##### Genres

Список жанров, которые могут быть у игр

```python
genre_id      str
genre_name    str
created_at    str # iso 8601 timestamp, UTC
```

Ограничения:
- `genre_id` PK
- `genre_name` unique

##### Platforms

Список всех платформ, на которые могут выходить игры

```python
platform_id      str
platform_name    str
created_at       str # iso 8601 timestamp, UTC
```

Ограничения:
- `platform_id` PK
- `platform_name` unique

##### Languages

Список языков, на которые переведены игры

```python
language_id      str
language_code    str
created_at       str # iso 8601 timestamp, UTC
```

Ограничения:
- `language_id` PK
- `language_code` unique

##### Game tags

Связь игр с тегами этих игр

```python
game_id    str
tag_id     str
```

Ограничения:
- `game_id` -> `games.game_id`
- `tag_id` -> `tags.tag_id`
- `game_id + tag_id` PK 

##### Game genres 

Связь игр с жанрами этих игр

```python
game_id         str
genre_id        str
is_primary     bool
position      int64
```

Ограничения:
- `game_id` -> `games.game_id`
- `genre_id` -> `genres.genre_id`
- `game_id + genre_id` PK 

##### Game platforms

Связь игр с платформами, на которые они адаптированы

```python
game_id        str
platform_id    str
```

Ограничения:
- `game_id` -> `games.game_id`
- `platform_id` -> `platforms.platform_id`
- `game_id + platform_id` PK 

##### Game languages

Связь игр с языками, на которые они переведены

```python
game_id        str
language_id    str
```

Ограничения:
- `game_id` -> `games.game_id`
- `language_id` -> `languages.language_id`
- `game_id + language_id` PK 

#### Game stats

Статистика по прохождени игры пользователем

```python
user_id                      str
game_id                      str
completion_status            ['playing', 'dropped', 'not_started', 'completed']
playtime_minutes           int64
sessions_count           float64
first_played_at              str # iso 8601 timestamp, UTC
last_played_at               str # iso 8601 timestamp, UTC
achievements_total       float64
achievements_unlocked    float64
```

Ограничения:
- `user_id` -> `users.user_id`
- `game_id` -> `games.game_id`
- `sessions_count` может быть `null`
- `first_played_at` может быть `null`
- `last_played_at` может быть `null`
- `achievements_total` может быть `null`
- `achievements_unlocked` может быть `null`
- `game_id + user_id` PK

#### Library 

Список игр, которые пользователь добавил в библиотеку

```python
library_id        str
user_id           str
game_id           str
added_at          str # iso 8601 timestamp, UTC
source            str
is_wishlist       bool
```

Ограничения:
- `game_id` -> `games.game_id`
- `user_id` -> `users.user_id`
- `source` может быть `null`
- `is_wishlist` может быть `null`
- `library_id` PK

#### Promoution

##### Promo campaigns

Список промо-кампаний

```python
campaign_id            str
developer_id           str
game_id                str
placement              str 
started_at             str # iso 8601 timestamp, UTC
ended_at               str # iso 8601 timestamp, UTC
budget_usd         float64
bid_cpc_usd        float64
target_country         str
campaign_status        ['finished', 'active']
```

Ограничения:
- `developer_id` -> `developers.developer_id`
- `game_id` -> `games.game_id`
- `budget_usd` может быть `null`
- `bid_cpc_usd` может быть `null`
- `target_country` может быть `null`
- `campaign_id` PK

#### Product analytics

##### Events

Список различных событий, которые пользователи совершают на платформе

```python
event_id                           str
event_type                         ['review_view', 'game_view', 'library_add', 'anti_library_add', 'promo_impression', 'promo_click']
occurred_at        datetime64[us, UTC]
user_id                            str
game_id                            str
campaign_id                        str
review_id                          str
session_id                         str
device_type                        ['mobile', 'desktop', 'console', 'tablet']
country                            str
source                             ['promo', 'search', 'review', 'catalog', 'friend_library']
reason                             ['not_interested', 'wrong_genre', 'too_expensive', 'already_played_elsewhere', 'bad_reviews']
page                               str
referrer                           str
placement                          str
target_country                     str
review_reaction                    ['none', 'useful', 'like', 'dislike', 'funny'] 
```

Ограничения:
- `user_id` -> `users.user_id`
- `game_id` -> `games.game_id`
- `campaign_id` -> `promo_campaigns.campaign_id`
- `review_id` -> `reviews.review_id`
- `user_id` может быть `null`
- `campaign_id` может быть `null`
- `review_id` может быть `null`
- `device_type` может быть `null`
- `country` может быть `null`
- `source` может быть `null`
- `reason` может быть `null`
- `page` может быть `null`
- `referrer` может быть `null`
- `placement` может быть `null`
- `target_country` может быть `null`
- `review_reaction` может быть `null`
- `event_id` PK


#### Reviews

Список рецензий игроков на игры

```python
review_id             str
user_id               str
game_id               str
rating              int64
review_text           str 
created_at            str # iso 8601 timestamp, UTC
updated_at            str # iso 8601 timestamp, UTC
is_spoiler           bool
likes_count       float64
dislikes_count    float64
```

Ограничения:
- `user_id` -> `users.user_id`
- `game_id` -> `games.game_id`
- `updated_at` может быть `null`
- `is_spoiler` может быть `null`
- `likes_count` может быть `null`
- `dislikes_count` может быть `null`
- `review_id` PK