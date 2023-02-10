#!/usr/bin/env python3

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

userLoginList = []
# Create an object containing the raw SQL query to run
sql = '''select eu.userid as userid, emd.logintime as loginTime, emd.loginduration as loginDuration, emd.datetimestamp as datetimestamp from extensionmobilitydynamic emd 
	inner join enduser eu on emd.fkenduser_lastlogin=eu.pkid'''
		
try:
	resp = service.executeSQLQuery( sql )
except Fault as err:
	print('Zeep error: executeSQLQuery: {err}'.format( err = err ) )
else:
	print( '\nFetching enduser login information' )
	
	
def get_column(tag, row):
	element = list(filter(lambda x: x.tag == tag, row))
	return element[0].text if len(element) > 0 else None
for rowXml in resp[ 'return' ][ 'row' ]:
	userid = get_column('userid', rowXml)
	loginTime = get_column('loginTime', rowXml)
	loginDuration = get_column('loginDuration', rowXml)
	datetimestamp = get_column('datetimestamp', rowXml)
	
	userLoginData = [userid,loginTime,loginDuration,datetimestamp]
	userLoginList.append(userLoginData)
	
userDf = pd.DataFrame(userLoginList, columns=['userid','loginTime','loginDuration','datetimestamp'])
userDf.to_excel("user-login-output.xlsx",index=False)