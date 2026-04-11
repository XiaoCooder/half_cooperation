// 数据管理
let conversations = [];
let currentConversationId = null;

// DOM 元素引用
let newChatBtn = null;
let conversationListContainer = null;
let messageListContainer = null;
let messageInput = null;
let sendBtn = null;

// 初始化
function init() {
    newChatBtn = document.querySelector('.new-chat-btn');
    conversationListContainer = document.querySelector('.conversation-list-container');
    messageListContainer = document.querySelector('.message-list-container');
    messageInput = document.querySelector('.message-input');
    sendBtn = document.querySelector('.send-btn');

    bindEvents();
    createNewConversation();
    renderSidebar();
    renderMessages();
}

// 事件绑定
function bindEvents() {
    newChatBtn.addEventListener('click', handleNewChat);
    sendBtn.addEventListener('click', handleSend);
    messageInput.addEventListener('keydown', handleInputKeydown);
}

function handleInputKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
}

// 创建新对话
function createNewConversation() {
    const id = Date.now().toString();
    const conversation = {
        id,
        title: '新对话',
        messages: [],
        createdAt: new Date().toISOString()
    };
    conversations.unshift(conversation);
    currentConversationId = id;
    return id;
}

// 渲染侧边栏
function renderSidebar() {
    conversationListContainer.innerHTML = '';
    conversations.forEach((conv) => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        if (conv.id === currentConversationId) {
            item.classList.add('active');
        }
        item.dataset.id = conv.id;

        const title = document.createElement('span');
        title.className = 'conversation-title';
        title.textContent = conv.title;

        item.appendChild(title);
        item.addEventListener('click', () => switchConversation(conv.id));
        conversationListContainer.appendChild(item);
    });
}

// 渲染消息
function renderMessages() {
    messageListContainer.innerHTML = '';
    const conversation = getCurrentConversation();
    if (!conversation) {
        return;
    }

    if (conversation.messages.length === 0) {
        messageListContainer.innerHTML = '<div class="empty-state">开始你的新对话吧</div>';
        return;
    }

    conversation.messages.forEach((msg) => {
        const bubble = document.createElement('div');
        bubble.className = `message ${msg.role}`;

        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = msg.content;

        bubble.appendChild(content);
        messageListContainer.appendChild(bubble);
    });

    scrollToBottom();
}

// 获取当前对话
function getCurrentConversation() {
    return conversations.find((c) => c.id === currentConversationId);
}

// 切换对话
function switchConversation(id) {
    currentConversationId = id;
    renderSidebar();
    renderMessages();
}

// 新建对话
function handleNewChat() {
    createNewConversation();
    renderSidebar();
    renderMessages();
    messageInput.value = '';
    messageInput.focus();
}

// 发送消息
function handleSend() {
    const text = messageInput.value.trim();
    if (!text) {
        return;
    }

    const conversation = getCurrentConversation();
    if (!conversation) {
        return;
    }

    // 添加用户消息
    conversation.messages.push({
        role: 'user',
        content: text,
        timestamp: new Date().toISOString()
    });

    // 更新对话标题（取第一条用户消息）
    if (conversation.messages.filter((m) => m.role === 'user').length === 1) {
        conversation.title = text.length > 20 ? text.slice(0, 20) + '...' : text;
    }

    messageInput.value = '';
    renderMessages();
    renderSidebar();

    // 模拟 AI 回复
    setTimeout(() => {
        conversation.messages.push({
            role: 'assistant',
            content: '我收到了你的消息：' + text,
            timestamp: new Date().toISOString()
        });
        renderMessages();
    }, 500);
}

// 滚动到底部
function scrollToBottom() {
    messageListContainer.scrollTop = messageListContainer.scrollHeight;
}

// DOMContentLoaded 后初始化
document.addEventListener('DOMContentLoaded', init);
