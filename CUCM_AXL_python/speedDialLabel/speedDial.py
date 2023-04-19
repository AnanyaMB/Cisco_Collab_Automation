import requests
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import csv
import bs4 as bs
import pandas as pd
import json
import time
import math


# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#to fetch speed dial index,label and number from a given phone
def fetchSpeedDialFromPhone(cucm,user,password,version,deviceName):
  url = "https://"+cucm+":8443/axl/"
  deviceName = deviceName
  payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/"+version+"\">\n<soapenv:Header/>\n<soapenv:Body>\n<ns:getPhone>\n    <name>"+deviceName+"</name>\n</ns:getPhone>\n</soapenv:Body>\n</soapenv:Envelope>"
  headers = {'Content-Type': 'text/xml'}
  response = requests.request("POST", url, headers=headers, data=payload,auth=HTTPBasicAuth(user,password),verify=False)
  # response = response.text
  return response

#to fetch speed dial index,label and number from a given device profile
def fetchSpeedDialFromDeviceProfile(cucm,user,password,version,deviceName):
  url = "https://"+cucm+":8443/axl/"
  deviceName = deviceName
  payload = payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/"+version+"\">\n<soapenv:Header/>\n<soapenv:Body>\n<ns:getDeviceProfile>\n    <name>"+deviceName+"</name>\n</ns:getDeviceProfile>\n</soapenv:Body>\n</soapenv:Envelope>"
  headers = {'Content-Type': 'text/xml'}
  response = requests.request("POST", url, headers=headers, data=payload,auth=HTTPBasicAuth(user,password),verify=False)
  return response

#parse xml response after fetching speed dial info into a json
def parseXmlResponse(response,deviceName):
  soup = bs.BeautifulSoup(response, "lxml")
  speedDials = soup.find_all('speeddials')
  speedDialList = []
  for speedDial in speedDials:
      speedDialXmlList = speedDial.find_all('speeddial')
      for eachSpeedDialXml in speedDialXmlList:
          eachSpeedDialDict = {
                      "deviceName" : deviceName,
                      "dirn": eachSpeedDialXml.find('dirn').text,
                      "index" : eachSpeedDialXml.find('index').text,
                      "label" : eachSpeedDialXml.find('label').text,
                        }
          speedDialList.append(eachSpeedDialDict)
  return (speedDialList)

#write the consolidated report for all devices in input to output file
def writeToCsv(filename,data):
  with open(filename, "w") as f:
    wr = csv.DictWriter(f, delimiter=",",fieldnames=list(data[0].keys()))
    wr.writeheader()
    wr.writerows(data)

#main function to invoke speed dial fetching
def fetchSpeedDialReport(cucm,user,password,deviceType):
  if deviceType.lower() == "device":
    output_file_name = "device_speedDialDump.csv"
    with open(filename, mode ='r')as file:
      csvFile = csv.reader(file)
      deviceList = []
      for lines in csvFile:
        deviceName = lines[0]
        response = fetchSpeedDialFromPhone(cucm,user,password,version,deviceName)
        if response.status_code == 200:
          response = response.text
          deviceList+=parseXmlResponse(response,deviceName)
        else:
          print("Speed dial fetch failed for ", deviceName)

  elif deviceType.upper() == "DP":
    output_file_name = "devicepool_speedDialDump.csv"
    with open(filename, mode ='r')as file:
      csvFile = csv.reader(file)
      deviceList = []
      for lines in csvFile:
        deviceName = lines[0]
        response = fetchSpeedDialFromDeviceProfile(cucm,user,password,version,deviceName)
        if response.status_code == 200:
          response = response.text
          deviceList+=parseXmlResponse(response,deviceName)
        else:
          print("Speed dial fetch failed for ", deviceName)

  if len(deviceList)>0:
    writeToCsv(output_file_name,deviceList)
    return ("Speed Dial info fetched successfully from ",cucm," for ",deviceType,".Please view ",output_file_name," for details")
  else:
    return ("No Speed Dial information was fetched")
  
def updateSpeedDialDevice(cucm,user,password,deviceName,speedDialPayload):
  session = Session()
  session.verify = False
  urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )
  session.auth = HTTPBasicAuth(user,password)
  transport = Transport( session = session, timeout = 10 )
  settings = Settings( strict = False, xml_huge_tree = True )
  plugin = []
  client = Client( WSDL_FILE, settings = settings, transport = transport,plugins = plugin )

  service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                'https://'+cucm+':8443/axl/' )
  speedDialList = speedDialPayload['speeddials']
  try:
    resp = service.updatePhone( name = deviceName, speeddials= speedDialList)
  except : 
    resp = "Error in updating speedDials for "+deviceName

  return resp

