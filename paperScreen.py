#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from html2image import Html2Image
import json
import requests
import time
from datetime import date
from datetime import datetime
import configparser
import imgkit
import re
hti = Html2Image(custom_flags=['--quiet'])

# Reading from the current path
path = __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

config_file = path+'/paper.conf'

# Parsing config file
config = configparser.ConfigParser()
config.read(config_file)
apiKey = config['DEFAULT']['ApiKey']

# This gets the system time
def getTime():
    now = datetime.now()
    global currentDate
    currentDate = now.strftime("%Y-%m-%d")
    print('Current Date: '+currentDate)
    global hour
    hour = now.hour
    global hourStr
    hourStr = str(hour)
    global currentTimeHour
    currentTimeHour = now.strftime("%H")
    global currentTime
    currentTime = now.strftime("%H:%M")
    print('Current Time: '+currentTime)


getTime()


# This we don't need
def convertTime():
    if 0 <= hour <= 9:
        newTime = myTime+hour
        global newTimeConverted
        newTimeConverted = '0'+str(newTime)
        print('Its a single digit hour')
        print('This is newtime: '+newTimeConverted)
    else:
        print(myTime)
        newTime = myTime+hour
        print(newTime)
        newTimeConverted = str(newTime)
        print('Its a double digit hour')
        print('This is newtime: '+newTimeConverted)



# City Codes
# A Coruña - 15030
# Madrid - 28079
# Burela - 27902

