import pandas as pd
import json
from operator import itemgetter
import itertools

def flatten(list_of_lists):
    return list(itertools.chain.from_iterable(list_of_lists))

# inputFile = input("Enter input excel file name : ")
inputFile = 'site-input.xlsx'
siteDetailSheet = 'Sheet1'
huntPilotDetailSheet = 'Sheet2'

siteDf = pd.read_excel(open(inputFile, 'rb'),sheet_name=siteDetailSheet)
huntDf = pd.read_excel(open(inputFile, 'rb'),sheet_name=huntPilotDetailSheet)

siteList = []
for i in range(len(siteDf)):
    siteId = siteDf.loc[i, "6 Digit Site ID"]
    ddiRangeList = (siteDf.loc[i, "DDI RANGE"])
    siteDict = {}
    if type(ddiRangeList) == str:
        if ";" in ddiRangeList:
            ddiRanges = [ddiRangeList.split(";")[0],ddiRangeList.split(";")[1]]
            for eachDdiRange in ddiRanges:
                
                startRange = eachDdiRange.split("-")[0]
                endRange = eachDdiRange.split("-")[1]
                siteDict.update({
                        "siteId" : siteId,
                        "startRange": startRange,
                        "endRange": endRange
                    })
                siteList.append(siteDict)
        else:
            startRange = ddiRangeList.split("-")[0]
            endRange = ddiRangeList.split("-")[1]
            siteDict.update({
                        "siteId" : siteId,
                        "startRange": startRange,
                        "endRange": endRange
                    })
            siteList.append(siteDict)

# print(len(siteList))
# site mapping output matched
            
huntList = []
huntPilotList = []
for i in range(len(huntDf)):
    huntDict = {}
    huntPilot = str(huntDf.loc[i, "Hunt Pilot"])
    DN = str(huntDf.loc[i, "DN"])
    if "\+" in huntPilot:
        huntPilot = str(huntPilot)[2:]
    if "\\+" in DN:
        DN = str(DN)[2:]
    huntDict['huntPilot'] = huntPilot
    huntDict['DN'] = DN
    huntList.append(huntDict)
    huntPilotList.append(huntPilot)


# print(len(huntList))
# Length of hunt validated

result1 = []
huntPilotInRange = []
for eachHuntDict in huntList:
    for eachSiteDict in siteList:
        siteHuntMap = {}
        dnRangeMatch = "N/A"
        if eachSiteDict['startRange'] <= eachHuntDict['huntPilot'] <= eachSiteDict['endRange']:
            huntPilotInRange.append(eachHuntDict['huntPilot'])
            if eachSiteDict['startRange'] <= eachHuntDict['DN'] <= eachSiteDict['endRange']:
                dnRangeMatch = "In Range"
            else:
                dnRangeMatch = "Out of Range"

            siteHuntMap.update({
                    "siteId" : eachSiteDict['siteId'],
                    "startRange" : eachSiteDict['startRange'],
                    "endRange" : eachSiteDict['endRange'],
                    "huntPilot" : eachHuntDict['huntPilot'],
                    "DN" : eachHuntDict['DN'],
                    "match" : dnRangeMatch})
        if siteHuntMap != {}:
            result1.append(siteHuntMap)

huntPilotNotInRange = list(set(huntPilotList) - set(huntPilotInRange))

result2 = []
for eachHPDict in huntList:
    if eachHPDict['huntPilot'] in huntPilotNotInRange:
        siteHuntMap = {
                        "siteId" : "",
                        "startRange" : "",
                        "endRange" : "",
                        "huntPilot" : eachHPDict['huntPilot'],
                        "DN" : eachHPDict['DN'],
                        "match" : ""}
        result2.append(siteHuntMap)

result = result1+result2
result = [i for n, i in enumerate(result) if i not in result[n + 1:]]
huntDf = pd.DataFrame(result, columns=['siteId', 'startRange','endRange','huntPilot','DN','match'])
huntDf.to_excel("site-output.xlsx",index=False)