# -*- coding: utf-8 -*-
'''
LvyiWin辅助功能
'''
import pandas as pd
import numpy as np
import os
import LvyiWin_Parameter
import DATA_CONSTANTS as DC
def resultCalc():
    '''
    重新统计多品种多周期的回测结果
    将各文件夹中的finalResult文件汇总到一起
    :return:
    '''
    upperpath=DC.getUpperPath(LvyiWin_Parameter.folderLevel)
    resultpath = upperpath + LvyiWin_Parameter.resultFolderName
    os.chdir(resultpath)
    allsymbolresult = pd.DataFrame(columns=
                                   ['Setname', 'MA_Short', 'MA_Long', 'KDJ_N', 'DMI_N', 'opentimes', 'end_cash',
                                    'SR', 'Annual', 'Sharpe', 'DrawBack', 'max_single_loss_rate',
                                    'strategyName', 'exchange_id', 'sec_id', 'K_MIN'])
    symbolset = pd.read_excel(resultpath + LvyiWin_Parameter.symbol_KMIN_set_filename)
    symbolsetNum = symbolset.shape[0]
    for i in range(symbolsetNum):
        strategyName=symbolset.ix[i, 'strategyName'],
        exchangeid = symbolset.ix[i, 'exchange_id']
        secid = symbolset.ix[i, 'sec_id']
        symbol = '.'.join([exchangeid, secid])
        K_MIN=symbolset.ix[i, 'K_MIN']
        foldername=' '.join([strategyName, exchangeid, secid, str(K_MIN)])
        result = pd.read_csv(foldername+'\\'+"%s %d finalresults.csv" % (symbol, K_MIN))
        allsymbolresult=pd.concat([allsymbolresult,result])

    allsymbolresult.to_csv(LvyiWin_Parameter.strategyName + "_symbol_KMIN_results.csv")
    pass


if __name__=='__main__':
    resultCalc()