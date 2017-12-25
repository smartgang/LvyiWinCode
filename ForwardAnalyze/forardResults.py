# -*- coding: utf-8 -*-
'''
多层推进分析第三步：
计算多层推进过程中，每个灰区的结果，并计算最终结果
'''

import pandas as pd
stepList=[1,2,3,4,5,6]
windowsSet=[1,2,3,4,5,6,9,12,15]
#windowsSet=[1,2,4,5]
#whiteWindows = 12
startFrom=0#从第0个月开始往前推
symbol='DCE.I'
monthlyRetR=pd.read_csv('prodresult '+symbol+'.csv',index_col='Setname')
for whiteWindows in windowsSet:
    whiteResult=pd.read_csv('whiteArea '+symbol+str(whiteWindows)+'.csv',index_col='Setname')
    monthlist=whiteResult.columns.values.tolist()
    del monthlist[0]
    resultlist=[]
    for colname in monthlist:
        head=whiteResult.sort_values(axis=0,by=colname,ascending=False).iloc[0]
        setname=head.name
        whiteValue=head[colname]
        #grayValue=monthlyRetR.ix[setname,colname]
        resultlist.append([colname,setname,whiteValue])
    df = pd.DataFrame(resultlist,columns=['Month','Setname','whiteValue'])
    setlist=df.Setname
    #df=df.set_index('Setname')
    for step in stepList:
        df[str(step)]=1
        for i in range(startFrom,len(monthlist),step):
            startindex=i
            endindex=i +step - 1
            if startindex>=len(monthlist):startindex = len(monthlist)-1
            if endindex>=len(monthlist):endindex = len(monthlist)-1
            startmonth = monthlist[startindex]
            endmonth = monthlist[endindex]
            grayValuelist=monthlyRetR.ix[setlist[i],startmonth:endmonth]
            grayValue=grayValuelist.prod()
            df.ix[i,str(step)]=grayValue
            pass
    df.to_csv('forwardResult '+symbol+str(whiteWindows)+'.csv')