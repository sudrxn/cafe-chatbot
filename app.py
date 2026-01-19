from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import time

app = Flask(__name__)

# ===== CAFE MENU DATABASE =====
# Add your cafe's actual menu here
menu = {
    "cappuccino": {"price": 120, "wait_time": "5 minutes", "quantity": 10},
    "latte": {"price": 150, "wait_time": "5 minutes", "quantity": 8},
    "espresso": {"price": 100, "wait_time": "3 minutes", "quantity": 15},
    "sandwich": {"price": 80, "wait_time": "10 minutes", "quantity": 5},
    "burger": {"price": 150, "wait_time": "15 minutes", "quantity": 7},
    "tea": {"price": 50, "wait_time": "3 minutes", "quantity": 20}
}

# ===== TEMPORARY STORAGE (30 min sessions) =====
user_sessions = {}

# ===== CAFE OWNER'S WHATSAPP NUMBER =====
# Replace with actual owner's number
OWNER_NUMBER = "whatsapp:+919876543210"


def clean_old_sessions():
    """Remove sessions older than 30 minutes"""
    current_time = time.time()
    expired = [user for user, data in user_sessions.items() 
               if current_time - data.get('timestamp', 0) > 1800]  # 1800 sec = 30 min
    for user in expired:
        del user_sessions[user]


def get_menu_text():
    """Format menu for display"""
    menu_text = "📋 *Our Menu:*\n\n"
    for item, details in menu.items():
        menu_text += f"• {item.title()}: ₹{details['price']} ({details['wait_time']})\n"
    menu_text += "\nPlease type the item name to order!"
    return menu_text


def check_item_availability(item_name):
    """Check if item exists and is available"""
    item_name = item_name.lower().strip()
    if item_name in menu:
        if menu[item_name]['quantity'] > 0:
            return True, menu[item_name]
        else:
            return False, "Sorry, this item is currently out of stock!"
    else:
        return False, "Sorry, we don't have this item on our menu."


def notify_owner(customer_name, order_items, table_no, customer_number):
    """Send order details to cafe owner"""
    # This would send a WhatsApp message to owner
    # For now, we'll just print it (you'll implement actual sending later)
    order_summary = f"🔔 *NEW ORDER*\n\n"
    order_summary += f"Customer: {customer_name}\n"
    order_summary += f"Table: {table_no}\n"
    order_summary += f"Phone: {customer_number}\n\n"
    order_summary += "*Items:*\n"
    for item in order_items:
        order_summary += f"• {item}\n"
    
    print(f"\n{'='*50}")
    print("NOTIFICATION TO OWNER:")
    print(order_summary)
    print(f"{'='*50}\n")
    
    return order_summary


@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook - receives messages from WhatsApp"""
    
    clean_old_sessions()  # Clean expired sessions
    
    # Get incoming message details
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    # Create Twilio response object
    resp = MessagingResponse()
    msg = resp.message()
    
    # Initialize session if new user
    if sender not in user_sessions:
        user_sessions[sender] = {
            'stage': 'greeting',
            'timestamp': time.time(),
            'name': None,
            'order': [],
            'table_no': None
        }
    
    session = user_sessions[sender]
    session['timestamp'] = time.time()  # Update timestamp
    
    # ===== CONVERSATION FLOW =====
    
    # Stage 1: Greeting
    if session['stage'] == 'greeting':
        msg.body("👋 Welcome to [Cafe Name]! What's your name?")
        session['stage'] = 'awaiting_name'
    
    # Stage 2: Get customer name
    elif session['stage'] == 'awaiting_name':
        session['name'] = incoming_msg
        msg.body(f"Nice to meet you, {session['name']}! 😊\n\nWhat would you like me to serve you today?\n\n{get_menu_text()}")
        session['stage'] = 'awaiting_order'
    
    # Stage 3: Take order
    elif session['stage'] == 'awaiting_order':
        available, result = check_item_availability(incoming_msg)
        
        if available:
            item_name = incoming_msg.lower().strip()
            session['order'].append(item_name)
            
            response_text = f"✅ Great! {item_name.title()} added to your order.\n\n"
            response_text += f"💰 Price: ₹{result['price']}\n"
            response_text += f"⏱️ Preparation time: {result['wait_time']}\n\n"
            response_text += "Would you like to:\n"
            response_text += "1. Add more items (type item name)\n"
            response_text += "2. Finish order (type 'done')"
            
            msg.body(response_text)
        else:
            msg.body(f"❌ {result}\n\nPlease choose from our menu:\n\n{get_menu_text()}")
    
        # Check if user said "done"
        if incoming_msg.lower() == 'done' and len(session['order']) > 0:
            order_summary = "📝 *Your Order:*\n\n"
            total_price = 0
            max_wait = 0
            
            for item in session['order']:
                order_summary += f"• {item.title()} - ₹{menu[item]['price']}\n"
                total_price += menu[item]['price']
                wait_minutes = int(menu[item]['wait_time'].split()[0])
                max_wait = max(max_wait, wait_minutes)
            
            order_summary += f"\n*Total: ₹{total_price}*\n"
            order_summary += f"⏱️ Total wait time: ~{max_wait} minutes\n\n"
            order_summary += "Please provide your table number:"
            
            msg.body(order_summary)
            session['stage'] = 'awaiting_table'
    
    # Stage 4: Get table number
    elif session['stage'] == 'awaiting_table':
        session['table_no'] = incoming_msg
        
        # Reduce quantity from menu
        for item in session['order']:
            menu[item]['quantity'] -= 1
        
        # Notify owner
        notify_owner(session['name'], session['order'], session['table_no'], sender)
        
        # Final confirmation to customer
        final_msg = f"🎉 Order confirmed!\n\n"
        final_msg += f"Thank you {session['name']}! Your order has been sent to the kitchen.\n"
        final_msg += f"Table: {session['table_no']}\n\n"
        final_msg += "We'll have it ready soon! 😊"
        
        msg.body(final_msg)
        
        # Clear session
        del user_sessions[sender]
    
    return str(resp)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "running", "active_sessions": len(user_sessions)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)