import asyncpg


class Database:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)
        await self.pool.execute(
            """
            CREATE TABLE IF NOT EXISTS authorized_users (
                user_id BIGINT PRIMARY KEY
            )
            """
        )

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    def _pool(self) -> asyncpg.Pool:
        if not self.pool:
            raise RuntimeError("Database pool is not initialized")
        return self.pool

    async def is_authorized(self, user_id: int) -> bool:
        row = await self._pool().fetchrow(
            "SELECT 1 FROM authorized_users WHERE user_id = $1", user_id
        )
        return row is not None

    async def add_user(self, user_id: int) -> bool:
        result = await self._pool().execute(
            "INSERT INTO authorized_users(user_id) VALUES($1) ON CONFLICT DO NOTHING",
            user_id,
        )
        return result.endswith("1")

    async def remove_user(self, user_id: int) -> bool:
        result = await self._pool().execute(
            "DELETE FROM authorized_users WHERE user_id = $1", user_id
        )
        return result.endswith("1")

    async def list_users(self, limit: int = 10, offset: int = 0) -> list[int]:
        rows = await self._pool().fetch(
            "SELECT user_id FROM authorized_users ORDER BY user_id LIMIT $1 OFFSET $2",
            limit,
            offset,
        )
        return [int(row["user_id"]) for row in rows]

    async def count_users(self) -> int:
        value = await self._pool().fetchval("SELECT COUNT(*) FROM authorized_users")
        return int(value or 0)
