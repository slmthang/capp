
#################### IMPORTS ####################

from xmlrpc.client import Boolean
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from capp import email, mysql
import random
from flask_mail import Message
import datetime
import calendar
import pymongo
import os

#######################################################

class User:
    """
    User account class
    description: class for person
    Attributes
    ----------
    personId : int 
        unique id number for each person
    username : str
        username
    email : str
        user's email
    password : str
        user's password
    dob : str
        user's date of birth
    gender : str
        user's gender
    
    Methods
    -------
    getId() -> int
        get User's ID
    setId(id) -> None
        set Username's ID
    getUserame() -> str
        get Username
    setUsername(username) -> None
        set Username
    getEmail() -> str
        get email
    setEmail(email) -> None
        set email
    getPassword() -> str
        get password
    setPassword(password) -> None
        set password
    getDob() -> Date (class)
        get DOB
    setDob(date) -> None
        set DOB
    getGender() -> str
        get gender
    setGender(gender) -> None
        set gender
    """
    
    def __init__(self, username, email, password, dob, gender) -> None:
        self.id = 1  # need to change
        self.username = username
        self.email = email
        self.password = password
        self.dob = dob
        self.gender = gender

    def getId(self) -> int:
        return self.id

    def setId(self, id) -> None:
        self.id = id

    def getUsername(self) -> str:
        return self.username

    def setUsername(self, username) -> None:
        self.username = username

    def getEmail(self) -> str:
        return self.email

    def setEmail(self, email) -> None:
        self.email = email
    
    def getPassword(self) -> str:
        return self.password

    def setPassword(self, password) -> None:
        self.password = password
    
    def getDob(self) -> datetime.date:
        return self.dob

    def setDob(self, dob) -> None:
        self.dob = dob
    
    def getGender(self) -> str:
        return self.gender

    def setGender(self, gender) -> None:
        self.gender = gender
    
    # toString
    def __str__(self):
        return f"""
        id : {self.getId()}
        name : {self.getUsername()}
        email : {self.getEmail()}
        password : {self.getPassword()}
        dob : {self.getDob()}
        gender : {self.getGender()}
        """


#################### ACTIONS #########################

#  sessionExists()
def sessionExists():
    """
        > check user's session existence
    """

    if session.get("user") is None:
        return False
    else:
        return True



# createAccount()
def createAccount(username : str, email : str, password : str, dob : str, gender : str) -> Boolean:
    """
        > create user's account with provided information
        > returns true if accunt is created sucessfully, else returns false
    """

    try:
        
        #Creating a connection cursor
        cursor = mysql.connection.cursor()

        # sql statement
        sql = """INSERT INTO users (username, email, password, dob, gender) VALUES (%s, %s, %s, %s, %s)"""

        # execute sql statement
        cursor.execute(sql, (username, email, generate_password_hash(password), dob, gender))

        # Saving the Actions performed on the DB
        mysql.connection.commit()

    except Exception as e:

        return e

    finally:

        #Closing the cursor
        cursor.close()

    return True



# log in account
def loginAccount(email : str, password : str) -> Boolean:
    """
        > log in user using provided email and password
        > return True if logged in successfully, otherwise False
    """

    try:

        #Creating a connection cursor
        cursor = mysql.connection.cursor()

        # sql statement
        sql = """SELECT * FROM users WHERE email=%s"""
        
        # execute the sql
        cursor.execute(sql, (email,))

        # fetch the data
        user = cursor.fetchone()

        # check if user exists in table and if the password is correct
        if user is None:
            return False

        elif not check_password_hash(user['password'], password):
            return False


        # store user's id, username and email in session
        userInfo = {
            "user_id" : user["user_id"],
            "username" : user["username"],
            "email" : user["email"]
        }

        session["user"] = userInfo

    except Exception as e:

        return False

    finally:

        #Closing the cursor
        cursor.close()

    return True



def sendVcode(messageSubject : str, userEmail : str) -> Boolean:
    """
        > Generate a code for verification and store it in session 
        > send the code to user via email
        > returns True if message was sent successfully, else returns False
    """

    try:

        # generate random code
        code = random.randint(10000,100000)

        # send verification code
        message = Message( messageSubject, sender = 'capp.supp2022@gmail.com', recipients = ['capp.supp2022@gmail.com', userEmail])
        message.body = str(code)
        mail = email()
        mail.send(message)

        # store code in session
        session["vcode"] = code
    
    except:

        return False

    return True


def sendEmail(messageSubject : str, messageBody : str, fromEmail : str, toEmail : str) -> Boolean:
    """
        > Send email using provided message subject, body and email address
        > returns True if message was sent successfully, else returns False
    """

    try:

        # send verification code
        message = Message( messageSubject, sender = fromEmail, recipients=[toEmail,])
        message.body = messageBody
        mail = email()
        mail.send(message)
    
    except Exception as e:

        return e

    return True



def existEmail(email : str) -> Boolean:
    """
        > checks if email exists in users database
        > returns True if exists, else returns False
    """

    try:

        #Creating a connection cursor
        cursor = mysql.connection.cursor()

        # sql statement
        sql = """SELECT * FROM users WHERE email=%s"""

        # execute sql statement
        cursor.execute(sql, (email,))

        # fetch row
        user = cursor.fetchone()

    except:

        return False

    finally:

        #Closing the cursor
        cursor.close()
    
    if user is None:

        return False

    return True


def updateUserPassword(email : str, newPassword : str) -> Boolean:
    """
        > update user's password in the database
        > returns True if update sucessfully, else returns False
    """

    try:

        #Creating a connection cursor
        cursor = mysql.connection.cursor()

        # sql statement
        sql = """UPDATE users SET password=%s WHERE email=%s"""

        # execute sql statement
        cursor.execute(sql, (generate_password_hash(newPassword), email,)) # update user password with new one

        # Saving the Actions performed on the DB
        mysql.connection.commit()

    except:

        return False

    finally:

        #Closing the cursor
        cursor.close()

    return True


def getMongoDB():
    """
        > returns mongoDB database
    """
    client = pymongo.MongoClient(f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASS')}@capp.7ecgh3z.mongodb.net/?retryWrites=true&w=majority")

    return client.capp

def extractTime(someDateTime):

    time = someDateTime.split(" ")[1]

    time = time.split(":")

    return time[0] + ":" + time[1]
    
