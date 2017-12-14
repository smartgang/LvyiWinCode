# -*- coding: utf-8 -*-
'''
多层推进分析第1步：
计算每个组合每个月的独立收益
'''

import pandas as pd


symbol='SHFE.RB'
monthlyRetR=pd.read_csv('prodresult '+symbol+'.csv',index_col='Setname')
monthlist=monthlyRetR.columns.values.tolist()
print monthlist

#index为排名，内容为set名
df = pd.DataFrame(columns=monthlist)
for colname in monthlist:
    head=monthlyRetR.sort_values(axis=0,by=colname,ascending=False).index.values.tolist()
    df[colname]=head
    pass
df.to_csv('monthlyRank '+symbol+'.csv')
'''
#index为set名，内容为index
df=pd.DataFrame(columns=monthlist,index=monthlyRetR.index)
for colname in monthlist:
    head=monthlyRetR.sort_values(axis=0,by=colname,ascending=False).index.values.tolist()
    for i in range(len(head)):
        df.ix[head[i],colname]=i
df.to_csv('monthlyRankNum '+symbol+'.csv')
'''