import os
from flask import Flask
from threading import Thread
from bot import bot

app = Flask('')

@app.route('/')
def home():
    return ">>Bot is alive<<"

def run_web():
    port = int(os.environ.get("PORT", 8000))
    app.run(host = "0.0.0.0", port = port)


Tread(target = run_web).start()

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
