# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 22:26:43 2018

@author: RNEL
"""
import time
import json

t0 = time.time()
with open('temp_data.json') as json_data:
    d = json.load(json_data)
t1 = time.time() - t0

print("elapsed time : %g" % t1)



t0 = time.time()
s = set()
for x in d:
    s = s.union(x.keys())

t2 = time.time() - t0

print("elapsed time : %g" % t2)
