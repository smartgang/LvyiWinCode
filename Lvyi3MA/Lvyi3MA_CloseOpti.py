# -*- coding: utf-8 -*-

import DynamicStopLoss as dsl
import OnceWinNoLoss as ownl
import FixRateStopLoss as frsl
import DslOwnlClose as dslownl
import MultiStopLoss as msl
import DATA_CONSTANTS as DC
import pandas as pd
import os
import numpy as np
import multiprocessing
import Lvyi3MA_Parameter as Parameter
import time


def bar1mPrepare(bar1m):
    bar1m['longHigh'] = bar1m['high']
    bar1m['shortHigh'] = bar1m['high']
    bar1m['longLow'] = bar1m['low']
    bar1m['shortLow'] = bar1m['low']
    bar1m['highshift1'] = bar1m['high'].shift(1).fillna(0)
    bar1m['lowshift1'] = bar1m['low'].shift(1).fillna(0)
    bar1m.loc[bar1m['open'] < bar1m['close'], 'longHigh'] = bar1m['highshift1']
    bar1m.loc[bar1m['open'] > bar1m['close'], 'shortLow'] = bar1m['lowshift1']
    bar1m.drop('highshift1', axis=1, inplace=True)
    bar1m.drop('lowshift1', axis=1, inplace=True)
    bar1m['Unnamed: 0'] = range(bar1m.shape[0])

    """
    bar=pd.DataFrame()
    bar['longHigh']=bar1m['longHigh']
    bar['longLow']=bar1m['longLow']
    bar['shortHigh']=bar1m['shortHigh']
    bar['shortLow']=bar1m['shortLow']
    bar['strtime']=bar1m['strtime']
    bar['utc_time']=bar1m['utc_time']
    #bar['Unnamed: 0']=bar1m['Unnamed: 0']
    bar['Unnamed: 0'] = range(bar1m.shape[0])
    bar['high']=bar1m['high']
    bar['low']=bar1m['low']
    return bar
    """
    return bar1m


