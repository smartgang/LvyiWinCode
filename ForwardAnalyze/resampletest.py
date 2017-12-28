# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

annualdf=pd.read_csv('annual_result.csv')
sharpedf=pd.read_csv('sharpe_result.csv')
col=annualdf.columns.tolist()[2:]
print col[0]
df=pd.DataFrame({'Setname':annualdf.Setname,'annual':annualdf[col[0]],'sharpe':sharpedf[col[0]]})
df['AnnualRank']=0
df=df.sort_values(by='annual', ascending=False)
df.head(1000)['Rank']+=50
df.head(500)['Rank']+=20
df.head(200)['Rank']+=30
print df.head(10)
'''
rawdata=pd.read_csv('SHFE.RB600result.csv')
date=rawdata.opentime
month=date.str.slice(0,7)
rawdata['month']=month
print rawdata.month
rawdata['ret_r_1']=rawdata['ret_r']+1
grouped_ret_r=rawdata['ret_r_1'].groupby(rawdata['month'])
ret_r_prod=grouped_ret_r.prod()
print ret_r_prod
'''