def getJson():
    url = "https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/horaria/27902/"
    querystring = {"api_key":apiKey}
    headers = {'cache-control': "no-cache"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    #print(response.text)
    request = requests.get(url, headers=headers, params=querystring)
    data = request.json()
    output = data['datos']
    #print('This is your data endpoint: '+output)
    jsonRequest = requests.get(output)
    global jsonData
    jsonData = jsonRequest.json()

getJson()


def generateJSONFile():
    with open('weatherdata.json', 'w') as outfile:
        json.dump(jsonData, outfile, indent=2)

generateJSONFile()

# WE NEED TO ITERATE THROUGH THE DAY, WE CANNOT HARDCODE THE VALUE, OTHERWISE IT WILL FAIL DURING THE MORNING
def getToday():
    for i in range(len(jsonData[0]['prediccion']['dia'])):
        jsonDataModified = jsonData[0]['prediccion']['dia'][i]['fecha']
        jsonDataModifiedNew = re.search(r'\d{4}-\d{2}-\d{2}', jsonDataModified)
        date = datetime.strptime(jsonDataModifiedNew.group(), '%Y-%m-%d').date()
        if str(date) == currentDate:
            global jsonToday
            jsonToday = jsonData[0]['prediccion']['dia'][i]
            print('API Date: '+jsonToday['fecha'])

getToday()

def getWeatherDesc(time):
    global myTime
    myTime = time
    convertTime()
    for i in range(len(jsonToday['estadoCielo'])):
        if jsonToday['estadoCielo'][i]['periodo'] == newTimeConverted:
            print('API Time: '+hourStr)
            global weatherDesc
            weatherDesc = jsonToday['estadoCielo'][i]['descripcion']
            print('The weather is: '+weatherDesc)

getWeatherDesc(1)


def getTemp():
    for i in range(len(jsonToday['temperatura'])):
        if jsonToday['temperatura'][i]['periodo'] == newTimeConverted:
            global temp
            temp = jsonToday['temperatura'][i]['value']
            print('The temp is: '+temp)

getTemp()

def getSunriseSunset():
    global sunrise
    sunrise = jsonToday['orto']
    global sunset
    sunset = jsonToday['ocaso']
    print('Sunrise: '+sunrise)
    print('Sunset: '+sunset)

getSunriseSunset()

# Why is this repeated?
def generateJSONFile():
    with open('weatherdata.json', 'w') as outfile:
        json.dump(jsonData, outfile, indent=2)

#generateJSONFile()

def showIcon():
    global weatherIcon
    #if weatherDesc == 'Cubierto con tormenta y lluvia escasa' or weatherDesc == 'Muy nuboso con tormenta y lluvia escasa' or weatherDesc == 'Muy nuboso con tormenta':
    if 'tormenta' in weatherDesc:
        weatherIcon = 'thunderstorm.png'
    elif weatherDesc == 'Cubierto con lluvia escasa' or weatherDesc == 'Nuboso con lluvia escasa' or weatherDesc == 'Muy nuboso con lluvia escasa':
        weatherIcon = 'rain.png'
    elif weatherDesc == 'Intervalos nubosos con lluvia escasa':
        weatherIcon = 'rainy.png'
    elif weatherDesc == 'Cubierto' or weatherDesc == 'Muy nuboso' or weatherDesc == 'Nuboso':
        weatherIcon = 'cloud.png'
    elif weatherDesc == 'Niebla':
        weatherIcon = 'haze.png'
    elif weatherDesc == 'Poco nuboso' or weatherDesc == 'Intervalos nubosos' or weatherDesc == 'Nubes altas':
        if 6 <= hour <= 21:
            weatherIcon = 'cloudy.png'
        else:
            weatherIcon = 'cloudy-night.png'
    elif weatherDesc == 'Despejado':
        if 6 <= hour <= 21:
            weatherIcon = 'sun.png'
        else:
            weatherIcon = 'full-moon.png'
    else:
        weatherIcon = 'ufo.png'
        pass

showIcon()

def jsonMainDetails():
    global jsonDate
    jsonDate = jsonData[0]['elaborado']
    print('Date of report: '+jsonDate)
    global jsonCity
    jsonCity = jsonData[0]['nombre']
    print('City: '+jsonCity)

jsonMainDetails()

def generateHtml():
    f = open('paper/index.html', 'w')
    html = """<html>
    <head>
    <meta charset='utf-8'/>
    <title>Smart Panel</title>
    <link rel= 'stylesheet' type='text/css' href='style.css'/>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@200&display=swap" rel="stylesheet">
    </head>
    <body>
    <img id='icon' src=weather/"""+weatherIcon+""" alt='weather-icon' width = "70" height = "70">
    <a id='temp'>"""+str(temp+'º')+"""</a>
    <a id='time'>"""+currentTime+"""</a>
    <p></p>
    <a id='text'>&nbsp;"""+weatherDesc+"""&nbsp;</a>
    <a id='text'>|</a>
    <a id='text'>&nbsp;"""+str(jsonCity)+"""&nbsp;</a>
    <p></p>
    <img src=weather/sunrise.png alt='weather-icon' width = "70" height = "70">
    <img id='left' src=weather/sunset.png alt='weather-icon' width = "70" height = "70">
    <p></p>
    <a>&nbsp;&nbsp;"""+str(sunrise)+"""</a>
    <a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+str(sunset)+"""</a>
    </body>
    </html>
    """
    # writing the code into the file
    f.write(html)
    
    # close the file
    f.close()


#generateHtml()

def generateHtmlSimple():
    f = open('paper/index.html', 'w')
    html = """<html>
    <head>
    <meta charset='utf-8'/>
    <title>Smart Panel</title>
    <link rel= 'stylesheet' type='text/css' href='style.css'/>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@200&display=swap" rel="stylesheet">
    </head>
    <body>
    <img id='icon' src=weather/"""+weatherIcon+""" alt='weather-icon' width = "70" height = "70">
    <a id='temp'>"""+str(temp+'º')+"""</a>
    <a id='time'>"""+currentTime+"""</a>
    <p></p>
    <a id='text'>&nbsp;"""+weatherDesc+"""&nbsp;</a>
    <a id='text'>|</a>
    <a id='text'>&nbsp;"""+str(jsonCity)+"""&nbsp;</a>
    <p></p>
    </body>
    </html>
    """
    # writing the code into the file
    f.write(html)
    
    # close the file
    f.close()

generateHtmlSimple()

def folderPermissions():
    os.system('cp style.css paper/')
    os.system('chmod -R 777 paper')
    os.system('cp -p -R paper /srv/http/')

folderPermissions()

def screenshot():
    hti.screenshot(url='http://localhost:8080/paper/index.html', save_as='status.png', size=(600, 800))
    os.system('convert status.png -type GrayScale -depth 8 -colors 256  -rotate 180 status.png')
    os.system('chmod 777 status.png')
    os.system('cp -p status.png /srv/http/status.png')

screenshot()

