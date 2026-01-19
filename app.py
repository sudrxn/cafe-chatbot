import os
import time
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

# ========== ENV CONFIG ==========
CAFE_NAME = os.getenv("CAFE_NAME", "Cafe")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
OWNER_NUMBER = os.getenv("OWNER_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ========== MENU ==========
menu = {
    "cappuccino": {"price": 120, "wait": 5, "qty": 10},
    "latte": {"price": 150, "wait": 5, "qty": 8},
    "espresso": {"price": 100, "wait": 3, "qty": 15},
    "sandwich": {"price": 80, "wait": 10, "qty": 5},
    "burger": {"price": 150, "wait": 15, "qty": 7},
    "tea": {"price": 50, "wait": 3, "qty": 20}
}

# ========== SESSIONS ==========
user_sessions = {}
SESSION_TIMEOUT = 1800  # 30 min


# ========== HELPERS ==========
def clean_sessions():
    now = time.time()
    expired = [u for u, d in user_sessions.items() if now - d["time"] > SESSION_TIMEOUT]
    for u in expired:
        del user_sessions[u]


def menu_text():
    text = "📋 *Menu*\n\n"
    for i, d in menu.items():
        text += f"• {i.title()} – ₹{d['price']} ({d['wait']} min)\n"
    text += "\nExample: `2 sandwich`\nType *done* to finish."
    return text


def parse_order(msg):
    parts = msg.lower().split()
    qty, item = 1, None
    for p in parts:
        if p.isdigit():
            qty = int(p)
        elif p in menu:
            item = p
    return item, qty


def notify_owner(name, order, table, customer):
    body = (
        "🔔 *NEW ORDER*\n\n"
        f"Customer: {name}\n"
        f"Table: {table}\n"
        f"Phone: {customer}\n\n"
        "*Items:*\n"
    )
    for item, qty in order.items():
        body += f"• {item.title()} x{qty}\n"

    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=OWNER_NUMBER,
        body=body
    )


# ========== WEBHOOK ==========
@app.route("/webhook", methods=["POST"])
def webhook():
    clean_sessions()

    incoming = request.values.get("Body", "").strip()
    sender = request.values.get("From")

    resp = MessagingResponse()
    msg = resp.message()

    if sender not in user_sessions:
        user_sessions[sender] = {
            "stage": "name",
            "time": time.time(),
            "name": None,
            "order": {},
            "table": None
        }
        msg.body(f"👋 Welcome to *{CAFE_NAME}*! What's your name?")
        return str(resp)

    s = user_sessions[sender]
    s["time"] = time.time()

    if s["stage"] == "name":
        s["name"] = incoming
        s["stage"] = "order"
        msg.body(f"Nice to meet you, {incoming}! 😊\n\n{menu_text()}")
        return str(resp)

    if s["stage"] == "order":
        if incoming.lower() == "done":
            if not s["order"]:
                msg.body("❌ No items added yet.")
                return str(resp)
            s["stage"] = "table"
            msg.body("Please provide your table number:")
            return str(resp)

        item, qty = parse_order(incoming)

        if not item:
            msg.body(f"❌ Invalid item.\n\n{menu_text()}")
            return str(resp)

        if menu[item]["qty"] < qty:
            msg.body(f"❌ Only {menu[item]['qty']} {item}(s) available.")
            return str(resp)

        s["order"][item] = s["order"].get(item, 0) + qty
        msg.body(f"✅ Added {qty} x {item.title()}\n\nAdd more or type *done*.")
        return str(resp)

    if s["stage"] == "table":
        s["table"] = incoming

        for item, qty in s["order"].items():
            menu[item]["qty"] -= qty

        notify_owner(s["name"], s["order"], s["table"], sender)

        msg.body(
            f"🎉 Order confirmed!\n\n"
            f"Thank you {s['name']}.\n"
            f"Table: {s['table']}\n"
            "Your order is being prepared 😊"
        )

        del user_sessions[sender]
        return str(resp)


# ========== HEALTH ==========
@app.route("/health")
def health():
    return jsonify({"status": "running", "sessions": len(user_sessions)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
