
############################## IMPORTS ##############################

# from xmlrpc.client import Boolean # delete ???
import functools


import datetime
from calendar import monthrange
from flask_mail import Message

from flask import (
    Blueprint, request, render_template, session,redirect, flash
)

from capp.actions import (
    sessionExists, sendEmail, extractTime
)

from capp.calendarStuff import (
    calendarInfo, Event, getEventDates, addEvent, getEventsCurMonth, getEventDay, getEvent, deleteEvent
)

from capp import email, mysql

from bson import json_util
import json
############################## VIEWS ##############################

views = Blueprint("views", __name__)

the_calendar = calendarInfo() # calendarInfo object to instore calendar information


############### HOMEPAGE/Calendar ###############

@views.route("/")
def homepage1():

    if (not sessionExists()): 

        return redirect("/auth/login")

    # get data needed to build calendar and to fetch events from mongo
    data = the_calendar.getData()

    # events collection of the user
    events_col = getEventsCurMonth(session['user']['username'], datetime.datetime(data['year'], data['month'], data['day']))
   
    # list of events to mark on calendar
    eventList = getEventDates(events_col)

    return render_template("homepage.html", data = data, events = eventList)
    

@views.route("/1")
def homepage2():

    if (not sessionExists()):

        return redirect("/auth/login")

    the_calendar.nextMonth()

    # get data needed to build calendar and to fetch events from mongo
    data = the_calendar.getData()

    # events collection of the user
    events_col = getEventsCurMonth(session['user']['username'], datetime.datetime(data['year'], data['month'], data['day']))

    # list of events to mark on calendar
    eventList = getEventDates(events_col)

    return render_template("homepage.html", data = data, events = eventList)


@views.route("/2")
def homepage3():

    if (not sessionExists()):

        return redirect("/auth/login")

    the_calendar.prevMonth()
    
    # get data needed to build calendar and to fetch events from mongo
    data = the_calendar.getData()

    # events collection of the user
    events_col = getEventsCurMonth(session['user']['username'], datetime.datetime(data['year'], data['month'], data['day']))

    # list of events to mark on calendar
    eventList = getEventDates(events_col)

    return render_template("homepage.html", data = data, events = eventList)


############### EVENTS ################

@views.route("/cevent", methods=('GET', 'POST'))
def cevent():
    """
        > where events are created and manage storing them in mongoDB
    """
    if (not sessionExists()):

        return redirect("/auth/login")

    
    if (request.method == "POST"):

        eventName = request.form["eventName"]
        [sdate, stime] = request.form['sdate'].split("T")
        [edate, etime] = request.form['edate'].split("T")
        [sy, sm, sd] = str(sdate).split("-") # y-m-d
        [shr, smin] = str(stime).split(":") # h:m
        [ey, em, ed] = str(edate).split("-")
        [ehr, emin] = str(etime).split(":")
        location = request.form["location"]
        description = request.form["description"]

        event = Event(str(eventName), datetime.datetime(int(sy), int(sm), int(sd), int(shr), int(smin)), datetime.datetime(int(ey), int(em), int(ed), int(ehr), int(emin)), location, description)

        addEvent(session['user']['username'], event)

        return redirect('/')

    return render_template("addEvent.html")
        

############### PROFILE ###############

@views.route("/profile")
def profile():

    if (not sessionExists()):

        return redirect("/auth/login")

    # get username and email from session
    username = session["user"]["username"]
    email = session["user"]["email"]

    return render_template('profile.html', username = username , email = email)



############### GROUPS ###############

@views.route("/groups")
def gorups():

    # if (not sessionExists()):

    #     return redirect("/auth/login")

    return render_template('groups.html')



############### HELP ###############

@views.route("/help", methods=["GET", "POST"])
def help():

    if (not sessionExists()):

        return redirect("/auth/login")

    if (request.method == "POST"):

        # get user's email and message from the form
        user_email = request.form["email"]
        user_message = request.form["message"]

        
        messageStatus = sendEmail("Help Needed - " + user_email, user_message, user_email, 'capp.supp2022@gmail.com')
    
        if messageStatus:

            flash("Message successfully delivered!", "s-message")
        
        else:

            flash("Message delivery failed!", "e-message")

        return render_template('help.html')

    return render_template('help.html')



############### SETTINGS ###############

@views.route("/settings")
def settings():

    if (not sessionExists()):

        return redirect("/auth/login")

    return render_template('settings.html')




@views.route("/displayEvents")
def displayEvents():

    if (not sessionExists()):

        return redirect("/auth/login")

    date = request.args["date"]

    [y, m, d] = date.split("-")
    events_col = getEventDay(session['user']['username'], datetime.datetime(int(y), int(m), int(d)))

    eventz = {}

    for i in events_col:
        i['_id'] = str(i['_id']) # turns ObjectID to str
        st = datetime.datetime.strptime(extractTime(str(i['startTime'])), "%H:%M")
        et = datetime.datetime.strptime(extractTime(str(i['endTime'])), "%H:%M")
        i['startTime'] = st.strftime("%I:%M %p")
        i['endTime'] = et.strftime("%I:%M %p")
        eventz[i['_id']] = i

    return render_template('displayEvents.html', eventDict=eventz, date = date)

# View Event
@views.route("/ve")
def ve():

    if (not sessionExists()):

        return redirect("/auth/login")

    eidd = request.args["eidd"] # event ID + date

    [eid, date] = eidd.split("date")

    event = getEvent(session['user']['username'], str(eid))

    st = datetime.datetime.strptime(extractTime(str(event['startTime'])), "%H:%M")
    et = datetime.datetime.strptime(extractTime(str(event['endTime'])), "%H:%M")
    
    event['startTime'] = st.strftime("%I:%M %p")
    event['endTime'] = et.strftime("%I:%M %p")

    return render_template('viewEvent.html', event=event, eventid=eid, date=date, eid=eid)

# modify Event
@views.route("/mode", methods=["GET", "POST"])
def mode():

    if (not sessionExists()):

        return redirect("/auth/login")

    if (request.method == "POST"):

        eventName = request.form["eventName"]
        [sdate, stime] = request.form['sdate'].split("T")
        [edate, etime] = request.form['edate'].split("T")
        [sy, sm, sd] = str(sdate).split("-") # y-m-d
        [shr, smin] = str(stime).split(":") # h:m
        [ey, em, ed] = str(edate).split("-")
        [ehr, emin] = str(etime).split(":")
        location = request.form["location"]
        description = request.form["description"]

        event = Event(str(eventName), datetime.datetime(int(sy), int(sm), int(sd), int(shr), int(smin)), datetime.datetime(int(ey), int(em), int(ed), int(ehr), int(emin)), location, description)

        addEvent(session['user']['username'], event)

        return redirect('/')

    eid = request.args["eid"] # event ID

    event = getEvent(session['user']['username'], str(eid)) # fetch event

    deleteEvent(session['user']['username'], eid) # delete event

    return render_template('modEvent.html', event=event)


# delete Event
@views.route("/de")
def de():

    if (not sessionExists()):

        return redirect("/auth/login")

    eid = request.args["eid"] # event ID

    deleteEvent(session['user']['username'], str(eid)) # delete event

    return redirect("/")


# PAGE NOT FOUND
@views.errorhandler(404)
def not_found(e):
    return "<h1>PAGE NOT FOUND</h2>"



