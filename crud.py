from sqlalchemy.orm import Session
import models
from datetime import datetime
from werkzeug.security import generate_password_hash


def log_action(db: Session, user_id: int, action_type: str, entity: str, entity_id: int, details: str = None):
    """Logs the CRUD action performed by a user."""
    log_entry = models.Log(
        user_id=user_id,
        action_type=action_type,
        entity=entity,
        entity_id=entity_id,
        timestamp=datetime.now(),
        details=details
    )
    db.add(log_entry)
    db.commit()


def create_user(db: Session, login: str, password: str, user_fname: str, user_sname: str):
    hashed_password = generate_password_hash(password)
    new_user = models.User(login=login, password=hashed_password, user_fname=user_fname, user_sname=user_sname)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_action(db, new_user.user_id, "CREATE", "user", new_user.user_id, f"User {login} created.")
    return new_user


def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter_by(login=login).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter_by(user_id=user_id).first()


def update_user(db: Session, user_id: int, new_fname: str, new_sname: str):
    user = db.query(models.User).filter_by(user_id=user_id).first()
    if user:
        user.user_fname = new_fname
        user.user_sname = new_sname
        db.commit()
        db.refresh(user)
        log_action(db, user_id, "UPDATE", "user", user_id, f"User {user.login} updated.")
        return user
    return None


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter_by(user_id=user_id).first()
    if user:
        db.delete(user)
        db.commit()
        log_action(db, user_id, "DELETE", "user", user_id, f"User {user.login} deleted.")
        return True
    return False


# CRUD operations for orders

def create_order(db: Session, user_id: int, cake_id: int, quantity: int, phone: str):
    new_order = models.Order(user_id=user_id, cake_id=cake_id, quantity=quantity, phone=phone)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    log_action(db, user_id, "CREATE", "order", new_order.order_id, f"Order for Cake {cake_id} created.")
    return new_order


def get_orders_by_user(db: Session, user_id: int):
    return db.query(models.Order).filter_by(user_id=user_id).all()


def get_order_by_id(db: Session, order_id: int):
    return db.query(models.Order).filter_by(order_id=order_id).first()


def update_order(db: Session, order_id: int, new_quantity: int):
    order = db.query(models.Order).filter_by(order_id=order_id).first()
    if order:
        order.quantity = new_quantity
        db.commit()
        db.refresh(order)
        log_action(db, order.user_id, "UPDATE", "order", order_id, f"Order {order_id} updated.")
        return order
    return None


def delete_order(db: Session, order_id: int):
    order = db.query(models.Order).filter_by(order_id=order_id).first()
    if order:
        db.delete(order)
        db.commit()
        log_action(db, order.user_id, "DELETE", "order", order_id, f"Order {order_id} deleted.")
        return True
    return False


# CRUD operations for cakes

def create_cake(db: Session, name: str, info: str, price: float, image: str):
    new_cake = models.Cake(name=name, info=info, price=price, image=image)
    db.add(new_cake)
    db.commit()
    db.refresh(new_cake)
    return new_cake


def get_all_cakes(db: Session):
    return db.query(models.Cake).all()


def get_cake_by_id(db: Session, cake_id: int):
    return db.query(models.Cake).filter_by(cake_id=cake_id).first()


def update_cake(db: Session, cake_id: int, new_name: str, new_info: str, new_price: float, new_image: str):
    cake = db.query(models.Cake).filter_by(cake_id=cake_id).first()
    if cake:
        cake.name = new_name
        cake.info = new_info
        cake.price = new_price
        cake.image = new_image
        db.commit()
        db.refresh(cake)
        return cake
    return None


def delete_cake(db: Session, cake_id: int):
    cake = db.query(models.Cake).filter_by(cake_id=cake_id).first()
    if cake:
        db.delete(cake)
        db.commit()
        return True
    return False


