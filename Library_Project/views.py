from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .models import User, Book, Transaction
from . import db
from flask_login import login_required, login_user, UserMixin, current_user, logout_user
import serial
import threading

views = Blueprint("views", __name__)
serial_lock = threading.Lock()

try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
except serial.SerialException as e:
    print(f"Error opening the port {e}")

def trigger_buzzer():
    try:
        arduino.write(b'BUZZER_ON\n')
    except Exception as e:
        print(f"Error sending command to Arduino: {e}")

PREDEFINED_USERNAME = 'admin'
PREDEFINED_PASSWORD = 'admin'

class User1(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

users = {
    "admin": User1(id=1, username='admin')
}

@views.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        if name == PREDEFINED_USERNAME and password == PREDEFINED_PASSWORD:
            user = users.get(name)
            login_user(user)
            flash("Logged in successfully", "success")
            return redirect(url_for('views.manage_users'))
        else:
            flash("Incorrect login credentials, try again")
    return render_template("index.html", user=current_user)

@views.route('/manage_users', methods=["GET", "POST"])
@login_required
def manage_users():
    if request.method == "POST":
        uid = request.form.get('uid')
        name = request.form.get('name')
        email = request.form.get("email")
        new_user = User(name=name, tag_uid=uid, email=email)
        db.session.add(new_user)
        db.session.commit()
    all_users = User.query.all()
    return render_template("manage_users.html", all_users=all_users, user=current_user)

@views.route('/manage_books', methods=["GET", "POST"])
@login_required
def manage_books():
    if request.method == 'POST':
        uid = request.form.get("uid")
        title = request.form.get("title")
        author = request.form.get("author")
        new_book = Book(title=title, rfid_tag=uid, author=author)
        db.session.add(new_book)
        db.session.commit()
    all_books = Book.query.all()
    return render_template('manage_books.html', all_books=all_books, user=current_user)

@views.route('/get_uid')
@login_required
def get_uid():
    with serial_lock:
        if arduino.in_waiting > 0:
            uid = arduino.readline().decode('utf-8').strip()
            return jsonify({'uid': uid})
        return jsonify({'uid':'no uid detected'})

@views.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        user_uid = request.form.get("user_uid")
        book_uid = request.form.get("book_uid")
        user = User.query.filter_by(tag_uid=user_uid).first()
        book = Book.query.filter_by(rfid_tag=book_uid).first()

        if user and book:
            if book.is_borrowed:    # Handling the return transaction, default=False
                tr1 = Transaction(user_id=user.id, book_id=book.id, action="return")
                book.is_borrowed = False
                flash('Book returned successfully', 'success')
                db.session.add(tr1)
                # redirect(url_for("views.transactions"))
            else:     # Handling the borrow transaction
                tr1 = Transaction(user_id=user.id, book_id=book.id, action="borrow")
                db.session.add(tr1)
                book.is_borrowed = True
                flash("Book borrowed successfully", 'success')
                # redirect(url_for("views.transactions"))
            db.session.commit()
        else:
            flash("User or Book credentials are not available in the database", "error")
            trigger_buzzer()
        redirect(url_for("views.transactions"))
    transactions = Transaction.query.all()
    return render_template("transactions.html", transactions=transactions, user=current_user)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

