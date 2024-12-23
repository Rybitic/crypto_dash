from logging import lastResort

from flask import Flask, render_template, request, redirect, session, url_for,jsonify
from functools import wraps
from datetime import timedelta, datetime, timezone

from pandas.io.clipboard import lazy_load_stub_paste
from pycares.errno import value
from pymongo import MongoClient
from bson import ObjectId
import requests
from apscheduler.schedulers.background import BackgroundScheduler

client = MongoClient('mongodb+srv://abitdevvv:India123@supr.l5109.mongodb.net/')
db = client['data']
user = db['user']
orders = db['orders']

# user_ = {
#     "username": "test",
#     "balance":{
#         "usdt": 100,
#         "pepe": 0
#     }
# }
# user.insert_one(user_)

app = Flask(__name__)
app.secret_key = 'j891nudh371gduo9nd98ugf783283'

# Session lifetime
app.permanent_session_lifetime = timedelta(days=1)

# User credentials (for demo purposes, replace with a secure method in production)
users = {
    "rhythm": "123",
    "towering": "123"
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_market_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    return float(response.json()['lastPrice'])


def check_and_fulfill_orders():
# Get all open limit orders
    open_orders = orders.find({"status": "open", "order_type": "limit", "pos": "long"})

    for order in open_orders:
        symbol = order['symbol']
        price = order['price']
        side = order['side']
        qty = order['quantity']

        # Get the current market price for the symbol
        market_price = get_market_price(symbol)

        # Check if the limit order should be fulfilled
        if (side == "buy" and market_price <= price) or (side == "sell" and market_price >= price):
            print(1)
            # Fulfill the order (update status and executed price)
            db.orders.update_one(
                {"_id": order["_id"]},
                {
                    "$set": {
                        "status": "executed",
                        "executed_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                        "executed_price": market_price
                    }
                }
            )

            # Here you could update the user balance based on the order (simplified logic)
            user_id = order['user_id']
            if side == "buy":
                amount = qty * price
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance - amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin + qty}})
            elif side == "sell":
                amount = qty * price
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance + amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin - qty}})

            print(f"Long Limit Order {order['_id']} fulfilled at price {market_price}")

    open_orders = orders.find({"status": "open", "order_type": "stop_limit", "pos": "long"})

    for order in open_orders:
        symbol = order['symbol']
        price = order['price']
        side = order['side']
        qty = order['quantity']

        # Get the current market price for the symbol
        market_price = get_market_price(symbol)

        print(f"Market Price: {market_price}")
        print(f"Stop Price: {price}")

        # Check if the limit order should be fulfilled
        if (side == "buy" and market_price >= price) or (side == "sell" and market_price <= price):
            print(2)
            # Fulfill the order (update status and executed price)
            db.orders.update_one(
                {"_id": order["_id"]},
                {
                    "$set": {
                        "status": "executed",
                        "executed_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                        "executed_price": market_price
                    }
                }
            )

            # Here you could update the user balance based on the order (simplified logic)
            user_id = order['user_id']
            if side == "buy":
                amount = qty * price
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance - amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin + qty}})
            elif side == "sell":
                amount = qty * price
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance + amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin - qty}})

            print(f"Stop Limit Long Order {order['_id']} fulfilled at price {market_price}")

    open_orders = orders.find({"status": "open", "order_type": "limit", "pos": "short"})

    for order in open_orders:
        symbol = order['symbol']
        price = order['price']
        side = order['side']
        qty = order['quantity']

        # Get the current market price for the symbol
        market_price = get_market_price(symbol)

        print(f"Market Price: {market_price}")
        print(f"Stop Price: {price}")

        # Check if the limit order should be fulfilled
        if (side == "buy" and market_price <= price) or (side == "sell" and market_price >= price):
            print(3)
            print(f"either {price} is less than {market_price} or {price} is greater than {market_price}")
            # Fulfill the order (update status and executed price)
            db.orders.update_one(
                {"_id": order["_id"]},
                {
                    "$set": {
                        "status": "executed",
                        "executed_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                        "executed_price": market_price
                    }
                }
            )

            # Here you could update the user balance based on the order (simplified logic)
            user_id = order['user_id']
            if side == "sell":
                amount = qty * price
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance - amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin - qty}})
            elif side == "buy":
                last_order = orders.find({"status": "executed", "pos": "short", "symbol": "PEPEUSDT", "side": "sell"})
                last_order_data = []
                for order in last_order:
                    last_order_data.append(order)
                last_order = last_order_data[-1]
                last_price = float(last_order["executed_price"])
                amount = float(last_order["quantity"]) * float(last_order["executed_price"])
                # calculate pnl of short
                pnl = ((last_price - price) * qty) + amount
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance + pnl}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin + qty}})

            print(f"Limit Short Order {order['_id']} fulfilled at price {market_price}")

    open_orders = orders.find({"status": "open", "order_type": "stop_limit", "pos": "short"})

    for order in open_orders:
        symbol = order['symbol']
        price = order['price']
        side = order['side']
        qty = order['quantity']

        # Get the current market price for the symbol
        market_price = get_market_price(symbol)

        print(f"Market Price: {market_price}")
        print(f"Stop Price: {price}")

        # Check if the limit order should be fulfilled
        if (side == "buy" and market_price >= price) or (side == "sell" and market_price <= price):
            print(4)
            # Fulfill the order (update status and executed price)
            db.orders.update_one(
                {"_id": order["_id"]},
                {
                    "$set": {
                        "status": "executed",
                        "executed_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                        "executed_price": market_price
                    }
                }
            )

            # Here you could update the user balance based on the order (simplified logic)
            user_id = order['user_id']
            if side == "sell":
                amount = qty * price
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance - amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin - qty}})
            elif side == "buy":
                last_order = orders.find({"status": "executed", "pos": "short", "symbol": "PEPEUSDT", "side": "sell"})
                last_order_data = []
                for order in last_order:
                    last_order_data.append(order)
                last_order = last_order_data[-1]
                last_price = float(last_order["executed_price"])
                amount = float(last_order["quantity"]) * float(last_order["executed_price"])
                pnl = ((last_price - price) * qty) + amount
                balance = user.find_one({"username": user_id})["balance"]["usdt"]
                balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance + pnl}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin + qty}})

            print(f"Stop Limit Short Order {order['_id']} fulfilled at price {market_price} 4")


    balance_pepe = user.find_one({"username": "test"})["balance"]["pepe"]
    if balance_pepe == 0:
        get_all_open_orders = orders.find({"status": "open"})
        for order in get_all_open_orders:
            orders.update_one({"_id": order["_id"]}, {
                "$set": {"status": "cancelled", "executed_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S")}})


