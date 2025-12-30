// === chatbot-faq.js ===

// 🔹 1. Simple keyword-based FAQ for quick answers
const faqResponses = {
  price: "💲 You can view all product prices at our Shop page: https://smartmouthtechnologies.com/shop",
  shipping: "🚚 We ship within 2–3 business days within the U.S.",
  compatibility: "🧩 Smartmouth tools are compatible with most standard handpieces and systems.",
  warranty: "🛡️ All products include a 1-year limited warranty.",
  contact: "📞 You can contact us anytime at info@smartmouthtechnologies.com or (877) 777-2237."
};

// 🔹 2. Detailed FAQ database for specific technical questions
const faqData = [
  { q: "What is the head diameter of the Badger Screw?", a: "2mm" },
  { q: "What is the screw channel diameter?", a: "2.04mm" },
  { q: "How much clamping force does the Badger Screw provide?", a: "~136N" },
  { q: "What is the screw channel stress?", a: "~35 MPa" },
  { q: "What driver is needed for the Badger Screw?", a: "0.048” (1.22mm) hex driver" },
  { q: "Why a smaller screw head?", a: "Preserves prosthetic material and increases prosthetic strength. The shaft secures the prosthetic, allowing a smaller head." },
  { q: "Can Badger Screws be used with Ti bases or single-unit restorations?", a: "Designed for <strong>direct to MUA</strong> only. Incorrect thread pattern for single-unit Ti base restorations." },
  { q: "Is angle correction available?", a: "Not at this time. Not needed in most cases due to the smaller screw head." },
  { q: "Which MUA brands are compatible with Badger Screws?", a: "3i®, Adin®, Astra®, BlueSkyBio®, Biohorizons®, Cortex®, Dentsply®, Dess®, GenTek ZFX®, Hiossen®, Keystone®, Megagen®, Medentika IPS®, Neodent®, NobelBiocare®, Noris®, Osstem®, Southern Implants®, SRL®, Straumann®, Thommen Medical®, ZFX®, ZimVie®" },
  { q: "What design software supports Badger Screw libraries?", a: "Exocad, 3Shape, Hyperdent, Millbox" },
  { q: "What milling tool is needed for screw channels?", a: "1mm endmill" },
  { q: "What is WIB Software used for?", a: "Finite Element Analysis (FEA) to predict structural strength of full arch designs before manufacturing." },
  { q: "How many tokens are needed per patient case in WIB?", a: "10 tokens per case (6 simulations included)" },
  { q: "How much does a WIB token cost?", a: "$7.25 per token" },
  { q: "What file types can be uploaded to WIB?", a: "<strong>Double Arch:</strong> Designed prosthetics + opposing scan in occlusion + construction info<br><strong>Single Arch:</strong> Prosthetic + opposing jaw scan + construction info" },
  { q: "Is WIB Software FDA certified?", a: "No" },
  { q: "Does WIB guarantee my arch won’t break?", a: "No. We cannot guarantee designs due to manufacturing errors, implant position, or installation issues." },
  { q: "Where do common stress points occur in full arch designs?", a: "Cantilevers, between teeth, on MUA bases, and sharp geometry transitions" },
  { q: "Where can I access WIB simulations?", a: "Via the <strong>WIB portal button</strong> on our website." },
  { q: "Is patient data secure in WIB?", a: "Yes. All patient information is <strong>encrypted and scrambled</strong> upon entry (HIPAA compliant)." }
];

// 🔹 3. Main handler function
function handleFAQ(userInput) {
  const input = userInput.toLowerCase();

  // Try quick keyword responses first
  for (const key in faqResponses) {
    if (input.includes(key)) {
      return faqResponses[key];
    }
  }

  // Try detailed Q/A match
  for (const item of faqData) {
    if (input.includes(item.q.toLowerCase().split(" ")[2])) {
      return item.a;
    }
  }

  // Fallback if nothing matches
  return "🤖 I couldn’t find an exact answer. Please leave your question and contact info (name, cell number, and email), and our agent will reach out to you shortly.";
}
