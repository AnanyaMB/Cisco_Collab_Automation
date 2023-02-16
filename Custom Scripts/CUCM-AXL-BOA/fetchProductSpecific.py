from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault
import pandas as pd

cucm = input("Enter the ip/hostname of CUCM : ")
user = input("Enter the AXL username : ")
password = input("Enter the AXL password : ")
version = input("Enter the version of CUCM (upto one decimal place) : ")

session = Session()
session.verify = False
WSDL = 'schema/'+version+'/AXLAPI.wsdl'

session.auth = HTTPBasicAuth(user,password )
transport = Transport( session = session, timeout = 10 )
settings = Settings( strict = False, xml_huge_tree = True )
plugin = []
client = Client( WSDL, settings = settings, transport = transport,plugins = plugin )
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                            'https://'+cucm+':8443/axl/' )

devicePoolList = []
# Create an object containing the raw SQL query to run
# sql = ''' select dp.name as devicepool,count(d.name) as phonecount 
#         from device d join devicepool dp on d.fkdevicepool= dp.pkid 
#         where d.tkclass = 1 
#         group by dp.name
#         '''


sql = '''select data::bson::json::lvarchar(32000) as data, d.name from devicejson join device d on d.pkid=devicejson.fkdevice'''

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
    device = get_column('device', rowXml)
    productInfo = get_column('productInfo', rowXml)

    devicePoolData = [device,productInfo]
    devicePoolList.append(devicePoolData)

print(devicePoolList)

# devicePoolDf = pd.DataFrame(devicePoolList, columns=[pattern,routePartitionName,numplanindex])
# print(devicePoolDf)
# # devicePoolDf.to_excel("output.xlsx",index=False)