@app.route('/', methods=['GET', 'POST'])
def login():
    # Check if the user is already logged in
    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get form inputs
        entered_username = request.form.get('username', '').lower()
        entered_password = request.form.get('password', '')

        # Validate user credentials
        if entered_username in users and users[entered_username] == entered_password:
            session['logged_in'] = True
            session['username'] = entered_username
            return redirect(url_for('index'))
        else:
            return "Invalid username or password", 401

    return render_template('login.html')

@app.route('/dash')
@login_required
def index():
    balance_usdt = user.find_one({"username": "test"})["balance"]["usdt"]
    amount_usdt = balance_usdt
    balance_pepe = user.find_one({"username": "test"})["balance"]["pepe"]
    value_pepe = abs(balance_pepe) * get_market_price("PEPEUSDT")
    balance_usdt += value_pepe
    balance_usdt = round(balance_usdt, 2)
    open_orders = list(orders.find({"status": "open"}))
    closed_orders = list(orders.find({"status": "executed"}))
    number_of_closed_orders = len(closed_orders)
    if not number_of_closed_orders % 2 == 0:
        closed_orders = closed_orders[:-1]

    win = 0
    lose = 0
    for i in closed_orders:
        if i['order_type'] == 'limit':
            win += 1
        elif i['order_type'] == 'stop_limit':
            lose += 1
    winrate = win / (win + lose) * 100

    return render_template('trade.html', balance_usdt=balance_usdt, balance_pepe=balance_pepe, open_orders=open_orders, closed_orders=closed_orders,
                           amount_usdt=amount_usdt, amount_pepe=balance_pepe, winrate=winrate, win=win, lose=lose)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/place_long', methods=['POST'])
