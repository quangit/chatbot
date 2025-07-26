const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const errorMsg = document.getElementById('error-msg');

function appendBubble(text, sender) {
    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + sender;
    bubble.innerHTML = text;
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorMsg.textContent = '';
    const message = userInput.value.trim();
    if (!message) return;
    appendBubble(message, 'user');
    userInput.value = '';
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await res.json();
        if (res.ok) {
            appendBubble(data.reply, 'bot');
        } else {
            errorMsg.textContent = data.error || 'Lỗi máy chủ.';
        }
    } catch (err) {
        errorMsg.textContent = 'Không kết nối được máy chủ.';
    }
});
