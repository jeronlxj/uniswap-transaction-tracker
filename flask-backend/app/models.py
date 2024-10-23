from app import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(66), unique=True, nullable=False)
    fee_usdt = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Transaction {self.hash}>'

