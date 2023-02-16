import pandas as pd
import requests
import time
import os
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import json
from threading import Thread
from collections import defaultdict
from bs4 import BeautifulSoup
disable_warnings(InsecureRequestWarning)

RIS_WSDL_FILE = 'schema/RISService70.wsdl'
session = Session()
session.verify = False

inputFile = open("input.json")
inputData = json.load(inputFile)

#Load Pre Data
if os.stat('db/precheck.json').st_size == 0:
    print('The precheck is empty. Diff cannot be run. Executing only precheck')
    diff = "False"
else:
    precheckFile = open('db/precheck.json')
    preDict = json.load(precheckFile)
    diff = "True"


# UCAAS
UCAAS_CUCM = inputData['UCAAS']['cucm']
UCAAS_USERNAME = inputData['UCAAS']['user']
UCAAS_PASSWORD = inputData['UCAAS']['password']
UCAAS_VERSION = inputData['UCAAS']['version']
UCAAS_WSDL = 'schema/'+UCAAS_VERSION+'/AXLAPI.wsdl'

# DI
DI_CUCM = inputData['DI']['cucm']
DI_USERNAME = inputData['DI']['user']
DI_PASSWORD = inputData['DI']['password']
DI_VERSION = inputData['DI']['version']
DI_WSDL = 'schema/'+DI_VERSION+'/AXLAPI.wsdl'


class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def registrationStatus(CUCM,AXL_USERNAME,AXL_PASSWORD,deviceList):
    StateInfo = '' 
    session.auth = HTTPBasicAuth(AXL_USERNAME,AXL_PASSWORD)
    transport = Transport( session = session, timeout = 10 )
    settings = Settings( strict = False, xml_huge_tree = True )
    plugin = []
    client = Client( RIS_WSDL_FILE, settings = settings, transport = transport, plugins = plugin)
    service = client.create_service('{http://schemas.cisco.com/ast/soap}RisBinding',
    'https://'+CUCM+':8443/realtimeservice2/services/RISService70')
    CmSelectionCriteria = {
    'MaxReturnedDevices': '10',
    'DeviceClass': 'Phone',
    'Model': '255',
    'Status': 'Registered',
    'NodeName': '',
    'SelectBy': 'Name',
    'SelectItems': {
        'item': deviceList},
    'Protocol': 'Any',
    'DownloadStatus': 'Any'}
    try:
        resp = service.selectCmDeviceExt(CmSelectionCriteria=CmSelectionCriteria, StateInfo=StateInfo)
    except Fault as err:
        print( f'Zeep error: selectCmDevice: { err }' )
        sys.exit( 1 )

    return (resp['SelectCmDeviceResult']['TotalDevicesFound'])

def devicesInDevicePoolZeep(CUCM,AXL_USERNAME,AXL_PASSWORD,WSDL):
    devicePoolList = []
    session.auth = HTTPBasicAuth( AXL_USERNAME,AXL_PASSWORD )
    transport = Transport( session = session, timeout = 10 )
    settings = Settings( strict = False, xml_huge_tree = True )
    plugin = []
    client = Client( WSDL, settings = settings, transport = transport,plugins = plugin )
    service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                'https://'+CUCM+':8443/axl/' )

    # Create an object containing the raw SQL query to run
    sql = '''select dp.name as devicepool,d.name as device from device d 
            join devicepool dp on d.fkdevicepool=dp.pkid
            where d.tkclass = '1'
            order by dp.name
            '''
    try:
        resp = service.executeSQLQuery( sql )
    except Fault as err:
        print('Zeep error: executeSQLQuery: {err}'.format( err = err ) )
    else:
        print( '\nFetching registered devices based on device pool' )

    def get_column(tag, row):
        element = list(filter(lambda x: x.tag == tag, row))
        return element[0].text if len(element) > 0 else None
    for rowXml in resp[ 'return' ][ 'row' ]:
        devicePool = get_column('devicepool', rowXml)
        deviceName = get_column('device', rowXml)
        devicePoolData = [devicePool,deviceName]
        devicePoolList.append(devicePoolData)

    devicePoolDf = pd.DataFrame(devicePoolList, columns=['DevicePool', 'Device'])
    devicePoolDf = devicePoolDf.groupby('DevicePool')['Device'].apply(list).to_dict()
    return(devicePoolDf)

def devicesInDevicePool(CUCM,AXL_USERNAME,AXL_PASSWORD,VERSION):
    url = "https://"+CUCM+":8443/axl/"
    payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/"+VERSION+"\">\n<soapenv:Header/>\n<soapenv:Body>\n<ns:executeSQLQuery>\n    <sql>select dp.name as devicepool,d.name as device from device d \n            join devicepool dp on d.fkdevicepool=dp.pkid\n            where d.tkclass = '1'\n            order by dp.name</sql>\n</ns:executeSQLQuery>\n</soapenv:Body>\n</soapenv:Envelope>"
    headers = {
    'Content-Type': 'text/xml'
    }
    response = requests.request("POST", url, headers=headers, data=payload,auth=HTTPBasicAuth(AXL_USERNAME,AXL_PASSWORD),verify=False)
    response = response.text

    soup = BeautifulSoup(response, 'xml')
    devicepool = soup.find_all('devicepool')
    deviceName = soup.find_all('device')
    devicePoolList = [eachDP.text for eachDP in devicepool]
    deviceList = [eachDevice.text for eachDevice in deviceName]
    merged_list = [(devicePoolList[i], deviceList[i]) for i in range(0, len(deviceList))]
    devicePoolDeviceMap = defaultdict(list)
    for dp, device in merged_list:
        devicePoolDeviceMap[dp].append(device)
    devicePoolDeviceMap = dict(devicePoolDeviceMap)
    # devicePoolDeviceMapDF = pd.DataFrame.from_dict(devicePoolDeviceMap)
    return(devicePoolDeviceMap)

