import random
import string
import httplib2
import json
import requests
from flask import Flask, render_template
from flask import url_for, request
from flask import flash, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category
from database_setup import HouseItem, FurnitureItem, CarItem, User

# IMPORTS FOR ANTI FORGERY STATE TOKEN
from flask import session as login_session
# IMPORTS OAUTH
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('postgresql:///catalogmenuwithusers')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(
            json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user'
                                            'is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;"'
    '"-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ''
    url += 'https://accounts.google.com/'
    url += 'o/oauth2/revoke?'
    url += 'token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/clearSession')
def clearSession():
    login_session.clear()
    return "Session cleared"


@app.route('/')
@app.route('/catalog')
def goodCategories():
    categories = session.query(Category).distinct(
        Category.name).group_by(Category.name, Category.id)
    latestCars = session.query(CarItem).order_by((CarItem.id).desc()).limit(2)
    latestHouses = session.query(HouseItem).order_by(
        (HouseItem.id).desc()).limit(2)
    latestFurnitures = session.query(FurnitureItem).order_by(
        (FurnitureItem.id).desc()).limit(2)
    allCars = session.query(CarItem).all()
    allHouses = session.query(HouseItem).all()
    allFurnitures = session.query(FurnitureItem).all()
    if 'username' not in login_session:
        return render_template("home.html", categories=categories,
                               latestCars=latestCars,
                               latestHouses=latestHouses,
                               latestFurnitures=latestFurnitures,
                               allCars=allCars, allHouses=allHouses,
                               allFurnitures=allFurnitures)
    else:
        return render_template("homeLoggedIn.html",
                               categories=categories,
                               latestCars=latestCars,
                               latestHouses=latestHouses,
                               latestFurnitures=latestFurnitures,
                               allCars=allCars, allHouses=allHouses,
                               allFurnitures=allFurnitures)


@app.route('/catalog/<category_name>/menu')
def goodCategoryItems(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    if category.name == "Cars":
        items = session.query(CarItem).all()
    elif category.name == "House":
        items = session.query(HouseItem).all()
    elif category.name == "Furniture":
        items = session.query(FurnitureItem).all()
    return render_template('categories.html',
                           category_name=category_name,
                           items=items, category=category)


@app.route('/catalog/selectCategory')
def selectCategory():
    if 'username' not in login_session:
        return redirect('/login')
    else:
        return render_template('categoryChoice.html')


@app.route('/catalog/<category_name>/menu/JSON')
def goodCategoryItemsJSON(category_name):
    category = session.query(Category).filter_by(
        name=category_name).one()
    if category.name == "Cars":
        items = session.query(CarItem).all()
    elif category.name == "House":
        items = session.query(HouseItem).all()
    elif category.name == "Furniture":
        items = session.query(FurnitureItem).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/car/<carItem_make>')
def carDetails(carItem_make):
    myCar = session.query(CarItem).filter_by(
        make=carItem_make).one()
    carUserID = myCar.user_id
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != carUserID:
        return render_template('carFile.html',
                               carItem_make=carItem_make, myCar=myCar)
    else:
        return render_template('myCarFile.html',
                               carItem_make=carItem_make, myCar=myCar)


@app.route('/catalog/car/new', methods=['GET', 'POST'])
def addCarDetails():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name="Cars").one()
        newCarItem = CarItem(make=request.form.get('make'),
                             model=request.form.get('model'),
                             year=request.form.get('year'),
                             price=request.form.get('price'),
                             color=request.form.get('color'),
                             image=request.form.get('image'),
                             category_id=category.id,
                             user_id=login_session['user_id'])
        session.add(newCarItem)
        session.commit()
        flash("New car item created!")
        return redirect(url_for('goodCategories'))
    else:
        return render_template('newCarItem.html')


@app.route('/catalog/car/<carItem_make>/delete',
           methods=['GET', 'POST'])
