from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
<<<<<<< HEAD
from flask_login import LoginManager, current_user
=======
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
>>>>>>> 76fbd312a37a45b92489564b9f04f0e6dc496c46


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost/shop_db'
app.config['SECRET_KEY'] = "my secret key here"

<<<<<<< HEAD
login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(db.Model):
=======
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
>>>>>>> 76fbd312a37a45b92489564b9f04f0e6dc496c46
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

<<<<<<< HEAD



@app.route('/')
def home():
    cakes = Cake.query.all()
    return render_template('home.html', cakes=cakes, current_user=current_user)
=======
@app.route('/')
def home():
    cakes = Cake.query.all()
    return render_template('home.html', cakes=cakes)
>>>>>>> 76fbd312a37a45b92489564b9f04f0e6dc496c46

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
<<<<<<< HEAD
            flash("There is already a user with this username.", "error")
            return redirect(url_for("registration"))
        elif pass1 != pass2:
            flash("Passwords do not match.", "error")
            return redirect(url_for("registration"))
=======
            flash("A user with this username already exists!", "error")
        elif pass1 != pass2:
            flash("Passwords do not match!", "error")
>>>>>>> 76fbd312a37a45b92489564b9f04f0e6dc496c46
        else:
            try:
                new_user = User(login=login, user_fname=fname, user_sname=sname, password=pass1)
                db.session.add(new_user)
                db.session.commit()
<<<<<<< HEAD
                flash("Registration was successful!", "success")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
=======
                flash("You have successfully registered!", "success")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"An error occurred during registration: {str(e)}", "error")
>>>>>>> 76fbd312a37a45b92489564b9f04f0e6dc496c46
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
            flash("The login or password was wrong", "error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out!", "success")
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/delete_account', methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        user_to_delete = current_user
        confirm_deletion = request.form.get('confirm_deletion')

        if confirm_deletion != "DELETE":
            flash("You must enter 'DELETE' in uppercase to confirm account deletion.", "error")
            return render_template('settings.html')

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Your account has been successfully deleted!", "success")
            session.clear()
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"Error deleting account: {str(e)}", "error")
            db.session.rollback()
    return render_template('settings.html')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    user = current_user

    if user.password != current_password:
        flash("Incorrect current password.", "error")
        return redirect(url_for('settings'))

    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "error")
        return redirect(url_for('settings'))

    user.password = new_password
    db.session.commit()

    flash("Password successfully updated.", "success")
    return redirect(url_for('settings'))

@app.route('/aboutUs')
def about_us():
    return render_template('about.html')

@app.route('/contact')
def contacts():
    return render_template('contacts.html')

@app.route('/favorites')
@login_required
def favorites():
    if 'favorites' not in session:
        session['favorites'] = []
    favorites_cakes = [Cake.query.get(cake_id) for cake_id in session['favorites']]
    return render_template('favorites.html', favorites=favorites_cakes)


@app.route('/cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    cart_item = {
        'cake_id': request.form['cake_id'],
        'quantity': request.form['quantity'],
        'name': request.form['name'],
        'phone': request.form['phone']
    }
    session['cart'].append(cart_item)
    session.modified = True  # Mark session as modified
    return redirect(url_for('home'))

<<<<<<< HEAD

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



=======
>>>>>>> 76fbd312a37a45b92489564b9f04f0e6dc496c46
@app.route('/view_cart')
def view_cart(cakes=None):
    if 'cart' not in session:
        session['cart'] = []
    cart_items = [cakes[int(item['cake_id']) - 1] for item in session['cart']]
    return render_template('cart.html', cart=cart_items)


<<<<<<< HEAD
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
                    flash("Your account was deleted!", "success")
                    session.clear()
                    return redirect(url_for('home'))
                except Exception as e:
                    flash(f"Error occurred: {str(e)}", "error")
                    db.session.rollback()
            else:
                flash("There is no such user!", "error")
        return redirect(url_for('home'))

    return render_template('delete_account.html')


@app.route('/aboutUs')
def about_us():
    return render_template('about.html')


@app.route('/contact')
def contacts():
    return render_template('contacts.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # предполагаем, что у вас используется SQLAlchemy


=======
>>>>>>> 76fbd312a37a45b92489564b9f04f0e6dc496c46
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
