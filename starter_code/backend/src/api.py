import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
Uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint:
    - returns json where 'drinks' is the list of drinks.
'''


@app.route('/drinks')
def read_drink():
    selection = Drink.query.all()

    if len(selection) == 0:
        abort(404)

    drinks = [drink.short() for drink in selection]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint:
    - returns json where 'drinks' is the list of drinks.
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def read_drink_detail(token):
    selection = Drink.query.all()

    if len(selection) == 0:
        abort(404)

    drinks = [drink.long() for drink in selection]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    # Handles post requests for adding a new drink to the database.
    body = request.get_json()

    if body is None:
        abort(400)

    try:
        drink = drink(title=body.get('title'), recipe=body.get('recipe'))
        drink.insert()

        return jsonify({
            "success": True,
            "drink": drink.long()
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id, token):
    # Handles patch requests for updating a drink's details.
    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()

    if body is None:
        abort(400)

    try:
        drink.title = body.get('title')
        drink.recipe = body.get('recipe')
        drink.update()

        return jsonify({
            "success": True,
            "drink": drink.long()
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id, token):
    # Handles delete requests for deleting a drink by ID.
    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink_id
        })
    except Exception:
        abort(422)

# Error Handling


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "Bad request."
                    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "Unauthorized."
                    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "Forbidden."
                    }), 403


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Resource not found."
                    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "Unprocessable entity."
                    }), 422


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error
                    }), error.status_code
