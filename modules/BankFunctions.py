from config import Auth

import sqlite3
import discord

from typing import Tuple, Any, Optional, Union

__all__ = [
    "DB",
    "open_bank",
    "get_bank_data",
    "update_bank",
    "reset_bank",
    "get_networth_lb",
]

TABLE_NAME = "economy"


class Database:
    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None

    async def connect(self):
        try:
            self.conn = sqlite3.connect(Auth.FILENAME)
        except sqlite3.Error:
            pass

        return self

    @property
    def is_connected(self) -> bool:
        return self.conn is not None

    @staticmethod
    async def _fetch(cursor, mode) -> Optional[Any]:
        if mode == "one":
            return cursor.fetchone()
        if mode == "many":
            return cursor.fetchmany()
        if mode == "all":
            return cursor.fetchall()

        return None

    async def execute(self, query: str, values: Tuple = (), *, fetch: str = None) -> Optional[Any]:
        cursor = self.conn.cursor()

        cursor.execute(query, values)
        data = await self._fetch(cursor, fetch)
        self.conn.commit()

        cursor.close()
        return data

DB = Database()

async def create_table() -> None:
    await DB.execute(f"CREATE TABLE IF NOT EXISTS `{TABLE_NAME}`(userID BIGINT, wallet BIGINT DEFAULT 0)")


async def open_bank(user: discord.Member) -> None:
    data = await DB.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE userID = ?", (user.id,), fetch="one")

    if data is None:
        await DB.execute(f"INSERT INTO `{TABLE_NAME}`(userID) VALUES(?)", (user.id,))
        await DB.execute(f"UPDATE `{TABLE_NAME}` SET `wallet` = ? WHERE userID = ?", (250, user.id,))


async def get_bank_data(user: discord.Member) -> Optional[Any]:
    users = await DB.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE userID = ?", (user.id,), fetch="one")
    print(users)
    return users


async def update_bank(user: discord.Member, amount: Union[float, int] = 0) -> Optional[Any]:
    data = await DB.execute(
        f"SELECT * FROM `{TABLE_NAME}` WHERE userID = ?", (user.id,), fetch="one")
    if data is not None:
        await DB.execute(f"UPDATE `{TABLE_NAME}` SET `wallet` = `wallet` + ? WHERE userID = ?", (amount, user.id))

    users = await DB.execute(f"SELECT `wallet` FROM `{TABLE_NAME}` WHERE userID = ?", (user.id,), fetch="one")
    return users


async def reset_bank(user: discord.Member) -> None:
    await DB.execute(f"DELETE FROM `{TABLE_NAME}` WHERE userID = ?", (user.id,))
    await open_bank(user)


async def get_networth_lb() -> Any:
    users = await DB.execute(f"SELECT `userID`, `wallet` FROM `{TABLE_NAME}` ORDER BY `wallet` DESC", fetch="all")
    return users
