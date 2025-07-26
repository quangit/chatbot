# Chatbot Phiên Dịch Việt-Nhật
<img width="613" height="1012" alt="image" src="https://github.com/user-attachments/assets/95ab4a24-dce2-4e0c-abe0-ad8e9b73ae43" />

## 🧪 SRS Compliance Testing

### Automated Test Suite
```bash
# Run comprehensive SRS compliance tests
python test_srs_compliance.py
```

### Manual Testing via Frontend
1. Open browser: http://localhost:5000
2. Click "🧪 Test All SRS" button
3. Check browser console for test results
4. Use "🗑️ Clear Context" to reset user context

### Test Coverage
- **F1**: Single message translation (new & old API format)
- **F2**: Batch translation (up to 50 items)
- **F3**: Automatic language detection (Vi/Ja)
- **F4**: OpenAI Function Calling (reimbursement calculation)
- **F5**: Context management (20 messages max)
- **F6**: Error handling and validation
- **F7**: Performance requirements (< 5s response)
- **F8**: Mock and utility endpoints

### API Endpoints for Testing
```bash
# Health check
curl http://localhost:5000/api/health

# Single translation (new format)
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Xin chào"}],"source_lang":"auto","user_id":"test"}'

# Batch translation
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"id":1,"text":"Xin chào"},{"id":2,"text":"こんにちは"}]'

# Context management
curl http://localhost:5000/api/context/test_user
curl -X DELETE http://localhost:5000/api/context/test_user

# Mock data endpoints
curl http://localhost:5000/api/mock-data
curl http://localhost:5000/api/batch-mock
```

## 📊 Project Status
Chatbot phiên dịch song ngữ Việt-Nhật với Function Calling, hỗ trợ dịch tức thì và batch processing.

## Tính năng chính
- ✅ Dịch song ngữ Việt ↔ Nhật với tự động phát hiện ngôn ngữ
- ✅ Function Calling để tính chi phí công tác
- ✅ Batch translation (tối đa 50 câu/lần)
- ✅ Quản lý ngữ cảnh hội thoại (20 tin nhắn gần nhất)
- ✅ Responsive design cho mobile
- ✅ Logging và error handling

## Cài đặt

1. **Python >= 3.8**
2. **Tạo virtual environment (khuyến nghị):**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Cài đặt dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Cấu hình environment:**
   Tạo file `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_ENDPOINT=https://api.openai.com/v1
   OPENAI_MODEL=gpt-3.5-turbo
   ```

5. **Chạy ứng dụng:**
   ```cmd
   python main.py
   ```

6. **Truy cập:** http://localhost:5000

## API Endpoints

### POST /api/translate
Dịch một tin nhắn với context
```json
{
  "message": "Xin chào",
  "source_lang": "auto|vi|ja",
  "user_id": "optional_user_id"
}
```

### POST /api/batch
Dịch batch nhiều câu
```json
[
  {"id": 1, "text": "Xin chào"},
  {"id": 2, "text": "こんにちは"}
]
```

## Function Calling
Hỗ trợ tính chi phí công tác:
- Thử: "Tính chi phí công tác 3 ngày, 200 USD"
- Bot sẽ gọi function `calculate_reimbursement` và trả kết quả

## Mock Data (Testing)
```javascript
// Test batch API
const testData = [
  {"id": 1, "text": "Xin chào, bạn khỏe không?"},
  {"id": 2, "text": "こんにちは、お元気ですか。"},
  {"id": 3, "text": "Tính chi phí công tác 5 ngày, 300 USD"}
];
```

## Cấu trúc Project
```
chatbot/
├── main.py              # Backend Flask + OpenAI API
├── templates/index.html # Frontend SPA
├── static/
│   ├── style.css       # Responsive CSS với modal
│   └── app.js          # JavaScript với batch support
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (không commit)
├── .gitignore         # Git ignore rules
└── README.md          # Hướng dẫn này
```

## Tính năng theo SRS
- ✅ F1: Nhập tin nhắn với validation ≤1000 ký tự, escape XSS
- ✅ F2: Dịch song ngữ với auto-detect, độ trễ ≤4s
- ✅ F3: OpenAI API với timeout 15s, retry 2 lần
- ✅ F4: Function Calling cho `calculate_reimbursement`
- ✅ F5: Batch processing tối đa 50 items
- ✅ F6: Context management 20 messages với TTL 30 phút (in-memory)
- ✅ F7: UI hiển thị hội thoại với auto-scroll
- ✅ F8: Logging với requestID, không log sensitive data

## Bảo mật
- API key được lưu trong `.env`, không commit lên repo
- Input validation và XSS protection
- CORS configuration cho localhost
- Error handling không expose sensitive info

## Performance
- Target: E2E ≤ 5s cho dịch 1 câu
- Batch: Xử lý song song, lỗi 1 item không ảnh hưởng items khác
- Context: Chỉ lưu 20 messages gần nhất để tối ưu memory

## Deployment Notes
- Sử dụng HTTPS cho production
- Cấu hình CORS phù hợp với domain thực
- Consider Redis cho context storage ở production
- Monitor OpenAI quota usage

## Testing
```bash
# Test function calling
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"message": "Tính chi phí công tác 3 ngày, 200 USD", "source_lang": "auto"}'

# Test batch
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"id":1,"text":"Xin chào"},{"id":2,"text":"こんにちは"}]'
```
