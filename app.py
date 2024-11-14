from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost/shop_db'
app.config['SECRET_KEY'] = "my secret key here"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Папка для хранения фотографий
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    user_fname = db.Column(db.String(80), nullable=False)
    user_sname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)  # Новое поле для фото


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

@app.route('/account')
@login_required
def account():
    user_data = {
        'login': current_user.login,
        'user_fname': current_user.user_fname,
        'user_sname': current_user.user_sname,
        'profile_picture': current_user.profile_picture
    }
    return render_template('account.html', context=user_data)
@app.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('account'))

    file = request.files['profile_picture']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('account'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)


        current_user.profile_picture = filename
        db.session.commit()

        flash("Profile picture uploaded successfully!", "success")
        return redirect(url_for('account'))
    else:
        flash("Allowed file types are png, jpg, jpeg, gif", "error")
        return redirect(url_for('account'))



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
            flash("A user with this username already exists!", "error")
        elif pass1 != pass2:
            flash("Passwords do not match!", "error")
        else:
            try:
                new_user = User(login=login, user_fname=fname, user_sname=sname, password=pass1)
                db.session.add(new_user)
                db.session.commit()
                flash("You have successfully registered!", "success")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"An error occurred during registration: {str(e)}", "error")
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

@app.route('/cart')
def view_cart():
    # Логика для отображения корзины
    return render_template('cart.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out!", "success")
    return redirect(url_for('home'))
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

@app.route('/cart', methods=['POST'])
@login_required
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    price = request.form['price']

    cart_item = {
        'cake_id': request.form['cake_id'],
        'quantity': request.form['quantity'],
        'name': request.form['name'],
        'phone': request.form['phone'],
        'price': price
    }
    session['cart'].append(cart_item)
    session.modified = True
    return redirect(url_for('home'))




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

@app.route('/get_user_info', methods=['GET'])
@login_required
def get_user_info():
    try:
        user_id = current_user.user_id

        user = User.query.get(user_id)
        if user:
            first_name = f"{user.user_fname}"
            second_name = f"{user.user_sname}"
            return jsonify({"name": first_name, "surname": second_name})
        else:
            return jsonify({"name": "", "surname": ""}), 404
    except Exception as e:
        print(f"Error retrieving user info: {e}")
        return jsonify({"name": ""}), 500


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


@app.route('/billing')
def billing():
    cart = session.get('cart', [])
    total = sum(item['quantity'] * float(item['price']) for item in cart)
    return render_template('billing.html', cart=cart, total=total)


@app.route('/process-payment', methods=['POST'])
def process_payment():
    payment_method = request.form['payment-method']

    if payment_method == 'card':
        card_number = request.form['card-number']
        card_name = request.form['card-name']
        expiry_date = request.form['expiry-date']
        cvv = request.form['cvv']
        # Process card payment logic here (e.g., integrate with a payment gateway)
        return redirect(url_for('payment_success'))

    elif payment_method == 'cash':
        # Process cash payment logic here
        return redirect(url_for('payment_success'))


@app.route('/payment-success')
def payment_success():
    return "Your payment has been successfully processed!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
