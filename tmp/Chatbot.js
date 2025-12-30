function addMessage(sender, text, html = false) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', sender);
  if (html) msgDiv.innerHTML = text;
  else msgDiv.textContent = text;
  document.getElementById('chatbot-messages').appendChild(msgDiv);
  document.getElementById('chatbot-messages').scrollTop =
    document.getElementById('chatbot-messages').scrollHeight;
}

window.addEventListener('load', () => {
  addMessage('bot', "👋 Hello! Welcome to Smartmouth! What would you like to do?");
  showOptions([
    { label: "🛒 Order", value: "order" },
    { label: "🔧 Compatibility", value: "compatibility" },
    { label: "❓ Questions", value: "questions" },
    { label: "👩‍💼 Connect with Agent", value: "agent" }
  ], handleMainChoice);
});

function handleMainChoice(choice) {
  addMessage('user', choice);
  if (choice === 'order') {
    addMessage('bot', "Select your product:");
    showOptions([
      { label: "🦷 Badger", value: "badger" },
      { label: "🔩 Reamer", value: "reamer" },
      { label: "🧠 Smartmouth", value: "smartmouth" },
      { label: "👑 Crown Prep", value: "crownprep" },
      { label: "✨ Others", value: "others" }
    ], handleOrder);
  } else if (choice === 'questions') {
    addMessage('bot', "Sure! Ask me about price, shipping, compatibility, or warranty.");
  } else if (choice === 'agent') {
    addMessage('bot', "👩‍💼 Please leave your contact info and we’ll reach out soon.");
  } else {
    addMessage('bot', "I can help with ordering, FAQs, or connecting you to support.");
  }
}

// Handle typed input
document.getElementById('send-btn').addEventListener('click', () => {
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text) return;
  addMessage('user', text);
  input.value = '';

  // Handle custom product state
  if (orderState === 'custom') {
    orderData.product = 'others';
    orderData.name = text;
    orderState = 'quantity';
    addMessage('bot', `Great! How many ${text}s would you like?`);
    showQuantitySlider();
    return;
  }

  // Try FAQ
  const reply = handleFAQ(text);
  if (reply) {
    addMessage('bot', reply);
    return;
  }

  addMessage('bot', "I'm not sure I understand. Try asking about price, order, or shipping.");
});
