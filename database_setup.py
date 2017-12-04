import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class CarItem (Base):
    __tablename__ = 'car_item'
    make = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    model = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String(80), nullable=True)
    price = Column(Integer, nullable=False)
    image = Column(String(250), nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'make': self.make,
            'model': self.model,
            'id': self.id,
            'price': self.price,

        }


class HouseItem(Base):
    __tablename__ = 'house_item'
    id = Column(Integer, primary_key=True)
    style = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String(250), nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'year': self.year,
            'id': self.id,
            'price': self.price,

        }


class FurnitureItem(Base):
    __tablename__ = 'furniture_item'
    id = Column(Integer, primary_key=True)
    style = Column(String(80), nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String(250), nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'year': self.year,
            'id': self.id,
            'price': self.price,

        }


engine = create_engine('postgresql:///catalogmenuwithusers')
Base.metadata.create_all(engine)
