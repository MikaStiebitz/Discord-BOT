from modules.BankFunctions import DB

__all__ = [
    "DB",
    "delete_prefix",
    "update_prefix",
    "get_prefix",
    "add_prefix",
]

TABLE_NAME = "prefix"

async def create_table() -> None:
    await DB.execute(f"CREATE TABLE IF NOT EXISTS `{TABLE_NAME}`(guildID BIGINT, prefix STR DEFAULT '!')")

async def add_prefix(guild_id: int) -> None:
    data = await DB.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE guildID = ?", (guild_id,), fetch="one")

    if data is None:
        await DB.execute(f"INSERT INTO `{TABLE_NAME}`(guildID) VALUES(?)", (guild_id,))
        await DB.execute(f"UPDATE `{TABLE_NAME}` SET `prefix` = ? WHERE guildID = ?", ("!", guild_id,))

async def get_prefix(guild_id: int) -> str:
    try:
        result = await DB.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE guildID = ?", (guild_id,), fetch="one")
        return result[1] if result is not None else "!"
    except:
        return "!"
    

async def update_prefix(guild_id: int, new_prefix: str) -> None:
    await DB.execute(f"UPDATE `{TABLE_NAME}` SET prefix = ? WHERE guildID = ?", (new_prefix, guild_id,))

async def delete_prefix(guild_id: int) -> None:
    await DB.execute(f"DELETE FROM `{TABLE_NAME}` WHERE guildID = ?", (guild_id,))