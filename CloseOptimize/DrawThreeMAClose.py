# -*- coding: utf-8 -*-
'''
画图流程：
(对齐index：opr时间和k时间)
参数exchangeid，secid，K_MIN
根据时间算周列表
参数组名，读3均线结果文件，计算mamid
根据参数名建文件夹
读k线数据，算3均线
遍历周列表，取时间
根据时间取k线数据，画k线，画3均线
画开仓，画旧平仓，画新平仓
设标题：时间，setname,mm
保存图片
'''
import pandas as pd
import PlotLib
import DATA_CONSTANTS as DC
from datetime import datetime
import os
import MA
import time
import matplotlib.pyplot as plt
import numpy

if __name__=='__main__':
    #参数设置
    exchange_id = 'DCE'
    sec_id='I'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    starttime='2016-01-01 00:00:00'
    endtime='2018-01-01 00:00:00'
    parasetname='Set10748 MS5 ML13 KN22 DN30'
    ms=5
    ml=13

    #文件路径
    upperpath=DC.getUpperPath(uppernume=2)
    resultpath=upperpath+"\\Results\\"
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
    workingDir=resultpath+foldername+'\\ThreeMAClose3to4\\'
    os.chdir(workingDir)#进入工作文件夹
    finalresult=pd.read_csv(symbol+str(K_MIN)+' '+' 3MA finalresult3.csv',index_col='Setname')
    setoprdf=pd.read_csv(symbol+str(K_MIN)+' '+parasetname+' 3MAresult3.csv')
    mm=int(finalresult.loc[parasetname]['mamid'])#计算ma_mid

    weeklist = [datetime.strftime(x, '%Y-%m-%d') for x in
                 list(pd.date_range(start='2016-01-01', end='2018-01-01', freq='7D'))]
    weeklist.append('2018-01-01')

    #根据setname创建文件夹
    os.mkdir(parasetname)

    #准备画布
    _xlength = 8
    _ylength = 4
    _Fig = plt.figure(figsize=(_xlength, _ylength),
                      dpi=200,
                      facecolor=PlotLib.__color_pink__,
                      edgecolor=PlotLib.__color_navy__,
                      linewidth=1.0)  # Figure 对象
    axes = _Fig.add_axes([0.1, 0.1, 0.8, 0.8], facecolor='black')

    bardata=DC.getBarData(symbol,K_MIN,starttime=starttime,endtime=endtime)
    bardata['ms']=MA.calMA(bardata['close'],ms)
    bardata['mm']=MA.calMA(bardata['close'],mm)
    bardata['ml']=MA.calMA(bardata['close'],ml)

    for w in range(1,len(weeklist)):
        weekstart=weeklist[w-1]
        weekend=weeklist[w]
        weekstartutc = float(time.mktime(time.strptime(weekstart+ ' 00:00:00', "%Y-%m-%d %H:%M:%S")))
        weekendutc = float(time.mktime(time.strptime(weekend+ ' 00:00:00', "%Y-%m-%d %H:%M:%S")))
        weekbar = bardata.loc[(bardata['utc_time'] >= weekstartutc) & (bardata['utc_time'] < weekendutc)]
        #这里没有reset_index！

        if weekbar.shape[0]==0:continue
        high = weekbar['high']
        low = weekbar['low']
        open = weekbar['open']
        close = weekbar['close']

        _xsize = len(high)
        phigh = high.max()
        plow = low.min()
        yhighlimUp = int(phigh / 10) * 10 + 10  # K线子图 Y 轴最大坐标,5%最大波动,调整为10的倍数
        ylowlimUp = int(plow / 10) * 10  # K线子图 Y 轴最小坐标

        xAxis = axes.get_xaxis()
        yAxis = axes.get_yaxis()

        title=("%s %s ma_mid=%d" %(weekstart,parasetname,mm))
        axes.set_title(title, fontsize=4)
        PlotLib.setup_Axes(axes)
        PlotLib.setup_xAxis(weekbar['strtime'], axes, xAxis, _xsize, isvisible=True)
        PlotLib.setup_yAxis(axes, yAxis, yhighlimUp, ylowlimUp)
        PlotLib.drawK(axes, open, high, low, close)
        PlotLib.drawMA(axes,weekbar['ms'],label=('MA:'+str(ms)))
        PlotLib.drawMA(axes, weekbar['mm'],color='yellow',label=('MA:'+str(mm)))
        PlotLib.drawMA(axes, weekbar['ml'],color='purple',label=('MA:'+str(ml)))


        openopr = setoprdf.loc[(setoprdf['openutc'] >= weekstartutc) & (setoprdf['openutc'] < weekendutc)][[
            'tradetype', 'openindex']]
        oldcloseopr = setoprdf.loc[(setoprdf['closeutc'] >= weekstartutc) & (setoprdf['closeutc'] < weekendutc)][[
            'tradetype', 'closeindex']]
        newcloseopr = setoprdf.loc[(setoprdf['new_closeutc'] >= weekstartutc) & (setoprdf['new_closeutc'] < weekendutc)][[
            'tradetype', 'new_closeindex']]

        beginindex = open.index.tolist()[0]
        if openopr.shape[0]>0:
            openindex=numpy.array(openopr['openindex']-beginindex)
            for i in openindex: axes.vlines(i, ylowlimUp, numpy.array(low)[int(i)], edgecolor=PlotLib.__color_gold__,
                                            linewidth=1, alpha=0.7)
        if oldcloseopr.shape[0]>0:
            oldcloseindex=numpy.array(oldcloseopr['closeindex']-beginindex)
            for i in oldcloseindex: axes.vlines(i, ylowlimUp, numpy.array(low)[int(i)], edgecolor='green',
                                                linestyles='dotted', linewidth=1, alpha=0.7)
        if newcloseopr.shape[0]>0:
            newcloseindex=numpy.array(newcloseopr['new_closeindex']-beginindex)
            for i in newcloseindex: axes.vlines(i,ylowlimUp,numpy.array(low)[int(i)],edgecolor=PlotLib.__color_lightblue__, linestyles='dashed',linewidth=1, alpha=0.7)
        axes.legend(loc='upper left', fontsize=4, shadow=False)
        _Fig.savefig(parasetname+'\\'+title+'.png',dip=500)
        axes.cla()