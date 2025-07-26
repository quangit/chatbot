from flask import Flask, request, jsonify, render_template
import openai
import os
import logging
import uuid
import json
import re
from datetime import datetime, timedelta
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

# In-memory context storage
context_storage = {}

# OpenAI client setup
client = openai.OpenAI(
    base_url=os.getenv("OPENAI_ENDPOINT", ""),
    api_key=os.getenv("OPENAI_API_KEY", "")
)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Function definitions for Function Calling
FUNCTIONS = [
    {
        "name": "calculate_reimbursement",
        "description": "Tính chi phí công tác",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Số tiền USD"},
                "days": {"type": "integer", "description": "Số ngày công tác"}
            },
            "required": ["amount", "days"]
        }
    }
]

# Helper functions
def detect_language(text):
    """Detect if text is Vietnamese or Japanese"""
    japanese_chars = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text)
    if len(japanese_chars) > len(text) * 0.3:
        return "ja"
    return "vi"

def get_conversation_history(user_id):
    """Get conversation history from memory"""
    return context_storage.get(user_id, [])

def save_conversation_history(user_id, messages):
    """Save conversation history to memory (keep last 10 exchanges = 20 messages)"""
    # Limit to 10 exchanges (20 messages) as per SRS F6 requirement
    context_storage[user_id] = messages[-20:]

def calculate_reimbursement(amount, days):
    """Function to calculate business trip reimbursement"""
    daily_allowance_rate = 50  # USD per day
    total_allowance = daily_allowance_rate * days
    total_reimbursement = amount + total_allowance
    
    return {
        "original_amount": amount,
        "days": days,
        "daily_allowance": total_allowance,
        "total_reimbursement": total_reimbursement,
        "currency": "USD",
        "breakdown": f"Số tiền gốc: ${amount} + Phụ cấp ({days} ngày × ${daily_allowance_rate}/ngày) = ${total_reimbursement}"
    }

def execute_function_call(function_name, arguments):
    """Execute function call and return result"""
    if function_name == "calculate_reimbursement":
        return calculate_reimbursement(**arguments)
    return {"error": f"Unknown function: {function_name}"}

@app.route("/")
def index():
    return render_template("index.html")

# Mock data endpoint for testing (SRS requirement 6.1)
@app.route("/api/mock-data", methods=["GET"])
def get_mock_data():
    """Get mock translation data for testing"""
    mock_sentences = [
        {"id": 1, "vi": "Xin chào, bạn khỏe không?", "ja": "こんにちは、お元気ですか。", "note": "Chào hỏi"},
        {"id": 2, "vi": "Tôi muốn đặt vé tàu.", "ja": "電車の切符を予約したいです。", "note": "Du lịch"},
        {"id": 3, "vi": "Tổng chi phí là bao nhiêu?", "ja": "合計費用はいくらですか。", "note": "Hỏi giá"},
        {"id": 4, "vi": "Tạm biệt và hẹn gặp lại.", "ja": "さようなら、また会いましょう。", "note": "Chào tạm biệt"},
        {"id": 5, "vi": "Tính chi phí công tác 3 ngày, 200 USD.", "ja": "3日間の出張費200ドルを計算して。", "note": "Function Calling"}
    ]
    return jsonify({"mock_data": mock_sentences, "total": len(mock_sentences)})

# Health check endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0",
        "active_contexts": len(context_storage),
        "model": OPENAI_MODEL
    })

# Context management endpoint
@app.route("/api/context/<user_id>", methods=["GET", "DELETE"])
def manage_context(user_id):
    """Get or clear user conversation context"""
    if request.method == "GET":
        history = get_conversation_history(user_id)
        return jsonify({
            "user_id": user_id,
            "message_count": len(history),
            "messages": history
        })
    elif request.method == "DELETE":
        if user_id in context_storage:
            del context_storage[user_id]
        return jsonify({"message": f"Context cleared for user {user_id}"})

# Batch mock endpoint for testing
@app.route("/api/batch-mock", methods=["GET"])
def batch_mock():
    """Generate batch mock data for testing"""
    batch_data = [
        {"id": 101, "text": "Hẹn gặp lại."},
        {"id": 102, "text": "今日は忙しいですか。"},
        {"id": 103, "text": "Cảm ơn bạn rất nhiều."},
        {"id": 104, "text": "すみません、遅れました。"},
        {"id": 105, "text": "Tính chi phí công tác 5 ngày, 300 USD."}
    ]
    return jsonify(batch_data)

