import pandas as pd
import math


def convertBatToJson(filename):
  filename = 'sanup_dp.csv'
  df = pd.read_csv(filename)
  deviceList = []
  for i in range(len(df)) :
    deviceDict = {}
    deviceName = str(int(df.iloc[i, 0]))
    speedDialsList = []
    speedDialsDict = {}
    col_count = df.shape[1]
    speedDialList = []
    for col in range(1,col_count,2):
      speedDialDict = {}
      if col == 1: 
        index = col
      else:
        index = int((col+1)/2)
      dirn =df.iloc[i, col]
      label = df.iloc[i, col+1]
      if type(dirn) !='str':
          if math.isnan(float(dirn)):
              break
      speedDialDict.update({"index":str(index),"dirn":str(int(dirn)),"label":str(label)})
      speedDialList.append(speedDialDict)
    if len(speedDialList)>0 : 
      deviceDict.update({deviceName:{"speeddials": {"speeddial":speedDialList}}})
      deviceList.append(deviceDict)
  return deviceList

print(convertBatToJson('sanup_dp.csv'))

    