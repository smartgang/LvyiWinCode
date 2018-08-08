# -*- coding: utf-8 -*-
'''
LvyiWin辅助功能
'''
import pandas as pd
import numpy as np
import os
import LvyiWin_Parameter as Parameter
import DATA_CONSTANTS as DC
import time
from datetime import datetime
import ResultStatistics as RS

def resultCalc():
    '''
    重新统计多品种多周期的回测结果
    将各文件夹中的finalResult文件汇总到一起
    :return:
    '''
    upperpath=DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    allsymbolresult = pd.DataFrame(columns=
                                   ['Setname', 'MA_Short', 'MA_Long', 'KDJ_N', 'DMI_N', 'opentimes', 'end_cash',
                                    'SR', 'Annual', 'Sharpe', 'DrawBack', 'max_single_loss_rate',
                                    'strategyName', 'exchange_id', 'sec_id', 'K_MIN'])
    symbolset = pd.read_excel(resultpath + Parameter.symbol_KMIN_set_filename)
    symbolsetNum = symbolset.shape[0]
    for i in range(symbolsetNum):
        strategyName=symbolset.ix[i, 'strategyName']
        exchangeid = symbolset.ix[i, 'exchange_id']
        secid = symbolset.ix[i, 'sec_id']
        symbol = '.'.join([exchangeid, secid])
        K_MIN=symbolset.ix[i, 'K_MIN']
        foldername=' '.join([strategyName, exchangeid, secid, str(K_MIN)])
        print ("collecting %s %d final results"%(symbol,K_MIN))
        result = pd.read_csv(foldername+'\\'+"%s %d finalresults.csv" % (symbol, K_MIN))
        result['strategyName']=strategyName
        result['exchange_id']=exchangeid
        result['sec_id'] = secid
        result['K_MIN'] = K_MIN
        allsymbolresult=pd.concat([allsymbolresult,result])

    allsymbolresult.to_csv(Parameter.strategyName + "_symbol_KMIN_results.csv")
    pass

def successiveEarnDistribut(resultdf,filename,new=True):
    '''连续盈亏分布统计'''
    if new:
        ret_col='new_ret'
    else:
        ret_col='ret'
    df1 = pd.DataFrame()
    df1[ret_col] = resultdf[ret_col]
    df1['tradetype'] = resultdf['tradetype']
    df1['oprindex'] = np.arange(df1.shape[0])
    df1['win'] = -1
    df1.loc[df1[ret_col] > 0, 'win'] = 1
    df1['win_shift1'] = df1['win'].shift(1).fillna(0)
    df1['win_cross'] = 0
    df1.loc[df1['win'] != df1['win_shift1'], 'win_cross'] = df1['oprindex']
    df1.ix[0, 'win_cross'] = 1
    df2 = pd.DataFrame()
    df2['oprindex'] = df1.loc[df1['win_cross'] != 0, 'oprindex']
    df2[ret_col] = df1.loc[df1['win_cross'] != 0,ret_col]
    df2['count'] = df2['oprindex'].shift(-1).fillna(0) - df2['oprindex']
    df2.ix[df2.iloc[-1].oprindex, 'count'] = 0
    win_count = df2.loc[df2[ret_col] > 0, 'count']
    loss_count = df2.loc[df2[ret_col] <= 0, 'count']
    df2.to_csv(filename+'successiveEarnDis.csv')

def parasetGenerator():
    upperpath=DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    setlist = []
    i = 0
    for ms in [5, 6, 7]:
        for ml in [24,25,26, 27, 28, 29, 30]:
            for kn in [6, 8, 20, 22, 24, 26, 28, 30]:
                for dn in [28, 30, 32, 34, 36]:
                    setname = 'Set' + str(i) + ' MS' + str(ms) + ' ML' + str(ml) + ' KN' + str(kn) + ' DN' + str(dn)
                    l = [setname, ms, ml, kn, dn]
                    setlist.append(l)
                    i += 1

    setpd = pd.DataFrame(setlist, columns=['Setname', 'MA_Short', 'MA_Long', 'KDJ_N', 'DMI_N'])
    setpd.to_csv(resultpath+'ParameterOptSet_simple.csv')


