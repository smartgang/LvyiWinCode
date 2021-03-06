# -*- coding: utf-8 -*-
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
'''
#统计连续为正最大的数量
#统计连续为负最大的数量
df=pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I600 slip\\DCE.I600 Set8564 MS5 ML12 KN22 DN26 result.csv')
ret=df.ret.tolist()
positiveDict=[0]*20
negativeDict=[0]*20
r0=ret[0]
positivenum=int(0)
negativenum=int(0)
for r in ret:
    if r>0:
        #当前为正，判断之前的数
        if r0>0:
            #如果当前为正，之前也为正，则正数+1
            positivenum+=1
        elif r0<=0:
            #如果当正，之前为负，正数+1，负数保存并清0
            positivenum+=1
            if negativenum>0:
                negativeDict[negativenum]+=1
            negativenum=0
    elif r<=0:
        if r0>0:
            #如果当前为负，之前为正，则正数清并保存，负数+1
            negativenum+=1
            if positivenum>0:
                positiveDict[positivenum] += 1
            positivenum=0
        elif r0<=0:
            negativenum+=1
    r0=r

positivedf=pd.DataFrame(positiveDict,columns=['successionnum'])
negativedf=pd.DataFrame(negativeDict,columns=['successionnum'])
positivedf.to_csv('positivedf.csv')
negativedf.to_csv('negativedf.csv')
pass
'''
'''
#根据月份生成utc值
import time
monthlist=['Jan-16','Feb-16','Mar-16','Apr-16','May-16','Jun-16','Jul-16','Aug-16','Sep-16','Oct-16','Nov-16','Dec-16',
            'Jan-17','Feb-17','Mar-17','Apr-17','May-17','Jun-17','Jul-17','Aug-17','Sep-17','Oct-17','Nov-17','Dec-17']
for month in monthlist:
    timestr=month+'-01 00:00:00'
    t=time.strptime(timestr,"%b-%y-%d %H:%M:%S")
    print t
    utc=int(time.mktime(t))
    print utc
'''
'''
#生成排序序列
import numpy
#indexarray=range(5,30,1)
#print indexarray
#b = numpy.arange(-0.01,-0.062,-0.002)
#print b
s=4
for l in range(10,28):
    steplist=[1,2,3,4]
    delta=(l-s)/4.0
    print 'l:',l
    print 'delta:',delta
    midlist=[]
    for i in steplist:
        #print i*delta
        midlist.append(s+int(i*delta))
    print midlist
'''
'''
#生成月份列表
#Jan-16
from datetime import datetime

date_l=[datetime.strftime(x,'%b-%y') for x in list(pd.date_range(start='2013-10-01', end='2018-01-01',freq='M'))]
print date_l
'''
'''
#月收益top200均值画图
import matplotlib.pyplot as plt
df = pd.read_csv("D:\\002 MakeLive\myquant\LvyiWin\Results\SHFE RB 600 ricequant\\SHFE.RB_600_monthy_retr.csv",index_col='Setname')  # 排名文件
cols = df.columns.tolist()
averagelist=[]
for c in cols:
    df = df.sort_values(by=c, ascending=False)
    averagelist.append(df.head(1000)[c].mean())
print averagelist
plt.plot(averagelist)
plt.show()
'''
''''
#获取当前目录
import os
path=os.getcwd()
print path
print os.path.abspath(os.curdir)
print os.path.abspath('..')#上一级目录
print os.path.abspath('.')#当前目录
import DATA_CONSTANTS as DC
p=DC.getUpperPath()
print p
'''
'''
计算1mk的ATR
从N-1开始遍历10mk，取0~N-2的ATR:trlist
根据N的strtime定位到1mk，取rng,1mkdata
for i in range(rng):
    trlist.append(1mkdata.iloc[i]['TR']
    df1m['ATR']=trlist.mean()
    del trlist[-1]
'''
'''
#查询最小价格变动
import DATA_CONSTANTS as DC
symbol='DCE.I'
print DC.getPriceTick(symbol)
'''

'''
import DATA_CONSTANTS as DC
symbol='DCE.I'
K_MIN=600
starttime = '2016-01-01 00:00:00'
endtime = '2018-01-01 00:00:00'
bar1m = DC.getBarData(symbol=symbol, K_MIN=60, starttime=starttime, endtime=endtime)
barxm = DC.getBarData(symbol=symbol, K_MIN=K_MIN, starttime=starttime, endtime=endtime)
# bar1m计算longHigh,longLow,shortHigh,shortLow
bar1m['longHigh'] = bar1m['high']
bar1m['shortHigh'] = bar1m['high']
bar1m['longLow'] = bar1m['low']
bar1m['shortLow'] = bar1m['low']
bar1m['highshift1'] = bar1m['high'].shift(1).fillna(0)
bar1m['lowshift1'] = bar1m['low'].shift(1).fillna(0)
bar1m.loc[bar1m['open'] < bar1m['close'],'longHigh'] = bar1m['highshift1']
bar1m.loc[bar1m['open'] > bar1m['close'],'shortLow'] = bar1m['lowshift1']

bar1m.to_csv('longHighTest.csv')
'''
'''
import time
print 'timer task test begin'
i=0
while 1:
    print 'i:',i
    time.sleep(10)
    i+=1
'''
'''
#批量重命名文件
import os
import pandas as pd
filepath='D:\\002 MakeLive\myquant\LvyiWin\Results\SHFE RB 600\OnceWinNoLoss9.0\\'
# 读取finalresult文件并排序，取前topN个
finalresult = pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\SHFE RB 600\SHFE.RB600 finanlresults.csv')
finalresult = finalresult.sort_values(by='end_cash', ascending=False)
totalnum = finalresult.shape[0]
topN=4500
os.chdir(filepath)
for sn in range(0, topN):
    opr = finalresult.iloc[sn]
    setname = opr['Setname']
    print setname
    srcfile='SHFE.RB600 '+setname+' resultDSL_by_realtick.csv'
    dstfile='SHFE.RB600 '+setname+' resultOWNL_by_realtick.csv'
    os.rename(srcfile,dstfile)#重命名文件
'''
from selenium import webdriver
webdriver.Firefox()