@app.route("/api/translate", methods=["POST"])
def translate():
    req_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    try:
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        source_lang = data.get("source_lang", "auto")
        user_id = data.get("user_id", "anonymous")
        
        # Validate input - support both old format (message) and new format (messages)
        if "message" in data:
            # Backward compatibility
            message = data.get("message", "")
            if not isinstance(message, str) or len(message) == 0 or len(message) > 1000:
                return jsonify({"error": "Tin nhắn không hợp lệ."}), 400
            messages = [{"role": "user", "content": message}]
        elif messages:
            if not isinstance(messages, list) or len(messages) == 0:
                return jsonify({"error": "Messages không hợp lệ."}), 400
            current_message = messages[-1].get("content", "")
            if len(current_message) > 1000:
                return jsonify({"error": "Tin nhắn quá dài (>1000 ký tự)."}), 400
        else:
            return jsonify({"error": "Thiếu messages hoặc message."}), 400
            
        # Get current message for processing
        current_message = messages[-1].get("content", "") if messages else ""
        
        # Escape XSS
        safe_message = current_message.replace("<", "&lt;").replace(">", "&gt;")
        
        # Detect language if auto
        if source_lang == "auto":
            detected_lang = detect_language(safe_message)
            target_lang = "ja" if detected_lang == "vi" else "vi"
        else:
            detected_lang = source_lang
            target_lang = "ja" if source_lang == "vi" else "vi"
            
        # Get conversation history (10 exchanges = 20 messages max)
        history = get_conversation_history(user_id)
        
        # Prepare system prompt for translation
        system_prompt = f"""Bạn là trợ lý phiên dịch chuyên nghiệp Việt-Nhật. 
Nhiệm vụ: Dịch từ {detected_lang} sang {target_lang}.
Quy tắc:
- Giữ định dạng, ngữ điệu gốc
- Thuật ngữ kỹ thuật: giữ nguyên hoặc ghi chú
- Trả lời ngắn gọn, chỉ bản dịch
- Nếu được yêu cầu tính chi phí công tác, sử dụng function calculate_reimbursement"""

        # Prepare messages for OpenAI
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(history)
        openai_messages.append({"role": "user", "content": safe_message})
        
        # Call OpenAI with retry logic (retry 2 times = 3 total attempts)
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=openai_messages,
                    tools=[{"type": "function", "function": func} for func in FUNCTIONS],
                    tool_choice="auto",
                    timeout=15,
                    temperature=0.3
                )
                
                message_obj = response.choices[0].message
                
                # Handle function calling
                if message_obj.tool_calls:
                    # Execute function
                    tool_call = message_obj.tool_calls[0]
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    function_result = execute_function_call(function_name, function_args)
                    
                    # Send function result back to OpenAI
                    openai_messages.append({
                        "role": "assistant",
                        "content": message_obj.content,
                        "tool_calls": message_obj.tool_calls
                    })
                    openai_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result)
                    })
                    
                    # Get final response
                    final_response = client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=openai_messages,
                        timeout=15,
                        temperature=0.3
                    )
                    reply = final_response.choices[0].message.content
                else:
                    reply = message_obj.content
                    
                break
                
            except Exception as e:
                # Retry only on 5xx server errors
                if attempt == 2 or not (hasattr(e, 'status_code') and str(e.status_code).startswith('5')):
                    if hasattr(e, 'status_code'):
                        if str(e.status_code).startswith('4'):
                            logging.error(f"{req_id} OpenAI client error: {e}")
                            return jsonify({"error": "Lỗi cấu hình API hoặc quota vượt giới hạn."}), 400
                    raise
                logging.warning(f"{req_id} Retry attempt {attempt + 1} due to: {e}")
        else:
            return jsonify({"error": "Không thể kết nối OpenAI sau 3 lần thử."}), 502
            
        # Update conversation history (keep last 10 exchanges = 20 messages)
        new_history = history + [
            {"role": "user", "content": safe_message},
            {"role": "assistant", "content": reply}
        ]
        save_conversation_history(user_id, new_history)
        
        # Log success
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        logging.info(f"{req_id} {start_time.isoformat()} 200 {latency_ms}ms lang:{detected_lang}->{target_lang}")
        
        return jsonify({
            "reply": str(reply),
            "detected_lang": detected_lang,
            "target_lang": target_lang,
            "request_id": req_id,
            "latency_ms": latency_ms
        })
        
    except Exception as ex:
        latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        logging.error(f"{req_id} {start_time.isoformat()} ERROR {type(ex).__name__}: {str(ex)} latency:{latency_ms}ms")
        return jsonify({"error": "Lỗi máy chủ nội bộ."}), 500

@app.route("/api/batch", methods=["POST"])
def batch_translate():
    req_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    try:
        data = request.get_json(force=True)
        
        if not isinstance(data, list) or len(data) > 50:
            return jsonify({"error": "Batch tối đa 50 items."}), 400
            
        results = []
        for item in data:
            try:
                item_id = item.get("id")
                text = item.get("text", "")
                
                if len(text) > 1000:
                    results.append({"id": item_id, "error": "Text quá dài"})
                    continue
                    
                # Detect language and translate
                detected_lang = detect_language(text)
                target_lang = "ja" if detected_lang == "vi" else "vi"
                
                # Simple translation call (no history for batch)
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": f"Dịch từ {detected_lang} sang {target_lang}. Chỉ trả lời bản dịch."},
                        {"role": "user", "content": text}
                    ],
                    timeout=15,
                    temperature=0.3
                )
                
                translation = response.choices[0].message.content
                results.append({
                    "id": item_id,
                    "original": text,
                    "translation": translation,
                    "source_lang": detected_lang,
                    "target_lang": target_lang
                })
                
            except Exception as e:
                results.append({"id": item.get("id"), "error": str(e)})
                
        logging.info(f"{req_id} batch {len(results)} items")
        return jsonify({"results": results, "request_id": req_id})
        
    except Exception as ex:
        logging.error(f"{req_id} batch ERROR {type(ex).__name__}")
        return jsonify({"error": "Lỗi xử lý batch."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
