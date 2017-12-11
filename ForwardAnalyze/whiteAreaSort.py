# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

monthlyRetR=pd.read_csv('prodresult.csv',index_col='Setname')
setnum=monthlyRetR.shape[0]
rowlist=[]
for num in range(setnum):
    print num
    loc=monthlyRetR.iloc[num]
    prodlist=[]
    prodlist.append(loc.name)
    for i in range(0,23):
        prodlist.append(loc[0+i:12+i].prod())
    rowlist.append(prodlist)

df=pd.DataFrame(rowlist)
df.to_csv('whiteArea.csv')