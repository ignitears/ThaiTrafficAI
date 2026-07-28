let chatHistory = [];
let lastAttemptedText = "";
const chatBox = document.getElementById('chat-box');
const msgInput = document.getElementById('msg-input');
const typingWrapper = document.getElementById('typing-wrapper');

// Send message on Enter keypress
msgInput.addEventListener('keypress', (e) => { 
    if (e.key === 'Enter') sendMessage(); 
});

// --- DEBUG PANEL LOGIC ---

function toggleDebug() {
    document.getElementById('debug-sidebar').classList.toggle('open');
    fetchDebugData();
}

async function fetchDebugData() {
    try {
        const res = await fetch('/api/debug');
        const data = await res.json();
        document.getElementById('debug-state').innerText = JSON.stringify(data.state, null, 2);
        document.getElementById('debug-attributes').innerText = JSON.stringify(data.attributes, null, 2);
        document.getElementById('debug-memories').innerText = JSON.stringify(data.memories, null, 2);
    } catch(e) {
        console.error("Failed to fetch debug data:", e);
    }
}

// --- MESSAGE FORMATTING & DOM HELPER FUNCTIONS ---

function formatMessage(text) {
    let safeText = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return safeText.replace(/\*(.*?)\*/g, '<span class="action-text">$1</span>');
}

function appendMsg(text, role) {
    const div = document.createElement('div');
    div.className = `msg ${role}`;
    div.innerHTML = formatMessage(text);
    chatBox.insertBefore(div, typingWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function regenerateMessage() {
    if (typingWrapper.style.display === 'flex' || !lastAttemptedText) return;

    const messages = document.querySelectorAll('.msg');
    if (messages.length < 2) return;

    const lastMsg = messages[messages.length - 1];
    const isError = lastMsg.innerText.includes("[Connection Error]");

    lastMsg.remove();
    messages[messages.length - 2].remove();

    if (!isError && chatHistory.length >= 2) {
        chatHistory.pop(); 
        chatHistory.pop(); 
    }

    sendMessage(lastAttemptedText);
}

function continueMessage() {
    sendMessage("...");
}

// --- UI TOGGLES & THEME MANAGEMENT ---

function toggleThemeMenu() {
    document.getElementById('theme-dropdown').classList.toggle('open');
}



function selectTheme(themeClass, themeName) {
    document.body.className = themeClass;
    localStorage.setItem('chatTheme', themeClass);
    localStorage.setItem('chatThemeName', themeName);
    
    document.getElementById('current-theme-name').innerText = themeName;
    document.getElementById('theme-dropdown').classList.remove('open');
}

// --- CHARACTER SWITCHING LOGIC ---




// --- INFINITE SCROLL HISTORY LOGIC ---

let loadedOffset = 0;
let isLoadingHistory = false;

async function loadHistory(isScrollingUp = false) {
    if (isLoadingHistory) return;
    isLoadingHistory = true;
    
    if (!isScrollingUp) {
        loadedOffset = 0;
        chatHistory = [];
        document.querySelectorAll('.msg').forEach(msg => msg.remove());
    }
    
    try {
        const res = await fetch(`/api/history?offset=${loadedOffset}&limit=20`);
        const olderMessages = await res.json();
        
        if (olderMessages.length === 0) {
            isLoadingHistory = false;
            return; 
        }
        
        const oldScrollHeight = chatBox.scrollHeight;
        
        if (!isScrollingUp) {
            chatHistory = [...olderMessages];
        } else {
            chatHistory = [...olderMessages, ...chatHistory];
        }
        
        const displayMessages = [...olderMessages].reverse();
        
        displayMessages.forEach(msg => {
            const div = document.createElement('div');
            div.className = `msg ${msg.role === 'assistant' ? 'char' : 'user'}`;
            div.innerHTML = formatMessage(msg.content);
            chatBox.insertBefore(div, chatBox.firstChild);
        });
        
        loadedOffset += olderMessages.length;
        
        if (!isScrollingUp) {
            chatBox.scrollTop = chatBox.scrollHeight;
        } else {
            chatBox.scrollTop = chatBox.scrollHeight - oldScrollHeight;
        }
    } catch (err) {
        console.error("Failed to load conversation history:", err);
    }
    isLoadingHistory = false;
}

chatBox.addEventListener('scroll', () => {
    if (chatBox.scrollTop === 0) {
        loadHistory(true);
    }
});

// --- GLOBAL EVENT LISTENERS & INITIALIZATION ---

document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('char-sidebar');
    const hamburgerBtn = document.querySelector('.icon-btn'); 
    if (sidebar && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && !hamburgerBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }

    const dropdown = document.getElementById('theme-dropdown');
    if (dropdown && dropdown.classList.contains('open')) {
        const themeBtn = document.querySelector('.dropdown-toggle');
        if (!dropdown.contains(e.target) && !themeBtn.contains(e.target)) {
            dropdown.classList.remove('open');
        }
    }
});

function openModal() {
    document.getElementById('full-image').src = document.getElementById('char-avatar').src;
    document.getElementById('image-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('image-modal').style.display = 'none';
}   

window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('chatTheme') || 'theme-gemini';
    const savedName = localStorage.getItem('chatThemeName') || 'Gemini Minimal';
    
    document.body.className = savedTheme;
    const nameSpan = document.getElementById('current-theme-name');
    if (nameSpan) nameSpan.innerText = savedName;

    const savedTsundere = localStorage.getItem('tsundereMode') === 'true';
    const checkbox = document.getElementById('tsundere-toggle');
    if (checkbox) {
        checkbox.checked = savedTsundere;
    }

    loadHistory();
});

// --- TSUNDERE MODE TOGGLE LOGIC ---

async function toggleTsundere(checkbox) {
    const isChecked = checkbox ? checkbox.checked : false;
    localStorage.setItem('tsundereMode', isChecked ? 'true' : 'false');

    try {
        await fetch('/api/set-tsundere', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tsundere: isChecked })
        });
        console.log("Tsundere mode set to:", isChecked);
    } catch (err) {
        console.error("Failed to update tsundere mode:", err);
    }
}

async function updateAndRestart() {
    const isTsundere = document.getElementById('tsundere-toggle').checked;
    localStorage.setItem('tsundereMode', isTsundere ? 'true' : 'false');

    try {
        const res = await fetch('/api/reset-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tsundere: isTsundere })
        });
        const data = await res.json();
        if (data.status === 'success') {
            // Instantly triggers a full page refresh
            window.location.reload();
        }
    } catch (err) {
        console.error("Failed to update behavioral modifier and restart:", err);
    }
}

// --- SEND MESSAGE LOGIC ---

async function sendMessage(overrideText = null) {
    if (typingWrapper.style.display === 'flex') return; 

    const text = overrideText || msgInput.value.trim();
    if (!text) return;

    lastAttemptedText = text; 
    if (!overrideText) msgInput.value = '';

    appendMsg(text, 'user');
    typingWrapper.style.display = 'flex';
    chatBox.scrollTop = chatBox.scrollHeight;

    const isTsundere = localStorage.getItem('tsundereMode') === 'true';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: text, 
                history: chatHistory, 
                tsundere: isTsundere 
            })
        });
        const data = await response.json();

        typingWrapper.style.display = 'none';
        appendMsg(data.reply, 'char');
        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'assistant', content: data.reply });
        setTimeout(fetchDebugData, 2000); 
    } catch (err) {
        typingWrapper.style.display = 'none';
        appendMsg("[Connection Error]", 'char');
    }
}