from flask import Flask, request, jsonify, render_template
import openai
import os
import logging
import uuid
from datetime import datetime
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost", "http://127.0.0.1"]}})

# Logging setup
logging.basicConfig(
    filename='chatbot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# OpenAI client setup
client = openai.OpenAI(
    base_url=os.getenv("OPENAI_ENDPOINT", ""),
    api_key=os.getenv("OPENAI_API_KEY", "")
)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    req_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    try:
        data = request.get_json(force=True)
        message = data.get("message", "")
        if not isinstance(message, str) or len(message) == 0 or len(message) > 1000:
            return jsonify({"error": "Tin nhắn không hợp lệ."}), 400
        # Escape special characters
        safe_message = message.replace("<", "&lt;").replace(">", "&gt;")
        # Call OpenAI
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": safe_message}],
                    timeout=15
                )
                reply = response.choices[0].message.content
                break
            except Exception as e:
                if attempt == 2 or not (hasattr(e, 'status_code') and str(e.status_code).startswith('5')):
                    raise
        else:
            return jsonify({"error": "Không thể kết nối OpenAI."}), 502
        # Ensure UTF-8
        reply = str(reply)
        # Log (no sensitive content)
        logging.info(f"{req_id} {start_time.isoformat()} 200")
        return jsonify({"reply": reply})
    except Exception as ex:
        logging.error(f"{req_id} {start_time.isoformat()} ERROR {type(ex).__name__}")
        return jsonify({"error": "Lỗi máy chủ."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)