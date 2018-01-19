# -*- coding: utf-8 -*-
'''
读取推进的opr结果，重新计算评价指标
'''
import pandas as pd
import ResultStatistics as RS
import numpy as np
import os
import time
import multiprocessing

def getOprlistByPeriod(oprResultPath,setname,startdate,enddate):
    '''
    根据setname和month，从result结果中取当月的操作集，并返回df
    :param setname:
    :param month:
    :return:
    '''
    os.chdir(oprResultPath)
    starttime = startdate + ' 00:00:00'
    endtime = enddate + ' 00:00:00'
    startutc = float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
    endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))
    filename=("%s.csv"%(setname))
    oprdf=pd.read_csv(filename)
    oprdf=oprdf.loc[(oprdf['openutc'] >= startutc) & (oprdf['openutc'] < endutc)]
    oprdf = oprdf.reset_index(drop=True)
    return oprdf[['opentime','openutc','openindex','openprice','closetime','closeutc','closeindex','closeprice','tradetype','ret','ret_r']]


def calResult(resultpath,oprdf,symbol,K_MIN,setname,enddate,savedata=False):
    os.chdir(resultpath)
    margin_rate = 0.2
    commission_ratio = 0.00012
    initial_cash = 20000
    firsttradecash = initial_cash / margin_rate
    oprdf['commission_fee'] = firsttradecash * commission_ratio * 2
    oprdf['funcuve'] = firsttradecash
    oprdf['per earn'] = 0  # 单笔盈亏
    oprdf['own cash'] = 0  # 自有资金线
    oprdf['trade money'] = 0  # 杠杆后的可交易资金线
    oprdf['retrace rate'] = 0  # 回撤率

    oprdf.ix[0, 'funcuve'] = firsttradecash * (1 + oprdf.ix[0, 'ret_r']) - 60
    oprdf.ix[0, 'per earn'] = firsttradecash * oprdf.ix[0, 'ret_r']
    maxcash = initial_cash + oprdf.ix[0, 'per earn'] - oprdf.ix[0, 'commission_fee']
    oprdf.ix[0, 'own cash'] = maxcash
    oprdf.ix[0, 'trade money'] = oprdf.ix[0, 'own cash'] / margin_rate
    oprtimes = oprdf.shape[0]
    for i in np.arange(1, oprtimes):
        oprdf.ix[i, 'funcuve'] = oprdf.ix[i - 1, 'funcuve'] * (1 + oprdf.ix[i, 'ret_r']) - 60
        commission = oprdf.ix[i - 1, 'trade money'] * commission_ratio * 2
        perearn = oprdf.ix[i - 1, 'trade money'] * oprdf.ix[i, 'ret_r']
        owncash = oprdf.ix[i - 1, 'own cash'] + perearn - commission
        maxcash = max(maxcash, owncash)
        retrace_rate = (maxcash - owncash) / maxcash
        oprdf.ix[i, 'own cash'] = owncash
        oprdf.ix[i, 'commission_fee'] = commission
        oprdf.ix[i, 'per earn'] = perearn
        oprdf.ix[i, 'trade money'] = owncash / margin_rate
        oprdf.ix[i, 'retrace rate'] = retrace_rate

    if savedata:
        tofilename = ("%s%d %s result_%s.csv" % (symbol, K_MIN, setname, enddate))
        oprdf.to_csv('OprResult' + enddate + '\\' + tofilename)
    annual = RS.annual_return(oprdf)
    sharpe = RS.sharpe_ratio(oprdf)
    average_change = RS.average_change(oprdf)
    successrate = RS.success_rate(oprdf)
    max_successive_up, max_successive_down = RS.max_successive_up(oprdf)
    max_return, min_return = RS.max_period_return(oprdf)
    endcash = oprdf.ix[oprtimes - 1, 'own cash']
    mincash = oprdf['own cash'].min()
    maxcash = oprdf['own cash'].max()
    return [setname, oprtimes, annual, sharpe, average_change, successrate, max_successive_up,
                       max_successive_down, max_return, min_return, endcash, mincash, maxcash]

def runPara(symbol,K_MIN,oprResultPath,setname,startdate,enddate,savedata=False):
    print setname
    oprdf = getOprlistByPeriod(oprResultPath, setname, startdate, enddate)
    return calResult(oprResultPath, oprdf, symbol,K_MIN,setname, enddate, savedata)

def calBacktestResult(symbol,K_MIN,oprResultPath,parasetList,datelist,savedata=False):
    os.chdir(oprResultPath)
    #filnamelist = os.listdir(resultpath)
    for dates in datelist:
        startdate=dates[0]
        enddate = dates[1]
        os.mkdir('OprResult'+enddate)
        resultlist = []
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for set in parasetList:
            setname=symbol+str(K_MIN)+set
            l.append(pool.apply_async(runPara,(symbol, K_MIN, oprResultPath, setname, startdate,enddate,savedata)))
        pool.close()
        pool.join()

        # 显示结果
        for res in l:
            resultlist.append(res.get())
        groupResultDf=pd.DataFrame(resultlist,columns=['Setname','opentimes','annual','sharpe','average_change','success_rate',
                                                            'max_successive_up','max_successive_down','max_return','min_return','endcash','mincash','maxcash'])
        tofilename = ("OprResult%s\\%s%d finnalresult_%s.csv" % (enddate,symbol, K_MIN, enddate))
        groupResultDf.to_csv(tofilename)

if __name__ == '__main__':
    resultpath = 'D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I 3600\\ForwardOprAnalyze\\'
    symbol='DCE.I'
    K_MIN=3600
    parasetlist = pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\RankWinSet.csv').Setname
    datelist=[['2017-01-01','2018-01-01']]
    calBacktestResult(symbol,K_MIN,resultpath,parasetlist,datelist,True)