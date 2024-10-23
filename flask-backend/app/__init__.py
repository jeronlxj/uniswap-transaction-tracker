from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)
CORS(app) 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "db", "uniswap.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

if not os.path.exists(os.path.join(BASE_DIR, "db")):
    os.makedirs(os.path.join(BASE_DIR, "db"))

with app.app_context():
    db.create_all()

from app.server import *

scheduler = BackgroundScheduler()
scheduler.add_job(record_real_time_transactions, 'interval', seconds=30)
scheduler.start()