def calResultByPeriod():
    '''
    按时间分段统计结果:
    1.设定开始和结束时间
    2.选择时间周期
    3.设定文件夹、买卖操作文件名、日结果文件名和要生成的新文件名
    :return:
    '''
    #设定开始和结束时间
    startdate = '2011-01-01'
    enddate = '2018-07-01'

    #2.选择时间周期
    #freq='YS' #按年统计
    #freq='2QS' #按半年统计
    #freq='QS' #按季度统计
    freq='MS' #按月统计，如需多个月，可以加上数据，比如2个月：2MS

    #3.设文件和文件夹状态
    filedir='D:\\002 MakeLive\myquant\LvyiWin\Results\LvyiWin SHFE RB 600\dsl_-0.018ownl_0.008\ForwardOprAnalyze\\' #文件所在文件夹
    oprfilename = 'LvyiWin SHFE.RB600_Rank4_win1_oprResult.csv' #买卖操作文件名
    dailyResultFileName = 'LvyiWin SHFE.RB600_Rank4_win1_oprdailyResult.csv' #日结果文件名
    newFileName = 'LvyiWin SHFE.RB600_Rank4_win1_result_by_Period_M.csv' #要生成的新文件名
    os.chdir(filedir)
    oprdf = pd.read_csv(oprfilename)
    dailyResultdf = pd.read_csv(dailyResultFileName)

    oprdfcols = oprdf.columns.tolist()
    if 'new_closeprice' in oprdfcols:
        newFlag = True
    else:
        newFlag = False

    monthlist = [datetime.strftime(x, '%Y-%m-%d %H:%M:%S') for x in list(pd.date_range(start=startdate, end=enddate, freq=freq, normalize=True, closed='right'))]

    if not startdate in monthlist[0]:
        monthlist.insert(0,startdate+" 00:00:00")
    if not enddate in monthlist[-1]:
        monthlist.append(enddate+" 23:59:59")
    else:
        monthlist[-1]=enddate+" 23:59:59"
    rlist=[]
    for i in range(1,len(monthlist)):
        starttime=monthlist[i-1]
        endtime = monthlist[i]
        startutc = float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
        endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))

        resultdata = oprdf.loc[(oprdf['openutc'] >= startutc) & (oprdf['openutc'] < endutc)]
        dailydata = dailyResultdf.loc[(dailyResultdf['utc_time'] >= startutc) & (dailyResultdf['utc_time'] < endutc)]
        resultdata.reset_index(drop=True,inplace=True)
        if resultdata.shape[0]>0:
            rlist.append([starttime,endtime]+RS.getStatisticsResult(resultdata, newFlag, Parameter.ResultIndexDic, dailydata))
        else:
            rlist.append([0]*len(Parameter.ResultIndexDic))
    rdf = pd.DataFrame(rlist,columns=['StartTime','EndTime']+Parameter.ResultIndexDic)
    rdf.to_csv(newFileName)


def remove_polar():
    symbol = 'SHFE.RB'
    symbolinfo = DC.SymbolInfo(symbol)
    folder = 'D:\\002 MakeLive\myquant\LvyiWin\Results\LvyiWin SHFE RB 600\dsl_-0.018ownl_0.008\ForwardOprAnalyze\\'
    filename = 'LvyiWin SHFE.RB600_Rank4_win1_oprResult.csv'
    opr = pd.read_csv(folder+filename)
    opr = RS.opr_result_remove_polar(opr, new_cols=True)
    opr['commission_fee_rp'], opr['per earn_rp'], opr['own cash_rp'], opr['hands_rp'] = RS.calcResult(result=opr, symbolinfo=symbolinfo, initialCash=200000, positionRatio=1, ret_col='new_ret')
    opr.to_csv(folder+'LvyiWin SHFE.RB600_Rank4_win1_oprResult_remove_polar.csv')

if __name__=='__main__':
    #resultCalc()
    #parasetGenerator()
    #calResultByPeriod()
    remove_polar()
