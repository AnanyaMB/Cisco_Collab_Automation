import requests
from urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import csv
import bs4 as bs


# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

cucm = input("Enter CUCM IP address : ")
user = input("Enter CUCM username : ")
password = input("Enter CUCM password : ")
filename = input("Enter input filename(with.csv) : ")

with open(filename, mode ='r')as file:
  csvFile = csv.reader(file)
  deviceList = []
  for lines in csvFile:
        url = "https://"+cucm+":8443/axl/"
        deviceName = lines[0]
        payload = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\">\n<soapenv:Header/>\n<soapenv:Body>\n<ns:getPhone>\n    <name>"+deviceName+"</name>\n</ns:getPhone>\n</soapenv:Body>\n</soapenv:Envelope>"
        headers = {'Content-Type': 'text/xml'}
        response = requests.request("POST", url, headers=headers, data=payload,auth=HTTPBasicAuth(user,password),verify=False)
        response = response.text
        # response = "<?xml version='1.0' encoding='UTF-8'?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><ns:getPhoneResponse xmlns:ns="http://www.cisco.com/AXL/API/10.5"><return><phone ctiid="1137" uuid="{0B149639-2E49-0A08-5437-A3E858022FF1}"><name>SEP000000000028</name><description>AZCDRBD - Conference phone</description><product>Cisco 8831</product><model>Cisco 8831</model><class>Phone</class><protocol>SIP</protocol><protocolSide>User</protocolSide><callingSearchSpaceName/><devicePoolName uuid="{ED8F55F5-6B23-4364-9224-703AAE0CDAE3}">AZ01_21_DP</devicePoolName><commonDeviceConfigName uuid="{49128DF0-9615-4D1A-9D4B-EFB3B8EE50E3}">IPTWTE1_Sites_CP</commonDeviceConfigName><commonPhoneConfigName uuid="{AC243D17-98B4-4118-8FEB-5FF2E1B781AC}">Standard Common Phone Profile</commonPhoneConfigName><networkLocation>Use System Default</networkLocation><locationName uuid="{3A14476D-C6CB-CB9C-CFA2-69DAEB261749}">AZ01_LOC</locationName><mediaResourceListName uuid="{03109E45-C7D5-6F37-A7EF-B2DC3440DEC5}">AZ01_56_MRGL</mediaResourceListName><networkHoldMohAudioSourceId /><userHoldMohAudioSourceId /><automatedAlternateRoutingCssName uuid="{05FE0A85-CE50-1E12-CC04-D0E7D604FF04}">AZ01_Device_CSS</automatedAlternateRoutingCssName><aarNeighborhoodName/><loadInformation special="false">sip8831.10-3-1SR6-4</loadInformation><vendorConfig><garp>1</garp><recordingTone>0</recordingTone><recordingToneLocalVolume>100</recordingToneLocalVolume><recordingToneRemoteVolume>50</recordingToneRemoteVolume><moreKeyReversionTimer>5</moreKeyReversionTimer><g722CodecSupport>0</g722CodecSupport><powerPriority>0</powerPriority><displayRefreshRate>0</displayRefreshRate><useEnblocDialing>1</useEnblocDialing></vendorConfig><versionStamp>{1680793930-318B7ADF-B5A3-4A4B-8402-AC71168743EA}</versionStamp><traceFlag>false</traceFlag><mlppDomainId /><mlppIndicationStatus>Off</mlppIndicationStatus><preemption>Disabled</preemption><useTrustedRelayPoint>Default</useTrustedRelayPoint><retryVideoCallAsAudio>true</retryVideoCallAsAudio><securityProfileName uuid="{2FB96225-04C3-48AF-8FC7-888F8DF3F483}">Cisco 8831 - Standard SIP Non-Secure Profile</securityProfileName><sipProfileName uuid="{FCBC7581-4D8D-48F3-917E-00B09FB39213}">Standard SIP Profile</sipProfileName><cgpnTransformationCssName/><useDevicePoolCgpnTransformCss>true</useDevicePoolCgpnTransformCss><geoLocationName/><geoLocationFilterName/><sendGeoLocation>false</sendGeoLocation><lines><line uuid="{F1BD95EC-BC7F-825C-4486-1617A0FE1297}"><index>1</index><label/><display>Conference Phone</display><dirn uuid="{D9A3CDCF-2033-87E1-8E36-A9BA2C3E7CA6}"><pattern>6024641171</pattern><routePartitionName uuid="{B8B08116-6611-E789-91DF-088C6E3F8EF9}">IPTWTE1_Global_Phones_PT</routePartitionName></dirn><ringSetting>Use System Default</ringSetting><consecutiveRingSetting>Use System Default</consecutiveRingSetting><ringSettingIdlePickupAlert>Use System Default</ringSettingIdlePickupAlert><ringSettingActivePickupAlert>Use System Default</ringSettingActivePickupAlert><displayAscii>Conference Phone</displayAscii><e164Mask>6024641171</e164Mask><dialPlanWizardId /><mwlPolicy>Use System Policy</mwlPolicy><maxNumCalls>2</maxNumCalls><busyTrigger>1</busyTrigger><callInfoDisplay><callerName>true</callerName><callerNumber>false</callerNumber><redirectedNumber>false</redirectedNumber><dialedNumber>true</dialedNumber></callInfoDisplay><recordingProfileName/><monitoringCssName/><recordingFlag>Call Recording Disabled</recordingFlag><audibleMwi>Default</audibleMwi><speedDial /><partitionUsage>General</partitionUsage><associatedEndusers/><missedCallLogging>true</missedCallLogging><recordingMediaSource>Gateway Preferred</recordingMediaSource></line></lines><numberOfButtons>12</numberOfButtons><phoneTemplateName uuid="{D5A665B3-15C1-4104-9E46-8DC23B1B183B}">Standard 8831 SIP</phoneTemplateName><speeddials><speeddial><dirn>1</dirn><label>test1</label><index>1</index></speeddial><speeddial><dirn>2</dirn><label>test2</label><index>2</index></speeddial></speeddials><busyLampFields/><primaryPhoneName/><ringSettingIdleBlfAudibleAlert>Default</ringSettingIdleBlfAudibleAlert><ringSettingBusyBlfAudibleAlert>Default</ringSettingBusyBlfAudibleAlert><blfDirectedCallParks/><addOnModules/><userLocale /><networkLocale /><idleTimeout /><authenticationUrl/><directoryUrl>test</directoryUrl><idleUrl/><informationUrl>test</informationUrl><messagesUrl/><proxyServerUrl/><servicesUrl/><services/><softkeyTemplateName/><loginUserId /><defaultProfileName/><enableExtensionMobility>false</enableExtensionMobility><currentProfileName/><loginTime /><loginDuration /><currentConfig><userHoldMohAudioSourceId /><phoneTemplateName uuid="{D5A665B3-15C1-4104-9E46-8DC23B1B183B}">Standard 8831 SIP</phoneTemplateName><mlppDomainId /><mlppIndicationStatus>Off</mlppIndicationStatus><preemption>Disabled</preemption><softkeyTemplateName/><ignorePresentationIndicators>false</ignorePresentationIndicators><singleButtonBarge>Off</singleButtonBarge><joinAcrossLines>Off</joinAcrossLines><callInfoPrivacyStatus>Default</callInfoPrivacyStatus><dndStatus /><dndRingSetting /><dndOption>Ringer Off</dndOption><alwaysUsePrimeLine>Default</alwaysUsePrimeLine><alwaysUsePrimeLineForVoiceMessage>Default</alwaysUsePrimeLineForVoiceMessage><emccCallingSearchSpaceName xsi:nil="true" uuid="" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/><deviceName/><model/><product/><deviceProtocol/><class/><addressMode/><allowAutoConfig/><remoteSrstOption/><remoteSrstIp/><remoteSrstPort/><remoteSipSrstIp/><remoteSipSrstPort/><geolocationInfo/><remoteLocationName/></currentConfig><singleButtonBarge>Off</singleButtonBarge><joinAcrossLines>Off</joinAcrossLines><builtInBridgeStatus>Default</builtInBridgeStatus><callInfoPrivacyStatus>Default</callInfoPrivacyStatus><hlogStatus>On</hlogStatus><ownerUserName/><ignorePresentationIndicators>false</ignorePresentationIndicators><packetCaptureMode>None</packetCaptureMode><packetCaptureDuration>0</packetCaptureDuration><subscribeCallingSearchSpaceName/><rerouteCallingSearchSpaceName/><allowCtiControlFlag>true</allowCtiControlFlag><presenceGroupName uuid="{AD243D17-98B4-4118-8FEB-5FF2E1B781AC}">Standard Presence group</presenceGroupName><unattendedPort>false</unattendedPort><requireDtmfReception>false</requireDtmfReception><rfc2833Disabled>false</rfc2833Disabled><certificateOperation>No Pending Operation</certificateOperation><certificateStatus>None</certificateStatus><upgradeFinishTime /><deviceMobilityMode>Default</deviceMobilityMode><remoteDevice>false</remoteDevice><dndOption>Ringer Off</dndOption><dndRingSetting /><dndStatus>false</dndStatus><isActive>true</isActive><isDualMode>false</isDualMode><mobilityUserIdName/><phoneSuite>Default</phoneSuite><phoneServiceDisplay>Default</phoneServiceDisplay><isProtected>false</isProtected><mtpRequired>false</mtpRequired><mtpPreferedCodec>711ulaw</mtpPreferedCodec><dialRulesName/><sshUserId/><digestUser/><outboundCallRollover>No Rollover</outboundCallRollover><hotlineDevice>false</hotlineDevice><secureInformationUrl/><secureDirectoryUrl/><secureMessageUrl/><secureServicesUrl/><secureAuthenticationUrl/><secureIdleUrl/><alwaysUsePrimeLine>Default</alwaysUsePrimeLine><alwaysUsePrimeLineForVoiceMessage>Default</alwaysUsePrimeLineForVoiceMessage><featureControlPolicy/><deviceTrustMode>Not Trusted</deviceTrustMode><confidentialAccess><confidentialAccessMode /><confidentialAccessLevel>-1</confidentialAccessLevel></confidentialAccess><cgpnIngressDN/><useDevicePoolCgpnIngressDN>true</useDevicePoolCgpnIngressDN><msisdn /><enableCallRoutingToRdWhenNoneIsActive>false</enableCallRoutingToRdWhenNoneIsActive><wifiHotspotProfile/><wirelessLanProfileGroup/></phone></return></ns:getPhoneResponse></soapenv:Body></soapenv:Envelope>"
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
        deviceList+=speedDialList


with open("speedDial_dump.csv", "w") as f:
    wr = csv.DictWriter(f, delimiter=",",fieldnames=list(deviceList[0].keys()))
    wr.writeheader()
    wr.writerows(deviceList)




       

