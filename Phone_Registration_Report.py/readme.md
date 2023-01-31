 - Phone Registration Check Report : 
    - Summary : Fetch count of registered phones in each device pool in CUCM
    - Libraries : Zeep
    - APIs used : AXL and RISPort70
    - Problem Statement : 
      Device and device pool relationship is stored in CUCM database. 
      However the registration status of device is stored in RIS DB.
      Leaving no direct way to fetch the count of registered phones in a given device pool.
      
      CLI command : to query RIS DB gives the total count of registered phones, but the breakdown per devicepool cannot be given
      
      RISPort70API : 
        Provides registration status of all devices along with count per each cucm node.
        But RISPort70 does not provide device pool information.
        RISPort70 also has a limitation that it can return 1000 results in one go.
        
    - SOLUTION : 
      This script uses AXL to fetch all the devicepools along with the devices associated to them.
      Then it breaks down the device list of each device pool into batches of 1000.
      For each batch of devices, RISPort70 API is called to fetch the count of registered phones among the 1000 devices in the given batch.
      Count from each batch is consolidated.
    
