#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

class Home(Resource):
    def get(self):
        return 'Welcome to the Cosmic Travel Agency API'


class AllScientists(Resource):
    def get(self):
        response = []
        for scientist in Scientist.query.all():
            response.append(scientist.to_dict(rules=('-missions',)))
        return make_response(response, 200)

    def post(self):
        req_data = request.get_json()
        try:
            new_sci = Scientist(name  = req_data.get('name'),
                                field_of_study = req_data.get('field_of_study')
                                )
        except Exception as error:
            # return make_response({'errors': error.args}, 400)
            return make_response({'errors': ['validation errors']}, 400)
        db.session.add(new_sci)
        db.session.commit()
        return  make_response(new_sci.to_dict(), 201)


class ScientistById(Resource):
    def get(self, id):
        sci = Scientist.query.filter(Scientist.id == id).first()
        if sci:
            return make_response(sci.to_dict(), 200)
        else:
            return make_response({"error": "Scientist not found"}, 404)

    def patch(self, id):
        req_data = request.get_json()
        sci = Scientist.query.filter(Scientist.id == id).first()
        if sci:
            try:
                for key, value in req_data.items():
                    setattr(sci, key, value) 
            except Exception as error:
                return make_response({'errors': ['validation errors']}, 400)
                # return make_response({'errors': error.args}, 400)
            db.session.add(sci)
            db.session.commit()
            return make_response(sci.to_dict(), 202)
        else:
            return make_response({"error": "Scientist not found"}, 404)

    def delete(self, id):
        sci = Scientist.query.filter(Scientist.id == id).first()
        if sci:
            db.session.delete(sci)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({"error": "Scientist not found"}, 404)

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]
        if len(planets):
            return make_response(planets, 200)
        else:
            return make_response({"error": "There are somehow no plannets?"}, 404)

class Missions(Resource):
    def post(self):
        req_data = request.get_json()
        try:
            new_mission = Mission(name = req_data.get('name'),
                                scientist_id = req_data.get('scientist_id'),
                                planet_id = req_data.get('planet_id'))
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except Exception as error:
                # return make_response({'errors': error.args}, 400)
                return make_response({'errors': ['validation errors']}, 400)

api.add_resource(Home, '/')
api.add_resource(AllScientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
