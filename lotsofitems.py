from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import  Category, CarItem, FurnitureItem, HouseItem, Base, User

engine = create_engine('postgresql:///catalogmenuwithusers')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Jim Jones", email="lightonserge@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Items for category Cars
category1 = Category(user_id=1,name="Cars")

session.add(category1)
session.commit()

carItem1 = CarItem(user_id = 1, make ="Volvo", model="s40", year = 2004, price= 2000 , color ="yellow", image ="carItem1", category= category1)

session.add(carItem1)
session.commit()


carItem2 = CarItem(user_id = 1, make="Volkswagen", model="Passat",year = 2005, price= 1000, color="blue", image ="carItem2", category= category1)

session.add(carItem2)
session.commit()

carItem3 = CarItem(user_id = 1, make="Nissan", model="Altima",year = 2015, price= 12000 , color="brown", image ="carItem3", category= category1)

session.add(carItem3)
session.commit()


#Items for category House
category2 = Category(user_id=1, name="House")

session.add(category2)
session.commit()


houseItem1 = HouseItem(user_id = 1,style="modern", year= 1974,  price= 125000 , image="houseItem1", category=category2)

session.add(houseItem1)
session.commit()

houseItem2 = HouseItem(user_id=1,style="Ranch", year= 1960,  price= 150000, image="houseItem2", category=category2)

session.add(houseItem2)
session.commit()

houseItem3 = HouseItem(user_id=1,style="traditional", year= 1940,  price= 95000 , image="houseItem3", category=category2)

session.add(houseItem3)
session.commit()


# Menu for category Furnitures
category3 = Category(user_id=1,name="Furniture")

session.add(category3)
session.commit()


furnitureItem1 = FurnitureItem(user_id=1,style="persic", year= 1995, price= 500, image="furnitureItem1", category=category3)
session.add(furnitureItem1)
session.commit()

furnitureItem2 = FurnitureItem(user_id=1,style="modern", year= 2015, price= 200, image="furnitureItem2", category=category3)
session.add(furnitureItem2)
session.commit()

furnitureItem3 = FurnitureItem(user_id=1,style="futuristic", year= 2017,  price= 300, image="furnitureItem3", category=category3)
session.add(furnitureItem3)
session.commit()

