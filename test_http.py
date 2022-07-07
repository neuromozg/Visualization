#!/usr/bin/env python3

import requests
import time

#URL = 'http://10.10.0.166:31222/user?user=all'
URL = 'http://cyber-drom.geoscan.aero/user?user=all'
#URL = 'http://10.10.1.58:5000/'
start_time = time.time()
counter = 0

while True:
    counter+=1
    
    try:
        objectData = requests.get(URL)
            
    except KeyboardInterrupt:
        #print ('error')
        break
        objectData = None
        
    if (time.time() - start_time) > 1 :
        print("FPS: %.2f result: %s" % (counter / (time.time() - start_time), objectData))
        counter = 0
        start_time = time.time()
        
    #print(objectData.text)
