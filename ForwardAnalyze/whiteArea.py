# -*- coding: utf-8 -*-
'''
多层推进分析第二步：
计算多层推进过程中，每个白色区的累计收益
多目标推进：
    通过utctime来截取数据：通过月份生成utc
    每读一个set文件把全部推进都做完，以减少文件读取次数
    每一次推进，将所有目标都计算完，保存到list中，每个set做完之后，每个目标的list根据推进月份有一行,append到总list中
    推进完后将总list使用df，每个目标一个df
    再在各个df中按列算排名和总分，保存到一个总分的df中
'''
import pandas as pd
import numpy as np
symbol='DCE.I'
monthlyRetR=pd.read_csv('prodresult '+symbol+'.csv',index_col='Setname')
setnum=monthlyRetR.shape[0]

#白区窗口值
#每次只需要修改这个值
windowsSet=[1,2,3,4,5,6,9,12,15]
#windowsSet=[1,2,4,5]
#whiteWindows = 6
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