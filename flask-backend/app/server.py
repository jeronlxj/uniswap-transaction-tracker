from flask import request, jsonify
from app import app, db
from app.models import Transaction
from datetime import datetime
import requests, json

ETHERSCAN_API_KEY = 'MVAI2RH5N6QTIURJFMEYDGJ283ZA8YGJWN'
UNISWAP_WETH_USDC_ADDRESS = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'

class TransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Transaction):
            return {
                "hash": obj.hash,
                "fee_usdt": obj.fee_usdt,
                "timestamp": obj.timestamp.timestamp(),
            }
        return super().default(obj)

def get_historical_eth_price(timestamp):
    ts = timestamp * 1000  # Convert to milliseconds
    binance_api_url = f'https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1m&startTime={ts}&endTime={str(ts + 120000)}'
    try:
        response = requests.get(binance_api_url)
        data = response.json()
        # print("data", data)
        if data:
            kline = data[0]  
            # open_time = kline[0] 
            # open_price = float(kline[1]) 
            # high_price = float(kline[2]) 
            # low_price = float(kline[3]) 
            close_price = float(kline[4]) 
            return close_price
        else:
            print("No historical eth data")
            return get_eth_price()
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
    # eth_price = get_eth_price()
    with db.session.no_autoflush:
        for txn in transactions:
            transaction = Transaction.query.filter_by(hash=txn['hash']).first()
            if not transaction and txn['tokenSymbol'] == 'USDC':
                # print(txn)
                fee_eth = float((float(txn['gasPrice'])) / (10.0**18) * float(txn['gasUsed']))
                # his_price = float(get_historical_eth_price(int(txn['timeStamp'])))
                # if not isinstance(fee_eth, float): print ("fee_eth is not a float",fee_eth)
                # if not isinstance(his_price, float): print ("his_price is not a float",his_price)
                transaction = Transaction(
                    hash=txn['hash'],
                    # fee_usdt=fee_eth * his_price,
                    fee_usdt=float(txn['value']),
                    # fee_usdt=1,
                    timestamp=datetime.fromtimestamp(int(txn['timeStamp']))
                )
                db.session.add(transaction)
                db.session.flush()
        db.session.commit()

def get_block_number_by_time(timestamp):
    url = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['result']  # Block number
    return None

def fetch_historical_transactions(start_timestamp, end_timestamp):
    start_block = get_block_number_by_time(start_timestamp)
    end_block = get_block_number_by_time(end_timestamp)

    if not start_block or not end_block:
        raise ValueError("Could not fetch block numbers for the given timestamps")

    url = f'https://api.etherscan.io/api?module=account&action=tokentx&address={UNISWAP_WETH_USDC_ADDRESS}&startblock={start_block}&endblock={end_block}&sort=asc&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get('result', [])
    return []

def record_real_time_transactions():
    with app.app_context():
        transactions = fetch_transactions()
        save_transactions(transactions)

@app.route('/api/txns', methods=['GET'])
def get_transactions():
    hash = request.args.get('hash', None)
    start_time = request.args.get('startTime', None)
    end_time = request.args.get('endTime', None)
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 50))

    print("page", page)
    query = Transaction.query 
    # print("query", query)

    if hash:
        query = query.filter(Transaction.hash == hash)

    if start_time:
        query = query.filter(Transaction.timestamp >= datetime.fromisoformat(start_time))

    if end_time:
        query = query.filter(Transaction.timestamp <= datetime.fromisoformat(end_time))

    total = query.count()
    transactions = query.order_by(Transaction.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    print(type(json.dumps(transactions, cls=TransactionEncoder)))
    return jsonify({
        'total': total,
        'page': page,
        'pageSize': page_size,
        'transactions': json.dumps(transactions, cls=TransactionEncoder),
    })

@app.route('/api/batch', methods=['POST'])
def fetch_batch_transactions():
    start_date = request.json.get('startDate', None)
    end_date = request.json.get('endDate', None)

    if not start_date or not end_date:
        return jsonify({'error': 'Start and end date required'}), 400

    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    try:
        transactions = fetch_historical_transactions(start_timestamp, end_timestamp)
        if not transactions:
            return jsonify({'error': 'No transactions found for this period.'}), 404
        save_transactions(transactions)

        return jsonify({'message': f'Successfully saved {len(transactions)} transactions.'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/txns/<txn_hash>', methods=['GET'])
def get_transaction_by_hash(txn_hash):
    transaction = Transaction.query.filter_by(hash=txn_hash).first()
    if transaction:
        return jsonify({
            'hash': transaction.hash,
            'fee_usdt': transaction.fee_usdt,
            'timestamp': transaction.timestamp.timestamp()
        })
    return jsonify({"error": "Transaction not found"}), 404

@app.route('/api/summary', methods=['GET'])
def get_summary():
    total_usdt = db.session.query(db.func.sum(Transaction.fee_usdt)).scalar() or 0
    print("total_usdt", total_usdt)
    return jsonify({
        'total_usdt': total_usdt,
    })

@app.route('/api/eth-now', methods=['GET'])
def get_eth_now():
    return jsonify({'price': get_eth_price()})