def test1(strategyName, symbolInfo, K_MIN, setname, bar1mdic, barxmdic, positionRatio, initialCash, stoplossTarget, dslFolderName, indexcols, timestart):
    # print 'sl;', str(slTarget), ',setname:', setname
    # timestart = time.time()
    # symbol=symbolInfo.domain_symbol
    # bar1m = q.get()
    symbol = 'SHFE.RB'

    oprdf = pd.read_csv(strategyName + ' ' + symbol + str(K_MIN) + ' ' + setname + ' result.csv')

    # timeopr = time.time()
    # print ("%s oprtime %.3f" % (setname,timeopr - timestart))
    symbolDomainDic = symbolInfo.amendSymbolDomainDicByOpr(oprdf)
    # timeamend = time.time()
    # print ("%s amendtime %.3f" % (setname,timeamend - timeopr))
    bar1m = DC.getDomainbarByDomainSymbol(symbolInfo.getSymbolList(), bar1mdic, symbolDomainDic)
    # timebar1m = time.time()
    # print("%s bar1mtime %.3f" % (setname,timebar1m - timeamend))
    bar1m = bar1mPrepare(bar1m)
    # timepre1m = time.time()
    # print ("%s preparetime %.3f" % (setname,timepre1m - timebar1m))
    barxm = DC.getDomainbarByDomainSymbol(symbolInfo.getSymbolList(), barxmdic, symbolDomainDic)
    # timexm = time.time()
    # print ("%s barxm %.3f" % (setname, timexm - timepre1m))

    a = bar1m.iloc[-1]['open']
    b = barxm.iloc[-1]['open']
    time1 = time.time()
    print ("Enter %s %.3f" % (setname, time1 - timestart))
    time.sleep(1)
    time1 = time.time()
    print ("%s opr_prepare: %.3f" % (setname, time1 - timestart))
    """
    oprdf['new_closeprice'] = oprdf['closeprice']
    oprdf['new_closetime'] = oprdf['closetime']
    oprdf['new_closeindex'] = oprdf['closeindex']
    oprdf['new_closeutc'] = oprdf['closeutc']
    oprdf['max_opr_gain'] = 0 #本次操作期间的最大收益
    oprdf['min_opr_gain'] = 0#本次操作期间的最小收益
    oprdf['max_dd'] = 0
    oprnum = oprdf.shape[0]
    """
    time.sleep(1)
    time1 = time.time()
    print ("%s priceTick: %.3f" % (setname, time1 - timestart))
    # pricetick = symbolInfo.getPriceTick()
    # pricetick = 1
    # worknum=0
    time1 = time.time()
    print ("%s dsl: %.3f" % (setname, time1 - timestart))
    time.sleep(1)
    """
    for i in range(oprnum):
        opr = oprdf.iloc[i]
        startutc = (barxm.loc[barxm['utc_time'] == opr.openutc]).iloc[0].utc_endtime - 60#从开仓的10m线结束后开始
        endutc = (barxm.loc[barxm['utc_time'] == opr.closeutc]).iloc[0].utc_endtime#一直到平仓的10m线结束
        oprtype = opr.tradetype
        openprice = opr.openprice
        data1m = bar1m.loc[(bar1m['utc_time'] >= startutc) & (bar1m['utc_time'] < endutc)]
        if oprtype == 1:
            # 多仓，取最大回撤，max为最大收益，min为最小收益
            max_dd, dd_close, maxprice, strtime, utctime, timeindex = getLongDrawbackByTick(data1m, slTarget)
            oprdf.ix[i, 'max_opr_gain'] = (data1m.high.max() - openprice) / openprice#1min用close,tick用high和low
            oprdf.ix[i, 'min_opr_gain'] = (data1m.low.min() - openprice) / openprice
            oprdf.ix[i, 'max_dd'] = max_dd
            if max_dd <= slTarget:
                ticknum = round((maxprice * slTarget) / pricetick, 0) - 1
                oprdf.ix[i, 'new_closeprice'] = maxprice + ticknum * pricetick
                oprdf.ix[i, 'new_closetime'] = strtime
                oprdf.ix[i, 'new_closeindex'] = timeindex
                oprdf.ix[i, 'new_closeutc'] = utctime
                worknum+=1

        else:
            # 空仓，取逆向最大回撤，min为最大收益，max为最小收闪
            max_dd, dd_close, minprice, strtime, utctime, timeindex = getShortDrawbackByTick(data1m, slTarget)
            oprdf.ix[i, 'max_opr_gain'] = (openprice - data1m.low.min()) / openprice
            oprdf.ix[i, 'min_opr_gain'] = (openprice - data1m.high.max()) / openprice
            oprdf.ix[i, 'max_dd'] = max_dd
            if max_dd <= slTarget:
                ticknum = round((minprice * slTarget) / pricetick, 0) - 1
                oprdf.ix[i, 'new_closeprice'] = minprice - ticknum * pricetick
                oprdf.ix[i, 'new_closetime'] = strtime
                oprdf.ix[i, 'new_closeindex'] = timeindex
                oprdf.ix[i, 'new_closeutc'] = utctime
                worknum+=1
    """
    # timedsl = time.time()
    # print ("%s timedsl %.3f" % (setname, timedsl - timexm))
    time1 = time.time()
    print ("%s finish: %.3f" % (setname, time1 - timestart))
    # slip = symbolInfo.getSlip()
    # slip = 1
    # 2017-12-08:加入滑点
    """
    print ("%s calcResult" % setname)
    oprdf['new_ret'] = ((oprdf['new_closeprice'] - oprdf['openprice']) * oprdf['tradetype']) - slip
    oprdf['new_ret_r'] = oprdf['new_ret'] / oprdf['openprice']
    oprdf['new_commission_fee'], oprdf['new_per earn'], oprdf['new_own cash'], oprdf['new_hands'] = RS.calcResult(oprdf,
                                                                                                      symbolInfo,
                                                                                                      initialCash,
                                                                                                      positionRatio,ret_col='new_ret')
    #timecalResult = time.time()
    #print ("%s timecalResult %.3f" % (setname, timecalResult - timedsl))
    #保存新的result文档
    oprdf.to_csv(tofolder+strategyName+' '+symbol + str(K_MIN) + ' ' + setname + ' resultDSL_by_tick.csv', index=False)

    print ("%s calcRS" % setname)
    olddailydf = pd.read_csv(strategyName + ' ' + symbol + str(K_MIN) + ' ' + setname + ' dailyresult.csv',index_col='date')
    #计算统计结果
    oldr = RS.getStatisticsResult(oprdf, False, indexcols,olddailydf)

    dailyK=DC.generatDailyClose(barxm)
    dR = RS.dailyReturn(symbolInfo, oprdf, dailyK, initialCash)  # 计算生成每日结果
    dR.calDailyResult()
    dR.dailyClose.to_csv((tofolder+strategyName + ' ' + symbol + str(K_MIN) + ' ' + setname + ' dailyresultDSL_by_tick.csv'), index=False)
    newr = RS.getStatisticsResult(oprdf,True,indexcols,dR.dailyClose)
    #timefinal = time.time()
    #print ("%s timefinal %.3f" % (setname, timefinal - timecalResult))
    #print ("%s totaltime %.3f" % (setname, timefinal - timestart))
    #print ("%s done!" % setname)
    del oprdf
    #return [setname,slTarget,worknum,oldendcash,oldAnnual,oldSharpe,oldDrawBack,oldSR,newendcash,newAnnual,newSharpe,newDrawBack,newSR,max_single_loss_rate]
    print ("%s finish" % setname)
    return [setname,slTarget,worknum]+oldr+newr
    """
    return 0


