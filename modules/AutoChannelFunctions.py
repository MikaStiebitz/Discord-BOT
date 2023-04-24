from modules.BankFunctions import DB
from typing import List

__all__ = [
    "DB",
    "add_channel",
    "get_all_channels",
    "delete_channel",
]

TABLE_NAME = "AutoChannels"

async def create_table() -> None:
    await DB.execute(f"CREATE TABLE IF NOT EXISTS `{TABLE_NAME}`(channelID BIGINT)")

async def add_channel(channel_id: int) -> None:
    data = await DB.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE channelID = ?", (channel_id,), fetch="one")

    if data is None:
        await DB.execute(f"INSERT INTO `{TABLE_NAME}`(channelID) VALUES(?)", (channel_id,))

async def get_all_channels() -> List[int]:
    data = await DB.execute(f"SELECT channelID FROM `{TABLE_NAME}`", fetch="all")
    return [row[0] for row in data] if data else []


async def delete_channel(channel_id: int) -> None:
    await DB.execute(f"DELETE FROM `{TABLE_NAME}` WHERE channelID = ?", (channel_id,))