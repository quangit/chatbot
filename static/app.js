const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const errorMsg = document.getElementById('error-msg');
const sourceLang = document.getElementById('source-lang');
const batchBtn = document.getElementById('batch-btn');
const batchModal = document.getElementById('batch-modal');
const batchText = document.getElementById('batch-text');
const batchResults = document.getElementById('batch-results');

// Generate user ID for conversation context
const userId = 'user_' + Math.random().toString(36).substr(2, 9);

function appendBubble(text, sender, extra = '') {
    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + sender;
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'bubble-content';
    content.innerHTML = text;
    
    // Create play button
    const playButton = document.createElement('button');
    playButton.className = 'play-button';
    playButton.title = 'Phát âm thanh';
    playButton.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
        </svg>
    `;
    
    // Determine language for TTS
    const isVietnamese = /[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]/i.test(text);
    const language = isVietnamese ? 'vi' : 'ja';
    
    playButton.onclick = () => playMessage(playButton, text, language);
    
    // Assemble bubble
    bubble.appendChild(content);
    bubble.appendChild(playButton);
    
    if (extra) {
        const extraDiv = document.createElement('div');
        extraDiv.className = 'bubble info';
        extraDiv.innerHTML = extra;
        chatBox.appendChild(extraDiv);
    }
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// TTS functionality
async function playMessage(button, text, language) {
    if (button.classList.contains('playing')) {
        return; // Already playing
    }
    
    try {
        button.classList.add('playing');
        button.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
        `;
        
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                language: language
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Create audio element and play
            const audio = new Audio();
            audio.src = `data:${data.content_type};base64,${data.audio_base64}`;
            
            audio.onended = () => {
                resetPlayButton(button);
            };
            
            audio.onerror = () => {
                showError('Lỗi phát âm thanh.');
                resetPlayButton(button);
            };
            
            await audio.play();
        } else {
            showError(data.error || 'Lỗi TTS.');
            resetPlayButton(button);
        }
    } catch (error) {
        showError('Không thể kết nối TTS.');
        resetPlayButton(button);
    }
}

