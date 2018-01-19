# -*- coding: utf-8 -*-
'''
使用ATR指标进行平仓：
设定一个阀值比例(AtrCloseRate)，当现价相对于开盘价的亏损超过ATR*AtrCloseRate的值，则平仓
假设ATR的n取值为N：
    取0~N-1根10分钟线
    最后第N根采用1分钟线的计算结果，相当于本10分钟内截止当前时间内的1分钟线拟合成10分钟（high,low,close)
'''
import talib
import numpy as np
import pandas as pd
import DATA_CONSTANTS as DC

def atr(high,low,close, n, array=False):
    """ATR指标"""
    h=high.values
    l=low.values
    c=close.values
    result = talib.ATR(h, l, c, n)
    if array:
        return result
    return result[-1]

if __name__ == '__main__':
    AtrCloseRate = 0.4
    ATR_N = 20
    slip = 0.5
    pricetick=0.5
    symbol="DCE.I"
    K_MIN = 600
    oprresultpath = "D:\\002 MakeLive\myquant\LvyiWin\Results\DCE I 600 ricequant\ForwardOprAnalyze\\"
    setname = "DCE.I600_Rank5_win8"
    #bar1m = pd.read_csv(DC.BAR_DATA_PATH + symbol + '\\' + symbol + ' ' + str(60) + '.csv')
    barxm = pd.read_csv(DC.BAR_DATA_PATH + symbol + '\\' + symbol + ' ' + str(K_MIN) + '.csv')
    barxm['ATR']=atr(barxm.high,barxm.low,barxm.close,ATR_N,True)
    df = pd.DataFrame({'high':barxm.high})
    df['max']=df.high.rolling(window=10).max()
    print df.head(100)