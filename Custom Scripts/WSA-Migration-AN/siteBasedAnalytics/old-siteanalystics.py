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
            

huntPilotList = []
huntList = []
for i in range(len(huntDf)):
    huntDict = {}
    huntPilot = str(huntDf.loc[i, "Hunt Pilot"])
    lineMembers = huntDf[huntDf['Hunt Pilot']==huntPilot]['DN']
    if "\+" in huntPilot:
        huntPilot = str(huntPilot)[2:]
    huntPilotList.append(huntPilot)
    huntDict[huntPilot]=list(set(lineMembers.values.tolist()))
    huntDict[huntPilot]=lineMembers.values.tolist()
    huntList.append(huntDict)

huntList = [i for n, i in enumerate(huntList) if i not in huntList[n + 1:]]
huntPilotListUnique = list(set(huntPilotList))



mapList = []
for eachSiteDict in siteList:
    huntPilotRange = [e for e in huntPilotListUnique if eachSiteDict['startRange'] <= e <= eachSiteDict['endRange'] and str(e) != 'nan' ]
    # huntPilotRange = [e for e in huntPilotList if eachSiteDict['startRange'] <= e <= eachSiteDict['endRange'] and str(e) != 'nan' ]
    eachSiteDict.update({"huntPilots": huntPilotRange})
    mapList.append(eachSiteDict)

result = []
for eachMap in mapList:
    mapDict = {}
    huntPilotList = eachMap['huntPilots']
    if huntPilotList != []:
        huntDictList = []
        for eachHP in huntPilotList:
            lineMembers = [d.get(eachHP, None) for d in huntList]
            lineMembers = [i for i in lineMembers if i is not None]
            nonelineMembers = [i for i in lineMembers if i is None]
            lineMembers = flatten(lineMembers)
            lineMembers = [str(i)[2:] if '\\+' in str(i) else str(i) for i in lineMembers]
            for eachLine in lineMembers:
                huntDict = {}
                if eachMap['startRange'] <= eachLine <= eachMap['endRange']:
                    rangeStatus = "In Range"
                else:
                    rangeStatus = "Out of Range"
                huntDict.update({
                        "siteId" : eachMap['siteId'],
                        "startRange" : eachMap['startRange'],
                        "endRange" : eachMap['endRange'],
                        "huntPilot" : eachHP,
                        "DN": eachLine,
                        "rangeStatus" : rangeStatus})
            if nonelineMembers != []:
                for eachLine in nonelineMembers:
                    huntDict = {}
                    huntDict.update({
                            "siteId" : eachMap['siteId'],
                            "startRange" : eachMap['startRange'],
                            "endRange" : eachMap['endRange'],
                            "huntPilot" : eachHP,
                            "DN": "",
                            "rangeStatus" : "N/A"})

            huntDictList.append(huntDict)
        result+=huntDictList
    else : 
        mapDict.update({
                        "siteId" : eachMap['siteId'],
                        "startRange" : eachMap['startRange'],
                        "endRange" : eachMap['endRange'],
                        "huntPilot" : "",
                        "DN": "",
                        "rangeStatus" : "N/A"})
        result.append(mapDict)

huntDf = pd.DataFrame(result, columns=['siteId', 'startRange','endRange','huntPilot','DN','rangeStatus'])
huntDf.to_excel("hunt-output.xlsx",index=False)

    