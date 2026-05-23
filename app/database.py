"""Database access layer for the FSTR Pereval REST API."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from app.config import DatabaseConfig, get_database_config

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - local tests may run before installing deps
    psycopg = None
    dict_row = None


class DatabaseManager:
    """Class responsible for all direct work with PostgreSQL."""

    def __init__(self, config: DatabaseConfig | None = None) -> None:
        self.config = config or get_database_config()

    @contextmanager
    def _connect(self) -> Iterator[Any]:
        """Open a database connection and close it after use."""

        if psycopg is None:
            raise RuntimeError(
                "psycopg is not installed. Run: pip install -r requirements.txt"
            )

        if self.config.database_url:
            connection = psycopg.connect(
                self.config.database_url,
                row_factory=dict_row,
            )
        else:
            connection = psycopg.connect(
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.database,
                user=self.config.login,
                password=self.config.password,
                row_factory=dict_row,
            )
        try:
            yield connection
        finally:
            connection.close()

    def add_pereval(self, data: dict[str, Any]) -> int:
        """Insert a new pereval and return its id.

        A new pereval always receives moderation status "new".
        """

        with self._connect() as connection:
            try:
                with connection.cursor() as cursor:
                    user_id = self._get_or_create_user(cursor, data["user"])
                    coords_id = self._insert_coords(cursor, data["coords"])
                    level_id = self._insert_level(cursor, data["level"])
                    pereval_id = self._insert_pereval(
                        cursor=cursor,
                        data=data,
                        user_id=user_id,
                        coords_id=coords_id,
                        level_id=level_id,
                    )
                    self._insert_images(cursor, pereval_id, data.get("images", []))
                connection.commit()
                return pereval_id
            except Exception:
                connection.rollback()
                raise

    def get_pereval_by_id(self, pereval_id: int) -> dict[str, Any] | None:
        """Return a full pereval record by id, including user, coords, level, images."""

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        p.id,
                        p.beauty_title,
                        p.title,
                        p.other_titles,
                        p.connect,
                        p.add_time,
                        p.status,
                        u.email,
                        u.fam,
                        u.name,
                        u.otc,
                        u.phone,
                        c.latitude,
                        c.longitude,
                        c.height,
                        l.winter,
                        l.summer,
                        l.autumn,
                        l.spring
                    FROM perevals p
                    JOIN users u ON u.id = p.user_id
                    JOIN coords c ON c.id = p.coords_id
                    JOIN levels l ON l.id = p.level_id
                    WHERE p.id = %s;
                    """,
                    (pereval_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    return None

                cursor.execute(
                    """
                    SELECT data, title
                    FROM images
                    WHERE pereval_id = %s
                    ORDER BY id;
                    """,
                    (pereval_id,),
                )
                images = cursor.fetchall()

        return self._build_pereval_response(row, images)

    def update_pereval(self, pereval_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Update a pereval if its status is new.

        User FIO, email and phone are intentionally not edited.
        """

        with self._connect() as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, status, coords_id, level_id
                        FROM perevals
                        WHERE id = %s;
                        """,
                        (pereval_id,),
                    )
                    existing = cursor.fetchone()

                    if existing is None:
                        return {"state": 0, "message": "Запись не найдена"}

                    if existing["status"] != "new":
                        return {
                            "state": 0,
                            "message": "Редактирование запрещено: статус записи не new",
                        }

                    self._update_coords(cursor, existing["coords_id"], data["coords"])
                    self._update_level(cursor, existing["level_id"], data["level"])
                    self._update_pereval_main_fields(cursor, pereval_id, data)

                    cursor.execute(
                        "DELETE FROM images WHERE pereval_id = %s;",
                        (pereval_id,),
                    )
                    self._insert_images(cursor, pereval_id, data.get("images", []))

                connection.commit()
                return {"state": 1, "message": "Запись успешно обновлена"}
            except Exception as exc:
                connection.rollback()
                return {"state": 0, "message": str(exc)}

    def get_perevals_by_email(self, email: str) -> list[dict[str, Any]]:
        """Return all perevals submitted by a user email."""

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.id
                    FROM perevals p
                    JOIN users u ON u.id = p.user_id
                    WHERE LOWER(u.email) = LOWER(%s)
                    ORDER BY p.id;
                    """,
                    (email,),
                )
                rows = cursor.fetchall()

        result = []
        for row in rows:
            item = self.get_pereval_by_id(row["id"])
            if item is not None:
                result.append(item)
        return result

    def _get_or_create_user(self, cursor: Any, user: dict[str, Any]) -> int:
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(%s);", (user["email"],))
        row = cursor.fetchone()
        if row is not None:
            return row["id"]

        cursor.execute(
            """
            INSERT INTO users (email, fam, name, otc, phone)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                user["email"],
                user["fam"],
                user["name"],
                user.get("otc", ""),
                user["phone"],
            ),
        )
        return cursor.fetchone()["id"]

    def _insert_coords(self, cursor: Any, coords: dict[str, Any]) -> int:
        cursor.execute(
            """
            INSERT INTO coords (latitude, longitude, height)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (coords["latitude"], coords["longitude"], coords["height"]),
        )
        return cursor.fetchone()["id"]

    def _insert_level(self, cursor: Any, level: dict[str, Any]) -> int:
        cursor.execute(
            """
            INSERT INTO levels (winter, summer, autumn, spring)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (
                level.get("winter", ""),
                level.get("summer", ""),
                level.get("autumn", ""),
                level.get("spring", ""),
            ),
        )
        return cursor.fetchone()["id"]

    def _insert_pereval(
        self,
        cursor: Any,
        data: dict[str, Any],
        user_id: int,
        coords_id: int,
        level_id: int,
    ) -> int:
        cursor.execute(
            """
            INSERT INTO perevals (
                beauty_title,
                title,
                other_titles,
                connect,
                add_time,
                user_id,
                coords_id,
                level_id,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'new')
            RETURNING id;
            """,
            (
                data["beauty_title"],
                data["title"],
                data.get("other_titles", ""),
                data.get("connect", ""),
                data.get("add_time"),
                user_id,
                coords_id,
                level_id,
            ),
        )
        return cursor.fetchone()["id"]

    def _insert_images(
        self,
        cursor: Any,
        pereval_id: int,
        images: list[dict[str, Any]],
    ) -> None:
        for image in images:
            cursor.execute(
                """
                INSERT INTO images (pereval_id, data, title)
                VALUES (%s, %s, %s);
                """,
                (pereval_id, image["data"], image["title"]),
            )

    def _update_coords(self, cursor: Any, coords_id: int, coords: dict[str, Any]) -> None:
        cursor.execute(
            """
            UPDATE coords
            SET latitude = %s, longitude = %s, height = %s
            WHERE id = %s;
            """,
            (coords["latitude"], coords["longitude"], coords["height"], coords_id),
        )

    def _update_level(self, cursor: Any, level_id: int, level: dict[str, Any]) -> None:
        cursor.execute(
            """
            UPDATE levels
            SET winter = %s, summer = %s, autumn = %s, spring = %s
            WHERE id = %s;
            """,
            (
                level.get("winter", ""),
                level.get("summer", ""),
                level.get("autumn", ""),
                level.get("spring", ""),
                level_id,
            ),
        )

    def _update_pereval_main_fields(
        self,
        cursor: Any,
        pereval_id: int,
        data: dict[str, Any],
    ) -> None:
        cursor.execute(
            """
            UPDATE perevals
            SET beauty_title = %s,
                title = %s,
                other_titles = %s,
                connect = %s,
                add_time = %s
            WHERE id = %s;
            """,
            (
                data["beauty_title"],
                data["title"],
                data.get("other_titles", ""),
                data.get("connect", ""),
                data.get("add_time"),
                pereval_id,
            ),
        )

    @staticmethod
    def _build_pereval_response(
        row: dict[str, Any],
        images: list[dict[str, Any]],
    ) -> dict[str, Any]:
        add_time = row["add_time"]
        if hasattr(add_time, "isoformat"):
            add_time = add_time.isoformat()

        return {
            "id": row["id"],
            "beauty_title": row["beauty_title"],
            "title": row["title"],
            "other_titles": row["other_titles"],
            "connect": row["connect"],
            "add_time": add_time,
            "status": row["status"],
            "user": {
                "email": row["email"],
                "fam": row["fam"],
                "name": row["name"],
                "otc": row["otc"],
                "phone": row["phone"],
            },
            "coords": {
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "height": row["height"],
            },
            "level": {
                "winter": row["winter"],
                "summer": row["summer"],
                "autumn": row["autumn"],
                "spring": row["spring"],
            },
            "images": images,
        }
