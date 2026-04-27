##-------------------------------##
## Barracuda(server)             ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Database Connection           ##
##-------------------------------##

## Imports
import sqlite3
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .models import UserSchema, User

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

## Constants
__all__ = ("DBContext", "initialize_database")
DB: str


## Functions
def initialize_database(db: str) -> None:
    global DB
    with sqlite3.Connection(db) as conn:
        # -Table: User
        conn.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt blob NOT NULL,
            mk_hash BLOB NOT NULL,
            mk_blob BLOB NOT NULL,
            rk_hash BLOB NOT NULL,
            rk_blob BLOB NOT NULL
        );""")
    DB = db


## Classes
@dataclass(frozen=True, slots=True)
class DBContext:
    # -Dunder Methods
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None
    ) -> None:
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        self._connection.close()

    # -Instance Methods
    def get_user(self, _id: int) -> User:
        user = self._connection.execute(
            "SELECT * FROM Users WHERE id = ?;",
            (_id,)
        ).fetchone()
        return User(**user)

    def read_user(self, username: str) -> User | None:
        user = self._connection.execute(
            "SELECT * FROM Users WHERE username = ?;",
            (username,)
        ).fetchone()
        if not user:
            return None
        return User(**user)

    def update_user(self, user: User) -> None:
        self._connection.execute(
            "UPDATE Users SET mk_hash = ?, mk_blob = ?, rk_hash = ?, rk_blob = ? WHERE id = ?;",
            (user.mk_hash, user.mk_blob, user.rk_hash, user.rk_blob, user.id)
        )

    def write_user(self, user: UserSchema) -> bool:
        try:
            self._connection.execute(
                "INSERT INTO Users (username, salt, mk_hash, mk_blob, rk_hash, rk_blob) VALUES (?, ?, ?, ?, ?, ?);",
                (user.username, user.salt, user.mk_hash, user.mk_blob, user.rk_hash, user.rk_blob)
            )
            return True
        except sqlite3.IntegrityError:
            return False

    # -Class Methods
    @classmethod
    def new(cls) -> Self:
        conn = sqlite3.Connection(DB)
        conn.row_factory = sqlite3.Row
        return cls(conn)

    # -Properties
    _connection: sqlite3.Connection
