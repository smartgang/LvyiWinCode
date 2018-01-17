# -*- coding: utf-8 -*-
'''
成交量与收益关系分析：
成交量的表征：
    volume_sum:周期内的累加值
    volume_vol：波动率，周期内的方差
收益的表片：
    retr_prod：周期内收益率的累乘，取top500的均值
    retr_sr:周期内成功率，取top500的均值
结果量现：
    一张图4根曲线
'''
import pandas as pd
from datetime import datetime

def calVolume(dfpath,periodlist):
    df = pd.read_csv(dfpath)
    df.index = pd.to_datetime(df['strtime'])
    df = df.tz_localize('UTC')
    df = df.tz_convert('Asia/Shanghai')
    # print df['2015-01-01':'2015-01-08']
    df['daylable'] = 0
    for i in range(len(periodlist) - 1):
        startday = periodlist[i]
        endday = periodlist[i + 1]
        print startday
        df.loc[startday:endday, 'daylable'] = startday
    volume = df['volume'].groupby(df['daylable'])
    volume_wave = df['volume_wave'].groupby(df['daylable'])
    price_wave = df['price_wave'].groupby(df['daylable'])
    volumedf = pd.DataFrame()
    volumedf['volume_sum'] = volume.sum()
    volumedf['volume_std'] = volume.std()
    volumedf['volume_wave'] = volume_wave.mean()
    volumedf['price_wave'] = price_wave.mean()
    volumedf.to_csv('RB_volumedf_wave.csv')

def calResult(resultpath,paralist,periodlist):
    '''
    计算每个日期2万个组合中top500的结果
    先将每个组合标上daylable，successlable，然后算收益和成功率
    保存到df的一列，列名为setname
    遍历后转，行名为setname,列名为daylable
    再每个daylable进行遍历，算每一个的top500取值
    :param resultpath:
    :param paralist:
    :return:
    '''
    finalretrdf=pd.DataFrame()
    finalSRdf=pd.DataFrame()
    for setname in paralist:
        print setname
        resultdf=pd.read_csv(resultpath+'DCE.I600 '+ setname + ' result.csv')
        resultdf.index = pd.to_datetime(resultdf['opentime'])
        resultdf = resultdf.tz_localize('UTC')
        resultdf = resultdf.tz_convert('Asia/Shanghai')

        resultdf['successlable']=0
        resultdf.loc[resultdf['ret']>0,'successlable']=1
        resultdf['retr1']=resultdf['ret_r']+1
        resultdf['daylable'] = 0
        for i in range(len(periodlist) - 1):
            startday = periodlist[i]
            endday = periodlist[i + 1]
            #print startday
            resultdf.loc[startday:endday, 'daylable'] = startday
        retr1 = resultdf['retr1'].groupby(resultdf['daylable'])
        finalretrdf[setname]=retr1.prod()
        succ = resultdf['successlable'].groupby(resultdf['daylable'])
        finalSRdf[setname] =succ.sum()/succ.count()
    finalretrdf=finalretrdf.T
    finalSRdf = finalSRdf.T
    cols=finalretrdf.columns.tolist()
    retrlist=[]
    succlist=[]
    for p in cols:
        retp = finalretrdf[p].sort_values(ascending=False)
        srp = finalSRdf[p].sort_values(ascending=False)
        retrlist.append(retp.head(500).mean())
        succlist.append(srp.head(500).mean())
    retrdf=pd.DataFrame(cols,columns=['daylable'])
    retrdf['retr']=retrlist
    retrdf.to_csv('retrdf.csv')
    succdf=pd.DataFrame(cols,columns=['daylable'])
    succdf['succ']=succlist
    succdf.to_csv('succdf.csv')

if __name__ == '__main__':

    kpath="D:\\002 MakeLive\DataCollection\\bar data\SHFE.RB\\SHFE.RB 600_wave.csv"
    resultpath='D:\\002 MakeLive\myquant\LvyiWin\Results\SHFE RB 600 ricequant\\'
    parasetlist = pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\ParameterOptSet.csv')['Setname']
    periodlist = [datetime.strftime(x, '%Y-%m-%d') for x in
                  list(pd.date_range(start='2010-01-01', end='2018-01-05', freq='7D'))]
    calVolume(kpath,periodlist)
    #calResult(resultpath,parasetlist,periodlist)
