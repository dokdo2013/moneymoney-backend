from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import json
import dotenv
import os
import onetimepass as otp
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib import parse


app = Flask(__name__)
cors = CORS(app)


@app.route("/money", methods=['GET'])
def get_sheet_data():
    return jsonify(message='API Not Ready')


@app.route("/money", methods=['POST'])
def add_to_sheets():
    # Load Dotenv
    try:
        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file, verbose=True)
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
        item_detail = req_data['itemDetail']
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
    
    # Connect to Google Sheets API
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]
        json_file_name = os.getenv('CRED_FILE_NAME')
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
        gc = gspread.authorize(credentials)

        spreadsheet_key = os.getenv('DOCUMENT_ID')
        doc = gc.open_by_key(spreadsheet_key)
        worksheet = doc.worksheet(parse.unquote(os.getenv('SHEET_NAME')))
    except Exception as e:
        print(e)
        data = {
            'code': 400,
            'message': 'Unable to connect Google Sheets API'
        }
        return make_response(json.dumps(data), 400)

    # Get new row number (Binary Search)
    MAX_SEARCH_LENGTH = int(os.getenv('MAX_SEARCH_LENGTH'))
    target_row = -1
    cnt = 0
    bin_start = 0
    bin_end = MAX_SEARCH_LENGTH
    while cnt < 30:  # Prevent Infinite Loop
        cnt = cnt + 1
        cursor = int((bin_start + bin_end) / 2)
        col_data = worksheet.cell(cursor, 2).value
        if col_data is None:
            bin_end = cursor
        else:
            bin_start = cursor
        if bin_start + 1 == bin_end:
            target_row = cursor + 1
            break

    if cnt == 30:
        data = {
            'code': 400,
            'message': 'Failed to find appropriate cell to write in Spreadsheet'
        }
        return make_response(json.dumps(data), 400)

    # Update row
    if target_row == -1:
        data = {
            'code': 400,
            'message': 'Unable to update row'
        }
        return make_response(json.dumps(data), 400)
        
    worksheet.update_cell(target_row, 2, date)
    worksheet.update_cell(target_row, 4, category)
    worksheet.update_cell(target_row, 5, item)
    worksheet.update_cell(target_row, 6, item_detail)
    worksheet.update_cell(target_row, 7, pay_method)
    worksheet.update_cell(target_row, 8, price)
    worksheet.update_cell(target_row, 9, etc)
    
    data = {
        'code': 200,
        'message': 'Success'
    }
    return make_response(json.dumps(data), 200)


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
