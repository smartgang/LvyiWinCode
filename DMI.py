# -*- coding: utf-8 -*-
''''
TR := SUM(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(LOW-REF(CLOSE,1))),N);
HD := HIGH-REF(HIGH,1);
LD := REF(LOW,1)-LOW;
DMP:= SUM(IFELSE(HD>0 && HD>LD,HD,0),N);
DMM:= SUM(IFELSE(LD>0 && LD>HD,LD,0),N);
PDI: DMP*100/TR;
MDI: DMM*100/TR;
ADX: MA(ABS(MDI-PDI)/(MDI+PDI)*100,M);
ADXR:(ADX+REF(ADX,M))/2;
BACKGROUNDSTYLE(1);
原理：
N=14
M=6
1、A=（最高价-最低价）与（最高价-昨日收盘价）两者之间较大者。
   B=（最低价-昨日收盘价）的绝对值
   C=A与B两者之间较大者
   TR=C在N个周期内的总和
2、HD=最高价-昨日最高价
3、LD=昨日最低价-最低价
4、如果HD>LD且HD>0,  那么DMP=HD在N个周期内的总和,否则DMP=0。
5、如果LD>HD且LD>0,  那么DMM=LD在N个周期内的总和,否则DMM=0。
6、PDI=DMP*100/TR
7、MDI=DMM*100/TR
8、ADX=（MDI-PDI）的绝对值/（MDI+PDI）*100在M个周期的简单移动平均
9、ADXR=（ADX+M个周期前的ADX）/2
用法：
1.PDI线(上升方向线)从下向上突破MDI线(下降方向线)，显示有新多头进场，为买进信号；
2.PDI线从上向下跌破MDI线，显示有新空头进场，为卖出信号；
3.ADX(趋向平均值)值持续高于前一日时，市场行情将维持原趋势；
4.ADX值递减，降到20以下，且横向行进时，市场气氛为盘整；
5.ADX值从上升倾向转为下降时，表明行情即将反转。
'''
'''
#2017-10-26:
    1、返回数据中，增加A、B、HD、LD列，以支持单个值的计算
    2、返回数据中，增加DMI_True列
    3、增加单个值计算函数newDMI（）
'''
import pandas as pd
import numpy as np
import MA
import talib

def npDMI(data,N=14,M=6):
    open=np.array(data['open'])
    hight = np.array(data["high"])
    low = np.array(data["low"])
    close = np.array(data["close"])
    closeshift1=np.roll(close,1)
    closeshift1[0]=0
    c=high-low
    d=high-closeshift1
    A=np.maximum(c,d)
    B=np.abs(low-close)
    C=np.maximum(A,B)
    #TR=talib.SUM(C,N)#可能要转换成float类型
    TR=pd.rolling_sum(C,N)
    highshift1=np.roll(high,1)
    highshift1[0]=0
    HD = high - highshift1
    lowshift1=np.roll(low,1)
    lowshift1[0]=0
    LD = low.shift1-low

    pass

def taDMI2(data,N=14,M=6):
    open1=np.array(data['open'])
    high1 = np.array(data["high"])
    low1 = np.array(data["low"])
    close1 = np.array(data["close"])

    open=pd.Series(open1)
    high=pd.Series(high1)
    low=pd.Series(low1)
    close=pd.Series(close1)

    closeshift1 = close.shift(1).fillna(0)
    c = high - low
    d = high - closeshift1
    df1 = pd.DataFrame({'c': c, 'd': d})
    df1['A'] = df1.max(axis=1)
    df1.drop('c', axis=1, inplace=True)
    df1.drop('d', axis=1, inplace=True)
    df1['B'] = np.abs(low - close)
    df1['C'] = df1.max(axis=1)
    TR = pd.rolling_sum(df1['C'], N)
    # 2、HD=最高价-昨日最高价
    # 3、LD=昨日最低价-最低价
    HD = high - high.shift(1).fillna(0)
    LD = low.shift(1).fillna(0) - low
    df1['HD'] = HD
    df1['LD'] = LD
    # DMP:= SUM(IFELSE(HD>0 && HD>LD,HD,0),N);
    # DMM:= SUM(IFELSE(LD>0 && LD>HD,LD,0),N);
    df2 = pd.DataFrame({'HD': HD, 'LD': LD})
    df2['DMP_1']=df2[(df2['HD']>df2['LD']) & (df2['HD']>0)]['HD']
    df2['DMM_1']=df2[(df2['LD']>df2['HD']) & (df2['LD']>0)]['LD']
    df2=df2.fillna(0)
    DMP=pd.rolling_sum(df2['DMP_1'], N)
    DMM = pd.rolling_sum(df2['DMM_1'], N)
    del df2
    # 6、PDI=DMP*100/TR
    # 7、MDI=DMM*100/TR
    PDI= np.array([DMP * 100 / TR])
    MDI= np.array([DMM * 100 / TR])
    return PDI,MDI