def deleteCarDetails(carItem_make):
    if 'username' not in login_session:
        return redirect('/login')
    carToDelete = session.query(CarItem).filter_by(
        make=carItem_make).one()
    deleteUserID = carToDelete.user_id
    if login_session['user_id'] != deleteUserID:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to delete this car item."
                "Please create your own car item"
                "in order to delete.');}</script><body onload='myFunction()'>")

    if request.method == 'POST':
        session.delete(carToDelete)
        flash('%s Successfully Deleted' % carToDelete.make)
        session.commit()
        return redirect(url_for('goodCategories'))
    else:
        return render_template('carDelete.html', carItem=carToDelete)


@app.route('/catalog/car/<carItem_make>/edit',
           methods=['GET', 'POST'])
def updateCarDetails(carItem_make):
    if 'username' not in login_session:
        return redirect('/login')
    carToUpdate = session.query(CarItem).filter_by(make=carItem_make).one()
    category = session.query(Category).filter_by(name="Cars").one()
    editUserID = carToUpdate.user_id
    if login_session['user_id'] != editUserID:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this car item. Please create your own"
                "car item in order"
                "to delete.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form.get('make'):
            carToUpdate.make = request.form.get('make')
        if request.form.get('model'):
            carToUpdate.model = request.form.get('model')
        if request.form.get('year'):
            carToUpdate.year = request.form.get('year')
        if request.form.get('price'):
            carToUpdate.price = request.form.get('price')
        if request.form.get('color'):
            carToUpdate.color = request.form.get('color')
        if request.form.get('image'):
            carToUpdate.image = request.form.get('image')
        session.add(carToUpdate)
        flash('%s Successfully updated' % carToUpdate.make)
        session.commit()
        return redirect(url_for('goodCategories'))
    else:
        return render_template('editCar.html',
                               carItem=carToUpdate)


@app.route('/catalog/house/<houseItem_style>')
def houseDetails(houseItem_style):
    myHouse = session.query(HouseItem).filter_by(
        style=houseItem_style).one()
    houseUserID = myHouse.user_id
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != houseUserID:
        return render_template('houseFile.html',
                               houseItem_style=houseItem_style,
                               myHouse=myHouse)
    else:
        return render_template('myHouseFile.html',
                               houseItem_style=houseItem_style,
                               myHouse=myHouse)


@app.route('/catalog/house/new',
           methods=['GET', 'POST'])
def addHouseDetails():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name="House").one()
        newHouseItem = HouseItem(style=request.form.get('style'),
                                 year=request.form.get('year'),
                                 price=request.form.get('price'),
                                 image=request.form.get('image'),
                                 category_id=category.id,
                                 user_id=login_session['user_id'])
        session.add(newHouseItem)
        session.commit()
        flash("New House item created!")
        return redirect(url_for('goodCategories'))
    else:
        return render_template('newHouseItem.html')


@app.route('/catalog/house/<houseItem_style>/edit',
           methods=['GET', 'POST'])
def updateHouseDetails(houseItem_style):
    if 'username' not in login_session:
        return redirect('/login')
    houseToUpdate = session.query(HouseItem).filter_by(
        style=houseItem_style).one()
    category = session.query(Category).filter_by(name="House").one()
    editUserID = houseToUpdate.user_id
    if login_session['user_id'] != editUserID:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this item. Please create your own house item"
                "in order to delete.')"
                ";}</script>"
                "<body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form.get('style'):
            houseToUpdate.style = request.form.get('style')
        if request.form.get('year'):
            houseToUpdate.year = request.form.get('year')
        if request.form.get('price'):
            houseToUpdate.price = request.form.get('price')
        if request.form.get('image'):
            houseToUpdate.image = request.form.get('image')
        session.add(houseToUpdate)
        flash('%s Successfully updated' % houseToUpdate.style)
        session.commit()
        return redirect(url_for('goodCategories'))
    else:
        return render_template('editHouse.html',
                               houseItem=houseToUpdate)


@app.route('/catalog/house/<houseItem_style>/delete',
           methods=['GET', 'POST'])
