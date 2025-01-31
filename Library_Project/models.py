from . import db     # access db object from __init__ file


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tag_uid = db.Column(db.String(100), nullable=False)   # unique=True
    email = db.Column(db.String(100), nullable=False)     #unique=True
    created_at = db.Column(db.DateTime, default=db.func.now())

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    rfid_tag = db.Column(db.String(100), nullable=False)     # unique=True
    is_borrowed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)   # referencing a column of another model
    timestamp = db.Column(db.DateTime, default=db.func.now())
    action = db.Column(db.String(10))    # borrow or return
    book = db.relationship("Book", backref='transactions')
    user = db.relationship("User", backref='transactions')