def DMI(df,N=14,M=6):
    high=df.high
    low=df.low
    close=df.close
    closeshift1=close.shift(1).fillna(0)
    open=df.open
    c=high-low
    d=high-closeshift1
    df1=pd.DataFrame({'c':c,'d':d})
    df1['A']=df1.max(axis=1)
    df1.drop('c',axis=1,inplace=True)
    df1.drop('d',axis=1,inplace=True)
    df1['B']=np.abs(low-close)
    df1['C']=df1.max(axis=1)

    #df1.drop('A',axis=1,inplace=True)
    #df1.drop('B',axis=1,inplace=True)

    df1['TR']=MA.sum_N(df1['C'],N)
    #2、HD=最高价-昨日最高价
    #3、LD=昨日最低价-最低价
    HD=high-high.shift(1).fillna(0)
    LD=low.shift(1).fillna(0)-low
    df1['HD']=HD
    df1['LD']=LD
    #DMP:= SUM(IFELSE(HD>0 && HD>LD,HD,0),N);
    #DMM:= SUM(IFELSE(LD>0 && LD>HD,LD,0),N);
    df2=pd.DataFrame({'HD':HD,'LD':LD})
    df2['DMP_1']=df2[(df2['HD']>df2['LD']) & (df2['HD']>0)]['HD']
    df2['DMM_1']=df2[(df2['LD']>df2['HD']) & (df2['LD']>0)]['LD']
    df2=df2.fillna(0)
    df1['DMP']=MA.sum_N(df2['DMP_1'],N)
    df1['DMM']=MA.sum_N(df2['DMM_1'],N)
    del df2
    #6、PDI=DMP*100/TR
    #7、MDI=DMM*100/TR
    df1['PDI']=df1['DMP']*100/df1['TR']
    df1['MDI']=df1['DMM']*100/df1['TR']
    #ADX: MA(ABS(MDI-PDI)/(MDI+PDI)*100,M);
    #ADXR:(ADX+REF(ADX,M))/2;
    df1['ADX']=MA.calMA(np.abs(df1['MDI']-df1['PDI'])/(df1['MDI']+df1['PDI'])*100,M)
    df1['ADXR']=(df1['ADX']+df1['ADX'].shift(M).fillna(0))/2

    #金叉死叉点
    df1['DMI_True']=0
    df1.loc[df1['PDI'] > df1['MDI'], 'DMI_True'] = 1
    df1.loc[df1['PDI'] < df1['MDI'], 'DMI_True'] = -1

    '''
    #相等的值，true标识修改为跟上一周期相同
    if df1.ix[0,'DMI_True']==0:
        df1.ix[0,'DMI_True']=1
    #填充0值，修改为上一周期的取值
    zeroindex=df1.loc[df1['DMI_True']==0].index
    for zi in zeroindex:
        df1.ix[zi,'DMI_True']=df1.ix[zi-1,'DMI_True']
    '''
    df1['bigger1']=df1['DMI_True'].shift(1).fillna(0)
    df1['DMI_GOLD_CROSS']=0
    df1.loc[df1['DMI_True']-df1['bigger1']>1,'DMI_GOLD_CROSS']=1
    df1.loc[df1['DMI_True'] - df1['bigger1'] < -1, 'DMI_GOLD_CROSS'] = -1
    df1.drop('bigger1', axis=1, inplace=True)
    return df1

def newDMI(rawdf,dmidf,N=14,M=6):
    loc=rawdf.iloc[-1]
    lastloc=rawdf.iloc[-2]
    open = loc.open
    high = loc.high
    low = loc.low
    close = loc.close
    lastclose = lastloc.close
    lasthigh = lastloc.high
    lastlow = lastloc.low

    A=max((high-low),(high-lastclose))
    B=abs(low-close)
    C=max(A,B)
    TR=dmidf.iloc[1-N:]['C'].sum()+C

    #2、HD=最高价-昨日最高价
    #3、LD=昨日最低价-最低价
    HD=high-lasthigh
    LD=lastlow-low

    #4、如果HD > LD且HD > 0, 那么DMP = HD在N个周期内的总和, 否则DMP = 0。
    #5、如果LD > HD且LD > 0, 那么DMM = LD在N个周期内的总和, 否则DMM = 0。
    DMP=0
    DMM=0
    df=dmidf.iloc[1-N:]
    for d in df.index:
        hd=df.ix[d,'HD']
        ld=df.ix[d,'LD']
        if hd>ld and hd>0:DMP+=hd
        if ld>hd and ld>0:DMM+=ld
    if HD>LD and HD>0:DMP+=HD
    if LD>HD and LD>0:DMM+=LD

    #6、PDI=DMP*100/TR
    #7、MDI=DMM*100/TR
    PDI= DMP * 100 /TR
    MDI = DMM *100 /TR
    #ADX: MA(ABS(MDI-PDI)/(MDI+PDI)*100,M);
    #ADXR:(ADX+REF(ADX,M))/2;
    #暂时用不到，懒得算了
    ADX=0
    ADXR=0

    #金叉死叉点
    lasttrue=dmidf.iloc[-1].DMI_True
    if PDI > MDI:DMI_True=1
    elif PDI < MDI:DMI_True=-1
    else : DMI_True=0#注：暂时跟上面的算法保持一致，对于相等的情况直接取0，不取为上一周期的值

    if lasttrue==-1 and lasttrue==1:DMI_GOLD_CROSS =1
    elif lasttrue==1 and lasttrue==-1:DMI_GOLD_CROSS=-1
    else:DMI_GOLD_CROSS=0
    return [A,B,C,TR,HD,LD,DMP,DMM,PDI,MDI,ADX,ADXR,DMI_True,DMI_GOLD_CROSS]

if __name__ == '__main__':
    N=14
    M=6
    df=pd.read_csv('test.csv')
    df1=DMI(df,N,M)
    tadf=taDMI2(df,N,M)
    '''
    import numpy
    for i in numpy.arange(21,344):
        df1.loc[i-1]=newDMI(df.iloc[0:i],df1,N,M)
        print df1.shape[0]
    '''
    df1.to_csv('DMI2.csv')
    tadf.to_csv('taDMI.csv')