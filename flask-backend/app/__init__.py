from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from app.server import record_real_time_transactions 

app = Flask(__name__)
CORS(app) 


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/uniswap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

scheduler = BackgroundScheduler()
scheduler.add_job(record_real_time_transactions, 'interval', seconds=30)
scheduler.start()

from app.server import *