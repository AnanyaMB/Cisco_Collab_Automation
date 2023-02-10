from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault
import sys
import urllib3
import csv
import time

INPUT_FILE = input("Enter input file name(include.csv) : ")
CUCM_ADDRESS = input("Enter CUCM IP address/hostname : ")
AXL_USERNAME = input("AXL username : ")
AXL_PASSWORD = input("AXL password : ")
CUCM_VERSION = input("CUCM Version :")

# The WSDL is a local file in the working directory, see README
WSDL_FILE = 'schema/'+CUCM_VERSION+'/AXLAPI.wsdl'
        
# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the line below

# session.verify = 'changeme.pem'

# Add Basic Auth credentials
session.auth = HTTPBasicAuth( AXL_USERNAME,AXL_PASSWORD )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport)

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding','https://'+CUCM_ADDRESS+':8443/axl/' )

AXL_COUNTER = 0
# opening the CSV file
with open(INPUT_FILE, mode ='r')as file:
  # reading the CSV file
    csvFile = csv.reader(file)

# displaying the contents of the CSV file
    for users in csvFile:
        OLD_NAME = str(users[0])
        NEW_NAME = str(users[1])
        # Execute the updatePhone request
        try:
            AXL_COUNTER += 1
            resp = service.updatePhone(name = OLD_NAME, newName = NEW_NAME)
            if AXL_COUNTER % 1200 == 0:
                time.sleep(60)

        except Fault as err:
            print( f'Zeep error: updateDevice: { err }' )
            sys.exit( 1 )

        print(OLD_NAME+ " Updated to "+ NEW_NAME) 