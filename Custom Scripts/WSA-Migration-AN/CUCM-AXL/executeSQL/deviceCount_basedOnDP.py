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


sql = '''select np.dnorpattern as pattern, NVL(rp.name, '') as routePartitionName, dnm.numplanindex as numplanindex, 
dnm.busytrigger as busyTrigger, NVL(dnm.display, '') as display,
 NVL(dnm.displayascii, '') as displayAscii, NVL(dnm.e164mask,'') as e164Mask, NVL(dnm.label,'') as label, dnm.maxnumcalls as maxNumCalls, NVL(r.name, '') as recordingProfileName,tpms.name as recordingMediaSource, trf.name as recordingFlag, css.name as monitoringCssName from devicenumplanmap dnm 
 left join device d on d.pkid=dnm.fkdevice left join numplan np on np.pkid=dnm.fknumplan left join routepartition rp on np.fkroutepartition=rp.pkid left join recordingprofile r on r.pkid=dnm.fkrecordingprofile left join typemwlpolicy tmp on tmp.enum=dnm.tkmwlpolicy left join typepartitionusage tpu on tpu.enum=dnm.tkpartitionusage left join typepreferredmediasource tpms on tpms.enum=dnm.tkpreferredmediasource left join typeringsetting trs on trs.enum=dnm.tkringsetting left join typeringsetting trsc on trsc.enum=dnm.tkringsetting_consecutive left join typeringsetting trsipa on trsipa.enum=dnm.tkringsetting_idlepickupalert left join typeringsetting trsapa on trsapa.enum=dnm.tkringsetting_activepickupalert left join typestatus ts on ts.enum=dnm.tkstatus_audiblemwi left join recordingdynamic rd on dnm.pkid=rd.fkdevicenumplanmap left join typerecordingflag trf on trf.enum=rd.tkrecordingflag left join callingsearchspace css on css.pkid = dnm.fkcallingsearchspace_monitoring where UPPER(d.name) = 'SEPAA00AB48515D' AND d.tkclass IN (1,254) AND dnm.tkpartitionusage = '99' AND dnm.numplanindex <= 8 order by dnm.numplanindex'''
        
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
    pattern = get_column('pattern', rowXml)
    routePartitionName = get_column('routePartitionName', rowXml)
    numplanindex = get_column('numplanindex', rowXml)

    devicePoolData = [pattern,routePartitionName,numplanindex]
    devicePoolList.append(devicePoolData)


devicePoolDf = pd.DataFrame(devicePoolList, columns=[pattern,routePartitionName,numplanindex])
print(devicePoolDf)
# devicePoolDf.to_excel("output.xlsx",index=False)