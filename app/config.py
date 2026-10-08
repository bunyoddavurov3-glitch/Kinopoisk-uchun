from dataclasses import dataclass
import os


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_id: int
    kinopoisk_api_key: str
    kinopoisk_api_url: str
    database_url: str
    max_results: int = 10


def load_settings() -> Settings:
    max_results = int(os.getenv("KINOPOISK_MAX_RESULTS", "10"))
    if max_results < 1 or max_results > 50:
        raise RuntimeError("KINOPOISK_MAX_RESULTS must be between 1 and 50")

    return Settings(
        bot_token=_required("BOT_TOKEN"),
        admin_id=int(_required("ADMIN_ID")),
        kinopoisk_api_key=_required("KINOPOISK_API_KEY"),
        kinopoisk_api_url=os.getenv(
            "KINOPOISK_API_URL",
            "https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword",
        ),
        database_url=_required("DATABASE_URL"),
        max_results=max_results,
    )
