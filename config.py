import os


def _env(primary, legacy=None, default=""):
    """Read the canonical environment variable, with an optional legacy alias."""
    value = os.environ.get(primary)
    if value is None and legacy:
        value = os.environ.get(legacy)
    return default if value is None else value


class Config:
    API_ID = _env("API_ID")
    API_HASH = _env("API_HASH")
    BOT_TOKEN = _env("BOT_TOKEN")
    BOT_SESSION = _env("BOT_SESSION", default="Indra-forward-bot")
    # Keep old deployment names working while preferring the documented names.
    DB_URL = _env("DB_URL", "DATABASE_URI")
    DB_NAME = _env("DB_NAME", "DATABASE_NAME", "IND_BOTZ_FORWARD")
    OWNER_ID = [int(value) for value in os.environ.get("OWNER_ID", "").split()]

    @classmethod
    def validate(cls):
        """Fail fast with a useful message when required deployment settings are missing."""
        required = {
            "API_ID": cls.API_ID,
            "API_HASH": cls.API_HASH,
            "BOT_TOKEN": cls.BOT_TOKEN,
            "OWNER_ID": cls.OWNER_ID,
            "DB_URL (or DATABASE_URI)": cls.DB_URL,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Missing required environment variables: " + ", ".join(missing)
            )


class temp:
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
