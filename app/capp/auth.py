
#################### IMPORTS ####################


from cmath import log
import functools
import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import (
    check_password_hash, generate_password_hash
)
from capp.actions import (
    createAccount, loginAccount, sendVcode, updateUserPassword, existEmail
)
from capp import email
from flask_mail import Message



#################### BLUEPRINTS ( AUTH ) ####################

auth = Blueprint('auth', __name__, url_prefix='/auth')



######################## AUTH ROUTES ########################


##### /signup #####
@auth.route('/signup', methods=('GET', 'POST'))
def signup():
    """
        -> sign up user 
        -> store user info to the database
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        dob = request.form["dob"]
        gender = request.form["gender"]

        # create user's account
        creationStatus = createAccount(username, email, password, dob, gender)

        # flash error message if there is an error
        if not creationStatus:

            flash('Failed to create account!', 'e-message')

            return redirect(url_for("auth.signup")) # redirect to signup page

        # flash sucess message
        flash('Account created successfully', 's-message')
        
        return redirect("/auth/login") # redirect to log-in page

    return render_template('auth/signup.html')



##### /login #####
@auth.route('/login', methods=('GET', 'POST'))
def login():
    """
        -> log in existing user 
        -> store user's session using the user's id
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # log in user
        loginStatus = loginAccount(email, password)

        # flash error message if there is an error
        if not loginStatus:

            flash('Failed to logged in!', "e-message")

            return redirect(url_for("auth.login")) # redirect to log-in page

        return redirect("/auth/loginVerify") # redirect to verification page

    return render_template("auth/login.html")



##### /loginVerify #####
@auth.route("/loginVerify", methods=('GET', 'POST'))
def loginVerify():
    """
        -> send verification code to user's email
        -> user put in the code
        -> take user to homepage if successful, else back to login page
    """

    if (request.method == "POST"):

        entered_code = request.form["vcode"] # user's input

        actual_code = session["vcode"]

        # if entered code matches, redirect to homepage
        if str(entered_code) == str(actual_code):

            return redirect("/") # homepage

        else:

            flash("Verification code do not match!", "e-message")
            return redirect(url_for("auth.loginVerify")) # 2fa page


    # generate verification to send it to user's email
    success = sendVcode("Verification Code for 2FA - CAPP", session['user']["email"])

    # display error message if something went wrong, else sucess message
    if not success:

        flash("Something went wrong!", "e-message")

    else:

        flash("Verification code sent!", "s-message")

    return render_template("auth/2fa.html")



##### /rp/sc #####
@auth.route("/rp/sc", methods=('GET', 'POST'))
def resetPassword1():


    if (request.method == "POST"):

        user_email = request.form["email"]

        # generate verification to send it to user's email
        success = sendVcode("Verification Code for Password Reset - CAPP", user_email)

        # check if email exists
        isEmail = existEmail(user_email)

        # check if email exists and if code was sent to user
        if not sendVcode or not isEmail:

            flash("Something went wrong!", "e-message") 
            return redirect(url_for('auth.resetPassword1'))

        else:

            flash("Verification code sent!", "s-message")

        # store user's email for password reset purpose
        # *need this*
        session["rp-email"] = user_email

        return redirect("/auth/rp/confirm") 

    else:

        return render_template("auth/password-reset1.html")


##### /rp/confirm #####
@auth.route("/rp/confirm", methods=('GET', 'POST'))
def resetPassword2():

    """
        -> send verification code to user's email
        -> user put in the code
        -> user enter new password as well
        -> take user to homepage if successful, else back to login page
    """

    if (request.method == "POST"):

        # user's inputs
        entered_code = request.form["code"] 
        entered_np = request.form["password"] 

        actual_code = session['vcode']

        # if entered code matches, redirect to homepage
        if str(entered_code) == str(actual_code):

            updateStatus = updateUserPassword(session["rp-email"], entered_np)

            if not updateStatus:

                flash("Password reset failed!", "e-message")
                return redirect(url_for("auth.resetPassword2"))

            else:

                flash("Password was successfully reset!", "s-message")

        return redirect("/auth/login")


    return render_template("auth/password-reset2.html")



##### /logout #####
@auth.route('/logout')
def logout():
    """
        -> logout user 
        -> clears session
        -> takes to log in page
    """
    session.clear()
    return redirect("/auth/login")