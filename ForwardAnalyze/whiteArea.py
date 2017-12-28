# -*- coding: utf-8 -*-
'''
多层推进分析第二步：
计算多层推进过程中，每个白色区的累计收益
'''
import pandas as pd
import numpy as np
import time
import ResultStatistics as RS
symbol='DCE.I'
monthlyRetR=pd.read_csv('prodresult '+symbol+'.csv',index_col='Setname')
setnum=monthlyRetR.shape[0]

#白区窗口值
#每次只需要修改这个值
windowsSet=[1,2,3,4,5,6,9,12,15]
#windowsSet=[1,2,4,5]
#whiteWindows = 12
monthlist=['Jan-16','Feb-16','Mar-16','Apr-16','May-16','Jun-16','Jul-16','Aug-16','Sep-16','Oct-16','Nov-16','Dec-16',
            'Jan-17','Feb-17','Mar-17','Apr-17','May-17','Jun-17','Jul-17','Aug-17','Sep-17','Oct-17','Nov-17','Dec-17']


for whiteWindows in windowsSet:
    rowlist = []
    for num in range(setnum):
        print num
        loc=monthlyRetR.iloc[num]
        prodlist=[]
        prodlist.append(loc.name)
        for i in range(0,24-whiteWindows):#往前走多少次
            prodlist.append(loc[0+i:whiteWindows+i].prod())#白色窗口长度
        rowlist.append(prodlist)
    colname=[]
    colname.append('Setname')
    for i in range(whiteWindows,24,1):
        colname.append(monthlist[i])
        pass
    df = pd.DataFrame(rowlist,columns=colname)
    df.to_csv('whiteArea '+symbol+str(whiteWindows)+'.csv')