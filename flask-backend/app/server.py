from flask import request, jsonify
from app import app, db
from app.models import Transaction
from datetime import datetime
import requests

ETHERSCAN_API_KEY = ''
UNISWAP_WETH_USDC_ADDRESS = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'

def get_historical_eth_price(timestamp):
    ts = timestamp * 1000  # Convert to milliseconds
    binance_api_url = f'https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1m&startTime={ts}&endTime={ts + 120000}'
    
    try:
        response = requests.get(binance_api_url)
        data = response.json()
        if data:
            kline = data[0]  
            # open_time = kline[0] 
            # open_price = float(kline[1]) 
            # high_price = float(kline[2]) 
            # low_price = float(kline[3]) 
            close_price = float(kline[4]) 
            return close_price
        else:
            raise ValueError('No data available for the given timestamp.') 
    except Exception as e:
        print(f'Error: {e}')
        return None
    
def get_eth_price():
    response = requests.get(BINANCE_API_URL)
    return response.json().get('price', None)

# Fetch transactions from Etherscan API
def fetch_transactions():
    url = f'https://api.etherscan.io/api?module=account&action=tokentx&address={UNISWAP_WETH_USDC_ADDRESS}&sort=desc&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('result', [])
    return []

def save_transactions(transactions):
    for txn in transactions:
        transaction = Transaction.query.filter_by(hash=txn['hash']).first()
        if not transaction:
            transaction = Transaction(
                hash=txn['hash'],
                fee_usdt=float(txn['value']),
                timestamp=datetime.fromtimestamp(int(txn['timeStamp']))
            )
            db.session.add(transaction)
    db.session.commit()

def record_real_time_transactions():
    transactions = fetch_transactions()
    save_transactions(transactions)

@app.route('/api/txns', methods=['GET'])
def get_transactions():
    hash = request.args.get('hash', None)
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 50))

    query = Transaction.query

    if hash:
        query = query.filter(Transaction.hash == hash)

    if start_date:
        start_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        query = query.filter(Transaction.timestamp >= datetime.fromtimestamp(start_timestamp))

    if end_date:
        end_timestamp = datetime.strptime(end_date, "%Y-%m-%d").timestamp()
        query = query.filter(Transaction.timestamp <= datetime.fromtimestamp(end_timestamp))

    total = query.count()
    transactions = query.order_by(Transaction.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'total': total,
        'page': page,
        'pageSize': page_size,
        'transactions': transactions
    })

@app.route('/api/txns/<txn_hash>', methods=['GET'])
def get_transaction_by_hash(txn_hash):
    transaction = Transaction.query.filter_by(hash=txn_hash).first()
    if transaction:
        return jsonify({
            'hash': transaction.hash,
            'fee_usdt': transaction.fee_usdt,
            'timestamp': transaction.timestamp
        })
    return jsonify({"error": "Transaction not found"}), 404

@app.route('/api/summary', methods=['GET'])
def get_summary():
    total_usdt = db.session.query(db.func.sum(Transaction.fee_usdt)).scalar() or 0
    return jsonify({
        'total_usdt': total_usdt,
    })

@app.route('/api/eth-now', methods=['GET'])
def get_eth_now():
    return jsonify({'price': get_eth_price()})

if __name__ == '__main__':
    app.run(debug=True)