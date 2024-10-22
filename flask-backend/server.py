from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

ETHERSCAN_API_KEY = ''
BINANCE_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'

@app.route('/api')
def service():
    return {'message': 'Hello, World!'}

@app.route('/api/txns', methods=['GET'])
def get_transactions():
    address = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640' # Uniswap WETH-USDC pool
    url = f'https://api.etherscan.io/api?module=account&action=tokentx&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}'
    response = requests.get(url)
    return jsonify(response.json())

@app.route('/api/eth-now', methods=['GET'])
def get_eth_price():
    response = requests.get(BINANCE_API_URL)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)