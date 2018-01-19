# -*- coding: utf-8 -*-
'''
中时长均线平仓优化
取MAShort和MALong中间某一周期长计算MA_Mid，以close价格与MA_Mid的上穿下破关系作为平仓出场条件
多仓条件下，close下破MA_Mid触发平仓
空仓条件下，close上穿MA_Mid触发平仓
1.close序列与MA_Mid的 cross情况
2.读取oprResult，逐个opr取openutc和closeutc，openutc和closeutc取cross序列
3.oprtype为1，则取第一个 cross为1的位置和close值，oprtype为-1则取第一个cross为-1的位置和close值
4.重新计算result的ret和ret_r，并重新计算评价结果
'''

import pandas as pd
import MA
import DATA_CONSTANTS as DC
import numpy as np

def getMAMid(MA_Short,MA_Mid,symbol,K_MIN,indexoffset=0):
    #计算ma以及ma_cross
    bardata = pd.read_csv(DC.BAR_DATA_PATH + symbol + '\\' + symbol + ' ' + str(K_MIN) + '.csv')
    madf = pd.DataFrame({'close': bardata.close})
    madf['utc_time'] = bardata['utc_time']
    madf['strtime'] = bardata['strtime']
    madf['index'] = bardata['Unnamed: 0']-indexoffset
    #madf['MA_Short'] = MA.calMA(madf['close'], MA_Short)
    madf['MA_Mid'] = MA.calMA(madf['close'], MA_Mid)
    madf['MA_True'], madf['MA_Cross'] = MA.dfCross(madf, 'close', 'MA_Mid')
    #madf.to_csv("mamid.csv")
    return madf

if __name__ == '__main__':
    oprresultpath="D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I600 slip\\"
    setname="Set5368 MS4 ML16 KN24 DN30"
    symbol="DCE.I"
    K_MIN= 600
    startdate="2016-01-04"
    MA_Short=4
    MA_Mid=10
    indexoffset=76
    #bardata=DC.GET_DATA(DC.DATA_TYPE_RAW,symbol=symbol,K_MIN=K_MIN,startdate=startdate)
    madf=getMAMid(MA_Short,MA_Mid,symbol,K_MIN,indexoffset)

    oprdf=pd.read_csv(oprresultpath+symbol+str(K_MIN)+" "+setname+" result.csv")
    oprdf['new_closetime']=oprdf['closetime']
    oprdf['new_closeindex'] = oprdf['closeindex']
    oprdf['new_closeutc'] = oprdf['closeutc']
    oprdf['new_closeprice'] = oprdf['closeprice']
    oprnum=oprdf.shape[0]
    for i in range(oprnum):
        opr=oprdf.iloc[i]
        startutc=opr.openutc
        endutc=opr.closeutc
        oprtype = opr.tradetype
        midma=madf.loc[(madf['utc_time']>startutc) & (madf['utc_time']<endutc)]
        knum=midma.shape[0]
        for l in range(knum):
            mak=midma.iloc[l]
            if (oprtype==1 and mak.MA_Cross==-1) or (oprtype==-1 and mak.MA_Cross==1):
                oprdf.ix[i,'new_closetime']=mak.strtime
                oprdf.ix[i,'new_closeindex']=mak['index']
                oprdf.ix[i,'new_closeutc']=mak.utc_time
                oprdf.ix[i,'new_closeprice']=mak.close
                break

    initial_cash=20000
    margin_rate=0.2
    slip=0.5
    commission_ratio=0.00012
    firsttradecash = initial_cash / margin_rate
    # 2017-12-08:加入滑点
    oprdf['new_ret'] = ((oprdf['new_closeprice'] - oprdf['openprice']) * oprdf['tradetype']) - slip
    oprdf['new_ret_r'] = oprdf['new_ret'] / oprdf['new_closeprice']
    oprdf['new_commission_fee'] = firsttradecash * commission_ratio * 2
    oprdf['new_per earn'] = 0  # 单笔盈亏
    oprdf['new_own cash'] = 0  # 自有资金线
    oprdf['new_trade money'] = 0  # 杠杆后的可交易资金线
    oprdf['new_retrace rate'] = 0  # 回撤率

    oprdf.ix[0, 'new_per earn'] = firsttradecash * oprdf.ix[0, 'new_ret_r']
    # 加入maxcash用于计算最大回撤
    maxcash = initial_cash + oprdf.ix[0, 'new_per earn'] - oprdf.ix[0, 'new_commission_fee']
    oprdf.ix[0, 'new_own cash'] = maxcash
    oprdf.ix[0, 'new_trade money'] = oprdf.ix[0, 'new_own cash'] / margin_rate
    oprtimes = oprdf.shape[0]
    for i in np.arange(1, oprtimes):
        commission = oprdf.ix[i - 1, 'new_trade money'] * commission_ratio * 2
        perearn = oprdf.ix[i - 1, 'new_trade money'] * oprdf.ix[i, 'new_ret_r']
        owncash = oprdf.ix[i - 1, 'new_own cash'] + perearn - commission
        maxcash = max(maxcash, owncash)
        retrace_rate = (maxcash - owncash) / maxcash
        oprdf.ix[i, 'new_own cash'] = owncash
        oprdf.ix[i, 'new_commission_fee'] = commission
        oprdf.ix[i, 'new_per earn'] = perearn
        oprdf.ix[i, 'new_trade money'] = owncash / margin_rate
        oprdf.ix[i, 'new_retrace rate'] = retrace_rate
    oprdf.to_csv('newoprResult.csv')