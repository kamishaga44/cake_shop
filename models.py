from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from flask_login import UserMixin

Base = declarative_base()

class User(UserMixin):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    user_fname = Column(String(255))
    user_sname = Column(String(255))

    orders = relationship("Order", back_populates="user")

class Cake(Base):
    __tablename__ = 'cakes'

    cake_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    info = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    image = Column(String(255))

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    cake_id = Column(Integer, ForeignKey('cakes.cake_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=False)

    user = relationship("User", back_populates="orders")
    cake = relationship("Cake")

class Log(Base):
    __tablename__ = 'logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    action_type = Column(String(50), nullable=False)
    entity = Column(String(50), nullable=False)
    entity_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)


    user = relationship("User")