def getDSL(strategyName, symbolInfo, K_MIN, stoplossList, parasetlist, bar1mdic, barxmdic, positionRatio, initialCash, indexcols, progress=False):
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    allresultdf_cols = ['setname', 'slTarget', 'worknum'] + indexcols + new_indexcols
    allresultdf = pd.DataFrame(columns=allresultdf_cols)

    allnum = 0
    paranum = parasetlist.shape[0]
    for stoplossTarget in stoplossList:
        timestart = time.time()
        dslFolderName = "DynamicStopLoss" + str(stoplossTarget * 1000)
        try:
            os.mkdir(dslFolderName)  # 创建文件夹
        except:
            # print 'folder already exist'
            pass
        print ("stoplossTarget:%f" % stoplossTarget)

        resultdf = pd.DataFrame(columns=allresultdf_cols)
        setnum = 0
        numlist = range(0, paranum, 100)
        numlist.append(paranum)
        for n in range(1, len(numlist)):
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for a in range(numlist[n - 1], numlist[n]):
                setname = parasetlist.ix[a, 'Setname']
                if not progress:
                    # l.append(dsl.dslCal(strategyName,symbolInfo, K_MIN, setname, oprdflist[a-a0], bar1mlist[a-a0], barxmlist[a-a0], positionRatio, initialCash, stoplossTarget, dslFolderName + '\\',
                    #                                       indexcols))
                    l.append(pool.apply_async(dsl.dslCal, (strategyName, symbolInfo, K_MIN, setname, bar1mdic, barxmdic, positionRatio, initialCash, stoplossTarget,
                                                           dslFolderName + '\\', indexcols)))
                else:
                    # l.append(dsl.progressDslCal(strategyName,symbolInfo, K_MIN, setname, bar1m, barxm, pricetick,
                    #                                               positionRatio, initialCash, stoplossTarget,
                    #                                               dslFolderName + '\\'))
                    l.append(pool.apply_async(dsl.progressDslCal, (strategyName,
                                                                   symbolInfo, K_MIN, setname, bar1mdic, barxmdic, positionRatio, initialCash, stoplossTarget,
                                                                   dslFolderName + '\\',indexcols)))
            pool.close()
            pool.join()
            for res in l:
                resultdf.loc[setnum] = res.get()
                allresultdf.loc[allnum] = resultdf.loc[setnum]
                setnum += 1
                allnum += 1
        resultdf.to_csv(dslFolderName + '\\' + strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_dsl' + str(stoplossTarget) + '.csv', index=False)
        timeend = time.time()
        timecost = timeend - timestart
        print (u"dsl_%.3f 计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (stoplossTarget,paranum, timecost, timecost / paranum))
    allresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_dsl.csv', index=False)


def getOwnl(strategyName, symbolInfo, K_MIN, winSwitchList, nolossThreshhold, parasetlist, bar1mdic, barxmdic, positionRatio, initialCash, indexcols, progress=False):
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    allresultdf_cols = ['setname', 'winSwitch', 'worknum'] + indexcols + new_indexcols
    ownlallresultdf = pd.DataFrame(columns=allresultdf_cols)
    allnum = 0
    paranum = parasetlist.shape[0]
    for winSwitch in winSwitchList:
        timestart = time.time()
        ownlFolderName = "OnceWinNoLoss" + str(winSwitch * 1000)
        try:
            os.mkdir(ownlFolderName)  # 创建文件夹
        except:
            # print "dir already exist!"
            pass
        print ("OnceWinNoLoss WinSwitch:%f" % winSwitch)

        ownlresultdf = pd.DataFrame(columns=allresultdf_cols)

        setnum = 0
        numlist = range(0, paranum, 100)
        numlist.append(paranum)
        for n in range(1, len(numlist)):
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for a in range(numlist[n - 1], numlist[n]):
                setname = parasetlist.ix[a, 'Setname']
                if not progress:
                    l.append(pool.apply_async(ownl.ownlCal,
                                              (strategyName, symbolInfo, K_MIN, setname, bar1mdic, barxmdic, winSwitch, nolossThreshhold, positionRatio, initialCash,
                                               ownlFolderName + '\\', indexcols)))
                else:
                    # l.append(ownl.progressOwnlCal(strategyName, symbolInfo, K_MIN, setname, bar1m, barxm, winSwitch,
                    #                           nolossThreshhold, positionRatio, initialCash,
                    #                           ownlFolderName + '\\'))
                    l.append(pool.apply_async(ownl.progressOwnlCal,
                                              (strategyName, symbolInfo, K_MIN, setname, bar1mdic, barxmdic, winSwitch, nolossThreshhold, positionRatio, initialCash,
                                               ownlFolderName + '\\', indexcols)))
            pool.close()
            pool.join()

            for res in l:
                ownlresultdf.loc[setnum] = res.get()
                ownlallresultdf.loc[allnum] = ownlresultdf.loc[setnum]
                setnum += 1
                allnum += 1
        # ownlresultdf['cashDelta'] = ownlresultdf['new_endcash'] - ownlresultdf['old_endcash']
        ownlresultdf.to_csv(ownlFolderName + '\\' + strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_ownl' + str(winSwitch) + '.csv', index=False)
        timeend = time.time()
        timecost = timeend - timestart
        print (u"ownl_%.3f 计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (winSwitch,paranum, timecost, timecost / paranum))
    # ownlallresultdf['cashDelta'] = ownlallresultdf['new_endcash'] - ownlallresultdf['old_endcash']
    ownlallresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_ownl.csv', index=False)


def getFRSL(strategyName, symbolInfo, K_MIN, fixRateList, parasetlist, bar1mdic, barxmdic, positionRatio, initialCash, indexcols, progress=False):
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    allresultdf = pd.DataFrame(columns=['setname', 'fixRate', 'worknum'] + indexcols + new_indexcols)
    allnum = 0
    paranum = parasetlist.shape[0]
    for fixRateTarget in fixRateList:
        timestart = time.time()
        folderName = "FixRateStopLoss" + str(fixRateTarget * 1000)
        try:
            os.mkdir(folderName)  # 创建文件夹
        except:
            # print 'folder already exist'
            pass
        print ("fixRateTarget:%f" % fixRateTarget)

        resultdf = pd.DataFrame(columns=['setname', 'fixRate', 'worknum'] + indexcols + new_indexcols)
        setnum = 0
        numlist = range(0, paranum, 100)
        numlist.append(paranum)
        for n in range(1, len(numlist)):
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for a in range(numlist[n - 1], numlist[n]):
                setname = parasetlist.ix[a, 'Setname']
                if not progress:
                    # l.append(frsl.frslCal(strategyName,
                    #                                       symbolInfo, K_MIN, setname, bar1m, barxm, fixRateTarget, positionRatio,initialCash, folderName + '\\'))
                    l.append(pool.apply_async(frsl.frslCal, (strategyName,
                                                             symbolInfo, K_MIN, setname, bar1mdic, barxmdic, fixRateTarget, positionRatio, initialCash, folderName + '\\',
                                                             indexcols)))
                else:
                    l.append(pool.apply_async(frsl.progressFrslCal, (strategyName,
                                                                     symbolInfo, K_MIN, setname, bar1mdic, barxmdic, fixRateTarget, positionRatio, initialCash, folderName + '\\',
                                                                     indexcols)))
            pool.close()
            pool.join()

            for res in l:
                resultdf.loc[setnum] = res.get()
                allresultdf.loc[allnum] = resultdf.loc[setnum]
                setnum += 1
                allnum += 1
        # resultdf['cashDelta'] = resultdf['new_endcash'] - resultdf['old_endcash']
        resultdf.to_csv(folderName + '\\' + strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_frsl' + str(fixRateTarget) + '.csv', index=False)
        timeend = time.time()
        timecost = timeend - timestart
        print (u"frsl_%.3f 计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (fixRateTarget,paranum, timecost, timecost / paranum))
    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_frsl.csv', index=False)


def getDslOwnl(strategyName, symbolInfo, K_MIN, parasetlist, stoplossList, winSwitchList, positionRatio, initialCash, indexcols):
    symbol = symbolInfo.domain_symbol
    allresultdf = pd.DataFrame(
        columns=['setname', 'dslTarget', 'ownlWinSwtich', 'old_endcash', 'old_Annual', 'old_Sharpe', 'old_Drawback',
                 'old_SR', 'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                 'dslWorknum', 'ownlWorknum', 'dslRetDelta', 'ownlRetDelta'])
    allnum = 0
    paranum = parasetlist.shape[0]
    for stoplossTarget in stoplossList:
        for winSwitch in winSwitchList:
            dslFolderName = "DynamicStopLoss" + str(stoplossTarget * 1000) + '\\'
            ownlFolderName = "OnceWinNoLoss" + str(winSwitch * 1000) + '\\'
            newfolder = ("dsl_%.3f_ownl_%.3f" % (stoplossTarget, winSwitch))
            try:
                os.mkdir(newfolder)  # 创建文件夹
            except:
                # print newfolder, ' already exist!'
                pass
            print ("slTarget:%f ownlSwtich:%f" % (stoplossTarget, winSwitch))
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for sn in range(0, paranum):
                setname = parasetlist.ix[sn, 'Setname']
                l.append(pool.apply_async(dslownl.dslAndownlCal,
                                          (strategyName, symbolInfo, K_MIN, setname, stoplossTarget, winSwitch, positionRatio, initialCash, dslFolderName,
                                           ownlFolderName, newfolder + '\\')))
            pool.close()
            pool.join()

            resultdf = pd.DataFrame(
                columns=['setname', 'dslTarget', 'ownlWinSwtich', 'old_endcash', 'old_Annual', 'old_Sharpe',
                         'old_Drawback',
                         'old_SR', 'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                         'dslWorknum', 'ownlWorknum', 'dslRetDelta', 'ownlRetDelta'])
            i = 0
            for res in l:
                resultdf.loc[i] = res.get()
                allresultdf.loc[allnum] = resultdf.loc[i]
                i += 1
                allnum += 1
            resultfilename = ("%s %s%d finalresult_dsl%.3f_ownl%.3f.csv" % (strategyName, symbol, K_MIN, stoplossTarget, winSwitch))
            resultdf.to_csv(newfolder + '\\' + resultfilename)

    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_dsl_ownl.csv')


def getMultiSLT(strategyName, symbolInfo, K_MIN, parasetlist, barxmdic, sltlist, positionRatio, initialCash, indexcols):
    """
    计算多个止损策略结合回测的结果
    :param strategyName:
    :param symbolInfo:
    :param K_MIN:
    :param parasetlist:
    :param sltlist:
    :param positionRatio:
    :param initialCash:
    :return:
    """
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    allresultdf_cols = ['setname', 'slt', 'slWorkNum'] + indexcols + new_indexcols
    allresultdf = pd.DataFrame(columns=allresultdf_cols)

    allnum = 0
    paranum = parasetlist.shape[0]

    # dailyK = DC.generatDailyClose(barxm)

    # 先生成参数列表
    allSltSetList = []  # 这是一个二维的参数列表，每一个元素是一个止损目标的参数dic列表
    for slt in sltlist:
        sltset = []
        for t in slt['paralist']:
            sltset.append({'name': slt['name'],
                           'sltValue': t,
                           'folder': slt['folderPrefix'] + str(t * 1000) + '\\',
                           'fileSuffix': slt['fileSuffix']
                           })
        allSltSetList.append(sltset)
    finalSltSetList = []  # 二维数据，每个一元素是一个多个止损目标的参数dic组合
    for sltpara in allSltSetList[0]:
        finalSltSetList.append([sltpara])
    for i in range(1, len(allSltSetList)):
        tempset = allSltSetList[i]
        newset = []
        for o in finalSltSetList:
            for t in tempset:
                newset.append(o + [t])
        finalSltSetList = newset
    print finalSltSetList

    for sltset in finalSltSetList:
        newfolder = ''
        for sltp in sltset:
            newfolder += (sltp['name'] + '_%.3f' % (sltp['sltValue']))
        try:
            os.mkdir(newfolder)  # 创建文件夹
        except:
            pass
        print (newfolder)
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for sn in range(0, paranum):
            setname = parasetlist.ix[sn, 'Setname']
            # l.append(msl.multiStopLosslCal(strategyName, symbolInfo, K_MIN, setname, sltset, barxmdic, positionRatio, initialCash,
            #                           newfolder, indexcols))
            l.append(pool.apply_async(msl.multiStopLosslCal,
                                      (strategyName, symbolInfo, K_MIN, setname, sltset, barxmdic, positionRatio, initialCash, newfolder, indexcols)))
        pool.close()
        pool.join()

        resultdf = pd.DataFrame(columns=allresultdf_cols)
        i = 0
        for res in l:
            resultdf.loc[i] = res.get()
            allresultdf.loc[allnum] = resultdf.loc[i]
            i += 1
            allnum += 1
        resultfilename = ("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, newfolder))
        resultdf.to_csv(newfolder + '\\' + resultfilename, index=False)

    allresultname = ''
    for slt in sltlist:
        allresultname += slt['name']
    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, allresultname), index=False)
    pass


if __name__ == '__main__':
    # 文件路径
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName

    # 取参数集
    parasetlist = pd.read_csv(resultpath + Parameter.parasetname)
    paranum = parasetlist.shape[0]

    # indexcols
    indexcols = Parameter.ResultIndexDic

    # 参数设置
    strategyParameterSet = []
    if not Parameter.symbol_KMIN_opt_swtich:
        # 单品种单周期模式
        paradic = {
            'strategyName': Parameter.strategyName,
            'exchange_id': Parameter.exchange_id,
            'sec_id': Parameter.sec_id,
            'K_MIN': Parameter.K_MIN,
            'startdate': Parameter.startdate,
            'enddate': Parameter.enddate,
            'positionRatio': Parameter.positionRatio,
            'initialCash': Parameter.initialCash,
            'progress': Parameter.progress_close,
            'calcDsl': Parameter.calcDsl_close,
            'calcOwnl': Parameter.calcOwnl_close,
            'calcFrsl': Parameter.calcFrsl_close,
            'calcMultiSLT': Parameter.calcMultiSLT_close,
            'calcDslOwnl': Parameter.calcDslOwnl_close,
            'dslStep': Parameter.dslStep_close,
            'dslTargetStart': Parameter.dslTargetStart_close,
            'dslTargetEnd': Parameter.dslTargetEnd_close,
            'ownlStep': Parameter.ownlStep_close,
            'ownlTargetStart': Parameter.ownlTargetStart_close,
            'ownltargetEnd': Parameter.ownltargetEnd_close,
            'nolossThreshhold': Parameter.nolossThreshhold_close,
            'frslStep': Parameter.frslStep_close,
            'frslTargetStart': Parameter.frslTargetStart_close,
            'frslTargetEnd': Parameter.frslTragetEnd_close
        }
        strategyParameterSet.append(paradic)
    else:
        # 多品种多周期模式
        symbolset = pd.read_excel(resultpath + Parameter.stoploss_set_filename, index_col='No')
        symbolsetNum = symbolset.shape[0]
        for i in range(symbolsetNum):
            exchangeid = symbolset.ix[i, 'exchange_id']
            secid = symbolset.ix[i, 'sec_id']
            strategyParameterSet.append({
                'strategyName': symbolset.ix[i, 'strategyName'],
                'exchange_id': exchangeid,
                'sec_id': secid,
                'K_MIN': symbolset.ix[i, 'K_MIN'],
                'startdate': symbolset.ix[i, 'startdate'],
                'enddate': symbolset.ix[i, 'enddate'],
                'positionRatio': Parameter.positionRatio,
                'initialCash': Parameter.initialCash,
                'progress': symbolset.ix[i, 'progress'],
                'calcDsl': symbolset.ix[i, 'calcDsl'],
                'calcOwnl': symbolset.ix[i, 'calcOwnl'],
                'calcFrsl': symbolset.ix[i, 'calcFrsl'],
                'calcMultiSLT': symbolset.ix[i, 'calcMultiSLT'],
                'calcDslOwnl': symbolset.ix[i, 'calcDslOwnl'],
                'dslStep': symbolset.ix[i, 'dslStep'],
                'dslTargetStart': symbolset.ix[i, 'dslTargetStart'],
                'dslTargetEnd': symbolset.ix[i, 'dslTargetEnd'],
                'ownlStep': symbolset.ix[i, 'ownlStep'],
                'ownlTargetStart': symbolset.ix[i, 'ownlTargetStart'],
                'ownltargetEnd': symbolset.ix[i, 'ownltargetEnd'],
                'nolossThreshhold': symbolset.ix[i, 'nolossThreshhold'],
                'frslStep': symbolset.ix[i, 'frslStep'],
                'frslTargetStart': symbolset.ix[i, 'frslTargetStart'],
                'frslTargetEnd': symbolset.ix[i, 'frslTargetEnd']
            }
            )

    for strategyParameter in strategyParameterSet:

        strategyName = strategyParameter['strategyName']
        exchange_id = strategyParameter['exchange_id']
        sec_id = strategyParameter['sec_id']
        K_MIN = strategyParameter['K_MIN']
        startdate = strategyParameter['startdate']
        enddate = strategyParameter['enddate']
        domain_symbol = '.'.join([exchange_id, sec_id])

        positionRatio = strategyParameter['positionRatio']
        initialCash = strategyParameter['initialCash']

        symbolinfo = DC.SymbolInfo(domain_symbol, startdate, enddate)
        pricetick = symbolinfo.getPriceTick()

        # 计算控制开关
        progress = strategyParameter['progress']
        calcDsl = strategyParameter['calcDsl']
        calcOwnl = strategyParameter['calcOwnl']
        calcFrsl = strategyParameter['calcFrsl']
        calcMultiSLT = strategyParameter['calcMultiSLT']
        calcDslOwnl = strategyParameter['calcDslOwnl']

        # 优化参数
        dslStep = strategyParameter['dslStep']
        stoplossList = np.arange(strategyParameter['dslTargetStart'], strategyParameter['dslTargetEnd'], dslStep)
        # stoplossList=[-0.022]
        ownlStep = strategyParameter['ownlStep']
        winSwitchList = np.arange(strategyParameter['ownlTargetStart'], strategyParameter['ownltargetEnd'], ownlStep)
        # winSwitchList=[0.009]
        nolossThreshhold = strategyParameter['nolossThreshhold'] * pricetick
        frslStep = strategyParameter['frslStep']
        fixRateList = np.arange(strategyParameter['frslTargetStart'], strategyParameter['frslTargetEnd'], frslStep)

        # 文件路径
        foldername = ' '.join([strategyName, exchange_id, sec_id, str(K_MIN)])
        oprresultpath = resultpath + foldername + '\\'
        os.chdir(oprresultpath)

        # 原始数据处理
        # bar1m=DC.getBarData(symbol=symbol,K_MIN=60,starttime=startdate+' 00:00:00',endtime=enddate+' 23:59:59')
        # barxm=DC.getBarData(symbol=symbol,K_MIN=K_MIN,starttime=startdate+' 00:00:00',endtime=enddate+' 23:59:59')
        # bar1m计算longHigh,longLow,shortHigh,shortLow
        # bar1m=bar1mPrepare(bar1m)
        # bar1mdic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), 60, startdate, enddate)
        # barxmdic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), K_MIN, startdate, enddate)
        cols = ['open', 'high', 'low', 'close', 'strtime', 'utc_time', 'utc_endtime']
        bar1mdic = DC.getBarDic(symbolinfo, 60, cols)
        barxmdic = DC.getBarDic(symbolinfo, K_MIN, cols)

        if calcMultiSLT:
            sltlist = []
            if calcDsl:
                sltlist.append({'name': 'dsl',
                                'paralist': stoplossList,
                                'folderPrefix': 'DynamicStopLoss',
                                'fileSuffix': 'resultDSL_by_tick.csv'})
            if calcOwnl:
                sltlist.append({'name': 'ownl',
                                'paralist': winSwitchList,
                                'folderPrefix': 'OnceWinNoLoss',
                                'fileSuffix': 'resultOWNL_by_tick.csv'})
            if calcFrsl:
                sltlist.append({'name': 'frsl',
                                'paralist': fixRateList,
                                'folderPrefix': 'FixRateStopLoss',
                                'fileSuffix': 'resultFRSL_by_tick.csv'})
            getMultiSLT(strategyName, symbolinfo, K_MIN, parasetlist, barxmdic, sltlist, positionRatio, initialCash, indexcols)
        else:
            if calcDsl:
                getDSL(strategyName, symbolinfo, K_MIN, stoplossList, parasetlist, bar1mdic, barxmdic, positionRatio, initialCash, indexcols, progress)

            if calcOwnl:
                getOwnl(strategyName, symbolinfo, K_MIN, winSwitchList, nolossThreshhold, parasetlist, bar1mdic, barxmdic, positionRatio, initialCash, indexcols, progress)

            if calcFrsl:
                getFRSL(strategyName, symbolinfo, K_MIN, fixRateList, parasetlist, bar1mdic, barxmdic, positionRatio, initialCash, indexcols, progress)

            if calcDslOwnl:
                getDslOwnl(strategyName, symbolinfo, K_MIN, parasetlist, stoplossList, winSwitchList, positionRatio, initialCash, indexcols)
