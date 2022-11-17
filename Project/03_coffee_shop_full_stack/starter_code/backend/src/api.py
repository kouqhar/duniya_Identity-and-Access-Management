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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods=["GET"])
def get_drinks():
    try:
        all_drinks = Drink.query.all()
        drinks= [drink.short() for drink in all_drinks]

        if len(all_drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks
        }) , 200
        
    except BaseException:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks-detail", methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(playload):

    try : 
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
        drinks_length = len(all_drinks)
        
        if drinks_length == 0:
            abort(404)
            
        return jsonify({
            'success': True,
            'drinks': drinks
        }) , 200

    except BaseException:
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):

    data = request.get_json()
    drink_title = data.get('title', None)
    get_recipe = data.get('recipe', None)
    recipe = json.dumps(get_recipe)

    try:
        add_drink = Drink(title = drink_title, recipe = recipe)
        add_drink.insert()
        add_drink.long()

        all_drinks = Drink.query.all()
        drinks = [drink.short() for drink in all_drinks]

        return jsonify({
            "success": True,
            "drinks": drinks
    })

    except BaseException:
        abort(422)



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(playload, id):

    data = request.get_json()
    filtered_drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    if filtered_drink is None:
        abort(404)

    try: 
        updated_title = data.get('title', None)
        updated_recipe = data.get('recipe', None)
        update_recipe = json.dumps(updated_recipe)

        if updated_title:
            filtered_drink.title = updated_title
        if updated_recipe:
            filtered_drink.recipe = update_recipe
        
        filtered_drink.update()
        updated_drink = [filtered_drink.long()]

        return jsonify({
                'success': True,
                'drinks': updated_drink
            }), 200


    except BaseException:
        abort(422)
           


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):

    filtered_drink = Drink.query.filter(Drink.id == id).one_or_none()

    if filtered_drink is None:
        abort(404)

    try:
        filtered_drink.delete()

        return jsonify({
            'sucess': True,
            'id': id,
        }), 200

    except BaseException:
     abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }), 401

@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Forbidden'
    }), 403


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code
