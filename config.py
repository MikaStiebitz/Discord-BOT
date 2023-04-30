from os import getenv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(raise_error_if_not_found=True))

class Auth:
    TOKEN = getenv("TOKEN")
    COMMAND_PREFIX = getenv("COMMAND_PREFIX")
    FILENAME = getenv("FILENAME")
    LAVALINK_HOST = getenv("LAVALINK_HOST")
    LAVALINK_PORT = getenv("LAVALINK_PORT")
    LAVALINK_PASSWORD = getenv("LAVALINK_PASSWORD")