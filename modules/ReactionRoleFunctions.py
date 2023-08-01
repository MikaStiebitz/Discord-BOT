from modules.BankFunctions import DB

__all__ = [
    "DB",
    "add_reaction",
    "delete_reaction",
    "get_all_reactions",
    "get_all_records"
]

TABLE_NAME = "ReactionRoles"

async def create_table() -> None:
    # uncomment the line below to reset the table
    # await DB.execute(f"DROP TABLE IF EXISTS `{TABLE_NAME}`")
    print("Creating table")
    await DB.execute(f"CREATE TABLE IF NOT EXISTS `{TABLE_NAME}`(messageID BIGINT, emoji STR, roleID BIGINT)")

async def add_reaction(message_id: int, emoji: str, role: int) -> None:
    await DB.execute(f"INSERT INTO `{TABLE_NAME}`(messageID, emoji, roleID) VALUES(?, ?, ?)", (message_id, emoji, role))

async def get_all_records() -> list:
    return await DB.execute(f"SELECT * FROM `{TABLE_NAME}`", fetch="all")
    
async def get_all_reactions(message_id: int) -> list:
    return await DB.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE messageID = ?", (message_id,), fetch="all")

async def delete_reaction(message_id: int, emoji: str) -> None:
    return await DB.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE messageID = ? AND emoji = ?", (message_id, emoji), fetch="one") is None