def updateSpeedDialDeviceProfile(cucm,user,password,deviceName,speedDialPayload):
  session = Session()
  session.verify = False
  urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )
  session.auth = HTTPBasicAuth(user,password)
  transport = Transport( session = session, timeout = 10 )
  settings = Settings( strict = False, xml_huge_tree = True )
  plugin = []
  client = Client( WSDL_FILE, settings = settings, transport = transport,plugins = plugin )

  service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                'https://'+cucm+':8443/axl/' )
  speedDialList = speedDialPayload['speeddials']
  try:
    resp = service.updateDeviceProfile( name = deviceName, speeddials= speedDialList)
  except : 
    resp = "Error in updating speedDials for "+deviceName

  return resp

def convertDftojson(filename):
  df = pd.read_csv(filename, names=("deviceName","dirn","index", "label"),skiprows=[0])
  inputDeviceData = df.to_dict(orient='records')
  uniqueDeviceList = list(set([eachDevice["deviceName"] for eachDevice in inputDeviceData]))
  mappedList = []
  for eachDevice in uniqueDeviceList:
    deviceDict = {}
    speedDialsDict = {}
    speedDialList = []
    for eachDeviceDict in inputDeviceData:
      speedDialDict = {}
      if eachDeviceDict['deviceName'] == eachDevice:
        speedDialDict.update({
                                "dirn": str(eachDeviceDict['dirn']),
                               "label" : str(eachDeviceDict['label']),
                              "index" : str(eachDeviceDict['index']) })
        
        speedDialList.append(speedDialDict)
    speedDialsDict.update({'speeddials':{"speeddial":speedDialList}})
    deviceDict.update({eachDevice:speedDialsDict})
    mappedList.append(deviceDict)
  return mappedList

def convertBatToJson(filename):
  filename = filename
  df = pd.read_csv(filename)
  deviceList = []
  for i in range(len(df)) :
    deviceDict = {}
    deviceName = str(int(df.iloc[i, 0]))
    speedDialsList = []
    speedDialsDict = {}
    col_count = df.shape[1]
    speedDialList = []
    for col in range(1,col_count,2):
      speedDialDict = {}
      if col == 1: 
        index = col
      else:
        index = int((col+1)/2)
      dirn =df.iloc[i, col]
      label = df.iloc[i, col+1]
      if type(dirn) !='str':
        if math.isnan(float(dirn)):
          a=1
        else:
          speedDialDict.update({"index":str(index),"dirn":str(int(dirn)),"label":str(label)})
          speedDialList.append(speedDialDict)
    if len(speedDialList)>0 : 
      deviceDict.update({deviceName:{"speeddials": {"speeddial":speedDialList}}})
      deviceList.append(deviceDict)
  return deviceList

inputPath = input('Enter name of the input json file : ')
with open(inputPath+".json") as inputFile:
    input_json = json.load(inputFile)

cucm = input_json["cucm"]
version = input_json["version"]
user = input_json["user"]
password = input_json["password"]
filename = input_json["inputFile"]
deviceType = input_json["deviceType"]
userChoice = input_json["fetch/update"]
inputType = input_json["inputType"]
WSDL_FILE = 'schema/'+version+'/AXLAPI.wsdl'

if userChoice.lower() == "fetch":
  fetchSpeedDialReport(cucm,user,password,deviceType)

if userChoice.lower() == "update":
  if inputType.lower() == "batexport":
    deviceList= convertBatToJson(filename)
  else:
    deviceList = convertDftojson(filename)
  count=0
  for device in deviceList:
    deviceName = list(device.keys()).pop()
    speedDialPayload = device[deviceName]
    count= count+1
    if deviceType.lower() == "device":
      try:
        response = updateSpeedDialDevice(cucm,user,password,deviceName,speedDialPayload)
        print(response)
        print("speedDial updated successfully for ",deviceName)
      except:
        print(response)
        print("speedDial could not be updated for ", deviceName)
    elif deviceType.upper() == "DP":
      try:
        response = updateSpeedDialDeviceProfile(cucm,user,password,deviceName,speedDialPayload)
        print("speedDial updated successfully for ",deviceName)
      except:
        print(response)
        print("speedDial could not be updated for ",deviceName)
    
    if count% 300 == 0:
      time.sleep(30)
      count = 0






