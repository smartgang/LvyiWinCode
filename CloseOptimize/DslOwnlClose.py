# -*- coding: utf-8 -*-
'''
将DSL和OWNL结合
同时计算和记录
触发时间早的作为实际平仓价
在同一根1minK线内的使用盈利大的
'''
import pandas as pd
import DATA_CONSTANTS as DC
import numpy as np
import os
import ResultStatistics as RS
import multiprocessing
from DynamicStopLoss import *
from OnceWinNoLoss import  *

def dslAndownlCal(symbol,K_MIN,setname,bar1m,barxm,pricetick,slip,dslFolder,ownlFolder,tofolder):
    print 'setname:', setname
    oprdf = pd.read_csv(symbol + str(K_MIN) + ' ' + setname + ' result.csv')
    dsloprname=symbol + str(K_MIN) + ' ' + setname + ' resultDSL_by_tick.csv'
    ownloprname=symbol + str(K_MIN) + ' ' + setname + ' resultOWNL_by_tick.csv'
    dsloprdf=pd.read_csv(dslFolder+dsloprname)
    ownloprdf=pd.read_csv(ownlFolder+ownloprname)
    oprdf['dsl_closeprice'] = dsloprdf['new_closeprice']
    oprdf['dsl_closetime'] = dsloprdf['new_closetime']
    oprdf['dsl_closeindex'] = dsloprdf['new_closeindex']
    oprdf['dsl_closeutc'] = dsloprdf['new_closeutc']

    oprdf['ownl_closeprice'] = ownloprdf['new_closeprice']
    oprdf['ownl_closetime'] = ownloprdf['new_closetime']
    oprdf['ownl_closeindex'] = ownloprdf['new_closeindex']
    oprdf['ownl_closeutc'] = ownloprdf['new_closeutc']

    oprdf['new_closeprice'] = oprdf['closeprice']
    oprdf['new_closetime'] = oprdf['closetime']
    oprdf['new_closeindex'] = oprdf['closeindex']
    oprdf['new_closeutc'] = oprdf['closeutc']

    oprdf.loc[oprdf['dsl_closeutc'] < oprdf['ownl_closeutc'], 'new_closeprice']= oprdf['dsl_closeprice']
    oprdf.loc[oprdf['dsl_closeutc'] < oprdf['ownl_closeutc'], 'new_closetime'] = oprdf['dsl_closetime']
    oprdf.loc[oprdf['dsl_closeutc'] < oprdf['ownl_closeutc'], 'new_closeindex'] = oprdf['dsl_closeindex']
    oprdf.loc[oprdf['dsl_closeutc'] < oprdf['ownl_closeutc'], 'new_closeutc'] = oprdf['dsl_closeutc']

    oprdf.loc[oprdf['ownl_closeutc'] < oprdf['dsl_closeutc'], 'new_closeprice']= oprdf['ownl_closeprice']
    oprdf.loc[oprdf['ownl_closeutc'] < oprdf['dsl_closeutc'], 'new_closetime'] = oprdf['ownl_closetime']
    oprdf.loc[oprdf['ownl_closeutc'] < oprdf['dsl_closeutc'], 'new_closeindex'] = oprdf['ownl_closeindex']
    oprdf.loc[oprdf['ownl_closeutc'] < oprdf['dsl_closeutc'], 'new_closeutc'] = oprdf['ownl_closeutc']

    equaredf=oprdf.loc[oprdf['dsl_closeutc'] == oprdf['ownl_closeutc']]
    if equaredf.shape[0]>0:
        indexlist=equaredf.index.tolist()
        for i in indexlist:
            if equaredf.ix[i,'tradetype']==1:
                if equaredf.ix[i,'dsl_closeprice']>=
                oprdf.ix[i,'new_closeprice']=
    initial_cash = 20000
    margin_rate = 0.2
    commission_ratio = 0.00012
    firsttradecash = initial_cash / margin_rate
    # 2017-12-08:加入滑点
    oprdf['new_ret'] = ((oprdf['new_closeprice'] - oprdf['openprice']) * oprdf['tradetype']) - slip
    oprdf['new_ret_r'] = oprdf['new_ret'] / oprdf['openprice']
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
    #保存新的result文档
    oprdf.to_csv(tofolder+symbol + str(K_MIN) + ' ' + setname + ' resultDSL_by_tick.csv')

    #计算统计结果
    oldendcash = oprdf.ix[oprnum - 1, 'own cash']
    oldAnnual = RS.annual_return(oprdf)
    oldSharpe = RS.sharpe_ratio(oprdf)
    oldDrawBack = RS.max_drawback(oprdf)[0]
    oldSR = RS.success_rate(oprdf)
    newendcash = oprdf.ix[oprnum - 1, 'new_own cash']
    newAnnual = RS.annual_return(oprdf,cash_col='new_own cash',closeutc_col='new_closeutc')
    newSharpe = RS.sharpe_ratio(oprdf,cash_col='new_own cash',closeutc_col='new_closeutc',retr_col='new_ret_r')
    newDrawBack = RS.max_drawback(oprdf,cash_col='new_own cash')[0]
    newSR = RS.success_rate(oprdf,ret_col='new_ret')
    max_single_loss_rate = abs(oprdf['new_ret_r'].min())
    max_retrace_rate = oprdf['new_retrace rate'].max()

    return [setname,slTarget,oldendcash,oldAnnual,oldSharpe,oldDrawBack,oldSR,newendcash,newAnnual,newSharpe,newDrawBack,newSR,max_single_loss_rate,max_retrace_rate]


