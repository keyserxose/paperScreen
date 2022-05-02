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
print('This is the current hour: '+hourFormated)

# This is a test to get the weather

def getJsonTest():
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
    #print(jsonData)
    #print(jsonData[0]['prediccion']['dia'][0])
    # Get data for today
    #for i in range(len(jsonData)):
    #    if jsonData[i]['prediccion']['dia'][0]['fecha'] == "2022-05-02T00:00:00":
    #        date = jsonData[i]['prediccion']['dia'][0]['fecha']
    #        print('Date: '+date)
    #        periodo = jsonData[i]['prediccion']['dia'][0]['estadoCielo'][0]['periodo']
    #        print('Periodo: '+periodo)
    #        description = jsonData[i]['prediccion']['dia'][0]['estadoCielo'][0]['descripcion']
    #        print('Descripcion: '+description)

    # This one below looks like it's working! - We select the first day or current day, and then itereate with i through all the periods and descriptions below estadoCielo
    for i in range(len(jsonData[0]['prediccion']['dia'][0])):
        #print('This is a test')
        #print(jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['periodo'])
        #print(jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['descripcion'])
        if jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['periodo'] == hourFormated:
            print('The time is: '+hourFormated)
            print('The weather is: '+jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['descripcion'])
            global weatherDesc
            weatherDesc = jsonData[0]['prediccion']['dia'][0]['estadoCielo'][i]['descripcion']
            #print(weatherDesc)
        
        elif jsonData[0]['prediccion']['dia'][0]['temperatura'][i]['periodo'] == hourFormated:
            global temp
            temp = jsonData[0]['prediccion']['dia'][0]['temperatura'][i]['value']
            print('The temperature is: '+temp)

getJsonTest()

def generateJSON():
    with open('weatherdata.json', 'w') as outfile:
        json.dump(jsonData, outfile, indent=2)

generateJSON()

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

def processJson():
    global jsonTemp
    jsonTemp = jsonData[-1]['ta']
    print('Temp: '+str(jsonTemp))

#processJson()

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
    <h2>This is a test</h2>
    <img src=weather/"""+weatherIcon+""" alt='weather-icon' width = "100" height = "100">
    <p>Date: """+str(jsonDate)+"""</p>
    <p>City: """+str(jsonCity)+"""</p>
    <p>Temp: """+str(temp)+"""º C</p>
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

# Take the screenshot
#hti.screenshot(url='http://localhost:8080/paper/index.html', save_as='status.png', size=(600, 800))

# Convert to grayscale
os.system('convert status.png -type GrayScale -depth 8 -colors 256 status.png')

# Permissions
os.system('chmod 777 status.png')

# Copy image to apache dir
os.system('cp -p status.png /srv/http/status.png')

