from flask import Flask
from threading import Thread
import logging

# Flask 로깅 끄기
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return "Discord Quiz Bot is running! 🤖"

@app.route('/status')
def status():
    return {"status": "active", "bot": "Discord Quiz Bot"}

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
