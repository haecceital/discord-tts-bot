import os
from threading import Thread

from flask import Flask

from bot import bot

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

app = Flask("")


@app.route("/")
def home():
    return ">>Bot is alive<<"


def run_web():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)


Thread(target=run_web).start()

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
