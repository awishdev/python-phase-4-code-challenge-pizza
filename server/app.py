#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants], 200
    

class RestaurantById(Resource):

    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            # include restaurant pizzas
            return restaurant.to_dict(rules=("restaurant_pizzas",)), 200
        else:
            return {"error": "Restaurant not found"}, 404
    def delete(self, id):
        # delete restaurant if it exists
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {"message": "Restaurant deleted successfully"}, 204
        else:
            return {"error": "Restaurant not found"}, 404
        

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200
    

class RestaurantPizzas(Resource):
    def post(self):
        # validate request data
        data = request.get_json()

        restaurant = Restaurant.query.filter_by(id=data["restaurant_id"]).first()
        pizza = Pizza.query.filter_by(id=data["pizza_id"]).first()
        if not restaurant or not pizza:
            return {"errors": ["validation errors"]}, 400
        
        if data["price"] < 1 or data["price"] > 30:
            return {"errors": ["validation errors"]}, 400
        
        #make new RestaurantPizza
        
        new_restaurant_pizza = RestaurantPizza(
            restaurant_id=data["restaurant_id"],
            pizza_id=data["pizza_id"],
            price=data["price"]
        )
        # add to database
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        return new_restaurant_pizza.to_dict(), 201
    
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
