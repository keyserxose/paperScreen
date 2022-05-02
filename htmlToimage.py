#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from html2image import Html2Image
import json
import requests
from datetime import date
from datetime import datetime
#import argparse
import configparser

hti = Html2Image()

# Reading from the current path
path = __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

config_file = path+'/htmlToimage.conf'

# Parsing config file
config = configparser.ConfigParser()
config.read(config_file)
apiKey = config['DEFAULT']['ApiKey']


# This gets the time
now = datetime.now()
hourFormated = str(now.hour)
print('This is the system hour: '+hourFormated)

def getJson():
    url = "https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/horaria/28079/"
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


def getSunriseSunset():
    global sunrise
    sunrise = jsonData[0]['prediccion']['dia'][0]['orto']
    global sunset
    sunset = jsonData[0]['prediccion']['dia'][0]['ocaso']
    print('Sunrise: '+sunrise)
    print('Sunset: '+sunset)

getSunriseSunset()

# This gets the weather description
def getWeatherDesc():
    # This one below looks like it's working! - We select the first day or current day, and then itereate with i through all the periods and descriptions below estadoCielo
    for i in range(len(jsonData[0]['prediccion']['dia'][0]['estadoCielo'])):
        #print(jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['periodo'])
        if jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['periodo'] == hourFormated:
            print('The API time is: '+hourFormated)
            print('The weather is: '+jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['descripcion'])
            global weatherDesc
            weatherDesc = jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['descripcion']

getWeatherDesc()

def getTemp():
    for i in range(len(jsonData[0]['prediccion']['dia'][0]['temperatura'])):
        if jsonData[0]['prediccion']['dia'][0]['temperatura'][i]['periodo'] == hourFormated:
            print('The temp is: '+jsonData[0]['prediccion']['dia'][0]['temperatura'][i]['value'])
            global temp
            temp = jsonData[0]['prediccion']['dia'][0]['temperatura'][i]['value']

getTemp()


def generateJSONFile():
    with open('weatherdata.json', 'w') as outfile:
        json.dump(jsonData, outfile, indent=2)

generateJSONFile()

def showIcon():
    global weatherIcon
    if weatherDesc == 'Cubierto con tormenta y lluvia escasa' or weatherDesc == 'Muy nuboso con tormenta y lluvia escasa':
        weatherIcon = 'thunderstorm.png'
    elif weatherDesc == 'Cubierto con lluvia escasa' or weatherDesc == 'Nuboso con lluvia escasa' or weatherDesc == 'Intervalos nubosos con lluvia escasa':
        weatherIcon = 'rain.png'
    elif weatherDesc == 'Nubes altas' or weatherDesc == 'Cubierto' or weatherDesc == 'Muy nuboso' or weatherDesc == 'Nuboso':
        weatherIcon = 'cloud.png'
    else:
        pass

showIcon()

# Weather codes

# 64 - Cubierto con tormenta y lluvia escasa
# 63 - Muy nuboso con tormenta y lluvia escasa
# 46 - Cubierto con lluvia escasa
# 44 - Nuboso con lluvia escasa
# 43 - Intervalos nubosos con lluvia escasa
# 17 - Nubes altas
# 16 - Cubierto
# 15 - Muy nuboso
# 14 - Nuboso


def jsonNewData():
    global jsonDate
    jsonDate = jsonData[0]['elaborado']
    print('Date of report: '+jsonDate)
    global jsonCity
    jsonCity = jsonData[0]['nombre']
    print('City: '+jsonCity)

jsonNewData()

# This can be removed in the future

def getJson():
    url = "https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/3195/"
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
    #print(jsonData)

getJson()

# This generates the index.html

def generateHtml():
    f = open('paper/index.html', 'w')
    html = """<html>
    <head>
    <meta charset='utf-8'/>
    <title>Title</title>
    <link rel= 'stylesheet' type='text/css' href='style.css'/>
    </head>
    <body>
    <h2>SMART PANEL</h2>
    <img src=weather/"""+weatherIcon+""" alt='weather-icon' width = "100" height = "100">
    <p>Date of report: """+str(jsonDate)+"""</p>
    <p>City: """+str(jsonCity)+"""</p>
    <p>Temp: """+str(temp)+"""º C</p>
    <p>Sunrise: """+str(sunrise)+"""</p>
    <img src=weather/sunrise.png alt='weather-icon' width = "100" height = "100">
    <p>Sunset: """+str(sunset)+"""</p>
    <img src=weather/sunset.png alt='weather-icon' width = "100" height = "100">
    </body>
    </html>
    """
    # writing the code into the file
    f.write(html)
    
    # close the file
    f.close()

generateHtml()

os.system('chmod -R 777 paper')

os.system('cp -p -R paper /srv/http/')

def screenshot():
    hti.screenshot(url='http://localhost:8080/paper/index.html', save_as='status.png', size=(600, 800))
    os.system('convert status.png -type GrayScale -depth 8 -colors 256 status.png')
    os.system('chmod 777 status.png')
    os.system('cp -p status.png /srv/http/status.png')


#screenshot()

