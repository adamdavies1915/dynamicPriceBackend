import pyrebase
import pandas as pd
import math
import schedule
import time
from twilio.rest import Client


def runPricing():
  rooms = db.child('roomDetails').get().val()

  roomPrices = calculatePriceOfMeetingRooms(rooms)

  db.child("roomPrices").set(roomPrices)

def getTimeToBookingWeighting(bookingDatetime):
  differenceInHours = (bookingDatetime - pd.Timestamp.now()).total_seconds()/3600
  if differenceInHours < 168:
    return 2.92 + (3.44 * math.log(differenceInHours))
  else:
    return 1

def calculatePriceOfMeetingRooms(rooms):
    roomPrices = {}
    for room in rooms:
      roomPrices[room] = calculatePriceOfMeetingRoom(rooms[room])
    return roomPrices
      
def calculatePriceOfMeetingRoom(room):
    startDatetime = pd.Timestamp.now().round('60min')
    endDatetime = startDatetime + pd.Timedelta("10 days")
    datetimeList = pd.date_range(startDatetime, endDatetime, freq="h").tolist()
    roomPrices = {}
    for datetime in datetimeList:
      if datetime < pd.Timestamp.now():
        continue
      roomPrices[datetime.strftime("%m-%d-%Y:%H:%M:%S")] = round((1 * (room["capacity"]/2.5) * getTimeToBookingWeighting(datetime)), 2)
    return roomPrices


def stream_handler(message):
  try:
    print("change")
    print("sending sms")
    message = client.messages.create(
    to="+447419345365",
    from_="+441356707052",
    body="Hello the booking you're watching: "+message["data"]+" has become available")

    print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
    print(message.sid)
  except:
    pass


###Firebase config
config = {
    "apiKey": "AIzaSyASUKH1z9HYxtqIWhbsufQgWK0E28I8zoE",
    "authDomain": "dynamicprice-36096.firebaseapp.com",
    "databaseURL": "https://dynamicprice-36096.firebaseio.com",
    "storageBucket": "dynamicprice-36096.appspot.com",
    "serviceAccount": "dynamicprice-36096-firebase-adminsdk-fyouj-c630fb9e51.json"
  }

firebase = pyrebase.initialize_app(config)

db = firebase.database()


###Twilio config


account_sid = "AC7862d1c7307e0ebcf16075a46840f0f2"
auth_token = "fc0342180b028509f1085cd58f380304"
client = Client(account_sid, auth_token)


my_stream = db.child("roomBookings").stream(stream_handler)

# schedule.every(1).minutes.do(runPricing)

# while(True):
#   schedule.run_pending()
#   time.sleep(1)