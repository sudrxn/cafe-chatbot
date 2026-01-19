# ☕ The Skylight Cafe – WhatsApp Ordering Chatbot

A production-ready WhatsApp chatbot built using **Flask, Twilio WhatsApp Sandbox, and Render**, designed to help small cafés take customer orders directly on WhatsApp with minimal cost and infrastructure.

This project is implemented as a **practical pilot system** suitable for local cafés and small businesses.
whatsapp number: +14155238886
---

## 🚀 Project Overview

The **Skylight Cafe WhatsApp Bot** allows customers to:

* Scan a QR code
* Join the WhatsApp sandbox (one-time)
* Chat with a bot to place orders
* Order multiple items with quantities
* Confirm table number
* Automatically send the order to the café owner’s WhatsApp

The café owner receives **real-time order notifications** on WhatsApp.

---

## ✨ Key Features

* ✅ WhatsApp-based ordering (no app install needed)
* ✅ Multi-item & multi-quantity orders (`3 sandwich`, `2 tea`)
* ✅ Session-based conversation flow
* ✅ Automatic owner notification
* ✅ Inventory quantity control
* ✅ 30-minute session timeout
* ✅ Free-tier friendly & low operating cost
* ✅ Secure (no credentials exposed to users)

---

## 🧠 How the System Works (High Level)

```
Customer WhatsApp
        ↓
Twilio WhatsApp Sandbox
        ↓
Flask Webhook (Render / Local)
        ↓
Order Processing & Session Logic
        ↓
Owner WhatsApp Notification
```

---

## 🧰 Tech Stack

| Layer         | Technology              |
| ------------- | ----------------------- |
| Backend       | Python + Flask          |
| Messaging API | Twilio WhatsApp         |
| Hosting       | Render                  |
| Local Testing | ngrok                   |
| State Storage | In-memory (Python dict) |

---

## 📁 Project Structure

```
cafe-chatbot/
│
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── venv/               # Virtual environment (local)
```

---

## ⚙️ Setup Instructions (Local Testing)

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd cafe-chatbot
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables (IMPORTANT)

This project **does NOT hardcode secrets**.

Set the following environment variables **locally** (PowerShell):

```powershell
$env:TWILIO_ACCOUNT_SID="YOUR_TWILIO_SID"
$env:TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN"
$env:TWILIO_WHATSAPP_NUMBER="whatsapp:+1**********"
$env:OWNER_NUMBER="whatsapp:+91XXXXXXXXXX"
$env:CAFE_NAME="YOUR BUSINESS "
```

---

## ▶️ Run Locally

```bash
python app.py
```

Health check:

```
http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "running",
  "sessions": 0
}
```

---

## 🌐 WhatsApp Testing (Using ngrok)

1. Start ngrok:

```bash
ngrok http 5000
```

2. Copy the HTTPS URL (example):

```
https://abc123.ngrok-free.app
```

3. Set Twilio Sandbox webhook:

```
https://abc123.ngrok-free.app/webhook
```

Method: **POST**

---

## 📲 Customer Usage Instructions (Sandbox Mode)

Since this project uses **Twilio WhatsApp Sandbox**, each customer must join once.

### 🧾 Instructions shown at café:

```
📲 ORDER ON WHATSAPP

1️⃣ Scan the QR Code
2️⃣ Send this message:
    join white-symbol
3️⃣ Start ordering 😊
```

After joining, customers can order normally.

---

## 💬 Sample Conversation

```
Customer: Hi
Bot: Welcome to The Skylight Cafe! What's your name?

Customer: Rahul
Bot: Shows menu

Customer: 3 sandwich
Bot: Added

Customer: 2 tea
Bot: Added

Customer: done
Bot: Ask for table number

Customer: 5
Bot: Order confirmed
```

---

## 🔔 Owner Notification (Automatic)

Owner receives on WhatsApp:

```
NEW ORDER

Customer: Rahul
Table: 5
Items:
• Sandwich x3
• Tea x2
```

---

## 💰 Billing & Cost Estimation (Transparent)

* Customers pay: **₹0 / $0**
* Billing is **conversation-based (24-hour window)**

### Approximate cost:

* ~$0.005–$0.007 per customer
* 20 customers/day ≈ $0.12/day
* $15 credit lasts ≈ **3–4 months**

This makes the system **highly affordable for small cafés**.

---

## ⚠️ Sandbox Limitations (Important)

* Each customer must send `join <sandbox-code>`
* Membership expires after **72 hours**
* Suitable for **pilot / small-scale deployment**
* Not suitable for mass public rollout

---

## 🚀 Deployment (Render)

* Push code to GitHub
* Create a Python Web Service on Render
* Set environment variables in Render dashboard
* Start command:

```
gunicorn app:app
```

---

## 🔮 Future Upgrade Path

This system can later be upgraded to:

* Official WhatsApp Business API
* Google Sheets / DB order logging
* Admin dashboard
* Payment integration
* AI-based recommendations


---

## 🧑‍💻 Author

**Mr. Sudershan Sharma **
AI & Data Science Engineer
Project: WhatsApp Ordering System for Local Cafés

---

## 📌 Final Note

This project is intentionally designed as a **realistic, cost-effective pilot**, balancing engineering quality with business feasibility.
