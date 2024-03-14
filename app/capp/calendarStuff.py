import calendar
from calendar import monthrange
import datetime
from capp.actions import getMongoDB
import pymongo

# importing ObjectId from bson library
from bson.objectid import ObjectId

class calendarInfo:

    def __init__(self) -> None:
        [todayYear,todayMonth, todayDay] = str(datetime.date.today()).split("-")
        self.todayYear = int(todayYear)
        self.todayMonth = int(todayMonth)
        self.todayDay = int(todayDay)
        self.year = self.todayYear
        self.month = self.todayMonth
        self.day = self.todayDay
        self.totalGrids = 42 # grids of the calendar from web app
    

    def getStartDay(self) -> int:

        return int(calendar.monthrange(self.year, self.month)[0])

    def getRange(self) -> int:

        return int(calendar.monthrange(self.year, self.month)[1])

    def getMonthName(self) -> str:

        return (str(calendar.month_name[self.month][0:3])).upper()

    def getEB(self) -> int:

        return self.totalGrids - (self.getStartDay() + self.getRange())

    def nextMonth(self):
        """
            > increase month by 1
        """
        if self.month == 12:

            self.year += 1
            self.month = 1
        
        else:

            self.month += 1

    def prevMonth(self):
        """
            > decrease month by 1
        """
        if self.month == 1:

            self.year -= 1
            self.month = 12
        
        else:

            self.month -= 1
        
    def getData(self) -> dict:
        """
            > returns data needed to build calendar
        """
        data = {
        "currentDay" : int(self.todayDay),
        "currentMonth" : int(self.todayMonth),
        "currentYear" : int(self.todayYear),
        "monthName" : self.getMonthName(),
        "startDay" : self.getStartDay(),
        "range" : self.getStartDay(),
        "day" : self.day,
        "month" : self.month,
        "year" : self.year,
        "cBuild" : {
            "mb" : self.getRange(),   # days of the month
            "eb" : self.getEB()       # empty grids at the end of calendar view
        }}

        return data




class Event:

    """
        > Event class
    """
    def __init__(self, name : str, startTime : datetime, endTime : datetime, location : str, description : str):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.location = location
        self.description = description

        self.tokenizeDatetime(self.startTime)

    def getName(self) -> str:
        return self.name

    def setName(self, name) -> None:
        self.name = name
    
    def getStartTime(self) -> datetime:
        return self.startTime

    def setStartTime(self, startTime) -> None:
        self.startTime = startTime
        self.tokenizeDatetime(self.startTime)

    def getEndTime(self) -> datetime:
        return self.endTime

    def setEndTime(self, endTime) -> None:
        self.endTime = endTime

    def getLocation(self) -> datetime:
        return self.location

    def setLocation(self, location) -> None:
        self.location = location

    def getDescription(self) -> datetime:
        return self.description

    def setDescription(self, description) -> None:
        self.description = description

    def tokenizeDatetime(self, time):

        [date, time] = str(time).split(" ")
        [y, m, d] = date.split("-")
        [hr, min, sec] = time.split(":")

        self.year = y
        self.month = m
        self.day = d
        self.hour = hr
        self.minute = min
        self.second = sec
        self.date = date
        self.time = time

    def getYear(self):
        return self.year
    
    def getMonth(self):
        return self.month

    def getDay(self):
        return self.day

    def getHour(self):
        return self.hour

    def getMinute(self):
        return self.minute
    
    def getDate(self):
        return self.date

    def getTime(self):
        return self.time

    def getSecond(self):
        return self.second

    def getFormattedData(self):

        data = {
            "eventName" : self.getName(),
            "startTime" : self.getStartTime(),
            "endTime" : self.getEndTime(),
            "location" : self.getLocation(),
            "description" : self.getDescription()
        }

        return data

    # toString
    def __str__(self):
        return f"""
        event name : {self.getName()}
        start time : {self.getStartTime()}
        end time : {self.getEndTime()}
        location : {self.getLocation()}
        description : {self.getDescription()}
        """


def getEventDates(eventList):

    a_dict = {}

    for event in eventList:

        a_dict[f"{event['startTime'].year}{event['startTime'].month}{event['startTime'].day}"] = 1

    return a_dict



def addEvent(username: str, event: Event) -> None:
    """
        > add new event to user's collection in mongoDB
    """
    db = getMongoDB()

    col = db[username]

    col.insert_one(event.getFormattedData())

def updateEvent(username: str, event: Event, eventID: str) -> None:
    """
        > update event
    """
    db = getMongoDB()

    col = db[username]

    col.update_one({'_id': ObjectId(eventID)}, { "$set" : event.getFormattedData() } )


def getEventsCurMonth(username : str, curDate : datetime) -> dict:

    lastDayOfMonth = monthrange(int(curDate.year), int(curDate.month))[1]

    db = getMongoDB()

    col = db[username]

    startDate = datetime.datetime(int(curDate.year), int(curDate.month), 1)
    endDate = datetime.datetime(int(curDate.year), int(curDate.month), int(lastDayOfMonth))

    return col.find({ "startTime" : {"$gte": startDate, "$lte": endDate}})


def getEventDay(username : str, curDate : datetime) -> dict:
    """
        return collection of events on a given datetime
    """
    db = getMongoDB()

    col = db[username]

    startDate = datetime.datetime(int(curDate.year), int(curDate.month), int(curDate.day), 0)
    endDate = datetime.datetime(int(curDate.year), int(curDate.month), int(curDate.day), 0)

    return col.find({ "startTime" : {"$gte": startDate, "$lte": endDate}}).sort("startTime", 1)


def getEvent(username : str, eventID: str) -> dict:
    """
        return event usingthe eventID
    """
    db = getMongoDB()

    col = db[username]

    return col.find_one(ObjectId(eventID))

def deleteEvent(username : str, eventID: str) -> None:
    """
        delete event
    """
    db = getMongoDB()

    col = db[username]

    col.delete_one({'_id': ObjectId(eventID)})