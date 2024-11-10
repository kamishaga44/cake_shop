from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost/shop_db'
app.config['SECRET_KEY'] = "my secret key here"

db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    user_fname = db.Column(db.String(80), nullable=False)
    user_sname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<User {self.login}>"


class Cake(db.Model):
    __tablename__ = 'cakes'
    cake_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Cake {self.name}>"


class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    cake_id = db.Column(db.Integer, db.ForeignKey('cakes.cake_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    cake = db.relationship('Cake', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.order_id} by User {self.user_id}>"


# Главная страница
@app.route('/')
def home():
    cakes = Cake.query.all()  # Получаем все торты из базы данных
    return render_template('home.html', cakes=cakes)


@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        login = request.form['username']
        fname = request.form['fname']
        sname = request.form['sname']
        pass1 = request.form['password']
        pass2 = request.form['password_conf']

        user_exists = db.session.query(User).filter_by(login=login).first()
        if user_exists:
            flash("Пользователь с таким логином уже существует!", "error")
            return redirect(url_for("registration"))
        elif pass1 != pass2:
            flash("Пароли не совпадают!", "error")
            return redirect(url_for("registration"))
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
                return redirect(url_for("registration"))

    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.session.query(User).filter_by(login=request.form['username'],
                                                password=request.form['password']).first()
        if user:
            session['authenticated'] = True
            session['uid'] = user.user_id
            session['username'] = user.login
            return redirect(url_for("home"))
        else:
            return render_template("login.html", context="The login or username were wrong")

    return render_template("login.html")


@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/favorites')
def favorites():
    if 'favorites' not in session:
        session['favorites'] = []
    favorites_cakes = [Cake.query.get(cake_id) for cake_id in session['favorites']]
    return render_template('favorites.html', favorites=favorites_cakes)


@app.route('/like/<int:cake_id>')
def like(cake_id):
    if 'favorites' not in session:
        session['favorites'] = []
    if cake_id not in session['favorites']:
        session['favorites'].append(cake_id)
    return redirect(url_for('home'))


@app.route('/remove_favorite/<int:cake_id>')
def remove_favorite(cake_id):
    if 'favorites' in session and cake_id in session['favorites']:
        session['favorites'].remove(cake_id)
    return redirect(url_for('favorites'))


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'uid' not in session:
        flash("Please log in to add items to your cart!", "error")
        return redirect(url_for('login'))

    try:
        user_id = session['uid']
        cake_id = request.form['cake_id']  # The cake ID from the form
        quantity = int(request.form['quantity'])  # Quantity
        phone = request.form['phone']  # User's phone for the order

        # Check if the cake exists
        cake = Cake.query.get(cake_id)
        if not cake:
            flash("This cake does not exist!", "error")
            return redirect(url_for('home'))

        # Add the order to the database
        new_order = Order(user_id=user_id, cake_id=cake_id, quantity=quantity, phone=phone)
        db.session.add(new_order)
        db.session.commit()

        # Respond with a success message
        return jsonify({"message": "Cake added to your cart successfully!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding cake to cart: {str(e)}"}), 500


# Просмотр корзины
@app.route('/view_cart')
def view_cart():
    if 'uid' not in session:
        flash("Please log in to view your cart!", "error")
        return redirect(url_for('login'))

    user_id = session['uid']
    # Get all orders related to the logged-in user
    orders = db.session.query(Order).filter_by(user_id=user_id).all()

    # Optional: Join Cake data to display cake details in the cart
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
def delete_account():
    if request.method == "POST":
        user_id = session.get('uid')

        if user_id:
            user_to_delete = User.query.get(user_id)

            if user_to_delete:
                try:
                    db.session.delete(user_to_delete)
                    db.session.commit()
                    flash("Ваш аккаунт был успешно удалён!", "success")
                    session.clear()
                    return redirect(url_for('home'))
                except Exception as e:
                    flash(f"Ошибка при удалении аккаунта: {str(e)}", "error")
                    db.session.rollback()
            else:
                flash("Пользователь не найден!", "error")
        return redirect(url_for('home'))

    return render_template('delete_account.html')


@app.route('/aboutUs')
def about_us():
    return render_template('about.html')


@app.route('/contact')
def contacts():
    return render_template('contacts.html')


# Инициализация базы данных
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