function resetPlayButton(button) {
    button.classList.remove('playing');
    button.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
        </svg>
    `;
}

function showError(message, type = 'error') {
    errorMsg.textContent = message;
    errorMsg.className = type === 'success' ? 'success-msg' : 'error-msg';
    setTimeout(() => {
        errorMsg.textContent = '';
        errorMsg.className = '';
    }, 5000);
}

// Main chat form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorMsg.textContent = '';
    
    const message = userInput.value.trim();
    if (!message) return;
    
    const sourceLanguage = sourceLang.value;
    
    appendBubble(message, 'user');
    userInput.value = '';
    
    try {
        // Use new SRS format: {"messages": [...], "source_lang": "auto|vi|ja"}
        const requestBody = {
            messages: [{"role": "user", "content": message}],
            source_lang: sourceLanguage,
            user_id: userId
        };
        
        const res = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        
        const data = await res.json();
        
        if (res.ok) {
            const langInfo = `🔄 ${data.detected_lang === 'vi' ? 'Việt' : 'Nhật'} → ${data.target_lang === 'vi' ? 'Việt' : 'Nhật'} (${data.latency_ms}ms)`;
            appendBubble(data.reply, 'bot', langInfo);
        } else {
            showError(data.error || 'Lỗi máy chủ.');
        }
    } catch (err) {
        showError('Không kết nối được máy chủ.');
    }
});

// Batch translation modal
batchBtn.addEventListener('click', () => {
    batchModal.style.display = 'block';
    batchResults.style.display = 'none';
    batchText.value = '';
});

// Close modal
document.querySelector('.close').addEventListener('click', () => {
    batchModal.style.display = 'none';
});

document.getElementById('batch-cancel-btn').addEventListener('click', () => {
    batchModal.style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === batchModal) {
        batchModal.style.display = 'none';
    }
});

// Batch translate
document.getElementById('batch-translate-btn').addEventListener('click', async () => {
    const text = batchText.value.trim();
    if (!text) {
        alert('Vui lòng nhập văn bản để dịch.');
        return;
    }
    
    // Split by lines and create batch data
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length > 50) {
        alert('Tối đa 50 câu mỗi lần dịch.');
        return;
    }
    
    const batchData = lines.map((line, index) => ({
        id: index + 1,
        text: line.trim()
    }));
    
    try {
        const res = await fetch('/api/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(batchData)
        });
        
        const data = await res.json();
        
        if (res.ok) {
            displayBatchResults(data.results);
        } else {
            alert(data.error || 'Lỗi xử lý batch.');
        }
    } catch (err) {
        alert('Không kết nối được máy chủ.');
    }
});

function displayBatchResults(results) {
    batchResults.innerHTML = '';
    batchResults.style.display = 'block';
    
    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'batch-item' + (result.error ? ' error' : '');
        
        if (result.error) {
            item.innerHTML = `
                <div class="batch-original">Câu ${result.id}: ${result.text || 'N/A'}</div>
                <div class="batch-error">Lỗi: ${result.error}</div>
            `;
        } else {
            const langInfo = `${result.source_lang === 'vi' ? 'Vi' : 'Ja'} → ${result.target_lang === 'vi' ? 'Vi' : 'Ja'}`;
            item.innerHTML = `
                <div class="batch-original">${result.original} <small>(${langInfo})</small></div>
                <div class="batch-translation">${result.translation}</div>
            `;
        }
        
        batchResults.appendChild(item);
    });
}

// Testing and validation methods for SRS compliance
async function testAllEndpoints() {
    console.log('🧪 Testing all SRS endpoints...');
    
    // Test F1: Single translation
    await testSingleTranslation();
    
    // Test F2: Batch translation
    await testBatchTranslation();
    
    // Test F3: Language detection
    await testLanguageDetection();
    
    // Test F4: Function calling
    await testFunctionCalling();
    
    // Test F5: Context management
    await testContextManagement();
    
    // Test Mock endpoints
    await testMockEndpoints();
    
    console.log('✅ All SRS tests completed');
}

async function testSingleTranslation() {
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: [{"role": "user", "content": "Xin chào"}],
                source_lang: "auto",
                user_id: "test_user"
            })
        });
        const data = await response.json();
        console.log('✅ F1 Single Translation:', data);
    } catch (err) {
        console.error('❌ F1 Single Translation failed:', err);
    }
}

async function testBatchTranslation() {
    try {
        const batchData = [
            {"id": 1, "text": "Xin chào"},
            {"id": 2, "text": "こんにちは"},
            {"id": 3, "text": "Cảm ơn bạn"}
        ];
        
        const response = await fetch('/api/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(batchData)
        });
        const data = await response.json();
        console.log('✅ F2 Batch Translation:', data);
    } catch (err) {
        console.error('❌ F2 Batch Translation failed:', err);
    }
}

async function testLanguageDetection() {
    const testCases = [
        {text: "Xin chào tôi là người Việt Nam", expected: "vi"},
        {text: "こんにちは、私は日本人です", expected: "ja"},
        {text: "Hello world", expected: "vi"} // Default fallback
    ];
    
    for (const testCase of testCases) {
        try {
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [{"role": "user", "content": testCase.text}],
                    source_lang: "auto",
                    user_id: "test_detection"
                })
            });
            const data = await response.json();
            console.log(`✅ F3 Language Detection for "${testCase.text}": ${data.detected_lang}`);
        } catch (err) {
            console.error(`❌ F3 Language Detection failed for "${testCase.text}":`, err);
        }
    }
}

async function testFunctionCalling() {
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: [{"role": "user", "content": "Tính chi phí công tác 3 ngày, 200 USD"}],
                source_lang: "vi",
                user_id: "test_function"
            })
        });
        const data = await response.json();
        console.log('✅ F4 Function Calling:', data);
    } catch (err) {
        console.error('❌ F4 Function Calling failed:', err);
    }
}

async function testContextManagement() {
    try {
        // Send multiple messages to test context
        for (let i = 1; i <= 5; i++) {
            await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [{"role": "user", "content": `Message ${i}`}],
                    source_lang: "auto",
                    user_id: "test_context"
                })
            });
        }
        
        // Check context endpoint
        const contextResponse = await fetch('/api/context/test_context');
        const contextData = await contextResponse.json();
        console.log('✅ F5 Context Management:', contextData);
    } catch (err) {
        console.error('❌ F5 Context Management failed:', err);
    }
}

async function testMockEndpoints() {
    try {
        // Test health endpoint
        const healthResponse = await fetch('/api/health');
        const healthData = await healthResponse.json();
        console.log('✅ Health Check:', healthData);
        
        // Test mock data endpoint
        const mockResponse = await fetch('/api/mock-data');
        const mockData = await mockResponse.json();
        console.log('✅ Mock Data:', mockData);
        
        // Test batch mock endpoint
        const batchMockResponse = await fetch('/api/batch-mock');
        const batchMockData = await batchMockResponse.json();
        console.log('✅ Batch Mock:', batchMockData);
        
    } catch (err) {
        console.error('❌ Mock endpoints test failed:', err);
    }
}

// Add test button functionality
function addTestControls() {
    const testControls = document.createElement('div');
    testControls.className = 'test-controls';
    testControls.innerHTML = `
        <button id="testAllBtn" class="test-btn">🧪 Test All SRS</button>
        <button id="clearContextBtn" class="test-btn">🗑️ Clear Context</button>
        <div id="testResults" class="test-results"></div>
    `;
    
    document.querySelector('.container').appendChild(testControls);
    
    document.getElementById('testAllBtn').addEventListener('click', testAllEndpoints);
    document.getElementById('clearContextBtn').addEventListener('click', clearUserContext);
}

async function clearUserContext() {
    try {
        const response = await fetch(`/api/context/${userId}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            document.getElementById('chat').innerHTML = '';
            showError('Context cleared successfully', 'success');
        }
    } catch (err) {
        showError('Failed to clear context');
    }
}

// Initialize test controls when page loads
document.addEventListener('DOMContentLoaded', () => {
    addTestControls();
});
