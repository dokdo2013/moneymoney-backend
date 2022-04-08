from flask import Flask, jsonify, request, make_response
import json
import dotenv
import os
import onetimepass as otp


app = Flask(__name__)


@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/money", methods=['GET'])
def get_sheet_data():
    return jsonify(message='API Not Ready')


@app.route("/money", methods=['POST'])
def add_to_sheets():
    # Load Dotenv
    try:
        dotenv.load_dotenv(verbose=True)
    except Exception as e:
        print(e)
        data = {
            'code': 400,
            'message': 'Cannot load environment variable'
        }
        return make_response(json.dumps(data), 400)

    # Load Request Data
    try:
        req_data = request.get_json()
        date = req_data['date']
        code = req_data['otpCode']
        category = req_data['category']
        pay_method = req_data['payMethod']
        item = req_data['item']
        item_detail = req_data['item_detail']
        price = req_data['price']
        etc = req_data['etc']
    except Exception as e:
        print(e)
        data = {
            'code': 422,
            'message': 'Unprocessable Entity'
        }
        return make_response(json.dumps(data), 422)

    # Data Validation
    if date == '' or code == '' or category == '' or pay_method == '' or item == '' or price == '':
        data = {
            'code': 422,
            'message': 'Unprocessable Entity'
        }
        return make_response(json.dumps(data), 422)
    
    # OTP Validation
    secret_key = os.getenv('SECRET_KEY')
    if not otp.valid_totp(code, secret_key):
        data = {
            'code': 401,
            'message': 'Unauthorized'
        }
        return make_response(json.dumps(data), 401)
    
    # Add to Sheets
    
    
    
    data = {
        'code': 200,
        'message': 'Success'
    }
    return make_response(json.dumps(data), 200)


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
