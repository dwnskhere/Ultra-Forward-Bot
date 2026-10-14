from config import Config

Config.validate()

from bot import Bot

app = Bot()
app.run()
