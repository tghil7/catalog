from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import  Category, CarItem, FurnitureItem, HouseItem, Base

engine = create_engine('postgresql:///catalogmenu')
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


# Items for category Cars
category1 = Category(name="Cars")

session.add(category1)
session.commit()

carItem1 = CarItem(make ="Volvo", model="s40", year = 2004, price= 2000 , color ="yellow", image ="/img/carItem1", category= category1)

session.add(carItem1)
session.commit()


carItem2 = CarItem(make="Volkswagen", model="Passat",year = 2005, price= 1000, color="blue", image ="/img/carItem2", category= category1)

session.add(carItem2)
session.commit()

carItem3 = CarItem(make="Nissan", model="Altima",year = 2015, price= 12000 , color="brown", image ="/img/carItem2", category= category1)

session.add(carItem3)
session.commit()



# Items for category House
category2 = Category(name="House")

session.add(category2)
session.commit()


houseItem1 = HouseItem(style="modern", year= 1974,  price= 125000 , image="img/houseItem1", category=category2)

session.add(houseItem1)
session.commit()

houseItem2 = HouseItem(style="Ranch", year= 1960,  price= 150000, image="img/houseItem2", category=category2)

session.add(houseItem2)
session.commit()

houseItem3 = HouseItem(style="traditional", year= 1940,  price= 95000 , image="img/houseItem3", category=category2)

session.add(houseItem3)
session.commit()


# Menu for category Furnitures
category3 = Category(name="Furniture")

session.add(category3)
session.commit()


furnitureItem1 = FurnitureItem(style="persic", year= 1995, price= 500, image="img/furnitureItem1", category=category3)
session.add(furnitureItem1)
session.commit()

furnitureItem2 = FurnitureItem(style="modern", year= 2015, price= 200, image="img/furnitureItem1", category=category3)
session.add(furnitureItem2)
session.commit()

furnitureItem3 = FurnitureItem(style="futuristic", year= 2017,  price= 300, image="img/furnitureItem1", category=category3)
session.add(furnitureItem3)
session.commit()

