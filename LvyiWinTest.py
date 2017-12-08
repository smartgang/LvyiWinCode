# -*- coding: utf-8 -*-
import pandas as pd
import numpy
import sys

'''
#日期去重
raw = pd.read_csv('df_all_600.csv')
raw.index = pd.to_datetime(raw['strtime'])
raw = raw.tz_localize('PRC')

openoprraw = pd.read_csv('result 600.csv')
openoprraw.index = pd.to_datetime(openoprraw['opentime'])

rawdate=pd.DataFrame({'date':raw.index.date})
a=rawdate.isin(openoprraw.index.date)
b=rawdate.loc[a[a['date']==False].index].drop_duplicates()
print b
for i in b.index:
    print b.loc[i].date
'''
'''
import ConfigParser
ini_file = 'LvyiWinConfig.ini'
conf=ConfigParser.ConfigParser()
conf.read(ini_file)
print conf.get('backtest', 'start_time')
'''
'''
#统计结果
openoprraw=pd.read_csv('JPG\\CZCE.CF600 Set6(KDJ_N=16,DMI_N=12 ) result.csv')
openoprraw.index=pd.to_datetime(openoprraw['opentime'])
openoprraw['month'] = '2016-01'
for i in openoprraw.index:
    openoprraw.ix[i, 'month'] = openoprraw.ix[i, 'opentime'][0:7]
L_POS_rgroued = openoprraw.loc[(openoprraw['ret_r']>0) & (openoprraw['tradetype']==1)]['ret_r'].groupby(openoprraw['month'])
L_NEG_rgroued = openoprraw.loc[(openoprraw['ret_r']<=0) & (openoprraw['tradetype']==1)]['ret_r'].groupby(openoprraw['month'])
S_POS_rgroued = openoprraw.loc[(openoprraw['ret_r']>0) & (openoprraw['tradetype']==-1)]['ret_r'].groupby(openoprraw['month'])
S_NeG_rgroued = openoprraw.loc[(openoprraw['ret_r']<=0) & (openoprraw['tradetype']==-1)]['ret_r'].groupby(openoprraw['month'])
a=L_POS_rgroued.count()
b=L_NEG_rgroued.count()
c=S_POS_rgroued.count()
d=S_NeG_rgroued.count()
monthlist=a.index
statdf=pd.DataFrame({'L_POS':a})
statdf['L_NEG']=b
statdf['S_POS']=c
statdf['S_NEG']=d
statdf=statdf.fillna(0)
statdf['LT']=statdf['L_POS']+statdf['L_NEG']
statdf['LTR']=statdf['L_POS']/statdf['LT']
statdf['ST']=statdf['S_POS']+statdf['S_NEG']
statdf['STR']=statdf['S_POS']/statdf['ST']
print statdf
'''
'''
dlist=[]
for i in numpy.arange(len(a)):
    dlist.append([(a[i]+b[i]),(a[i]/(a[i]+b[i])),(c[i]+d[i]),(c[i]/(c[i]+d[i]))])
print dlist
'''
'''
openoprraw['TT']='long'
openoprraw['POS']='Pos'
openoprraw.loc[openoprraw['ret_r']<=0,'POS']='Neg'
openoprraw.loc[openoprraw['tradetype']==-1,'TT']='short'
keys1=numpy.array(openoprraw['TT'])
keys2=numpy.array(openoprraw['POS'])
grouped=openoprraw['ret_r'].groupby([openoprraw['month'],keys1,keys2])
a= grouped.count()
print type(a)
'''
'''
#文件夹操作，读取目录中的文件列表
import os
os.chdir('D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I900 ALL')
filnamelist=os.listdir('D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I900 ALL')
for i in range(15):
    if 'Set' in filnamelist[i]:
        print filnamelist[i]
'''
#回测结果中去掉跨合约的操作
#1.将合约切换点转换为index：将日期转换为时间，在原文件中找到该时间对应的index
#2.遍历操作列表，去掉包含切换index的操作