# Chatbot OpenAI - Simple Web App

## Mô tả
Ứng dụng chatbot web đơn giản gồm frontend (HTML/CSS/JS) và backend Python (Flask), tích hợp OpenAI API.

## Cài đặt
1. Cài Python >= 3.8
2. Tạo file `.env` và điền OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ```
3. Cài đặt thư viện:
   ```
   pip install -r requirements.txt
   ```
4. Chạy server:
   ```
   python main.py
   ```
5. Truy cập: http://localhost:5000

## Cấu trúc thư mục
- `main.py`: Backend Flask
- `templates/index.html`: Giao diện chính
- `static/style.css`, `static/app.js`: CSS & JS frontend
- `.env`: Biến môi trường (API key)
- `requirements.txt`: Thư viện Python

## Ghi chú
- Không commit file `.env` lên repo.
- Đảm bảo key OpenAI được bảo mật.
- Để production, bật HTTPS và cấu hình CORS phù hợp.

## Tham khảo
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)
- [Flask Docs](https://flask.palletsprojects.com/)
