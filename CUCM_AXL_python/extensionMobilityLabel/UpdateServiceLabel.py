import requests
from urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import csv
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

cucm = input("Enter CUCM IP address : ")
user = input("Enter CUCM username : ")
password = input("Enter CUCM password : ")
filename = input("Enter input filename(with.csv) : ")
url = "https://"+cucm+":8443/axl/"
serviceLabel = "Extension Mobility"
print("deviceName, serviceIndex, labelUpdateStatus")
with open(filename, mode ='r')as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
        deviceName = lines[0]
        serviceIndex=lines[1]
        payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/12.5\">\n<soapenv:Header/>\n<soapenv:Body>\n<ns:updatePhone>\n    <name>"+deviceName+"</name>\n    <services>\n        <service>\n            <telecasterServiceName>Extension Mobility</telecasterServiceName>\n            <urlButtonIndex>"+serviceIndex+"</urlButtonIndex>\n            <name>Extension Mobility</name>\n            <urlLabel>"+serviceLabel+"</urlLabel>\n        </service>\n    </services>\n</ns:updatePhone>\n</soapenv:Body>\n</soapenv:Envelope>"
        headers = {'Content-Type': 'text/xml'}
        response = requests.request("POST", url, headers=headers, data=payload,auth=HTTPBasicAuth(user,password),verify=False)
        if(response.status_code == 200):
            print(deviceName,serviceIndex,"SUCCESS")
        else:
            print(deviceName,serviceIndex,"FAILURE")
