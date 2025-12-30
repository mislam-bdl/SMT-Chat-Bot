const productLinks = {
  badger: "https://smartmouthtechnologies.com/?add-to-cart=1320&quantity=",
  reamer: "https://smartmouthtechnologies.com/?add-to-cart=1147&quantity=",
  smartmouth: "https://smartmouthtechnologies.com/?add-to-cart=1010&quantity=",
  crownprep: "https://smartmouthtechnologies.com/?add-to-cart=1030&quantity=",
  others: "https://smartmouthtechnologies.com/shop"
};

const productPrices = {
  badger: 180.0,
  reamer: 120.0,
  smartmouth: 160.0,
  crownprep: 140.0,
  others: 0
};

function showFAQMenu() {
  addMessage('bot', "Here are some FAQs. Tap one or type your question:");
  const options = faqData.map((item, i) => ({ label: item.q, value: i }));
  options.push({ label: "Back to Main Menu", value: "back" });
  showOptions(options, handleFAQChoice);
}

function handleFAQChoice(index) {
  if (index === "back") {
    showMainMenu();
    return;
  }
  const faq = faqData[index];
  addMessage('user', faq.q);
  setTimeout(() => addMessage('bot', faq.a, true), 400);
}

let orderData = {};
let orderState = null;

function showOptions(options, callback) {
  const container = document.createElement('div');
  container.classList.add('option-buttons');
  options.forEach(opt => {
    const btn = document.createElement('div');
    btn.classList.add('option-button');
    btn.textContent = opt.label;
    btn.onclick = () => {
      container.remove();
      callback(opt.value);
    };
    container.appendChild(btn);
  });
  document.getElementById('chatbot-messages').appendChild(container);
}

function showQuantitySlider() {
  const html = `
    <div id="qty-box" style="margin-top:8px;text-align:center;background:#f9f9f9;border-radius:8px;padding:10px;">
      <strong>Select Quantity</strong><br>
      <input type="range" min="1" max="100" value="1" id="qty-range" style="width:100%;accent-color:var(--main-color);">
      <div id="qty-value" style="margin-top:4px;font-weight:bold;">1</div>
      <button id="confirm-qty" style="margin-top:6px;background:var(--main-color);color:white;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;">Confirm</button>
    </div>`;
  addMessage('bot', html, true);
  setTimeout(() => {
    const slider = document.getElementById('qty-range');
    const qtyVal = document.getElementById('qty-value');
    slider.oninput = () => (qtyVal.textContent = slider.value);
    document.getElementById('confirm-qty').onclick = () => {
      orderData.quantity = parseInt(slider.value);
      document.getElementById('qty-box').remove();
      addMessage('user', orderData.quantity.toString());
      showSummary();
    };
  }, 100);
}

function handleOrder(product) {
  addMessage('user', product);
  if (product === 'others') {
    orderState = 'custom';
    addMessage('bot', "Please type the product name:");
  } else {
    orderData.product = product;
    orderData.name = product.charAt(0).toUpperCase() + product.slice(1);
    addMessage('bot', `How many ${orderData.name}s would you like?`);
    showQuantitySlider();
  }
}

function showSummary() {
  const link = productLinks[orderData.product] || productLinks.others;
  const qty = orderData.quantity;
  const price = productPrices[orderData.product] || 0;
  const total = price * qty;
  const priceInfo = price
    ? `$${price.toFixed(2)} each<br>Total: <strong>$${total.toFixed(2)}</strong>`
    : "Price: See shop for details";

  const html = `
    <strong>Order Summary:</strong><br>
    Product: ${orderData.name}<br>
    Quantity: ${qty}<br>
    ${priceInfo}<br><br>
    <a href="#" onclick="event.preventDefault(); addToCartAndGo('${link + qty}');" class="order-now-btn">
      🛍️ ORDER NOW
    </a>
  `;
  addMessage('bot', html, true);
}

function addToCartAndGo(url) {
  const img = new Image();
  img.src = url;
  setTimeout(() => {
    window.location.href = "https://smartmouthtechnologies.com/cart/";
  }, 400);
}


