from flask import request, jsonify
from app import app, db
from app.models import Transaction
from datetime import datetime
import requests

ETHERSCAN_API_KEY = ''
UNISWAP_WETH_USDC_ADDRESS = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'

@app.before_first_request
def create_tables():
    db.create_all()

# Fetch transactions from Etherscan API
def fetch_transactions():
    url = f'https://api.etherscan.io/api?module=account&action=tokentx&address={UNISWAP_WETH_USDC_ADDRESS}&sort=desc&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('result', [])
    return []

@app.route('/api/txns', methods=['GET'])
def get_transactions():
    hash = request.args.get('hash', None)
    start_date = request.args.get('startDate', None)
    end_date = request.args.get('endDate', None)
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 50))

    # Fetch all transactions from Etherscan
    transactions = fetch_transactions()

    # Filter transactions by hash
    if hash:
        transactions = [txn for txn in transactions if txn['hash'] == hash]

    # Filter transactions by date range (timestamp)
    if start_date:
        start_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        transactions = [txn for txn in transactions if int(txn['timeStamp']) >= start_timestamp]
    
    if end_date:
        end_timestamp = datetime.strptime(end_date, "%Y-%m-%d").timestamp()
        transactions = [txn for txn in transactions if int(txn['timeStamp']) <= end_timestamp]

    # Paginate results
    total = len(transactions)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_transactions = transactions[start_index:end_index]

    return jsonify({
        'total': total,
        'page': page,
        'pageSize': page_size,
        'transactions': paginated_transactions
    })

@app.route('/api/eth-now', methods=['GET'])
def get_eth_price():
    response = requests.get(BINANCE_API_URL)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)