from datetime import datetime
import pandas as pd
import paramiko
import time

currentTime = str(datetime.now())
duplicateCerts = []
service_list = []
deleteList = [] 
rootList = []
toRestartServices = []

certServiceMapDict  = {
    "tomcat-trust" : ['Cisco Tomcat'],
    "CallManager-trust" : ['Cisco CallManager','Cisco Tftp','Cisco CTIManager'],
    "CAPF-trust": ['Cisco Certificate Authority Proxy Function'],
    "TVS-trust": ['Cisco Trust Verification Service'],
    "ipsec-trust" : ['Cisco DRF Local','Cisco DRF Local']
}

# --Accepting user inputs----------------
cert_out = input("Enter the filename : ")


host = input("Enter the IP address : ")
username = input("Enter the username : ")
password = input("Enter the password : ")
output_path = cert_out+"_cli"+currentTime+".xlsx"
root_path = cert_out+"_root"+currentTime+".xlsx"

remote_conn_pre = paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(host, username=username, password=password, look_for_keys=False, allow_agent=False)
remote_conn = remote_conn_pre.invoke_shell()
remote_conn.send('\n')

df = pd.read_excel(cert_out+'.xlsx', sheet_name=host)
certNames = df["name"]
duplicated = df[certNames.isin(certNames[certNames.duplicated()])].sort_values("name")

for i in range(len(df)) :
    certType = df.loc[i, "type"]
    isExpired = df.loc[i,"hasExpired"]
    if certType == "TrustCertificate" and isExpired:
        deleteDict = {}
        rootDict = {}
        needRootAccess = None
        deleteStatus = None
        serialNumber = None
        
        serviceName =df.loc[i, "service"]
        certName = df.loc[i, "name"]
        serialNumber = df.loc[i, "serialNumber"]

        if duplicated['name'].str.contains(certName).any():
            duplicateCerts.append(certName)
            needRootAccess = "true"
            deleteStatus = "skipped"
            print("Certificate deletion skipped for ",certName , ' as it has duplicate name')
            rootDict = {
            "certificateName" : certName,
            "serialNumber" : serialNumber,
            "serviceName":serviceName,
            "deleteStatus" : deleteStatus,
            "needRootAccess" : needRootAccess}
            rootList.append(rootDict)
        else:
            print("Deleting certificate : ",certName)
            service_list.append(serviceName)
            try: 
                command = 'set cert delete '+serviceName+' ' + certName+ '\n'
                print(command)
                remote_conn.send(command)
                time.sleep(20)
                deleteCert = remote_conn.recv(50000)
                deleteCert = deleteCert.decode()
                deleteCert = deleteCert.split("\r\n")
                print("Certificate deletion successful for ",certName)
                deleteStatus = "sucess"
                needRootAccess = "false"
            except: 
                print("Certificate deletion failed for ",certName)
                deleteStatus = "failure"
                needRootAccess = "false"
            deleteDict = {
                "certificateName" : certName,
                "serialNumber" : serialNumber,
                "serviceName":serviceName,
                "deleteStatus" : deleteStatus,
                "needRootAccess" : needRootAccess,
            }
            deleteList.append(deleteDict)

delete_df = pd.DataFrame(deleteList)    

if(len(delete_df) > 0):
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        delete_df.to_excel(writer, sheet_name=host)

if len(rootList) >0 : 
    rootDeleteDict = {}
    rootUser = input("Enter root username for the server : "+ host)
    rootPassword = input("Enter root password for the server : "+host)
    remote_conn_pre = paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_conn_pre.connect(host, username=rootUser, password=rootPassword, look_for_keys=False, allow_agent=False)
    remote_conn = remote_conn_pre.invoke_shell()
    remote_conn.send('\n')
    for eachRootCert in rootList:
        try: 
            serialNumber = eachRootCert['serialNumber']
            serviceName = eachRootCert['serviceName']
            command = 'delete from certificate where serialnumber = '+ serialNumber+ '\n'
            remote_conn.send(command)
            time.sleep(20)
            deleteCert = remote_conn.recv(50000)
            deleteCert = deleteCert.decode()
            deleteCert = deleteCert.split("\r\n")
            deleteStatus = 'success'
            service_list.append(serviceName)
        except:
            deleteStatus = 'failure'
        eachRootCert['deleteStatus'] = deleteStatus
    root_df = pd.DataFrame(rootList)     
    if(len(root_df)>0):
        with pd.ExcelWriter(root_path, engine='xlsxwriter') as writer:
            root_df.to_excel(writer, sheet_name=host)


# After deleting a service certificate, service needs to be restarted
unique_service_list = set(service_list)

for eachService in unique_service_list:
    servicesToBeRestarted = certServiceMapDict[eachService]
    if eachService == 'tomcat-trust' or eachService == 'ipsec-trust' :
       for eachRestartService in servicesToBeRestarted:
            try: 
               command = 'utils service restart '+ eachRestartService + '\n'
               remote_conn.send(command)
               time.sleep(40)
               print(eachRestartService, " restarted successfully from CLI")
            except:
                print("Error in restarting service ", eachRestartService)
    else :
        toRestartServices = toRestartServices+servicesToBeRestarted

print("Please restart these services from GUI for changes to reflect : ", toRestartServices)
