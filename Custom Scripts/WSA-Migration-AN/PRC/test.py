import requests
from urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from collections import defaultdict
# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)



user = "axltest"
password = "axltest"
cucm = "10.105.60.95"
url = "https://"+cucm+":8443/axl/"

payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/14.0\">\n<soapenv:Header/>\n<soapenv:Body>\n<ns:executeSQLQuery>\n    <sql>select dp.name as devicepool,d.name as device from device d \n            join devicepool dp on d.fkdevicepool=dp.pkid\n            where d.tkclass = '1'\n            order by dp.name</sql>\n</ns:executeSQLQuery>\n</soapenv:Body>\n</soapenv:Envelope>"
headers = {
  'Content-Type': 'text/xml'
}


response = requests.request("POST", url, headers=headers, data=payload,auth=HTTPBasicAuth(user,password),verify=False)
response= response.text


soup = BeautifulSoup(response, 'xml')
devicepool = soup.find_all('devicepool')
deviceName = soup.find_all('device')
devicePoolList = [eachDP.text for eachDP in devicepool]
deviceList = [eachDevice.text for eachDevice in deviceName]
merged_list = [(devicePoolList[i], deviceList[i]) for i in range(0, len(deviceList))]

devicePoolDeviceMap = defaultdict(list)
for dp, device in merged_list:
    devicePoolDeviceMap[dp].append(device)

print(devicePoolDeviceMap)

    
