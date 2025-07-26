# Copilot Instructions for AI Coding Agents

## Project Overview
This is a Vietnamese-Japanese translation chatbot with OpenAI Function Calling support. The architecture follows SRS requirements for a professional translation service with batch processing capabilities.

## Key Architectural Patterns
- **Translation Service:** Automatic language detection (Vi/Ja) with bidirectional translation
- **Function Calling:** OpenAI tools integration for business trip cost calculation
- **Context Management:** In-memory conversation history (20 messages per user, 30min TTL)
- **Batch Processing:** Handle up to 50 translation requests simultaneously
- **Model Switching:** Configure via environment variables:
  ```python
  client = openai.OpenAI(
      base_url=os.getenv("OPENAI_ENDPOINT", ""),
      api_key=os.getenv("OPENAI_API_KEY", "")
  )
  OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
  ```

## API Endpoints & Usage
- **POST /api/translate:** Single message translation with context
  - Input: `{"message": "text", "source_lang": "auto|vi|ja", "user_id": "optional"}`
  - Supports function calling for reimbursement calculations
- **POST /api/batch:** Batch translation (max 50 items)
  - Input: `[{"id": 1, "text": "..."}]`
  - Independent error handling per item

## Developer Workflows
- **Run locally:** `python main.py` (Flask dev server on port 5000)
- **Environment setup:** Requires `.env` with OPENAI_API_KEY, OPENAI_ENDPOINT, OPENAI_MODEL
- **Dependencies:** `pip install -r requirements.txt` (Flask, OpenAI SDK >=1.0, python-dotenv, flask-cors)
- **Testing:** Manual test via UI or curl commands (see README examples)

## Project-Specific Conventions
- **Language Detection:** Japanese chars regex `[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]` (>30% = Japanese)
- **Error Handling:** Request ID tracking, retry logic (3 attempts), graceful degradation
- **Input Validation:** Max 1000 chars, XSS escaping, proper HTTP status codes
- **Context Storage:** `context_storage[user_id] = messages[-20:]` (in-memory fallback for Redis)

## Integration Points
- **OpenAI API:** Modern client with tools/function calling, timeout=15s
- **Frontend Communication:** JSON REST API, CORS enabled for localhost
- **Function Schema:** `calculate_reimbursement(amount: number, days: integer)` returns cost breakdown

## Security & Performance
- **API Key Management:** Environment variables only, never commit to repo
- **Input Sanitization:** HTML escape, length validation, type checking
- **Performance Targets:** <5s E2E translation, <4s average response time
- **Logging:** Request tracking without sensitive data exposure

## Key Files & Directories
- `main.py`: Flask backend with OpenAI integration and function calling
- `templates/index.html`: SPA with language selector and batch modal
- `static/app.js`: Frontend logic for translation and batch processing
- `static/style.css`: Responsive design with modal styling
- `.env`: Secret configuration (API keys, endpoints, model names)

## Example Function Calling Usage
```python
# User input: "Tính chi phí công tác 3 ngày, 200 USD"
# System automatically calls calculate_reimbursement(amount=200, days=3)
# Returns: {"original_amount": 200, "days": 3, "daily_allowance": 150, "total_reimbursement": 350}
```

---

_This chatbot implements SRS v1.0 requirements for Vi-Ja translation with professional-grade error handling and batch processing capabilities._