if __name__ == '__main__':
    #参数配置
    exchange_id = 'DCE'
    sec_id='I'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    topN=50
    pricetick=DC.getPriceTick(symbol)
    slip=pricetick
    starttime='2016-01-01 00:00:00'
    endtime='2018-01-01 00:00:00'
    #优化参数
    stoplossStep=-0.002
    stoplossList = np.arange(-0.02, -0.04, stoplossStep)

    #文件路径
    upperpath=DC.getUpperPath(uppernume=2)
    resultpath=upperpath+"\\Results\\"
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
    oprresultpath=resultpath+foldername

    # 读取finalresult文件并排序，取前topN个
    finalresult=pd.read_csv(oprresultpath+"\\"+symbol+str(K_MIN)+" finanlresults.csv")
    finalresult=finalresult.sort_values(by='end_cash',ascending=False)
    totalnum=finalresult.shape[0]

    #原始数据处理
    bar1m=DC.getBarData(symbol=symbol,K_MIN=60,starttime=starttime,endtime=endtime)
    barxm=DC.getBarData(symbol=symbol,K_MIN=K_MIN,starttime=starttime,endtime=endtime)
    #bar1m计算longHigh,longLow,shortHigh,shortLow
    bar1m['longHigh']=bar1m['high']
    bar1m['shortHigh']=bar1m['high']
    bar1m['longLow']=bar1m['low']
    bar1m['shortLow']=bar1m['low']
    bar1m['highshift1']=bar1m['high'].shift(1).fillna(0)
    bar1m['lowshift1']=bar1m['low'].shift(1).fillna(0)
    bar1m.loc[bar1m['open']<bar1m['close'],'longHigh']=bar1m['highshift1']
    bar1m.loc[bar1m['open']>bar1m['close'],'shortLow']=bar1m['lowshift1']

    os.chdir(oprresultpath)
    allresultdf = pd.DataFrame(columns=['setname', 'slTarget', 'old_endcash', 'old_Annual', 'old_Sharpe', 'old_Drawback',
                                     'old_SR',
                                     'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                                     'maxSingleLoss', 'maxSingleDrawBack'])
    allnum=0
    for stoplossTarget in stoplossList:
        resultList = []
        dslFolderName="DynamicStopLoss" + str(stoplossTarget*1000)
        os.mkdir(dslFolderName)#创建文件夹
        print ("stoplossTarget:%f"%stoplossTarget)
        '''
        for sn in range(0, topN):
            opr = finalresult.iloc[sn]
            setname=opr['Setname']
            l=dslCal(symbol=symbol,K_MIN=K_MIN,setname=setname,bar1m=bar1m,barxm=barxm,pricetick=pricetick,slip=slip,slTarget=stoplossTarget,tofolder=dslFolderName+'\\')
            resultList.append(l)
            allresultlist.append(l)
        '''

        pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
        l = []

        for sn in range(0,topN):
            opr = finalresult.iloc[sn]
            setname = opr['Setname']
            l.append(pool.apply_async(dslCal,
                                      (symbol, K_MIN, setname, bar1m,barxm,pricetick,slip,stoplossTarget, dslFolderName + '\\')))
        pool.close()
        pool.join()

        resultdf=pd.DataFrame(columns=['setname','slTarget','old_endcash','old_Annual','old_Sharpe','old_Drawback','old_SR',
                                                  'new_endcash','new_Annual','new_Sharpe','new_Drawback','new_SR','maxSingleLoss','maxSingleDrawBack'])
        i = 0
        for res in l:
            resultdf.loc[i]=res.get()
            allresultdf.loc[allnum]=resultdf.loc[i]
            i+=1
            allnum+=1
        resultdf['cashDelta']=resultdf['new_endcash']-resultdf['old_endcash']
        resultdf.to_csv(dslFolderName+'\\'+symbol+str(K_MIN)+' finalresult_by_tick'+str(stoplossTarget)+'.csv')

    allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(symbol + str(K_MIN) + ' finalresult_dsl_by_tick.csv')
