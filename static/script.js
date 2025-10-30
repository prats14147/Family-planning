let currentLanguage = 'english';

const langButtons = document.querySelectorAll('.lang-btn');
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

langButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        langButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentLanguage = btn.getAttribute('data-lang');
        
        const welcomeMessage = currentLanguage === 'english' 
            ? "Hello! Welcome to FamilyCare. I'm here to help you with family planning information. How can I assist you today?"
            : "नमस्ते! FamilyCare मा स्वागत छ। म तपाईंलाई परिवार नियोजन जानकारीमा मद्दत गर्न यहाँ छु। म तपाईंलाई कसरी सहयोग गर्न सक्छु?";
        
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <p>${welcomeMessage}</p>
                </div>
            </div>
        `;
    });
});

function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    // content.innerHTML = `<p>${message}</p>`;
    content.innerHTML = message.replace(/\n/g, '<br>');
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// "Bot is typing..." indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <p><em>Bot is typing<span class="dots">...</span></em></p>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingDiv = document.querySelector('.typing-indicator');
    if (typingDiv) typingDiv.remove();
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    addMessage(message, true);
    userInput.value = '';

    // Show "Bot is typing…" while waiting for response
    showTypingIndicator();
    
    try {
        const response = await fetch('/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                language: currentLanguage
            })
        });
        
        const data = await response.json();

        removeTypingIndicator();
        addMessage(data.response, false);
    } catch (error) {
        removeTypingIndicator();
        const errorMessage = currentLanguage === 'english' 
            ? "Sorry, I'm having trouble connecting. Please try again."
            : "माफ गर्नुहोस्, मलाई जडान गर्न समस्या भइरहेको छ। कृपया फेरि प्रयास गर्नुहोस्।";
        addMessage(errorMessage, false);
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
