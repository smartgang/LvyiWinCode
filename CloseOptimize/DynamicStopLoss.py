# -*- coding: utf-8 -*-
'''
只能做到min级
遍历oprlist，取出startutc和endutc，根据utc取1min的数据
如果是多仓，算1min数据close的最大回撤，作为最大期间亏损
如果是空仓，算1min数据close的最大反回撤，作为最大期间亏损
如果最大期间亏损大于阀值，则根据最大值和阀值round出一个平仓价格
附带统计：
统计每个操作期间的最大收益和最大亏损
'''
import pandas as pd
import DATA_CONSTANTS as DC
import numpy as np

def max_draw(bardf):
    '''
    根据close的最大回撤值和比例
    :param df:
    :return:
    '''
    df=pd.DataFrame({'close':bardf.close,'strtime':bardf['strtime'],'utc_time':bardf['utc_time'],'timeindex':bardf['Unnamed: 0']})

    df['max2here']=df['close'].expanding().max()
    df['dd2here']=df['close']/df['max2here']-1

    temp= df.sort_values(by='dd2here').iloc[0]
    max_dd=temp['dd2here']
    max_dd_close=temp['close']
    max = temp['max2here']
    strtime = temp['strtime']
    utctime = temp['utc_time']
    timeindex = temp['timeindex']
    #返回值为最大回撤比例，最大回撤价格，最大回撤的最高价,最大回撤时间和位置
    return max_dd,max_dd_close,max,strtime,utctime,timeindex

def max_reverse_draw(bardf):
    df = pd.DataFrame({'close': bardf.close, 'strtime': bardf['strtime'], 'utc_time': bardf['utc_time'],
                       'timeindex': bardf['Unnamed: 0']})

    df['min2here']=df['close'].expanding().min()
    df['dd2here']=1-df['close']/df['min2here']

    temp= df.sort_values(by='dd2here').iloc[0]
    max_dd=temp['dd2here']
    max_dd_close=temp['close']
    min = temp['min2here']
    strtime = temp['strtime']
    utctime = temp['utc_time']
    timeindex = temp['timeindex']
    return max_dd,max_dd_close,min,strtime,utctime,timeindex

def getLongDrawback(bardf,stopTarget):
    df = pd.DataFrame({'close': bardf.close, 'strtime': bardf['strtime'], 'utc_time': bardf['utc_time'],
                       'timeindex': bardf['Unnamed: 0']})
    df['max2here']=df['close'].expanding().max()
    df['dd2here'] = df['close'] / df['max2here'] - 1
    df['dd'] = df['dd2here'] - stopTarget
    tempdf = df.loc[df['dd']<0]
    if tempdf.shape[0]>0:
        temp = tempdf.iloc[0]
        max_dd = temp['dd2here']
        max_dd_close = temp['close']
        maxprice = temp['max2here']
        strtime = temp['strtime']
        utctime = temp['utc_time']
        timeindex = temp['timeindex']
    else:
        max_dd = 0
        max_dd_close = 0
        maxprice = 0
        strtime = ' '
        utctime = 0
        timeindex = 0
    return max_dd,max_dd_close,maxprice,strtime,utctime,timeindex

def getShortDrawback(bardf,stopTarget):
    df = pd.DataFrame({'close': bardf.close, 'strtime': bardf['strtime'], 'utc_time': bardf['utc_time'],
                       'timeindex': bardf['Unnamed: 0']})
    df['min2here']=df['close'].expanding().min()
    df['dd2here'] = 1 - df['close'] / df['min2here']
    df['dd'] = df['dd2here'] - stopTarget
    tempdf = df.loc[df['dd']<0]
    if tempdf.shape[0]>0:
        temp = tempdf.iloc[0]
        max_dd = temp['dd2here']
        max_dd_close = temp['close']
        maxprice = temp['min2here']
        strtime = temp['strtime']
        utctime = temp['utc_time']
        timeindex = temp['timeindex']
    else:
        max_dd = 0
        max_dd_close = 0
        maxprice = 0
        strtime = ' '
        utctime = 0
        timeindex = 0
    return max_dd,max_dd_close,maxprice,strtime,utctime,timeindex

def getLongDrawbackByTick(bardf,stopTarget):
    df = pd.DataFrame({'high': bardf.high,'low':bardf.low, 'strtime': bardf['strtime'], 'utc_time': bardf['utc_time'],
                       'timeindex': bardf['Unnamed: 0']})
    df['max2here']=df['high'].expanding().max()
    df['dd2here'] = df['low'] / df['max2here'] - 1
    df['dd'] = df['dd2here'] - stopTarget
    tempdf = df.loc[df['dd']<0]
    if tempdf.shape[0]>0:
        temp = tempdf.iloc[0]
        max_dd = temp['dd2here']
        max_dd_close = temp['low']
        maxprice = temp['max2here']
        strtime = temp['strtime']
        utctime = temp['utc_time']
        timeindex = temp['timeindex']
    else:
        max_dd = 0
        max_dd_close = 0
        maxprice = 0
        strtime = ' '
        utctime = 0
        timeindex = 0
    return max_dd,max_dd_close,maxprice,strtime,utctime,timeindex

