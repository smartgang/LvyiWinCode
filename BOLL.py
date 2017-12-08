# -*- coding: utf-8 -*-
'''
MID:MA(CLOSE,N);
TMP2:=STD(CLOSE,M);
TOP:MID+P*TMP2;
BOTTOM:MID-P*TMP2;

    收盘价向上突破下限LOWER，为买入时机
    收盘价向下突破上限UPPER，为卖出时机

参数： N  天数，在计算布林带时用，一般26天
       P　一般为2，用于调整下限的值
'''
import pandas as pd
import MA



def BOLL(df,N=26,M=26,P=2):
    print 'start computing DMI'
    mid=MA.calMA(df['close'],N)
    tmp2=pd.rolling_std(df['close'],M)
    TOP=mid+P*tmp2
    BOTTOM=mid-P*tmp2
    df1=pd.DataFrame({'close':df['close'],'MID':mid,'TOP':TOP,'BOTTOM':BOTTOM})
    print 'DMI compute finished'
    return df1

if __name__ == '__main__':
    N=26
    M=26
    P=2
    df=pd.read_csv('test.csv')
    df1=BOLL(df,N,M,P)
    df1.to_csv('BOLL.csv')
