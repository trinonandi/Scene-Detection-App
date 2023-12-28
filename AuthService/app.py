import json

import firebase_admin
import requests
from flask import Flask, request, jsonify
from utils import validation_utils, firebase_utils
from firebase_admin import auth

app = Flask(__name__)

firebase_client = firebase_utils.get_firebase_client()

default_app = firebase_admin.initialize_app()


@app.route('/signup', methods=['POST'])
def signup():  # put application's code here
    body = request.get_json()
    email = body.get("email")
    password = body.get("password")
    display_name = "New User" if body.get("display_name") is None else body.get("display_name")

    if email is None or not validation_utils.is_valid_email(email):
        invalid_email_response = {
            "message": "Invalid Email ID",
            "code": 400
        }
        return jsonify(invalid_email_response), 400

    if password is None or not validation_utils.is_valid_password(password):
        invalid_password_response = {
            "message": "Invalid Password. Password should be: \n 1. At least 8 characters long. \n 2. Contains at "
                       "least one uppercase letter. \n 3. Contains at least one lowercase letter. \n 4. Contains at "
                       "least one digit. \n 5. Contains at least one special character from (! @ # $ % ^ & *).",
            "code": 400
        }
        return jsonify(invalid_password_response), 400

    try:
        user = firebase_client.auth().create_user_with_email_and_password(email, password)
        firebase_client.auth().update_profile(user["idToken"], display_name=display_name)
        firebase_client.auth().send_email_verification(user["idToken"])
        success_response = {
            "message": "User Successfully Created. Please Verify Email",
            "code": 200
        }
        return jsonify(success_response), 200

    except requests.exceptions.HTTPError as e:
        return json.loads(e.strerror), 400


@app.route('/signin', methods=['POST'])
def signin():
    body = request.get_json()
    email = body.get("email")
    password = body.get("password")

    try:
        user = firebase_client.auth.sign_in_with_email_and_password(email, password)
        account_info = firebase_client.auth.get_account_info(user["idToken"])
        email_verified = account_info["users"][0]["emailVerified"]

        if not email_verified:
            verify_email_response = {
                "message": "Email is not verified. A new verification link is sent to the registered email",
                "code": 401
            }
            firebase_client.auth.send_email_verification(user["idToken"])
            return jsonify(verify_email_response), 401

        return user, 200

    except requests.exceptions.HTTPError as e:
        return json.loads(e.strerror), 401


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    body = request.get_json()
    email = body.get("email")
    if email is None or not validation_utils.is_valid_email(email):
        invalid_email_response = {
            "message": "Invalid Email ID",
            "code": 400
        }
        return jsonify(invalid_email_response), 400

    try:
        firebase_client.auth.send_password_reset_email(email)
        forgot_password_email_response = {
            "message": "Password reset link has been sent to the email provided",
            "code": 200
        }
        return jsonify(forgot_password_email_response), 200

    except requests.exceptions.HTTPError as e:
        return json.loads(e.strerror), 400


# By default user id token remains valid for 1 hr. Refresh will generate a new id token with 1 hr validity
def refresh_user_id_token(refresh_token):
    return firebase_client.auth.refresh(refresh_token)


if __name__ == '__main__':
    app.run()