def place_long():
    try:
        # Get data from the request
        data = request.json
        user_id = "test"
        print(data)
        # Validate required fields
        required_fields = ["symbol", "type", "side", "qty", "price"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
        balance = user.find_one({"username": user_id})["balance"]["usdt"]

        if balance_coin <= 0 and data['side'] == "sell":
            return jsonify({"error": "Insufficient balance"}), 400

        if balance <= 0 and data['side'] == "buy":
            return jsonify({"error": "Insufficient balance"}), 400


        # Extract order data
        symbol = data['symbol']
        order_type = data['type'].lower()
        side = data['side'].lower()
        qty = float(data['qty'])
        price = float(data['price'])

        if order_type not in ["market", "limit", "stop_limit"]:
            return jsonify({"error": "Invalid order type"}), 400

        if qty > balance_coin and data['side'] == "sell":
            return jsonify({"error": "Insufficient balance"}), 400

        if price <= 0 or order_type == "market":
            url = "https://api.binance.com/api/v3/ticker/24hr?symbol=PEPEUSDT"
            response = requests.get(url)
            price = float(response.json()['lastPrice'])
        amount = qty * price

        if amount > balance and side == "buy":
            return jsonify({"error": "Insufficient balance"}), 400

        # Create the order object
        if order_type == "market":
            order = {
                "user_id": user_id,
                "symbol": symbol,
                "order_type": order_type,
                "side": side,
                "pos": "long",
                "quantity": qty,
                "price": price,
                "status": "executed",
                "created_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                "executed_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                "executed_price": price
            }
            if side == "buy":
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance - amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin + qty}})
            elif side == "sell":
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance + amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin - qty}})

        else:
            order = {
                "user_id": user_id,
                "symbol": symbol,
                "order_type": order_type,
                "pos": "long",
                "side": side,
                "quantity": qty,
                "price": price,
                "status": "open",  # Order is open initially
                "created_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                "executed_at": None,
                "executed_price": None
            }

        # Insert the order into the Orders collection
        order_id = orders.insert_one(order).inserted_id

        # Respond with success and the order ID
        return jsonify({"message": "Order placed successfully", "order_id": str(order_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/place_short', methods=['POST'])
def place_short():
    try:
        # Get data from the request
        data = request.json
        user_id = "test"
        print(data)
        # Validate required fields
        required_fields = ["symbol", "type", "side", "qty", "price"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        balance_coin = user.find_one({"username": user_id})["balance"]["pepe"]
        balance = user.find_one({"username": user_id})["balance"]["usdt"]

        if balance_coin >= 0 and data['side'] == "buy":
            return jsonify({"error": "Insufficient balance"}), 400

        if balance <= 0 and data['side'] == "sell":
            return jsonify({"error": "Insufficient balance"}), 400


        # Extract order data
        symbol = data['symbol']
        order_type = data['type'].lower()
        side = data['side'].lower()
        qty = float(data['qty'])
        price = float(data['price'])

        if order_type not in ["market", "limit", "stop_limit"]:
            return jsonify({"error": "Invalid order type"}), 400

        if qty < balance_coin and data['side'] == "buy":
            return jsonify({"error": "Insufficient balance"}), 400

        if price <= 0 or order_type == "market":
            url = "https://api.binance.com/api/v3/ticker/24hr?symbol=PEPEUSDT"
            response = requests.get(url)
            price = float(response.json()['lastPrice'])
        amount = qty * price

        if amount > balance and side == "sell":
            return jsonify({"error": "Insufficient balance"}), 400

        # Create the order object
        if order_type == "market":
            order = {
                "user_id": user_id,
                "symbol": symbol,
                "order_type": order_type,
                "pos": "short",
                "side": side,
                "quantity": qty,
                "price": price,
                "status": "executed",
                "created_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                "executed_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                "executed_price": price
            }
            if side == "sell":
                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance - amount}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin - qty}})
            elif side == "buy":
                last_order = orders.find_one({"status": "executed", "pos": "short", "symbol": symbol})
                last_price = float(last_order["executed_price"])
                amount = float(last_order["quantity"]) * last_price
                # calculate pnl of short
                pnl = ((last_price - price) * qty) + amount

                user.update_one({"username": user_id}, {"$set": {"balance.usdt": balance + pnl}})
                user.update_one({"username": user_id}, {"$set": {"balance.pepe": balance_coin + qty}})

        else:
            order = {
                "user_id": user_id,
                "symbol": symbol,
                "order_type": order_type,
                "pos": "short",
                "side": side,
                "quantity": qty,
                "price": price,
                "status": "open",  # Order is open initially
                "created_at": datetime.now(timezone.utc).strftime("%d-%B-%Y %H-%M-%S"),
                "executed_at": None,
                "executed_price": None
            }

        # Insert the order into the Orders collection
        order_id = orders.insert_one(order).inserted_id

        # Respond with success and the order ID
        return jsonify({"message": "Order placed successfully", "order_id": str(order_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/balance', methods=['GET'])
def balance():
    balance_usdt = user.find_one({"username": "test"})["balance"]["usdt"]
    balance_pepe = user.find_one({"username": "test"})["balance"]["pepe"]
    return jsonify({"usdt": balance_usdt, "pepe": balance_pepe})

@app.route('/last_order', methods=['GET'])
def last_order_():
    last_order_api = orders.find({"status": "executed", "symbol": "PEPEUSDT", 'order_type': 'market'})
    last_order_data_api = []
    for order in last_order_api:
        order['_id'] = str(order['_id'])  # Convert ObjectId to string
        last_order_data_api.append(order)
    last_order_api = last_order_data_api[-1]
    return jsonify(last_order_api)
@app.route('/reset', methods=['GET'])
def reset():
    user.update_one({"username": "test"}, {"$set": {"balance.usdt": 100}})
    user.update_one({"username": "test"}, {"$set": {"balance.pepe": 0}})
    orders.delete_many({})
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


scheduler = BackgroundScheduler()
scheduler.add_job(check_and_fulfill_orders, 'interval', seconds=5)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