def getShortDrawbackByTick(bardf,stopTarget):
    df = pd.DataFrame({'high': bardf.high,'low':bardf.low ,'strtime': bardf['strtime'], 'utc_time': bardf['utc_time'],
                       'timeindex': bardf['Unnamed: 0']})
    df['min2here']=df['low'].expanding().min()
    df['dd2here'] = 1 - df['high'] / df['min2here']
    df['dd'] = df['dd2here'] - stopTarget
    tempdf = df.loc[df['dd']<0]
    if tempdf.shape[0]>0:
        temp = tempdf.iloc[0]
        max_dd = temp['dd2here']
        max_dd_close = temp['high']
        maxprice = temp['min2here']
        strtime = temp['strtime']
        utctime = temp['utc_time']
        timeindex = temp['timeindex']
    else:
        max_dd = 0
        max_dd_close = 0
        maxprice = 0
        strtime = ' '
        utctime = 0
        timeindex = 0
    return max_dd,max_dd_close,maxprice,strtime,utctime,timeindex
if __name__ == '__main__':
    stoplossStep=-0.002
    stoplossList = np.arange(-0.01, -0.062, stoplossStep)
    slip = 0.5
    pricetick=0.5
    symbol="DCE.I"
    K_MIN = 600
    oprresultpath = "D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I 600 ricequant\ForwardOprAnalyze\\"
    setname = "DCE.I600_Rank5_win8"
    bar1m = pd.read_csv(DC.BAR_DATA_PATH + symbol + '\\' + symbol + ' ' + str(60) + '.csv')
    barxm = pd.read_csv(DC.BAR_DATA_PATH + symbol + '\\' + symbol + ' ' + str(K_MIN) + '.csv')
    endcashList=[]
    for stoplossTarget in stoplossList:
        print ("stoplossTarget:%f"%stoplossTarget)
        oprdf = pd.read_csv(oprresultpath + setname +"_oprResult.csv")
        #oprdf['new_closetime'] = oprdf['closetime']
        #oprdf['new_closeindex'] = oprdf['closeindex']
        #oprdf['new_closeutc'] = oprdf['closeutc']
        oprdf['new_closeprice'] = oprdf['closeprice']
        oprdf['max_opr_gain'] = 0
        oprdf['min_opr_gain'] = 0
        oprdf['max_dd'] =0
        oprnum = oprdf.shape[0]
        for i in range(oprnum):
            opr = oprdf.iloc[i]
            startutc = (barxm.loc[barxm['utc_time']==opr.openutc]).iloc[0].utc_endtime-60
            endutc = (barxm.loc[barxm['utc_time']==opr.closeutc]).iloc[0].utc_endtime
            oprtype = opr.tradetype
            openprice = opr.openprice
            data1m = bar1m.loc[(bar1m['utc_time'] > startutc) & (bar1m['utc_time'] < endutc)]
            if oprtype == 1:
                #多仓，取最大回撤，max为最大收益，min为最小收益
                max_dd,dd_close,maxprice,strtime,utctime,timeindex=getLongDrawbackByTick(data1m,stoplossTarget)
                oprdf.ix[i, 'max_opr_gain'] = (data1m.close.max() - openprice)/openprice
                oprdf.ix[i, 'min_opr_gain'] = (data1m.close.min() - openprice)/openprice
                oprdf.ix[i,'max_dd'] = max_dd
                if max_dd<=stoplossTarget:
                    ticknum=round((maxprice*stoplossTarget)/pricetick,0)-1
                    oprdf.ix[i, 'new_closeprice'] = maxprice +ticknum*pricetick-slip
                '''
                if max_dd !=0:
                    #超过门限，触发动态止损
                    oprdf.ix[i, 'new_closetime'] = strtime
                    oprdf.ix[i, 'new_closeindex'] = timeindex
                    oprdf.ix[i, 'new_closeutc'] = utctime
                    oprdf.ix[i, 'new_closeprice'] = dd_close-slip
                '''
            else:
                #空仓，取逆向最大回撤，min为最大收益，max为最小收闪
                max_dd, dd_close, minprice, strtime, utctime, timeindex = getShortDrawbackByTick(data1m,stoplossTarget)
                oprdf.ix[i, 'max_opr_gain'] = (openprice - data1m.close.min()) / openprice
                oprdf.ix[i, 'min_opr_gain'] = (openprice - data1m.close.max()) / openprice
                oprdf.ix[i, 'max_dd'] = max_dd
                if max_dd<=stoplossTarget:
                    ticknum=round((minprice*stoplossTarget)/pricetick,0)-1
                    oprdf.ix[i, 'new_closeprice'] = minprice - ticknum*pricetick + slip
                '''
                if max_dd !=0:
                    # 超过门限，触发动态止损
                    oprdf.ix[i, 'new_closetime'] = strtime
                    oprdf.ix[i, 'new_closeindex'] = timeindex
                    oprdf.ix[i, 'new_closeutc'] = utctime
                    oprdf.ix[i, 'new_closeprice'] = dd_close + slip
                '''
        initial_cash = 20000
        margin_rate = 0.2
        commission_ratio = 0.00012
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

        oprdf.to_csv(setname+'DSL_tick'+str(stoplossTarget)+'.csv')

        endcash = oprdf.ix[oprtimes - 1, 'new_own cash']
        endcashList.append([stoplossTarget,endcash])
    endcashdf=pd.DataFrame(endcashList,columns=['SL-Target','end cash'])
    endcashdf.to_csv(setname+'_tick_endcash.csv')
    pass