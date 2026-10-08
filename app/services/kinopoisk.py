from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(slots=True)
class Film:
    film_id: int
    title: str
    year: str
    rating: str
    kind: str
    poster_url: str | None

    @property
    def url(self) -> str:
        return f"https://www.kinopoisk.ru/film/{self.film_id}/"


class KinopoiskAPI:
    def __init__(self, api_key: str, api_url: str) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            headers={"X-API-KEY": self.api_key, "Accept": "application/json"},
        )

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None

    async def search(self, query: str, limit: int = 10) -> list[Film]:
        if not self.client:
            raise RuntimeError("Kinopoisk client is not initialized")

        response = await self.client.get(
            self.api_url,
            params={"keyword": query, "page": 1},
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        raw_items = data.get("films") or data.get("items") or []
        result: list[Film] = []
        seen: set[int] = set()

        for item in raw_items:
            film_id = item.get("filmId") or item.get("kinopoiskId") or item.get("id")
            if not film_id:
                continue
            try:
                film_id = int(film_id)
            except (TypeError, ValueError):
                continue
            if film_id in seen:
                continue
            seen.add(film_id)

            title = (
                item.get("nameRu")
                or item.get("nameUz")
                or item.get("nameEn")
                or item.get("name")
                or "Noma'lum film"
            )
            year = str(item.get("year") or "—")
            rating = item.get("rating") or item.get("ratingKinopoisk") or "—"
            if isinstance(rating, (int, float)):
                rating = f"{rating:.1f}"

            result.append(
                Film(
                    film_id=film_id,
                    title=str(title),
                    year=year,
                    rating=str(rating),
                    kind=self._kind(item),
                    poster_url=(
                        item.get("posterUrlPreview")
                        or item.get("posterUrl")
                        or item.get("posterUrlOriginal")
                    ),
                )
            )
            if len(result) >= limit:
                break

        return result

    @staticmethod
    def _kind(item: dict[str, Any]) -> str:
        raw = str(item.get("type") or item.get("filmType") or "").lower()
        if "tv" in raw or "serial" in raw or "series" in raw:
            return "Serial"
        return "Film"
