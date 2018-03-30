# -*- coding: utf-8 -*-

import DynamicStopLoss as dsl
import OnceWinNoLoss as ownl
import DslOwnlClose as dslownl
import DATA_CONSTANTS as DC
import pandas as pd
import os
import numpy as np
import multiprocessing
import Lvyi3MA_Parameter

def bar1mPrepare(bar1m):
    bar1m['longHigh'] = bar1m['high']
    bar1m['shortHigh'] = bar1m['high']
    bar1m['longLow'] = bar1m['low']
    bar1m['shortLow'] = bar1m['low']
    bar1m['highshift1'] = bar1m['high'].shift(1).fillna(0)
    bar1m['lowshift1'] = bar1m['low'].shift(1).fillna(0)
    bar1m.loc[bar1m['open'] < bar1m['close'], 'longHigh'] = bar1m['highshift1']
    bar1m.loc[bar1m['open'] > bar1m['close'], 'shortLow'] = bar1m['lowshift1']
    return bar1m

def getDSL(symbolInfo,K_MIN,stoplossList,parasetlist,bar1m,barxm):
    symbol=symbolInfo.symbol
    pricetick=symbolInfo.getPriceTick()
    slip=symbolInfo.getSlip()
    allresultdf = pd.DataFrame(
        columns=['setname', 'slTarget', 'worknum', 'old_endcash', 'old_Annual', 'old_Sharpe', 'old_Drawback',
                 'old_SR',
                 'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                 'maxSingleLoss', 'maxSingleDrawBack'])
    allnum = 0
    paranum=parasetlist.shape[0]
    for stoplossTarget in stoplossList:

        dslFolderName = "DynamicStopLoss" + str(stoplossTarget * 1000)
        try:
            os.mkdir(dslFolderName)  # 创建文件夹
        except:
            #print 'folder already exist'
            pass
        print ("stoplossTarget:%f" % stoplossTarget)

        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for sn in range(0, paranum):
            setname = parasetlist.ix[sn,'Setname']
           # l.append(dsl.dslCal(symbol, K_MIN_SAR, fullsetname, bar1m, barxm,pricetick,slip, stoplossTarget, dslFolderName + '\\'))
            l.append(pool.apply_async(dsl.dslCal,(symbol, K_MIN, setname, bar1m, barxm,pricetick,slip, stoplossTarget, dslFolderName + '\\')))
        pool.close()
        pool.join()

        resultdf=pd.DataFrame(columns=['setname','slTarget','worknum','old_endcash','old_Annual','old_Sharpe','old_Drawback','old_SR',
                                                  'new_endcash','new_Annual','new_Sharpe','new_Drawback','new_SR','maxSingleLoss','maxSingleDrawBack'])
        i = 0
        for res in l:
            resultdf.loc[i]=res.get()
            allresultdf.loc[allnum]=resultdf.loc[i]
            i+=1
            allnum+=1
        resultdf['cashDelta']=resultdf['new_endcash']-resultdf['old_endcash']
        resultdf.to_csv(dslFolderName+'\\'+symbol+str(K_MIN)+' finalresult_dsl'+str(stoplossTarget)+'.csv')

    allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(symbol + str(K_MIN)+' finalresult_dsl.csv')
    #return allresultdf

def getOwnl(symbolInfo,K_MIN,winSwitchList,nolossThreshhold,parasetlist,bar1m,barxm):
    symbol=symbolInfo.symbol
    slip=symbolInfo.getSlip()
    ownlallresultdf = pd.DataFrame(
        columns=['setname', 'winSwitch', 'worknum', 'old_endcash', 'old_Annual', 'old_Sharpe', 'old_Drawback',
                 'old_SR',
                 'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                 'maxSingleLoss', 'maxSingleDrawBack'])
    allnum=0
    for winSwitch in winSwitchList:
        ownlFolderName = "OnceWinNoLoss" + str(winSwitch * 1000)
        try:
            os.mkdir(ownlFolderName)  # 创建文件夹
        except:
            #print "dir already exist!"
            pass
        print ("OnceWinNoLoss WinSwitch:%f" % winSwitch)

        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for sn in range(0, paranum):
            setname = parasetlist.ix[sn,'Setname']
           # l.append(dsl.dslCal(symbol, K_MIN_SAR, fullsetname, bar1m, barxm,pricetick,slip, stoplossTarget, dslFolderName + '\\'))
            l.append(pool.apply_async(ownl.ownlCal,(symbol, K_MIN, setname, bar1m, barxm, winSwitch, nolossThreshhold, slip,
                         ownlFolderName + '\\')))
        pool.close()
        pool.join()

        ownlresultdf = pd.DataFrame(columns=['setname', 'winSwitch', 'worknum', 'old_endcash', 'old_Annual', 'old_Sharpe', 'old_Drawback',
                     'old_SR','new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR','maxSingleLoss', 'maxSingleDrawBack'])

        i = 0
        for res in l:
            ownlresultdf.loc[i] = res.get()
            ownlallresultdf.loc[allnum] = ownlresultdf.loc[i]
            i += 1
            allnum += 1

        ownlresultdf['cashDelta'] = ownlresultdf['new_endcash'] - ownlresultdf['old_endcash']
        ownlresultdf.to_csv(ownlFolderName + '\\' + symbol + str(K_MIN) + ' finalresult_ownl' + str(winSwitch) + '.csv')

    ownlallresultdf['cashDelta'] = ownlallresultdf['new_endcash'] - ownlallresultdf['old_endcash']
    ownlallresultdf.to_csv(symbol + str(K_MIN)+' finalresult_ownl.csv')
    #return ownlallresultdf

def getDslOwnl(symbolInfo,K_MIN,parasetlist,stoplossList,winSwitchList):
    symbol=symbolInfo.symbol
    slip=symbolInfo.getSlip()

    allresultdf = pd.DataFrame(
        columns=['setname', 'dslTarget', 'ownlWinSwtich', 'old_endcash', 'old_Annual', 'old_Sharpe', 'old_Drawback',
                 'old_SR', 'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                 'dslWorknum', 'ownlWorknum', 'dslRetDelta', 'ownlRetDelta'])
    allnum=0
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
                                                  (symbol, K_MIN,setname, stoplossTarget, winSwitch, slip, dslFolderName,
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
                allnum+=1
            resultfilename = ("%s%d finalresult_dsl%.3f_ownl%.3f.csv" % (symbol, K_MIN, stoplossTarget, winSwitch))
            resultdf.to_csv(newfolder + '\\' + resultfilename)

    allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(symbol + str(K_MIN)+ ' finalresult_dsl_ownl.csv')
    #return allresultdf

if __name__=='__main__':
    # 文件路径
    upperpath = DC.getUpperPath(Lvyi3MA_Parameter.folderLevel)
    resultpath = upperpath + Lvyi3MA_Parameter.resultFolderName

    # 取参数集
    parasetlist = pd.read_csv(resultpath + Lvyi3MA_Parameter.parasetname)
    paranum = parasetlist.shape[0]

    # 参数设置
    strategyParameterSet = []
    if not Lvyi3MA_Parameter.symbol_KMIN_opt_swtich:
        # 单品种单周期模式
        paradic = {
            'strategyName': Lvyi3MA_Parameter.strategyName,
            'exchange_id': Lvyi3MA_Parameter.exchange_id,
            'sec_id': Lvyi3MA_Parameter.sec_id,
            'K_MIN': Lvyi3MA_Parameter.K_MIN,
            'startdate': Lvyi3MA_Parameter.startdate,
            'enddate': Lvyi3MA_Parameter.enddate,
            'symbol': '.'.join([Lvyi3MA_Parameter.exchange_id, Lvyi3MA_Parameter.sec_id]),
            'calcDsl': Lvyi3MA_Parameter.calcDsl_close,
            'calcOwnl': Lvyi3MA_Parameter.calcOwnl_close,
            'calcDslOwnl': Lvyi3MA_Parameter.calcDslOwnl_close,
            'dslStep':Lvyi3MA_Parameter.dslStep_close,
            'dslTargetStart':Lvyi3MA_Parameter.dslTargetStart_close,
            'dslTargetEnd':Lvyi3MA_Parameter.dslTargetEnd_close,
            'ownlStep' : Lvyi3MA_Parameter.ownlStep_close,
            'ownlTargetStart': Lvyi3MA_Parameter.ownlTargetStart_close,
            'ownltargetEnd': Lvyi3MA_Parameter.ownltargetEnd_close,
            'nolossThreshhold':Lvyi3MA_Parameter.nolossThreshhold_close
        }
        strategyParameterSet.append(paradic)
    else:
        # 多品种多周期模式
        symbolset = pd.read_excel(resultpath + Lvyi3MA_Parameter.stoploss_set_filename,index_col='No')
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
                'symbol': '.'.join([exchangeid, secid]),
                'calcDsl': symbolset.ix[i, 'calcDsl'],
                'calcOwnl': symbolset.ix[i, 'calcOwnl'],
                'calcDslOwnl': symbolset.ix[i, 'calcDslOwnl'],
                'dslStep': symbolset.ix[i, 'dslStep'],
                'dslTargetStart': symbolset.ix[i, 'dslTargetStart'],
                'dslTargetEnd': symbolset.ix[i, 'dslTargetEnd'],
                'ownlStep': symbolset.ix[i, 'ownlStep'],
                'ownlTargetStart': symbolset.ix[i, 'ownlTargetStart'],
                'ownltargetEnd': symbolset.ix[i, 'ownltargetEnd'],
                'nolossThreshhold': symbolset.ix[i, 'nolossThreshhold']
            }
            )

    for strategyParameter in strategyParameterSet:

        strategyName = strategyParameter['strategyName']
        exchange_id = strategyParameter['exchange_id']
        sec_id = strategyParameter['sec_id']
        K_MIN = strategyParameter['K_MIN']
        startdate = strategyParameter['startdate']
        enddate = strategyParameter['enddate']
        symbol = '.'.join([exchange_id, sec_id])

        symbolinfo = DC.SymbolInfo(symbol)
        slip = DC.getSlip(symbol)
        pricetick = DC.getPriceTick(symbol)

        #计算控制开关
        calcDsl=strategyParameter['calcDsl']
        calcOwnl=strategyParameter['calcOwnl']
        calcDslOwnl=strategyParameter['calcDslOwnl']

        #优化参数
        dslStep = strategyParameter['dslStep']
        stoplossList = np.arange(strategyParameter['dslTargetStart'], strategyParameter['dslTargetEnd'], dslStep)
        #stoplossList=[-0.022]
        ownlStep=strategyParameter['ownlStep']
        winSwitchList = np.arange(strategyParameter['ownlTargetStart'], strategyParameter['ownltargetEnd'], ownlStep)
        #winSwitchList=[0.009]
        nolossThreshhold = strategyParameter['nolossThreshhold'] * pricetick

        #文件路径
        foldername = ' '.join([strategyName,exchange_id, sec_id, str(K_MIN)])
        oprresultpath=resultpath+foldername
        os.chdir(oprresultpath)

        #原始数据处理
        bar1m=DC.getBarData(symbol=symbol,K_MIN=60,starttime=startdate+' 00:00:00',endtime=enddate+' 23:59:59')
        barxm=DC.getBarData(symbol=symbol,K_MIN=K_MIN,starttime=startdate+' 00:00:00',endtime=enddate+' 23:59:59')
        #bar1m计算longHigh,longLow,shortHigh,shortLow
        bar1m=bar1mPrepare(bar1m)

        if calcDsl:
            getDSL(symbolinfo, K_MIN, stoplossList, parasetlist, bar1m,barxm)

        if calcOwnl:
            getOwnl(symbolinfo,K_MIN,winSwitchList,nolossThreshhold,parasetlist,bar1m,barxm)

        if calcDslOwnl:
            getDslOwnl(symbolinfo,K_MIN,parasetlist,stoplossList,winSwitchList)