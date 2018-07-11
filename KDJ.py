# -*- coding: utf-8 -*-
'''
RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
BACKGROUNDSTYLE(1);
K:SMA(RSV,M1,1);
D:SMA(K,M2,1);
J:3*K-2*D;
'''
'''
注：KDJ数据在LvyiWin中有KDJ_HLim和KDJ_LLim的限制，所以暂时不把true和cross的功能转移到模块中
'''
import pandas as pd
#import talib
import numpy as np

def taKDJ(data,N=9,M=3):
    hight = np.array(data["high"])
    low = np.array(data["low"])
    close = np.array(data["close"])
    #matype: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
    K, D = talib.STOCH(hight, low, close, fastk_period=N, slowk_matype=1, slowk_period=M, slowd_period=M,slowd_matype=1)
    J = 3 * K - 2 * D
    tadf=pd.DataFrame({'KDJ_K': K})
    tadf['KDJ_D']=D
    tadf['KDJ_J']=J
    return tadf

def taKDJ2(data,N=9,M=3):
    high = np.array(data["high"])
    low = np.array(data["low"])
    close = np.array(data["close"])
    low_list = pd.rolling_min(low, N)
    #low_list.fillna(value=pd.expanding_min(low, inplace=True))
    high_list = pd.rolling_max(high, N)
    #high_list.fillna(value=pd.expanding_max(high), inplace=True)
    rsv = (close - low_list) / (high_list - low_list) * 100
    KDJ_K = pd.ewma(rsv, com=M-1)#a=1/(1+com),所以com=M-1
    KDJ_D = pd.ewma(KDJ_K, com=M-1)
    KDJ_J = 3 * KDJ_K - 2 * KDJ_D
    a=KDJ_K[-1]
    df1=pd.DataFrame({'KDJ_K':KDJ_K})
    df1['KDJ_D']=KDJ_D
    df1['KDJ_J']=KDJ_J
    return df1



def KDJ(data, N=9, M=3):
    #low_list = pd.rolling_min(data['low'], N)
    low_list = data['low'].rolling(N).min()
    #low_list.fillna(value=pd.expanding_min(data['low']), inplace=True)
    low_list.fillna(value=data['low'].rolling(N).min(), inplace=True)
    #high_list = pd.rolling_max(data['high'], N)
    high_list = data['high'].rolling(N).max()
    #high_list.fillna(value=pd.expanding_max(data['high']), inplace=True)
    high_list.fillna(value=data['high'].rolling(N).max(), inplace=True)
    rsv = (data['close'] - low_list) / (high_list - low_list) * 100
    #KDJ_K = pd.ewma(rsv, com=M-1)#a=1/(1+com),所以com=M-1
    KDJ_K = rsv.ewm(span=M, adjust=False).mean()
    #KDJ_D = pd.ewma(KDJ_K, com=M-1)
    KDJ_D = KDJ_K.ewm(span=M, adjust=False).mean()
    KDJ_J = 3 * KDJ_K - 2 * KDJ_D
    df1=pd.DataFrame({'KDJ_K':KDJ_K})
    df1['KDJ_D']=KDJ_D
    df1['KDJ_J']=KDJ_J
    #df1['rsv']=rsv
    #df1['Hn']=high_list
    #df1['Ln']=low_list
    return df1

def newKDJ(data,kdjdata,N=9,M=3):
    '''
    计算单个KDJ的值
    1: 获取股票T日收盘价X
    2: 计算周期的未成熟随机值RSV(n)＝（Ct－Ln）/（Hn-Ln）×100，
    其中：C为当日收盘价，Ln为N日内最低价，Hn为N日内最高价，n为基期分别取5、9、19、36、45、60、73日。
    3: 计算K值，当日K值=(1-a)×前一日K值+a×当日RSV
    4: 计算D值，当日D值=(1-a)×前一日D值+a×当日K值。
    若无前一日K值与D值，则可分别用50来代替,a为平滑因子，不过目前已经约定俗成，固定为1/3。
    5: 计算J值，当日J值=3×当日K值-2×当日D值

    :return:
    '''
    closeT=data.iloc[-1].close
    Ln=float(min(data.iloc[-N:].low))
    Hn=float(max(data.iloc[-N:].high))
    if Hn==Ln:#防止出现Hn和Ln相等，导致分母为0的情况
        rsv=100
    else :
        rsv=((closeT-Ln)/(Hn-Ln))*1000
    lastK=kdjdata.iloc[-1].KDJ_K
    lastD=kdjdata.iloc[-1].KDJ_D
    a=1/float(M)
    '''
    if rsv==200:
        newK=lastK
    else:
        newK=(1-a)*lastK+a*rsv#不能用2/3和1/3来算，会变成int，结果变0
    '''
    newK = (1 - a) * lastK + a * rsv
    newD=(1-a)*lastD+a*newK
    newJ=3*newK-2*newD
    return [newK,newD,newJ]
    #kdjdata.loc[kdjrow] = [data.ix[datarow-1, 'start_time'], rsv,Ln, Hn, newK, newD, newJ]

if __name__ == '__main__':
    N=9
    M=2
    KDJ_HLim=85
    KDJ_LLim=15
    df=pd.read_csv('test2.csv')
    #df_KDJ=KDJ(df,N,M)
    tadf=taKDJ2(df,N,M)
    '''
    df_KDJ=KDJ(df.iloc[0:20],N,M)
    df_KDJ['KDJ_True']=0
    df_KDJ.loc[(KDJ_HLim>df_KDJ['KDJ_K'])&(df_KDJ['KDJ_K']> df_KDJ['KDJ_D']), 'KDJ_True'] = 1
    df_KDJ.loc[(KDJ_LLim<df_KDJ['KDJ_K'])&(df_KDJ['KDJ_K']< df_KDJ['KDJ_D']), 'KDJ_True'] = -1
    import numpy
    for i in numpy.arange(21,344):
        kdj=newKDJ(df.iloc[0:i],df_KDJ,N,M)
        newk=kdj[0]
        newd=kdj[1]
        KDJ_True=0
        if KDJ_HLim>newk and newk>newd:KDJ_True=1
        elif KDJ_LLim<newk and newk<newd:KDJ_True=-1
        kdj.append(KDJ_True)
        df_KDJ.loc[i-1]=kdj
    '''
    #df_KDJ.to_csv('KDJ1.csv')
    tadf.to_csv('taKDJ2.csv')