def deleteHouseDetails(houseItem_style):
    if 'username' not in login_session:
        return redirect('/login')
    houseToDelete = session.query(
        HouseItem).filter_by(
        style=houseItem_style).one()
    deleteUserID = houseToDelete.user_id
    if login_session['user_id'] != deleteUserID:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to delete this item.Please create your own"
                "house item in order to delete.');}"
                "</script><body onload='myFunction()'>")

    if request.method == 'POST':
        session.delete(houseToDelete)
        flash('%s Successfully Deleted' % houseToDelete.style)
        session.commit()
        return redirect(url_for('goodCategories'))
    else:
        return render_template('houseDelete.html',
                               houseItem=houseToDelete)


@app.route('/catalog/furniture/<furnitureItem_style>')
def furnitureDetails(furnitureItem_style):
    myFurniture = session.query(FurnitureItem).filter_by(
        style=furnitureItem_style).one()
    furnitureUserID = myFurniture.user_id
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != furnitureUserID:
        return render_template('furnitureFile.html',
                               furnitureItem_style=furnitureItem_style,
                               myFurniture=myFurniture)
    else:
        return render_template('myFurnitureFile.html',
                               furnitureItem_style=furnitureItem_style,
                               myFurniture=myFurniture)


@app.route('/catalog/furniture/new',
           methods=['GET', 'POST'])
def addFurnitureDetails():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(name="Furniture").one()
        newFurnitureItem = FurnitureItem(style=request.form.get('style'),
                                         year=request.form.get('year'),
                                         price=request.form.get('price'),
                                         image=request.form.get('image'),
                                         category_id=category.id,
                                         user_id=login_session['user_id'])
        session.add(newFurnitureItem)
        session.commit()
        flash("New furniture item created!")
        return redirect(url_for('goodCategories'))
    else:
        return render_template('newFurnitureItem.html')


@app.route('/catalog/furniture/<furnitureItem_style>/edit',
           methods=['GET', 'POST'])
def updateFurnitureDetails(furnitureItem_style):
    if 'username' not in login_session:
        return redirect('/login')
    furnitureToUpdate = session.query(FurnitureItem).filter_by(
        style=furnitureItem_style).one()
    category = session.query(Category).filter_by(name="Furniture").one()
    editUserID = furnitureToUpdate.user_id
    if login_session['user_id'] != editUserID:
        return ("<script>function myFunction() {alert('You are not authorized "
                "to edit this furniture item."
                "Please create your own furniture item in order "
                "to delete.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form.get('style'):
            furnitureToUpdate.style = request.form.get('style')
        if request.form.get('year'):
            furnitureToUpdate.year = request.form.get('year')
        if request.form.get('price'):
            furnitureToUpdate.price = request.form.get('price')
        if request.form.get('image'):
            furnitureToUpdate.image = request.form.get('image')
        session.add(furnitureToUpdate)
        flash('%s Successfully updated' % furnitureToUpdate.style)
        session.commit()
        return redirect(url_for('goodCategories'))
    else:
        return render_template('editFurniture.html',
                               furnitureItem=furnitureToUpdate)


@app.route('/catalog/furniture/<furnitureItem_style>/delete',
           methods=['GET', 'POST'])
def deleteFurnitureDetails(furnitureItem_style):
    if 'username' not in login_session:
        return redirect('/login')
    furnitureToDelete = session.query(FurnitureItem).filter_by(
        style=furnitureItem_style).one()
    deleteUserID = furnitureToDelete.user_id
    if login_session['user_id'] != deleteUserID:
        return ("<script>function myFunction()"
                "{alert('You are not authorized to "
                "delete this furniture item."
                "Please create your own furniture item"
                "in order to delete.');}</script><body onload='myFunction()'>")

    if request.method == 'POST':
        session.delete(furnitureToDelete)
        flash('%s Successfully Deleted' % furnitureToDelete.style)
        session.commit()
        return redirect(url_for('goodCategories'))
    else:
        return render_template('furnitureDelete.html',
                               furnitureItem=furnitureToDelete)


@app.route('/catalog/about')
def goAbout():
    if 'username' not in login_session:
        return render_template('about.html')
    else:
        return render_template('aboutLoggedIn.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