def fetchDeviceCount(cucmType):
    devicePoolDict = {}
    if cucmType == "UCAAS":
        # UCAAS
        CUCM = UCAAS_CUCM
        AXL_USERNAME = UCAAS_USERNAME
        AXL_PASSWORD = UCAAS_PASSWORD
        WSDL = UCAAS_WSDL
        VERSION = UCAAS_VERSION
        # devicePoolInfo = devicesInDevicePool(CUCM,AXL_USERNAME,AXL_PASSWORD,WSDL)
        devicePoolInfo = devicesInDevicePool(CUCM,AXL_USERNAME,AXL_PASSWORD,VERSION)
    elif cucmType == "DI":
        # DI
        CUCM = DI_CUCM
        AXL_USERNAME = DI_USERNAME
        AXL_PASSWORD = DI_PASSWORD
        WSDL = DI_WSDL
        VERSION = DI_VERSION
        # devicePoolInfo = devicesInDevicePool(CUCM,AXL_USERNAME,AXL_PASSWORD,WSDL)
        devicePoolInfo = devicesInDevicePool(CUCM,AXL_USERNAME,AXL_PASSWORD,VERSION)
    RISRateLimit = 0
    for eachDevicePool in devicePoolInfo:
        devicePoolCount=0
        deviceList = devicePoolInfo[eachDevicePool]
        deviceBatches = [deviceList[i:i+1000] for i in range(0,len(deviceList),1000)]
        for eachBatch in deviceBatches:
            RISRateLimit+=1
            if (RISRateLimit%13) == 0:
                RISRateLimit = 0
                time.sleep(60)
            devicePoolCount += registrationStatus(CUCM,AXL_USERNAME,AXL_PASSWORD,eachBatch)
        devicePoolDict.update({eachDevicePool:devicePoolCount})
    return(devicePoolDict)

def diffReport(preDict,currentDict):
    # validate if any change in devicepool count
    diffList = []
    preCheckDP = list(preDict.keys())
    currentDP = list(currentDict.keys())
    if len(preCheckDP) == len(currentDP):
        for eachDP in currentDP:
            diffDict = {}
            preUCAAS = preDict[eachDP]["UCAAS"]
            preDI = preDict[eachDP]["DI"]
            currentUCAAS = currentDict[eachDP]["UCAAS"]
            currentDI = currentDict[eachDP]["DI"]
            delta = abs(int(preUCAAS)-int(currentUCAAS))
            if (delta == currentDI):
                diffStatus = "Match"
                delta = "N/A"
            else:
                diffStatus = "Mismatch"
                delta = abs(delta-currentDI)
                
            diffDict.update({
                "devicePool":eachDP,
                "preUCAAS" : preUCAAS,
                "preDI":preDI,
                "currentUCAAS":currentUCAAS,
                "currentDI":currentDI,
                "diffStatus": diffStatus,
                "delta" : delta
            })
            diffList.append(diffDict)
    else:
        diffList.append("There has been addition/deletion of device pool since last run")
    return diffList

def generateHTMLFile(responseDF,HTMLfileName):
    html = responseDF.to_html()
    text_file = open(HTMLfileName, "w")
    text_file.write(html)
    text_file.close()

def main():
    UCAAS_thread = ThreadWithReturnValue(target=fetchDeviceCount, args=('UCAAS',))
    DI_thread = ThreadWithReturnValue(target=fetchDeviceCount, args=('DI',))

    UCAAS_thread.start()
    print("Starting to fetch registered phone per for UCAAS")
    DI_thread.start()
    print("Starting to fetch registered phone per for DI")
    UCAAS_dict = UCAAS_thread.join()
    DI_dict = DI_thread.join()

    UCAAS_DP = list(UCAAS_dict.keys())
    DI_DP = list(DI_dict.keys())
    consolidatedDPList = list(set(UCAAS_DP+DI_DP))

    currentDict = {}
    for eachDP in consolidatedDPList:
        eachDPDict = {"UCAAS": 0,
                        "DI": 0}
        if eachDP in UCAAS_DP:
            eachDPDict["UCAAS"]=UCAAS_dict[eachDP]
        if eachDP in DI_DP:
            eachDPDict["DI"]= DI_dict[eachDP]
        currentDict.update({eachDP:eachDPDict})
    print(currentDict)
    if diff == "True":
        diffResponse=diffReport(preDict,currentDict)
        with open('db/diff.json', 'w') as fp:
            json.dump(diffResponse, fp)
        diffDF = pd.DataFrame(diffResponse)
        diffDF = diffDF.sort_values(by = 'diffStatus',ascending = False)
        htmlFile = "templates/diff.html"
        generateHTMLFile(diffDF,htmlFile)
        print("Completed Successfully - view the diff report")

    currentList = []
    for eachDP in currentDict.keys():
        DPdict = {}
        DPdict.update(
            {
                "devicePool": eachDP,
                "UCAAS_count" : currentDict[eachDP]["UCAAS"],
                "DI_count": currentDict[eachDP]["DI"]
            })
        currentList.append(DPdict)
    currentDF = pd.DataFrame(currentList)
    htmlFileName = "templates/post.html"
    generateHTMLFile(currentDF,htmlFileName)

    with open('db/precheck.json', 'w') as fp:
        json.dump(currentDict, fp)
        print("Completed Successfully - view the pre report")

main()


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diff')
def diff():
    return render_template('diff.html')

@app.route("/current")
def current():
    return render_template('post.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=8080)
