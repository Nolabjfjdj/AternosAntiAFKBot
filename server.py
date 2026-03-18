import threading
import asyncio
from flask import Flask
from bot import main

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot en ligne !", 200

@app.route("/health")
def health():
    return "OK", 200

def lancer_bot():
    asyncio.run(main())

if __name__ == "__main__":
    # Lance le bot dans un thread séparé
    thread = threading.Thread(target=lancer_bot, daemon=True)
    thread.start()

    # Lance le serveur Flask (pour UptimeRobot)
    app.run(host="0.0.0.0", port=8080)
