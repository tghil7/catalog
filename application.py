from flask import Flask, render_template, url_for, request ,flash, redirect, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, HouseItem, FurnitureItem, CarItem

engine = create_engine('postgresql:///catalogmenu')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories')
def goodCategories():
    categories = session.query(Category).distinct(Category.name).group_by(Category.name, Category.id)
    latestCars = session.query(CarItem).order_by((CarItem.id).desc()).limit(2)
    latestHouses = session.query(HouseItem).order_by((HouseItem.id).desc()).limit(2)
    latestFurnitures = session.query(FurnitureItem).order_by((FurnitureItem.id).desc()).limit(2)
    allCars = session.query(CarItem).all()
    allHouses = session.query(HouseItem).all()
    allFurnitures = session.query(FurnitureItem).all()
    return render_template("home.html", categories = categories, latestCars = latestCars, latestHouses = latestHouses, latestFurnitures = latestFurnitures, allCars =allCars, allHouses = allHouses, allFurnitures =allFurnitures)




@app.route('/categories/<int:category_id>/menu')
def goodCategoryItems(category_id):
    category = session.query(Category).filter_by(id= category_id).one()
    if category.name == "Cars":
        items = session.query(CarItem).all()
    elif category.name == "House":
        items = session.query(HouseItem).all()
    elif category.name == "Furniture":
        items = session.query(FurnitureItem).all()
    return render_template('categories.html', category_id = category_id, items = items, category = category)

@app.route('/categories/<int:category_id>/menu/JSON')
def goodCategoryItemsJSON(category_id):
    category = session.query(Category).filter_by(id= category_id).one()
    if category.name == "Cars":
        items = session.query(CarItem).all()
    elif category.name == "House":
        items = session.query(HouseItem).all()
    elif category.name == "Furniture":
        items = session.query(FurnitureItem).all()
    return jsonify (items =[i.serialize for i in items]) 


@app.route('/catalog/Car/<carItem_id>')
def carDetails(carItem_id):
    carDescriptions = session.query(CarItem).filter_by(id = carItem_id)
    return render_template ('carFile.html', carItem_id = carItem_id, carDescriptions = carDescriptions)

@app.route('/catalog/Car/new')
def addCarDetails():
    if request.method == 'POST':
		newCarItem = CarItem(make = request.form.get('make'), model = request.form.get('model'),
                year = request.form.get('year'), price = request.form.get('price'),
                color = request.form.get('color'), image = request.form.get('image'), category = Category(name="Cars"))
		session.add(newCarItem)
		session.commit()
		flash ("New car item created!")
		return redirect(url_for('goodCategories'))
    else:
		return render_template('newcaritem.html')

@app.route('/catalog/House/<houseItem_id>')
def houseDetails(houseItem_id):
    houseDescriptions = session.query(HouseItem).filter_by(id= houseItem_id)
    return render_template ('houseFile.html', houseItem_id = houseItem_id, houseDescriptions = houseDescriptions)

@app.route('/catalog/Furniture/<furnitureItem_id>')
def furnitureDetails(furnitureItem_id):
    furnitureDescriptions = session.query(FurnitureItem).filter_by(id= furnitureItem_id)
    return render_template ('furnitureFile.html', furnitureItem_id = furnitureItem_id, furnitureDescriptions = furnitureDescriptions)



@app.route('/categories/cars/<int:car_id>/options')
def carOptions(car_id):
    return "The car options are the following for " + str(car_id)






if __name__== '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
    
