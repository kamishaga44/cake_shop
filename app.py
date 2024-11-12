from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost/shop_db'
app.config['SECRET_KEY'] = "my secret key here"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модель пользователя, добавлено наследование от UserMixin для Flask-Login
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    user_fname = db.Column(db.String(80), nullable=False)
    user_sname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def get_id(self):
        return str(self.user_id)

class Cake(db.Model):
    __tablename__ = 'cakes'
    cake_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=True)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    cake_id = db.Column(db.Integer, db.ForeignKey('cakes.cake_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    cake = db.relationship('Cake', backref=db.backref('orders', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Главная страница
@app.route('/')
def home():
    cakes = Cake.query.all()
    return render_template('home.html', cakes=cakes)

@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        login = request.form['username']
        fname = request.form['fname']
        sname = request.form['sname']
        pass1 = request.form['password']
        pass2 = request.form['password_conf']

        user_exists = User.query.filter_by(login=login).first()
        if user_exists:
            flash("Пользователь с таким логином уже существует!", "error")
        elif pass1 != pass2:
            flash("Пароли не совпадают!", "error")
        else:
            try:
                new_user = User(login=login, user_fname=fname, user_sname=sname, password=pass1)
                db.session.add(new_user)
                db.session.commit()
                flash("Вы успешно зарегистрированы!", "success")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"Произошла ошибка при регистрации: {str(e)}", "error")
                db.session.rollback()

    return render_template("registration.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(login=request.form['username'], password=request.form['password']).first()
        if user:
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("The login or username were wrong", "error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы!", "success")
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/favorites')
@login_required
def favorites():
    if 'favorites' not in session:
        session['favorites'] = []
    favorites_cakes = [Cake.query.get(cake_id) for cake_id in session['favorites']]
    return render_template('favorites.html', favorites=favorites_cakes)

@app.route('/like/<int:cake_id>')
@login_required
def like(cake_id):
    if 'favorites' not in session:
        session['favorites'] = []
    if cake_id not in session['favorites']:
        session['favorites'].append(cake_id)
    return redirect(url_for('home'))

@app.route('/remove_favorite/<int:cake_id>')
@login_required
def remove_favorite(cake_id):
    if 'favorites' in session and cake_id in session['favorites']:
        session['favorites'].remove(cake_id)
    return redirect(url_for('favorites'))

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        user_id = current_user.user_id
        cake_id = request.form['cake_id']
        quantity = int(request.form['quantity'])
        phone = request.form['phone']

        cake = Cake.query.get(cake_id)
        if not cake:
            flash("This cake does not exist!", "error")
            return redirect(url_for('home'))

        new_order = Order(user_id=user_id, cake_id=cake_id, quantity=quantity, phone=phone)
        db.session.add(new_order)
        db.session.commit()

        return jsonify({"message": "Cake added to your cart successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding cake to cart: {str(e)}"}), 500

@app.route('/view_cart')
@login_required
def view_cart():
    user_id = current_user.user_id
    orders = Order.query.filter_by(user_id=user_id).all()

    cart_items = []
    for order in orders:
        cake = Cake.query.get(order.cake_id)
        cart_items.append({
            "cake": cake,
            "quantity": order.quantity,
            "phone": order.phone
        })

    return render_template('cart.html', cart_items=cart_items)

@app.route('/delete_account', methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        user_to_delete = current_user
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Ваш аккаунт был успешно удалён!", "success")
            logout_user()
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"Ошибка при удалении аккаунта: {str(e)}", "error")
            db.session.rollback()

    return render_template('delete_account.html')

@app.route('/aboutUs')
def about_us():
    return render_template('about.html')

@app.route('/contact')
def contacts():
    return render_template('contacts.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
