from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault
import json
import pandas as pd


disable_warnings(InsecureRequestWarning)


session = Session()
session.verify = False

inputFile = open("input.json")
inputData = json.load(inputFile)

cucm = inputData['cucm']
user = inputData['user']
password = inputData['password']
version = inputData['version']
WSDL = 'schema/'+version+'/AXLAPI.wsdl'
RIS_WSDL_FILE = 'schema/RISService70.wsdl'



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
    'Status': 'Any',
    'NodeName': '',
    'SelectBy': 'Name',
    'SelectItems': {
        'item': deviceList
    },
    'Protocol': 'Any',
    'DownloadStatus': 'Any'
}
    try:
        resp = service.selectCmDeviceExt(CmSelectionCriteria=CmSelectionCriteria, StateInfo=StateInfo)
    except Fault as err:
        print( f'Zeep error: selectCmDevice: { err }' )
        sys.exit( 1 )

    return (resp['SelectCmDeviceResult']['TotalDevicesFound'])

def devicesInDevicePool(CUCM,AXL_USERNAME,AXL_PASSWORD,WSDL):
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


devicePoolInfo = devicesInDevicePool(cucm,user,password,WSDL)
devicePoolList = []
for eachDevicePool in devicePoolInfo:
    devicePoolDict = {}
    devicePoolCount=0
    deviceList = devicePoolInfo[eachDevicePool]
    deviceBatches = [deviceList[i:i+1000] for i in range(0,len(deviceList),1000)]
    for eachBatch in deviceBatches:
        devicePoolCount += registrationStatus(cucm,user,password,eachBatch)
    devicePoolDict.update({"devicePoolName":eachDevicePool,
                            "totalCount" : len(deviceList),
                            "registeredDevicesCount":devicePoolCount})
    devicePoolList.append(devicePoolDict)

devicePoolDf = pd.DataFrame(devicePoolList, columns=['devicePoolName', 'totalCount','registeredDevicesCount'])
devicePoolDf.to_excel("output.xlsx",index=False)


